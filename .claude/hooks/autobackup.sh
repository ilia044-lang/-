#!/usr/bin/env bash
# Stop hook: commits and pushes everything so the repo is never left unbacked.
# Emits JSON with a systemMessage so the result is visible in the UI.
set -uo pipefail

input=$(cat 2>/dev/null || echo '{}')
# recursion guard: never re-run while a stop hook is already running
if command -v jq >/dev/null 2>&1; then
  [[ "$(echo "$input" | jq -r '.stop_hook_active // false')" == "true" ]] && exit 0
fi

msg() {
  printf '{"systemMessage":%s,"suppressOutput":true}\n' \
    "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/')"
}

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$root" || exit 0
[[ -z "$(git remote 2>/dev/null)" ]] && exit 0

branch=$(git branch --show-current)
[[ -z "$branch" ]] && { msg "⚠ הגיבוי לא רץ — HEAD מנותק"; exit 0; }

# refresh the skills mirror first, without letting it push on its own
[[ -x ./backup.sh ]] && BACKUP_NO_PUSH=1 ./backup.sh >/dev/null 2>&1

changed=$(git status --porcelain | wc -l | tr -d ' ')
if [[ "$changed" != "0" ]]; then
  git add -A >/dev/null 2>&1
  git commit -q -m "backup: auto-save $(date -u '+%Y-%m-%d %H:%M UTC')" >/dev/null 2>&1
fi

ahead=$(git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo 0)
[[ "$ahead" == "0" && "$changed" == "0" ]] && exit 0

if git push -q -u origin "$branch" >/dev/null 2>&1; then
  msg "🟣 מגובה — נדחף ל-$branch"
else
  msg "🔴 הגיבוי נכשל — הרץ ./backup.sh ידנית (ענף $branch)"
fi
exit 0
