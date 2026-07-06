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
        self, *, cursor: object | None = None, block_at: object | None = None
    ) -> None:
        self._cursor = cursor
        self._block_at = block_at
        self.calls: list[tuple] = []
        self.controls: dict[str, bool] = {}
        # Spawned at (0, 64, 0) facing yaw 0 (south, +z) — lets dig() fall back
        # to _block_in_front when nothing is aimed at.
        self.entity = SimpleNamespace(
            position=SimpleNamespace(x=0.0, y=64.0, z=0.0), yaw=0.0
        )

    def blockAtCursor(self, max_distance: float) -> object | None:  # noqa: N802
        self.calls.append(("blockAtCursor", max_distance))
        return self._cursor

    def dig(self, the_block: object) -> None:
        self.calls.append(("dig", the_block))

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
    fake = TriggerJs(username="G1_labfire")

    assert Bot(fake).action("put out") is None
    assert fake.messages == ["/trigger g1_labfire_put_out"]


def test_action_normalises_case_hyphens_and_spacing() -> None:
    fake = TriggerJs(username="G1_labfire")

    Bot(fake).action("  Put-Out ")
    assert fake.messages == ["/trigger g1_labfire_put_out"]


def test_action_attaches_optional_value_payload() -> None:
    fake = TriggerJs(username="G1_labfire")

    Bot(fake).action("put out", 2)
    assert fake.messages == ["/trigger g1_labfire_put_out set 2"]


def test_action_rejects_bad_characters() -> None:
    fake = TriggerJs(username="G1_labfire")

    with pytest.raises(ValueError, match="動作名稱"):
        Bot(fake).action("放水")
    assert fake.messages == []


def test_action_before_login_raises() -> None:
    from minethon.errors import NotSpawnedError

    with pytest.raises(NotSpawnedError):
        Bot(TriggerJs(username=None)).action("put out")
