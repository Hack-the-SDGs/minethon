#!/usr/bin/env python3
"""Write plaintext setup.sh / setup.ps1 for staff to mark a student PC.

These one-time scripts record a student PC's group + computer number into a
hidden identity file (``~/.htsdg.json``) that `create_bot("g-swim")` reads.
Staff run them once per machine.

    python pc_setup/build_setup.py

No password, no encryption: the marking logic is trivial and account security
must live server-side (event-scoped, rate-limited) regardless. All output is
ASCII to avoid Windows console encoding issues on staff machines.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SETUP_SH = r"""#!/usr/bin/env bash
# minethon setup - run once per student PC.
set -euo pipefail
read -rp "group number: " GROUP
read -rp "computer number: " COMPUTER
case "$GROUP$COMPUTER" in
  *[!0-9]*) echo "digits only" >&2; exit 1 ;;
esac
printf '{"group": %d, "computer": %d}\n' "$GROUP" "$COMPUTER" > "$HOME/.htsdg.json"
echo "wrote $HOME/.htsdg.json (group=$GROUP, computer=$COMPUTER)"
"""

SETUP_PS1 = r"""# minethon setup - run once per student PC.
$ErrorActionPreference = 'Stop'
$group = Read-Host "group number"
$computer = Read-Host "computer number"
if ($group -notmatch '^\d+$' -or $computer -notmatch '^\d+$') {
    Write-Error "digits only"; exit 1
}
$path = Join-Path $HOME ".htsdg.json"
"{""group"": $group, ""computer"": $computer}" | Set-Content -Path $path -Encoding UTF8
Write-Host "wrote $path (group=$group, computer=$computer)"
"""


def main() -> int:
    out_dir = ROOT / "pc_setup"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "setup.sh").write_text(SETUP_SH, encoding="utf-8")
    (out_dir / "setup.ps1").write_text(SETUP_PS1, encoding="utf-8")
    (out_dir / "setup.sh").chmod(0o755)
    print(f"Wrote {out_dir}/setup.sh and {out_dir}/setup.ps1")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
