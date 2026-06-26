"""Unit tests for chat (public send, stringifies any object)."""

from __future__ import annotations

from minethon._bot_runtime import Bot


class ChatJs:
    def __init__(self) -> None:
        self.sent: list[str] = []

    def chat(self, message: str) -> None:
        self.sent.append(message)


def test_chat_sends_a_string_verbatim() -> None:
    fake = ChatJs()

    Bot(fake).chat("hello world")

    assert fake.sent == ["hello world"]


def test_chat_stringifies_non_string_values() -> None:
    # Stringifying proves chat goes through the Commands mixin and not the raw
    # JS proxy fall-through (which would forward the int unchanged).
    fake = ChatJs()
    bot = Bot(fake)

    bot.chat(42)
    bot.chat([1, 2, 3])

    assert fake.sent == ["42", "[1, 2, 3]"]
