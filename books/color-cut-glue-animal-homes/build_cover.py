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

# ---------------------------------------------------------------- design tokens
# The interior stays pure B&W - colour there would take print cost from $2.84
# to over $9. The cover prints full colour at no extra charge, so it uses it.
#
# One principle carries over from interface design and decides this cover:
# CONTRAST. A cover is chosen at ~200px wide in a search result, which is the
# print equivalent of a small viewport. check_contrast() below reports the WCAG
# ratio of every text/background pair, and any pair under 4.5:1 is rejected.

SPACE = 6                                    # base spacing unit, in points
TYPE = {                                     # one scale, no arbitrary sizes
    "hero":    60, "title": 40, "badge": 32, "h": 13,
    "body":  10.5, "cap":   11, "fine":   9, "spine": 12,
}

THEMES = {
    "sunshine": {"bg": (1.00, 0.85, 0.24), "ink": (0.106, 0.227, 0.361),
                 "badge": [(0.837, 0.223, 0.251), (0.06, 0.45, 0.45),
                           (0.42, 0.25, 0.70)]},
    "lagoon":   {"bg": (0.36, 0.83, 0.82), "ink": (0.06, 0.20, 0.30),
                 "badge": [(0.816, 0.240, 0.336), (0.665, 0.385, 0.070),
                           (0.35, 0.22, 0.62)]},
    "berry":    {"bg": (1.00, 0.72, 0.78), "ink": (0.29, 0.09, 0.28),
                 "badge": [(0.842, 0.198, 0.416), (0.10, 0.45, 0.50),
                           (0.684, 0.374, 0.072)]},
}

THEME = os.environ.get("COVER_THEME", "sunshine")
LAYOUT = os.environ.get("COVER_LAYOUT", "oval")   # "oval" | "banner"

# Where the empty title oval sits inside cover_hero.png, measured from the file
# itself (largest enclosed white region) rather than guessed.
OVAL_CX, OVAL_CY = 0.4988, 0.4486      # fraction of art width / height from top
OVAL_W, OVAL_H = 0.5813, 0.3772
_t = THEMES[THEME]
BG, INK, BADGE = _t["bg"], _t["ink"], _t["badge"]
PANEL = (1, 1, 1)


def _lum(c):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_contrast():
    """Every text/background pair in the design, against the WCAG 4.5:1 floor."""
    text = [("title on background", INK, BG),
            ("body on panel", INK, PANEL)]
    text += [(f"badge {i+1} numeral (white on fill)", (1, 1, 1), c)
             for i, c in enumerate(BADGE)]
    # a panel edge is a surface boundary, not text: WCAG puts those at 3:1, and
    # white on a light background cannot reach it, so the panel carries an ink
    # outline and the outline is what is measured
    surface = [("panel outline against background", INK, BG)]

    rows, worst = [], 99.0
    for name, fg, bg in text:
        r = contrast(fg, bg)
        worst = min(worst, r / 4.5)
        rows.append((name, r, "PASS" if r >= 4.5 else "FAIL", 4.5))
    for name, fg, bg in surface:
        r = contrast(fg, bg)
        worst = min(worst, r / 3.0)
        rows.append((name, r, "PASS" if r >= 3.0 else "FAIL", 3.0))
    return rows, worst


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
    c.setFillColorRGB(.62, .62, .62); c.setFont(BODY, 13)
    c.drawCentredString(x + w / 2, y + h / 2, f"[ {label} ]")
    c.restoreState()


def fit_text(c, text, font, max_w, start):
    """Largest size at or below `start` that keeps `text` inside `max_w`."""
    size = start
    while size > 6 and pdfmetrics.stringWidth(text, font, size) > max_w:
        size -= 0.5
    return size


def draw_front_oval(c, art):
    """Title inside the artwork's own oval. The squint test showed the banner
    layout leaving a white void at the optical centre; this fills it, and the
    animals go back to doing what a frame should do."""
    x0, y0 = FRONT_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE

    side = 7.6 * inch
    ax, ay = x0 + (w - side) / 2, y0 + 2.6 * inch
    place(c, os.path.join(art, "cover_hero.png") if art else None,
          ax, ay, side, side, "cover_hero.png")

    cx = ax + OVAL_CX * side
    cy = ay + side - OVAL_CY * side
    inner = OVAL_W * side - 0.34 * inch          # oval width less padding

    c.setFillColorRGB(*INK)
    k = fit_text(c, TITLE, DISPLAY, inner, TYPE["title"] * 0.72)
    c.setFont(DISPLAY, k)
    c.drawCentredString(cx, cy + 0.62 * inch, TITLE)

    t = fit_text(c, SUBTITLE, DISPLAY, inner, TYPE["hero"])
    c.setFont(DISPLAY, t)
    c.drawCentredString(cx, cy - 0.12 * inch, SUBTITLE)

    c.setFont(BODY, TYPE["cap"])
    c.drawCentredString(cx, cy - 0.66 * inch, "AGES 3-6")

    c.setFont(BODY, TYPE["h"])
    c.drawCentredString(x0 + w / 2, y0 + 2.12 * inch, STRAP)

    bw = w / 3
    for i, (big, small) in enumerate([("40", "COLORING PAGES"),
                                      ("24", "CUT-OUT ANIMALS"),
                                      ("5", "HABITAT SCENES")]):
        bx = x0 + bw * i + bw / 2
        c.setFillColorRGB(*BADGE[i])
        c.circle(bx, y0 + 1.22 * inch, 0.42 * inch, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1); c.setFont(DISPLAY, TYPE["badge"])
        c.drawCentredString(bx, y0 + 1.08 * inch, big)
        c.setFillColorRGB(*INK); c.setFont(DISPLAY, TYPE["cap"])
        c.drawCentredString(bx, y0 + 0.62 * inch, small)

    c.setFillColorRGB(*INK); c.setFont(DISPLAY, TYPE["h"] + 1)
    c.drawCentredString(x0 + w / 2, y0 + 0.22 * inch, AUTHOR)


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
    c.setFont(DISPLAY, TYPE["title"])
    c.drawCentredString(x0 + w / 2, y0 + h - 0.85 * inch, TITLE)
    c.setFont(DISPLAY, TYPE["hero"])
    c.drawCentredString(x0 + w / 2, y0 + h - 1.75 * inch, SUBTITLE)
    c.setFont(BODY, TYPE["h"] + 1)
    c.drawCentredString(x0 + w / 2, y0 + h - 2.2 * inch, STRAP)

    # white panel so the coloured animals never sit on the yellow
    ph = h - 4.0 * inch
    c.setFillColorRGB(*PANEL); c.setStrokeColorRGB(*INK); c.setLineWidth(2)
    c.roundRect(x0 - 0.1 * inch, y0 + 1.45 * inch,
                w + 0.2 * inch, ph + 0.1 * inch, 14, stroke=1, fill=1)
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
        c.setFillColorRGB(1, 1, 1); c.setFont(DISPLAY, TYPE["badge"])
        c.drawCentredString(cx, y0 + 0.87 * inch, big)
        c.setFillColorRGB(*INK); c.setFont(DISPLAY, TYPE["cap"])
        c.drawCentredString(cx, y0 + 0.42 * inch, small)

    c.setFillColorRGB(*INK); c.setFont(DISPLAY, 14)
    c.drawCentredString(x0 + w / 2, y0 + 0.08 * inch, AUTHOR)


def draw_spine(c):
    if PAGES <= SPINE_TEXT_MIN_PAGES:
        return
    c.saveState()
    c.translate(SPINE_X0 + SPINE / 2, BLEED + TRIM_H / 2)
    c.rotate(90)
    c.setFillColorRGB(*INK); c.setFont(DISPLAY, TYPE["spine"])
    c.drawCentredString(0, -4.2, f"{SUBTITLE}   ·   {AUTHOR}")
    c.restoreState()


def draw_back(c, art):
    x0, y0 = BACK_X0 + SAFE, BLEED + SAFE
    w, h = TRIM_W - 2 * SAFE, TRIM_H - 2 * SAFE

    # white panel keeps the body copy readable over the yellow
    c.setFillColorRGB(*PANEL); c.setStrokeColorRGB(*INK); c.setLineWidth(2)
    c.roundRect(x0 - 0.12 * inch, y0 + BARCODE_H + 0.12 * inch,
                w + 0.24 * inch, h - BARCODE_H + 0.05 * inch, 14,
                stroke=1, fill=1)

    y = y0 + h - 0.45 * inch
    c.setFillColorRGB(*INK)
    for kind, text in BACK_BLURB:
        if kind == "gap":
            y -= 0.16 * inch
            continue
        if kind == "h":
            y -= 0.06 * inch
            c.setFillColorRGB(*INK); c.setFont(DISPLAY, TYPE["h"])
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
            c.setFont(BODY, TYPE["body"])
            c.drawString(x0 + 15, y, text)
            y -= 0.215 * inch
        else:
            c.setFont(BODY, TYPE["body"])
            c.drawString(x0, y, text)
            y -= 0.215 * inch

    # the dead zone between the blurb and the barcode earns its keep here
    draw_steps(c, x0, y0 + h * 0.30, w)

    c.setFillColorRGB(*INK)
    c.setFont(BODY, TYPE["fine"])
    c.drawString(x0, y0 + BARCODE_H + 0.35 * inch,
                 "Ages 3-6  ·  Preschool & Kindergarten  ·  "
                 "Use safety scissors with adult help")

    # barcode keep-out: KDP prints its own barcode here, so it must stay blank
    bx = BACK_X0 + TRIM_W - SAFE - BARCODE_W
    by = BLEED + SAFE
    c.saveState()
    c.setDash(3, 3); c.setStrokeColorRGB(.8, .8, .8)
    c.rect(bx, by, BARCODE_W, BARCODE_H)
    c.setFillColorRGB(.72, .72, .72); c.setFont(BODY, 8)
    c.drawCentredString(bx + BARCODE_W / 2, by + BARCODE_H / 2,
                        "KDP barcode - keep clear")
    c.restoreState()


def build(out, art):
    c = canvas.Canvas(out, pagesize=(WRAP_W, WRAP_H),
                      initialFontName=BODY, initialFontSize=10)
    c.setTitle(f"{TITLE}: {SUBTITLE} - cover")
    c.setFillColorRGB(*BG)                      # covers the full bleed area
    c.rect(0, 0, WRAP_W, WRAP_H, stroke=0, fill=1)
    draw_back(c, art)
    draw_spine(c)
    (draw_front_oval if LAYOUT == "oval" else draw_front)(c, art)
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
    print(f"  theme        : {THEME}   layout: {LAYOUT}")
    rows, worst = check_contrast()
    for name, ratio, verdict, floor in rows:
        print(f"    {verdict}  {ratio:5.2f}:1  (floor {floor})  {name}")
    if worst < 1.0:
        raise SystemExit("FAIL: a contrast pair is below its WCAG floor")
