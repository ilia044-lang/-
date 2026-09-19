#!/usr/bin/env python3
"""
Build the KDP-ready full-wrap paperback cover for "Color, Cut & Glue: Animal Homes".

Geometry (US KDP, verified 2026-09), all derived from PAGES so it stays correct
if the page count ever moves:
  trim          8.5" x 11"
  spine         PAGES x 0.002252"  (white paper)  -> 110pp = 0.2477"
  full wrap     (2 x 8.5) + spine + (2 x 0.125" bleed)  x  (11 + 0.25")
  safe margin   0.25" in from every trim edge
  barcode zone  2" x 1.2" kept clear at the bottom-right of the back cover

Art is optional: missing files render as labelled placeholders so the layout can
be proofed before any illustration exists.

    python3 build_cover.py --art ./art --out cover.pdf
    python3 build_cover.py --out cover_proof.pdf
"""
import argparse, os
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def load_fonts():
    """Fredoka (SIL OFL, commercial use permitted) - a rounded display face
    that reads as a children's book. Falls back to Helvetica if absent."""
    try:
        pdfmetrics.registerFont(TTFont("Display", os.path.join(FONT_DIR, "Fredoka-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("Body", os.path.join(FONT_DIR, "Fredoka-SemiBold.ttf")))
        return "Display", "Body"
    except Exception:
        return "Helvetica-Bold", "Helvetica"


DISPLAY, BODY = load_fonts()

PAGES = 110
TRIM_W, TRIM_H = 8.5 * inch, 11.0 * inch
BLEED = 0.125 * inch
SAFE = 0.25 * inch
SPINE = PAGES * 0.002252 * inch          # white paper
SPINE_TEXT_MIN_PAGES = 79                # KDP prints spine text only above this

WRAP_W = 2 * TRIM_W + SPINE + 2 * BLEED
WRAP_H = TRIM_H + 2 * BLEED

BACK_X0 = BLEED                          # back cover spans left of the spine
SPINE_X0 = BLEED + TRIM_W
FRONT_X0 = SPINE_X0 + SPINE

BARCODE_W, BARCODE_H = 2.0 * inch, 1.2 * inch

# cover palette. The interior stays pure B&W - the cover is full colour at no
# extra print cost, so it uses it. Yellow + navy survives CMYK and stays
# readable at 200px thumbnail width.
BG        = (1.00, 0.85, 0.24)   # sunny yellow
INK       = (0.106, 0.227, 0.361)  # deep navy
PANEL     = (1, 1, 1)
BADGE     = [(1.00, 0.42, 0.42), (0.31, 0.80, 0.77), (0.65, 0.55, 0.98)]

TITLE = "COLOR, CUT & GLUE"
SUBTITLE = "ANIMAL HOMES"
STRAP = "Scissor Skills & Coloring Activity Book  ·  Ages 3-6"
AUTHOR = "BubiPop Kids"

BACK_BLURB = [
    ("h", "THREE BOOKS IN ONE"),
    ("p", "Color it. Cut it. Give every animal a home."),
    ("p", "Bubi, Maya and Leo need your help! Twenty-four animals"),
    ("p", "have lost their way home - and only you can bring them back."),
    ("gap", ""),
    ("h", "WHAT'S INSIDE"),
    ("b", "40 BIG & SIMPLE coloring pages - thick lines for little hands"),
    ("b", "24 cut-out animals to color, snip and keep"),
    ("b", "5 full-page habitat scenes: Ocean, Sky, Farm, Jungle, Night"),
    ("b", "A finish-the-book certificate with your child's name"),
    ("gap", ""),
    ("h", "HOW IT WORKS"),
    ("n", "1.  Color your favourite animal."),
    ("n", "2.  Cut it out along the dotted line (with a grown-up!)."),
    ("n", "3.  Glue it where it belongs."),
    ("n", '4.  Say it out loud: "The owl lives in the tree!"'),
    ("gap", ""),
    ("h", "WHY PARENTS LOVE IT"),
    ("b", "SINGLE-SIDED PAGES - markers never bleed to the next picture"),
    ("b", "Big 8.5 x 11 pages, one animal per page, no tiny details"),
    ("b", "Builds scissor skills, pencil grip and first science words"),
]


def place(c, path, x, y, w, h, label):
    """Draw art fitted into a box, or a labelled placeholder if it is missing."""
    if path and os.path.exists(path):
        img = ImageReader(path)
        iw, ih = img.getSize()
        s = min(w / iw, h / ih)
        c.drawImage(img, x + (w - iw * s) / 2, y + (h - ih * s) / 2,
                    iw * s, ih * s, mask="auto")
        return
    c.saveState()
    c.setDash(4, 4); c.setStrokeColorRGB(.78, .78, .78)
    c.rect(x, y, w, h)
    c.setFillColorRGB(.62, .62, .62); c.setFont("Helvetica", 13)
    c.drawCentredString(x + w / 2, y + h / 2, f"[ {label} ]")
    c.restoreState()


def draw_steps(c, x0, y, w, r=0.34 * inch, label_size=12, num_size=22):
    """Three numbered circles: COLOR -> CUT -> GLUE. Pure vector, needs no art."""
    slot = w / 3
    for i, word in enumerate(["COLOR", "CUT", "GLUE"]):
        cx = x0 + slot * i + slot / 2
        c.setFillColorRGB(*BADGE[i])
        c.circle(cx, y, r, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont(DISPLAY, num_size)
        c.drawCentredString(cx, y - num_size * 0.36, str(i + 1))
        c.setFillColorRGB(*INK); c.setFont(DISPLAY, label_size)
        c.drawCentredString(cx, y - r - 0.24 * inch, word)
        if i < 2:                                   # arrow to the next step
            ax, k = cx + slot / 2, r * 0.26
            c.setStrokeColorRGB(*INK); c.setLineWidth(1.6)
            c.line(ax - k * 2, y, ax + k * 2, y)
            c.line(ax + k * 2, y, ax + k * 0.7, y + k * 1.1)
            c.line(ax + k * 2, y, ax + k * 0.7, y - k * 1.1)
    c.setLineWidth(1)


def draw_front(c, art):
    x0, y0 = FRONT_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE

    c.setFillColorRGB(*INK)
    c.setFont(DISPLAY, 40)
    c.drawCentredString(x0 + w / 2, y0 + h - 0.85 * inch, TITLE)
    c.setFont(DISPLAY, 60)
    c.drawCentredString(x0 + w / 2, y0 + h - 1.75 * inch, SUBTITLE)
    c.setFont(BODY, 14)
    c.drawCentredString(x0 + w / 2, y0 + h - 2.2 * inch, STRAP)

    # white panel so the coloured animals never sit on the yellow
    ph = h - 4.0 * inch
    c.setFillColorRGB(*PANEL)
    c.roundRect(x0 - 0.1 * inch, y0 + 1.45 * inch,
                w + 0.2 * inch, ph + 0.1 * inch, 14, stroke=0, fill=1)
    place(c, os.path.join(art, "cover_hero.png") if art else None,
          x0, y0 + 1.5 * inch, w, ph, "cover_hero.png")

    # the hero art leaves a large empty oval at its centre - fill it with the
    # book's actual mechanism rather than leaving a white hole
    draw_steps(c, x0 + w * 0.22, y0 + 1.5 * inch + ph / 2 + 0.12 * inch,
               w * 0.56, r=0.26 * inch, label_size=9, num_size=16)

    # three coloured badges - what the eye catches in a search result
    bw = w / 3
    for i, (big, small) in enumerate([("40", "COLORING PAGES"),
                                      ("24", "CUT-OUT ANIMALS"),
                                      ("5", "HABITAT SCENES")]):
        cx = x0 + bw * i + bw / 2
        c.setFillColorRGB(*BADGE[i])
        c.circle(cx, y0 + 1.00 * inch, 0.40 * inch, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont(DISPLAY, 32)
        c.drawCentredString(cx, y0 + 0.87 * inch, big)
        c.setFillColorRGB(*INK); c.setFont(DISPLAY, 11)
        c.drawCentredString(cx, y0 + 0.42 * inch, small)

    c.setFillColorRGB(*INK); c.setFont(DISPLAY, 14)
    c.drawCentredString(x0 + w / 2, y0 + 0.08 * inch, AUTHOR)


def draw_spine(c):
    if PAGES <= SPINE_TEXT_MIN_PAGES:
        return
    c.saveState()
    c.translate(SPINE_X0 + SPINE / 2, BLEED + TRIM_H / 2)
    c.rotate(90)
    c.setFillColorRGB(*INK); c.setFont(DISPLAY, 12)
    c.drawCentredString(0, -4.2, f"{SUBTITLE}   ·   {AUTHOR}")
    c.restoreState()


def draw_back(c, art):
    x0, y0 = BACK_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE

    # white panel keeps the body copy readable over the yellow
    c.setFillColorRGB(*PANEL)
    c.roundRect(x0 - 0.12 * inch, y0 + BARCODE_H + 0.12 * inch,
                w + 0.24 * inch, h - BARCODE_H + 0.05 * inch, 14,
                stroke=0, fill=1)

    y = y0 + h - 0.45 * inch
    c.setFillColorRGB(*INK)
    for kind, text in BACK_BLURB:
        if kind == "gap":
            y -= 0.16 * inch
            continue
        if kind == "h":
            y -= 0.06 * inch
            c.setFillColorRGB(*INK); c.setFont(DISPLAY, 13)
            c.drawString(x0, y, text)
            y -= 0.26 * inch
        elif kind == "b":
            # drawn, not typed: Fredoka carries no U+2713 and a missing glyph
            # prints as an empty box
            c.saveState()
            c.setLineWidth(2.0); c.setLineCap(1)
            c.setStrokeColorRGB(0.42, 0.72, 0.36)
            c.line(x0 + 1, y + 2.5, x0 + 4, y - 0.5)
            c.line(x0 + 4, y - 0.5, x0 + 9, y + 6.5)
            c.restoreState()
            c.setFont(BODY, 10.5)
            c.drawString(x0 + 15, y, text)
            y -= 0.215 * inch
        else:
            c.setFont(BODY, 10.5)
            c.drawString(x0, y, text)
            y -= 0.215 * inch

    # the dead zone between the blurb and the barcode earns its keep here
    draw_steps(c, x0, y0 + h * 0.30, w)

    c.setFillColorRGB(*INK)
    c.setFont(BODY, 9)
    c.drawString(x0, y0 + BARCODE_H + 0.35 * inch,
                 "Ages 3-6  ·  Preschool & Kindergarten  ·  "
                 "Use safety scissors with adult help")

    # barcode keep-out: KDP prints its own barcode here, so it must stay blank
    bx = BACK_X0 + TRIM_W - SAFE - BARCODE_W
    by = BLEED + SAFE
    c.saveState()
    c.setDash(3, 3); c.setStrokeColorRGB(.8, .8, .8)
    c.rect(bx, by, BARCODE_W, BARCODE_H)
    c.setFillColorRGB(.72, .72, .72); c.setFont("Helvetica", 8)
    c.drawCentredString(bx + BARCODE_W / 2, by + BARCODE_H / 2,
                        "KDP barcode - keep clear")
    c.restoreState()


def build(out, art):
    c = canvas.Canvas(out, pagesize=(WRAP_W, WRAP_H))
    c.setTitle(f"{TITLE}: {SUBTITLE} - cover")
    c.setFillColorRGB(*BG)                      # covers the full bleed area
    c.rect(0, 0, WRAP_W, WRAP_H, stroke=0, fill=1)
    draw_back(c, art)
    draw_spine(c)
    draw_front(c, art)
    c.showPage()
    c.save()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default=None)
    ap.add_argument("--out", default="cover.pdf")
    a = ap.parse_args()
    build(a.out, a.art)
    print(f"{a.out}")
    print(f"  pages        : {PAGES}")
    print(f"  spine        : {SPINE/inch:.4f}\"  "
          f"({'spine text printed' if PAGES > SPINE_TEXT_MIN_PAGES else 'no spine text'})")
    print(f"  full wrap    : {WRAP_W/inch:.4f}\" x {WRAP_H/inch:.4f}\"")
    print(f"  at 300 DPI   : {round(WRAP_W/inch*300)} x {round(WRAP_H/inch*300)} px")
    print(f"  barcode zone : {BARCODE_W/inch:g}\" x {BARCODE_H/inch:g}\" "
          f"clear at back-cover bottom-right")
