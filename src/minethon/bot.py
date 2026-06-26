"""Bot — public entry point for minethon (thin re-export).

`class Bot` and `create_bot` runtime live in `_bot_runtime`. This module
exists only so that `from minethon.bot import Bot` keeps working AND so
`bot.pyi` (the IDE type overlay) is the sole `class Bot` declaration that
PyCharm / pyright sees in `minethon.bot`. Any runtime code that wraps
mineflayer belongs in `_bot_runtime`, not here.
"""

from __future__ import annotations

from minethon._bot_runtime import Bot, create_bot

__all__ = ["Bot", "create_bot"]
