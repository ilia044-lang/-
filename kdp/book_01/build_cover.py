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


def draw_front(c, art):
    x0, y0 = FRONT_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(x0 + w / 2, y0 + h - 0.85 * inch, TITLE)
    c.setFont("Helvetica-Bold", 62)
    c.drawCentredString(x0 + w / 2, y0 + h - 1.75 * inch, SUBTITLE)

    c.setFont("Helvetica", 14)
    c.drawCentredString(x0 + w / 2, y0 + h - 2.2 * inch, STRAP)

    place(c, os.path.join(art, "cover_hero.png") if art else None,
          x0, y0 + 1.5 * inch, w, h - 4.0 * inch, "cover_hero.png")

    # the three-promise badge row - this is what sells at thumbnail size
    bw = w / 3
    for i, (big, small) in enumerate([("40", "COLORING\nPAGES"),
                                      ("24", "CUT-OUT\nANIMALS"),
                                      ("5", "HABITAT\nSCENES")]):
        cx = x0 + bw * i + bw / 2
        c.setFont("Helvetica-Bold", 40)
        c.drawCentredString(cx, y0 + 0.95 * inch, big)
        c.setFont("Helvetica-Bold", 11)
        for j, line in enumerate(small.split("\n")):
            c.drawCentredString(cx, y0 + 0.62 * inch - j * 13, line)

    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(x0 + w / 2, y0 + 0.1 * inch, AUTHOR)


def draw_spine(c):
    if PAGES <= SPINE_TEXT_MIN_PAGES:
        return
    c.saveState()
    c.translate(SPINE_X0 + SPINE / 2, BLEED + TRIM_H / 2)
    c.rotate(90)
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(0, -4.2, f"{SUBTITLE}   ·   {AUTHOR}")
    c.restoreState()


def draw_steps(c, x0, y, w):
    """Three numbered circles: COLOR -> CUT -> GLUE. Pure vector, needs no art."""
    r = 0.34 * inch
    slot = w / 3
    for i, word in enumerate(["COLOR", "CUT", "GLUE"]):
        cx = x0 + slot * i + slot / 2
        c.setLineWidth(2.2); c.setStrokeColorRGB(0, 0, 0)
        c.circle(cx, y, r, stroke=1, fill=0)
        c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(cx, y - 8, str(i + 1))
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx, y - r - 0.24 * inch, word)
        if i < 2:                                   # arrow to the next step
            ax = cx + slot / 2
            c.setLineWidth(1.6)
            c.line(ax - 9, y, ax + 9, y)
            c.line(ax + 9, y, ax + 3, y + 5)
            c.line(ax + 9, y, ax + 3, y - 5)
    c.setLineWidth(1)


def draw_back(c, art):
    x0, y0 = BACK_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE
    y = y0 + h - 0.45 * inch

    c.setFillColorRGB(0, 0, 0)
    for kind, text in BACK_BLURB:
        if kind == "gap":
            y -= 0.16 * inch
            continue
        if kind == "h":
            y -= 0.06 * inch
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x0, y, text)
            y -= 0.26 * inch
        elif kind == "b":
            c.setFont("Helvetica", 10.5)
            c.drawString(x0, y, "✓   " + text)
            y -= 0.215 * inch
        else:
            c.setFont("Helvetica", 10.5)
            c.drawString(x0, y, text)
            y -= 0.215 * inch

    # the dead zone between the blurb and the barcode earns its keep here
    draw_steps(c, x0, y0 + h * 0.30, w)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Oblique", 9)
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
