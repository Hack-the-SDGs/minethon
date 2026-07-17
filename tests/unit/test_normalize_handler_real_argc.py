"""Unit tests for the `_REAL_ARGC` table in `_normalize_handler`.

Covers the emitter-shift bug reported in
https://github.com/Hack-the-SDGs/minethon/issues/26 — the old
identity/arity heuristic coincidentally fails for `chat`, `whisper`, and
`resourcePack`, and is bypassed entirely by any handler using a trailing
`*_` catch-all. See `_bot_runtime.py::_normalize_handler` docstring.
"""

from __future__ import annotations

from typing import Any, cast

import minethon._bot_runtime as bot_module

_normalize_handler: Any = cast("Any", bot_module)._normalize_handler


def test_normalize_handler_uses_real_argc_table_for_known_events() -> None:
    """chat: 4 real args + 1 emitter = 5, which coincidentally equals a
    fully-declared handler's slot count — the old arity_excess check
    (`len(args) > slots`) fails here (`5 > 5` is False), and proxy identity
    never matches JSPyBridge's freshly-constructed proxies either. Only the
    `_REAL_ARGC` table (`event_name="chat"`) can strip correctly.
    """
    calls: list[tuple[object, ...]] = []
    emitter = object()

    def handler(username, message, translate, json_msg, matches):
        calls.append((username, message, translate, json_msg, matches))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="chat")
    # A different object stands in for the emitter, like JSPyBridge's
    # freshly-built proxy — `is emitter` would fail here on purpose.
    fresh_proxy = object()
    wrapped(fresh_proxy, "alice", "hi", None, None)

    assert calls == [("alice", "hi", None, None, None)]


def test_normalize_handler_real_argc_table_covers_whisper() -> None:
    """whisper shares chat's exact boundary collision (same deprecated
    addChatPattern emit path — see chat.js:85) and is pinned separately so a
    typo'd or dropped `_REAL_ARGC["whisper"]` entry doesn't hide behind the
    `chat` case passing."""
    calls: list[tuple[object, ...]] = []
    emitter = object()

    def handler(username, message, translate, json_msg, matches):
        calls.append((username, message, translate, json_msg, matches))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="whisper")
    fresh_proxy = object()
    wrapped(fresh_proxy, "bob", "psst", None, None)

    assert calls == [("bob", "psst", None, None, None)]


def test_normalize_handler_real_argc_table_covers_resource_pack() -> None:
    """resourcePack: 2 real args + 1 emitter = 3, same boundary collision
    as chat but against a 3-slot handler (url, hash_, uuid)."""
    calls: list[tuple[object, ...]] = []
    emitter = object()

    def handler(url, hash_, uuid):
        calls.append((url, hash_, uuid))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="resourcePack")
    fresh_proxy = object()
    wrapped(fresh_proxy, "http://example.com/pack.zip", "some-uuid")

    assert calls == [("http://example.com/pack.zip", "some-uuid", None)]


def test_normalize_handler_real_argc_table_ignores_accepts_varargs() -> None:
    """A trailing `*_` catch-all disables the old arity_excess check
    entirely (`not accepts_varargs` is False regardless of arg count), so
    only the real-argc table path can still strip correctly for a varargs
    handler."""
    calls: list[tuple[object, ...]] = []
    emitter = object()

    def handler(username, message, *_rest):
        calls.append((username, message, _rest))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="chat")
    fresh_proxy = object()
    wrapped(fresh_proxy, "alice", "hi", None, None)

    assert calls == [("alice", "hi", (None, None))]


def test_normalize_handler_falls_back_to_heuristic_for_unknown_events() -> None:
    """Events not yet catalogued in `_REAL_ARGC` keep today's identity/arity
    heuristic untouched — pins existing behavior for the other 94 events."""
    calls: list[tuple[object | None, object | None]] = []
    emitter = object()

    def handler(username, message):
        calls.append((username, message))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="jump")
    wrapped(emitter, "alice")  # same object => old identity check still fires

    assert calls == [("alice", None)]


def test_normalize_handler_keeps_first_real_arg_for_short_handlers() -> None:
    """The pinned runtime (Node 22+) never injects the emitter, so a short
    handler receiving more real args than it declares must be truncated from
    the END. The old arity-excess heuristic treated `4 args > 2 slots` as an
    injected emitter and stripped `username`, handing the handler
    `(message, translate)` — the C3-01 regression this test pins."""
    calls: list[tuple[object | None, object | None]] = []
    emitter = object()

    def handler(username, message):
        calls.append((username, message))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="chat")
    # chat's real 4 args, no emitter injected — exactly what Node 22 sends.
    wrapped("alice", "hi", None, None)

    assert calls == [("alice", "hi")]


def test_normalize_handler_identity_still_strips_when_table_is_stale() -> None:
    """If `_REAL_ARGC["chat"]` ever drifts so the observed count no longer
    matches `real_argc + 1`, proxy identity remains the only safe fallback —
    it can never misfire on a real first argument."""
    calls: list[tuple[object | None, object | None]] = []
    emitter = object()

    def handler(username, message):
        calls.append((username, message))

    wrapped = _normalize_handler(handler, emitter=emitter, event_name="chat")
    # 3 raw args (≠ 4 + 1): the table path skips; args[0] IS the emitter.
    wrapped(emitter, "alice", "hi")

    assert calls == [("alice", "hi")]
