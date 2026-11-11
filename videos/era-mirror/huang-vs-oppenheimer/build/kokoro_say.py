#!/usr/bin/env python3
"""Kokoro TTS: one WAV per line. Usage: kokoro_say.py <voice> <speed> <out.wav> <text>   |   --batch <voice> <speed> <script.json> <outdir> [key]"""
import sys, json, numpy as np, soundfile as sf
from pathlib import Path
from kokoro import KPipeline
def synth(pipe, text, voice, speed):
    parts = [a for _, _, a in pipe(text, voice=voice, speed=speed, split_pattern=r"\n+")]
    return np.concatenate([np.asarray(p) for p in parts])
if sys.argv[1] == "--batch":
    voice, speed, script, outdir = sys.argv[2], float(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
    key = sys.argv[6] if len(sys.argv) > 6 else "lines"
    outdir.mkdir(parents=True, exist_ok=True)
    pipe = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
    for sc in json.load(open(script, encoding="utf-8"))["scenes"]:
        for i, line in enumerate(sc[key], 1):
            a = synth(pipe, line, voice, speed)
            sf.write(str(outdir / f"{sc['id']}_{i:02d}.wav"), a, 24000, subtype="PCM_16")
    print("DONE", voice)
else:
    voice, speed, out, text = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    pipe = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
    sf.write(out, synth(pipe, text, voice, speed), 24000, subtype="PCM_16")
    print("ok", out)
