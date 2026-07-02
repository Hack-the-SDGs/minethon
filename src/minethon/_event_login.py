"""Hack-The-SDGs event login shorthand.

Lets students write ``create_bot("g-swim")`` or ``create_bot("swim")`` with no
host/credentials. Each PC's group + computer number live in a hidden file that
staff write once per machine via ``setup.sh`` / ``setup.ps1``.

Shorthand → real account (usernames use "_" — never "-"):

    create_bot("g_swim")  → username "G<group>_swim"
                            password sha256("Hack-The-SDGs-Python@<group>")
    create_bot("swim")    → username "U<computer>_swim"
                            password sha256("Hack-The-SDGs-Python@<group>:<computer>")

Security note: the salt below lives in importable code, so these passwords are
NOT secret from anyone who reads the SDK. This is casual deterrence only — real
account protection is server-side (event-scoped accounts, rate limits, rotation).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from minethon.errors import MinethonError

_SALT = "Hack-The-SDGs-Python@"

# Hidden per-machine identity, written once by the staff setup script.
IDENTITY_FILE = Path.home() / ".htsdg.json"

# Baked event defaults — public infrastructure, safe to ship in the SDK.
_DEFAULTS: dict[str, Any] = {
    "host": "mc.ntust.camp",
    "port": 50213,
    "auth": "mojang",
    "auth_server": "https://drasl.ntust.camp/auth",
    "session_server": "https://drasl.ntust.camp/session",
    "version": "1.21.11",
}


def _read_identity() -> tuple[int, int]:
    if not IDENTITY_FILE.exists():
        msg = (
            f"找不到本機識別檔 {IDENTITY_FILE}。"
            "請先請工作人員執行 setup.sh / setup.ps1 標記本機的組別與電腦編號。"
        )
        raise MinethonError(msg)
    try:
        # utf-8-sig tolerates a UTF-8 BOM (older PowerShell Set-Content emits
        # one) so a stray BOM doesn't break json.loads on already-set-up PCs.
        data = json.loads(IDENTITY_FILE.read_text(encoding="utf-8-sig"))
        return int(data["group"]), int(data["computer"])
    except (ValueError, KeyError, OSError) as exc:
        msg = f"本機識別檔 {IDENTITY_FILE} 內容無效，請重跑 setup.sh / setup.ps1。"
        raise MinethonError(msg) from exc


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_account(shorthand: str) -> dict[str, Any]:
    """Map a task shorthand to full ``create_bot`` options.

    A ``g-`` / ``g_`` prefix means a group account; anything else is the
    personal account. Generated usernames join with "_" (server forbids "-").
    """
    group, computer = _read_identity()
    if shorthand[:2] in ("g-", "g_"):
        task = shorthand[2:]
        username = f"G{group}_{task}"
        password = _sha256(f"{_SALT}{group}")
    else:
        username = f"U{computer}_{shorthand}"
        password = _sha256(f"{_SALT}{group}:{computer}")
    return {**_DEFAULTS, "username": username, "password": password}
