# מאגר העבודה של אילייה

| מה | איפה |
|---|---|
| **מכונת הספרים ל-KDP** — חוקים, מפרטים, פרומפט 8 תפקידים, מחשבון תמלוגים | `.claude/skills/kdp-factory/` |
| ספרים בייצור | `kdp/` |
| גיבוי הסקילים האישיים (BubiPop) | `skills-backup/` |
| סקריפט גיבוי | `backup.sh` |

## גיבוי — אוטומטי

הגיבוי רץ **לבד** בסוף כל תשובה של Claude (Stop hook). אתה לא צריך לזכור כלום.

**הסימון בשורת הסטטוס אומר לך איפה אתה עומד:**

| | מצב |
|---|---|
| 🟣 **● מגובה** | הכל שמור והכל ב-GitHub. שקט. |
| 🟡 **● N לא נשמרו** | יש שינויים מקומיים שעוד לא נכנסו לקומיט |
| 🔴 **● N לא נדחפו** | שמור מקומית, אבל **לא** ב-GitHub — הרץ `./backup.sh` |

ידנית, מתי שבא לך:
```bash
./backup.sh                  # מסנכרן סקילים, מוסיף הכל, דוחף עם retry
```

הכל בענף `claude/amazon-book-creation-machine-fxlvzm` ב-GitHub.

**מה מגובה איפה:** `.claude/settings.json` מחבר את הכל —
`.claude/hooks/autobackup.sh` (Stop hook) ו-`.claude/hooks/backup-status.sh` (שורת סטטוס).

## התחלה מהירה — כמה ארוויח על ספר?
```bash
python3 .claude/skills/kdp-factory/scripts/kdp_calc.py \
    --pages 110 --ink bw --trim large --price 9.99 --target 500
```
