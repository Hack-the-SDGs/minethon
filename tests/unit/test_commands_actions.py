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


class BucketJs(ActJs):
    """ActJs plus the inventory/equip/lookAt surface put_water relies on.

    ``activateItem`` emulates the server swapping the held bucket: pour turns
    ``water_bucket`` into ``bucket``, scoop turns it back.
    """

    def __init__(
        self,
        *,
        block_at: object | None = None,
        items: tuple = (),
        held: SimpleNamespace | None = None,
    ) -> None:
        super().__init__(block_at=block_at)
        self._items = list(items)
        self.heldItem = held  # mirrors the mineflayer field name
        self.inventory = SimpleNamespace(items=lambda: self._items)

    def equip(self, item: object, destination: str) -> None:
        self.calls.append(("equip", item, destination))
        self.heldItem = item

    def lookAt(self, point: object, force: bool) -> None:  # noqa: N802
        self.calls.append(("lookAt", point, force))

    def activateItem(self) -> None:  # noqa: N802
        self.calls.append(("activateItem",))
        if self.heldItem is not None and self.heldItem.name == "water_bucket":
            self.heldItem = SimpleNamespace(name="bucket", count=1)
        elif self.heldItem is not None and self.heldItem.name == "bucket":
            self.heldItem = SimpleNamespace(name="water_bucket", count=1)


def item(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name, count=1)


def test_put_water_pours_and_scoops_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    monkeypatch.setattr(cmd, "_PUT_WATER_SETTLE_SECONDS", 0.0)
    fire = block("fire", 0, 64, 1)
    fake = BucketJs(block_at=fire, items=(item("water_bucket"),))

    assert Bot(fake).action("put_water") is True
    # Equipped from the inventory, aimed at the fire's centre, poured + scooped.
    assert ("equip", fake._items[0], "hand") in fake.calls
    assert ("lookAt", (0.5, 64.5, 1.5), True) in fake.calls
    assert fake.calls.count(("activateItem",)) == 2
    assert fake.heldItem.name == "water_bucket"  # bucket refilled after scoop


def test_put_water_aims_at_floor_when_nothing_ahead(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    monkeypatch.setattr(cmd, "_PUT_WATER_SETTLE_SECONDS", 0.0)
    fake = BucketJs(block_at=None, held=item("water_bucket"))

    assert Bot(fake).action("put_water") is True
    # Spawn is (0, 64, 0) yaw 0 -> front cell (0, 64, -1); aim its floor top.
    assert ("lookAt", (0.5, 63.5, -0.5), True) in fake.calls


def test_put_water_without_bucket_returns_false() -> None:
    fake = BucketJs(block_at=None)

    assert Bot(fake).action("put_water") is False
    assert ("activateItem",) not in fake.calls


def test_action_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="put_water"):
        Bot(BucketJs()).action("make_coffee")
