"""Bot — public entry point for minethon.

Runtime behavior lives here. A sibling `bot.pyi` (generated from
mineflayer's `index.d.ts`) supplies the typed overloads that IDEs
use for completion of property and method signatures.

Pure synchronous callback model — no asyncio. Event handlers are
registered exclusively via subclassing :class:`EventAdaptor` and
calling :meth:`Bot.bind`. The legacy decorator entries
(`bot.on(...)`, `bot.once(...)`, `@bot.on_<event>`) have been
removed in favor of the single class-based path.
"""

from __future__ import annotations

import atexit
import contextlib
import inspect
import os
import socket
import sys
import threading
import time
import traceback
import warnings
from functools import wraps
from typing import TYPE_CHECKING, Any

from javascript import On, Once, connection, eval_js, require

from minethon._bridge import BUNDLED_VERSIONS, get_mineflayer
from minethon._commands import (
    Commands,
    bounded_keys,
    component_plaintext,
    suggest,
)
from minethon._event_login import resolve_account
from minethon._events import EVENT_ATTRIBUTE_MAP, BotEvent
from minethon._handlers import EventAdaptor
from minethon._members import BOT_MEMBERS
from minethon.errors import PluginNotInstalledError, VersionPinRequiredError

if TYPE_CHECKING:
    from collections.abc import Callable

# Shown instead of a traceback when a student stops the script with Ctrl-C.
_GOODBYE = "\n程式已結束。"
# Shown when the server drops the bot mid-run.
_DISCONNECTED = "\n機器人已斷線，程式結束。"
# Shown when login fails (wrong task name / task closed), instead of leaking the
# raw yggdrasil "Invalid credentials" stack trace.
_QUEST_NOT_FOUND = "\n找不到此任務。請檢查任務名稱是否正確，或是任務是否開放。"
# Shown when a bridge call times out / the node process dies — usually the bot
# was disconnected (e.g. killed and kicked) mid-command, leaving JSPyBridge
# waiting on a dead connection. Rendered instead of the raw JSPyBridge stack.
_CONNECTION_LOST = "\n與伺服器的連線中斷了，程式結束。"
# Shown when a single bridge method call hits JSPyBridge's per-call timeout
# ("Call to 'X' timed out."). Distinct from _CONNECTION_LOST: the connection
# may be fine and the action simply took too long, so say both possibilities.
_CALL_TIMEOUT = (
    "\n指令等不到伺服器回應（逾時）。可能是連線中斷，或這個動作耗時過長，程式結束。"
)
# Marker for JSPyBridge's per-method-call timeout. Ref: javascript/proxy.py —
# "Call to '{attr}' timed out. Increase the timeout by setting ...".
_CALL_TIMEOUT_MARKER = "timed out. increase the timeout"
# Substrings JSPyBridge puts in the bare Exceptions it raises when the node
# bridge stops responding. Ref: javascript/proxy.py + connection.py.
_BRIDGE_FAILURE_MARKERS = (
    "timed out accessing",
    "execution timed out",
    "process has crashed",
    _CALL_TIMEOUT_MARKER,
)
# Shown after a student's own uncaught exception, right below the traceback.
_SCRIPT_FAILED = "程式因為上面的錯誤停止了。"
# Shown when a straight-line script runs off the end and the bot is kept alive.
# Without it the terminal simply stops producing output — indistinguishable from
# a hang — because `atexit` blocks in run_forever() until the server drops the
# bot, which for a healthy connection is never.
_SCRIPT_DONE = "\n（你的程式已經跑完了。機器人還在線上，按 Ctrl-C 結束。）"
# Shown when the server's TCP port cannot be reached at all.
_UNREACHABLE = "\n連不到伺服器 {host}:{port}。請確認網路連線正常，以及伺服器已經開啟。"
# Seconds to spend on the pre-flight reachability probe. Long enough for a slow
# link, short enough not to feel like a hang if the host is simply down.
_REACHABILITY_TIMEOUT = 6.0
# mineflayer's default port, so the probe checks the same endpoint createBot will.
# Ref: mineflayer lib/loader.js — options.port ?? 25565.
_DEFAULT_PORT = 25565
# Vanilla's per-IP reconnect throttle. A whole classroom behind one NAT address
# trips it constantly, and the raw kick text reads like the script's fault.
_THROTTLE_MARKER = "connection throttled"
_THROTTLE_HINT = "連線太密集了（伺服器限制每個 IP 的重連間隔）。等幾秒再跑一次就好。"
# Default per-instruction pause (seconds) so a straight-line script's steps are
# individually visible. Tunable via create_bot(instruction_sleep=...).
_DEFAULT_INSTRUCTION_SLEEP = 0.2
# `seen` makes the goodbye/disconnect line print once. A dict holder avoids a
# `global` rebind.
_INTERRUPT = {"seen": False}


def _stop_with_message(message: str, *, code: int = 0) -> None:
    """Print ``message`` once and hard-stop the program with exit ``code``.

    Runs on a bridge callback thread (a disconnect, or a login `error`). The
    student's main thread may be parked in run_forever, blocked in wait_spawn
    that will never fire, or deep inside a bridge call on a dead connection — an
    async interrupt can't reliably break those, so we terminate the node bridge
    and exit the process outright. Abrupt, but it guarantees the script stops.

    ``code`` is 0 for a normal end (quit / server closed the session) and 1 for
    failures (login error, lost bridge), so shells and CI can tell them apart.
    os._exit skips atexit and buffered writers by design — flush both streams
    first so the student's own prints aren't lost.
    """
    if _INTERRUPT["seen"]:
        return
    _INTERRUPT["seen"] = True
    print(message, flush=True)  # noqa: T201 — student-facing, intentional
    with contextlib.suppress(Exception):
        sys.stderr.flush()
    # Best-effort: terminate the node subprocess so it isn't orphaned.
    with contextlib.suppress(Exception):
        connection.stop()
    os._exit(code)  # only reliable way out of a blocked bridge call


def _looks_like_auth_error(text: str) -> bool:
    """True when an `error` payload reads like a bad-credentials failure."""
    low = text.lower()
    return "invalid credentials" in low or "invalid username or password" in low


def _is_bridge_failure(exc: BaseException) -> bool:
    """True when ``exc`` is a JSPyBridge timeout / crashed-process error.

    These surface as bare ``Exception`` (no dedicated class), so match by the
    message the bridge writes. Ref: javascript/proxy.py, connection.py.
    """
    text = str(exc).lower()
    return any(marker in text for marker in _BRIDGE_FAILURE_MARKERS)


def _on_login_error(err: Any) -> None:
    """Turn a bot `error` (esp. auth failure) into a friendly line + clean exit.

    Registering any `error` listener also stops mineflayer's EventEmitter from
    throwing the raw yggdrasil stack. Ref: mineflayer lib/loader.js — bot._client
    'error' is re-emitted as bot 'error'.
    """
    text = ""
    with contextlib.suppress(Exception):
        text = str(getattr(err, "message", None) or err)
    message = (
        _QUEST_NOT_FOUND if _looks_like_auth_error(text) else f"\n連線發生錯誤：{text}"  # noqa: RUF001 — zh-TW fullwidth colon
    )
    _stop_with_message(message, code=1)


def _on_kicked(reason: Any = None, *_a: Any) -> None:
    """Print the server's kick reason so it isn't swallowed.

    Runs before the `end` handler's disconnect line. Ref: mineflayer
    index.d.ts — kicked: (reason: string, loggedIn: boolean).
    """
    text = ""
    with contextlib.suppress(Exception):
        # `reason` is a protodef NBT structure, not a string: str() on it prints
        # a Python dict repr with the actual message buried inside
        # ({'type': 'compound', 'value': {'translate': {...}}}).
        text = component_plaintext(reason) or str(reason)
    if _THROTTLE_MARKER in text.lower():
        # Vanilla's per-IP reconnect throttle. Worth naming: a classroom sharing
        # one NAT address hits this constantly, and "被踢出" alone reads as a bug
        # in the student's script.
        print(f"\n{_THROTTLE_HINT}", flush=True)  # noqa: T201 — student-facing
        return
    print(f"\n機器人被伺服器踢出：{text}", flush=True)  # noqa: T201, RUF001 — student-facing; zh-TW colon


# Clientbound packet carrying a vehicle's current passenger list. Listened to
# on `bot._client` (the minecraft-protocol client), not on the bot itself.
# Ref: mineflayer lib/plugins/entities.js — bot._client.on('set_passengers').
_SET_PASSENGERS = "set_passengers"
# mineflayer's sentinel for "this packet detaches rather than attaches".
# Ref: mineflayer lib/plugins/entities.js — `entityId === -1 ? null : ...`.
_NO_VEHICLE = -1
# Printed when the protocol client is missing, so a silently broken is_riding()
# is at least noisy. Same escape hatch run_forever() guards against.
_NO_CLIENT_WARNING = (
    "bot._client 不存在，無法修正下車後的 bot.vehicle。"
    "is_riding() 在機器人騎過任何東西之後會一直回傳 True。"
)


def _clear_stale_vehicle(js_bot: Any, packet: Any) -> None:
    """Clear ``bot.vehicle`` when a `set_passengers` packet says the bot got off.

    mineflayer's own handler only acts when the bot appears *in* the new
    passenger list (`entities.js` —
    ``passengers.includes(bot.entity.id) && entityId === -1``). A 1.9+ dismount
    is expected to arrive as the vehicle's own id plus a list the bot has
    already been removed from, so neither condition holds — that packet shape
    is the load-bearing assumption here and only
    ``tests/integration/test_vehicle_dismount.py`` checks it. The fallback
    meant to cover the case is dead code, and that part *is* settled from
    source: the event is emitted on ``bot`` (`entities.js:302`) while the
    handler is registered on ``bot._client`` (`:812`) — two different
    EventEmitters, per `loader.js`. The result is that ``bot.vehicle`` keeps
    pointing at the old vehicle forever and :meth:`Commands.is_riding` never
    goes back to ``False``.

    Re-emits `dismount` for the same reason, so ``EventAdaptor.on_dismount``
    fires at all. mineflayer's own `set_passengers` branch needs the bot to be
    *in* the list, so it can never double-fire with this one.

    Does **not** cover a vehicle that despawns under the bot, or a death /
    dimension change — see :meth:`Commands.is_riding` and
    :func:`_install_dismount_repair` for those two.
    """
    # `packet` is a plain dict, so reading it costs nothing: protodef builds
    # payloads as plain JS objects and JSPyBridge inlines those by value rather
    # than handing back a Proxy — its JSON replacer only allocates an ffid when
    # `constructor.name` is neither 'Object' nor 'Array' (javascript/js/pyi.js).
    # Subscripting stays correct if one ever does arrive as a Proxy, since
    # Proxy.__getitem__ maps to the same getProp as __getattr__.
    riders = {int(rider) for rider in packet["passengers"]}
    entity_id = int(packet["entityId"])
    vehicle = js_bot.vehicle
    if vehicle is None:
        # Not riding as far as mineflayer knows, so there is normally nothing to
        # do. The exception is a mount that this same handler already undid:
        # Python callbacks are drained one at a time, long after every JS
        # handler has run, so a dismount+remount of one vehicle inside a single
        # tick reaches us as "clear" then "the bot is aboard" — with mineflayer's
        # JS state already settled on "aboard". Put it back rather than leave
        # is_riding() saying False while the bot is really riding. `-1` is
        # mineflayer's "no vehicle" sentinel (`entities.js`), never a real id.
        # The bogus `dismount` already emitted for the first packet cannot be
        # taken back — the state ends up right, the event stream in that one
        # window does not.
        if entity_id != _NO_VEHICLE and int(js_bot.entity.id) in riders:
            js_bot.vehicle = js_bot.entities[entity_id]
        return
    if entity_id != int(vehicle.id):
        return  # some other entity's passenger list changed
    if int(js_bot.entity.id) in riders:
        return  # the list changed, but the bot is still aboard
    js_bot.vehicle = None
    js_bot.emit(BotEvent.DISMOUNT.value, vehicle)


def _install_dismount_repair(js_bot: Any) -> None:
    """Keep ``bot.vehicle`` honest: `set_passengers` repair plus a respawn reset.

    Both are registered with ``On`` rather than ``Once`` — the bot may mount and
    dismount any number of times. That leaves permanent entries in JSPyBridge's
    callback table, which the `end` listener in ``create_bot`` deliberately
    avoids. It is not a new hazard: the `error` and `kicked` ``Once`` handlers
    also stay registered for the whole session (they are only removed when they
    fire, which in a normal run never happens) and every ``bind()``-ed student
    handler uses ``On``, so that table is already permanently non-empty. Note
    the atexit spin-wait's ``connection.is_alive()`` guard tracks the *node
    subprocess*, which outlives a Minecraft disconnect — it is not a bound.
    Ref: javascript/__init__.py — On/Once; javascript/events.py — on_exit;
    javascript/connection.py — is_alive.
    """
    client = getattr(js_bot, "_client", None)
    if client is None:
        warnings.warn(_NO_CLIENT_WARNING, RuntimeWarning, stacklevel=2)
        return

    def repair(packet: Any, *_a: Any, **_k: Any) -> None:
        _clear_stale_vehicle(js_bot, packet)

    def reset(*_a: Any, **_k: Any) -> None:
        vehicle = js_bot.vehicle
        if vehicle is None:
            return
        js_bot.vehicle = None
        # Same event as the packet path, so a handler waiting on `dismount`
        # wakes whether the bot got off or died getting off.
        js_bot.emit(BotEvent.DISMOUNT.value, vehicle)

    On(client, _SET_PASSENGERS)(
        _normalize_handler(repair, emitter=client, event_name=_SET_PASSENGERS)
    )
    # Nothing in mineflayer resets `bot.vehicle`: `bot.entities` is cleared only
    # on the `login` packet, and no path assigns `bot.vehicle = null` outside
    # the two `set_passengers` / `attach_entity` branches. So whenever the
    # server takes the bot off a vehicle without a `set_passengers` — believed
    # to include death and dimension change, though that is server behaviour
    # this repo cannot verify — is_riding() would stay True forever. Resetting
    # on `respawn` is the cheapest cover. It is not free of assumptions either —
    # if a server ever kept a bot mounted across a dimension change, this would
    # briefly report not-riding — but the handler above self-heals that as soon
    # as the vehicle's next `set_passengers` arrives, and being wrong for a
    # moment beats being wrong for the rest of the session. mineflayer emits
    # `respawn` straight off the clientbound packet, so this fires for whatever
    # the server uses it for.
    # Ref: mineflayer lib/plugins/health.js — bot._client.on('respawn').
    On(js_bot, BotEvent.RESPAWN.value)(
        _normalize_handler(reset, emitter=js_bot, event_name=BotEvent.RESPAWN.value)
    )


_NO_CLIENT_VELOCITY_WARNING = (
    "bot._client 不存在，無法修正擊退封包的速度解析。"
    "機器人被攻擊後，位置可能從此讀不到。"
)

# Runs natively in node — the arrow this template returns closes over nothing
# Python-side, so the per-packet cost is JS-only. The guard makes it a no-op
# wherever mineflayer parsed correctly: flat `velocityX` packets (pre-1.21.2
# servers) are left alone, and on a minecraft-data new enough to carry the
# feature flag it merely rewrites the value mineflayer already stored.
_VELOCITY_REPAIR_JS = """
return (bot) => {
  const FROM_NOTCH_VEL = 1 / 8000
  bot._client.on('entity_velocity', (packet) => {
    if (packet.velocityX !== undefined || !packet.velocity) return
    const entity = bot.entities[packet.entityId]
    if (!entity || !entity.velocity) return
    entity.velocity.set(
      packet.velocity.x * FROM_NOTCH_VEL,
      packet.velocity.y * FROM_NOTCH_VEL,
      packet.velocity.z * FROM_NOTCH_VEL
    )
  })
}
"""


def _install_velocity_repair(js_bot: Any) -> None:
    """Fix the NaN velocity mineflayer writes when the bot takes knockback.

    mineflayer 4.37.0 supports the 1.21.2+ `entity_velocity` shape (a nested
    vec3i16 `velocity` field) behind `supportFeature('entityVelocityIsLpVec3')`,
    but the minecraft-data releases it installs against (≤ 3.110.x) never
    shipped that feature: the query answers false, the legacy branch reads
    `packet.velocityX` — undefined on 1.21.2+ — and `fromNotchVelocity` turns
    `Vec3(undefined)` into NaN on `entity.velocity`.

    For the bot's own entity that packet is knockback, so the first time
    anything lands a hit, the next physics tick integrates NaN velocity into
    `bot.entity.position` (NaN + x = NaN), JSPyBridge's JSON layer serializes
    NaN as null, and from then on every position read in Python is None — a
    student's `move_forward()` dies with `float() argument … not 'NoneType'`
    the moment the bot is punched, and every later `get_pos()` stays broken.

    The repair is a second `entity_velocity` listener installed *in node* via
    `eval_js`: entity velocity changes are far too frequent for a per-packet
    bridge callback (same reasoning as rejecting an `entityGone` listener for
    `is_riding`). EventEmitter dispatch is synchronous and this listener
    registers after mineflayer's, so the physics interval can never observe
    the NaN in between. Upstream has since fixed the pairing (minecraft-data
    master carries the feature, mineflayer master dropped the gate), so this
    becomes removable once the bundled mineflayer pin moves past 4.37.x — and
    it stays harmless if left in.

    Ref: mineflayer lib/plugins/entities.js — `bot._client.on('entity_velocity')`;
    mineflayer lib/conversions.js — `FROM_NOTCH_VEL = 1/8000`; minecraft-data
    data/pc/1.21.4/protocol.json — `packet_entity_velocity` / `vec3i16`.
    """
    client = getattr(js_bot, "_client", None)
    if client is None:
        warnings.warn(_NO_CLIENT_VELOCITY_WARNING, RuntimeWarning, stacklevel=2)
        return
    install = eval_js(_VELOCITY_REPAIR_JS)
    install(js_bot)


def _install_quiet_interrupt() -> None:
    """Replace the traceback for an uncaught Ctrl-C with a friendly line.

    Students shouldn't see a KeyboardInterrupt stack trace — just that the
    program ended. Non-interrupt exceptions still print normally.
    """
    previous = sys.excepthook

    def _hook(exc_type: type[BaseException], exc: BaseException, tb: Any) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            if not _INTERRUPT["seen"]:  # real Ctrl-C; disconnect already printed
                _INTERRUPT["seen"] = True
                print(_GOODBYE)  # noqa: T201 — student-facing, intentional
            return
        if _CALL_TIMEOUT_MARKER in str(exc).lower():
            # A single method call timed out — connection may be fine, the
            # action just outlived the bridge's per-call budget. The late JS
            # reply can still poison JSPyBridge's IO loop, so exit cleanly
            # rather than limp on toward a cryptic hang.
            _stop_with_message(_CALL_TIMEOUT, code=1)
            return
        if _is_bridge_failure(exc):
            # Bridge went silent mid-command (usually a disconnect). Show a clean
            # line and hard-exit — os._exit also skips the atexit run_forever,
            # which would otherwise time out again on the dead bridge.
            _stop_with_message(_CONNECTION_LOST, code=1)
            return
        # The student's own bug (TypeError, IndexError…). Print the real traceback
        # — reading it is the point — then stop, because the atexit keep-alive
        # below would otherwise block in run_forever() until the server drops the
        # bot. That left a correct, well-formatted traceback followed by a
        # terminal that never returns, which reads as "the computer froze" to
        # someone who has not met Ctrl-C yet. A script that has crashed has no
        # business holding the bot online; event-driven scripts keep it alive by
        # calling run_forever() themselves, which is what that method is for.
        previous(exc_type, exc, tb)
        _stop_with_message(_SCRIPT_FAILED, code=1)

    sys.excepthook = _hook


# Events known to suffer the emitter-shift bug: how many real args each one
# sends, counted by hand from mineflayer's source — a fact independent of
# how the user's handler happens to declare its own parameters.
# chat/whisper: lib/plugins/chat.js:85 (legacy addChatPattern deprecated path)
# resourcePack: lib/plugins/resource_pack.js (all 3 call sites send exactly 2
#   args, but the *order* isn't stable — the first positional value is
#   sometimes `url`, sometimes `uuid`, depending on which branch fires. This
#   is a separate mineflayer-level quirk; this table only guarantees "how
#   many", not "which means what", so that part is out of scope here).
_REAL_ARGC: dict[str, int] = {
    "chat": 4,
    "error": 1,
    "kicked": 2,
    "whisper": 4,
    "resourcePack": 2,
}


def _normalize_handler(
    func: Callable[..., Any],
    *,
    emitter: Any | None = None,
    event_name: str | None = None,
) -> Callable[..., Any]:
    """Adapt a user handler to mineflayer's loose event-arity conventions.

    Mineflayer's TypeScript typings sometimes declare trailing callback
    parameters that the JS runtime never actually emits (the ``chat`` event's
    ``matches: string[] | null`` is the canonical example — the type
    advertises 5 args but ``lib/plugins/chat.js`` only emits 4). A handler
    written against the declared signature would otherwise crash with
    ``TypeError: missing positional argument``.

    This wrapper:

    * drops the leading emitter arg when JSPyBridge injects it. The pinned
      runtime (Node 22+, javascript 1.2.x) never injects — `needsNodePatches`
      only returns true on Node 14/15 — so detection is deliberately narrow:
      a known ``_REAL_ARGC`` entry whose observed count matches exactly
      (``len(args) == real_argc + 1``), or proxy identity
      (``args[0] is emitter``). Arity excess is **not** treated as injection:
      a short handler (``def on_chat(self, username, message)``) legitimately
      receives more real args than it declares, and stripping the first one
      would hand it the wrong values — excess args are truncated from the
      end instead.
    * pads missing trailing positional args with ``None``
    * truncates any excess positional args JS emits (from the end)
    * isolates handler exceptions: a bug in a student handler prints a
      friendly message plus the traceback and skips that one event, instead
      of flowing back into JS as an unhandled rejection that kills the node
      process (Node ≥15 terminates on unhandled rejections) and leaves the
      script hanging forever.

    Ref: mineflayer/lib/plugins/chat.js:85 — chat event emit arity
    Ref: mineflayer/lib/plugins/resource_pack.js — resourcePack emit arity
    Ref: javascript/js/bridge.js — needsNodePatches() (emitter injection gate)
    """
    params = list(inspect.signature(func).parameters.values())
    accepts_varargs = any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in params)
    slots = sum(
        1
        for p in params
        if p.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    real_argc = _REAL_ARGC.get(event_name) if event_name is not None else None

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if emitter is not None and args:
            if real_argc is not None and len(args) == real_argc + 1:
                should_strip = True
            else:
                should_strip = args[0] is emitter
            if should_strip:
                args = args[1:]
        try:
            if accepts_varargs:
                return func(*args, **kwargs)
            if len(args) < slots:
                args = (*args, *([None] * (slots - len(args))))
            return func(*args[:slots], **kwargs)
        except Exception:  # noqa: BLE001 — must not reach JS as unhandled rejection
            label = event_name or getattr(func, "__name__", "handler")
            print(  # noqa: T201 — student-facing, intentional
                f"\n事件處理發生錯誤（{label}），已略過這一次事件：\n"  # noqa: RUF001 — zh-TW fullwidth colon
                f"{traceback.format_exc()}",
                flush=True,
            )
            return None

    return wrapper


# npm package → attribute on the required module that holds the plugin
# installer function. Most plugins export the installer as the default,
# but a few (pathfinder) expose it on a named property.
_PLUGIN_EXPORT_KEY: dict[str, str] = {
    "mineflayer-pathfinder": "pathfinder",
}

# User-facing hint when bot.pathfinder is touched before the plugin loads.
_PATHFINDER_MISSING = (
    "pathfinder 尚未載入。先呼叫 bot.load_plugin('mineflayer-pathfinder')。"
)


class Bot(Commands):
    """Pythonic façade over a mineflayer Bot proxy.

    Prefer `create_bot(...)` over direct construction. The curated
    synchronous student API (``move_forward``, ``dig``, ``get_pos`` …)
    comes from :class:`minethon._commands.Commands`; unknown attribute
    reads fall through to the underlying JS proxy, so every documented
    mineflayer property or method also works transparently.

    Ref: mineflayer/index.d.ts — Bot interface
    """

    _js: Any

    def __init__(self, js_bot: Any, instruction_sleep: float = 0.0) -> None:
        """Wrap an existing mineflayer JS bot proxy.

        ``instruction_sleep`` is the pause (seconds) added after each action so a
        straight-line script's steps are visible; ``create_bot`` sets it, direct
        construction defaults to no pause.
        """
        object.__setattr__(self, "_js", js_bot)
        object.__setattr__(self, "_instruction_sleep", float(instruction_sleep))
        # A grid provider exposes one score/trigger ACK channel per player.
        # Serialize this Bot's movement transactions so concurrent main/callback
        # calls cannot derive and wait on the same sequence number.
        object.__setattr__(self, "_grid_move_lock", threading.Lock())
        object.__setattr__(self, "_grid_move_sequence", 0)
        # Diagnostics that must not repeat inside a loop — see
        # Commands._warn_if_action_unavailable and Commands._block_id.
        object.__setattr__(self, "_checked_actions", set())
        object.__setattr__(self, "_reported_unknown_blocks", set())

    def __getattr__(self, name: str) -> Any:
        """Forward attribute reads to the underlying JS bot.

        Private names (leading underscore) are not forwarded — they should
        be set via `object.__setattr__` in this class or raise AttributeError.

        Ref: mineflayer/index.d.ts — all fields on the Bot interface
        """
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            value = getattr(self._js, name)
        except AttributeError as exc:
            if name == "pathfinder":
                raise PluginNotInstalledError(_PATHFINDER_MISSING) from exc
            raise
        # The real JSPyBridge proxy returns None for missing JS attributes
        # instead of raising AttributeError (bridge.js answers 'void' for
        # undefined), so the except-branch above never fires against a live
        # bridge — check the value too, or students get a bare
        # "'NoneType' object has no attribute 'goto'" instead of this hint.
        if value is None:
            if name == "pathfinder":
                raise PluginNotInstalledError(_PATHFINDER_MISSING)
            self._reject_misspelling(name)
        return value

    def _reject_misspelling(self, name: str) -> None:
        """Raise ``AttributeError`` when ``name`` looks like a typo of a real one.

        Because the bridge answers ``None`` rather than raising, a misspelling
        used to be indistinguishable from an attribute that is legitimately
        ``None`` (``bot.entity`` before spawn, ``bot.heldItem`` empty-handed):
        ``bot.usernam`` evaluated to ``None`` silently, and
        ``bot.move_foward(3)`` reported ``'NoneType' object is not callable``
        without naming what was misspelled. Both are the paths a beginner hits
        most, and the course only teaches reading the error *reason*.

        Deliberately conservative — it only fires on a close match to a name that
        really exists, so an attribute that is simply absent still returns
        ``None`` as before. Being wrong here would break working scripts, which is
        worse than staying quiet.

        The name set must come from ``BOT_MEMBERS`` (generated from ``bot.pyi``),
        not from the live proxy: ``list(bot_proxy)`` yields only JavaScript's
        *own* enumerable keys, so a documented property JS has not assigned yet is
        absent from it. ``bot.vehicle`` is exactly that — ``undefined`` until the
        first mount — and an earlier version of this method, keyed on proxy keys,
        rejected it as a typo of ``moveVehicle``. The proxy keys are still unioned
        in, to cover anything a plugin adds at runtime.

        Ref: javascript/js/bridge.js — 'void' reply for undefined properties;
        javascript/proxy.py — Proxy.__iter__ lists the JS object's own keys.
        """
        known = set(BOT_MEMBERS)
        known.update(dir(type(self)))
        known.update(bounded_keys(self._js))
        if name in known:
            return  # a real attribute that happens to be None
        hint = suggest(name, sorted(known))
        if not hint:
            return
        msg = f"機器人沒有「{name}」這個東西。{hint}"
        raise AttributeError(msg)

    def load_plugin(
        self,
        name: str,
        version: str | None = None,
        *,
        export_key: str | None = None,
        **options: Any,
    ) -> Any:
        """Install a Type A mineflayer plugin in one line.

        Args:
            name: npm package name (e.g. ``"mineflayer-pathfinder"``).
            version: pinned version string. Bundled plugins may omit this and
                use minethon's pinned default; all other packages must pass an
                explicit version so npm resolution stays reproducible.
            export_key: which attribute of the loaded module holds the
                plugin installer function. Pass this for packages whose
                installer is a named export (e.g. pathfinder's ``pathfinder``).
                Overrides the built-in defaults in ``_PLUGIN_EXPORT_KEY``.
            **options: collected into a Python dict and forwarded as a
                single JS options-object to higher-order plugin factories
                (e.g. ``dashboard({port: 25566})`` → ``bot.load_plugin(
                "@ssmidge/mineflayer-dashboard", port=25566)``). This
                matches the standard JS ``factory(opts)`` convention and
                is required because JSPyBridge's ``Proxy.__call__`` only
                accepts positional args — Python ``**kwargs`` expansion
                would raise ``TypeError`` at the bridge boundary.
                Regular plugins ignore this.

        Returns:
            The raw JS module — use the result to access classes/constants
            the plugin exports, e.g. ``pf.goals.GoalNear(x, y, z, 1)``.

        Ref: mineflayer/index.d.ts — Bot.loadPlugin (expects a ``(bot, options) => void`` function)
        """
        resolved_version = _resolve_package_version(name, version)
        module = require(name, resolved_version)
        key = export_key or _PLUGIN_EXPORT_KEY.get(name)
        plugin_fn = getattr(module, key) if key else module
        if options:
            # Pass as a single JS object — JSPyBridge marshals the Python
            # dict to a JS object literal. `plugin_fn(**options)` would fail
            # because the bridge's Proxy.__call__ rejects keyword args.
            plugin_fn = plugin_fn(options)
        self._js.loadPlugin(plugin_fn)
        return module

    @staticmethod
    def require(name: str, version: str | None = None) -> Any:
        """Raw escape hatch — load a JS module and return its proxy.

        Use for Type B/C/D plugins (prismarine-viewer, web-inventory,
        mineflayer-statemachine, etc.) that don't fit the single-call
        ``bot.loadPlugin`` pattern. You get the raw module back; initialize
        it yourself following the package's README.

        Args:
            name: npm package name.
            version: pinned version. Pass this unless the package is one of
                minethon's bundled defaults.

        Returns:
            The raw JS module proxy — everything on it is untyped.

        Ref: javascript.require (JSPyBridge)
        """
        resolved_version = _resolve_package_version(name, version)
        return require(name, resolved_version)

    def bind(self, handlers: EventAdaptor) -> EventAdaptor:
        """Register every overridden ``on_<event>`` on an `EventAdaptor` instance.

        This is the **only** public event-registration entry point. Walks the
        generated :class:`EventAdaptor` method set, finds entries overridden on
        the concrete subclass, and wires each one to the JS EventEmitter on
        the matching mineflayer event. Handler arity is normalized by
        ``_normalize_handler``, so short signatures like
        ``def on_chat(self, username, message)`` work even though the typed
        signature declares more parameters.

        Returns the handlers instance so calls can chain.

        Example::

            class My(EventAdaptor):
                def on_chat(self, username, message, *_): ...

            bot.bind(My())
        """
        js_bot = self._js
        for attr, event in EVENT_ATTRIBUTE_MAP.items():
            method_name = f"on_{attr}"
            impl = getattr(type(handlers), method_name, None)
            base_impl = getattr(EventAdaptor, method_name, None)
            if impl is None or impl is base_impl:
                continue
            handler = getattr(handlers, method_name)
            On(js_bot, event.value)(
                _normalize_handler(handler, emitter=js_bot, event_name=event.value)
            )
        # A typo'd handler name (`on_chatt`, `on_Spawn`) silently never fires —
        # the most common beginner mistake with class-based handlers. Walk the
        # subclass's own on_* methods and call out any that match no event.
        known = {f"on_{attr}" for attr in EVENT_ATTRIBUTE_MAP}
        unknown: list[str] = []
        for klass in type(handlers).__mro__:
            if klass is EventAdaptor:
                break
            for name, member in vars(klass).items():
                if (
                    name.startswith("on_")
                    and callable(member)
                    and name not in known
                    and name not in unknown
                ):
                    unknown.append(name)
        for name in sorted(unknown):
            print(  # noqa: T201 — student-facing, intentional
                f"提醒：`{name}` 不是任何 mineflayer 事件，永遠不會被觸發。"  # noqa: RUF001 — zh-TW fullwidth colon
                "請檢查拼字（例如 on_chat、on_spawn；完整清單見 EventAdaptor 的方法）。",  # noqa: RUF001 — zh-TW fullwidth semicolon
                flush=True,
            )
        return handlers

    def run_forever(self) -> None:
        """Block the calling thread until the bot disconnects.

        Intended as the last line of a student script — keeps the main
        Python thread alive while JSPyBridge's event thread drives the
        bot. Exits cleanly on `end` event or Ctrl-C.

        Uses `Once` so repeated calls don't accumulate listeners on the
        underlying JS EventEmitter.

        Ref: mineflayer/index.d.ts — Bot.on('end', reason)
        """
        if _INTERRUPT["seen"]:  # already shutting down — don't re-block
            return
        done = threading.Event()

        def _on_end(*_a: Any, **_kw: Any) -> None:
            done.set()

        try:
            Once(self._js, BotEvent.END.value)(
                _normalize_handler(_on_end, emitter=self._js)
            )
            # Race guard: if `end` fired between create_bot() returning and the
            # Once(...) above, no listener was installed and done.wait() would
            # block forever. Seed `done` from the protocol client's `ended` flag
            # (minecraft-protocol sets it synchronously in end()/disconnect()).
            # `_client` is an internal minecraft-protocol attribute; warn loudly
            # if it ever disappears so a silent indefinite hang is noticed.
            client = getattr(self._js, "_client", None)
            if client is None:
                warnings.warn(
                    "bot._client 不存在，run_forever() 無法防止提早 disconnect"
                    "造成的卡死。若在 create_bot() 與 run_forever() 之間斷線，"
                    "需要手動 Ctrl-C。",
                    RuntimeWarning,
                    stacklevel=2,
                )
            elif bool(getattr(client, "ended", False)):
                done.set()
            done.wait()
        except KeyboardInterrupt:
            if not _INTERRUPT["seen"]:  # disconnect already printed its message
                _INTERRUPT["seen"] = True
                print(_GOODBYE)  # noqa: T201 — student-facing, intentional
        except Exception as exc:  # noqa: BLE001 — atexit must not raise
            # Bridge already dead/unresponsive (e.g. disconnect mid-command).
            # Nothing to keep alive; exit quietly instead of dumping a stack.
            if _is_bridge_failure(exc) and not _INTERRUPT["seen"]:
                _INTERRUPT["seen"] = True
                print(_CONNECTION_LOST)  # noqa: T201 — student-facing


# Seconds to wait after spawn (shorthand path) before acting — covers the
# server's post-login invulnerability / settle window.
_SPAWN_SETTLE_SECONDS = 3.5


def _announce_then_keep_alive(bot: Bot) -> None:
    """Say the script finished, then hold the bot online (the atexit path).

    ``run_forever`` blocks until the server drops the bot, which for a healthy
    connection never happens — so a straight-line script that simply runs off the
    end produced no further output and never returned. "Finished" and "hung" look
    identical when both are a blank terminal, and every quest example has exactly
    that shape (no ``quit()``, no ``run_forever()``). Even with an explicit
    ``bot.quit()`` there is a measured ~30s wait for the server's `end` before the
    process goes away.

    Only the implicit path announces: a script that calls ``run_forever()``
    itself is event-driven and staying online on purpose.
    """
    if _INTERRUPT["seen"]:
        return
    print(_SCRIPT_DONE, flush=True)  # noqa: T201 — student-facing, intentional
    bot.run_forever()


def _require_reachable(host: str, port: int) -> None:
    """Stop with one friendly line when the server's port cannot be reached.

    mineflayer pings the server as soon as ``createBot`` returns, and forwards a
    failed ping as a bot-level `error` (``loader.js``). Our `error` listener is
    registered on the next bridge round-trip, so a connection refusal lands in
    the gap where the bot has no listener at all — Node's EventEmitter then
    throws, killing the node process with ~77 lines of ``AggregateError
    [ECONNREFUSED]`` stack, after which the friendly handler can no longer read
    the error object and prints "連線發生錯誤:" with nothing after the colon.
    Measured: 10.5 seconds of that, for the single most likely failure at an
    event (server down, wrong host, no network).

    Winning that race is not worth attempting when the question — "is anything
    listening?" — is answerable directly and more precisely. Anything past the
    TCP handshake (bad credentials, version mismatch, whitelist) still flows
    through the existing `error` / `kicked` handlers, which by then are attached.
    """
    try:
        socket.create_connection((host, port), timeout=_REACHABILITY_TIMEOUT).close()
    except OSError:
        _stop_with_message(_UNREACHABLE.format(host=host, port=port), code=1)


def create_bot(
    account: str | None = None,
    *,
    instruction_sleep: float = _DEFAULT_INSTRUCTION_SLEEP,
    bypass_instruction_sleep: bool = False,
    **options: Any,
) -> Bot:
    """Create and connect a mineflayer bot.

    Two ways to call it:

    - `create_bot(host=..., username=...)` — explicit options mirroring
      `mineflayer.createBot()` with snake_case (`auth_server` → `authServer`).
    - `create_bot("g-swim")` / `create_bot("swim")` — Hack-The-SDGs shorthand:
      host + credentials are resolved from this PC's identity file, and the call
      blocks until the bot has spawned so a straight-line student script can act
      immediately. Explicit keyword options still override resolved ones.

    Every action command pauses `instruction_sleep` seconds afterwards so each
    step of a straight-line script is visible. Pass `bypass_instruction_sleep=True`
    to turn that off, or `instruction_sleep=0.1` to shorten it.

    Ref: mineflayer/lib/loader.js — `createBot(options)`
    """
    if account is not None:
        options = {**resolve_account(account), **options}
    js_options = {_to_camel(key): value for key, value in options.items()}
    # mineflayer defaults logErrors=true, registering its own bot.on('error',
    # console.log) that dumps the raw stack (e.g. the yggdrasil auth trace) on
    # top of our friendly message. Turn it off; _on_login_error handles errors.
    # Ref: mineflayer lib/loader.js — options.logErrors ?? true.
    js_options.setdefault("logErrors", False)
    mineflayer = get_mineflayer()
    _install_quiet_interrupt()
    _require_reachable(
        str(js_options.get("host") or "localhost"),
        int(js_options.get("port") or _DEFAULT_PORT),
    )
    js_bot = mineflayer.createBot(js_options)
    pace = 0.0 if bypass_instruction_sleep else instruction_sleep
    bot = Bot(js_bot, instruction_sleep=pace)
    # Turn a login failure (wrong task name, task closed) into a friendly line
    # instead of the raw yggdrasil stack; also unblocks the wait_spawn below,
    # which would otherwise hang forever since 'spawn' never fires.
    Once(js_bot, BotEvent.ERROR.value)(
        _normalize_handler(
            _on_login_error, emitter=js_bot, event_name=BotEvent.ERROR.value
        )
    )
    # Surface the kick reason. mineflayer's logErrors=false (above) plus our
    # own listeners would otherwise swallow it entirely — a version mismatch
    # or whitelist kick showed nothing but the generic disconnect line.
    Once(js_bot, BotEvent.KICKED.value)(
        _normalize_handler(_on_kicked, emitter=js_bot, event_name=BotEvent.KICKED.value)
    )
    # mineflayer leaves bot.vehicle pointing at the old vehicle after a
    # dismount, which pins is_riding() to True for the rest of the session.
    _install_dismount_repair(js_bot)
    # mineflayer 4.37.0 paired with a minecraft-data that lacks
    # 'entityVelocityIsLpVec3' mis-parses every 1.21.2+ knockback packet into
    # NaN velocity; one punch would poison bot.entity.position (and so every
    # position read) for the rest of the session.
    _install_velocity_repair(js_bot)
    # End the script automatically when the server drops the bot, wherever the
    # main thread happens to be (mid-script or in the keep-alive below). `Once`
    # (not `On`) so the callback removes itself after firing — a lingering
    # callback would deadlock JSPyBridge's atexit on_exit (it waits while any
    # callback is still registered and the node process is alive).
    Once(js_bot, BotEvent.END.value)(
        _normalize_handler(
            lambda *_a, **_k: _stop_with_message(_DISCONNECTED), emitter=js_bot
        )
    )
    # Keep the bot alive after the student's straight-line script ends, so they
    # don't have to remember a trailing bot.run_forever(). Fires on normal exit;
    # returns immediately if the bot already disconnected (e.g. bot.quit()) or
    # the student pressed Ctrl-C.
    atexit.register(_announce_then_keep_alive, bot)
    if account is not None:
        bot.wait_spawn()
        # Post-spawn invulnerability window: the server may still teleport /
        # settle the player for a moment. Wait it out before the student's
        # straight-line script starts acting, to avoid unexpected behaviour.
        time.sleep(_SPAWN_SETTLE_SECONDS)
        # Level the view. A bot does not spawn looking at the horizon (measured
        # -52° to -68° on the competition server), and dig / place / use /
        # look_block all resolve through blockAtCursor — at that pitch they target
        # the floor, so `bot.dig()` breaks the ground instead of what is in front.
        # Do it after the settle wait, so a server teleport during it cannot undo
        # the aim. See Commands.look_level.
        bot.look_level()
    return bot


def _to_camel(snake: str) -> str:
    """snake_case → camelCase (auth_server → authServer)."""
    head, *tail = snake.split("_")
    return head + "".join(part.capitalize() for part in tail)


def _resolve_package_version(name: str, version: str | None) -> str:
    if version is not None:
        return version
    default = BUNDLED_VERSIONS.get(name)
    if default is not None:
        return default
    msg = (
        f"`{name}` 需要顯式版本號。請改成 "
        f"`bot.require({name!r}, 'x.y.z')` 或 "
        f"`bot.load_plugin({name!r}, 'x.y.z')`。"
    )
    raise VersionPinRequiredError(msg)
