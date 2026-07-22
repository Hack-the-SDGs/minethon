"""Unit tests for the beginner-facing error-handling paths.

Covers the fixes from the 2026-07 adversarial review: handler exception
isolation, the pathfinder None guard, the bind() typo warning, bridge
call-timeout routing, and wait_spawn's Ctrl-C contract.
"""

from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest

import minethon._bot_runtime as rt
import minethon._commands as cmd
from minethon import EventAdaptor
from minethon._bot_runtime import Bot
from minethon.errors import PluginNotInstalledError

# ── handler exception isolation (C1-01) ──────────────────────────────


def test_handler_exception_is_isolated(capsys: pytest.CaptureFixture) -> None:
    # A bug in a student handler must not propagate back toward JS (an
    # unhandled rejection there kills the node process) — print and skip.
    def handler(username, message):
        raise ValueError("boom")

    wrapped = rt._normalize_handler(handler, emitter=object(), event_name="chat")

    assert wrapped("alice", "hi", None, None) is None
    out = capsys.readouterr().out
    assert "事件處理發生錯誤" in out
    assert "chat" in out
    assert "ValueError: boom" in out


def test_handler_keyboard_interrupt_still_propagates() -> None:
    def handler(_a):
        raise KeyboardInterrupt

    wrapped = rt._normalize_handler(handler, emitter=object())

    with pytest.raises(KeyboardInterrupt):
        wrapped("x")


# ── pathfinder guard against the real bridge's None (C1-02) ──────────


def test_missing_pathfinder_none_raises_user_facing_error() -> None:
    # The real JSPyBridge proxy answers None for missing JS attributes — it
    # never raises AttributeError like a plain Python object would.
    bot = Bot(SimpleNamespace(pathfinder=None))

    with pytest.raises(PluginNotInstalledError, match="load_plugin"):
        _ = bot.pathfinder


# ── bind() typo warning (C3-02) ──────────────────────────────────────


def test_bind_warns_on_unknown_handler_names(capsys: pytest.CaptureFixture) -> None:
    class Handlers(EventAdaptor):
        def on_chatt(self, *_a: Any) -> None:  # typo on purpose
            pass

    Bot(SimpleNamespace()).bind(Handlers())

    out = capsys.readouterr().out
    assert "on_chatt" in out
    assert "不是任何 mineflayer 事件" in out


def test_bind_stays_silent_for_known_handler_names(
    capsys: pytest.CaptureFixture,
) -> None:
    registered: list[str] = []

    def fake_on(_js: Any, event: str) -> Any:
        def register(fn: Any) -> Any:
            registered.append(event)
            return fn

        return register

    class Handlers(EventAdaptor):
        def on_spawn(self) -> None:
            pass

    original = rt.On
    rt.On = fake_on
    try:
        Bot(SimpleNamespace()).bind(Handlers())
    finally:
        rt.On = original

    assert registered == ["spawn"]
    assert "不是任何 mineflayer 事件" not in capsys.readouterr().out


# ── bridge call-timeout routing (C1-04 / C2-09) ──────────────────────


def test_is_bridge_failure_covers_per_call_timeout() -> None:
    exc = Exception(
        "Call to 'dig' timed out. Increase the timeout by setting the "
        "`timeout` keyword argument."
    )
    assert rt._is_bridge_failure(exc)


def test_excepthook_routes_call_timeout_to_friendly_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, Any] = {}

    def fake_stop(message: str, *, code: int = 0) -> None:
        recorded["message"] = message
        recorded["code"] = code

    monkeypatch.setattr(rt, "_stop_with_message", fake_stop)
    old_hook = sys.excepthook
    try:
        rt._install_quiet_interrupt()
        exc = Exception("Call to 'dig' timed out. Increase the timeout by ...")
        sys.excepthook(Exception, exc, None)
    finally:
        sys.excepthook = old_hook

    assert recorded == {"message": rt._CALL_TIMEOUT, "code": 1}


# ── wait_spawn honors the Ctrl-C contract (C1-03) ────────────────────


def test_wait_spawn_ctrl_c_stops_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    class InterruptingEvent:
        def set(self) -> None:
            pass

        def wait(self) -> None:
            raise KeyboardInterrupt

    recorded: dict[str, Any] = {}

    def fake_stop(message: str, *, code: int = 0) -> None:
        recorded["message"] = message
        recorded["code"] = code

    monkeypatch.setattr(cmd.threading, "Event", InterruptingEvent)
    monkeypatch.setattr(cmd, "Once", lambda *_a, **_k: lambda fn: fn)
    monkeypatch.setattr(rt, "_stop_with_message", fake_stop)

    Bot(SimpleNamespace(entity=None)).wait_spawn()

    assert recorded == {"message": rt._GOODBYE, "code": 0}
