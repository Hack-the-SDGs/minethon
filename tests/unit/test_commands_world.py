"""Unit tests for world-sensing commands (get_block / look_block / find_block*)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot


def block(name: str, x: float = 0, y: float = 0, z: float = 0) -> SimpleNamespace:
    return SimpleNamespace(name=name, position=SimpleNamespace(x=x, y=y, z=z))


class _Names:
    """Mirror a JS object proxy: missing key returns None, not KeyError."""

    def __init__(self, mapping: dict[str, int]) -> None:
        self._d = {n: SimpleNamespace(id=i) for n, i in mapping.items()}

    def __getitem__(self, key: str) -> object | None:
        return self._d.get(key)


class FakeJs:
    def __init__(
        self,
        *,
        block_at: object | None = None,
        cursor: object | None = None,
        find: object | None = None,
        finds: list[object] | None = None,
        names: dict[str, int] | None = None,
    ) -> None:
        self._block_at = block_at
        self._cursor = cursor
        self._find = find
        self._finds = finds or []
        self.registry = SimpleNamespace(blocksByName=_Names(names or {}))
        self.calls: dict[str, object] = {}

    def blockAt(self, point: object) -> object | None:  # noqa: N802
        self.calls["blockAt"] = point
        return self._block_at

    def blockAtCursor(self, max_distance: float) -> object | None:  # noqa: N802
        self.calls["blockAtCursor"] = max_distance
        return self._cursor

    def findBlock(self, options: object) -> object | None:  # noqa: N802
        self.calls["findBlock"] = options
        return self._find

    def findBlocks(self, options: object) -> list[object]:  # noqa: N802
        self.calls["findBlocks"] = options
        return self._finds


def test_get_block_returns_name_and_builds_vec3(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    fake = FakeJs(block_at=block("stone"))

    assert Bot(fake).get_block(1, 2, 3) == "stone"
    assert fake.calls["blockAt"] == (1, 2, 3)


def test_get_block_returns_none_when_unloaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))

    assert Bot(FakeJs(block_at=None)).get_block(0, 0, 0) is None


def test_look_block_returns_coords_and_name() -> None:
    fake = FakeJs(cursor=block("dirt", 5, 64, 5))

    assert Bot(fake).look_block() == ((5, 64, 5), "dirt")
    assert fake.calls["blockAtCursor"] == cmd._REACH_BLOCKS


def test_look_block_returns_none_when_nothing_in_reach() -> None:
    assert Bot(FakeJs(cursor=None)).look_block() is None


def test_find_block_resolves_name_to_id_and_returns_coords() -> None:
    fake = FakeJs(find=block("diamond_ore", 10, 20, 30), names={"diamond_ore": 56})

    assert Bot(fake).find_block("diamond_ore") == (10, 20, 30)
    assert fake.calls["findBlock"]["matching"] == 56


def test_find_block_unknown_name_returns_none_without_querying() -> None:
    fake = FakeJs(names={})

    assert Bot(fake).find_block("not_a_block") is None
    assert "findBlock" not in fake.calls


def test_find_blocks_maps_each_coordinate() -> None:
    coords = [SimpleNamespace(x=1, y=2, z=3), SimpleNamespace(x=4, y=5, z=6)]
    fake = FakeJs(finds=coords, names={"oak_log": 47})

    assert Bot(fake).find_blocks("oak_log", max=2) == [(1, 2, 3), (4, 5, 6)]
    assert fake.calls["findBlocks"]["count"] == 2


def test_find_blocks_unknown_name_returns_empty_list() -> None:
    assert Bot(FakeJs(names={})).find_blocks("nope") == []
