# הרצת כל האיורים מול ChatGPT — פרומפט אחד

## מה שצריך לדעת לפני

**ChatGPT לא מייצר 47 תמונות מהודעה אחת.** הוא מייצר **תמונה אחת לכל תור**.
אין דרך לעקוף את זה, ומי שאומר אחרת מוכר לך קורס.

מה שכן אפשר: להזריק את כל הכללים **פעם אחת** בתחילת השיחה, ואז לכתוב `next`
ולקבל את הבא בתור בלי לחזור על הפרומפט. זה ההבדל בין 44 הדבקות ארוכות
לבין 44 פעמים המילה `next`.

**רזולוציה — אל תילחם בזה:** המקסימום של ChatGPT בפורטרט הוא **1024×1536**.
על עמוד 11 אינץ' זה 139 DPI. KDP דורש 300. **אין הגדרה שתפתור את זה.**
לכן `prep_art.py` הוא חלק קבוע מהצינור, לא פתרון חירום.
בחר 1024×1536 (פורטרט) — זה הכי טוב שיש, והשאר שלי.

---

## שלב 1 — הדבק את זה פעם אחת, בתחילת שיחה חדשה

```
You are my illustration engine for a children's activity book.
We are going to produce 44 images in this conversation, one per turn.

=== PERMANENT RULES - apply to EVERY image, never restate them to me ===

TECHNICAL
- Size: 1024x1536 (portrait). Never landscape, never square, no exceptions.
- Pure white background. Pure black lines. Nothing else.

STYLE
- Black and white coloring book line art for toddlers aged 3-6.
- Bold, uniform black outlines, thick and even, like a marker.
- Large open areas that a small child can fill in.
- NO shading. NO gradients. NO gray. NO cross-hatching. NO texture.
- NO fur detail, NO scales, NO feather detail, NO tiny dots.
- NO text, NO letters, NO border, NO frame, NO watermark, NO signature.
- Kawaii-friendly: big head, big round eyes, simple smile.
- Vector-like clean lines, printable at large size.

FOR ANIMALS (items 1-37)
- Exactly ONE animal per image. Front-facing, smiling, whole body visible.
- The animal fills about 70% of the frame, centered, clean white margin all around.
- Where I give a count (three spots, four stripes), use EXACTLY that count,
  drawn LARGE. Never many small marks.
- The outer contour must be one clean closed shape.

FOR SCENES (items 38-41)
- Environment ONLY. This is the single most important rule in this whole job:
  the ENTIRE CENTER of the image must stay EMPTY WHITE SPACE.
- ABSOLUTELY NO animals, no creatures, no people anywhere in a scene.
- Keep every sky and every water area WHITE, never filled black.

=== HOW WE WORK ===
When I write "next", generate the next item in the queue below and nothing else.
Do not ask questions. Do not explain. Do not show me the prompt.
Above each image write only its number and its filename, like:
    04 - color_ocean_turtle.png
Then generate the image.

=== THE QUEUE ===
01 color_ocean_turtle.png       sea turtle
02 color_ocean_fish.png         round tropical fish
03 color_ocean_crab.png         crab with big claws
04 color_ocean_octopus.png      octopus with eight simple tentacles
05 color_ocean_starfish.png     starfish
06 color_ocean_whale.png        whale with a water spout
07 color_ocean_seahorse.png     seahorse
08 color_sky_butterfly.png      butterfly with big simple wings
09 color_sky_bee.png            bumblebee with two thick stripes
10 color_sky_bird.png           small round bird
11 color_sky_ladybug.png        ladybug with exactly five large dots
12 color_sky_dragonfly.png      dragonfly
13 color_sky_parrot.png         parrot
14 color_sky_eagle.png          eagle with spread wings
15 color_sky_hummingbird.png    hummingbird
16 color_farm_pig.png           pig
17 color_farm_sheep.png         sheep with simple cloud-shaped wool
18 color_farm_horse.png         horse
19 color_farm_duck.png          duck
20 color_farm_chicken.png       chicken
21 color_farm_goat.png          goat
22 color_farm_rabbit.png        rabbit with long ears
23 color_jungle_lion.png        lion with a simple round mane
24 color_jungle_elephant.png    elephant
25 color_jungle_monkey.png      monkey
26 color_jungle_giraffe.png     giraffe with exactly five large spots
27 color_jungle_zebra.png       zebra with exactly five thick stripes
28 color_jungle_tiger.png       tiger with exactly four thick stripes
29 color_jungle_snake.png       friendly coiled snake
30 color_jungle_crocodile.png   smiling crocodile
31 color_night_fox.png          fox
32 color_night_hedgehog.png     hedgehog with about twelve thick spikes
33 color_night_deer.png         deer with simple antlers
34 color_night_bat.png          friendly bat with open wings
35 color_night_raccoon.png      raccoon
36 color_night_bear.png         bear
37 color_night_wolf.png         wolf

--- SCENES: environment only, empty center, no creatures ---
38 scene_sky.png       Open sky. ONLY: a smiling sun in the top left, three big
                       simple clouds, a rainbow arc on the right, one bare tree
                       branch entering from the bottom right corner.
                       No birds. No insects. Center empty.
39 scene_farm.png      A farm. ONLY: a simple barn with a door and one window on
                       the left, a wooden fence along the bottom, a small round
                       pond on the right, two simple hills on the horizon.
                       No animals. No people. Center empty.
40 scene_jungle.png    A jungle. ONLY: two tall palm trees at the left and right
                       edges, three hanging vines, a curving river across the
                       bottom, one large rounded rock, a few big simple leaves
                       in the corners. No animals. Center empty.
41 scene_night.png     A forest at night. ONLY: a crescent moon top right, six
                       simple five-point stars, two pine trees at the edges, one
                       thick tree trunk with a round hollow opening on the left,
                       two rounded bushes at the bottom. Sky stays WHITE, not
                       filled black. No owls. No animals. Center empty.

--- COVER ART ---
42 cover_hero.png      Six simple cartoon animals - dolphin, butterfly, cow,
                       lion, owl, turtle - arranged in a loose ring with a LARGE
                       EMPTY WHITE OVAL in the middle where a title will go.
43 cover_scissors.png  A simple icon of child safety scissors, bold outline.
44 color_night_owl.png Owl with big round eyes. REGENERATE IN PORTRAIT - the
                       previous attempt came out landscape.

Reply with only "ready" and wait for my first "next".
```

---

## שלב 2 — העבודה

תכתוב `next`. תקבל תמונה. תוריד. תכתוב `next` שוב. 44 פעמים.

**אם הסגנון נסחף** (קווים נהיים דקים, מופיע אפור, מופיעות חיות בסצנות) — תכתוב:
```
Style drift. Re-read the PERMANENT RULES and regenerate that item.
```

**אם סצנה חוזרת עם חיות** — זה קורה, זה הכשל הכי נפוץ:
```
There are creatures in that scene. The center must be COMPLETELY EMPTY
white space. Regenerate with environment elements only.
```

---

## שלב 3 — מה שאני עושה

תעלה לי את כל הקבצים. אני מריץ:

```bash
python3 prep_art.py --in raw --out art     # 300 DPI, 1-bit, שחור-לבן טהור
python3 build_interior.py --art ./art --out interior.pdf
python3 build_cover.py    --art ./art --out cover.pdf
```

**שמות הקבצים לא חייבים להיות מדויקים** — תגיד לי מה כל תמונה ואני אסדר.
