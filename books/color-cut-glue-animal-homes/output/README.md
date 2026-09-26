# קבצי הספר

| קובץ | מה זה |
|---|---|
| `interior.pdf` | הפנים — 110 עמודים, 8.625 × 11.25 אינץ' |
| `cover.pdf` | הכריכה המלאה — 17.4977 × 11.25 אינץ' |
| `cover_preview.png` | תצוגה מהירה של הכריכה |
| `pages_preview.png` | 21 עמודים מתוך ה-110 |

## ⚠️ אל תעלה את זה ל-KDP עדיין

**32 עמודי צביעה ו-4 סצנות הם עדיין מסגרות ריקות.** הקבצים תקינים טכנית
ויעברו את הבדיקות של KDP, אבל לקוח יקבל ספר עם חורים.

הם כאן כדי שתראה בדיוק איך הספר ייראה לפני שתשקיע בייצור האיורים.

## מצב הבדיקות

```
PASS  110 עמודים
PASS  MediaBox פנים   8.625 x 11.250 in
PASS  MediaBox כריכה  17.4977 x 11.250 in
PASS  איורים >= 300 DPI   (הגרוע ביותר: 375)
PASS  כל הגופנים מוטמעים  (Fredoka בלבד)
PASS  ניגודיות כריכה      6 מתוך 6
```

## לבנות מחדש אחרי שמוסיפים איורים

```bash
python3 prep_art.py --in raw --out art
python3 check_art.py --dir art
python3 build_interior.py --art ./art --out output/interior.pdf
COVER_THEME=sunshine python3 build_cover.py --art ./art --out output/cover.pdf
```
