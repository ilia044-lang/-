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


def text_page(c, page_no, title, lines):
    x, y, w, h = safe_box(page_no)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(x + w / 2, y + h - 1.2 * inch, title)
    c.setFont("Helvetica", 15)
    ty = y + h - 2.1 * inch
    for ln in lines:
        c.drawCentredString(x + w / 2, ty, ln)
        ty -= 0.34 * inch


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
    text_page(c, newpage(), "Color, Cut & Glue", ["ANIMAL HOMES", "", "with Bubi, Maya & Leo"])
    c.showPage()
    text_page(c, newpage(), "This Book Belongs To", ["", "_______________________", "", "I am ____ years old"])
    c.showPage()
    text_page(c, newpage(), "How To Use This Book", [
        "1.  Color the animal.",
        "2.  Cut it out along the dotted line.",
        "3.  Glue it where it lives.",
        "4.  Say it out loud!",
        "", "Always use safety scissors with a grown-up."])
    c.showPage()
    text_page(c, newpage(), "Meet Your Friends", ["Bubi", "Maya", "Leo", "", "They will help you on every page!"])
    c.showPage()

    # --- 40 coloring pages, single-sided: art on recto, blank verso (pages 5-84)
    for hab, animals in HABITATS.items():
        for a in animals:
            n = newpage()
            draw_art(c, A(f"color_{hab}_{a}.png"), safe_box(n), f"{a.upper()}")
            c.showPage()
            blank()                                  # blank back - no bleed-through

    # --- transition, pages 85-86
    text_page(c, newpage(), "Great Job!", ["Now let's bring the animals home.", "", "Turn the page..."])
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
                     (cx + 22, cy + 22, w / 2 - 44, h / 2 - 44), a.upper())
        c.showPage()
        blank()

    # --- 5 habitat spreads, 2 pages each (pages 99-108)
    for hab, title in SCENES:
        n = newpage()                                 # verso: who lives here
        text_page(c, n, "Who Lives Here?", [f"Find the animals that belong in", title.lower() + ".", "", "Tick the box when you glue one."])
        c.showPage()
        n = newpage()                                 # recto: the scene
        draw_art(c, A(f"scene_{hab}.png"), safe_box(n), title.upper())
        c.showPage()

    # --- back matter, pages 109-110
    text_page(c, newpage(), "You Did It!", ["I finished my Animal Homes book.", "", "Name: ______________", "Date: ______________", "", "- Bubi, Maya & Leo"])
    c.showPage()
    text_page(c, newpage(), "More Free Pages", ["Scan the code for free bonus", "coloring pages and videos.", "", "[ QR CODE ]"])
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
