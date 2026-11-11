#!/usr/bin/env python3
"""Lay narration lines onto the film timeline. EN: lines sit at their own start times.
Dubs: each scene's lines are packed into that scene's slot; if a dub runs long it is time-compressed (max 1.28x) per scene.
Usage: build_vo.py <lang> <out.wav> [scene ids...]"""
import json, sys, wave, array, subprocess, tempfile, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
lang, out, only = sys.argv[1], sys.argv[2], sys.argv[3:]
T = json.load(open(ROOT / "build/timeline.json"))
SR = 24000
def read(p, tempo=1.0):
    if tempo != 1.0:
        tmp = tempfile.mktemp(suffix=".wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p), "-af", f"atempo={tempo:.4f}", "-ar", str(SR), "-ac", "1", tmp], check=True)
        p = tmp
    with wave.open(str(p)) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1, p
        a = array.array("h"); a.frombytes(w.readframes(w.getnframes()))
    return a
scenes = [s for s in T["scenes"] if not only or s["id"] in only]
off = scenes[0]["start"] - 0.35 if only else 0
total = scenes[-1]["start"] + scenes[-1]["dur"] - off
buf = array.array("h", bytes(2 * int(total * SR) + 2))
report = []
subs = []
SCRIPT = {x["id"]: x for x in json.load(open(ROOT / "script/script.json", encoding="utf-8"))["scenes"]}
for s in scenes:
    files = [ROOT / f"assets/audio/vo_{lang}/{s['id']}_{i:02d}.wav" for i in range(1, len(s["L"]) + 1)]
    if lang == "en":
        starts, tempo = [s["start"] + x for x in s["L"]], 1.0
    else:
        durs = []
        for f in files:
            with wave.open(str(f)) as w: durs.append(w.getnframes() / SR)
        gap = 0.22
        slot = s["dur"] - 0.55 if s is not T["scenes"][-1] else s["E"][-1] + 1.5
        need = sum(durs) + gap * (len(durs) - 1)
        tempo = min(1.28, max(1.0, need / slot))
        # place each line at its EN start when it fits, otherwise push it later; never overlap
        starts, cur = [], s["start"]
        for i, d in enumerate(durs):
            st = max(cur, s["start"] + s["L"][i] - (0.0 if tempo == 1.0 else 9e9))
            if tempo > 1.0: st = cur
            starts.append(st); cur = st + d / tempo + gap
        report.append((s["id"], round(tempo, 3), round(cur - gap - (s["start"] + s["dur"]), 2)))
    texts = SCRIPT[s["id"]]["lines" if lang == "en" else f"lines_{lang}"]
    for k, (f, st) in enumerate(zip(files, starts)):
        if not f.exists(): continue
        a = read(f, tempo)
        subs.append((st - off, st - off + len(a) / SR, texts[k]))
        i0 = int((st - off) * SR)
        n = min(len(a), len(buf) - i0)
        for k in range(n):
            v = buf[i0 + k] + a[k]
            buf[i0 + k] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
raw = tempfile.mktemp(suffix=".wav")
with wave.open(raw, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(buf.tobytes())
# loudness: -16 LUFS, true peak -1.5 dB, 48 kHz for video
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", "-ac", "2", out], check=True)
os.remove(raw)
def ts(x):
    ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
def chunks(text, a, b):
    """split a long line into subtitle cues of at most ~84 characters, timed by length"""
    import re
    lim = 30 if lang == "zh" else 84
    parts = [p for p in re.split(r"(?<=[.!?。！？，,;])\s*", text) if p]
    cues, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) + 1 > lim: cues.append(cur); cur = p
        else: cur = (cur + ("" if lang == "zh" else " ") + p).strip()
    if cur: cues.append(cur)
    tot = sum(len(c) for c in cues) or 1; out, t0 = [], a
    for c in cues:
        t1 = t0 + (b - a) * len(c) / tot; out.append((t0, t1, c)); t0 = t1
    return out
if not only:
    srt = ROOT / f"out/subtitles_{lang}.srt"; srt.parent.mkdir(exist_ok=True)
    n = 0
    with open(srt, "w", encoding="utf-8") as fh:
        for a, b, text in subs:
            for c0, c1, c in chunks(text, a, b):
                n += 1; fh.write(f"{n}\n{ts(c0)} --> {ts(c1 - 0.04)}\n{c}\n\n")
print(lang, f"{total:.1f}s", "tempo/overrun per scene:", report)
