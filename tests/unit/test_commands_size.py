"""Unit tests for size commands (get_height / set_height via scale attribute)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from minethon._bot_runtime import Bot
from minethon.errors import NotSpawnedError


def entity_with_scale(
    scale: float | None = None,
    *,
    key: str = "minecraft:generic.scale",
    modifiers: list[dict[str, float]] | None = None,
) -> SimpleNamespace:
    attrs = None if scale is None else {key: {"value": scale, "modifiers": modifiers}}
    return SimpleNamespace(attributes=attrs)


class FakeJs:
    def __init__(self, entity: object | None, username: str = "U1_bot") -> None:
        self.entity = entity
        self.username = username
        self.sent: list[str] = []

    def chat(self, message: str) -> None:
        self.sent.append(message)


def test_get_height_maps_scale_to_level() -> None:
    assert Bot(FakeJs(entity_with_scale(1.0))).get_height() == 1
    assert Bot(FakeJs(entity_with_scale(3.0))).get_height() == 3
    assert Bot(FakeJs(entity_with_scale(5.0))).get_height() == 5


def test_get_height_rounds_and_clamps() -> None:
    assert Bot(FakeJs(entity_with_scale(3.4))).get_height() == 3
    assert Bot(FakeJs(entity_with_scale(0.2))).get_height() == 1  # clamp low
    assert Bot(FakeJs(entity_with_scale(9.0))).get_height() == 5  # clamp high


def test_get_height_defaults_to_1_without_scale() -> None:
    assert Bot(FakeJs(SimpleNamespace(attributes=None))).get_height() == 1
    other = SimpleNamespace(attributes={"generic.armor": {"value": 0, "modifiers": []}})
    assert Bot(FakeJs(other)).get_height() == 1


def test_get_height_applies_modifiers() -> None:
    # base 2 + operation-0 modifier (+1) -> 3.
    entity = entity_with_scale(2.0, modifiers=[{"operation": 0, "amount": 1.0}])
    assert Bot(FakeJs(entity)).get_height() == 3


def test_get_height_finds_legacy_scale_key() -> None:
    assert Bot(FakeJs(entity_with_scale(4.0, key="generic.scale"))).get_height() == 4


@pytest.mark.parametrize("bad", [0, 6, -1, 100])
def test_set_height_rejects_out_of_range(bad: int) -> None:
    with pytest.raises(ValueError, match="大小等級"):
        Bot(FakeJs(entity_with_scale(1.0))).set_height(bad)


def test_set_height_asks_the_server_via_trigger() -> None:
    js = FakeJs(entity_with_scale(1.0))

    Bot(js).set_height(4)

    assert js.sent == ["/trigger u1_bot_set_height set 4"]


def test_set_height_does_not_fake_the_reading() -> None:
    """The old version wrote the scale locally, so get_height echoed the request.

    That made the obvious way to check — set it, then read it back — confirm a
    resize that never happened in-world. The reading must stay server-sourced.
    """
    js = FakeJs(entity_with_scale(1.0))
    bot = Bot(js)

    bot.set_height(4)

    assert bot.get_height() == 1


def test_set_height_rejects_non_numbers() -> None:
    with pytest.raises(TypeError, match="大小等級"):
        Bot(FakeJs(entity_with_scale(1.0))).set_height("3")  # type: ignore[arg-type]


def test_set_height_before_spawn_raises() -> None:
    with pytest.raises(NotSpawnedError):
        Bot(FakeJs(None)).set_height(3)
