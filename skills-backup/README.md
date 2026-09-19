# גיבוי סקילים אישיים

הסקילים האלה חיים בענן ומסונכרנים ל-`~/.claude/skills/synced/<id>/` בכל סשן.
התיקייה הזו היא **עותק בגיט** שלהם — אם הסנכרון נשבר, החשבון מתאפס, או שסקיל
נמחק בטעות, זה המקור לשחזור.

| סקיל | מה זה |
|---|---|
| `bubipop-channel-ops/` | תפעול וצמיחה של ערוץ BubiPop Kids |
| `bubipop-video-production/` | פייפליין הפקת הסרטונים — כולל דפי דמויות (bubi, maya, leo, mom, dad) |

**לא מגובים כאן:** סקילים של Anthropic (docx, pptx, xlsx, pdf, docs, skill-creator,
morning, import-memory) — הם לא שלך, הם יורדים מחדש אוטומטית, ו-4MB רעש בגיט.

## רענון הגיבוי
```bash
./backup.sh
```

## שחזור
```bash
cp -r skills-backup/bubipop-channel-ops ~/.claude/skills/
cp -r skills-backup/bubipop-video-production ~/.claude/skills/
```
