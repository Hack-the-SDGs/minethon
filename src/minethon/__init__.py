"""minethon — a Python-first Mineflayer SDK.

Typical usage::

    from minethon import EventAdaptor, create_bot

    bot = create_bot(
        host="mc.example.com",
        port=25565,
        username="my_bot",
    )


    class Greeter(EventAdaptor):
        def on_spawn(self) -> None:
            bot.chat("Hello from minethon!")

        def on_chat(self, username, message, *_):
            if message == "quit":
                bot.quit("bye")


    bot.bind(Greeter())
    bot.run_forever()
"""

from __future__ import annotations

import sys

from minethon._events import BotEvent
from minethon._handlers import EventAdaptor
from minethon.bot import Bot, create_bot
from minethon.errors import (
    MinethonError,
    NotSpawnedError,
    PlayerNotFoundError,
    PluginNotInstalledError,
    VersionPinRequiredError,
)

# Force UTF-8 on stdout/stderr so Chinese messages never raise UnicodeEncodeError
# on Windows, where redirected/piped output otherwise falls back to cp950/cp1252.
# ponytail: source parsing is already UTF-8 (PEP 3120); this only fixes output.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="backslashreplace")
        except ValueError, OSError:  # detached or non-reconfigurable stream
            pass

__all__ = [
    "Bot",
    "BotEvent",
    "EventAdaptor",
    "MinethonError",
    "NotSpawnedError",
    "PlayerNotFoundError",
    "PluginNotInstalledError",
    "VersionPinRequiredError",
    "create_bot",
]
