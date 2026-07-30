"""Regression tests for the failures that used to be silent.

Every case here was measured against the competition server first: the command
returned a success-shaped value (or nothing at all) while the world did not
change, so a student had no traceback, no output, and no way to tell a working
script from a broken one. Each test pins the report that replaced it.
"""

from __future__ import annotations

import math
from types import SimpleNamespace
from typing import Any

import pytest

import minethon._bot_runtime as rt
import minethon._commands as cmd
from minethon._bot_runtime import Bot
from minethon._members import BOT_MEMBERS


class Js:
    """Minimal mineflayer stand-in: spawned, named, records what it is told."""

    def __init__(self, *, yaw: float = 1.0, pitch: float = -1.2) -> None:
        self.username = "U100_bot"
        self.entity = SimpleNamespace(
            position=SimpleNamespace(x=0.0, y=64.0, z=0.0), yaw=yaw, pitch=pitch
        )
        self.sent: list[str] = []
        self.looks: list[tuple[float, float, bool]] = []
        self.controls: dict[str, bool] = {}

    def chat(self, message: str) -> None:
        self.sent.append(message)

    def look(self, yaw: float, pitch: float, force: bool) -> None:
        self.looks.append((yaw, pitch, force))
        self.entity.yaw, self.entity.pitch = yaw, pitch

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        self.controls[control] = state

    def getControlState(self, control: str) -> bool:  # noqa: N802
        return self.controls.get(control, False)


# ── look_level: dig/place/use all resolve through where the bot is aiming ──


def test_look_level_zeroes_the_pitch_and_keeps_the_facing() -> None:
    """Measured spawn pitch on the competition server: -52° to -68°.

    At that angle blockAtCursor returns the floor, so dig() breaks the ground
    instead of what is in front, and nothing in the student API could undo it —
    set_turn deliberately preserves pitch and look_at needs coordinates the
    caller has to work out.
    """
    js = Js(yaw=2.5, pitch=math.radians(-67.7))
    bot = Bot(js)

    assert bot.look_level() == (bot.get_yaw(), 0.0)
    assert js.entity.pitch == 0.0
    assert js.entity.yaw == 2.5  # horizontal facing untouched


# ── move_*: walking into a wall, and nonsense distances ──


def test_walk_says_so_when_it_gives_up_against_a_wall(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cmd, "_WALK_STALL_TIMEOUT", 0.0)
    js = Js(yaw=0.0)
    # Never moves, so the stall timeout is the only way out of the poll loop.
    bot = Bot(js)

    assert bot.move_forward(20) == (0.0, 64.0, 0.0)
    out = capsys.readouterr().out
    assert "走不動" in out
    assert "20" in out  # says what was asked for, not just that it stopped


def test_walk_says_so_for_a_non_positive_distance(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bot = Bot(Js())

    assert bot.move_forward(-2) == (0.0, 64.0, 0.0)
    assert "要大於 0" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("call", "label"),
    [
        (lambda bot: bot.move_forward("3"), "移動的格數"),
        (lambda bot: bot.wait("3"), "等待的秒數"),
        (lambda bot: bot.turn("90"), "轉的角度"),
        (lambda bot: bot.look_at("1", 2, 3), "X 座標"),
    ],
)
def test_numeric_arguments_name_themselves(call: Any, label: str) -> None:
    """Previously these surfaced three frames deep as e.g.

    ``TypeError: '<=' not supported between instances of 'str' and 'int'`` —
    naming neither the argument nor the method the student called.
    """
    with pytest.raises(TypeError, match=label):
        call(Bot(Js()))


# ── action(): the server-authoritative no-op ──


def test_action_rejects_a_non_string_name() -> None:
    # str(123) -> "123" passed the charset check and sent a trigger nobody
    # implements, i.e. a silent no-op for an obvious mistake.
    with pytest.raises(TypeError, match="動作名稱要是文字"):
        Bot(Js()).action(123)  # type: ignore[arg-type]


def test_action_warns_when_the_server_has_not_enabled_it(
    capsys: pytest.CaptureFixture[str],
) -> None:
    js = Js()
    bot = Bot(js)
    # Brigadier only suggests triggers /trigger accepts from this player.
    bot._enabled_trigger_objectives = lambda: {  # type: ignore[method-assign]
        "u100_bot_put_out",
        "u100_bot_open_door",
        "someone_else_thing",
    }

    bot.action("extinguish")

    out = capsys.readouterr().out
    assert "不接受動作" in out
    assert "put out" in out  # lists this bot's own actions
    assert "open door" in out
    assert "someone_else_thing" not in out  # not other players' triggers
    # Still sent: an unavailable-looking trigger is harmless, but skipping a
    # valid one because the suggestion list was incomplete would not be.
    assert js.sent == ["/trigger u100_bot_extinguish"]


def test_action_stays_quiet_when_it_is_enabled(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bot = Bot(Js())
    bot._enabled_trigger_objectives = lambda: {"u100_bot_put_out"}  # type: ignore[method-assign]

    bot.action("put out")

    assert capsys.readouterr().out == ""


def test_action_stays_quiet_when_the_server_tells_us_nothing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # An empty suggestion set means "could not tell", not "nothing is enabled".
    bot = Bot(Js())
    bot._enabled_trigger_objectives = set  # type: ignore[method-assign]

    bot.action("put out")

    assert capsys.readouterr().out == ""


# ── use_player(): the call that ends the session ──


def test_use_player_refuses_the_bot_itself() -> None:
    """The server answers a self-interact by disconnecting ("Cannot interact
    with self!"), and this used to return True on the way out.
    """
    with pytest.raises(ValueError, match="不能對自己"):
        Bot(Js()).use_player("U100_bot")


# ── block names: "wrong name" vs "not nearby" were the same answer ──


class Registry:
    """Block registry that answers None for unknown names, like the JS proxy."""

    def __init__(self, names: dict[str, int]) -> None:
        self._d = {n: SimpleNamespace(id=i) for n, i in names.items()}

    def __getitem__(self, key: str) -> object | None:
        return self._d.get(key)

    def __iter__(self) -> Any:
        return iter(self._d)


def test_unknown_block_name_says_so_and_suggests(
    capsys: pytest.CaptureFixture[str],
) -> None:
    js = Js()
    js.registry = SimpleNamespace(  # type: ignore[attr-defined]
        blocksByName=Registry({"stone": 1, "dirt": 2, "stonecutter": 3})
    )

    assert Bot(js).find_block("stonee") is None
    out = capsys.readouterr().out
    assert "沒有叫做「stonee」的方塊" in out
    assert "stone" in out


# ── bounded_keys: the guard on iterating a foreign object ──


def test_bounded_keys_refuses_a_getitem_only_object() -> None:
    """A JS-proxy stand-in that defines only __getitem__ satisfies Python's
    legacy iteration protocol, and iterating it asks for index 0, 1, 2… forever
    because a missing key yields None instead of raising IndexError.

    This is not hypothetical: it hung the whole test suite once.
    """

    class GetItemOnly:
        def __getitem__(self, key: object) -> None:
            return None

    assert cmd.bounded_keys(GetItemOnly()) == []


def test_bounded_keys_caps_an_unbounded_iterator() -> None:
    class Endless:
        def __iter__(self) -> Any:
            def gen() -> Any:
                n = 0
                while True:
                    yield f"name{n}"
                    n += 1

            return gen()

    assert len(cmd.bounded_keys(Endless())) == cmd._SUGGEST_SCAN_LIMIT


# ── misspelled attributes: the bridge answers None instead of raising ──


class ProxyLike(Js):
    """Answers None for unknown attributes, as JSPyBridge does."""

    def __iter__(self) -> Any:
        return iter(("username", "entity", "heldItem", "health", "vehicle"))

    def __getattr__(self, name: str) -> None:
        return None  # bridge.js replies 'void' for undefined properties


def test_misspelled_attribute_raises_instead_of_being_none() -> None:
    with pytest.raises(AttributeError, match="username"):
        _ = Bot(ProxyLike()).usernam


def test_misspelled_method_names_itself() -> None:
    # Used to be `TypeError: 'NoneType' object is not callable`, which never
    # mentions what was misspelled.
    with pytest.raises(AttributeError, match="move_forward"):
        Bot(ProxyLike()).move_foward(3)


def test_wrong_case_is_caught_too() -> None:
    with pytest.raises(AttributeError, match="chat"):
        Bot(ProxyLike()).Chat("hi")


def test_a_real_attribute_that_is_none_still_returns_none() -> None:
    """bot.vehicle is legitimately None when not riding.

    Regression: an earlier version keyed the known-name set on the live proxy's
    own keys, and JS leaves `bot.vehicle` undefined until the first mount — so
    reading it was rejected as a typo of `moveVehicle` on a bot that had simply
    never ridden anything. The set now comes from the generated BOT_MEMBERS.
    """
    proxy = ProxyLike()
    assert "vehicle" in BOT_MEMBERS
    assert Bot(proxy).vehicle is None


def test_an_unrecognisable_name_stays_quiet() -> None:
    # No close match means no confident guess, so behave as before rather than
    # risk breaking a mineflayer attribute we simply do not know about.
    assert Bot(ProxyLike()).zzzzzzzz is None


# ── kick reasons arrive as protodef NBT, not strings ──


def test_kick_reason_is_flattened_from_nbt(
    capsys: pytest.CaptureFixture[str],
) -> None:
    reason = {
        "type": "compound",
        "value": {
            "translate": {
                "type": "string",
                "value": "multiplayer.disconnect.duplicate_login",
            }
        },
    }

    rt._on_kicked(reason)

    out = capsys.readouterr().out
    assert "duplicate_login" in out
    assert "'type'" not in out  # not a dict repr


def test_connection_throttle_gets_its_own_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Vanilla throttles reconnects per IP; a classroom behind one NAT address
    trips it constantly, and the raw kick text reads like the script's fault.
    """
    rt._on_kicked({"type": "string", "value": "Connection throttled! Please wait"})

    out = capsys.readouterr().out
    assert "等幾秒再跑一次" in out
    assert "被伺服器踢出" not in out
