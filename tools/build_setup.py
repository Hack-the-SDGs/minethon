#!/usr/bin/env python3
"""Build password-gated, AES-encrypted setup.sh / setup.ps1.

These one-time scripts mark a student PC's group + computer number into a hidden
identity file (``~/.htsdg.json``) that `create_bot("g-swim")` reads. Staff run
them once per machine; students never get the password.

The plaintext "payload" (what actually runs) is encrypted with
``openssl enc -aes-256-cbc -pbkdf2`` so opening setup.sh / setup.ps1 shows only a
Base64 blob. At runtime each script prompts for the password, decrypts, and runs.

    python tools/build_setup.py --password 'YOUR_STAFF_PASSWORD'

Honest limit: this only stops people WITHOUT the password. Anyone who has it can
dump the plaintext. And `create_bot`'s salt lives in the importable SDK, so the
account passwords are recoverable by reading minethon — this is casual deterrence,
not real security. Protect accounts server-side (event-scoped, rate-limited).

Requires: openssl on PATH (macOS/Linux ship it; Git-for-Windows bundles it).
The generated setup.ps1 decrypts the same openssl format with pure .NET, so the
target Windows machine does NOT need openssl.
"""

from __future__ import annotations

import argparse
import base64
import subprocess
import sys
from pathlib import Path

ITER = 100_000
ROOT = Path(__file__).resolve().parent.parent

# ── plaintext payloads (the real marking logic) ───────────────────────────────

PAYLOAD_SH = r"""
set -euo pipefail
read -rp "組別 group number: " GROUP
read -rp "電腦編號 computer number: " COMPUTER
case "$GROUP$COMPUTER" in
  *[!0-9]*) echo "只接受數字" >&2; exit 1 ;;
esac
printf '{"group": %d, "computer": %d}\n' "$GROUP" "$COMPUTER" > "$HOME/.htsdg.json"
echo "已寫入 $HOME/.htsdg.json (group=$GROUP, computer=$COMPUTER)"
"""

PAYLOAD_PS1 = r"""
$group = Read-Host "組別 group number"
$computer = Read-Host "電腦編號 computer number"
if ($group -notmatch '^\d+$' -or $computer -notmatch '^\d+$') {
    Write-Error "只接受數字"; exit 1
}
$path = Join-Path $HOME ".htsdg.json"
"{""group"": $group, ""computer"": $computer}" | Set-Content -Path $path -Encoding UTF8
Write-Host "已寫入 $path (group=$group, computer=$computer)"
"""

# ── self-decrypting wrappers ──────────────────────────────────────────────────

WRAPPER_SH = """#!/usr/bin/env bash
# minethon setup — encrypted, password-gated. Run once per student PC.
set -euo pipefail
read -rsp "Password: " PW; echo
PAYLOAD='{blob}'
# Decrypt to a variable first: openssl exits non-zero on a wrong password, and
# running the plaintext separately keeps stdin on the terminal so the payload's
# own `read` prompts work (piping the script into bash would steal that stdin).
PLAIN=$(echo "$PAYLOAD" | base64 -d \\
  | openssl enc -d -aes-256-cbc -pbkdf2 -iter {iter} -pass pass:"$PW" 2>/dev/null) \\
  || {{ echo "密碼錯誤或解密失敗" >&2; exit 1; }}
bash -c "$PLAIN"
"""

WRAPPER_PS1 = """# minethon setup — encrypted, password-gated. Run once per student PC.
$ErrorActionPreference = 'Stop'
$sec = Read-Host -AsSecureString "Password"
$pw = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
$blob = [Convert]::FromBase64String('{blob}')
# openssl "Salted__" format: magic(8) + salt(8) + ciphertext
$salt = $blob[8..15]
$ct = [byte[]]($blob[16..($blob.Length - 1)])
$kdf = New-Object System.Security.Cryptography.Rfc2898DeriveBytes(
    $pw, [byte[]]$salt, {iter}, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$keyiv = $kdf.GetBytes(48)
$aes = [System.Security.Cryptography.Aes]::Create()
$aes.Key = $keyiv[0..31]; $aes.IV = $keyiv[32..47]
$aes.Mode = 'CBC'; $aes.Padding = 'PKCS7'
try {{
    $plain = [Text.Encoding]::UTF8.GetString(
        $aes.CreateDecryptor().TransformFinalBlock($ct, 0, $ct.Length))
}} catch {{
    Write-Error "密碼錯誤或解密失敗"; exit 1
}}
Invoke-Expression $plain
"""


def encrypt(plaintext: str, password: str) -> str:
    """openssl AES-256-CBC + PBKDF2 → Base64 (the 'Salted__' container)."""
    result = subprocess.run(
        [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-pbkdf2",
            "-iter",
            str(ITER),
            "-salt",
            "-pass",
            f"pass:{password}",
        ],
        input=plaintext.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return base64.b64encode(result.stdout).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build encrypted setup scripts.")
    parser.add_argument("--password", required=True, help="staff decryption password")
    args = parser.parse_args()

    sh = WRAPPER_SH.format(blob=encrypt(PAYLOAD_SH, args.password), iter=ITER)
    ps1 = WRAPPER_PS1.format(blob=encrypt(PAYLOAD_PS1, args.password), iter=ITER)

    # Dedicated folder so we never clobber the repo's dev-install setup.sh.
    out_dir = ROOT / "pc_setup"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "setup.sh").write_text(sh, encoding="utf-8")
    (out_dir / "setup.ps1").write_text(ps1, encoding="utf-8")
    (out_dir / "setup.sh").chmod(0o755)
    print(f"Wrote {out_dir}/setup.sh and {out_dir}/setup.ps1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
