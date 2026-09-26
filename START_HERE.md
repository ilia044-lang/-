# START HERE

30 שניות להבין איפה הכל עומד. לפרטים: `CLAUDE.md` (מדיניות) ו-`HANDOFF.md` (מצב מלא).

## הפרויקט
ספרי ילדים ל-Amazon KDP, שוק ארה"ב. שם עט **Ilia Rai**. יעד: עד **$200/חודש**.
בידול: איליה פרמדיק 20 שנה → "Written by a Paramedic" בספרי בטיחות.

## שלושת הכללים שמפילים הכל אם שוברים אותם
1. **רק איליה לוחץ Publish.** Claude מכין טיוטה עם תאריך מתוזמן, לא יותר.
2. **כל כלל בטיחות/עזרה ראשונה דורש אישור מפורש של איליה** לפני איור ועימוד.
3. **מה שלא סוכם — "לא הוחלט".** לא ממציאים, שואלים.

## שישה ספרים — מצב

| # | ספר | מצב | קבצים בריפו |
|---|---|---|---|
| 1 | Awesome Activity Book | טיוטה ב-KDP עם **קבצים ישנים** | ❌ |
| 2 | Pencil Control | מעומד, לא הועלה | ❌ |
| 3 | Letter Tracing | מעומד, לא הועלה | ❌ |
| 4 | Number Tracing | מעומד, לא הועלה | ❌ |
| 5 | M20 Brave Little Helpers | מושהה — "לא מרגיש ספר" | ❌ |
| 6 | Zoe and the Five Safety Stars | 13/16 איורים נוצרו | ⚠️ קבצים לא הגיעו |
| + | Color, Cut & Glue: Animal Homes | בנוי ומאומת | ✅ 41 קבצים |

**ספרים 1–5 קיימים רק אצל איליה.** הם לא בריפו. עד שיועברו, אי אפשר לגעת בהם.

## התקנה
```bash
pip install reportlab pypdf pillow fonttools pypdfium2 pymupdf scipy
apt-get install -y poppler-utils        # pdftoppm, לאימות דו-מנועי
```

## בנייה — Color, Cut & Glue
```bash
cd books/color-cut-glue-animal-homes
python3 check_art.py --dir art
python3 prep_art.py --in raw --out art
python3 build_interior.py --art ./art --out output/interior.pdf
COVER_THEME=sunshine python3 build_cover.py --art ./art --out output/cover.pdf
```

## גיבוי
אוטומטי. Stop hook דוחף בסוף כל תשובה, לענף ול-`main`. ידנית: `./backup.sh`.
