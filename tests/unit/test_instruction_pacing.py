"""Unit tests for the per-instruction pacing sleep and login-error framing."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

import minethon._commands as cmd
from minethon._bot_runtime import Bot, _is_bridge_failure, _looks_like_auth_error


class TurnJs:
    """Minimal fake exposing what set_turn / sneak need."""

    def __init__(self) -> None:
        self.entity = SimpleNamespace(yaw=0.0, pitch=0.0)
        self.calls: list[tuple] = []

    def look(self, yaw: float, pitch: float, force: bool) -> None:
        self.entity.yaw = yaw
        self.calls.append(("look", yaw, pitch, force))

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        self.calls.append(("setControlState", control, state))


@pytest.fixture
def paces(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record every _bridge_safe_sleep duration instead of really sleeping."""
    recorded: list[float] = []
    monkeypatch.setattr(cmd, "_bridge_safe_sleep", recorded.append)
    return recorded


def test_action_paces_once(paces: list[float]) -> None:
    Bot(TurnJs(), instruction_sleep=0.25).set_turn(90.0)
    assert paces == [0.25]


def test_turn_left_paces_exactly_once(paces: list[float]) -> None:
    # turn_left -> turn -> set_turn; only the set_turn leaf is paced.
    Bot(TurnJs(), instruction_sleep=0.2).turn_left()
    assert paces == [0.2]


def test_default_construction_does_not_pace(paces: list[float]) -> None:
    Bot(TurnJs()).set_turn(90.0)  # no instruction_sleep -> 0.0
    assert paces == [0.0]


def test_sneak_is_not_paced(paces: list[float]) -> None:
    # sneak stays unpaced so a toggle loop isn't throttled by the delay.
    Bot(TurnJs(), instruction_sleep=0.2).sneak(True)
    assert paces == []


def test_reads_are_not_paced(paces: list[float]) -> None:
    Bot(TurnJs(), instruction_sleep=0.2).get_yaw()
    assert paces == []


def test_bridge_safe_sleep_skips_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    waited: list[float] = []

    class FakeEvent:
        def wait(self, seconds: float) -> None:
            waited.append(seconds)

    monkeypatch.setattr(cmd.threading, "Event", FakeEvent)
    cmd._bridge_safe_sleep(0.0)
    cmd._bridge_safe_sleep(0.3)
    assert waited == [0.3]  # zero/negative durations are a no-op


def test_sneak_state_uses_control(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmd, "_bridge_safe_sleep", lambda _s: None)
    js = TurnJs()
    Bot(js, instruction_sleep=0.1).sneak(True)
    assert ("setControlState", "sneak", True) in js.calls


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Invalid credentials. Invalid username or password.", True),
        ("INVALID USERNAME OR PASSWORD", True),
        (" ECONNREFUSED 1.2.3.4:25565", False),
        ("", False),
    ],
)
def test_looks_like_auth_error(text: str, expected: bool) -> None:
    assert _looks_like_auth_error(text) is expected


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Timed out accessing 'setControlState'", True),
        ("Execution timed out", True),
        ("The JavaScript process has crashed. Please restart", True),
        ("NameError: name 'foo' is not defined", False),
        ("", False),
    ],
)
def test_is_bridge_failure(message: str, expected: bool) -> None:
    assert _is_bridge_failure(Exception(message)) is expected


def test_set_turn_still_returns_angles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmd, "_bridge_safe_sleep", lambda _s: None)
    js = TurnJs()
    yaw, pitch = Bot(js, instruction_sleep=0.1).set_turn(90.0)
    assert math.isclose(yaw, 90.0, abs_tol=1e-6)
    assert pitch == 0.0
