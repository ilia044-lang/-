# פרומפט להרכבת החוברת ב-ChatGPT

הדבק בשיחה שבה נמצאות כל התמונות. **חשוב:** ChatGPT חייב להשתמש בכלי הפייתון
(Code Interpreter / Advanced Data Analysis), לא במחולל התמונות. אם הכלי כבוי אצלך
הוא לא יוכל לעשות את זה בכלל.

---

```
Use your Python tool for this entire task. Do NOT use image generation.
This is a layout and measurement job, not an illustration job.

All the artwork is already in this conversation. Read every image you have.

=== WHAT WE ARE BUILDING ===
A print-ready Amazon KDP paperback: a children's colouring and cut-and-glue
activity book, 8.5 x 11 inches, 110 pages, black and white interior, full
colour cover. You will produce exactly two files for me to download:
  interior.pdf
  cover.pdf

=== NON-NEGOTIABLE KDP SPECIFICATIONS ===
These are verified against KDP's own documentation. Do not change any number,
and do not "round" anything. If a computed value disagrees with one below,
stop and tell me rather than adjusting it silently.

INTERIOR
  trim size            8.5" x 11"  (this is a KDP "large trim")
  page count           exactly 110, no more, no less
  page size in the PDF 8.625" x 11.25"
                       (bleed adds 0.125" to the OUTER edge only, and 0.125"
                        to both top and bottom - never to the gutter edge)
  inside margin        0.375" from the gutter edge
  outer/top/bottom     0.375" (this is the with-bleed figure for a 24-150 page book)
  printing             SINGLE-SIDED: artwork on recto (odd) pages, the verso
                       (even) page behind each one stays completely blank
  gutter side          MIRRORED: on odd pages the gutter is on the LEFT,
                       on even pages it is on the RIGHT
  ink                  pure black on white, 1-bit, no greys anywhere
  resolution           every placed image at 300 DPI or higher
  fonts                embedded, nothing below 7pt
  output               one flattened PDF, no transparency, under 650 MB

WHY 110 PAGES: KDP charges a flat $2.84 to print a black-and-white large-trim
book from 24 to 110 pages, then switches to per-page pricing. 110 is the most
book we can give for the lowest possible print cost. Do not exceed it.

COVER
  spine width          110 x 0.002252" = 0.2477"  (white paper)
  full wrap size       17.4977" x 11.25"
                       = (2 x 8.5) + 0.2477 + (2 x 0.125) wide, 11 + 0.25 high
  at 300 DPI           5249 x 3375 pixels
  safe margin          keep all text and important art 0.25" inside every trim edge
  barcode keep-out     leave a 2" x 1.2" area completely blank at the
                       BOTTOM-RIGHT of the BACK cover - KDP prints its barcode there
  spine text           allowed, because the book is over 79 pages

=== STEP 1: NORMALISE THE ARTWORK ===
The generator's output is roughly 1024x1536, RGB, with soft anti-aliased grey
edges. That is about 139 DPI on an 11" page, well under KDP's 300 DPI minimum.
For thick, simple line art - and only for that - upscaling then thresholding is
safe, because there is no fine detail to lose and the threshold rebuilds a crisp
edge. For each interior image:
  1. convert to greyscale
  2. upscale with LANCZOS until the image covers 2550 x 3300 pixels
  3. threshold at about 170 to pure 1-bit black and white, killing every grey
  4. pad onto a white canvas of the exact 8.5:11 aspect ratio - never crop
  5. save as PNG tagged at 300 DPI
Report the before and after size of every file.

If any source image came out LANDSCAPE rather than portrait, tell me which ones
and stop - do not stretch or crop them to fit.

=== STEP 2: BUILD THE INTERIOR, EXACTLY THIS PAGE MAP ===
  page 1        title page: "Color, Cut & Glue" / "ANIMAL HOMES"
  page 2        "This Book Belongs To ______" and "I am ____ years old"
  page 3        How To Use This Book: 1 colour it, 2 cut it out, 3 glue it where
                it lives, 4 say it out loud. Plus: "Always use safety scissors
                with a grown-up."
  page 4        Meet Your Friends: Bubi, Maya and Leo
  pages 5-84    40 COLOURING PAGES, single-sided. One animal per recto page,
                scaled to fill the safe area while keeping its aspect ratio.
                The verso behind each one is blank. Order them by habitat:
                8 ocean, 8 sky, 8 farm, 8 jungle, 8 forest-at-night.
  page 85       "Great Job! Now let's bring the animals home."
  page 86       "Time To Cut" - colour first, then cut along the dotted line.
                Grown-ups: safety scissors only.
  pages 87-98   24 CUT-OUT CARDS: 6 single-sided sheets, 4 animals per sheet in
                a 2x2 grid, each inside a dashed rounded-rectangle cut line.
                REUSE the colouring artwork scaled down - these animals already
                have clean closed outer contours, so they do not need their own
                drawings. Verso pages blank.
  pages 99-108  5 HABITAT SPREADS, two pages each:
                  verso = "Who Lives Here?" with tick boxes
                  recto = the full-page habitat scene
                Order: Ocean, Sky, Farm, Jungle, Forest at Night.
  page 109      Certificate: "I finished my Animal Homes book!" with blanks for
                Name and Date
  page 110      "More Free Pages" with a placeholder square for a QR code

After building, ASSERT the page count is exactly 110 and fail loudly if not.

=== STEP 3: COLOUR THE COVER ARTWORK ===
The cover illustration is black line art: six animals in a ring around a large
empty oval. Colour it programmatically:
  1. label every connected white region (scipy.ndimage.label)
  2. regions touching the image border are background -> make them TRANSPARENT,
     so the animals sit directly on the cover colour instead of painting a white
     rectangle over it
  3. regions under about 0.025% of the image are eye whites -> leave them white
  4. the single region over 10% of the image is the title oval -> leave it
     OPAQUE WHITE, it becomes the badge behind the title
  5. fill every remaining region from a bright children's palette
  6. CRITICAL: drop any palette colour whose WCAG contrast against the cover
     background is below 1.4:1. The obvious yellow is the same value as a sunny
     yellow background, and an animal filled with it disappears at thumbnail size.
  7. keep the line work pure black on top
Save as RGBA PNG at 300 DPI.

=== STEP 4: LAY OUT THE COVER ===
Background: a single flat colour across the FULL bleed area. Use sunny yellow
#FFD93D with deep navy #1B3A5C type.

FRONT COVER (the right-hand panel):
  - place the coloured artwork large, roughly 7.6" square, centred horizontally
  - MEASURE where the empty oval sits inside the artwork by finding the largest
    enclosed white region and taking its bounding box. Do not estimate it.
  - inside that oval, stacked and centred:
      "COLOR, CUT & GLUE"   (smaller kicker)
      "ANIMAL HOMES"        (the big one)
      "AGES 3-6"            (small)
    Auto-fit each line's font size so it stays inside the oval's width with
    padding. Never let text touch the oval's edge.
  - under the artwork: "Scissor Skills & Coloring Activity Book  ·  Ages 3-6"
  - near the bottom, three filled circles with white numerals and a label under
    each: 40 COLORING PAGES / 24 CUT-OUT ANIMALS / 5 HABITAT SCENES
  - at the very bottom: "BubiPop Kids"

SPINE: "ANIMAL HOMES · BubiPop Kids", rotated 90 degrees, centred in the
0.2477" spine, in the navy.

BACK COVER (the left-hand panel): a white rounded panel WITH A NAVY OUTLINE
(white alone cannot reach 3:1 contrast against a light background), holding:

  THREE BOOKS IN ONE
  Color it. Cut it. Give every animal a home.
  Bubi, Maya and Leo need your help! Twenty-four animals
  have lost their way home - and only you can bring them back.

  WHAT'S INSIDE
  40 BIG & SIMPLE coloring pages - thick lines for little hands
  24 cut-out animals to color, snip and keep
  5 full-page habitat scenes: Ocean, Sky, Farm, Jungle, Night
  A finish-the-book certificate with your child's name

  HOW IT WORKS
  1. Color your favourite animal.
  2. Cut it out along the dotted line (with a grown-up!).
  3. Glue it where it belongs.
  4. Say it out loud: "The owl lives in the tree!"

  WHY PARENTS LOVE IT
  SINGLE-SIDED PAGES - markers never bleed to the next picture
  Big 8.5 x 11 pages, one animal per page, no tiny details
  Builds scissor skills, pencil grip and first science words

  Ages 3-6 · Preschool & Kindergarten · Use safety scissors with adult help

Below that copy, draw three numbered circles reading COLOR -> CUT -> GLUE with
arrows between them, then leave the 2" x 1.2" barcode area blank.

TYPOGRAPHY: use a rounded, friendly display face. Try to fetch Fredoka (SIL Open
Font License, free for commercial use) and embed it. If your sandbox has no
internet, say so plainly and fall back to the heaviest sans-serif you have -
do not silently ship a font you did not check.

DO NOT type a checkmark character unless you have verified the font contains
that glyph. A missing glyph prints as an empty box. Draw ticks as two lines.

=== STEP 5: VERIFY, AND SHOW ME THE NUMBERS ===
Before giving me the files, run these checks and print a PASS/FAIL table.
If anything fails, FIX IT and re-run. Do not hand me a FAIL.

  [ ] interior.pdf has exactly 110 pages
  [ ] interior MediaBox is 8.625 x 11.25 inches (621 x 810 points)
  [ ] cover MediaBox is 17.4977 x 11.25 inches (1259.836 x 810 points)
  [ ] every placed image resolves to 300 DPI or more at its printed size
  [ ] no image contains any grey value - pure black and white only
  [ ] gutter margin is on the correct side of every single page
  [ ] every verso page behind a colouring page is truly blank
  [ ] all fonts embedded, nothing under 7pt
  [ ] cover: WCAG contrast of title-on-background >= 4.5:1
  [ ] cover: WCAG contrast of white numeral on each circle >= 4.5:1
  [ ] cover: panel outline against background >= 3:1
  [ ] barcode area is empty
  [ ] no text or important art within 0.25" of any trim edge

Then render and show me:
  - interior pages 1, 5, 87 and 100 as images
  - the full cover
  - the front cover alone at 200 pixels wide, which is the size a parent
    actually sees it at in Amazon search results
  - the front cover blurred heavily (a squint test). Tell me honestly what
    survives the blur and what disappears.

Finally, list anything you had to guess, approximate, or could not verify.
Do not tell me it is perfect. Tell me what is weak.
```

---

## מה לצפות

**יעבוד:** ChatGPT מרכיב PDF-ים עם reportlab בלי בעיה.

**יכשל, כנראה:**
- **פונטים** — אין אינטרנט בסנדבוקס, אז Fredoka לא יירד. הוא ייפול ל-Helvetica.
- **מדידת האובל** — אם הוא ינחש במקום למדוד, הכותרת תצא לא במקום.
- **300 DPI** — הוא עלול לשים את התמונות כמו שהן ולדלג על ההגדלה.

תשווה את מה שיצא לו למה שיש לנו. אם יצא לו טוב יותר במשהו — תגיד לי ואני אשפר אצלנו.
