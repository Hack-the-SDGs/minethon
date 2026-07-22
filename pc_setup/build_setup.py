#!/usr/bin/env python3
"""Write plaintext setup.sh / setup.ps1 for staff to mark a student PC.

These one-time scripts record a student PC's group + computer number into a
hidden identity file (``~/.htsdg.json``) that `create_bot("g-swim")` reads.
Staff run them once per machine.

    python pc_setup/build_setup.py

When the hostname matches ``CSIE-PC<number>`` the computer number is taken from
that trailing number (leading zeros stripped) and the group is looked up from
GROUP_RANGES. Anything else (no match, or a number outside the ranges) falls
back to prompting staff for both values.

No password, no encryption: the marking logic is trivial and account security
must live server-side (event-scoped, rate-limited) regardless. All output is
ASCII to avoid Windows console encoding issues on staff machines.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Source of truth: computer number -> group. Inclusive ranges; a single machine
# is a (n, n) range. Both the bash and PowerShell lookups are generated from
# this, so they can never drift apart.
GROUP_RANGES: dict[int, list[tuple[int, int]]] = {
    1: [(1, 10), (61, 61)],
    2: [(11, 16), (20, 23), (62, 62)],
    3: [(17, 19), (24, 29), (63, 64)],
    4: [(31, 37), (41, 44)],
    5: [(38, 40), (45, 51), (65, 65)],
    6: [(52, 60), (66, 67)],
}


def group_for(n: int) -> int:
    """Return the group for computer number ``n``, or 0 if it maps to none."""
    for group, ranges in GROUP_RANGES.items():
        if any(lo <= n <= hi for lo, hi in ranges):
            return group
    return 0


def _bash_cond(ranges: list[tuple[int, int]]) -> str:
    parts = [f"n=={lo}" if lo == hi else f"(n>={lo} && n<={hi})" for lo, hi in ranges]
    return " || ".join(parts)


def _ps1_cond(ranges: list[tuple[int, int]]) -> str:
    parts = [
        f"$n -eq {lo}" if lo == hi else f"($n -ge {lo} -and $n -le {hi})"
        for lo, hi in ranges
    ]
    return " -or ".join(parts)


def _bash_group_for() -> str:
    lines = ["group_for() {", "  local n=$1"]
    keyword = "if"
    for group, ranges in GROUP_RANGES.items():
        lines.append(f"  {keyword} (( {_bash_cond(ranges)} )); then echo {group}")
        keyword = "elif"
    lines += ["  else echo 0", "  fi", "}"]
    return "\n".join(lines)


def _ps1_group_for() -> str:
    lines = ["function Group-For([int]$n) {"]
    keyword = "if"
    for group, ranges in GROUP_RANGES.items():
        lines.append(f"    {keyword} ({_ps1_cond(ranges)}) {{ return {group} }}")
        keyword = "elseif"
    lines += ["    else { return 0 }", "}"]
    return "\n".join(lines)


def _selfcheck() -> None:
    seen: dict[int, int] = {}
    for group, ranges in GROUP_RANGES.items():
        for lo, hi in ranges:
            for n in range(lo, hi + 1):
                assert n not in seen, f"computer {n} in groups {seen[n]} and {group}"
                seen[n] = group
    for n, expected in {5: 1, 61: 1, 20: 2, 64: 3, 30: 0, 44: 4, 45: 5, 67: 6}.items():
        assert group_for(n) == expected, f"group_for({n}) != {expected}"


def _setup_sh() -> str:
    return f"""#!/usr/bin/env bash
# minethon setup - run once per student PC.
set -euo pipefail

{_bash_group_for()}

GROUP=0
COMPUTER=0
HOST=$(hostname)
if [[ "$HOST" =~ [Cc][Ss][Ii][Ee]-[Pp][Cc]([0-9]+) ]]; then
  COMPUTER=$((10#${{BASH_REMATCH[1]}}))
  GROUP=$(group_for "$COMPUTER")
fi

if (( GROUP > 0 )); then
  echo "detected $HOST -> group=$GROUP, computer=$COMPUTER"
else
  read -rp "group number: " GROUP
  read -rp "computer number: " COMPUTER
  case "$GROUP$COMPUTER" in
    *[!0-9]*) echo "digits only" >&2; exit 1 ;;
  esac
  GROUP=$((10#$GROUP))
  COMPUTER=$((10#$COMPUTER))
fi

printf '{{"group": %d, "computer": %d}}\\n' "$GROUP" "$COMPUTER" > "$HOME/.htsdg.json"
echo "wrote $HOME/.htsdg.json (group=$GROUP, computer=$COMPUTER)"
"""


def _setup_ps1() -> str:
    return f"""# minethon setup - run once per student PC.
$ErrorActionPreference = 'Stop'

{_ps1_group_for()}

$group = 0
$computer = 0
$hostName = $env:COMPUTERNAME
if ($hostName -match 'CSIE-PC(\\d+)') {{
    $computer = [int]$matches[1]
    $group = Group-For $computer
}}

if ($group -gt 0) {{
    Write-Host "detected $hostName -> group=$group, computer=$computer"
}} else {{
    $group = Read-Host "group number"
    $computer = Read-Host "computer number"
    if ($group -notmatch '^\\d+$' -or $computer -notmatch '^\\d+$') {{
        Write-Error "digits only"; exit 1
    }}
    $group = [int]$group
    $computer = [int]$computer
}}

$path = Join-Path $HOME ".htsdg.json"
$json = "{{""group"": $group, ""computer"": $computer}}"
# Write UTF-8 WITHOUT a BOM. Set-Content -Encoding UTF8 adds a BOM on Windows
# PowerShell 5.1, which then breaks json parsing on the Python side. WriteAllText
# with an explicit no-BOM UTF8Encoding works on both PS 5.1 and 7.
[System.IO.File]::WriteAllText($path, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "wrote $path (group=$group, computer=$computer)"
"""


def main() -> int:
    _selfcheck()
    out_dir = ROOT / "pc_setup"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "setup.sh").write_text(_setup_sh(), encoding="utf-8")
    (out_dir / "setup.ps1").write_text(_setup_ps1(), encoding="utf-8")
    (out_dir / "setup.sh").chmod(0o755)
    print(f"Wrote {out_dir}/setup.sh and {out_dir}/setup.ps1")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
