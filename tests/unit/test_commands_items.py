"""Unit tests for item commands (hold / unhold / drop)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

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

    def toss(self, item_type: int, metadata: object | None, count: int | None) -> None:
        self.calls.append(("toss", item_type, metadata, count))


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


def test_drop_by_name_full_stack() -> None:
    gold = SimpleNamespace(name="gold_ingot", type=266, count=10)
    fake = InvJs(items=[gold])

    assert Bot(fake).drop("gold_ingot") is True
    assert fake.calls == [("tossStack", gold)]


def test_drop_by_name_partial_count_with_metadata() -> None:
    gold = SimpleNamespace(name="gold_ingot", type=266, count=10, metadata=5)
    fake = InvJs(items=[gold])

    assert Bot(fake).drop("gold_ingot", 3) is True
    assert fake.calls == [("toss", 266, 5, 3)]


def test_drop_by_name_not_carried() -> None:
    fake = InvJs(items=[SimpleNamespace(name="dirt", type=3, count=5)])

    assert Bot(fake).drop("gold_ingot") is False
    assert fake.calls == []


def test_drop_by_int_id_present() -> None:
    gold = SimpleNamespace(name="gold_ingot", type=266, count=10)
    fake = InvJs(items=[gold])

    assert Bot(fake).drop(266, 5) is True
    assert fake.calls == [("toss", 266, None, 5)]


def test_drop_by_int_id_absent() -> None:
    fake = InvJs(items=[SimpleNamespace(name="dirt", type=3, count=5)])

    assert Bot(fake).drop(266, 5) is False
    assert fake.calls == []


def test_drop_invalid_count_raises_value_error() -> None:
    fake = InvJs(items=[SimpleNamespace(name="gold_ingot", type=266, count=10)])

    with pytest.raises(ValueError, match="count 必須是大於 0 的正整數"):
        Bot(fake).drop("gold_ingot", 0)

    with pytest.raises(ValueError, match="count 必須是大於 0 的正整數"):
        Bot(fake).drop("gold_ingot", -5)

    assert fake.calls == []


def test_drop_multi_stack_spanning() -> None:
    stack1 = SimpleNamespace(name="gold_ingot", type=266, count=5, metadata=0)
    stack2 = SimpleNamespace(name="gold_ingot", type=266, count=32, metadata=0)
    fake = InvJs(items=[stack1, stack2])

    assert Bot(fake).drop("gold_ingot", 10) is True
    assert fake.calls == [("tossStack", stack1), ("toss", 266, 0, 5)]


def test_drop_count_exceeding_total_issues_warning() -> None:
    gold = SimpleNamespace(name="gold_ingot", type=266, count=10)
    fake = InvJs(items=[gold])

    with pytest.warns(UserWarning, match="超過持有量"):
        assert Bot(fake).drop("gold_ingot", 50) is True

    assert fake.calls == [("tossStack", gold)]
