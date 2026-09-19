# חבילת האיורים — 51 פרומפטים מוכנים

**שמות הקבצים כאן חייבים להישמר בדיוק** — `build_interior.py` מחפש אותם ככה.
שים הכל בתיקייה `art/` ליד הסקריפט, ואז:
```bash
python3 build_interior.py --art ./art --out interior.pdf
```

---

## 0. הגדרות קבועות לכל איור

| | |
|---|---|
| רזולוציה | **300 DPI מינימום** (8.5×11 → לפחות 2550×3300 px) |
| צבע | **שחור-לבן טהור בלבד** — אין אפור, אין הצללה |
| עובי קו | **6–8px** אחיד |
| רקע | לבן טהור, בלי מסגרת, בלי טקסט, בלי watermark |
| פורמט | PNG |

### פסילה מיידית — בדוק כל איור מול זה
- יש אזור אפור או מוצלל → **פסול**
- יש קו דק מ-4px → **פסול**
- יש טקסטורה/פרווה/קשקשים מפורטים → **פסול** (בן 3 לא יצבע את זה)
- ילד בן 3 לא מזהה את החיה בחצי שנייה → **פסול**

---

## 1. פרומפט הבסיס (החלף רק את `{ANIMAL}`)

```
Black and white coloring book page for toddlers aged 3-6.
Subject: a single friendly cartoon {ANIMAL}, front-facing, smiling, whole body visible.
Style: extremely simple, bold uniform black outlines 6-8px thick, large open areas,
NO shading, NO gradients, NO gray, NO cross-hatching, NO tiny details, NO texture.
Pure white background, pure black lines only, nothing else.
The animal fills about 70% of the frame, centered, with clean white margin all around.
Kawaii-friendly proportions: big head, big round eyes, simple smile.
Vector-like clean lines suitable for printing at 300 DPI on 8.5x11 inch paper.
No text, no letters, no border, no frame, no watermark.
```

---

## 2. 40 עמודי הצביעה — רשימת שמות קבצים

### 🌊 אוקיינוס
| קובץ | {ANIMAL} |
|---|---|
| `color_ocean_dolphin.png` | dolphin leaping |
| `color_ocean_turtle.png` | sea turtle |
| `color_ocean_fish.png` | round tropical fish |
| `color_ocean_crab.png` | crab with big claws |
| `color_ocean_octopus.png` | octopus with 8 simple tentacles |
| `color_ocean_starfish.png` | starfish |
| `color_ocean_whale.png` | whale with water spout |
| `color_ocean_seahorse.png` | seahorse |

### ☁️ שמיים
| קובץ | {ANIMAL} |
|---|---|
| `color_sky_butterfly.png` | butterfly with big simple wings |
| `color_sky_bee.png` | bumblebee with two stripes |
| `color_sky_bird.png` | small round bird |
| `color_sky_ladybug.png` | ladybug with five large dots |
| `color_sky_dragonfly.png` | dragonfly |
| `color_sky_parrot.png` | parrot |
| `color_sky_eagle.png` | eagle with spread wings |
| `color_sky_hummingbird.png` | hummingbird |

### 🚜 חווה
| קובץ | {ANIMAL} |
|---|---|
| `color_farm_cow.png` | cow with three big spots |
| `color_farm_pig.png` | pig |
| `color_farm_sheep.png` | fluffy sheep (simple cloud-shaped wool) |
| `color_farm_horse.png` | horse |
| `color_farm_duck.png` | duck |
| `color_farm_chicken.png` | chicken |
| `color_farm_goat.png` | goat |
| `color_farm_rabbit.png` | rabbit with long ears |

### 🌴 ג'ונגל
| קובץ | {ANIMAL} |
|---|---|
| `color_jungle_lion.png` | lion with a simple round mane |
| `color_jungle_elephant.png` | elephant |
| `color_jungle_monkey.png` | monkey |
| `color_jungle_giraffe.png` | giraffe with five large spots |
| `color_jungle_zebra.png` | zebra with five thick stripes |
| `color_jungle_tiger.png` | tiger with four thick stripes |
| `color_jungle_snake.png` | friendly coiled snake |
| `color_jungle_crocodile.png` | smiling crocodile |

### 🌲 יער בלילה
| קובץ | {ANIMAL} |
|---|---|
| `color_night_owl.png` | owl with big round eyes |
| `color_night_fox.png` | fox |
| `color_night_hedgehog.png` | hedgehog with about 12 thick spikes |
| `color_night_deer.png` | deer with simple antlers |
| `color_night_bat.png` | friendly bat with open wings |
| `color_night_raccoon.png` | raccoon |
| `color_night_bear.png` | bear |
| `color_night_wolf.png` | wolf |

> ⚠️ שים לב לכמויות שכתבתי — "five large dots", "four thick stripes", "about 12 spikes".
> זה לא קישוט. אם המחולל יעשה 40 נקודות קטנות, ילד בן 3 לא יצבע את זה והספר יקבל כוכב אחד.

---

## 3. 24 חיות לגזירה — פרומפט שונה

הגודל קטן יותר (4 בעמוד), אז החיה צריכה להיות **עוד יותר פשוטה** ועם **מתאר חיצוני נקי**
שאפשר לגזור סביבו.

```
Black and white coloring sticker for toddlers aged 3-6.
Subject: a single friendly cartoon {ANIMAL}, front-facing, smiling, whole body visible,
drawn as one connected compact silhouette with no thin protruding parts.
Style: extremely simple, bold uniform black outlines 6-8px thick, large open areas,
NO shading, NO gradients, NO gray, NO tiny details.
The OUTER contour must be a single smooth closed shape that a child can cut along.
Pure white background, pure black lines only.
The animal fills about 80% of the frame, centered.
Square composition. No text, no border, no frame, no watermark.
```

| קובץ | {ANIMAL} |
|---|---|
| `cut_ocean_dolphin.png` · `cut_ocean_turtle.png` · `cut_ocean_fish.png` · `cut_ocean_crab.png` | ים |
| `cut_sky_butterfly.png` · `cut_sky_bee.png` · `cut_sky_bird.png` · `cut_sky_ladybug.png` | שמיים |
| `cut_farm_cow.png` · `cut_farm_pig.png` · `cut_farm_sheep.png` · `cut_farm_horse.png` | חווה |
| `cut_jungle_lion.png` · `cut_jungle_elephant.png` · `cut_jungle_monkey.png` · `cut_jungle_giraffe.png` | ג'ונגל |
| `cut_night_owl.png` · `cut_night_fox.png` · `cut_night_hedgehog.png` · `cut_night_deer.png` | לילה |
| `cut_mixed_octopus.png` · `cut_mixed_duck.png` · `cut_mixed_zebra.png` · `cut_mixed_bat.png` | מעורב |

---

## 4. 5 סצנות בית-הגידול — הלב של הספר

כאן הכלל הפוך: הסצנה חייבת להיות **ריקה באמצע**. זה המקום שאליו הילד מדביק את החיות.
אם המחולל ימלא את הסצנה בחיות — הספר מת.

### `scene_ocean.png`
```
Black and white coloring book background scene for toddlers aged 3-6: the ocean.
Show ONLY the environment: a wavy water line across the upper third, a few simple
seaweed plants at the bottom left, two rounded coral shapes at the bottom right,
a sandy seabed line, and three or four simple bubbles in the corners.
The ENTIRE CENTER of the image must stay EMPTY white space - absolutely no animals,
no fish, no creatures anywhere in the picture.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture.
Pure white background, pure black lines only. Landscape 8.5x11 inch page at 300 DPI.
No text, no border, no watermark.
```

### `scene_sky.png`
```
Black and white coloring book background scene for toddlers aged 3-6: the open sky.
Show ONLY the environment: a smiling sun in the top left corner, three big simple
clouds, a rainbow arc on the right, and one bare tree branch entering from the
bottom right corner.
The ENTIRE CENTER must stay EMPTY white space - absolutely no birds, no insects,
no creatures anywhere in the picture.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture.
Pure white background, pure black lines only. 8.5x11 inch page at 300 DPI.
No text, no border, no watermark.
```

### `scene_farm.png`
```
Black and white coloring book background scene for toddlers aged 3-6: a farm.
Show ONLY the environment: a simple barn with a door and one window on the left,
a wooden fence running along the bottom, a small round pond on the right,
and two simple hills on the horizon.
The ENTIRE CENTER must stay EMPTY white space - absolutely no animals,
no people anywhere in the picture.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture.
Pure white background, pure black lines only. 8.5x11 inch page at 300 DPI.
No text, no border, no watermark.
```

### `scene_jungle.png`
```
Black and white coloring book background scene for toddlers aged 3-6: a jungle.
Show ONLY the environment: two tall palm trees at the left and right edges,
three hanging vines, a curving river across the bottom, one large rounded rock,
and a few big simple leaves in the corners.
The ENTIRE CENTER must stay EMPTY white space - absolutely no animals,
no creatures anywhere in the picture.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture.
Pure white background, pure black lines only. 8.5x11 inch page at 300 DPI.
No text, no border, no watermark.
```

### `scene_night.png`
```
Black and white coloring book background scene for toddlers aged 3-6:
a forest at night.
Show ONLY the environment: a crescent moon in the top right, six simple five-point
stars, two pine trees at the edges, one thick tree trunk with a round hollow opening
on the left, and two rounded bushes at the bottom.
The ENTIRE CENTER must stay EMPTY white space - absolutely no animals,
no owls, no creatures anywhere in the picture.
Keep the sky WHITE, not filled black - children must be able to color it.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture.
Pure white background, pure black lines only. 8.5x11 inch page at 300 DPI.
No text, no border, no watermark.
```

---

## 5. הכריכה — 3 נכסים

### `cover_hero.png` — האיור הראשי לחזית
```
Black and white line art for a children's activity book cover.
A cheerful group arrangement of six simple cartoon animals - a dolphin, a butterfly,
a cow, a lion, an owl and a turtle - arranged in a loose circle with a large EMPTY
white oval in the middle where a title will be placed.
Style: bold uniform black outlines 6-8px thick, NO shading, NO gray, NO texture,
kawaii-friendly, big eyes, simple smiles.
Pure white background, pure black lines only. Square composition at 300 DPI.
No text, no letters, no border, no watermark.
```

### `cover_scissors.png` — אייקון המספריים
```
Simple black line icon of a pair of child safety scissors, bold 8px outline,
pure black on pure white, no shading, no gray. Square, centered, 300 DPI.
No text, no background, no watermark.
```

### `bubi_mascot.png` — Bubi
קח את דף הדמות מ-`skills-backup/bubipop-video-production/references/character-sheets/bubi.jpg`
והפוך אותו לקו שחור-לבן:
```
Convert this character into black and white coloring book line art.
Bold uniform black outlines 6-8px thick, NO shading, NO gray, NO color, NO texture.
Keep the character instantly recognizable but simplify every detail.
Pure white background, pure black lines only. 300 DPI. No text, no border.
```

---

## 6. סדר עבודה מומלץ

1. **תייצר 3 איורים בלבד קודם** — `color_ocean_dolphin`, `color_farm_cow`, `color_night_owl`.
2. תריץ `build_interior.py --art ./art` ותסתכל על ה-PDF בגודל אמיתי.
3. אם הסגנון עובד — תייצר את כל השאר באותו מחולל ובאותן הגדרות בדיוק.
4. **אל תחליף מחולל באמצע.** 40 איורים בשני סגנונות שונים = ספר שנראה זול.
5. סצנות אחרונות — הן הכי קשות (המחולל תמיד רוצה למלא את המרכז).

**זמן משוער:** 51 איורים × ~2 דקות כולל פסילות וחזרות = 2–3 שעות עבודה.
