"""Unit tests for the event-login shorthand → account resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import minethon._event_login as login
from minethon.errors import MinethonError

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def _identity(monkeypatch: pytest.MonkeyPatch) -> None:
    # group 1, computer 7. Not autouse: the _read_identity tests below need
    # the real function, and an autouse patch would silently replace it.
    monkeypatch.setattr(login, "_read_identity", lambda: (1, 7))


@pytest.mark.usefixtures("_identity")
def test_group_account_username() -> None:
    assert login.resolve_account("g_swim")["username"] == "G1_swim"


@pytest.mark.usefixtures("_identity")
def test_personal_account_username_is_letter_prefixed() -> None:
    # Must not start with a digit — "U" prefix instead of a bare number.
    name = login.resolve_account("swim")["username"]
    assert name == "U7_swim"
    assert not name[0].isdigit()


# --- _read_identity error paths -------------------------------------------
# A student who hits any of these has a broken PC, not a broken script. The
# course only teaches them to read the error reason, so every one of these
# must surface the Chinese "go find staff" line rather than a traceback.


def _identity_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    path = tmp_path / ".htsdg.json"
    path.write_text(text, encoding="utf-8")
    monkeypatch.setattr(login, "IDENTITY_FILE", path)


def test_missing_identity_file_names_the_setup_scripts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(login, "IDENTITY_FILE", tmp_path / "nope.json")
    with pytest.raises(MinethonError, match="setup"):
        login._read_identity()


@pytest.mark.parametrize(
    ("label", "content"),
    [
        ("not json at all", "}{"),
        ("json but a list", "[]"),
        ("json but a bare scalar", "5"),
        ("missing computer key", '{"group": 1}'),
        ("null value", '{"group": null, "computer": 24}'),
        ("non-numeric value", '{"group": "abc", "computer": 24}'),
        ("list value", '{"group": [1, 2], "computer": 24}'),
    ],
)
def test_corrupt_identity_file_raises_minethon_error(
    label: str, content: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _identity_file(tmp_path, monkeypatch, content)
    # Not TypeError/KeyError/ValueError leaking out — students see the
    # friendly line. `label` only names the case in pytest output.
    with pytest.raises(MinethonError, match="setup"):
        login._read_identity()


def test_utf8_bom_is_tolerated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Older PowerShell Set-Content emits a BOM; already-set-up PCs must keep working.
    _identity_file(tmp_path, monkeypatch, '\ufeff{"group": 3, "computer": 24}')
    assert login._read_identity() == (3, 24)
