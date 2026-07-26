"""Unit tests for the synchronous read/lifecycle command surface."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot
from minethon.errors import NotSpawnedError


def make_entity(
    x: float = 1.5,
    y: float = 64.0,
    z: float = -2.5,
    yaw: float = 0.0,
    pitch: float = 0.0,
) -> SimpleNamespace:
    return SimpleNamespace(
        position=SimpleNamespace(x=x, y=y, z=z),
        yaw=yaw,
        pitch=pitch,
    )


class FakeJs:
    """Minimal stand-in for the mineflayer JS proxy."""

    def __init__(
        self,
        entity: object | None = None,
        controls: dict[str, bool] | None = None,
        held: object | None = None,
        vehicle: object | None = None,
    ) -> None:
        self.entity = entity
        self._controls = controls or {}
        self.heldItem = held
        # mineflayer keeps bot.vehicle null while the bot rides nothing.
        self.vehicle = vehicle

    def getControlState(self, control: str) -> bool:  # noqa: N802
        return self._controls.get(control, False)


def test_get_position_reads_entity() -> None:
    bot = Bot(FakeJs(entity=make_entity(x=1.5, y=64.0, z=-2.5)))

    assert bot.get_x() == 1.5
    assert bot.get_y() == 64.0
    assert bot.get_z() == -2.5
    assert bot.get_pos() == (1.5, 64.0, -2.5)


def test_get_yaw_converts_radians_to_normalised_degrees() -> None:
    assert Bot(FakeJs(entity=make_entity(yaw=math.pi / 2))).get_yaw() == pytest.approx(
        90.0
    )
    # Negative yaw wraps into [0, 360).
    assert Bot(FakeJs(entity=make_entity(yaw=-math.pi / 2))).get_yaw() == pytest.approx(
        270.0
    )


def test_get_pitch_converts_radians_to_degrees() -> None:
    assert Bot(
        FakeJs(entity=make_entity(pitch=math.pi / 2))
    ).get_pitch() == pytest.approx(90.0)


def test_reads_before_spawn_raise_not_spawned() -> None:
    bot = Bot(FakeJs(entity=None))

    with pytest.raises(NotSpawnedError):
        bot.get_x()
    with pytest.raises(NotSpawnedError):
        bot.get_pos()
    with pytest.raises(NotSpawnedError):
        bot.get_yaw()


def test_get_sneak_reflects_control_state() -> None:
    assert Bot(FakeJs(controls={"sneak": True})).get_sneak() is True
    assert Bot(FakeJs(controls={})).get_sneak() is False


def test_is_riding_reflects_bot_vehicle() -> None:
    assert Bot(FakeJs()).is_riding() is False
    assert Bot(FakeJs(vehicle=SimpleNamespace(name="minecart"))).is_riding() is True


def test_get_hand_returns_name_count_or_none() -> None:
    assert Bot(FakeJs(held=None)).get_hand() is None
    held = SimpleNamespace(name="diamond_sword", count=1)
    assert Bot(FakeJs(held=held)).get_hand() == ("diamond_sword", 1)


def test_wait_spawn_returns_immediately_when_already_spawned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    used: list[object] = []
    monkeypatch.setattr(cmd, "Once", lambda *a, **_k: used.append(a) or (lambda fn: fn))

    Bot(FakeJs(entity=make_entity())).wait_spawn()

    assert used == []  # Once is never wired when the bot is already in-world


def test_wait_spawn_waits_for_spawn_event(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    def fake_once(_js: object, event: str):
        seen["event"] = event

        def deco(fn):
            fn()  # simulate the 'spawn' event firing
            return fn

        return deco

    monkeypatch.setattr(cmd, "Once", fake_once)

    Bot(FakeJs(entity=None)).wait_spawn()  # returns once the handler sets the event

    assert seen["event"] == "spawn"


def test_wait_returns_quickly_for_zero_seconds() -> None:
    Bot(FakeJs()).wait(0)  # must not raise and must return promptly
