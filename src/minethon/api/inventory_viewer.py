"""Public API for the web inventory viewer (mineflayer-web-inventory).

Type B service — wraps the private
``_bridge.services.web_inventory.WebInventoryService`` so that the
public SDK does not expose ``_bridge`` types.

Ref: mineflayer-web-inventory/index.js
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from minethon._bridge.services.web_inventory import WebInventoryService


class InventoryViewerAPI:
    """Web inventory viewer (mineflayer-web-inventory).

    Type B service — lazily created on first access via
    ``bot.inventory_viewer``.  Call ``bot.inventory_viewer.initialize()``
    before using ``start()`` / ``stop()``.

    Ref: mineflayer-web-inventory/index.js
    """

    def __init__(self, service: WebInventoryService) -> None:
        self._service = service

    def initialize(self, port: int = 3008) -> None:
        """Require the npm module and attach it to the bot.

        The HTTP server is **not** started automatically.  Call
        :meth:`start` after initialisation to begin serving.

        This is a **synchronous blocking** call because JSPyBridge is
        thread-affine.  The first call may take a while if Node.js
        needs to install the npm package.

        Args:
            port: TCP port for the web inventory UI.  Fixed at
                initialisation; ``start()``/``stop()`` do not accept a
                port parameter.

        Raises:
            BridgeError: If already initialised.

        Ref: mineflayer-web-inventory/index.js:5 —
             ``module.exports = function (bot, options = {})``
        """
        self._service.initialize(port=port)

    async def start(self) -> None:
        """Start the web inventory HTTP server.

        Raises:
            BridgeError: If not initialised, already running, or the
                JS ``start()`` Promise rejects.

        Ref: mineflayer-web-inventory/index.js —
             ``bot.webInventory.start()``
        """
        await self._service.start()

    async def stop(self) -> None:
        """Stop the web inventory HTTP server.

        Raises:
            BridgeError: If not initialised, not running, or the
                JS ``stop()`` Promise rejects.

        Ref: mineflayer-web-inventory/index.js —
             ``bot.webInventory.stop()``
        """
        await self._service.stop()

    @property
    def is_running(self) -> bool:
        """Whether the web inventory HTTP server is currently running."""
        return self._service.is_running

    @property
    def is_initialized(self) -> bool:
        """Whether the service has been initialised."""
        return self._service.is_initialized

    @property
    def port(self) -> int | None:
        """The TCP port the service was initialised with, or ``None``."""
        return self._service.port
