"""ViewerService — prismarine-viewer bridge (Type B service).

prismarine-viewer is NOT loaded via ``bot.loadPlugin()``.  It is
initialized by calling ``require('prismarine-viewer').mineflayer(bot, opts)``
directly, which starts an Express + Socket.IO HTTP server for a
web-based 3D viewer.

Ref: prismarine-viewer/lib/mineflayer.js — module.exports
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from minethon._bridge.runtime import BridgeRuntime


class ViewerService:
    """Web 3D viewer service (prismarine-viewer).

    Type B plugin -- standalone service, not loaded via ``bot.loadPlugin()``.

    Ref: prismarine-viewer/lib/mineflayer.js
    """

    def __init__(self, runtime: BridgeRuntime, js_bot: Any) -> None:
        self._runtime = runtime
        self._js_bot = js_bot
        self._started = False

    def start(
        self,
        *,
        port: int = 3007,
        view_distance: int = 6,
        first_person: bool = False,
    ) -> None:
        """Start the web viewer.  Opens an HTTP server on *port*.

        Calling ``start()`` when the viewer is already running is a
        no-op (idempotent).

        Args:
            port: HTTP port for the viewer (default 3007).
            view_distance: Render distance in chunks.
            first_person: Enable first-person camera.

        Ref: prismarine-viewer/lib/mineflayer.js — module.exports
        """
        if self._started:
            return
        mod = self._runtime.require("prismarine-viewer")
        mod.mineflayer(
            self._js_bot,
            {
                "viewDistance": view_distance,
                "firstPerson": first_person,
                "port": port,
            },
        )
        self._started = True

    def stop(self) -> None:
        """Close the viewer.  Best-effort cleanup.

        Safe to call when the viewer has not been started.

        Ref: prismarine-viewer/lib/mineflayer.js — bot.viewer.close()
        """
        if not self._started:
            return
        try:
            self._js_bot.viewer.close()
        except (AttributeError, TypeError):
            pass
        self._started = False

    @property
    def is_started(self) -> bool:
        """Whether the viewer HTTP server is currently running."""
        return self._started
