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

import contextlib
import json
import math
import threading
import time
import warnings
from functools import wraps
from typing import TYPE_CHECKING, Any, cast

from javascript import Once

from minethon._bridge import get_vec3
from minethon.errors import MinethonError, NotSpawnedError, PlayerNotFoundError

if TYPE_CHECKING:
    from collections.abc import Callable

# Cursor reach for "what am I aiming at" — covers look_block/dig/place. Slightly
# beyond survival reach (~4.5 blocks) so creative interaction still resolves.
# Ref: mineflayer/docs/api.md — bot.blockAtCursor(maxDistance).
_REACH_BLOCKS = 6.0
# Names that aren't worth digging — dig() skips these when picking the block in
# front so it never "breaks" empty space. Ref: minecraft-data block names.
_NON_SOLID = frozenset(
    {"air", "cave_air", "void_air", "water", "lava", "bubble_column"}
)
# Default search radius for find_block / find_blocks.
# Ref: mineflayer/docs/api.md — bot.findBlocks(options.maxDistance) (default 16).
_FIND_MAX_DISTANCE = 64
# dig(): longest break we'll wait for. Anything slower (obsidian bare-handed is
# 250s; bedrock's Infinity arrives over the bridge as None) gets a friendly
# "too hard" line instead of a JSPyBridge call timeout mid-dig. Deepslate
# bare-handed (~15s) fits well under.
_MAX_DIG_SECONDS = 60.0
# dig(): margin added on top of mineflayer's digTime estimate, and the floor so
# short digs keep JSPyBridge's default 10s budget.
_DIG_TIMEOUT_MARGIN_SECONDS = 5.0
_DIG_TIMEOUT_FLOOR_SECONDS = 10.0

# Movement: a datapack can advertise an exact-grid provider with any trigger
# objective whose display title is `minethon:grid_move:v1`. The objective must
# occupy a display slot so its definition reaches the client, but vanilla
# 1.21.11 may still omit that bot's score. Prefer the negative score ACK when it
# is visible; otherwise use Brigadier's per-player enabled-trigger suggestions
# for authorization and re-enable ACK. Other servers retain the mineflayer
# control-state + position-polling fallback.
_POLL_SECONDS = 0.05  # ~one physics tick
_WALK_STALL_TIMEOUT = 5.0  # tolerate eight-tick grid locks even near 2 TPS
_WALK_PROGRESS_EPSILON = 0.01  # ignore packet jitter when refreshing the stall timer
_GRID_MOVE_PROVIDER_TITLE = "minethon:grid_move:v1"
_GRID_MOVE_PROVIDER_CACHE_ATTR = "_grid_move_provider_objective"
_GRID_MOVE_SEQUENCE_ATTR = "_grid_move_sequence"
_GRID_MOVE_TIMEOUT = 5.0
_GRID_MOVE_TAB_COMPLETE_TIMEOUT_MS = 1000
_GRID_MOVE_SEQUENCE_BASE = 10
_GRID_MOVE_MAX_SEQUENCE = 200_000_000
_GRID_MOVE_DIRECTIONS = {
    "north": 1,
    "east": 2,
    "south": 3,
    "west": 4,
}
# Turn-in-place codes share the provider's ones digit: direction code + 4
# (5..8 = face north/east/south/west). The datapack rotates the bot with an
# absolute-rotation tp, so the ack also syncs the client yaw to the exact
# cardinal — rotation becomes server-authoritative like grid moves.
_GRID_TURN_OFFSET = 4
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

# bot.action(name): the action key is normalised to this charset, then sent as
# the vanilla trigger `/trigger <username>_<action>`. Server-authoritative — the
# competition datapack validates and performs the action; the client does
# nothing in-world. Ref: vanilla /trigger (players can only fire objectives the
# server enabled for them, so stray calls are harmless).
_ACTION_NAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_")

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


def _control_vector(control: str, yaw: float) -> tuple[float, float]:
    """Horizontal unit vector for a movement control at ``yaw`` radians."""
    forward_x, forward_z = -math.sin(yaw), -math.cos(yaw)
    vectors = {
        "forward": (forward_x, forward_z),
        "back": (-forward_x, -forward_z),
        "left": (forward_z, -forward_x),
        "right": (-forward_z, forward_x),
    }
    return vectors[control]


def _grid_direction(control: str, yaw: float) -> int:
    """Quantise a relative control to an absolute cardinal direction code."""
    direction_x, direction_z = _control_vector(control, yaw)
    if abs(direction_x) >= abs(direction_z):
        return (
            _GRID_MOVE_DIRECTIONS["east"]
            if direction_x > 0
            else _GRID_MOVE_DIRECTIONS["west"]
        )
    return (
        _GRID_MOVE_DIRECTIONS["south"]
        if direction_z > 0
        else _GRID_MOVE_DIRECTIONS["north"]
    )


def _mapping_item(mapping: Any, key: str) -> Any:
    """Read a dict-like JS proxy entry, treating an absent key as ``None``."""
    if mapping is None:
        return None
    try:
        return mapping[key]
    except AttributeError, KeyError, TypeError:
        return None


def _mapping_keys(mapping: Any) -> list[str]:
    """List keys from a Python mapping or a JSPyBridge plain-object proxy.

    Ref: javascript/proxy.py — ``Proxy.__iter__`` requests the JS object's own
    keys when it has no array length.
    """
    if mapping is None:
        return []
    try:
        return [str(key) for key in mapping]
    except TypeError:
        return []


def _component_plaintext(component: Any) -> str:  # noqa: PLR0911
    """Flatten the text/extra subset of a JSON text component.

    Pinned mineflayer already turns a scoreboard title into ``str``. Accepting
    raw JSON strings and mapping-shaped components here keeps provider discovery
    correct for fake proxies and future upstream representations without using
    prefix or substring matching.
    """
    if component is None:
        return ""
    if isinstance(component, str):
        original = component
        try:
            component = json.loads(component)
        except json.JSONDecodeError:
            return original
        if not isinstance(component, str | list | dict):
            return original
    if isinstance(component, list | tuple):
        return "".join(_component_plaintext(part) for part in component)

    component_type = _mapping_item(component, "type")
    component_value = _mapping_item(component, "value")
    if str(component_type) == "string" and component_value is not None:
        # minecraft-protocol 1.21.11 exposes anonymous-NBT strings through
        # JSPyBridge as ``{type: "string", value: "..."}``.
        return _component_plaintext(component_value)

    text = _mapping_item(component, "text")
    extra = _mapping_item(component, "extra")
    if text is None and extra is None:
        return str(component)
    prefix = "" if text is None else str(text)
    suffix = "" if extra is None else _component_plaintext(extra)
    return prefix + suffix


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


def _bridge_safe_sleep(seconds: float) -> None:
    """Block for ``seconds`` without the bot going idle in-world.

    mineflayer's physics loop is a Node-side ``setInterval`` (physics.js), so it
    keeps ticking — position and control-state packets keep flowing — while the
    Python thread parks here. That's why a held state (e.g. sneak) stays live
    across a pause. Ref: mineflayer lib/plugins/physics.js setInterval(doPhysics).
    """
    if seconds > 0:
        threading.Event().wait(seconds)


def _paced(method: Callable[..., Any]) -> Callable[..., Any]:
    """Run an action, then pause ``self._instruction_sleep`` seconds.

    Gives each student action a short trailing beat so a straight-line script's
    steps are individually visible (turn, pause, turn, pause…). Only leaf actions
    are wrapped, so ``turn_left`` (which delegates to ``set_turn``) still pauses
    exactly once. The interval is set by ``create_bot(instruction_sleep=...)`` and
    is ``0`` when ``bypass_instruction_sleep=True``.
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = method(self, *args, **kwargs)
        _bridge_safe_sleep(getattr(self, "_instruction_sleep", 0.0))
        return result

    return wrapper


class Commands:
    """Curated synchronous commands mixed into :class:`Bot`.

    Relies on ``self._js`` (the mineflayer proxy) being set by
    ``Bot.__init__``. Kept in its own module so the runtime façade
    (``_bot_runtime.py``) stays focused on bridge/event plumbing.
    """

    _js: Any  # the mineflayer JS bot proxy, set by Bot.__init__
    _grid_move_lock: threading.Lock  # per-Bot grid request/ACK serialization
    _grid_move_sequence: int  # last locally issued scoreless-provider sequence

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
            # Ctrl-C while waiting on a login that never spawns: honor the
            # project's Ctrl-C contract (goodbye line + clean stop) instead of
            # swallowing the interrupt and letting the script run on with an
            # un-spawned bot straight into a NotSpawnedError.
            from minethon import _bot_runtime  # noqa: PLC0415 — avoids an import cycle

            _bot_runtime._stop_with_message(  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
                _bot_runtime._GOODBYE  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
            )

    def wait(self, seconds: float) -> None:
        """Pause the script for ``seconds`` without the bot going idle.

        Use it to hold a state for a moment::

            bot.sneak(True)
            bot.wait(0.2)
            bot.sneak(False)

        Plain ``time.sleep`` works the same way — the bot keeps its place and its
        held controls (sneak, etc.) in-world during the pause because mineflayer's
        physics tick runs on the Node side, independent of this Python thread.
        (``sleep`` is not added as a method name: mineflayer already uses
        ``bot.sleep`` for sleeping in a bed.)
        """
        _bridge_safe_sleep(seconds)

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

    def get_block_property(
        self, x: int, y: int, z: int, property_name: str
    ) -> str | int | bool | None:
        """獲取指定座標方塊的特定狀態屬性（Block State）。

        例如紅石燈的 "lit" 狀態、熔爐的 "facing" 朝向等。

        Args:
            x: 方塊 X 整數座標
            y: 方塊 Y 整數座標
            z: 方塊 Z 整數座標
            property_name: 屬性名稱（例如 "lit", "facing", "powered"）

        Returns:
            屬性的值（可能是 str, int, bool），若方塊未載入或無此屬性則回傳 None。
        """
        # 呼叫底層 mineflayer 的 blockAt 獲取方塊 Proxy 物件
        block = self._js.blockAt(_make_vec3(x, y, z))
        if block is None:
            return None

        # 呼叫 prismarine-block 的 getProperties() 獲取屬性字典。
        # JSPyBridge 的 JS 物件 Proxy 對不存在的 key 直接回傳 None（不丟例外），
        # KeyError 只會在 props 是原生 dict 時出現。
        # bridge / JS 端的錯誤刻意不攔，讓它往上拋，
        # 避免「連線壞掉」跟「沒有這個屬性」對呼叫端長得一樣。
        props = block.getProperties()
        try:
            return props[property_name]
        except KeyError:
            return None

    def look_block(self) -> tuple[tuple[int, int, int], str] | None:
        """Block currently aimed at as ``((x, y, z), name)``, or ``None``.

        Ref: mineflayer/docs/api.md — bot.blockAtCursor(maxDistance).
        """
        block = self._js.blockAtCursor(_REACH_BLOCKS)
        if block is None:
            return None
        p = block.position
        return ((int(p.x), int(p.y), int(p.z)), str(block.name))

    def get_block_in_front(self) -> tuple[tuple[int, int, int], str] | None:
        """Solid block one step ahead as ``((x, y, z), name)``, or ``None``.

        Public face of the forward probe ``dig()`` falls back on: checks the
        feet-level block one step along the dominant facing axis, then head
        height. Non-solid names (air/water/lava…) read as "nothing in front";
        anything else — including fire — is reported, so a script can inspect
        what it is about to walk into.
        Ref: mineflayer lib/plugins/ray_trace.js getViewDirection.
        """
        block = self._block_in_front()
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
    def _scoreboard_value(self, objective: str, username: str) -> int | None:
        """Read one player's score from mineflayer's client-side scoreboard."""
        scoreboard = _mapping_item(getattr(self._js, "scoreboards", None), objective)
        if scoreboard is None:
            return None
        item = _mapping_item(getattr(scoreboard, "itemsMap", None), username)
        if item is None:
            return None
        value = getattr(item, "value", None)
        return None if value is None else int(value)

    def _is_grid_provider(self, scoreboards: Any, objective: str) -> bool:
        """Whether an objective advertises the exact grid-move v1 title."""
        scoreboard = _mapping_item(scoreboards, objective)
        if scoreboard is None:
            return False
        title = _component_plaintext(getattr(scoreboard, "title", None))
        return title == _GRID_MOVE_PROVIDER_TITLE

    def _enabled_trigger_objectives(self) -> set[str]:
        """Return trigger objectives currently enabled for this player.

        Vanilla Brigadier only suggests objectives accepted by ``/trigger`` for
        the requesting player. This is also an ordered server round-trip, so an
        objective disappearing after a request and becoming suggestible again
        is a usable ACK when the server does not broadcast its score packets.

        Ref: mineflayer ``bot.tabComplete`` and minecraft-protocol 1.21.11
        ``packet_tab_complete.matches[].match``.
        """
        tab_complete = getattr(self._js, "tabComplete", None)
        if not callable(tab_complete):
            return set()
        raw_matches = tab_complete(
            "/trigger ",
            True,
            False,
            _GRID_MOVE_TAB_COMPLETE_TIMEOUT_MS,
        )
        if raw_matches is None:
            return set()
        try:
            matches = list(cast("Any", raw_matches))
        except TypeError:
            return set()

        objectives: set[str] = set()
        for item in matches:
            match = _mapping_item(item, "match")
            value = item if match is None else match
            candidate = _component_plaintext(value).strip()
            if candidate.startswith("/trigger "):
                candidate = candidate.removeprefix("/trigger ").split(maxsplit=1)[0]
            if candidate:
                objectives.add(candidate)
        return objectives

    def _grid_move_context(self) -> tuple[str, str, int | None] | None:
        """Discover or validate the advertised grid-move v1 provider."""
        username_value = getattr(self._js, "username", None)
        if username_value is None:
            return None
        username = str(username_value)
        scoreboards = getattr(self._js, "scoreboards", None)

        cached = getattr(self, _GRID_MOVE_PROVIDER_CACHE_ATTR, None)
        if cached is not None:
            if self._is_grid_provider(scoreboards, cached):
                score = self._scoreboard_value(cached, username)
                if score is not None:
                    return cached, username, score
                if cached in self._enabled_trigger_objectives():
                    return cached, username, None
            object.__setattr__(self, _GRID_MOVE_PROVIDER_CACHE_ATTR, None)

        marked = [
            objective
            for objective in _mapping_keys(scoreboards)
            if self._is_grid_provider(scoreboards, objective)
        ]

        providers: list[tuple[str, int | None]] = []
        enabled: set[str] | None = None
        for objective in marked:
            score = self._scoreboard_value(objective, username)
            if score is not None:
                providers.append((objective, score))
                continue
            if enabled is None:
                enabled = self._enabled_trigger_objectives()
            if objective in enabled:
                providers.append((objective, None))

        if len(providers) > 1:
            names = ", ".join(sorted(objective for objective, _score in providers))
            msg = (
                f"伺服器同時提供多個精確移動 provider: {names}。"
                "請檢查伺服器 datapack，只為這個機器人保留一個 grid_move v1 provider。"
            )
            raise MinethonError(msg)
        if not providers:
            return None

        objective, score = providers[0]
        object.__setattr__(self, _GRID_MOVE_PROVIDER_CACHE_ATTR, objective)
        return objective, username, score

    def _next_grid_sequence(self, score: int | None) -> int:
        """First sequence number for a new provider transaction batch."""
        if score is None:
            return getattr(self, _GRID_MOVE_SEQUENCE_ATTR, 0) + 1
        return abs(score) // _GRID_MOVE_SEQUENCE_BASE + 1

    def _grid_transaction(
        self,
        context: tuple[str, str, int | None],
        sequence: int,
        code: int,
        action: str,
    ) -> int:
        """Send one sequenced provider request and wait for its exact ack.

        Returns the effective (wrap-adjusted) sequence that was used, so the
        caller can continue a multi-step batch with ``+ 1``.
        """
        objective, username, score = context
        if sequence > _GRID_MOVE_MAX_SEQUENCE:
            sequence = 1
        payload = sequence * _GRID_MOVE_SEQUENCE_BASE + code
        deadline = time.monotonic() + _GRID_MOVE_TIMEOUT
        if score is None:
            # The scoreless ACK ("trigger enabled again") carries no payload
            # identity, so a timed-out request's delayed re-enable could be
            # misread as the next request's ACK. Drain it *before* sending:
            # only send once the trigger is observed enabled, which means any
            # earlier request has been fully processed. Every enabled state
            # seen after our send can then only come from our own request
            # (the provider re-enables in the same tick it processes).
            while objective not in self._enabled_trigger_objectives():
                if time.monotonic() >= deadline:
                    msg = (
                        f"伺服器未完成{action}: 前一筆 provider 請求仍未被伺服器"
                        "處理（trigger 尚未重新啟用），已放棄送出新請求。"
                        "請確認任務進行中，且 datapack 與 minethon 版本一致。"
                    )
                    raise MinethonError(msg)
                time.sleep(_POLL_SECONDS)
        self._js.chat(f"/trigger {objective} set {payload}")
        while True:
            score_ack = self._scoreboard_value(objective, username) == -payload
            trigger_ack = score is None and (
                objective in self._enabled_trigger_objectives()
            )
            if score_ack or trigger_ack:
                break
            if time.monotonic() >= deadline:
                if score is None:
                    msg = (
                        f"伺服器未完成{action}: provider trigger 未重新啟用。"
                        "請確認任務已開始，且 datapack 與 minethon 版本一致。"
                    )
                else:
                    msg = (
                        f"伺服器未完成{action}。請確認任務已開始，且 "
                        "datapack 與 minethon 版本一致; 也請確認 provider objective "
                        "的 criteria 是 trigger，而不是 dummy。"
                    )
                raise MinethonError(msg)
            time.sleep(_POLL_SECONDS)
        object.__setattr__(self, _GRID_MOVE_SEQUENCE_ATTR, sequence)
        return sequence

    def _walk_server_grid(
        self,
        control: str,
        blocks: float,
        context: tuple[str, str, int | None],
    ) -> tuple[float, float, float]:
        """Send sequenced one-cell trigger requests and wait for exact server ack."""
        requested = float(blocks)
        if not requested.is_integer():
            msg = "此任務使用精確格狀移動，move_* 的格數必須是整數。"
            raise ValueError(msg)
        sequence = self._next_grid_sequence(context[2])
        direction = _grid_direction(control, float(self._entity().yaw))
        for _ in range(int(requested)):
            sequence = self._grid_transaction(
                context, sequence, direction, "精確格狀移動"
            )
            sequence += 1
        return self.get_pos()

    def _turn_server_grid(
        self,
        yaw: float,
        context: tuple[str, str, int | None],
    ) -> tuple[float, float]:
        """Ask the server to face the cardinal nearest ``yaw`` (degrees).

        The turn is one provider transaction (code = direction + 4). The
        datapack applies an absolute-rotation tp, so once the ack arrives both
        the server and this client agree on the exact cardinal yaw — a
        subsequent ``action("put out")`` can never race the rotation.
        """
        code = _grid_direction("forward", math.radians(yaw)) + _GRID_TURN_OFFSET
        sequence = self._next_grid_sequence(context[2])
        self._grid_transaction(context, sequence, code, "精確轉向")
        return (self.get_yaw(), self.get_pitch())

    def _walk(self, control: str, blocks: float) -> tuple[float, float, float]:
        """Move through an advertised server grid, or fall back to client physics.

        The server-grid protocol is authoritative and acknowledges every exact
        one-cell move. The fallback is relative to the facing when the call
        starts and polls directional progress with a stall timeout.
        """
        if blocks <= 0:
            return self.get_pos()
        # The score or enabled-trigger state is one per-player request/ACK slot.
        # Discovery, sequence derivation and ACK waiting must be one transaction;
        # otherwise concurrent main/callback calls can reuse a sequence.
        with self._grid_move_lock:
            grid_context = self._grid_move_context()
            if grid_context is not None:
                return self._walk_server_grid(control, blocks, grid_context)
        entity = self._entity()
        start = entity.position
        sx, sz = float(start.x), float(start.z)
        direction_x, direction_z = _control_vector(control, float(entity.yaw))
        best_progress = 0.0
        last_progress_at = time.monotonic()
        self._js.setControlState(control, True)
        try:
            while True:
                pos = self._entity().position
                progress = (float(pos.x) - sx) * direction_x + (
                    float(pos.z) - sz
                ) * direction_z
                if progress >= blocks:
                    break
                now = time.monotonic()
                if progress >= best_progress + _WALK_PROGRESS_EPSILON:
                    best_progress = progress
                    last_progress_at = now
                elif now - last_progress_at >= _WALK_STALL_TIMEOUT:
                    break
                time.sleep(_POLL_SECONDS)
        finally:
            self._js.setControlState(control, False)
        return self.get_pos()

    @_paced
    def move_forward(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Walk forward ``blocks`` blocks; returns the new position."""
        return self._walk("forward", blocks)

    @_paced
    def move_backward(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Walk backward ``blocks`` blocks; returns the new position."""
        return self._walk("back", blocks)

    @_paced
    def move_left(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Strafe left ``blocks`` blocks; returns the new position."""
        return self._walk("left", blocks)

    @_paced
    def move_right(self, blocks: float = 1.0) -> tuple[float, float, float]:
        """Strafe right ``blocks`` blocks; returns the new position."""
        return self._walk("right", blocks)

    @_paced
    def jump(self) -> tuple[float, float, float]:
        """Jump once; returns the position right after the hop begins.

        Ref: mineflayer/docs/api.md — bot.setControlState('jump', state).
        """
        self._js.setControlState("jump", True)
        time.sleep(_JUMP_SECONDS)
        self._js.setControlState("jump", False)
        return self.get_pos()

    # ── orientation (write) ───────────────────────────────────────────
    @_paced  # turn / turn_left / turn_right delegate here, so they pace once
    def set_turn(self, yaw: float) -> tuple[float, float]:
        """Face an absolute ``yaw`` (degrees); returns the new ``(yaw, pitch)``.

        ``0`` faces -Z (north); larger yaw turns counter-clockwise. Pitch is
        left unchanged. On a server that advertises the grid-move provider the
        turn is server-authoritative: ``yaw`` is quantised to the nearest
        cardinal and sent as a provider transaction, and the method returns
        only after the server has rotated the bot and acknowledged — client
        ``look`` packets alone have no delivery guarantee (a look racing a
        server teleport's confirm window is dropped and never resent), which
        used to leave the in-world facing stale. Without a provider this
        falls back to the plain client-side look.
        Ref: mineflayer/docs/api.md — bot.look(yaw, pitch, force).
        """
        entity = self._entity()
        # Same transaction discipline as _walk: discovery, sequence derivation
        # and ACK waiting must happen under the per-Bot lock.
        with self._grid_move_lock:
            grid_context = self._grid_move_context()
            if grid_context is not None:
                return self._turn_server_grid(yaw, grid_context)
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

    @_paced
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

    @_paced
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
            if str(getattr(item, "name", "")) == name:
                return item
        return None

    def _find_inventory_items(self, name_or_id: str | int) -> list[Any]:
        """Find all inventory items matching the given string name or integer ID."""
        matching = []
        for item in self._js.inventory.items():
            if isinstance(name_or_id, str):
                if str(getattr(item, "name", "")) == name_or_id:
                    matching.append(item)
            elif getattr(item, "type", None) == name_or_id:
                matching.append(item)
        return matching

    @_paced
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

    @_paced
    def unhold(self) -> bool:
        """Move the held item back into the inventory.

        Returns ``False`` if the hand was already empty.
        Ref: mineflayer/docs/api.md — bot.unequip('hand').
        """
        if self._js.heldItem is None:
            return False
        self._js.unequip("hand")
        return True

    @_paced
    def drop(
        self, name_or_id: str | int | None = None, count: int | None = None
    ) -> bool:
        """Throw item(s) onto the ground (held item by default, or specified item name/ID).

        When ``name_or_id`` is ``None``, throws the currently held item stack.
        When a string name or integer ID is given, searches inventory for matching items.
        If ``count`` is ``None`` or greater than/equal to total carried count, throws all matching stacks.
        Returns ``True`` on success, ``False`` if hand is empty or item is not carried.
        Raises ``ValueError`` if ``count`` is less than or equal to 0.
        Ref: mineflayer/docs/api.md — bot.tossStack(item) / bot.toss(itemType, metadata, count).
        """
        if count is not None and count <= 0:
            msg = f"count 必須是大於 0 的正整數，收到 {count}。"
            raise ValueError(msg)

        if name_or_id is None:
            item = self._js.heldItem
            if item is None:
                return False
            self._js.tossStack(item)
            return True

        matching_items = self._find_inventory_items(name_or_id)
        if not matching_items:
            return False

        total_carried = sum(getattr(item, "count", 1) for item in matching_items)
        if count is not None and count > total_carried:
            warnings.warn(
                f"count ({count}) 超過持有量 ({total_carried})，將丟出全部。",
                stacklevel=2,
            )

        if count is None or count >= total_carried:
            for item in matching_items:
                self._js.tossStack(item)
            return True

        remaining = count
        for item in matching_items:
            stack_count = getattr(item, "count", 1)
            if remaining >= stack_count:
                self._js.tossStack(item)
                remaining -= stack_count
            else:
                item_type = getattr(item, "type", None)
                if item_type is not None:
                    metadata = getattr(item, "metadata", None)
                    self._js.toss(item_type, metadata, remaining)
                break

        return True

    # ── actions (on the block/face being aimed at) ────────────────────
    def _front_cell(self) -> tuple[int, int, int]:
        """Feet-level grid cell one step ahead along the dominant facing axis.

        Ref: mineflayer lib/plugins/ray_trace.js getViewDirection — forward =
        (-sin(yaw), 0, -cos(yaw)).
        """
        ent = self._entity()
        yaw = float(ent.yaw)
        dx, dz = -math.sin(yaw), -math.cos(yaw)
        step = (
            (1 if dx > 0 else -1, 0) if abs(dx) >= abs(dz) else (0, 1 if dz > 0 else -1)
        )
        return (
            math.floor(float(ent.position.x)) + step[0],
            math.floor(float(ent.position.y)),
            math.floor(float(ent.position.z)) + step[1],
        )

    def _block_in_front(self) -> Any:
        """Solid block one step ahead of the bot, or ``None`` if only air.

        Used as dig()'s fallback when the bot isn't aiming at anything (e.g.
        looking level over flat ground, where blockAtCursor sees only air).
        Steps along the dominant horizontal facing axis and checks the feet
        block first, then head height. The public native-type view of the same
        probe is :meth:`get_block_in_front`.
        """
        bx, by, bz = self._front_cell()
        for y in (by, by + 1):  # feet level, then head level
            block = self._js.blockAt(_make_vec3(bx, y, bz))
            if block is not None and str(block.name) not in _NON_SOLID:
                return block
        return None

    @_paced
    def dig(self) -> tuple[tuple[int, int, int], str] | None:
        """Break the block in front of the bot; returns its ``((x, y, z), name)``.

        Uses whatever the bot is aiming at; if it isn't aiming at a block (e.g.
        looking straight ahead over flat ground), falls back to the solid block
        one step forward. Returns ``None`` when there's nothing solid to break,
        or when the block is too hard to break in a reasonable time (prints a
        friendly line in that case). (This renames mineflayer's ``break``
        action.) Ref: mineflayer/docs/api.md — bot.dig(block), bot.digTime.
        """
        block = self._js.blockAtCursor(_REACH_BLOCKS)
        if block is None:
            block = self._block_in_front()
        if block is None:
            return None
        p = block.position
        result = ((int(p.x), int(p.y), int(p.z)), str(block.name))
        # Long digs (deepslate bare-handed is ~15s) outlive JSPyBridge's 10s
        # per-call budget: the student got a raw English timeout stack and the
        # late JS reply then poisoned the bridge IO loop. Size the call timeout
        # from mineflayer's own estimate; refuse effectively unbreakable blocks.
        # Unbreakable (bedrock) digTime is Infinity, which the bridge's JSON
        # serialization delivers as None — float(None) raises, leaving the
        # sentinel in place, so None routes to the "too hard" line too.
        dig_ms: float | None = None
        with contextlib.suppress(Exception):
            dig_ms = float(self._js.digTime(block))
        if (
            dig_ms is None
            or not math.isfinite(dig_ms)
            or dig_ms > _MAX_DIG_SECONDS * 1000
        ):
            print(f"「{result[1]}」太硬了，挖不動。", flush=True)  # noqa: T201 — student-facing
            return None
        timeout = max(
            _DIG_TIMEOUT_FLOOR_SECONDS, dig_ms / 1000 + _DIG_TIMEOUT_MARGIN_SECONDS
        )
        # mineflayer looks at the block itself (forceLook)
        self._js.dig(block, timeout=timeout)
        return result

    @_paced
    def place(self) -> tuple[tuple[int, int, int], str] | None:
        """Place the held block against the face being aimed at.

        Returns the new block's ``((x, y, z), name)``, or ``None`` if nothing
        is in reach or the hand is empty (hold something first — mineflayer
        would otherwise throw a raw "must be holding an item" error).
        Ref: mineflayer/docs/api.md — bot.placeBlock(ref, faceVector).
        """
        if self._js.heldItem is None:
            return None
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

    @_paced
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

    def get_player_pos(self, username: str) -> tuple[float, float, float]:
        """Live ``(x, y, z)`` of the named player — for following or aiming.

        Reads the player's current entity position immediately (the same lookup
        :meth:`use_player` uses) and returns native floats, so a follow loop can
        write ``bot.look_at(*bot.get_player_pos(name))`` then
        ``bot.move_forward()`` without touching ``Vec3``. Raises
        :class:`PlayerNotFoundError` when the player is offline, in another
        world, or outside the bot's loaded entity range.

        Ref: mineflayer/docs/api.md — bot.players[name].entity.position.
        """
        self._entity()
        try:
            player = self._js.players[username]
        except IndexError, KeyError, TypeError:
            player = None
        target = getattr(player, "entity", None)
        if target is None or not bool(getattr(target, "isValid", True)):
            msg = (
                f"找不到玩家 {username!r}。"
                "請確認對方在線、與機器人在同一世界，且位於已載入範圍內。"
            )
            raise PlayerNotFoundError(msg)
        position = target.position
        return (float(position.x), float(position.y), float(position.z))

    @_paced
    def use_player(self, username: str) -> bool:
        """Right-click the named player's current entity.

        Looks at the center of the player's live bounding box immediately
        before sending the same INTERACT_AT then INTERACT sequence as a real
        client right-click, so callers never need to calculate a yaw/pitch for
        players at different heights. Raises
        :class:`PlayerNotFoundError` when the player is offline, in another
        world, or outside the bot's loaded entity range.

        Ref: mineflayer index.d.ts and lib/plugins/inventory.js —
        bot.players, bot.activateEntityAt, bot.activateEntity.
        """
        self._entity()
        try:
            player = self._js.players[username]
        except IndexError, KeyError, TypeError:
            player = None
        target = getattr(player, "entity", None)
        if target is None or not bool(getattr(target, "isValid", True)):
            msg = (
                f"找不到玩家 {username!r}。"
                "請確認對方在線、與機器人在同一世界，且位於已載入範圍內。"
            )
            raise PlayerNotFoundError(msg)

        position = target.position
        center_y = float(position.y) + float(getattr(target, "height", 1.8)) / 2
        click_point = _make_vec3(
            float(position.x),
            center_y,
            float(position.z),
        )
        self._js.activateEntityAt(target, click_point)
        self._js.activateEntity(target)
        return True

    def sneak(self, on: bool) -> bool:
        """Hold or release sneak (a persistent state); returns ``on``.

        Ref: mineflayer/docs/api.md — bot.setControlState('sneak', state).
        """
        self._js.setControlState("sneak", on)
        return on

    # ── high-level named actions (bot.action) ─────────────────────────
    @_paced
    def action(self, name: str, value: int | None = None) -> None:
        """Ask the server to run the named quest action (e.g. ``"put out"``).

        Server-authoritative by design: this only sends the vanilla trigger
        ``/trigger <username>_<action>`` (username lowercased; action
        lowercased with spaces/hyphens collapsed to underscores) and does
        **nothing** client-side — no block edits, no item use, so a lost
        connection mid-action can never damage the map. Bot ``G1_labfire_1``
        calling ``action("put out")`` fires ``/trigger g1_labfire_1_put_out``.
        ``value``, when given, is attached as the trigger's integer payload
        (``set <value>``) for quests that want a parameter. The competition
        datapack validates the request (right bot, quest active, target in
        front…) and performs or silently ignores it; players can only fire
        trigger objectives the server has enabled for them, so a stray call
        is harmless. Ref: mineflayer/docs/api.md — bot.chat(message);
        vanilla /trigger.
        """
        key = "_".join(str(name).strip().lower().replace("-", " ").split())
        if not key or not all(c in _ACTION_NAME_CHARS for c in key):
            msg = f"動作名稱只能包含英文字母、數字、空格、連字號或底線，收到 {name!r}。"
            raise ValueError(msg)
        username = getattr(self._js, "username", None)
        if username is None:
            msg = "機器人還沒登入伺服器。請先呼叫 bot.wait_spawn()。"
            raise NotSpawnedError(msg)
        command = f"/trigger {str(username).lower()}_{key}"
        if value is not None:
            command += f" set {int(value)}"
        self._js.chat(command)

    # ── chat ──────────────────────────────────────────────────────────
    @_paced
    def chat(self, obj: object) -> None:
        """Send ``obj`` (converted to text) as a normal public chat message.

        Group-only visibility is handled server-side by the competition's
        chat plugin — the bot just sends and receives normally.
        Ref: mineflayer/docs/api.md — bot.chat(message).
        """
        self._js.chat(str(obj))
