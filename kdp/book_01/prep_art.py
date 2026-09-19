#!/usr/bin/env python3
"""
Normalise generated line art into print-ready pages for KDP.

Generators hand back soft, anti-aliased RGB at whatever size they feel like.
KDP wants >=300 DPI and the book wants pure black on pure white. For thick,
simple line art - and only for that - upscaling then thresholding is safe:
there is no fine detail to lose, and the threshold rebuilds crisp edges.

Per file it:
  1. converts to grayscale
  2. upscales (LANCZOS) so the short side clears the target DPI
  3. thresholds to pure 1-bit black and white - kills every gray
  4. pads to the exact page aspect ratio on white, so nothing is cropped
  5. writes a 1-bit PNG carrying 300 DPI metadata

    python3 prep_art.py --in raw/ --out art/
    python3 prep_art.py --in raw/ --out art/ --square      # cut-outs, cover art
"""
import argparse, os, sys
from PIL import Image

DPI = 300
PAGE_W_IN, PAGE_H_IN = 8.5, 11.0
THRESHOLD = 170          # generated line art sits well below this; edges above


def target_size(square):
    if square:
        s = int(PAGE_W_IN * DPI)
        return s, s
    return int(PAGE_W_IN * DPI), int(PAGE_H_IN * DPI)


def prep(src, dst, square=False):
    im = Image.open(src).convert("L")
    tw, th = target_size(square)

    # Scale to FIT inside the page box, never to cover it. Covering overshoots
    # one dimension, so art of different aspect ratios would land at different
    # sizes on the page and the book would look uneven. Fitting then padding
    # puts every drawing in an identical box.
    scale = min(tw / im.width, th / im.height)
    im = im.resize((max(1, round(im.width * scale)),
                    max(1, round(im.height * scale))), Image.LANCZOS)

    # pure black or pure white, nothing between
    im = im.point(lambda p: 255 if p > THRESHOLD else 0, mode="1")

    # centre on a white page of exactly the page aspect ratio - never crop
    if (im.width, im.height) != (tw, th):
        canvas = Image.new("1", (tw, th), 1)
        canvas.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        im = canvas

    im.save(dst, dpi=(DPI, DPI), optimize=True)
    return im.size


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--square", action="store_true",
                    help="square output, for cut-out cards and cover art")
    a = ap.parse_args()

    os.makedirs(a.dst, exist_ok=True)
    files = sorted(f for f in os.listdir(a.src)
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    if not files:
        sys.exit(f"no images in {a.src}")

    for f in files:
        name = os.path.splitext(f)[0] + ".png"
        before = Image.open(os.path.join(a.src, f)).size
        w, h = prep(os.path.join(a.src, f), os.path.join(a.dst, name), a.square)
        print(f"  {f:<34} {before[0]}x{before[1]}  ->  {w}x{h}  "
              f"({min(w/PAGE_W_IN, h/PAGE_H_IN):.0f} DPI, 1-bit)")
    print(f"{len(files)} files ready in {a.dst}")
