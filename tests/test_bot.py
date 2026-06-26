from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import minethon._bot_runtime as bot_module
from minethon.errors import PluginNotInstalledError, VersionPinRequiredError

_normalize_handler: Any = cast("Any", bot_module)._normalize_handler


class _FakeJsBot:
    def loadPlugin(self, plugin: object) -> None:  # noqa: N802
        self.plugin = plugin


def test_decorator_event_api_removed() -> None:
    bot = bot_module.Bot(_FakeJsBot())

    assert not hasattr(bot_module.Bot, "on")
    assert not hasattr(bot_module.Bot, "once")
    with pytest.raises(AttributeError):
        _ = cast("Any", bot).on_chat
    with pytest.raises(AttributeError):
        _ = cast("Any", bot).once_chat


def test_normalize_handler_drops_injected_emitter_and_pads_missing_args() -> None:
    calls: list[tuple[object | None, object | None]] = []
    emitter = object()

    def handler(username: object | None, message: object | None) -> None:
        calls.append((username, message))

    wrapped = _normalize_handler(handler, emitter=emitter)
    wrapped(emitter, "alice")

    assert calls == [("alice", None)]


def test_missing_pathfinder_raises_user_facing_error() -> None:
    bot = bot_module.Bot(SimpleNamespace())

    with pytest.raises(PluginNotInstalledError):
        _ = bot.pathfinder


def test_require_without_version_rejects_unbundled_packages() -> None:
    bot = bot_module.Bot(_FakeJsBot())

    with pytest.raises(VersionPinRequiredError):
        bot.require("mineflayer-tool")


def test_bind_wires_only_overridden_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from minethon import EventAdaptor

    registered: list[str] = []

    def fake_on(js_bot: object, event: str):
        del js_bot

        def decorator(func: object) -> object:
            registered.append(event)
            return func

        return decorator

    monkeypatch.setattr(bot_module, "On", fake_on)
    bot = bot_module.Bot(_FakeJsBot())

    class MyHandlers(EventAdaptor):
        def on_chat(self, *_args: object, **_kwargs: object) -> None:
            pass

        def on_spawn(self, *_args: object, **_kwargs: object) -> None:
            pass

    returned = bot.bind(MyHandlers())

    assert isinstance(returned, MyHandlers)
    assert set(registered) == {"chat", "spawn"}


def test_bind_skips_methods_not_overridden(monkeypatch: pytest.MonkeyPatch) -> None:
    from minethon import EventAdaptor

    registered: list[str] = []

    def fake_on(js_bot: object, event: str):
        del js_bot

        def decorator(func: object) -> object:
            registered.append(event)
            return func

        return decorator

    monkeypatch.setattr(bot_module, "On", fake_on)
    bot = bot_module.Bot(_FakeJsBot())

    bot.bind(EventAdaptor())

    assert registered == []
