"""Shared toolkit for trading TikTok videos: theme, animation helpers, AI voice (Kokoro),
original background music, and final audio/video mixing. 100% free / open-source.

Usage from a render script:
    import sys; sys.path.insert(0, "/path/to/skill/scripts")
    from vidlib import *
"""
import os, subprocess, wave
import numpy as np

# ---------- Theme (keep identical across all videos = channel identity) ----------
BG = "#0b1220"; GRID = "#1c2740"; GREEN = "#22c55e"; RED = "#ef4444"
GOLD = "#facc15"; WHITE = "#f8fafc"; MUTED = "#94a3b8"; ORANGE = "#fb923c"; BLUE = "#38bdf8"
CARD = "#111c33"
FPS = 30
W_IN, H_IN, DPI = 5.4, 9.6, 200          # -> 1080x1920 vertical
# TikTok safe zones (figure coords 0..1): keep text between y=0.13 and y=0.88.
TITLE_Y = (0.855, 0.805); CAPTION_Y = 0.23; CHART_RECT = [0.06, 0.31, 0.88, 0.47]

# ---------- Animation helpers ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): return 1 - (1 - clamp(x)) ** 3
def fade(t, start, dur=0.4): return clamp((t - start) / dur)
def window(t, s, e, d=0.3): return min(fade(t, s, d), clamp((e - t) / d))

def draw_candle(ax, i, o, h, l, c, p=1.0, width=0.64, lw=1.6):
    """Draw candle i growing from open to close; p in 0..1 is the grow progress."""
    from matplotlib.patches import Rectangle
    col = GREEN if c >= o else RED
    cc = o + (c - o) * p
    hh = max(o, cc) + (h - max(o, c)) * p
    ll = min(o, cc) - (min(o, c) - l) * p
    ax.plot([i, i], [ll, hh], color=col, lw=lw, zorder=2)
    ax.add_patch(Rectangle((i - width / 2, min(o, cc)), width, max(abs(cc - o), 0.08), color=col, zorder=3))

def style_axes(ax, xlim, ylim, grid_step=3):
    ax.set_facecolor(BG); ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    for y in np.arange(ylim[0], ylim[1], grid_step): ax.axhline(y, color=GRID, lw=0.6, zorder=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

# ---------- AI voice (Kokoro, free, offline) ----------
SK = "/home/claude/kokoro"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def setup_voice():
    """Install kokoro-onnx and download model files (sequentially - parallel downloads corrupted before)."""
    os.makedirs(SK, exist_ok=True)
    subprocess.run("pip install kokoro-onnx soundfile --break-system-packages -q", shell=True)
    for url, name, minsize in [(MODEL_URL, "kokoro.onnx", 300e6), (VOICES_URL, "voices.bin", 25e6)]:
        p = f"{SK}/{name}"
        if not (os.path.exists(p) and os.path.getsize(p) > minsize):
            subprocess.run(["curl", "-sL", "-o", p, url], check=True)

def tts(lines, prefix="line", voice="am_michael", speed=1.05, outdir="."):
    """Generate one wav per line. Returns list of (path, duration_seconds).
    Default voice am_michael (calm male mentor). Alternative: af_heart (warm female)."""
    setup_voice()
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(f"{SK}/kokoro.onnx", f"{SK}/voices.bin")
    out = []
    for i, text in enumerate(lines):
        a, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        p = os.path.join(outdir, f"{prefix}{i}.wav"); sf.write(p, a, sr)
        out.append((p, len(a) / sr))
    return out

def schedule(durations, first=0.3, gap=0.35):
    """Back-to-back start times for narration lines. Returns (starts, total_end)."""
    starts, t = [], first
    for d in durations:
        starts.append(round(t, 2)); t += d + gap
    return starts, t

# ---------- Original background music (lo-fi, royalty-free because we generate it) ----------
def make_music(path, dur, bpm=100):
    sr = 44100; beat = 60 / bpm; t = np.arange(int(sr * dur)) / sr; out = np.zeros_like(t)
    f = lambda n: 440 * 2 ** ((n - 69) / 12)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    bar = beat * 4
    for k in range(int(dur / bar) + 1):
        s = int(k * bar * sr); e = min(len(t), int((k + 1) * bar * sr))
        if s >= len(t): break
        tt = t[s:e] - t[s]; env = np.minimum(1, tt / 0.6) * np.exp(-tt * 0.25)
        for n in chords[k % 4]:
            out[s:e] += 0.05 * env * (np.sin(2 * np.pi * f(n) * tt) + 0.3 * np.sin(2 * np.pi * f(n) * 2 * tt))
        for j, n in enumerate(chords[k % 4] * 2 + [chords[k % 4][0] + 12] * 2):
            ps = s + int(j * beat / 2 * sr); pe = min(len(t), ps + int(0.4 * sr))
            if ps >= len(t): break
            pt = t[ps:pe] - t[ps]; out[ps:pe] += 0.035 * np.exp(-pt * 9) * np.sin(2 * np.pi * f(n + 12) * pt)
    for b in np.arange(0, dur, beat):
        ps = int(b * sr); pe = min(len(t), ps + int(0.25 * sr)); pt = t[ps:pe] - t[ps]
        out[ps:pe] += 0.12 * np.exp(-pt * 18) * np.sin(2 * np.pi * (55 + 60 * np.exp(-pt * 30)) * pt)
    fl = int(1.5 * sr); out[-fl:] *= np.linspace(1, 0, fl); fi = int(0.3 * sr); out[:fi] *= np.linspace(0, 1, fi)
    out = out / np.max(np.abs(out)) * 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

# ---------- Final mix ----------
def mix(video, voice_wavs, starts, out, music=None, music_vol=0.2, voice_vol=1.5):
    """Place each narration wav at its start time (seconds), add music underneath, mux with video."""
    inputs = ["-i", video]
    for p in voice_wavs: inputs += ["-i", p]
    n = len(voice_wavs); fc = []
    for i, s in enumerate(starts):
        fc.append(f"[{i+1}]adelay={int(s*1000)}:all=1[a{i}]")
    fc.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,volume={voice_vol},aresample=44100[vo]")
    if music:
        inputs += ["-i", music]
        fc.append(f"[{n+1}]volume={music_vol},aresample=44100[m]")
        fc.append("[vo][m]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]")
    else:
        fc.append("[vo]alimiter=limit=0.95[aout]")
    cmd = ["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
           "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    subprocess.run(cmd, check=True)

def save_anim(fig, draw, duration, path, bg=BG):
    from matplotlib.animation import FuncAnimation, FFMpegWriter
    FuncAnimation(fig, draw, frames=int(FPS * duration)).save(
        path, writer=FFMpegWriter(fps=FPS, bitrate=6000, codec="libx264", extra_args=["-pix_fmt", "yuv420p"]),
        savefig_kwargs={"facecolor": bg})

def preview(video, times, out_png, width=1600):
    """Grab frames at given seconds and tile them side by side for a visual check."""
    frames = []
    for i, s in enumerate(times):
        p = f"/tmp/_pv{i}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(s), "-i", video, "-frames:v", "1", p], check=True)
        frames.append(p)
    args = []
    for p in frames: args += ["-i", p]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-filter_complex",
                    f"{''.join(f'[{i}]' for i in range(len(frames)))}hstack={len(frames)},scale={width}:-1", out_png], check=True)
