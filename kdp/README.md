# KDP Factory — מכונת ייצור ספרים וחוברות לאמזון

| קובץ | מה זה |
|---|---|
| `01_KDP_RULES_RESEARCH.md` | כל התנאים, החוקים, המפרטים והמספרים של KDP — מאומת מול דפי העזרה הרשמיים, ספטמבר 2026 |
| `02_MASTER_PROMPT.md` | **הפרומפט הראשי** — 8 תפקידים, 3 שערי החלטה, מנישה עד קבצים מוכנים להעלאה |
| `kdp_calc.py` | מחשבון תמלוגים/עלות הדפסה/עובי שדרה — לבדוק כלכלה לפני שכותבים עמוד |

## התחלה מהירה
```bash
# כמה ארוויח על חוברת עבודה 120 עמ', שחור-לבן, 8.5x11, במחיר $12.99?
python3 kdp_calc.py --pages 120 --ink bw --trim large --price 12.99 --target 500

# מה המחיר המינימלי המותר לספר צביעה 60 עמ' בצבע פרימיום?
python3 kdp_calc.py --pages 60 --ink premium_color --trim large

# תמלוג eBook
python3 kdp_calc.py --ebook --price 9.99 --mb 2
```

אחר כך: פתח את `02_MASTER_PROMPT.md`, מלא את 4 השדות, הדבק בצ'אט עם גישה לאינטרנט.

## ספר ראשון בייצור
`book_01/` — Color, Cut & Glue: Animal Homes. מפרט מלא + סקריפט בנייה.
```bash
pip install reportlab pillow
python3 book_01/build_interior.py --out proof.pdf          # פרוף עם מקומות שמורים
python3 book_01/build_interior.py --art ./art --out interior.pdf
```
