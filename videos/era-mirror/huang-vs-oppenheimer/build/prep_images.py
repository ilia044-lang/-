#!/usr/bin/env python3
"""Grade every source image into hf/assets/img: <slug>_g.jpg (era grade) and <slug>_bg.jpg (blurred, darkened backdrop)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets/images", ROOT / "hf/assets/img"
OUT.mkdir(parents=True, exist_ok=True)
MODERN = ("huang", "nvidia", "granholm", "rubio", "airforceone", "ccp", "capitol", "doe_", "h100", "wafer", "datacenter", "great_hall", "trump", "warren", "whitehouse", "hearing_room")
DOCS = ("aec_doc", "strauss_memo", "doe_")
for p in sorted(SRC.iterdir()):
    if p.suffix.lower() not in (".jpg", ".png", ".gif"): continue
    slug = p.stem
    if (OUT / f"{slug}_g.jpg").exists() and "--force" not in sys.argv: continue
    im = Image.open(p)
    if getattr(im, "n_frames", 1) > 1: im.seek(0)
    im = im.convert("RGB")
    if max(im.size) > 1800: im.thumbnail((1800, 1800), Image.LANCZOS)
    if slug.startswith(DOCS):
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
        g = ImageOps.colorize(g, black="#1b1813", white="#efe6d2")
    elif slug.startswith(MODERN):
        g = ImageEnhance.Color(im).enhance(0.72)
        g = ImageEnhance.Contrast(g).enhance(1.06)
        r, gg, b = g.split(); b = b.point(lambda v: min(255, int(v * 1.05 + 4))); r = r.point(lambda v: int(v * 0.97))
        g = Image.merge("RGB", (r, gg, b))
    else:
        gr = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=0.5)
        g = ImageOps.colorize(gr, black="#0d0b09", mid="#8c7a61", white="#f6ecd6")
        g = ImageEnhance.Contrast(g).enhance(1.05)
    g.save(OUT / f"{slug}_g.jpg", quality=90)
    bg = g.resize((640, max(1, int(640 * g.size[1] / g.size[0])))).filter(ImageFilter.GaussianBlur(14))
    bg = ImageEnhance.Brightness(bg).enhance(0.42)
    bg.save(OUT / f"{slug}_bg.jpg", quality=82)
    print(slug, g.size)
