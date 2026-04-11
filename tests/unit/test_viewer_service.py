"""Unit tests for ViewerService (prismarine-viewer bridge)."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from minethon._bridge._events import ViewerStartDoneEvent
from minethon._bridge.event_relay import EventRelay
from minethon._bridge.services.viewer import ViewerService
from minethon.bot import Bot
from minethon.models.errors import BridgeError, MinethonConnectionError


class TestViewerServiceLifecycle:
    """Tests for ViewerService start/stop/is_started behavior."""

    def _make_service(self) -> tuple[ViewerService, MagicMock, EventRelay]:
        runtime = MagicMock()
        js_bot = MagicMock()
        relay = EventRelay()
        relay.set_loop(asyncio.get_running_loop())
        service = ViewerService(runtime, js_bot, relay)
        return service, runtime, relay

    @pytest.mark.asyncio
    async def test_initial_state(self) -> None:
        service, _rt, _relay = self._make_service()
        assert service.is_started is False

    @pytest.mark.asyncio
    async def test_start_success(self) -> None:
        service, runtime, relay = self._make_service()
        runtime.require.return_value = MagicMock()

        async def post_done() -> None:
            await asyncio.sleep(0.01)
            relay._dispatch(
                ViewerStartDoneEvent,
                ViewerStartDoneEvent(error=None),
            )

        asyncio.create_task(post_done())
        await service.start(port=8080, view_distance=4, first_person=True)
        assert service.is_started is True

    @pytest.mark.asyncio
    async def test_start_error(self) -> None:
        service, runtime, relay = self._make_service()
        runtime.require.return_value = MagicMock()

        async def post_error() -> None:
            await asyncio.sleep(0.01)
            relay._dispatch(
                ViewerStartDoneEvent,
                ViewerStartDoneEvent(error="module not found"),
            )

        asyncio.create_task(post_error())
        with pytest.raises(BridgeError, match="viewer start failed"):
            await service.start()
        assert service.is_started is False

    @pytest.mark.asyncio
    async def test_start_idempotent(self) -> None:
        service, runtime, relay = self._make_service()
        runtime.require.return_value = MagicMock()

        async def post_done() -> None:
            await asyncio.sleep(0.01)
            relay._dispatch(
                ViewerStartDoneEvent,
                ViewerStartDoneEvent(error=None),
            )

        asyncio.create_task(post_done())
        await service.start()
        # Second call should be no-op
        await service.start()
        assert service.is_started is True

    def test_stop_when_not_started(self) -> None:
        runtime = MagicMock()
        js_bot = MagicMock()
        relay = MagicMock()
        service = ViewerService(runtime, js_bot, relay)
        service.stop()  # no-op, no error
        assert service.is_started is False

    @pytest.mark.asyncio
    async def test_stop_after_start(self) -> None:
        service, runtime, relay = self._make_service()
        runtime.require.return_value = MagicMock()

        async def post_done() -> None:
            await asyncio.sleep(0.01)
            relay._dispatch(
                ViewerStartDoneEvent,
                ViewerStartDoneEvent(error=None),
            )

        asyncio.create_task(post_done())
        await service.start()
        service.stop()
        assert service.is_started is False

    def test_stop_swallows_attribute_error(self) -> None:
        runtime = MagicMock()
        js_bot = MagicMock()
        relay = MagicMock()
        service = ViewerService(runtime, js_bot, relay)
        service._started = True  # force started state
        js_bot.viewer.close.side_effect = AttributeError("gone")
        service.stop()  # should not raise
        assert service.is_started is False


class TestBotViewerProperty:
    """Tests for Bot.viewer lazy property."""

    def test_viewer_raises_when_not_connected(self) -> None:
        bot = Bot(host="localhost")
        with pytest.raises(MinethonConnectionError):
            _ = bot.viewer

    @pytest.mark.asyncio
    async def test_viewer_cleared_after_disconnect(self) -> None:
        bot = Bot(host="localhost")
        service = MagicMock()
        bot._viewer_service = service  # pyright: ignore[reportAttributeAccessIssue]
        await bot.disconnect()
        service.stop.assert_called_once()
        assert bot._viewer_service is None  # pyright: ignore[reportAttributeAccessIssue]
