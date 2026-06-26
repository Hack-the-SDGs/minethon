"""Unit tests for movement commands (move_* / jump) via control-state polling."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot


class MoveJs:
    """Fake proxy whose X advances each position read while 'forward' is on."""

    def __init__(self, *, step: float = 0.0) -> None:
        self._x = 0.0
        self._z = 0.0
        self._step = step
        self.controls: dict[str, bool] = {}
        self.history: list[tuple[str, bool]] = []

    @property
    def entity(self) -> SimpleNamespace:
        if self.controls.get("forward"):
            self._x += self._step
        return SimpleNamespace(position=SimpleNamespace(x=self._x, y=64.0, z=self._z))

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        self.controls[control] = state
        self.history.append((control, state))


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make time.sleep a no-op so polling loops run instantly."""
    monkeypatch.setattr(cmd.time, "sleep", lambda _s: None)


def _frozen_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clock that never advances: the loop exits only on distance reached."""
    monkeypatch.setattr(cmd.time, "monotonic", lambda: 0.0)


def _expiring_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clock that jumps past any deadline on the first in-loop check."""
    ticks = iter([0.0, 1000.0])
    monkeypatch.setattr(cmd.time, "monotonic", lambda t=ticks: next(t))


def test_move_forward_toggles_control_and_reaches_distance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _frozen_clock(monkeypatch)
    fake = MoveJs(step=0.5)

    pos = Bot(fake).move_forward(2.0)

    assert fake.history == [("forward", True), ("forward", False)]
    assert fake.controls["forward"] is False  # always released at the end
    assert pos[0] >= 2.0


def test_move_backward_uses_back_control(monkeypatch: pytest.MonkeyPatch) -> None:
    _expiring_clock(monkeypatch)
    fake = MoveJs()

    Bot(fake).move_backward(1.0)

    assert ("back", True) in fake.history
    assert fake.controls["back"] is False


def test_move_left_and_right_map_to_strafe_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for direction in ("left", "right"):
        _expiring_clock(monkeypatch)
        fake = MoveJs()
        getattr(Bot(fake), f"move_{direction}")(1.0)
        assert (direction, True) in fake.history
        assert fake.controls[direction] is False


def test_move_zero_blocks_is_a_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    _frozen_clock(monkeypatch)
    fake = MoveJs(step=0.5)

    Bot(fake).move_forward(0)

    assert fake.history == []  # never touches controls for a zero-distance move


def test_walk_times_out_when_stuck(monkeypatch: pytest.MonkeyPatch) -> None:
    _expiring_clock(monkeypatch)
    fake = MoveJs(step=0.0)  # wall: position never changes

    pos = Bot(fake).move_forward(5.0)

    assert fake.controls["forward"] is False  # released despite never arriving
    assert pos == (0.0, 64.0, 0.0)


def test_jump_pulses_jump_control() -> None:
    fake = MoveJs()

    Bot(fake).jump()

    assert fake.history == [("jump", True), ("jump", False)]
