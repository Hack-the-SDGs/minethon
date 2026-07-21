"""Unit tests for movement commands (move_* / jump) via control-state polling."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot


class MoveJs:
    """Fake proxy that applies each active control at yaw zero."""

    def __init__(self, *, step: float = 0.0) -> None:
        self._x = 0.0
        self._z = 0.0
        self._step = step
        self.controls: dict[str, bool] = {}
        self.history: list[tuple[str, bool]] = []

    @property
    def entity(self) -> SimpleNamespace:
        if self.controls.get("forward"):
            self._z -= self._step
        if self.controls.get("back"):
            self._z += self._step
        if self.controls.get("left"):
            self._x -= self._step
        if self.controls.get("right"):
            self._x += self._step
        return SimpleNamespace(
            position=SimpleNamespace(x=self._x, y=64.0, z=self._z),
            yaw=0.0,
        )

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        self.controls[control] = state
        self.history.append((control, state))


class FakeClock:
    """Controllable monotonic clock for long-running movement tests."""

    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class GridLockJs(MoveJs):
    """Server-authoritative grid that advances one cell after every lock."""

    def __init__(self, clock: FakeClock, *, lock_seconds: float) -> None:
        super().__init__()
        self._clock = clock
        self._lock_seconds = lock_seconds
        self._next_step_at = lock_seconds

    @property
    def entity(self) -> SimpleNamespace:
        if self.controls.get("forward") and self._clock.now >= self._next_step_at:
            self._z -= 1.0
            self._next_step_at += self._lock_seconds
        return SimpleNamespace(
            position=SimpleNamespace(x=self._x, y=64.0, z=self._z),
            yaw=0.0,
        )


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
    assert pos[2] <= -2.0


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


@pytest.mark.parametrize(
    ("method", "axis", "sign"),
    [
        ("move_forward", "z", -1),
        ("move_backward", "z", 1),
        ("move_left", "x", -1),
        ("move_right", "x", 1),
    ],
)
def test_all_move_controls_reach_the_requested_direction(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    axis: str,
    sign: int,
) -> None:
    _frozen_clock(monkeypatch)
    fake = MoveJs(step=0.25)

    pos = getattr(Bot(fake), method)(3.0)

    coordinate = pos[0] if axis == "x" else pos[2]
    assert coordinate * sign >= 3.0


@pytest.mark.parametrize(
    ("control", "yaw", "expected"),
    [
        ("forward", 0.0, (0.0, -1.0)),
        ("back", 0.0, (0.0, 1.0)),
        ("left", 0.0, (-1.0, 0.0)),
        ("right", 0.0, (1.0, 0.0)),
        ("forward", cmd.math.pi / 2, (-1.0, 0.0)),
        ("back", cmd.math.pi / 2, (1.0, 0.0)),
        ("left", cmd.math.pi / 2, (0.0, 1.0)),
        ("right", cmd.math.pi / 2, (0.0, -1.0)),
    ],
)
def test_control_vectors_follow_facing_at_cardinal_yaws(
    control: str,
    yaw: float,
    expected: tuple[float, float],
) -> None:
    assert cmd._control_vector(control, yaw) == pytest.approx(expected, abs=1e-12)


def test_lateral_drift_does_not_count_as_forward_progress(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _expiring_clock(monkeypatch)
    fake = MoveJs(step=0.0)
    fake._x = 5.0

    pos = Bot(fake).move_forward(1.0)

    assert pos == (5.0, 64.0, 0.0)
    assert fake.controls["forward"] is False


def test_progress_refreshes_timeout_during_a_long_slow_walk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(cmd.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(cmd.time, "sleep", lambda _seconds: clock.sleep(1.0))
    fake = MoveJs(step=0.25)

    pos = Bot(fake).move_forward(2.0)

    assert pos[2] <= -2.0
    assert clock.now > cmd._WALK_STALL_TIMEOUT


def test_multiple_server_grid_steps_can_outlive_one_stall_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(cmd.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(cmd.time, "sleep", lambda _seconds: clock.sleep(0.5))
    fake = GridLockJs(clock, lock_seconds=4.5)

    pos = Bot(fake).move_forward(3.0)

    assert pos == (0.0, 64.0, -3.0)
    assert clock.now >= 13.5


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
