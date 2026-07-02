#!/usr/bin/env bash
# minethon setup - run once per student PC.
set -euo pipefail
read -rp "group number: " GROUP
read -rp "computer number: " COMPUTER
case "$GROUP$COMPUTER" in
  *[!0-9]*) echo "digits only" >&2; exit 1 ;;
esac
printf '{"group": %d, "computer": %d}\n' "$GROUP" "$COMPUTER" > "$HOME/.htsdg.json"
echo "wrote $HOME/.htsdg.json (group=$GROUP, computer=$COMPUTER)"
