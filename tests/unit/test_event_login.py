"""Unit tests for the event-login shorthand → account resolution."""

from __future__ import annotations

import pytest

import minethon._event_login as login


@pytest.fixture(autouse=True)
def _identity(monkeypatch: pytest.MonkeyPatch) -> None:
    # group 1, computer 7
    monkeypatch.setattr(login, "_read_identity", lambda: (1, 7))


def test_group_account_username() -> None:
    assert login.resolve_account("g_swim")["username"] == "G1_swim"


def test_personal_account_username_is_letter_prefixed() -> None:
    # Must not start with a digit — "U" prefix instead of a bare number.
    name = login.resolve_account("swim")["username"]
    assert name == "U7_swim"
    assert not name[0].isdigit()
