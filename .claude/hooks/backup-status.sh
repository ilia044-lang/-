#!/usr/bin/env bash
# Status line: one glance tells you whether everything is on GitHub.
#   purple  = committed, pushed to the branch, AND mirrored to main  <- all clear
#   orange  = branch is safe on GitHub but main has not caught up
#   yellow  = local changes not saved yet
#   red     = saved locally but not on GitHub, or no remote at all
# Reads local refs only (no network) so it stays instant; the refs are updated
# by every push the backup scripts make.
set -uo pipefail
cat >/dev/null 2>&1   # drain the stdin payload

P='\033[95m'; Y='\033[93m'; R='\033[91m'; O='\033[33m'; D='\033[90m'; N='\033[0m'

root=$(git rev-parse --show-toplevel 2>/dev/null) || { printf "${D}not a repo${N}"; exit 0; }
cd "$root" || exit 0
branch=$(git branch --show-current 2>/dev/null)
name=$(basename "$root")

if [[ -z "$(git remote 2>/dev/null)" ]]; then
  printf "${R}● אין רימוט${N} ${D}%s${N}" "$name"
  exit 0
fi

dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
ahead=$(git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo 0)
ahead_main=$(git rev-list --count "origin/main..HEAD" 2>/dev/null || echo 0)

if   (( dirty > 0 )); then
  printf "${Y}● %d לא נשמרו${N} ${D}%s · %s${N}" "$dirty" "$name" "$branch"
elif (( ahead > 0 )); then
  printf "${R}● %d לא נדחפו${N} ${D}%s · %s${N}" "$ahead" "$name" "$branch"
elif (( ahead_main > 0 )); then
  printf "${O}● main מאחור ב-%d${N} ${D}%s · %s${N}" "$ahead_main" "$name" "$branch"
else
  printf "${P}● מגובה ×2${N} ${D}%s · %s + main${N}" "$name" "$branch"
fi
