# Zoe and the Five Safety Stars — 17 פרומפטים מלאים

**עודכן 26.9.2026.** 40 עמודים, 8.5×8.5, Premium Color, bleed.

---

## ⚠️ קודם כל — הרזולוציה. זה המקום שבו זה ייכשל.

| | |
|---|---|
| גודל עמוד עם bleed | 8.625" × 8.75" |
| **נדרש ב-300 DPI** | **2588 × 2625 px** |
| תמונה ריבועית חייבת להיות | **2625 px מינימום בכל צלע** |

**מה שיקרה בפועל:**

| מה שהמחולל יחזיר | DPI בהדפסה | |
|---|---|---|
| 1024 px | 117 | ✗ מטושטש |
| 1536 px | 176 | ✗ מטושטש |
| 2048 px | 234 | ✗ גבולי, עדיין מתחת לתקן |
| **2625 px** | **300** | ✓ עובר |
| 4096 px | 468 | ✓ מצוין |

**אני לא יודע מה הרזולוציה המקסימלית של Grok** ולא אמציא מספר.
**בדוק בעצמך על התמונה הראשונה:** הורד אותה, קליק ימני → *מידע*, ותסתכל על הממדים.

- **2625 px ומעלה** → מושלם, אין מה לעשות.
- **מתחת** → אפשר לשחזר, אבל **לא לאיור מצויר.** הגדלה עובדת על קווים עבים
  ופשוטים (כמו ספר הצביעה), **לא** על גואש עם מרקם נייר והצללות רכות.
  שם היא תיראה מרוחה. אם Grok נותן רק 1024 — **עדיף מחולל אחר.**

---

## שלושת הכשלים שכבר קרו — והניסוח שמונע אותם

| הכשל | מה שגרם לו | הניסוח שמונע |
|---|---|---|
| **פס שטוח עם קו חד בראש התמונה** | ביקשנו "keep the top third for text" | `the characters fill only the lower two-thirds; above them is a wide open sky painted as one continuous seamless sky` |
| **מסגרת נייר דקה סביב האיור** | Gemini מוסיף אותה מעצמו | `full bleed edge to edge, the illustration extends completely to all four edges, no frame, no border, no paper edge, no white margin, no vignette` |
| **טקסט וכתוביות בתוך האיור** | לא נאסר מספיק חזק | `NO text, NO letters, NO numbers, NO captions, NO speech bubbles, NO signs, NO labels, NO watermark` |

**וכלל נוסף שעלה מסצנה 13:** צלב אדום **אסור**. הוא סימן מוגן של התנועה
הבינלאומית של הצלב האדום; שימוש מסחרי בו אסור ואמזון מסירה עליו.
בכל סצנה עם ציוד רפואי: `ABSOLUTELY NO red cross symbol`.

---

## שלב 1 — הדבק פעם אחת בתחילת השיחה

```
You are my illustration engine for a children's picture book.
We will produce 17 images in this conversation, one per turn.

=== TECHNICAL — EVERY IMAGE ===
- Square 1:1.
- Generate at the HIGHEST resolution available. I need at least 2625 x 2625
  pixels. Tell me the pixel dimensions of every image you produce.
- FULL BLEED: the illustration extends completely to all four edges.
  NO frame, NO border, NO paper edge, NO white margin, NO vignette,
  NO rounded corners, NO drop shadow around the image.

=== STYLE — EVERY IMAGE ===
Hand-painted children's picture book illustration in soft gouache and colored
pencil, visible warm paper grain texture, gentle hand-drawn outlines, warm
natural light, cheerful palette of sunny yellow, coral, sky blue, leafy green
and warm cream, rounded friendly shapes, big expressive eyes, cozy and calm
mood, American suburban setting.

=== COMPOSITION — EVERY IMAGE ===
The characters fill only the LOWER TWO-THIRDS of the picture. Above them is a
wide, open, uninterrupted area - sky, ceiling or wall - painted as ONE
CONTINUOUS SEAMLESS surface with no hard edge, no band and no panel. Text will
be placed there later, but do NOT leave a blank strip and do NOT draw one.

=== FORBIDDEN — EVERY IMAGE ===
NO text, NO letters, NO numbers, NO captions, NO speech bubbles, NO signs,
NO labels, NO logos, NO watermark, NO signature.
ABSOLUTELY NO red cross symbol anywhere, on any vehicle, bag or uniform.
NO brand names. NO photorealism. NO 3D render look.

=== CHARACTER SHEET — repeat the full description in every prompt ===
ZOE: a 6-year-old girl with warm brown skin, a round face, big round dark-brown
eyes, rosy cheeks, a big cloud of curly black hair tied on top with a yellow
scrunchie, wearing a coral t-shirt, blue denim overall shorts, white sneakers
with yellow laces, and a bright yellow backpack with one big white star on it.

PICKLES: a real small scruffy puppy (never a plush toy) with cream-white fur,
one caramel-brown floppy ear, a caramel patch around his left eye, big shiny
black eyes, a pink tongue, and a red collar with a round gold tag.

MOM: a young woman with warm brown skin, curly black hair in a high puff, gold
hoop earrings, a sage-green sweater and jeans.
DAD: a young man with warm brown skin, short black hair, a short neat beard,
round glasses, a mustard-yellow sweater and khaki pants.
OFFICER GRANT: a friendly older police officer, light tan skin, gray mustache,
kind smiling eyes, dark navy uniform and cap, a plain gold star badge with no
text.
MS. RIVERA: a cheerful teacher, light olive skin, long wavy dark-brown hair,
a teal cardigan over a white blouse.
COACH JAY: a young lifeguard with freckles and sandy hair, red swim shorts, a
red tank top with no text, a silver whistle on a cord, a red rescue tube.
AUNT SAM: a young woman with warm brown skin, short curly hair, a navy paramedic
uniform with reflective silver stripes and NO text and NO badges, a stethoscope.
LEO: a boy with light skin, short ginger hair, a green t-shirt and green shorts.

=== HOW WE WORK ===
When I write "next", generate the next item and nothing else. Do not explain.
Above each image write only its number, filename and pixel size, like:
    04 - zoe-scene-04.png - 2048x2048
Then generate the image.

Reply with only "ready" and wait for my first "next".
```

---

## שלב 2 — 17 הפרומפטים, אחד בכל תור

> בכל תור: הדבק `next`, ואז את הפרומפט של הפריט.
> **את הבלוק מלמעלה אין צורך לחזור עליו** — הוא כבר בשיחה.

### 01 — zoe-scene-01.png · המרפסת, המשאלה
```
SCENE 1: the front porch of a suburban American house on a bright morning. Zoe
stands on the wooden porch steps hugging Pickles, who stands on his hind legs
against her. She looks up and away with a big hopeful smile - she is making a
wish. ZOE and PICKLES exactly as in the character sheet.
```

### 02 — zoe-scene-02.png · הכיתה, הכוכב
```
SCENE 2: a sunny classroom. Children sit cross-legged on a colorful rug. Zoe
sits in front with her yellow backpack beside her, one arm raised high, mouth
open with excitement. MS. RIVERA stands at the right holding up one big shiny
gold star, smiling. ZOE and MS. RIVERA exactly as in the character sheet.
```

### 03 — zoe-scene-03.png · הסלון, כבל המנורה
```
SCENE 3: a cozy living room. Pickles has a lamp cord in his mouth and is pulling
it; a side table with a lamp on it wobbles. Zoe stands in the middle, both palms
raised in a clear STOP gesture, worried but calm. DAD appears in the doorway on
the right, surprised and moving toward them. ZOE, PICKLES and DAD exactly as in
the character sheet.
```

### 04 — zoe-scene-04.png · המטבח, אזור חם · כוכב 1
```
SCENE 4: a bright kitchen. MOM stands at the stove flipping a pancake in a pan.
Zoe is mid-motion taking a big step backwards away from the stove, arms out for
balance, a careful expression on her face. Pickles watches from the right. One
single small gold star sticker is on Zoe's yellow backpack. ZOE, MOM and PICKLES
exactly as in the character sheet.
```

### 05 — zoe-scene-05.png · המדרכה, אורות נסיעה לאחור
```
SCENE 5: a quiet suburban street in autumn. A car at the left has its white
reverse lights glowing and is beginning to back up. Zoe stands safely on the
sidewalk holding DAD's hand and pointing at the car with a serious, alert face.
Pickles sits at her feet on a red leash. One gold star on her backpack. ZOE, DAD
and PICKLES exactly as in the character sheet.
```

### 06 — zoe-scene-06.png · מעבר חצייה
```
SCENE 6: a street corner with a wide white crosswalk. OFFICER GRANT stands in
the road holding a red octagonal stop paddle with NO letters on it; a yellow
school bus waits behind him. Zoe stands at the curb holding DAD's hand, one hand
shading her eyes as she looks left. Pickles sits beside her on a red leash. ZOE,
DAD, PICKLES and OFFICER GRANT exactly as in the character sheet.
```

### 07 — zoe-scene-07.png · הכדור והניקוז
```
SCENE 7: the edge of a suburban street after rain, water running along the gutter
toward a storm drain. A small ball rolls toward the drain. Pickles leans forward
after it; Zoe grabs his collar and holds him back, one palm raised in a STOP
gesture, alarmed but in control. ZOE and PICKLES exactly as in the character
sheet.
```

### 08 — zoe-scene-08.png · כוכב 2
```
SCENE 8: the same street corner. OFFICER GRANT kneels on one knee in front of
Zoe and pins a shiny gold star onto her yellow backpack. Zoe smiles proudly.
DAD stands behind her, smiling. Pickles sits at her feet. Two gold stars are now
on the backpack. ZOE, DAD, PICKLES and OFFICER GRANT exactly as in the character
sheet.
```

### 09 — zoe-scene-09.png · אזעקת אש
```
SCENE 9: a school playground on a sunny day. A line of calm children, Zoe among
them near the front, walks in an orderly single file away from the school
building toward a big tree. Nobody runs. MS. RIVERA walks alongside the line
with a reassuring hand raised. Zoe looks calm and focused. Two gold stars on her
backpack. ZOE and MS. RIVERA exactly as in the character sheet.
```

### 10 — zoe-scene-10.png · הזר בשער · כוכב 3
```
SCENE 10: the front gate of an American elementary school in the afternoon.
Outside the low fence, a friendly-looking man Zoe does not know - gray hoodie,
baseball cap, NOT scary, simply a stranger - waves and smiles. Zoe stays inside
the schoolyard, already turning and running toward MS. RIVERA, who walks toward
her with an open, caring face and arms slightly out. Three gold stars on the
backpack. ZOE and MS. RIVERA exactly as in the character sheet.
```

### 11 — zoe-scene-11.png · הבריכה, Leo רץ
```
SCENE 11: a public swimming pool on a summer day. LEO runs along the wet pool
edge. COACH JAY sits on the lifeguard chair at the right, whistle at his lips,
one hand raised in a clear STOP gesture. Zoe walks calmly beside MOM on the left,
both of them at a safe walking pace. ZOE, MOM, LEO and COACH JAY exactly as in
the character sheet.
```

### 12 — zoe-scene-12.png · במים, אמא צופה · כוכב 4
```
SCENE 12: the same swimming pool. Zoe is in the shallow water wearing orange arm
floats, waving happily. MOM sits at the pool edge with her feet in the water,
looking straight at Zoe and waving back - clearly watching her. COACH JAY sits
on the lifeguard chair behind them. ZOE, MOM and COACH JAY exactly as in the
character sheet.
```

### 13 — zoe-scene-13.png · Leo נופל · ⚠️ הייצור הקודם נפסל
```
SCENE 13: a school parking area on a sunny afternoon. LEO sits on the ground
holding his scraped knee with a worried face. Zoe stands beside him, calm and
confident, raising one arm to wave toward AUNT SAM, who is hurrying over
carrying a plain dark-green first-aid bag with a white handle. Behind them, a
plain white ambulance with NO markings, NO symbols and NO lettering of any kind.
Four gold stars on Zoe's backpack. ZOE, LEO and AUNT SAM exactly as in the
character sheet. ABSOLUTELY NO red cross symbol on the ambulance, the bag or the
uniform.
```

### 14 — zoe-scene-14.png · Aunt Sam חובשת · כוכב 5
```
SCENE 14: the same school parking area. AUNT SAM kneels and gently places a
colorful bandage on LEO's knee; an open plain dark-green first-aid bag, a water
bottle and clean gauze lie beside her. Leo smiles bravely. Aunt Sam turns her
head toward Zoe and pins a fifth shiny gold star onto her yellow backpack. Zoe
beams. ZOE, LEO and AUNT SAM exactly as in the character sheet. ABSOLUTELY NO
red cross symbol anywhere.
```

### 15 — zoe-scene-15.png · Junior Safety Star
```
SCENE 15: a joyful celebration in the schoolyard. Zoe stands in the center
wearing a shiny gold medal on a ribbon, her yellow backpack covered with five
gold stars, both arms raised in triumph. Around her, cheering: MOM, DAD, OFFICER
GRANT, MS. RIVERA, COACH JAY and AUNT SAM, with LEO and other children clapping.
Pickles jumps happily at her feet. Colorful paper confetti in the air. All
characters exactly as in the character sheet.
```

### 16 — zoe-scene-16.png · לפני השינה
```
SCENE 16: Zoe's cozy bedroom at night, lit by a warm bedside lamp, with a big
window showing a starry night sky. Zoe sits in bed in yellow pajamas, smiling
sleepily, counting the five gold stars on her yellow backpack which hangs on the
bedpost. Pickles is fast asleep, curled at the foot of the bed. ZOE and PICKLES
exactly as in the character sheet.
```

### 17 — zoe-cover.png · הכריכה
```
BOOK COVER illustration. Zoe and Pickles, large and close to the viewer, fill
the lower 60% of the picture. Zoe looks straight at the viewer with a big proud
smile and gives a thumbs up; her yellow backpack shows five shiny gold stars.
Pickles stands beside her, also looking at the viewer, tongue out. Behind them,
softly out of focus: a crosswalk, a yellow school bus and a school building. The
upper 40% is a wide, bright, open sky with a few soft clouds and sparkling gold
stars, painted as one continuous seamless sky. ZOE and PICKLES exactly as in the
character sheet. Warm saturated palette of sunny yellow, coral and sky blue.
```

---

## שלב 3 — בדוק כל תמונה לפני שאתה ממשיך

| בדיקה | אם נכשל |
|---|---|
| **גודל ≥ 2625 px** | תבקש שוב ברזולוציה גבוהה. אם המחולל לא מסוגל — תחליף מחולל |
| **אין מסגרת/שוליים** | `Regenerate with true full bleed. The illustration must reach all four edges. No frame, no border, no paper edge.` |
| **אין טקסט** | `There is text in that image. Regenerate with NO text, NO letters, NO captions, NO speech bubbles.` |
| **אין צלב אדום** | `Remove the red cross. It is a protected emblem. Plain white ambulance, plain green bag, no symbols.` |
| **Zoe נראית אותו דבר** | `Zoe drifted. Re-read the character sheet and regenerate.` |
| **אין פס שטוח בראש** | `There is a flat band across the top. The sky must be one continuous painted surface with no hard edge.` |

**אל תחליף מחולל באמצע.** 16 סצנות בשני סגנונות = ספר שנראה זול.

---

## שלב 4 — לשלוח אליי

**ZIP אחד.** גרירת תמונות בודדות לצ'אט **לא שומרת אותן** — זה מה שקרה ל-13
האיורים הקודמים, ראיתי אותם ולא יכולתי לשמור. שמות לא משנים, אני אזהה ואמקם.
