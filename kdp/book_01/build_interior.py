#!/usr/bin/env python3
"""
Build a KDP-ready interior PDF for the "Color, Cut & Glue" series.

Spec enforced here (US KDP, verified 2026-09):
  trim        8.5" x 11"  (large trim)
  bleed       page size 8.625" x 11.25"  (+0.125" outer edge, +0.125" top & bottom)
  margins     gutter 0.375", outer/top/bottom 0.375" (bleed present, 24-150 pages)
  pages       110, single-sided (art on recto, blank verso)
  ink         black & white, 300 DPI art

Art is supplied as PNG/JPG files named by the manifest below. Missing art is
rendered as a labelled placeholder so the page count and layout can be proofed
before a single image exists.

    python3 build_interior.py --art ./art --out interior.pdf
    python3 build_interior.py --out proof.pdf          # all placeholders
"""
import argparse, os
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

TRIM_W, TRIM_H = 8.5 * inch, 11.0 * inch
BLEED = 0.125 * inch
PAGE_W, PAGE_H = TRIM_W + BLEED, TRIM_H + 2 * BLEED   # 8.625 x 11.25
GUTTER, OUTER = 0.375 * inch, 0.375 * inch
TOTAL_PAGES = 110

HABITATS = {
    "ocean":  ["dolphin", "turtle", "fish", "crab", "octopus", "starfish", "whale", "seahorse"],
    "sky":    ["butterfly", "bee", "bird", "ladybug", "dragonfly", "parrot", "eagle", "hummingbird"],
    "farm":   ["cow", "pig", "sheep", "horse", "duck", "chicken", "goat", "rabbit"],
    "jungle": ["lion", "elephant", "monkey", "giraffe", "zebra", "tiger", "snake", "crocodile"],
    "night":  ["owl", "fox", "hedgehog", "deer", "bat", "raccoon", "bear", "wolf"],
}
CUTOUTS = {              # 6 sheets x 4 animals = 24 cut-out cards
    "ocean": ["dolphin", "turtle", "fish", "crab"],
    "sky":   ["butterfly", "bee", "bird", "ladybug"],
    "farm":  ["cow", "pig", "sheep", "horse"],
    "jungle":["lion", "elephant", "monkey", "giraffe"],
    "night": ["owl", "fox", "hedgehog", "deer"],
    "mixed": ["octopus", "duck", "zebra", "bat"],
}
SCENES = [("ocean", "Under the Sea"), ("sky", "Up in the Sky"), ("farm", "On the Farm"),
          ("jungle", "In the Jungle"), ("night", "Forest at Night")]

# Every colouring page is captioned. Competitors that sell (SOCOLER's
# paint-with-water books label every page) do this because the caption turns a
# picture into a first-reading-word, and because an uncaptioned drawing floating
# on white reads as unfinished. The habitat line also keeps reminding the child
# where the animal is going to be glued.
HABITAT_LABEL = {
    "ocean":  "lives in the OCEAN",
    "sky":    "lives in the SKY",
    "farm":   "lives on the FARM",
    "jungle": "lives in the JUNGLE",
    "night":  "lives in the FOREST",
}


FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def load_fonts():
    """Same rounded face as the cover, so the book reads as one object."""
    try:
        pdfmetrics.registerFont(TTFont("IDisplay", os.path.join(FONT_DIR, "Fredoka-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("IBody", os.path.join(FONT_DIR, "Fredoka-SemiBold.ttf")))
        return "IDisplay", "IBody"
    except Exception:
        return "Helvetica-Bold", "Helvetica"


DISPLAY, BODY = load_fonts()


def safe_box(page_no):
    """Printable safe area (x, y, w, h) for a page, accounting for gutter side."""
    recto = page_no % 2 == 1                      # odd pages are right-hand
    x = GUTTER if recto else BLEED + OUTER
    w = PAGE_W - GUTTER - OUTER - BLEED
    return x, BLEED + OUTER, w, PAGE_H - 2 * (BLEED + OUTER)


def draw_art(c, path, box, label):
    x, y, w, h = box
    if path and os.path.exists(path):
        img = ImageReader(path)
        iw, ih = img.getSize()
        s = min(w / iw, h / ih)
        c.drawImage(img, x + (w - iw * s) / 2, y + (h - ih * s) / 2,
                    iw * s, ih * s, mask="auto")
    else:
        c.setDash(4, 4); c.setStrokeColorRGB(.75, .75, .75)
        c.rect(x, y, w, h); c.setDash()
        c.setFillColorRGB(.6, .6, .6); c.setFont("Helvetica", 22)
        c.drawCentredString(x + w / 2, y + h / 2, f"[ {label} ]")
        c.setFont("Helvetica", 10)
        c.drawCentredString(x + w / 2, y + h / 2 - 26, "art placeholder")
        c.setFillColorRGB(0, 0, 0)


def text_page(c, page_no, title, lines, title_size=46, gap=0.56, top=None):
    """A text page whose block sits in the upper-middle of the page, not jammed
    against the top. An 8.5x11 page with copy in the top quarter reads as a
    mistake; this centres the block in the space it actually has."""
    x, y, w, h = safe_box(page_no)
    cx = x + w / 2

    body = sum(gap for ln in lines if ln) + sum(gap * 0.5 for ln in lines if not ln)
    block = 0.9 + body                              # title + rule + copy, inches
    ty = y + h - (top if top is not None else max(1.1, (h / inch - block) / 2.6)) * inch

    c.setFont(DISPLAY, title_size)
    c.drawCentredString(cx, ty, title)
    ty -= 0.34 * inch

    c.setLineWidth(3); c.setLineCap(1)
    c.line(cx - 0.9 * inch, ty, cx + 0.9 * inch, ty)
    c.setLineWidth(1)
    ty -= 0.52 * inch

    for ln in lines:
        if ln == "":
            ty -= gap * 0.5 * inch
            continue
        c.setFont(BODY, 20)
        c.drawCentredString(cx, ty, ln)
        ty -= gap * inch
    return ty


def folio(c, page_no):
    """Small page number at the outer bottom corner - cheap, and its absence is
    one of the things that makes a self-published interior look self-published."""
    x, y, w, _ = safe_box(page_no)
    c.setFont(BODY, 10)
    c.setFillGray(0.35)
    c.drawCentredString(x + (w - 0.25 * inch if page_no % 2 else 0.25 * inch),
                        y - 0.22 * inch, str(page_no))
    c.setFillGray(0)


def tool_icons(c, cx, y, size):
    """Crayon, safety scissors and glue stick, drawn as vectors - no art needed."""
    s = size
    slots = [cx - 1.9 * s, cx, cx + 1.9 * s]
    c.setLineWidth(3); c.setLineJoin(1)

    # crayon
    a = slots[0]
    c.rect(a - 0.28 * s, y - 0.9 * s, 0.56 * s, 1.5 * s)
    c.line(a - 0.28 * s, y + 0.6 * s, a, y + 1.1 * s)
    c.line(a, y + 1.1 * s, a + 0.28 * s, y + 0.6 * s)
    c.line(a - 0.28 * s, y + 0.15 * s, a + 0.28 * s, y + 0.15 * s)

    # safety scissors
    b = slots[1]
    c.circle(b - 0.3 * s, y - 0.72 * s, 0.26 * s)
    c.circle(b + 0.3 * s, y - 0.72 * s, 0.26 * s)
    c.line(b - 0.3 * s, y - 0.46 * s, b + 0.24 * s, y + 1.05 * s)
    c.line(b + 0.3 * s, y - 0.46 * s, b - 0.24 * s, y + 1.05 * s)

    # glue stick
    d = slots[2]
    c.rect(d - 0.3 * s, y - 0.9 * s, 0.6 * s, 1.25 * s)
    c.rect(d - 0.22 * s, y + 0.35 * s, 0.44 * s, 0.6 * s)
    c.setLineWidth(1)

    c.setFont(DISPLAY, 15)
    for a, lbl in zip(slots, ["CRAYONS", "SAFETY\nSCISSORS", "GLUE STICK"]):
        for i, line in enumerate(lbl.split("\n")):
            c.drawCentredString(a, y - 1.25 * s - i * 15, line)


def write_line(c, cx, y, width, label=None):
    """A ruled blank for a child to write on, with an optional label above."""
    if label:
        c.setFont(BODY, 12)
        c.drawCentredString(cx, y + 0.24 * inch, label)
    c.setLineWidth(2)
    c.line(cx - width / 2, y, cx + width / 2, y)
    c.setLineWidth(1)


def build(out, art_dir):
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Color, Cut & Glue: Animal Homes")
    A = lambda n: os.path.join(art_dir, n) if art_dir else None
    page = 0

    def newpage():
        nonlocal page
        page += 1
        return page

    def blank():
        c.showPage()
        newpage()

    # --- front matter, pages 1-4
    n = newpage()
    bx, by, bw, bh = safe_box(n)
    cx = bx + bw / 2
    c.setLineWidth(4)
    c.roundRect(bx + 0.2 * inch, by + 0.4 * inch,
                bw - 0.4 * inch, bh - 0.8 * inch, 18)
    c.setLineWidth(1)
    c.setFont(DISPLAY, 34)
    c.drawCentredString(cx, by + bh - 2.6 * inch, "Color, Cut & Glue")
    c.setFont(DISPLAY, 58)
    c.drawCentredString(cx, by + bh - 3.8 * inch, "ANIMAL HOMES")
    c.setLineWidth(3); c.setLineCap(1)
    c.line(cx - 1.6 * inch, by + bh - 4.3 * inch, cx + 1.6 * inch, by + bh - 4.3 * inch)
    c.setLineWidth(1)
    c.setFont(BODY, 17)
    for i, ln in enumerate(["40 coloring pages", "24 cut-out animals",
                            "5 habitat scenes"]):
        c.drawCentredString(cx, by + bh - (5.1 + i * 0.5) * inch, ln)
    c.setFont(BODY, 16)
    c.drawCentredString(cx, by + 1.9 * inch, "with Bubi, Maya & Leo")
    c.setFont(DISPLAY, 20)
    c.drawCentredString(cx, by + 1.3 * inch, "BubiPop Kids")
    c.showPage()
    n = newpage()
    ty = text_page(c, n, "This Book Belongs To", [], top=1.1)
    bx, by, bw, bh = safe_box(n)
    cx = bx + bw / 2
    write_line(c, cx, ty - 0.5 * inch, 4.8 * inch, "MY NAME")
    write_line(c, cx, ty - 2.1 * inch, 2.6 * inch, "I AM THIS MANY")
    c.setFont(BODY, 18)
    c.drawCentredString(cx, ty - 3.4 * inch, "Draw a picture of yourself here!")
    c.setDash(5, 5); c.setLineWidth(2)
    c.roundRect(cx - 2.2 * inch, ty - 6.9 * inch, 4.4 * inch, 3.3 * inch, 12)
    c.setDash(); c.setLineWidth(1)
    c.showPage()
    text_page(c, newpage(), "How To Use This Book", [
        "1.  Color the animal.",
        "2.  Cut it out along the dotted line.",
        "3.  Glue it where it lives.",
        "4.  Say it out loud!",
        "", "Always use safety scissors with a grown-up."])
    c.showPage()
    n = newpage()
    text_page(c, n, "What You Will Need", [], top=1.3)
    bx, by, bw, bh = safe_box(n)
    tool_icons(c, bx + bw / 2, by + bh - 4.3 * inch, 0.62 * inch)
    c.setFont(BODY, 19)
    c.drawCentredString(bx + bw / 2, by + bh - 6.4 * inch,
                        "Bubi, Maya and Leo are waiting inside.")
    c.drawCentredString(bx + bw / 2, by + bh - 6.9 * inch,
                        "Let's bring every animal home!")
    c.showPage()

    # --- 40 coloring pages, single-sided: art on recto, blank verso (pages 5-84)
    for hab, animals in HABITATS.items():
        for a in animals:
            n = newpage()
            x, y, w, h = safe_box(n)
            caption = 1.45 * inch                    # room reserved under the art
            draw_art(c, A(f"color_{hab}_{a}.png"),
                     (x, y + caption, w, h - caption), f"{a.upper()}")

            cx = x + w / 2
            c.setFont(DISPLAY, 58)
            c.drawCentredString(cx, y + 0.62 * inch, a.upper())
            c.setFont(BODY, 17)
            c.drawCentredString(cx, y + 0.24 * inch, HABITAT_LABEL[hab])
            folio(c, n)
            c.showPage()
            blank()                                  # blank back - no bleed-through

    # --- transition, pages 85-86
    n = newpage()
    ty = text_page(c, n, "Great Job!",
                   ["You colored them all.", "Now let's bring them home."], top=1.4)
    bx, by, bw, bh = safe_box(n)
    cx = bx + bw / 2
    r = 0.6 * inch
    for i, word in enumerate(["COLOR", "CUT", "GLUE"]):
        sy = ty - (1.6 + i * 2.0) * inch
        c.setLineWidth(4)
        c.circle(cx - 1.4 * inch, sy, r)
        c.setLineWidth(1)
        c.setFont(DISPLAY, 34)
        c.drawCentredString(cx - 1.4 * inch, sy - 0.16 * inch, str(i + 1))
        c.setFont(DISPLAY, 30)
        c.drawString(cx - 0.4 * inch, sy - 0.12 * inch, word)
    c.showPage()
    text_page(c, newpage(), "Time To Cut", [
        "Color each animal first.",
        "Then cut along the dotted line.",
        "Keep them in a safe place!",
        "", "Grown-ups: safety scissors only."])
    c.showPage()

    # --- 24 cut-out cards, 4 per sheet, single-sided (pages 87-98)
    for hab, animals in CUTOUTS.items():
        n = newpage()
        x, y, w, h = safe_box(n)
        for i, a in enumerate(animals):
            cx, cy = x + (i % 2) * w / 2, y + (1 - i // 2) * h / 2
            c.setDash(3, 3); c.setStrokeColorRGB(.4, .4, .4)
            c.roundRect(cx + 6, cy + 6, w / 2 - 12, h / 2 - 12, 10)
            c.setDash(); c.setStrokeColorRGB(0, 0, 0)
            # a dedicated cut-out drawing if one exists, otherwise reuse the
            # full-page artwork - these animals already have clean closed
            # outer contours, so scaling one down cuts just as well and
            # saves generating 24 near-duplicate images
            cut = A(f"cut_{hab}_{a}.png")
            if not (cut and os.path.exists(cut)):
                cut = next((p for p in (A(f"color_{h2}_{a}.png")
                                        for h2 in HABITATS)
                            if p and os.path.exists(p)), cut)
            draw_art(c, cut,
                     (cx + 22, cy + 40, w / 2 - 44, h / 2 - 62), a.upper())
            c.setFont(DISPLAY, 19)
            c.drawCentredString(cx + w / 4, cy + 20, a.upper())
        c.showPage()
        blank()

    # --- 5 habitat spreads, 2 pages each (pages 99-108)
    for hab, title in SCENES:
        n = newpage()                                 # verso: the checklist
        text_page(c, n, "Who Lives Here?",
                  [f"Glue the animals that belong in {title.lower()}.",
                   "Tick each box when it is home."], top=1.2)
        bx, by, bw, bh = safe_box(n)
        # the checklist the old version only described
        box = 0.32 * inch
        ly = by + bh - 3.6 * inch
        for a in HABITATS[hab]:
            c.setLineWidth(2.5)
            c.rect(bx + 1.5 * inch, ly - box * 0.2, box, box)
            c.setLineWidth(1)
            c.setFont(DISPLAY, 22)
            c.drawString(bx + 1.5 * inch + box + 0.28 * inch, ly, a.upper())
            ly -= 0.62 * inch
        c.showPage()
        n = newpage()                                 # recto: the scene
        draw_art(c, A(f"scene_{hab}.png"), safe_box(n), title.upper())
        folio(c, n)
        c.showPage()

    # --- back matter, pages 109-110
    n = newpage()
    text_page(c, n, "You Did It!", ["I finished my", "Animal Homes book!"])
    bx, by, bw, bh = safe_box(n)
    cx = bx + bw / 2
    # a certificate border makes the page feel like a reward, not a form
    c.setLineWidth(3)
    c.roundRect(bx + 0.3 * inch, by + 0.6 * inch,
                bw - 0.6 * inch, bh - 1.35 * inch, 16)
    c.setLineWidth(1)
    write_line(c, cx, by + bh - 5.6 * inch, 4.6 * inch, "NAME")
    write_line(c, cx, by + bh - 7.0 * inch, 4.6 * inch, "DATE")
    c.setFont(DISPLAY, 16)
    c.drawCentredString(cx, by + 1.9 * inch, "Bubi, Maya & Leo")
    c.setFont(BODY, 12)
    c.drawCentredString(cx, by + 1.55 * inch, "are proud of you!")
    c.showPage()
    n = newpage()
    ty = text_page(c, n, "More Free Pages",
                   ["Grown-ups: scan the code for free bonus",
                    "coloring pages to print at home."], top=1.2)
    bx, by, bw, bh = safe_box(n)
    cx = bx + bw / 2
    box = 2.4 * inch
    c.setDash(6, 6); c.setLineWidth(2)
    c.rect(cx - box / 2, ty - 0.5 * inch - box, box, box)
    c.setDash(); c.setLineWidth(1)
    c.setFont(BODY, 12)
    c.drawCentredString(cx, ty - 0.5 * inch - box / 2, "[ QR CODE ]")
    ty = ty - 1.2 * inch - box
    c.setFont(BODY, 15)
    c.drawCentredString(cx, ty, "More books in this series:")
    c.setFont(DISPLAY, 16)
    for i, t in enumerate(["Things That Go", "My Body & Me",
                           "Food & The Farm", "Seasons"]):
        c.drawCentredString(cx, ty - (0.55 + i * 0.5) * inch,
                            f"Color, Cut & Glue: {t}")
    c.showPage()

    c.save()
    return page


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default=None, help="folder with 300 DPI art")
    ap.add_argument("--out", default="interior.pdf")
    a = ap.parse_args()
    n = build(a.out, a.art)
    print(f"{a.out}: {n} pages, {PAGE_W/inch:.3f}\" x {PAGE_H/inch:.3f}\" "
          f"(trim {TRIM_W/inch:g}x{TRIM_H/inch:g} + bleed)")
    if n != TOTAL_PAGES:
        raise SystemExit(f"FAIL: expected {TOTAL_PAGES} pages, produced {n}")
    print(f"OK: page count locked at {TOTAL_PAGES} "
          f"(print cost $2.84 flat, 24-110pp B&W large trim)")
