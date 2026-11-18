# Bedtime — סרטון דמויות-מקל (זוג + ילד)

סרטון 26 שניות, אנכי 1080×1920, אנגלית. דמויות מקוריות (לא DAFOR).
**תוצר סופי:** `bedtime_v2.mp4`

## מה כל קובץ
| קובץ | מה |
|---|---|
| `scene.html` | כל הסרטון בקוד: רקע, 3 דמויות (שלד SVG), תנוחות, דלת, כתוביות. זמנים "ישנים" |
| `scene_voiced.html` | אותו דבר + מיפוי זמנים לפי אורך הקריינות האמיתי |
| `make_voices.py` | קריינות עם Kokoro (אבא am_michael, אמא af_heart, ילד af_sky +4 חצאי טונים) |
| `mix_audio.py` | ערבוב קול + חריקת דלת + בונק + מוזיקה |
| `render.js` / `stills.js` | רינדור וידאו / פריימים בודדים לבדיקה (Playwright + ffmpeg) |
| `sfx/` | אפקטים מ-Soundza (חינם, רישיון ב-SOUNDZA-LICENSE.txt). המוזיקה (32MB) לא נשמרה — להוריד מחדש לפי ה-id |

## איך מרנדרים מחדש
```bash
node render.js $PWD/scene_voiced.html $PWD/video_only.mp4 24
python3 mix_audio.py
ffmpeg -i video_only.mp4 -i full_mix.wav -c:v copy -c:a aac -b:a 192k -af "loudnorm=I=-14:TP=-1.5:LRA=11" -shortest bedtime.mp4
```
המודל של Kokoro (325MB) לא בריפו — מורידים מ-HuggingFace: `onnx-community/Kokoro-82M-v1.0-ONNX`.

## סרטון חדש באותו סגנון
להחליף ב-`scene.html` את `LINES` (תסריט), `KF` (תנוחות), `DOOR`, `CAPTIONS`. הדמויות והחדר נשארים.

## AI
קול: Kokoro (AI). מוזיקה: Soundza "Pizzicato Comedy 2" — AI-generated. אנימציה: קוד.
