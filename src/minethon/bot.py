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

import threading
from collections.abc import Callable
from typing import Any, TypeVar

from javascript import On, Once

from minethon._bridge import get_mineflayer

F = TypeVar("F", bound=Callable[..., Any])


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

        Ref: mineflayer/index.d.ts — Bot extends EventEmitter, see `on()`
        """
        js_bot = self._js

        def decorator(func: F) -> F:
            On(js_bot, event)(func)
            return func

        return decorator

    def once(self, event: str) -> Callable[[F], F]:
        """Register a one-shot event handler.

        Ref: mineflayer/index.d.ts — Bot.once (from EventEmitter)
        """
        js_bot = self._js

        def decorator(func: F) -> F:
            Once(js_bot, event)(func)
            return func

        return decorator

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
