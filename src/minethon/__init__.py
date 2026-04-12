"""minethon — a Python-first Mineflayer SDK.

Typical usage::

    from minethon import create_bot

    bot = create_bot(
        host="mc.example.com",
        port=25565,
        username="my_bot",
    )

    @bot.on("spawn")
    def on_spawn() -> None:
        bot.chat("Hello from minethon!")

    @bot.on("chat")
    def on_chat(username: str, message: str) -> None:
        if message == "quit":
            bot.quit("bye")

    bot.run_forever()
"""

from __future__ import annotations

from minethon.bot import Bot, create_bot

__all__ = ["Bot", "create_bot"]
