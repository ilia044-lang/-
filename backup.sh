#!/usr/bin/env bash
# גיבוי מלא: מסנכרן את הסקילים האישיים מהמכונה לתוך הריפו ודוחף ל-GitHub.
# הרצה: ./backup.sh  [הודעת commit]
set -euo pipefail
cd "$(dirname "$0")"

BRANCH="${BACKUP_BRANCH:-claude/amazon-book-creation-machine-fxlvzm}"
MINE=(bubipop-channel-ops bubipop-video-production)   # רק הסקילים שלנו
SRC=""
for d in "$HOME"/.claude/skills/synced/*/; do
  [ -d "$d/${MINE[0]}" ] && SRC="$d" && break
done

if [ -n "$SRC" ]; then
  for s in "${MINE[@]}"; do
    if [ -d "$SRC/$s" ]; then
      rm -rf "skills-backup/$s"
      cp -r "$SRC/$s" skills-backup/
      echo "  ✓ $s"
    else
      echo "  ! $s לא נמצא במכונה — משאיר את הגיבוי הקיים"
    fi
  done
else
  echo "  ! לא נמצאה תיקיית skills מסונכרנת — משאיר את הגיבוי הקיים"
fi

# called from the Stop hook: mirror the skills only, let the hook commit and push
[ "${BACKUP_NO_PUSH:-0}" = "1" ] && exit 0

git add -A
if git diff --cached --quiet; then
  echo "אין שינויים לגבות."
else
  git commit -q -m "${1:-backup: sync skills and project files $(date -u +%Y-%m-%d)}"
  for i in 1 2 4 8 16; do
    git push -u origin "$BRANCH" && { echo "✓ נדחף ל-$BRANCH"; exit 0; }
    echo "push נכשל, מנסה שוב בעוד ${i}s..."; sleep "$i"
  done
  echo "✗ push נכשל אחרי 5 נסיונות"; exit 1
fi
