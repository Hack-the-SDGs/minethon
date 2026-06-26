"""Unit tests for orientation commands (turn* / set_turn / look_at)."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot


class TurnJs:
    """Fake proxy: look()/lookAt() update the entity's yaw/pitch in radians."""

    def __init__(self, yaw: float = 0.0, pitch: float = 0.0) -> None:
        self.entity = SimpleNamespace(yaw=yaw, pitch=pitch)
        self.calls: list[tuple] = []

    def look(self, yaw: float, pitch: float, force: bool) -> None:
        self.calls.append(("look", yaw, pitch, force))
        self.entity.yaw = yaw
        self.entity.pitch = pitch

    def lookAt(self, point: object, force: bool) -> None:  # noqa: N802
        self.calls.append(("lookAt", point, force))
        self.entity.yaw = math.pi  # simulate ending up facing +Z


def test_set_turn_sets_absolute_yaw_in_radians() -> None:
    fake = TurnJs()

    result = Bot(fake).set_turn(90.0)

    kind, yaw, _pitch, force = fake.calls[0]
    assert kind == "look"
    assert yaw == pytest.approx(math.pi / 2)
    assert force is True
    assert result[0] == pytest.approx(90.0)


def test_turn_is_relative_to_current_yaw() -> None:
    fake = TurnJs(yaw=math.pi / 2)  # already facing 90°

    result = Bot(fake).turn(90.0)

    assert result[0] == pytest.approx(180.0)


def test_turn_left_adds_quarter_turn() -> None:
    assert Bot(TurnJs(yaw=0.0)).turn_left()[0] == pytest.approx(90.0)


def test_turn_right_wraps_into_zero_to_360() -> None:
    # 0° - 90° = -90° → normalised to 270°.
    assert Bot(TurnJs(yaw=0.0)).turn_right()[0] == pytest.approx(270.0)


def test_look_at_calls_lookat_with_vec3_and_force(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
    fake = TurnJs()

    result = Bot(fake).look_at(10, 64, -3)

    kind, point, force = fake.calls[0]
    assert kind == "lookAt"
    assert point == (10, 64, -3)
    assert force is True
    assert result[0] == pytest.approx(180.0)  # fake faces +Z after lookAt
