# מאגר העבודה של אילייה

| מה | איפה |
|---|---|
| **מכונת הספרים ל-KDP** — חוקים, מפרטים, פרומפט 8 תפקידים, מחשבון תמלוגים | `.claude/skills/kdp-factory/` |
| ספרים בייצור | `kdp/` |
| גיבוי הסקילים האישיים (BubiPop) | `skills-backup/` |
| סקריפט גיבוי | `backup.sh` |

## גיבוי
```bash
./backup.sh                  # מסנכרן סקילים, מוסיף הכל, דוחף ל-GitHub
```
הכל בענף `claude/amazon-book-creation-machine-fxlvzm` ב-GitHub. כל דחיפה היא הגיבוי.

## התחלה מהירה — כמה ארוויח על ספר?
```bash
python3 .claude/skills/kdp-factory/scripts/kdp_calc.py \
    --pages 110 --ink bw --trim large --price 9.99 --target 500
```
