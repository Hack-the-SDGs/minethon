#!/usr/bin/env bash
# minethon setup - run once per student PC.
set -euo pipefail

group_for() {
  local n=$1
  if (( (n>=1 && n<=10) || n==61 )); then echo 1
  elif (( (n>=11 && n<=16) || (n>=20 && n<=23) || n==62 )); then echo 2
  elif (( (n>=17 && n<=19) || (n>=24 && n<=29) || (n>=63 && n<=64) )); then echo 3
  elif (( (n>=31 && n<=37) || (n>=41 && n<=44) )); then echo 4
  elif (( (n>=38 && n<=40) || (n>=45 && n<=51) || n==65 )); then echo 5
  elif (( (n>=52 && n<=60) || (n>=66 && n<=67) )); then echo 6
  else echo 0
  fi
}

GROUP=0
COMPUTER=0
HOST=$(hostname)
if [[ "$HOST" =~ [Cc][Ss][Ii][Ee]-[Pp][Cc]([0-9]+) ]]; then
  COMPUTER=$((10#${BASH_REMATCH[1]}))
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

printf '{"group": %d, "computer": %d}\n' "$GROUP" "$COMPUTER" > "$HOME/.htsdg.json"
echo "wrote $HOME/.htsdg.json (group=$GROUP, computer=$COMPUTER)"
