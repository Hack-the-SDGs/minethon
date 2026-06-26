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


def test_dig_returns_none_when_nothing_aimed_at() -> None:
    assert Bot(ActJs(cursor=None)).dig() is None


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
