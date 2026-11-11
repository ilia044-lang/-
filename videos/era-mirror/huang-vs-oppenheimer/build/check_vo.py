#!/usr/bin/env python3
"""Transcribe every narration line and compare with the script. Usage: check_vo.py <lang> [script.json]"""
import json, sys, re, difflib
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path(__file__).resolve().parent.parent
lang = sys.argv[1]
script = json.load(open(sys.argv[2] if len(sys.argv) > 2 else ROOT / "script/script.json", encoding="utf-8"))
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
norm = lambda s: re.sub(r"[^\w\s]", "", s.lower(), flags=re.U).split() if lang != "zh" else list(re.sub(r"[^\w]", "", s, flags=re.U))
bad = []
for sc in script["scenes"]:
    for i, line in enumerate(sc["lines" if lang == "en" else f"lines_{lang}"], 1):
        p = ROOT / f"assets/audio/vo_{lang}/{sc['id']}_{i:02d}.wav"
        if not p.exists(): bad.append((sc["id"], i, 0, "MISSING")); continue
        segs, _ = m.transcribe(str(p), language=lang, beam_size=1)
        hyp = " ".join(s.text for s in segs)
        r = difflib.SequenceMatcher(None, norm(line), norm(hyp)).ratio()
        if r < 0.82: bad.append((sc["id"], i, round(r, 2), hyp.strip()[:150]))
json.dump(bad, open(ROOT / f"build/vo_check_{lang}.json", "w"), ensure_ascii=False, indent=1)
print(lang, "suspect lines:", len(bad))
for b in bad: print(b)
