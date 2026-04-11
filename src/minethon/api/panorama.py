"""Panorama and image capture API.

.. warning:: **Experimental.** Requires native ``node-canvas-webgl``
   build. mineflayer-panorama 0.0.1 — API may be unstable.

Ref: mineflayer-panorama/index.js
"""

import asyncio
from typing import TYPE_CHECKING, Any

from minethon._bridge._events import PanoramaDoneEvent, PictureDoneEvent
from minethon.models.errors import BridgeError

if TYPE_CHECKING:
    from minethon._bridge.event_relay import EventRelay
    from minethon._bridge.plugins.panorama import PanoramaBridge
    from minethon.models.vec3 import Vec3


class PanoramaAPI:
    """Panorama and image capture API.

    .. warning:: **Experimental.** Requires native ``node-canvas-webgl``.
       mineflayer-panorama 0.0.1 — API may be unstable.

    Example::

        await bot.plugins.load("mineflayer-panorama")
        stream = await bot.panorama.take_panorama()

    Ref: mineflayer-panorama/index.js
    """

    def __init__(
        self,
        bridge: PanoramaBridge,
        relay: EventRelay,
    ) -> None:
        self._bridge = bridge
        self._relay = relay
        self._panorama_lock = asyncio.Lock()
        self._picture_lock = asyncio.Lock()

    async def take_panorama(
        self, camera_height: float | None = None
    ) -> Any:
        """Take a 360-degree panorama. Returns JPEG stream proxy.

        Args:
            camera_height: Camera height above the bot. ``None`` for
                default (height 10), or a float for custom height.

        Returns:
            The JPEG stream proxy from the JS side.

        Raises:
            BridgeError: If the capture fails or times out.

        Ref: mineflayer-panorama/lib/camera.js:51-56 — camPos handling
        """
        async with self._panorama_lock:
            self._bridge.start_take_panorama(camera_height)
            try:
                event = await self._relay.wait_for(
                    PanoramaDoneEvent, timeout=60.0
                )
            except TimeoutError as exc:
                raise BridgeError("panorama capture timed out") from exc
            if event.error is not None:
                raise BridgeError(f"panorama capture failed: {event.error}")
            return event.result

    async def take_picture(self, point: Vec3, direction: Vec3) -> Any:
        """Take a single picture at a point looking in a direction.

        Args:
            point: Camera position as a Vec3.
            direction: Look direction as a Vec3.

        Returns:
            The JPEG stream proxy from the JS side.

        Raises:
            BridgeError: If the capture fails or times out.

        Ref: mineflayer-panorama/lib/camera.js — ``takePicture(point, direction)``
        """
        async with self._picture_lock:
            self._bridge.start_take_picture(
                point.x, point.y, point.z,
                direction.x, direction.y, direction.z,
            )
            try:
                event = await self._relay.wait_for(
                    PictureDoneEvent, timeout=60.0
                )
            except TimeoutError as exc:
                raise BridgeError("picture capture timed out") from exc
            if event.error is not None:
                raise BridgeError(f"picture capture failed: {event.error}")
            return event.result
