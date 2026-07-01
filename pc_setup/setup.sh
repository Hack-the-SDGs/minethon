#!/usr/bin/env bash
# minethon setup — encrypted, password-gated. Run once per student PC.
set -euo pipefail
read -rsp "Password: " PW; echo
PAYLOAD='U2FsdGVkX19A2+XqkkXqGJAuLANqT8+hgYZFbJ8GoRIrR8ukPJU/vwxFTKbyWWHMtqai0MQTT9I0zQVwSqMtl68Qk/owoqScP+uii4N0dcYdJ92Ow78vdP2MWPRK0pGvaWC4meA6Fvta3aHZ2/OG8aP5aALoR+GOaHYCujS1uwsTAoOSuOVvZVN4ukXzswpGW4Jkyv9+CXAmk18RsVsZZF0tNqGcLf3wEL8ViQhz9cG5UISJ+5xUMywFtw4fQA6RVTrRA3KYEMKekNh0Mk6lYdwXiLnUiveqtw1H4UgXBnDKM6QhmfO280LVOx38hLKZyqwj3gT5e1irkC54CbBJHu7iwNZTAUzZEbEQ0hiIHEJE7Z9ZX4em5hd2eV/03yGPsKNEiq770ylrFSgTuN9sBz1COCDAJtah/dnL3tbz7Mmf8P2q+11suodT9A6y5F3s2AC9LsNo86ZCpEHRKOTbhHDUiIrtAR1ccZwbx05XaCg='
# Decrypt to a variable first: openssl exits non-zero on a wrong password, and
# running the plaintext separately keeps stdin on the terminal so the payload's
# own `read` prompts work (piping the script into bash would steal that stdin).
PLAIN=$(echo "$PAYLOAD" | base64 -d \
  | openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -pass pass:"$PW" 2>/dev/null) \
  || { echo "密碼錯誤或解密失敗" >&2; exit 1; }
bash -c "$PLAIN"
