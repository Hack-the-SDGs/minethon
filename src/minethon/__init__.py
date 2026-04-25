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
