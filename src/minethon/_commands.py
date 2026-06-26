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
import time
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

# Movement: no "walk N blocks" primitive without pathfinder, so move_* presses a
# control key and polls position until the horizontal distance travelled reaches
# the target (or a safety timeout fires). 4.317 b/s is vanilla walking speed.
# Ref: mineflayer/docs/api.md — bot.setControlState; Minecraft physics.
_WALK_SPEED_BPS = 4.317
_POLL_SECONDS = 0.05  # ~one physics tick
_WALK_TIMEOUT_FACTOR = 3.0  # allow 3x the ideal travel time before giving up
_WALK_TIMEOUT_FLOOR = 1.0  # always allow at least 1s (short hops)
_JUMP_SECONDS = 0.1  # hold 'jump' briefly to trigger a single hop
_DEGREES_PER_TURN = 90.0  # turn_left / turn_right default quarter turn

# Size level <-> entity "scale" attribute. get_height reads the server-reported
# scale; set_height writes it locally (best-effort) and validates the 1..5 range.
# Ref: mineflayer lib/plugins/entities.js (entity.attributes[key] = {value,
# modifiers}) + explosion.js getAttributeValue (base + operation 0/1/2 modifiers).
_MIN_HEIGHT = 1
_MAX_HEIGHT = 5
_DEFAULT_SCALE_KEY = "minecraft:generic.scale"
# Attribute modifier operations. Ref: mineflayer lib/plugins/explosion.js.
_OP_ADD = 0  # add amount to the base value
_OP_ADD_FRACTION_OF_BASE = 1  # add base * amount
_OP_MULTIPLY_TOTAL = 2  # multiply the running total by (1 + amount)

# Raycast face index (0..5) -> unit offset for placeBlock's faceVector.
# Ref: mineflayer lib/plugins/digging.js (rayBlock.face) + Minecraft face order.
_FACE_VECTORS = (
    (0, -1, 0),  # 0: bottom (-Y)
    (0, 1, 0),  # 1: top (+Y)
    (0, 0, -1),  # 2: north (-Z)
    (0, 0, 1),  # 3: south (+Z)
    (-1, 0, 0),  # 4: west (-X)
    (1, 0, 0),  # 5: east (+X)
)


def _norm_deg(deg: float) -> float:
    """Normalise an angle to the ``[0, 360)`` range."""
    return deg % 360.0


def _make_vec3(x: float, y: float, z: float) -> Any:
    """Construct a mineflayer ``Vec3`` proxy from coordinates.

    Ref: vec3 module — the package export is callable as ``vec3(x, y, z)``.
    """
    return get_vec3()(x, y, z)


def _walk_timeout(blocks: float) -> float:
    """Safety deadline (seconds) for walking ``blocks`` so a stuck bot stops."""
    return max(
        _WALK_TIMEOUT_FLOOR, abs(blocks) / _WALK_SPEED_BPS * _WALK_TIMEOUT_FACTOR
    )


def _attribute_value(prop: Any) -> float:
    """Effective value of an entity attribute (base + modifiers).

    Mirrors mineflayer's ``getAttributeValue`` (lib/plugins/explosion.js):
    operation 0 adds to the base, 1 adds ``base*amount``, 2 multiplies the
    running total. Uses subscript access so it works on both a JS object
    proxy and a plain dict.
    """
    base = float(prop["value"])
    raw = prop["modifiers"]
    modifiers = list(raw) if raw is not None else []
    base += sum(float(m["amount"]) for m in modifiers if int(m["operation"]) == _OP_ADD)
    value = base + sum(
        base * float(m["amount"])
        for m in modifiers
        if int(m["operation"]) == _OP_ADD_FRACTION_OF_BASE
    )
    for m in modifiers:
        if int(m["operation"]) == _OP_MULTIPLY_TOTAL:
            value += value * float(m["amount"])
    return value


def _scale_key(attributes: Any) -> str | None:
    """First attribute key naming the entity scale, or ``None``."""
    for key in attributes:
        if "scale" in str(key):
            return str(key)
    return None


def _read_scale(entity: Any) -> float:
    """Server-reported scale of ``entity``; ``1.0`` when no scale attribute."""
    attributes = getattr(entity, "attributes", None)
    if attributes is None:
        return 1.0
    key = _scale_key(attributes)
    if key is None:
        return 1.0
    return _attribute_value(attributes[key])


def _scale_to_level(scale: float) -> int:
    """Round + clamp a raw scale onto the ``1..5`` size-level range."""
    return max(_MIN_HEIGHT, min(_MAX_HEIGHT, round(scale)))


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

    # ── movement ──────────────────────────────────────────────────────
    def _walk(self, control: str, blocks: float) -> tuple[float, float, float]:
        """Hold ``control`` until the bot travels ``blocks`` horizontally.

        Movement is relative to the bot's current facing. Stops early on a
        safety timeout so walking into a wall can't hang the script.
        Ref: mineflayer/docs/api.md — bot.setControlState(control, state).
        """
        if blocks <= 0:
            return self.get_pos()
        start = self._entity().position
        sx, sz = float(start.x), float(start.z)
        self._js.setControlState(control, True)
        deadline = time.monotonic() + _walk_timeout(blocks)
        try:
            while time.monotonic() < deadline:
                pos = self._entity().position
                if math.hypot(float(pos.x) - sx, float(pos.z) - sz) >= blocks:
                    break
                time.sleep(_POLL_SECONDS)
        finally:
            self._js.setControlState(control, False)
        return self.get_pos()

    def move_forward(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Walk forward ``blocks`` blocks; returns the new position."""
        return self._walk("forward", blocks)

    def move_backward(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Walk backward ``blocks`` blocks; returns the new position."""
        return self._walk("back", blocks)

    def move_left(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Strafe left ``blocks`` blocks; returns the new position."""
        return self._walk("left", blocks)

    def move_right(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Strafe right ``blocks`` blocks; returns the new position."""
        return self._walk("right", blocks)

    def jump(self) -> tuple[float, float, float]:
        """Jump once; returns the position right after the hop begins.

        Ref: mineflayer/docs/api.md — bot.setControlState('jump', state).
        """
        self._js.setControlState("jump", True)
        time.sleep(_JUMP_SECONDS)
        self._js.setControlState("jump", False)
        return self.get_pos()

    # ── orientation (write) ───────────────────────────────────────────
    def set_turn(self, yaw: float) -> tuple[float, float]:
        """Face an absolute ``yaw`` (degrees); returns the new ``(yaw, pitch)``.

        ``0`` faces -Z (north); larger yaw turns counter-clockwise. Pitch is
        left unchanged. Ref: mineflayer/docs/api.md — bot.look(yaw, pitch, force).
        """
        entity = self._entity()
        self._js.look(math.radians(yaw), float(entity.pitch), True)
        return (self.get_yaw(), self.get_pitch())

    def turn(self, degrees: float) -> tuple[float, float]:
        """Turn ``degrees`` relative to the current facing (positive = left).

        Returns the new ``(yaw, pitch)`` in degrees.
        """
        return self.set_turn(self.get_yaw() + degrees)

    def turn_left(self) -> tuple[float, float]:
        """Turn 90° to the left; returns the new ``(yaw, pitch)``."""
        return self.turn(_DEGREES_PER_TURN)

    def turn_right(self) -> tuple[float, float]:
        """Turn 90° to the right; returns the new ``(yaw, pitch)``."""
        return self.turn(-_DEGREES_PER_TURN)

    def look_at(self, x: int, y: int, z: int) -> tuple[float, float]:
        """Face the exact point ``(x, y, z)``; returns the new ``(yaw, pitch)``.

        Ref: mineflayer/docs/api.md — bot.lookAt(point, force).
        """
        self._js.lookAt(_make_vec3(x, y, z), True)
        return (self.get_yaw(), self.get_pitch())

    # ── size ──────────────────────────────────────────────────────────
    def get_height(self) -> int:
        """Current size level ``1..5`` from the server-reported scale attribute.

        Returns ``1`` when the server has not sent a scale. Ref: mineflayer
        lib/plugins/entities.js — entity.attributes.
        """
        return _scale_to_level(_read_scale(self._entity()))

    def set_height(self, level: int) -> None:
        """Request a size ``level`` in ``1..5``; raises ``ValueError`` otherwise.

        Writes the scale attribute locally so :meth:`get_height` round-trips.
        Note: an entity's scale is server-authoritative — the competition
        server's plugin is what actually resizes the model in-world.
        """
        if not _MIN_HEIGHT <= level <= _MAX_HEIGHT:
            msg = f"大小等級只能是 {_MIN_HEIGHT}~{_MAX_HEIGHT}，收到 {level}。"
            raise ValueError(msg)
        entity = self._entity()
        prop = {"value": float(level), "modifiers": []}
        attributes = getattr(entity, "attributes", None)
        if attributes is None:
            # ponytail: create the whole attributes object in one assignment so
            # the bridge never has to mutate a nested proxy in place.
            entity.attributes = {_DEFAULT_SCALE_KEY: prop}
            return
        attributes[_scale_key(attributes) or _DEFAULT_SCALE_KEY] = prop

    # ── items ─────────────────────────────────────────────────────────
    def _find_inventory_item(self, name: str) -> Any:
        """First inventory item named ``name`` or ``None``.

        Ref: mineflayer/docs/api.md — bot.inventory.items() (prismarine-windows).
        """
        for item in self._js.inventory.items():
            if str(item.name) == name:
                return item
        return None

    def hold(self, name: str) -> bool:
        """Equip the inventory item named ``name`` in the main hand.

        Returns ``True`` on success, ``False`` if the item is not carried.
        Ref: mineflayer/docs/api.md — bot.equip(item, 'hand').
        """
        item = self._find_inventory_item(name)
        if item is None:
            return False
        self._js.equip(item, "hand")
        return True

    def unhold(self) -> bool:
        """Move the held item back into the inventory.

        Returns ``False`` if the hand was already empty.
        Ref: mineflayer/docs/api.md — bot.unequip('hand').
        """
        if self._js.heldItem is None:
            return False
        self._js.unequip("hand")
        return True

    def drop(self) -> bool:
        """Throw the entire held stack onto the ground.

        Returns ``False`` if the hand was empty. Ref: mineflayer/docs/api.md —
        bot.tossStack(item).
        """
        item = self._js.heldItem
        if item is None:
            return False
        self._js.tossStack(item)
        return True

    # ── actions (on the block/face being aimed at) ────────────────────
    def dig(self) -> tuple[tuple[int, int, int], str] | None:
        """Break the block currently aimed at; returns its ``((x, y, z), name)``.

        Returns ``None`` when nothing is in reach. (This renames mineflayer's
        ``break`` action.) Ref: mineflayer/docs/api.md — bot.dig(block).
        """
        block = self._js.blockAtCursor(_REACH_BLOCKS)
        if block is None:
            return None
        p = block.position
        result = ((int(p.x), int(p.y), int(p.z)), str(block.name))
        self._js.dig(block)
        return result

    def place(self) -> tuple[tuple[int, int, int], str] | None:
        """Place the held block against the face being aimed at.

        Returns the new block's ``((x, y, z), name)`` or ``None`` if nothing is
        in reach. Ref: mineflayer/docs/api.md — bot.placeBlock(ref, faceVector).
        """
        ref = self._js.blockAtCursor(_REACH_BLOCKS)
        if ref is None:
            return None
        offset = _FACE_VECTORS[int(ref.face)]
        self._js.placeBlock(ref, _make_vec3(*offset))
        rp = ref.position
        pos = (int(rp.x) + offset[0], int(rp.y) + offset[1], int(rp.z) + offset[2])
        placed = self._js.blockAt(_make_vec3(*pos))
        name = str(placed.name) if placed is not None else ""
        return (pos, name)

    def use(self) -> bool:
        """Right-click: interact with the aimed block, else use the held item.

        Ref: mineflayer/docs/api.md — bot.activateBlock / bot.activateItem.
        """
        block = self._js.blockAtCursor(_REACH_BLOCKS)
        if block is not None:
            self._js.activateBlock(block)
        else:
            self._js.activateItem()
        return True

    def sneak(self, on: bool) -> bool:
        """Hold or release sneak (a persistent state); returns ``on``.

        Ref: mineflayer/docs/api.md — bot.setControlState('sneak', state).
        """
        self._js.setControlState("sneak", on)
        return on

    # ── chat ──────────────────────────────────────────────────────────
    def chat(self, obj: object) -> None:
        """Send ``obj`` (converted to text) as a normal public chat message.

        Group-only visibility is handled server-side by the competition's
        chat plugin — the bot just sends and receives normally.
        Ref: mineflayer/docs/api.md — bot.chat(message).
        """
        self._js.chat(str(obj))
