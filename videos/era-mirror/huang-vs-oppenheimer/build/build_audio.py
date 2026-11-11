#!/usr/bin/env python3
"""Music bed + sound effects for the film, from build/audio_plan.json. Writes hf/assets/audio/music.wav and sfx.wav.
Bed A (slow pad) sits under the 1943-1954 story, bed B (pulse) under 2026, crossfading at each era change."""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
P = json.load(open(ROOT / "build/audio_plan.json"))
S, OUT, T = ROOT / "assets/audio/sfx", ROOT / "hf/assets/audio", P["total"]
XF = 1.4
def run(cmd): subprocess.run(cmd, check=True)
# ---- music: volume envelopes per bed
def env(want):
    pts = []
    for e in P["eras"]:
        on = 1.0 if (e["era"] == "c") == (want == "B") else 0.0
        pts.append((e["start"], on))
    expr, prev = "", None
    segs = []
    for i, (st, on) in enumerate(pts):
        en = pts[i + 1][0] if i + 1 < len(pts) else T
        segs.append((st, en, on))
    parts = []
    for i, (st, en, on) in enumerate(segs):
        prev_on = segs[i - 1][2] if i else on
        if prev_on != on:
            parts.append(f"between(t,{st:.2f},{st + XF:.2f})*({prev_on}+({on}-{prev_on})*(t-{st:.2f})/{XF})")
            parts.append(f"between(t,{st + XF:.2f},{en:.2f})*{on}")
        else:
            parts.append(f"between(t,{st:.2f},{en:.2f})*{on}")
    return "+".join(parts)
MUSIC_DB = -29.0   # under the narration
fade = f"afade=t=in:d=1.2,afade=t=out:st={T - 5:.2f}:d=5"
run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(S / "dark-suspense-underscore-2.wav"), "-stream_loop", "-1", "-i", str(S / "dark-suspense-underscore-3.wav"),
     "-filter_complex", f"[0:a]atrim=0:{T:.2f},volume='{env('A')}':eval=frame[a];[1:a]atrim=0:{T:.2f},volume='0.8*({env('B')})':eval=frame[b];[a][b]amix=inputs=2:normalize=0,loudnorm=I={MUSIC_DB}:TP=-3:LRA=7,{fade}[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", str(OUT / "music.wav")])
# ---- effects
FILES = {"whoosh": [("cinematic-whoosh.wav", 0.42, 0.5), ("short-whoosh-transition.wav", 0.40, 0.5)], "boom": [("deep-boom-hit.wav", 0.02, 0.55)], "thump": [("deep-bass-thump.wav", 0.06, 0.38)], "key": [("mechanical-key-press.wav", 0.09, 0.5)]}
ev = [e for e in P["fx"] if e["kind"] in FILES]
ins, filt, labels, n = [], [], [], {}
for i, e in enumerate(sorted(ev, key=lambda e: e["t"])):
    opts = FILES[e["kind"]]; k = n.get(e["kind"], 0); n[e["kind"]] = k + 1
    f, lead, vol = opts[k % len(opts)]
    ins += ["-i", str(S / f)]
    d = max(0, int((e["t"] - lead + 0.033) * 1000))   # peak lands one frame after the picture
    filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={d}|{d}[s{i}]"); labels.append(f"[s{i}]")
filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={T:.2f},atrim=0:{T:.2f},alimiter=limit=0.7[o]")
run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[o]", "-ar", "48000", "-ac", "2", str(OUT / "sfx.wav")])
print("music + sfx written:", len(ev), "cues", n)
