import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np

BG = "#0b1220"; GRID = "#1c2740"; GREEN = "#22c55e"; RED = "#ef4444"
BLUE = "#38bdf8"; GOLD = "#facc15"; WHITE = "#f8fafc"; MUTED = "#94a3b8"

# (open, high, low, close)
C = [
    (100, 103.5, 99.5, 103), (103, 106.5, 102.5, 106), (106, 109.5, 105.5, 109),
    (109, 109.6, 106.5, 107), (107, 107.5, 104.5, 105),
    (105, 108.5, 104.8, 108), (108, 111.5, 107.5, 111), (111, 114.5, 110.5, 114),
    (114, 114.6, 111.5, 112), (112, 112.5, 109.5, 110),
    (110, 113.5, 109.8, 113), (113, 116.5, 112.5, 116), (116, 119.5, 115.5, 119),
]
APPEAR = [0.3, 1.1, 1.9, 3.0, 3.6, 4.2, 4.8, 5.4, 6.2, 6.9, 10.1, 10.7, 11.3]
GROW = 0.35
FPS = 30; DUR = 15.0; N = int(FPS * DUR)

PEAKS = [(2, 109.5), (7, 114.5), (12, 119.5)]
LOWS = [(4, 104.5), (9, 109.5)]

fig = plt.figure(figsize=(5.4, 9.6), dpi=200, facecolor=BG)
ax = fig.add_axes([0.06, 0.30, 0.88, 0.48])
tax = fig.add_axes([0, 0, 1, 1]); tax.axis("off"); tax.set_xlim(0, 1); tax.set_ylim(0, 1)

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def fade(t, start, dur=0.4):
    return max(0.0, min(1.0, (t - start) / dur))

def draw(frame):
    t = frame / FPS
    ax.clear(); tax.clear(); tax.axis("off"); tax.set_xlim(0, 1); tax.set_ylim(0, 1)
    ax.set_facecolor(BG)
    ax.set_xlim(-1, len(C)); ax.set_ylim(97, 123)
    for y in range(98, 123, 3):
        ax.axhline(y, color=GRID, lw=0.6, zorder=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

    # title
    tax.text(0.5, 0.855, "How to spot an", color=MUTED, ha="center", fontsize=17, weight="bold")
    tax.text(0.5, 0.805, "UPTREND", color=GREEN, ha="center", fontsize=34, weight="bold")

    # candles
    for i, (o, h, l, c) in enumerate(C):
        if t < APPEAR[i]: continue
        p = ease((t - APPEAR[i]) / GROW)
        col = GREEN if c >= o else RED
        cur_c = o + (c - o) * p
        cur_h = max(o, cur_c) + (h - max(o, c)) * p
        cur_l = min(o, cur_c) - (min(o, c) - l) * p
        ax.plot([i, i], [cur_l, cur_h], color=col, lw=1.6, zorder=2)
        bottom = min(o, cur_c); height = max(abs(cur_c - o), 0.08)
        ax.add_patch(Rectangle((i - 0.32, bottom), 0.64, height, color=col, zorder=3))

    # higher highs
    a = fade(t, 5.8)
    if a > 0:
        for k, (i, y) in enumerate(PEAKS[:2]):
            ax.scatter(i, y + 0.9, s=120, color=GOLD, alpha=a, zorder=5, edgecolors=WHITE, linewidths=1)
        ax.annotate("", xy=(7, 115.6), xytext=(2, 110.6),
                    arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.8, alpha=a, linestyle="--"))
        ax.text(4.5, 115.2, "Higher High", color=GOLD, fontsize=13, weight="bold",
                ha="center", alpha=a, rotation=0)
    if t >= 11.6:
        a3 = fade(t, 11.6)
        ax.scatter(12, 120.4, s=120, color=GOLD, alpha=a3, zorder=5, edgecolors=WHITE, linewidths=1)

    # higher lows
    b = fade(t, 7.4)
    if b > 0:
        for i, y in LOWS:
            ax.scatter(i, y - 0.9, s=120, color=BLUE, alpha=b, zorder=5, edgecolors=WHITE, linewidths=1)
        ax.text(6.5, 103.0, "Higher Low", color=BLUE, fontsize=13, weight="bold", ha="center", alpha=b)

    # trend line
    if t >= 9.0:
        p = ease((t - 9.0) / 1.0)
        line = lambda x: 103.8 + (x - 4)
        x0 = 1; x1 = x0 + (13.2 - x0) * p
        ax.plot([x0, x1], [line(x0), line(x1)],
                color=WHITE, lw=2.2, alpha=0.9, zorder=1)
        if p >= 1:
            ax.text(11.2, 108.5, "Trend Line", color=WHITE, fontsize=12, weight="bold",
                    ha="center", alpha=fade(t, 10.0), rotation=32)

    # bottom captions per phase
    caps = [(0.0, 3.0, "Watch the waves...", WHITE),
            (3.0, 6.0, "Each peak beats the last one", GOLD),
            (6.0, 9.0, "Each dip stops higher", BLUE),
            (9.0, 12.0, "Connect the lows = trend line", WHITE)]
    for s, e, txt, col in caps:
        if s <= t < e:
            al = min(fade(t, s, 0.3), max(0, min(1, (e - t) / 0.3)))
            tax.text(0.5, 0.23, txt, color=col, ha="center", fontsize=17, weight="bold", alpha=al)
    if t >= 12.0:
        al = fade(t, 12.0)
        box = FancyBboxPatch((0.08, 0.175), 0.84, 0.11, boxstyle="round,pad=0.01,rounding_size=0.03",
                             fc="#111c33", ec=GREEN, lw=1.5, alpha=al)
        tax.add_patch(box)
        tax.text(0.5, 0.25, "Higher Highs + Higher Lows", color=WHITE, ha="center",
                 fontsize=16, weight="bold", alpha=al)
        tax.text(0.5, 0.198, "= UPTREND", color=GREEN, ha="center", fontsize=20, weight="bold", alpha=al)
        if t >= 13.3:
            tax.text(0.5, 0.135, "Break a low → trend in danger", color=RED, ha="center",
                     fontsize=13, weight="bold", alpha=fade(t, 13.3))

anim = FuncAnimation(fig, draw, frames=N)
anim.save("/mnt/user-data/outputs/uptrend_tiktok.mp4",
          writer=FFMpegWriter(fps=FPS, bitrate=6000, codec="libx264",
                              extra_args=["-pix_fmt", "yuv420p"]),
          savefig_kwargs={"facecolor": BG})
print("done")
