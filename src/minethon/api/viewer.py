"""Public API for the web 3D viewer (prismarine-viewer).

Type B service — wraps the private ``_bridge.services.viewer.ViewerService``
so that the public SDK does not expose ``_bridge`` types.

Ref: prismarine-viewer/lib/mineflayer.js
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from minethon._bridge.services.viewer import ViewerService


class ViewerAPI:
    """Web 3D viewer (prismarine-viewer).

    Type B service — lazy-initialised on first access via ``bot.viewer``.
    Call ``await bot.viewer.start()`` to launch the HTTP server and
    ``bot.viewer.stop()`` to shut it down.  The viewer is automatically
    stopped on ``disconnect()``.

    Ref: prismarine-viewer/lib/mineflayer.js
    """

    def __init__(self, service: ViewerService) -> None:
        self._service = service

    async def start(
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

        Raises:
            BridgeError: If the viewer module fails to initialise.

        Ref: prismarine-viewer/lib/mineflayer.js — module.exports
        """
        await self._service.start(
            port=port,
            view_distance=view_distance,
            first_person=first_person,
        )

    def stop(self) -> None:
        """Close the viewer.  Best-effort cleanup.

        Safe to call when the viewer has not been started.

        Ref: prismarine-viewer/lib/mineflayer.js — bot.viewer.close()
        """
        self._service.stop()

    @property
    def is_started(self) -> bool:
        """Whether the viewer HTTP server is currently running."""
        return self._service.is_started
