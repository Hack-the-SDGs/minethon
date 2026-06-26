"""Unit tests for item commands (hold / unhold / drop)."""

from __future__ import annotations

from types import SimpleNamespace

from minethon._bot_runtime import Bot


def item(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name, count=1)


class InvJs:
    def __init__(
        self,
        items: list[SimpleNamespace] | None = None,
        held: object | None = None,
    ) -> None:
        carried = items or []
        self.inventory = SimpleNamespace(items=lambda: carried)
        self.heldItem = held
        self.calls: list[tuple] = []

    def equip(self, the_item: object, destination: str) -> None:
        self.calls.append(("equip", the_item, destination))

    def unequip(self, destination: str) -> None:
        self.calls.append(("unequip", destination))

    def tossStack(self, the_item: object) -> None:  # noqa: N802
        self.calls.append(("tossStack", the_item))


def test_hold_equips_matching_item_to_hand() -> None:
    stone = item("stone")
    fake = InvJs(items=[item("dirt"), stone])

    assert Bot(fake).hold("stone") is True
    assert fake.calls == [("equip", stone, "hand")]


def test_hold_returns_false_when_item_absent() -> None:
    fake = InvJs(items=[item("dirt")])

    assert Bot(fake).hold("gold_ingot") is False
    assert fake.calls == []


def test_unhold_unequips_when_holding() -> None:
    fake = InvJs(held=item("sword"))

    assert Bot(fake).unhold() is True
    assert fake.calls == [("unequip", "hand")]


def test_unhold_returns_false_when_empty_handed() -> None:
    fake = InvJs(held=None)

    assert Bot(fake).unhold() is False
    assert fake.calls == []


def test_drop_tosses_held_stack() -> None:
    sword = item("sword")
    fake = InvJs(held=sword)

    assert Bot(fake).drop() is True
    assert fake.calls == [("tossStack", sword)]


def test_drop_returns_false_when_empty_handed() -> None:
    fake = InvJs(held=None)

    assert Bot(fake).drop() is False
    assert fake.calls == []
