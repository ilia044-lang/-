# KDP — פרויקטי ספרים בייצור

הידע, החוקים והכלים עברו ל**סקיל**: `.claude/skills/kdp-factory/`.
התיקייה הזו מחזיקה רק את הספרים עצמם.

| תיקייה | מה |
|---|---|
| `book_01/` | Color, Cut & Glue: Animal Homes — 110 עמ', 8.5×11, ש/ל, חד-צדדי |

## בנייה
```bash
pip install reportlab pillow
python3 book_01/build_interior.py --out proof.pdf            # פרוף עם מקומות שמורים
python3 book_01/build_interior.py --art ./art --out interior.pdf
```

## מחשבון
```bash
python3 ../.claude/skills/kdp-factory/scripts/kdp_calc.py --pages 110 --ink bw --trim large --price 9.99
```
