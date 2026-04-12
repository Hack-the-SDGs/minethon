"""Bot — public entry point for minethon.

Runtime behavior lives here. A sibling `bot.pyi` (generated from
mineflayer's `index.d.ts`) supplies the typed overloads that IDEs
use for completion of event names, callback signatures, and
properties like `bot.health`, `bot.entity.position`, etc.

Pure synchronous callback model — no asyncio. Long-running JS work
(dig, goto, ...) reports completion via events registered with
`@bot.on(event)`.
"""

from __future__ import annotations

import inspect
import threading
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from javascript import On, Once, require

from minethon._bridge import get_mineflayer

F = TypeVar("F", bound=Callable[..., Any])


def _normalize_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """Adapt a user handler to mineflayer's loose event-arity conventions.

    Mineflayer's TypeScript typings sometimes declare trailing callback
    parameters that the JS runtime never actually emits (the ``chat`` event's
    ``matches: string[] | null`` is the canonical example — the type
    advertises 5 args but ``lib/plugins/chat.js`` only emits 4). A handler
    written against the declared signature would otherwise crash with
    ``TypeError: missing positional argument``.

    This wrapper:

    * pads missing trailing positional args with ``None``
    * truncates any excess positional args JS emits
    * returns ``func`` untouched when it already accepts ``*args``

    Ref: mineflayer/lib/plugins/chat.js:85 — chat event emit arity
    """
    params = list(inspect.signature(func).parameters.values())
    if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in params):
        return func
    slots = sum(
        1
        for p in params
        if p.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if len(args) < slots:
            args = (*args, *([None] * (slots - len(args))))
        return func(*args[:slots], **kwargs)

    return wrapper


# npm package → attribute on the required module that holds the plugin
# installer function. Most plugins export the installer as the default,
# but a few (pathfinder) expose it on a named property.
_PLUGIN_EXPORT_KEY: dict[str, str] = {
    "mineflayer-pathfinder": "pathfinder",
}


class Bot:
    """Pythonic façade over a mineflayer Bot proxy.

    Prefer `create_bot(...)` over direct construction. Unknown attribute
    reads fall through to the underlying JS proxy, so every documented
    mineflayer property or method works transparently.

    Ref: mineflayer/index.d.ts — Bot interface
    """

    _js: Any

    def __init__(self, js_bot: Any) -> None:
        """Wrap an existing mineflayer JS bot proxy."""
        object.__setattr__(self, "_js", js_bot)

    def __getattr__(self, name: str) -> Any:
        """Forward attribute reads to the underlying JS bot.

        Private names (leading underscore) are not forwarded — they should
        be set via `object.__setattr__` in this class or raise AttributeError.

        Ref: mineflayer/index.d.ts — all fields on the Bot interface
        """
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._js, name)

    def on(self, event: str) -> Callable[[F], F]:
        """Register a handler for a mineflayer event.

        Per-event typed overloads live in `bot.pyi`; at runtime this is a
        generic dispatcher. Handlers run on the JSPyBridge event thread —
        do not block them with long Python work.

        Handler arity is auto-normalized: mineflayer occasionally types
        more callback params than it emits (the ``chat`` event is the
        classic case), so missing trailing args are padded with ``None``.

        Ref: mineflayer/index.d.ts — Bot extends EventEmitter, see `on()`
        """
        js_bot = self._js

        def decorator(func: F) -> F:
            On(js_bot, event)(_normalize_handler(func))
            return func

        return decorator

    def once(self, event: str) -> Callable[[F], F]:
        """Register a one-shot event handler.

        Same arity-normalization rules apply as ``on()``.

        Ref: mineflayer/index.d.ts — Bot.once (from EventEmitter)
        """
        js_bot = self._js

        def decorator(func: F) -> F:
            Once(js_bot, event)(_normalize_handler(func))
            return func

        return decorator

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
            version: pinned version string, or None to use whatever is
                already installed in the bridge's node_modules. Pass this
                explicitly in production scripts so behavior is reproducible.
            export_key: which attribute of the loaded module holds the
                plugin installer function. Pass this for packages whose
                installer is a named export (e.g. pathfinder's ``pathfinder``).
                Overrides the built-in defaults in ``_PLUGIN_EXPORT_KEY``.
            **options: keyword options forwarded to higher-order plugin
                factories (e.g. ``@ssmidge/mineflayer-dashboard``). Regular
                plugins ignore this.

        Returns:
            The raw JS module — use the result to access classes/constants
            the plugin exports, e.g. ``pf.goals.GoalNear(x, y, z, 1)``.

        Ref: mineflayer/index.d.ts — Bot.loadPlugin (expects a ``(bot, options) => void`` function)
        """
        module = require(name, version)
        key = export_key or _PLUGIN_EXPORT_KEY.get(name)
        plugin_fn = getattr(module, key) if key else module
        if options:
            plugin_fn = plugin_fn(options)
        self._js.loadPlugin(plugin_fn)
        return module

    def require(self, name: str, version: str | None = None) -> Any:
        """Raw escape hatch — load a JS module and return its proxy.

        Use for Type B/C/D plugins (prismarine-viewer, web-inventory,
        mineflayer-statemachine, etc.) that don't fit the single-call
        ``bot.loadPlugin`` pattern. You get the raw module back; initialize
        it yourself following the package's README.

        Args:
            name: npm package name.
            version: pinned version or None.

        Returns:
            The raw JS module proxy — everything on it is untyped.

        Ref: javascript.require (JSPyBridge)
        """
        return require(name, version)

    def run_forever(self) -> None:
        """Block the calling thread until the bot disconnects.

        Intended as the last line of a student script — keeps the main
        Python thread alive while JSPyBridge's event thread drives the
        bot. Exits cleanly on `end` event or Ctrl-C.

        Ref: mineflayer/index.d.ts — Bot.on('end', reason)
        """
        done = threading.Event()

        def _on_end(*_a: Any, **_kw: Any) -> None:
            done.set()

        self.on("end")(_on_end)
        try:
            done.wait()
        except KeyboardInterrupt:
            pass


def create_bot(**options: Any) -> Bot:
    """Create and connect a mineflayer bot.

    Keyword options mirror `mineflayer.createBot()` with snake_case:
    `auth_server` → `authServer`, `session_server` → `sessionServer`, etc.
    Typed overloads live in `bot.pyi`.

    Returns immediately; the bot connects on the JS side. Register a
    `spawn` handler to know when you can send chat, move, etc.

    Ref: mineflayer/lib/loader.js — `createBot(options)`
    """
    js_options = {_to_camel(key): value for key, value in options.items()}
    mineflayer = get_mineflayer()
    js_bot = mineflayer.createBot(js_options)
    return Bot(js_bot)


def _to_camel(snake: str) -> str:
    """snake_case → camelCase (auth_server → authServer)."""
    head, *tail = snake.split("_")
    return head + "".join(part.capitalize() for part in tail)
