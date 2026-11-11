#!/usr/bin/env python3
"""Render every narration line to its own WAV (one model load). Usage: tts_batch.py <lang> <script.json> <outdir> [--voice ref.wav]"""
import sys, json, re, os
from pathlib import Path
import torch, torchaudio as ta
lang, script, outdir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
voice = sys.argv[sys.argv.index('--voice')+1] if '--voice' in sys.argv else None
outdir.mkdir(parents=True, exist_ok=True)
import os as _os
torch.set_num_threads(int(_os.environ.get("TTS_THREADS", "4")))
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
if lang == 'ru':
    from ruaccent import RUAccent
    import chatterbox.models.tokenizers.tokenizer as tok
    from unicodedata import normalize
    class _S:
        def __init__(s):
            s.acc = RUAccent(); s.acc.load(omograph_model_size="turbo", use_dictionary=True)
        def stress_text(s, t):
            out = s.acc.process_all(normalize("NFC", t))
            out = re.sub(r"\+(\w)", lambda m: m.group(1) + "́", out)
            def strip_mono(m):
                w = m.group(0)
                return w.replace("́", "") if sum(ch in "аеёиоуыэюяАЕЁИОУЫЭЮЯ" for ch in w) <= 1 else w
            return normalize("NFKD", re.sub(r"[\ẃ]+", strip_mono, out))
    tok._russian_stresser = _S()
model = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
data = json.load(open(script))
key = 'lines' if lang == 'en' else f'lines_{lang}'
cps = {'en': 15.5, 'ru': 14.5, 'es': 15.5, 'zh': 4.8}[lang]
for sc in data['scenes']:
    for i, line in enumerate(sc[key], 1):
        out = outdir / f"{sc['id']}_{i:02d}.wav"
        if out.exists(): continue
        expect = max(0.6, len(line) / cps)
        best = None
        for attempt in range(3):
            wav = model.generate(line, language_id=lang, audio_prompt_path=voice, exaggeration=0.55, cfg_weight=0.4, temperature=0.75).cpu()
            dur = wav.shape[-1] / model.sr
            ratio = dur / expect
            if best is None or abs(ratio - 1) < abs(best[1] - 1): best = (wav, ratio, dur)
            if 0.6 < ratio < 1.6: break
        ta.save(str(out), best[0], model.sr)
        print(f"{out.name} {best[2]:.1f}s ratio={best[1]:.2f} | {line[:50]}", flush=True)
print("DONE", flush=True)
