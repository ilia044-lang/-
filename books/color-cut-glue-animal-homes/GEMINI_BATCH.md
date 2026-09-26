# 37 האיורים החסרים — פרומפט ל-Google Gemini

**יתרון אמיתי של Gemini כאן:** הוא מייצר ברזולוציה גבוהה בהרבה מ-ChatGPT.
תבקש **4K / highest quality** — אם תקבל ~2048×3072 או יותר, זה **קרוב ל-300 DPI
במקור** ולא יצטרך שום שחזור. בקש את זה במפורש.

**מה שלא ישתנה:** גם Gemini מייצר תמונה אחת בכל תור. אין דרך לקבל 37 מהודעה
אחת. מה שהפרומפט הזה עושה הוא לנעול את הכללים **פעם אחת**, ואז אתה כותב `next`.

---

## הדבק פעם אחת בשיחה חדשה

```
You are my illustration engine for a children's colouring book.
We will produce 37 images in this conversation, one per turn.

=== PERMANENT RULES - apply to EVERY image, never restate them to me ===

TECHNICAL
- PORTRAIT orientation, aspect ratio 3:4. Never landscape, never square.
- Generate at the HIGHEST resolution you can. I need at least 2048x2730.
- Pure white background. Pure black lines. Nothing else.

STYLE
- Black and white colouring book line art for toddlers aged 3-6.
- Bold, uniform black outlines, thick and even, like a marker.
- Large open areas a small child can fill in with a crayon.
- NO shading. NO gradients. NO grey. NO cross-hatching. NO texture.
- NO fur detail, NO scales, NO feather detail, NO tiny dots or speckles.
- NO text, NO letters, NO border, NO frame, NO watermark, NO signature.
- Kawaii-friendly: big head, big round eyes, simple smile.
- Clean vector-like lines that stay crisp when printed large.

FOR ANIMALS (items 1-33)
- Exactly ONE animal per image. Front-facing, smiling, whole body visible.
- The animal fills about 70% of the frame, centred, clean white margin around it.
- Where I give a count (three spots, four stripes), use EXACTLY that count,
  drawn LARGE. Never many small marks.
- The outer contour must be one clean closed shape - a child will cut along it.

FOR SCENES (items 34-37)
- Environment ONLY. This is the most important rule in the whole job:
  the ENTIRE CENTRE of the image must stay EMPTY WHITE SPACE.
- ABSOLUTELY NO animals, no creatures, no people anywhere in a scene.
- Keep every sky and every water area WHITE, never filled black.

=== HOW WE WORK ===
When I write "next", generate the next item in the queue and nothing else.
Do not ask questions. Do not explain. Do not show me the prompt back.
Above each image write only its number and filename, like:
    04 - color_sky_ladybug.png
Then generate the image.

=== THE QUEUE ===

--- OCEAN (2) ---
01 color_ocean_turtle.png       sea turtle with a patterned shell, five large plates
02 color_ocean_seahorse.png     seahorse

--- SKY (8) ---
03 color_sky_butterfly.png      butterfly with big simple wings
04 color_sky_bee.png            bumblebee with exactly two thick stripes
05 color_sky_bird.png           small round bird
06 color_sky_ladybug.png        ladybug with exactly five large dots
07 color_sky_dragonfly.png      dragonfly
08 color_sky_parrot.png         parrot
09 color_sky_eagle.png          eagle with spread wings
10 color_sky_hummingbird.png    hummingbird

--- FARM (7) ---
11 color_farm_pig.png           pig
12 color_farm_sheep.png         sheep with simple cloud-shaped wool
13 color_farm_horse.png         horse
14 color_farm_duck.png          duck
15 color_farm_chicken.png       chicken
16 color_farm_goat.png          goat
17 color_farm_rabbit.png        rabbit with long ears

--- JUNGLE (8) ---
18 color_jungle_lion.png        lion with a simple round mane
19 color_jungle_elephant.png    elephant
20 color_jungle_monkey.png      monkey
21 color_jungle_giraffe.png     giraffe with exactly five large spots
22 color_jungle_zebra.png       zebra with exactly five thick stripes
23 color_jungle_tiger.png       tiger with exactly four thick stripes
24 color_jungle_snake.png       friendly coiled snake
25 color_jungle_crocodile.png   smiling crocodile

--- FOREST AT NIGHT (7) ---
26 color_night_fox.png          fox
27 color_night_hedgehog.png     hedgehog with about twelve thick spikes
28 color_night_deer.png         deer with simple antlers
29 color_night_bat.png          friendly bat with open wings
30 color_night_raccoon.png      raccoon
31 color_night_bear.png         bear
32 color_night_wolf.png         wolf

--- REDO ---
33 color_night_owl.png          owl with big round eyes.
                                MUST BE PORTRAIT - the earlier attempt came out
                                landscape and cannot be used.

--- SCENES: environment only, empty centre, no creatures ---
34 scene_sky.png       Open sky. ONLY: a smiling sun in the top left, three big
                       simple clouds, a rainbow arc on the right, one bare tree
                       branch entering from the bottom right corner.
                       No birds. No insects. Centre completely empty.
35 scene_farm.png      A farm. ONLY: a simple barn with a door and one window on
                       the left, a wooden fence along the bottom, a small round
                       pond on the right, two simple hills on the horizon.
                       No animals. No people. Centre completely empty.
36 scene_jungle.png    A jungle. ONLY: two tall palm trees at the left and right
                       edges, three hanging vines, a curving river across the
                       bottom, one large rounded rock, a few big simple leaves in
                       the corners. No animals. Centre completely empty.
37 scene_night.png     A forest at night. ONLY: a crescent moon top right, six
                       simple five-point stars, two pine trees at the edges, one
                       thick tree trunk with a round hollow opening on the left,
                       two rounded bushes at the bottom. The sky stays WHITE, not
                       filled black. No owls. No animals. Centre completely empty.

Reply with only "ready" and wait for my first "next".
```

---

## שתי הודעות תיקון ששווה לשמור בצד

הסגנון נסחף — קווים דקים, אפור מופיע, יותר מדי פרטים:
```
Style drift. Re-read the PERMANENT RULES and regenerate that item.
```

סצנה חזרה עם חיות — **זה הכשל הכי נפוץ, זה יקרה**:
```
There are creatures in that scene. The centre must be COMPLETELY EMPTY
white space. Regenerate with environment elements only.
```

התמונה יצאה לרוחב:
```
That came out landscape. Regenerate in PORTRAIT, 3:4.
```

---

## סדר עבודה

1. **תתחיל ב-3 בלבד** (פריטים 1, 11, 18) ותשלח לי. אני בודק שהסגנון תואם
   לשמונה האיורים שכבר בספר. Gemini לא בהכרח יצייר כמו OpenArt.
2. אם תואם — תמשיך את כל התור.
3. **אל תחליף מחולל באמצע.** 40 איורים בשני סגנונות = ספר שנראה זול,
   וזה נראה בביקורות.
4. **4 הסצנות אחרונות** — הן הכי קשות, תשמור כוח אליהן.

תעלה לי הכל בבת אחת כשזה מוכן. לא צריך שמות קבצים מדויקים, אני אסדר.
