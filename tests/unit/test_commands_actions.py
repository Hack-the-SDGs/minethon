"""Unit tests for action commands (dig / place / use / sneak)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot


def block(
    name: str, x: int = 0, y: int = 0, z: int = 0, face: int = 1
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name, position=SimpleNamespace(x=x, y=y, z=z), face=face
    )


class ActJs:
    def __init__(
        self,
        *,
        cursor: object | None = None,
        block_at: object | None = None,
        held: object | None = SimpleNamespace(name="stone", count=1),
        dig_ms: float | None = 1000.0,
    ) -> None:
        self._cursor = cursor
        self._block_at = block_at
        self.heldItem = held
        self.dig_ms = dig_ms
        self.calls: list[tuple] = []
        self.dig_timeouts: list[float] = []
        self.controls: dict[str, bool] = {}
        # Spawned at (0, 64, 0) facing yaw 0 (south, +z) — lets dig() fall back
        # to _block_in_front when nothing is aimed at.
        self.entity = SimpleNamespace(
            position=SimpleNamespace(x=0.0, y=64.0, z=0.0), yaw=0.0
        )

    def blockAtCursor(self, max_distance: float) -> object | None:  # noqa: N802
        self.calls.append(("blockAtCursor", max_distance))
        return self._cursor

    def digTime(self, the_block: object) -> float | None:  # noqa: N802
        self.calls.append(("digTime", the_block))
        return self.dig_ms

    def dig(self, the_block: object, timeout: float = 10.0) -> None:
        self.calls.append(("dig", the_block))
        self.dig_timeouts.append(timeout)

    def placeBlock(self, ref: object, face_vector: object) -> None:  # noqa: N802
        self.calls.append(("placeBlock", ref, face_vector))

    def blockAt(self, point: object) -> object | None:  # noqa: N802
        self.calls.append(("blockAt", point))
        return self._block_at

    def activateBlock(self, the_block: object) -> None:  # noqa: N802
        self.calls.append(("activateBlock", the_block))

    def activateItem(self) -> None:  # noqa: N802
        self.calls.append(("activateItem",))

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        self.calls.append(("setControlState", control, state))
        self.controls[control] = state


def test_dig_breaks_block_at_cursor() -> None:
    aimed = block("stone", 5, 64, 5)
    fake = ActJs(cursor=aimed)

    assert Bot(fake).dig() == ((5, 64, 5), "stone")
    assert ("dig", aimed) in fake.calls


def test_dig_returns_none_when_only_air_in_front() -> None:
    # Nothing aimed at and only air one step ahead -> nothing to break.
    assert Bot(ActJs(cursor=None, block_at=None)).dig() is None


def test_dig_falls_back_to_block_in_front(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Not aiming at anything, but a solid block sits one step forward (yaw 0
    # faces +z, so the block ahead is at (0, 64, 1)).
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    ahead = block("dirt", 0, 64, 1)
    fake = ActJs(cursor=None, block_at=ahead)

    assert Bot(fake).dig() == ((0, 64, 1), "dirt")
    assert ("dig", ahead) in fake.calls


def test_place_places_against_aimed_top_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    ref = block("grass_block", 5, 64, 5, face=1)  # face 1 == top (+Y)
    fake = ActJs(cursor=ref, block_at=SimpleNamespace(name="cobblestone"))

    assert Bot(fake).place() == ((5, 65, 5), "cobblestone")
    assert ("placeBlock", ref, (0, 1, 0)) in fake.calls


def test_place_returns_none_without_target() -> None:
    assert Bot(ActJs(cursor=None)).place() is None


def test_use_activates_block_when_aiming() -> None:
    lever = block("lever")
    fake = ActJs(cursor=lever)

    assert Bot(fake).use() is True
    assert ("activateBlock", lever) in fake.calls


def test_use_activates_held_item_without_target() -> None:
    fake = ActJs(cursor=None)

    assert Bot(fake).use() is True
    assert ("activateItem",) in fake.calls


class PlayerUseJs(ActJs):
    def __init__(
        self,
        players: dict[str, object],
        *,
        spawned: bool = True,
        vehicle: object | None = None,
    ) -> None:
        super().__init__()
        self.players = players
        self.vehicle = vehicle
        if not spawned:
            self.entity = None

    def lookAt(self, point: object, force: bool) -> None:  # noqa: N802
        self.calls.append(("lookAt", point, force))

    def activateEntityAt(self, entity: object, point: object) -> None:  # noqa: N802
        self.calls.append(("activateEntityAt", entity, point))

    def activateEntity(self, entity: object) -> None:  # noqa: N802
        self.calls.append(("activateEntity", entity))


def player_entity(
    *, x: float = 2.0, y: float = 70.0, z: float = 3.0, height: float = 1.8
) -> SimpleNamespace:
    return SimpleNamespace(
        position=SimpleNamespace(x=x, y=y, z=z),
        height=height,
        isValid=True,
    )


def test_use_player_interacts_at_live_center_then_activates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    target = player_entity(y=76.0, height=2.0)
    fake = PlayerUseJs({"Alice": SimpleNamespace(entity=target)})

    assert Bot(fake).use_player("Alice") is True
    # Not riding, so mineflayer's own lookAt turns the bot for the INTERACT_AT.
    # The INTERACT that follows is always pre-aimed — see the riding tests.
    assert fake.calls == [
        ("activateEntityAt", target, (2.0, 77.0, 3.0)),
        ("lookAt", (2.0, 77.0, 3.0), True),
        ("activateEntity", target),
    ]


def test_use_player_uses_default_height_with_negative_fractional_coordinates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    target = SimpleNamespace(
        position=SimpleNamespace(x=-12.5, y=-4.25, z=0.125),
        isValid=True,
    )
    fake = PlayerUseJs({"Alice": SimpleNamespace(entity=target)})

    assert Bot(fake).use_player("Alice") is True
    assert fake.calls == [
        ("activateEntityAt", target, (-12.5, -3.35, 0.125)),
        ("lookAt", (-12.5, -3.25, 0.125), True),
        ("activateEntity", target),
    ]


def test_use_player_does_not_fall_through_when_interact_at_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    target = player_entity()
    fake = PlayerUseJs({"Alice": SimpleNamespace(entity=target)})

    def fail_interact_at(entity: object, point: object) -> None:
        fake.calls.append(("activateEntityAt", entity, point))
        msg = "INTERACT_AT failed"
        raise RuntimeError(msg)

    fake.activateEntityAt = fail_interact_at  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="INTERACT_AT failed"):
        Bot(fake).use_player("Alice")
    assert fake.calls == [("activateEntityAt", target, (2.0, 70.9, 3.0))]


def test_use_player_forces_the_look_while_riding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A mounted bot must pre-aim, or mineflayer's own lookAt never resolves.

    physics.js turns `shouldUsePhysics` off on 'mount', so the 'move' event
    that settles a non-forced lookAt stops firing and the activate call hangs
    until JSPyBridge's per-call timeout kills the script.
    """
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    target = player_entity()
    fake = PlayerUseJs(
        {"Alice": SimpleNamespace(entity=target)}, vehicle=SimpleNamespace()
    )

    assert Bot(fake).use_player("Alice") is True
    assert fake.calls == [
        ("lookAt", (2.0, 70.9, 3.0), True),
        ("activateEntityAt", target, (2.0, 70.9, 3.0)),
        ("lookAt", (2.0, 71.0, 3.0), True),
        ("activateEntity", target),
    ]


def test_use_player_forces_the_look_before_interact_even_when_not_yet_mounted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The INTERACT pre-aim must not depend on `bot.vehicle` still being null.

    INTERACT_AT has already gone out by then, so the mount notification can
    land after the check and while activateEntity's own look is awaiting —
    physics goes off mid-await and that look never settles. `bot.vehicle` here
    is still null, and the forced look has to happen anyway.

    The pre-aim also re-reads the entity position, because activateEntity aims
    one block above where the entity is *at call time*.
    """
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    target = player_entity()
    fake = PlayerUseJs({"Alice": SimpleNamespace(entity=target)})

    def move_then_interact_at(entity: object, point: object) -> None:
        fake.calls.append(("activateEntityAt", entity, point))
        target.position = SimpleNamespace(x=8.0, y=71.0, z=9.0)

    fake.activateEntityAt = move_then_interact_at  # type: ignore[method-assign]

    assert Bot(fake).use_player("Alice") is True
    assert fake.vehicle is None
    assert fake.calls == [
        ("activateEntityAt", target, (2.0, 70.9, 3.0)),
        ("lookAt", (8.0, 72.0, 9.0), True),
        ("activateEntity", target),
    ]


@pytest.mark.parametrize(
    "players",
    [
        {},
        {"Alice": SimpleNamespace(entity=None)},
        {"Alice": SimpleNamespace(entity=player_entity())},
    ],
    ids=["missing-player", "missing-entity", "invalid-entity"],
)
def test_use_player_raises_when_target_is_not_loaded(
    players: dict[str, object],
) -> None:
    from minethon.errors import PlayerNotFoundError

    target = getattr(players.get("Alice"), "entity", None)
    if target is not None:
        target.isValid = False

    fake = PlayerUseJs(players)
    with pytest.raises(PlayerNotFoundError, match="Alice") as exc_info:
        Bot(fake).use_player("Alice")
    assert str(exc_info.value) == (
        "找不到玩家 'Alice'。請確認對方在線、與機器人在同一世界，且位於已載入範圍內。"
    )
    assert fake.calls == []


def test_use_player_before_spawn_raises() -> None:
    from minethon.errors import NotSpawnedError

    with pytest.raises(NotSpawnedError):
        Bot(PlayerUseJs({}, spawned=False)).use_player("Alice")


def test_get_player_pos_returns_native_float_tuple() -> None:
    # ints in -> floats out, so follow loops get a plain (x, y, z), never a Vec3.
    target = SimpleNamespace(position=SimpleNamespace(x=2, y=70, z=3), isValid=True)
    fake = PlayerUseJs({"Alice": SimpleNamespace(entity=target)})

    result = Bot(fake).get_player_pos("Alice")

    assert result == (2.0, 70.0, 3.0)
    assert all(type(value) is float for value in result)


@pytest.mark.parametrize(
    "players",
    [{}, {"Alice": SimpleNamespace(entity=None)}],
)
def test_get_player_pos_raises_when_target_is_not_loaded(
    players: dict[str, object],
) -> None:
    from minethon.errors import PlayerNotFoundError

    with pytest.raises(PlayerNotFoundError, match="Alice"):
        Bot(PlayerUseJs(players)).get_player_pos("Alice")


def test_get_player_pos_before_spawn_raises() -> None:
    from minethon.errors import NotSpawnedError

    with pytest.raises(NotSpawnedError):
        Bot(PlayerUseJs({}, spawned=False)).get_player_pos("Alice")


def test_sneak_toggles_control_and_returns_state() -> None:
    fake = ActJs()

    assert Bot(fake).sneak(True) is True
    assert fake.controls["sneak"] is True
    assert Bot(fake).sneak(False) is False


def test_get_block_in_front_reports_fire(monkeypatch: pytest.MonkeyPatch) -> None:
    # Fire is not in the non-solid skip list, so the forward probe reports it.
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    fake = ActJs(block_at=block("fire", 0, 64, -1))

    assert Bot(fake).get_block_in_front() == ((0, 64, -1), "fire")


def test_get_block_in_front_none_over_open_ground(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))

    assert Bot(ActJs(block_at=None)).get_block_in_front() is None


class TriggerJs(ActJs):
    """ActJs plus the username/chat surface bot.action() relies on."""

    def __init__(self, *, username: str | None = None) -> None:
        super().__init__()
        self.username = username
        self.messages: list[str] = []

    def chat(self, message: str) -> None:
        self.messages.append(message)


def test_action_sends_username_prefixed_trigger() -> None:
    fake = TriggerJs(username="G1_labfire_1")

    assert Bot(fake).action("put out") is None
    assert fake.messages == ["/trigger g1_labfire_1_put_out"]


def test_action_normalises_case_hyphens_and_spacing() -> None:
    fake = TriggerJs(username="G1_labfire_1")

    Bot(fake).action("  Put-Out ")
    assert fake.messages == ["/trigger g1_labfire_1_put_out"]


def test_action_attaches_optional_value_payload() -> None:
    fake = TriggerJs(username="G1_labfire_1")

    Bot(fake).action("put out", 2)
    assert fake.messages == ["/trigger g1_labfire_1_put_out set 2"]


def test_action_rejects_bad_characters() -> None:
    fake = TriggerJs(username="G1_labfire_1")

    with pytest.raises(ValueError, match="動作名稱"):
        Bot(fake).action("放水")
    assert fake.messages == []


def test_action_before_login_raises() -> None:
    from minethon.errors import NotSpawnedError

    with pytest.raises(NotSpawnedError):
        Bot(TriggerJs(username=None)).action("put out")


def test_dig_scales_bridge_timeout_from_dig_time() -> None:
    # 15s of digging (deepslate bare-handed) must outlive JSPyBridge's 10s
    # default call budget: timeout = digTime + margin.
    fake = ActJs(cursor=block("deepslate", 1, 64, 1), dig_ms=15_000.0)

    assert Bot(fake).dig() == ((1, 64, 1), "deepslate")
    assert fake.dig_timeouts == [20.0]


def test_dig_keeps_default_timeout_floor_for_quick_digs() -> None:
    fake = ActJs(cursor=block("dirt", 1, 64, 1), dig_ms=300.0)

    Bot(fake).dig()
    assert fake.dig_timeouts == [10.0]


def test_dig_refuses_unbreakable_blocks(capsys: pytest.CaptureFixture) -> None:
    # Bare-handed obsidian is 250s — refuse with a friendly line instead of
    # blocking for minutes and then dumping a bridge-timeout stack.
    fake = ActJs(cursor=block("obsidian", 1, 64, 1), dig_ms=250_000.0)

    assert Bot(fake).dig() is None
    assert not fake.dig_timeouts
    assert "太硬" in capsys.readouterr().out


def test_dig_refuses_bedrock_infinity_as_none(capsys: pytest.CaptureFixture) -> None:
    # Bedrock's digTime is Infinity; the bridge's JSON serialization delivers
    # it as None — that must route to the friendly "too hard" line too.
    fake = ActJs(cursor=block("bedrock", 1, 64, 1), dig_ms=None)

    assert Bot(fake).dig() is None
    assert not fake.dig_timeouts
    assert "太硬" in capsys.readouterr().out


def test_place_returns_none_when_hand_is_empty() -> None:
    fake = ActJs(cursor=block("stone", 5, 64, 5), held=None)

    assert Bot(fake).place() is None
    assert not any(call[0] == "placeBlock" for call in fake.calls)
