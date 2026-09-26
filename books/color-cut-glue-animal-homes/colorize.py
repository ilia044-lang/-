#!/usr/bin/env python3
"""
Colorize black-and-white line art for the cover.

The interior of the book stays pure black and white - that is the product, and
color there would wreck the print cost. The COVER is printed in full color at no
extra charge, so the cover artwork should use it.

Method: label every white region enclosed by the black lines, then fill each one
with a color from a fixed children's palette. Regions that touch the image
border are background and stay white; very small regions (eye whites, highlights)
stay white; one very large interior region is the title oval and stays white.

    python3 colorize.py --in raw/cover_hero.png --out art/cover_hero_color.png
"""
import argparse
import numpy as np
import scipy.ndimage as ndi
from PIL import Image

# bright, high-contrast, and distinguishable when printed small
PALETTE = [
    (255, 107, 107),   # coral
    (255, 217,  61),   # sunny yellow
    ( 78, 205, 196),   # teal
    ( 93, 169, 233),   # sky blue
    (107, 203, 119),   # leaf green
    (255, 159,  69),   # orange
    (255, 143, 171),   # pink
    (167, 139, 250),   # purple
]

DPI = 300
MIN_AREA_FRAC = 0.00025   # below this a region is an eye white or a highlight
OVAL_AREA_FRAC = 0.10     # above this an interior region is the title oval


def _lum(c):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x / 255) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def usable_palette(avoid, floor=1.4):
    """Drop palette entries that would vanish against the cover background.
    The stock palette contains a yellow identical to the sunshine theme, which
    made the dolphin disappear at thumbnail size."""
    if not avoid:
        return PALETTE
    la = _lum(avoid)
    keep = []
    for c in PALETTE:
        lc = _lum(c)
        hi, lo = max(la, lc), min(la, lc)
        if (hi + 0.05) / (lo + 0.05) >= floor:
            keep.append(c)
    return keep or PALETTE


def colorize(src, dst, line_threshold=128, avoid=None):
    gray = np.array(Image.open(src).convert("L"))
    h, w = gray.shape
    total = h * w

    white = gray > line_threshold
    lab, n = ndi.label(white)

    out = np.stack([gray] * 3, axis=-1).astype(np.uint8)
    out[white] = 255                       # clean any anti-aliased gray away

    # a region touching the border is outside the drawing
    border = set(lab[0].tolist()) | set(lab[-1].tolist()) \
        | set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())

    pal = usable_palette(avoid)
    areas = ndi.sum(white, lab, range(1, n + 1))
    filled = 0
    for i, area in enumerate(areas, start=1):
        if i in border:
            continue                       # background
        frac = area / total
        if frac < MIN_AREA_FRAC:
            continue                       # eye white, tiny highlight
        if frac > OVAL_AREA_FRAC:
            continue                       # the title oval
        out[lab == i] = pal[filled % len(pal)]
        filled += 1

    # keep the lines crisp black over the fills
    out[~white] = 0

    # The outside background becomes transparent so the artwork sits directly on
    # the cover colour instead of painting an unstyled white rectangle over it.
    # Enclosed whites - the title oval, the eye whites - are kept opaque.
    alpha = np.full((h, w), 255, dtype=np.uint8)
    for i in border:
        if i:
            alpha[lab == i] = 0

    Image.fromarray(np.dstack([out, alpha]), mode="RGBA").save(dst, dpi=(DPI, DPI))
    return filled, n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--avoid", help="cover background as RRGGBB; palette "
                    "colours too close to it are dropped")
    a = ap.parse_args()
    avoid = tuple(int(a.avoid[i:i+2], 16) for i in (0, 2, 4)) if a.avoid else None
    pal = usable_palette(avoid)
    filled, n = colorize(a.src, a.dst, avoid=avoid)
    print(f"{a.dst}: filled {filled} of {n} regions "
          f"using {len(pal)} of {len(PALETTE)} palette colours")
