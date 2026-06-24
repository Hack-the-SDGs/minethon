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

from minethon.errors import NotSpawnedError


def _norm_deg(deg: float) -> float:
    """Normalise an angle to the ``[0, 360)`` range."""
    return deg % 360.0


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
