"""Unit tests for movement commands (move_* / jump) via control-state polling."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
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
        self.yaw = 0.0
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
            yaw=self.yaw,
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
            yaw=self.yaw,
        )


class CountingScoreboards(dict[str, SimpleNamespace]):
    """Mapping that records full-table provider discovery scans."""

    def __init__(self) -> None:
        super().__init__()
        self.iterations = 0

    def __iter__(self):
        self.iterations += 1
        return super().__iter__()


class ServerGridJs(MoveJs):
    """Fake server capability that atomically moves and negates each request."""

    def __init__(
        self,
        *,
        username: str = "G0_labfire_1",
        acknowledge: bool = True,
        move: bool = True,
        initial_score: int = 0,
        objective: str = "maze.step",
        title: object = cmd._GRID_MOVE_PROVIDER_TITLE,
    ) -> None:
        super().__init__()
        self._x = 0.5
        self._z = 0.5
        self.username = username
        self.objective = objective
        self.scoreboards = CountingScoreboards()
        self.score = self.add_provider(objective, title=title, score=initial_score)
        self.commands: list[str] = []
        self.acknowledge = acknowledge
        self.move = move

    def add_provider(
        self,
        objective: str,
        *,
        title: object = cmd._GRID_MOVE_PROVIDER_TITLE,
        score: int = 0,
    ) -> SimpleNamespace:
        item = SimpleNamespace(value=score)
        self.scoreboards[objective] = SimpleNamespace(
            title=title,
            itemsMap={self.username: item},
        )
        if objective == self.objective:
            self.score = item
        return item

    def chat(self, command: str) -> None:
        self.commands.append(command)
        objective = command.split(maxsplit=3)[1]
        payload = int(command.rsplit(" ", maxsplit=1)[1])
        if not self.acknowledge:
            return
        direction = payload % cmd._GRID_MOVE_SEQUENCE_BASE
        offsets = {
            cmd._GRID_MOVE_DIRECTIONS["north"]: (0.0, -1.0),
            cmd._GRID_MOVE_DIRECTIONS["east"]: (1.0, 0.0),
            cmd._GRID_MOVE_DIRECTIONS["south"]: (0.0, 1.0),
            cmd._GRID_MOVE_DIRECTIONS["west"]: (-1.0, 0.0),
        }
        if self.move:
            dx, dz = offsets[direction]
            self._x += dx
            self._z += dz
        item = self.scoreboards[objective].itemsMap[self.username]
        item.value = -payload
        if objective == self.objective:
            self.score = item


class ScorelessServerGridJs(MoveJs):
    """Grid provider whose trigger score is never broadcast to the client."""

    def __init__(
        self,
        *,
        acknowledge: bool = True,
        objective: str = "q.labfire.step",
    ) -> None:
        super().__init__()
        self._x = 0.5
        self._z = 0.5
        self.username = "G1_labfire_1"
        self.objective = objective
        self.scoreboards = CountingScoreboards()
        self.scoreboards[objective] = SimpleNamespace(
            title={
                "type": "string",
                "value": cmd._GRID_MOVE_PROVIDER_TITLE,
            },
            itemsMap={},
        )
        self.commands: list[str] = []
        self.tab_queries: list[tuple[str, bool, bool, int]] = []
        self.enabled = True
        self.additional_enabled: set[str] = set()
        self.acknowledge = acknowledge
        self.move = True
        self._pending_payload: int | None = None

    def tabComplete(  # noqa: N802
        self,
        text: str,
        assume_command: bool,
        send_block_in_sight: bool,
        timeout: int,
    ) -> list[dict[str, object]]:
        self.tab_queries.append((text, assume_command, send_block_in_sight, timeout))
        if self._pending_payload is not None and self.acknowledge:
            direction = self._pending_payload % cmd._GRID_MOVE_SEQUENCE_BASE
            dx, dz = {
                cmd._GRID_MOVE_DIRECTIONS["north"]: (0.0, -1.0),
                cmd._GRID_MOVE_DIRECTIONS["east"]: (1.0, 0.0),
                cmd._GRID_MOVE_DIRECTIONS["south"]: (0.0, 1.0),
                cmd._GRID_MOVE_DIRECTIONS["west"]: (-1.0, 0.0),
            }[direction]
            if self.move:
                self._x += dx
                self._z += dz
            self._pending_payload = None
            self.enabled = True
        objectives = set(self.additional_enabled)
        if self.enabled:
            objectives.add(self.objective)
        # Modern minecraft-protocol represents each match as an object.
        return [
            {"match": objective, "tooltip": None} for objective in sorted(objectives)
        ]

    def chat(self, command: str) -> None:
        self.commands.append(command)
        self.enabled = False
        self._pending_payload = int(command.rsplit(" ", maxsplit=1)[1])


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


def test_unrelated_scoreboard_uses_physics_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _frozen_clock(monkeypatch)
    fake = MoveJs(step=0.5)
    fake.username = "plain_bot"
    fake.scoreboards = {
        "unrelated": SimpleNamespace(
            title="not a movement provider",
            itemsMap={fake.username: SimpleNamespace(value=0)},
        )
    }

    pos = Bot(fake).move_forward(1)

    assert pos[2] <= -1.0
    assert fake.history == [("forward", True), ("forward", False)]


@pytest.mark.parametrize(
    ("method", "expected", "payload"),
    [
        ("move_forward", (0.5, 64.0, -0.5), 11),
        ("move_backward", (0.5, 64.0, 1.5), 13),
        ("move_left", (-0.5, 64.0, 0.5), 14),
        ("move_right", (1.5, 64.0, 0.5), 12),
    ],
)
def test_server_grid_capability_moves_exactly_without_controls(
    method: str,
    expected: tuple[float, float, float],
    payload: int,
) -> None:
    fake = ServerGridJs()

    pos = getattr(Bot(fake), method)(1)

    assert pos == expected
    assert fake.history == []
    assert fake.commands == [f"/trigger {fake.objective} set {payload}"]
    assert fake.score.value == -payload


def test_server_grid_splits_multi_block_walk_into_acknowledged_cells() -> None:
    fake = ServerGridJs()

    pos = Bot(fake).move_forward(3)

    assert pos == (0.5, 64.0, -2.5)
    assert fake.commands == [
        f"/trigger {fake.objective} set 11",
        f"/trigger {fake.objective} set 21",
        f"/trigger {fake.objective} set 31",
    ]
    assert fake.score.value == -31


def test_server_grid_uses_new_sequence_after_stale_ack() -> None:
    fake = ServerGridJs(initial_score=-11)

    Bot(fake).move_forward(1)

    assert fake.commands == [f"/trigger {fake.objective} set 21"]
    assert fake.score.value == -21


def test_server_grid_provider_is_cached_after_first_scan() -> None:
    fake = ServerGridJs()
    bot = Bot(fake)

    bot.move_forward(1)
    scans_after_discovery = fake.scoreboards.iterations
    bot.move_forward(1)

    assert scans_after_discovery == 1
    assert fake.scoreboards.iterations == scans_after_discovery


def test_server_grid_serializes_concurrent_calls_before_sequence_read() -> None:
    fake = ServerGridJs()
    bot = Bot(fake)
    first_request_started = threading.Event()
    release_first_request = threading.Event()
    second_worker_started = threading.Event()
    second_request_started = threading.Event()
    calls_lock = threading.Lock()
    call_count = 0
    original_chat = fake.chat

    def delayed_chat(command: str) -> None:
        nonlocal call_count
        with calls_lock:
            call_count += 1
            current_call = call_count
        if current_call == 1:
            first_request_started.set()
            assert release_first_request.wait(timeout=1.0)
        else:
            second_request_started.set()
        original_chat(command)

    fake.chat = delayed_chat  # type: ignore[method-assign]

    def move_second() -> tuple[float, float, float]:
        second_worker_started.set()
        return bot.move_forward(1)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(bot.move_forward, 1)
        assert first_request_started.wait(timeout=1.0)
        second = executor.submit(move_second)
        assert second_worker_started.wait(timeout=1.0)

        # The second call must not reach chat or derive its sequence until the
        # first transaction has received ACK and released the per-Bot lock.
        assert not second_request_started.wait(timeout=0.05)
        release_first_request.set()
        results = [first.result(timeout=1.0), second.result(timeout=1.0)]

    assert len(results) == 2
    assert fake.commands == [
        f"/trigger {fake.objective} set 11",
        f"/trigger {fake.objective} set 21",
    ]
    assert fake.score.value == -21
    assert fake.entity.position.z == -1.5


def test_server_grid_rejects_multiple_providers_with_names() -> None:
    fake = ServerGridJs(objective="maze.step")
    fake.add_provider("parkour.move")

    with pytest.raises(
        cmd.MinethonError,
        match=r"maze\.step, parkour\.move.*只為這個機器人保留一個",
    ):
        Bot(fake).move_forward(1)

    assert fake.commands == []
    assert fake.history == []


@pytest.mark.parametrize("removal", ["objective", "score"])
def test_server_grid_cache_invalidates_and_falls_back(removal: str) -> None:
    fake = ServerGridJs()
    bot = Bot(fake)
    bot.move_forward(1)

    if removal == "objective":
        del fake.scoreboards[fake.objective]
    else:
        del fake.scoreboards[fake.objective].itemsMap[fake.username]
    fake._step = 0.5

    bot.move_forward(1)

    assert fake.commands == [f"/trigger {fake.objective} set 11"]
    assert fake.history == [("forward", True), ("forward", False)]
    assert fake.scoreboards.iterations == 2


def test_server_grid_provider_can_be_rediscovered_after_rebuild() -> None:
    fake = ServerGridJs()
    bot = Bot(fake)
    bot.move_forward(1)

    del fake.scoreboards[fake.objective]
    fake._step = 0.5
    bot.move_forward(1)

    fake._step = 0.0
    fake.add_provider(fake.objective)
    bot.move_forward(1)

    assert fake.commands == [
        f"/trigger {fake.objective} set 11",
        f"/trigger {fake.objective} set 11",
    ]
    assert fake.score.value == -11
    assert fake.scoreboards.iterations == 3


@pytest.mark.parametrize(
    "title",
    [
        cmd._GRID_MOVE_PROVIDER_TITLE,
        f'"{cmd._GRID_MOVE_PROVIDER_TITLE}"',
        f'{{"text":"{cmd._GRID_MOVE_PROVIDER_TITLE}"}}',
        {"text": cmd._GRID_MOVE_PROVIDER_TITLE},
        {
            "text": "minethon:",
            "extra": [{"text": "grid_move:"}, {"text": "v1"}],
        },
        {"type": "string", "value": cmd._GRID_MOVE_PROVIDER_TITLE},
    ],
)
def test_server_grid_provider_title_plaintext_forms_match(title: object) -> None:
    fake = ServerGridJs(title=title)

    Bot(fake).move_forward(1)

    assert fake.commands == [f"/trigger {fake.objective} set 11"]


def test_server_grid_provider_title_requires_exact_plaintext() -> None:
    fake = ServerGridJs(
        title={
            "text": cmd._GRID_MOVE_PROVIDER_TITLE,
            "extra": [{"text": " extra"}],
        }
    )
    fake._step = 0.5

    Bot(fake).move_forward(1)

    assert fake.commands == []
    assert fake.history == [("forward", True), ("forward", False)]


def test_server_grid_uses_trigger_reenable_ack_when_score_is_not_broadcast() -> None:
    fake = ScorelessServerGridJs()

    pos = Bot(fake).move_forward(2)

    assert pos == (0.5, 64.0, -1.5)
    assert fake.commands == [
        f"/trigger {fake.objective} set 11",
        f"/trigger {fake.objective} set 21",
    ]
    assert fake.history == []
    assert all(query == ("/trigger ", True, False, 1000) for query in fake.tab_queries)


def test_server_grid_scoreless_provider_times_out_if_trigger_is_not_reenabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(cmd.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(cmd.time, "sleep", clock.sleep)
    fake = ScorelessServerGridJs(acknowledge=False)

    with pytest.raises(cmd.MinethonError, match="未重新啟用"):
        Bot(fake).move_forward(1)

    assert fake.commands == [f"/trigger {fake.objective} set 11"]
    assert fake.history == []
    assert clock.now >= cmd._GRID_MOVE_TIMEOUT


def test_server_grid_scoreless_provider_must_be_enabled_for_this_bot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _frozen_clock(monkeypatch)
    fake = ScorelessServerGridJs()
    fake.enabled = False
    fake._step = 0.5

    pos = Bot(fake).move_forward(1)

    assert pos == (0.5, 64.0, -0.5)
    assert fake.commands == []
    assert fake.history == [("forward", True), ("forward", False)]


def test_server_grid_rejects_multiple_enabled_scoreless_providers() -> None:
    fake = ScorelessServerGridJs(objective="maze.step")
    fake.scoreboards["parkour.move"] = SimpleNamespace(
        title=cmd._GRID_MOVE_PROVIDER_TITLE,
        itemsMap={},
    )
    fake.additional_enabled.add("parkour.move")

    with pytest.raises(
        cmd.MinethonError,
        match=r"maze\.step, parkour\.move.*只為這個機器人保留一個",
    ):
        Bot(fake).move_forward(1)

    assert fake.commands == []
    assert fake.history == []


def test_server_grid_scoreless_adversarial_sequence_never_reuses_ack() -> None:
    fake = ScorelessServerGridJs()
    bot = Bot(fake)
    cases = [
        ("move_forward", 0.0, (0.0, -1.0), 1),
        ("move_right", 0.0, (1.0, 0.0), 2),
        ("move_backward", 0.0, (0.0, 1.0), 3),
        ("move_left", 0.0, (-1.0, 0.0), 4),
        ("move_forward", cmd.math.pi / 2, (-1.0, 0.0), 4),
        ("move_forward", -cmd.math.pi / 2, (1.0, 0.0), 2),
        ("move_forward", cmd.math.pi, (0.0, 1.0), 3),
    ]
    expected_x = 0.5
    expected_z = 0.5

    for index in range(400):
        method, yaw, (dx, dz), direction = cases[index % len(cases)]
        fake.yaw = yaw
        fake.move = index % 7 != 0
        if fake.move:
            expected_x += dx
            expected_z += dz

        pos = getattr(bot, method)(1)
        sequence = index + 1
        expected_payload = sequence * cmd._GRID_MOVE_SEQUENCE_BASE + direction

        assert pos == (expected_x, 64.0, expected_z)
        assert fake.commands[-1] == (
            f"/trigger {fake.objective} set {expected_payload}"
        )
        assert fake.history == []


def test_server_grid_blocked_move_acknowledges_without_position_drift() -> None:
    fake = ServerGridJs(move=False)

    pos = Bot(fake).move_forward(1)

    assert pos == (0.5, 64.0, 0.5)
    assert fake.commands == [f"/trigger {fake.objective} set 11"]
    assert fake.score.value == -11


def test_server_grid_quantises_facing_before_request() -> None:
    fake = ServerGridJs()
    fake.yaw = cmd.math.pi / 2

    pos = Bot(fake).move_forward(1)

    assert pos == (-0.5, 64.0, 0.5)
    assert fake.commands == [f"/trigger {fake.objective} set 14"]


def test_server_grid_rejects_fractional_blocks() -> None:
    fake = ServerGridJs()

    with pytest.raises(ValueError, match="必須是整數"):
        Bot(fake).move_forward(1.5)

    assert fake.commands == []


def test_non_trigger_provider_times_out_with_criteria_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(cmd.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(cmd.time, "sleep", clock.sleep)
    fake = ServerGridJs(acknowledge=False)

    with pytest.raises(cmd.MinethonError, match="criteria 是 trigger，而不是 dummy"):
        Bot(fake).move_forward(1)

    assert fake.controls == {}
    assert clock.now >= cmd._GRID_MOVE_TIMEOUT


def test_server_grid_adversarial_sequence_never_drifts_or_reuses_ack() -> None:
    fake = ServerGridJs()
    bot = Bot(fake)
    cases = [
        ("move_forward", 0.0, (0.0, -1.0), 1),
        ("move_right", 0.0, (1.0, 0.0), 2),
        ("move_backward", 0.0, (0.0, 1.0), 3),
        ("move_left", 0.0, (-1.0, 0.0), 4),
        ("move_forward", cmd.math.pi / 2, (-1.0, 0.0), 4),
        ("move_forward", -cmd.math.pi / 2, (1.0, 0.0), 2),
        ("move_forward", cmd.math.pi, (0.0, 1.0), 3),
    ]
    expected_x = 0.5
    expected_z = 0.5

    for index in range(400):
        method, yaw, (dx, dz), direction = cases[index % len(cases)]
        fake.yaw = yaw
        fake.move = index % 7 != 0
        if fake.move:
            expected_x += dx
            expected_z += dz

        pos = getattr(bot, method)(1)
        sequence = index + 1
        expected_payload = sequence * cmd._GRID_MOVE_SEQUENCE_BASE + direction

        assert pos == (expected_x, 64.0, expected_z)
        assert fake.commands[-1] == (
            f"/trigger {fake.objective} set {expected_payload}"
        )
        assert fake.score.value == -expected_payload
        assert fake.history == []


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


def test_final_progress_sample_is_read_at_stall_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(cmd.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(cmd.time, "sleep", lambda _seconds: clock.sleep(1.0))
    fake = GridLockJs(clock, lock_seconds=cmd._WALK_STALL_TIMEOUT)

    pos = Bot(fake).move_forward(1.0)

    assert pos == (0.0, 64.0, -1.0)
    assert clock.now == cmd._WALK_STALL_TIMEOUT


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
