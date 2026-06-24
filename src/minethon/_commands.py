"""Synchronous, beginner-facing command surface for :class:`Bot`.

Everything here is **blocking** and speaks **native Python types** (tuples,
``str``, ``bool``, ``int``) — no ``Vec3``/``Block``/``Item`` objects, no
pathfinder, no ``await``. The mixin is folded into
:class:`minethon._bot_runtime.Bot`; each method delegates to the mineflayer
JS proxy through ``self._js``. mineflayer Promises are awaited by JSPyBridge
before the call returns, so a student script reads as straight-line code::

    bot.wait_spawn()
    bot.move_forward(3)
    bot.turn_right()
    bot.dig()

Source of truth: mineflayer ``docs/api.md`` (pinned 4.37.0). Every JS call
below cites the api.md / lib section it relies on.
"""

from __future__ import annotations

import math
import threading
from typing import Any

from javascript import Once

from minethon._bridge import get_vec3
from minethon.errors import NotSpawnedError

# Cursor reach for "what am I aiming at" — covers look_block/dig/place. Slightly
# beyond survival reach (~4.5 blocks) so creative interaction still resolves.
# Ref: mineflayer/docs/api.md — bot.blockAtCursor(maxDistance).
_REACH_BLOCKS = 6.0
# Default search radius for find_block / find_blocks.
# Ref: mineflayer/docs/api.md — bot.findBlocks(options.maxDistance) (default 16).
_FIND_MAX_DISTANCE = 64


def _norm_deg(deg: float) -> float:
    """Normalise an angle to the ``[0, 360)`` range."""
    return deg % 360.0


def _make_vec3(x: float, y: float, z: float) -> Any:
    """Construct a mineflayer ``Vec3`` proxy from coordinates.

    Ref: vec3 module — the package export is callable as ``vec3(x, y, z)``.
    """
    return get_vec3()(x, y, z)


class Commands:
    """Curated synchronous commands mixed into :class:`Bot`.

    Relies on ``self._js`` (the mineflayer proxy) being set by
    ``Bot.__init__``. Kept in its own module so the runtime façade
    (``_bot_runtime.py``) stays focused on bridge/event plumbing.
    """

    _js: Any  # the mineflayer JS bot proxy, set by Bot.__init__

    # ── internal helpers ──────────────────────────────────────────────
    def _entity(self) -> Any:
        """Return ``bot.entity`` or raise if the bot has not spawned yet.

        Ref: mineflayer/docs/api.md — bot.entity (undefined before spawn).
        """
        entity = getattr(self._js, "entity", None)
        if entity is None:
            msg = "機器人還沒進入世界。請先呼叫 bot.wait_spawn()。"
            raise NotSpawnedError(msg)
        return entity

    # ── lifecycle ─────────────────────────────────────────────────────
    def wait_spawn(self) -> None:
        """Block until the bot has spawned into the world.

        Returns immediately if already spawned. Lets a student write a
        straight-line script that starts acting only once it is in-world.

        Ref: mineflayer/docs/api.md — 'spawn' event, bot.entity.
        """
        if getattr(self._js, "entity", None) is not None:
            return
        done = threading.Event()

        def _on_spawn(*_a: Any, **_k: Any) -> None:
            done.set()

        Once(self._js, "spawn")(_on_spawn)
        # Race guard: spawn may have fired between the check above and the
        # listener registration — re-check so we never wait on a past event.
        if getattr(self._js, "entity", None) is not None:
            done.set()
        try:
            done.wait()
        except KeyboardInterrupt:
            pass

    def wait(self, seconds: float) -> None:
        """Sleep for ``seconds`` while staying connected.

        The JSPyBridge Node thread keeps the bot's connection alive during
        the sleep, so this is a safe pause between actions.
        """
        # ponytail: plain sleep — the bridge's event thread drives the bot
        # independently of the Python main thread, so the connection holds.
        threading.Event().wait(seconds)

    # ── position & orientation (read) ─────────────────────────────────
    def get_x(self) -> float:
        """Current X coordinate."""
        return float(self._entity().position.x)

    def get_y(self) -> float:
        """Current Y coordinate (height)."""
        return float(self._entity().position.y)

    def get_z(self) -> float:
        """Current Z coordinate."""
        return float(self._entity().position.z)

    def get_pos(self) -> tuple[float, float, float]:
        """Current position as ``(x, y, z)``."""
        p = self._entity().position
        return (float(p.x), float(p.y), float(p.z))

    def get_yaw(self) -> float:
        """Current horizontal facing in degrees, normalised to ``[0, 360)``.

        ``0`` faces -Z (north); increasing yaw turns counter-clockwise
        (toward -X / west). Ref: mineflayer/docs/api.md — bot.look (yaw).
        """
        return _norm_deg(math.degrees(float(self._entity().yaw)))

    def get_pitch(self) -> float:
        """Current vertical facing in degrees (``+90`` up, ``-90`` down)."""
        return math.degrees(float(self._entity().pitch))

    # ── state (read) ──────────────────────────────────────────────────
    def get_sneak(self) -> bool:
        """Whether the bot is currently sneaking.

        Ref: mineflayer/docs/api.md — bot.getControlState('sneak').
        """
        return bool(self._js.getControlState("sneak"))

    def get_hand(self) -> tuple[str, int] | None:
        """Held item as ``(name, count)`` or ``None`` when empty-handed.

        Ref: mineflayer/docs/api.md — bot.heldItem (prismarine-item).
        """
        item = self._js.heldItem
        if item is None:
            return None
        return (str(item.name), int(item.count))

    # ── world sensing (read) ──────────────────────────────────────────
    def _block_id(self, name: str) -> int | None:
        """Resolve a block name to its numeric id via the bot's registry.

        Ref: mineflayer/docs/api.md — bot.registry (minecraft-data) blocksByName.
        """
        entry = self._js.registry.blocksByName[name]
        if entry is None:
            return None
        return int(entry.id)

    def get_block(self, x: int, y: int, z: int) -> str | None:
        """Name of the block at ``(x, y, z)`` or ``None`` if that point is unloaded.

        Ref: mineflayer/docs/api.md — bot.blockAt(point).
        """
        block = self._js.blockAt(_make_vec3(x, y, z))
        if block is None:
            return None
        return str(block.name)

    def look_block(self) -> tuple[tuple[int, int, int], str] | None:
        """Block currently aimed at as ``((x, y, z), name)``, or ``None``.

        Ref: mineflayer/docs/api.md — bot.blockAtCursor(maxDistance).
        """
        block = self._js.blockAtCursor(_REACH_BLOCKS)
        if block is None:
            return None
        p = block.position
        return ((int(p.x), int(p.y), int(p.z)), str(block.name))

    def find_block(self, name: str) -> tuple[int, int, int] | None:
        """Nearest block named ``name`` as ``(x, y, z)`` or ``None``.

        Ref: mineflayer/docs/api.md — bot.findBlock(options) + bot.registry.
        """
        block_id = self._block_id(name)
        if block_id is None:
            return None
        block = self._js.findBlock(
            {"matching": block_id, "maxDistance": _FIND_MAX_DISTANCE}
        )
        if block is None:
            return None
        p = block.position
        return (int(p.x), int(p.y), int(p.z))

    def find_blocks(
        self,
        name: str,
        max: int = 16,  # noqa: A002 — public student-facing name from IDEA.md spec
    ) -> list[tuple[int, int, int]]:
        """Up to ``max`` nearest blocks named ``name``, closest first.

        Returns an empty list when the name is unknown or none are found.
        Ref: mineflayer/docs/api.md — bot.findBlocks(options) (returns coords).
        """
        block_id = self._block_id(name)
        if block_id is None:
            return []
        points = self._js.findBlocks(
            {"matching": block_id, "maxDistance": _FIND_MAX_DISTANCE, "count": max}
        )
        return [(int(p.x), int(p.y), int(p.z)) for p in points]
