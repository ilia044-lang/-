"""One-command build: script in scene.html -> voices -> retimed animation -> audio mix -> mp4.

  python3 build.py OUT.mp4

Env:
  KOKORO_DIR  folder with onnx/model.onnx and voices/*.bin (onnx-community/Kokoro-82M-v1.0-ONNX)
  SFX_DIR     folder with the Soundza files listed in SOUNDZA-LICENSE.txt
Pose/door/caption times in scene.html are "script time". Only line lengths change:
the gap after each line is kept, so action beats (door, freeze, cut) keep their length.
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
KOKORO_DIR = os.environ['KOKORO_DIR']
SFX_DIR = os.environ.get('SFX_DIR', os.path.join(HERE, 'sfx'))
OUT = os.path.abspath(sys.argv[1])
WORK = os.path.join(os.path.dirname(OUT), 'build_tmp'); os.makedirs(WORK, exist_ok=True)

CAST = {'dad': ('am_michael', 1.0, 0), 'mom': ('af_heart', 1.0, 0), 'kid': ('af_sky', 0.92, 4)}
SCENE_B_GAIN = 0.75          # scene B is whispered
KICK_T = 26.6                # script time of the kick (bonk)
DOOR_OPEN_T = [4.6, 10.1, 14.6]
MUSIC_STOP_AFTER_LINE = 6    # music dies after "what happens when we die?"

html = open(os.path.join(HERE, 'scene.html')).read()
LINES = [dict(who=w, t0=float(a), t1=float(b), text=t) for w, a, b, t in
         re.findall(r"\{who:'(\w+)', t0:([\d.]+),\s*t1:([\d.]+),\s*text:\"(.*?)\"\}", html)]
CUT = float(re.search(r'const CUT = ([\d.]+);', html).group(1))
DUR = float(re.search(r'const DURATION = ([\d.]+);', html).group(1))
print(f'{len(LINES)} lines, cut {CUT}, duration {DUR}')

# ---------- 1. voices ----------
from kokoro_onnx import Kokoro
names = sorted({v for v, _, _ in CAST.values()})
np.savez(os.path.join(WORK, 'voices.npz'),
         **{n: np.fromfile(f'{KOKORO_DIR}/voices/{n}.bin', dtype=np.float32).reshape(-1, 1, 256) for n in names})
k = Kokoro(f'{KOKORO_DIR}/onnx/model.onnx', os.path.join(WORK, 'voices.npz'))
SR = 24000
clips = []
for i, l in enumerate(LINES):
    v, spd, semi = CAST[l['who']]
    a, sr = k.create(l['text'], voice=v, speed=spd, lang='en-us')
    raw = f'{WORK}/raw_{i}.wav'; fin = f'{WORK}/line_{i}.wav'; sf.write(raw, a, sr)
    af = f'asetrate={sr}*{2**(semi/12):.5f},aresample={SR},atempo={1/2**(semi/12):.5f}' if semi else f'aresample={SR}'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-ac', '1', '-af', af, fin], check=True)
    clips.append(sf.read(fin, dtype='float32')[0])

# ---------- 2. check every line is understood (speech recognition) ----------
from faster_whisper import WhisperModel
wm = WhisperModel('base.en', device='cpu', compute_type='int8')
norm = lambda s: re.sub(r'[^a-z ]', '', s.lower()).split()
for i, (l, c) in enumerate(zip(LINES, clips)):
    c16 = np.interp(np.arange(0, len(c), SR / 16000), np.arange(len(c)), c).astype(np.float32)
    heard = ' '.join(s.text.strip() for s in wm.transcribe(c16, beam_size=5)[0])
    ok = norm(heard) == norm(l['text'])
    print(f"{'OK ' if ok else '?? '} {l['who']}: {l['text']}  | heard: {heard}")

# ---------- 3. retime ----------
new, t = [], LINES[0]['t0']
for i, (l, c) in enumerate(zip(LINES, clips)):
    new.append((round(t, 3), round(t + len(c) / SR, 3))); t += len(c) / SR
    if i + 1 < len(LINES):
        gap = LINES[i + 1]['t0'] - l['t1']
        if l['t1'] <= CUT < LINES[i + 1]['t0']:
            new_cut = t + (CUT - l['t1']); t = new_cut + (LINES[i + 1]['t0'] - CUT)
        else:
            t += max(0.3, gap)
new_dur = t + (DUR - LINES[-1]['t1'])
old_a, new_a = [0.0], [0.0]
for (l, n) in zip(LINES, new):
    if l['t0'] > CUT and CUT not in old_a:
        old_a.append(CUT); new_a.append(round(new_cut, 3))
    old_a += [l['t0'], l['t1']]; new_a += [n[0], n[1]]
old_a.append(DUR); new_a.append(round(new_dur, 3))
fromOld = lambda x: float(np.interp(x, old_a, new_a))
inj = (f"const WARP_NEW={json.dumps(new_a)}, WARP_OLD={json.dumps(old_a)};\n"
       "function toOld(t){ for(let i=1;i<WARP_NEW.length;i++){ if(t<=WARP_NEW[i]){ const u=(t-WARP_NEW[i-1])/(WARP_NEW[i]-WARP_NEW[i-1]); return WARP_OLD[i-1]+u*(WARP_OLD[i]-WARP_OLD[i-1]); } } return WARP_OLD[WARP_OLD.length-1]; }\n"
       f"const NEW_DURATION={round(new_dur, 3)};\n")
h = html.replace('// ---------- helpers ----------', inj + '// ---------- helpers ----------')
h = h.replace("function render(t){\n  const tq = Math.floor(t*12)/12;",
              "function render(tn){\n  const tq = toOld(Math.floor(tn*12)/12); const t = toOld(tn);")
h = h.replace('window.render=render; window.DURATION=DURATION;', 'window.render=render; window.DURATION=NEW_DURATION;')
assert 'toOld(Math.floor' in h and 'NEW_DURATION;' in h
voiced = os.path.join(HERE, 'scene_voiced.html'); open(voiced, 'w').write(h)
json.dump({'lines': new, 'cut': new_cut, 'dur': new_dur}, open(os.path.join(HERE, 'timing.json'), 'w'))
print('new duration', round(new_dur, 2))

# ---------- 4. render picture ----------
vid = f'{WORK}/video_only.mp4'
subprocess.run(['node', os.path.join(HERE, 'render.js'), voiced, vid, '24'], check=True)

# ---------- 5. audio mix ----------
MSR = 44100
def load(p):
    pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-ac', '1', '-ar', str(MSR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()
N = int((new_dur + 0.3) * MSR)
mix = np.zeros(N, np.float32)
def put(a, t, g):
    s = int(t * MSR); e = min(N, s + len(a)); mix[s:e] += a[:e - s] * g
for i, n in enumerate(new):
    put(load(f'{WORK}/line_{i}.wav'), n[0], 0.9 * (SCENE_B_GAIN if LINES[i]['t0'] > CUT else 1.0))
creak = load(f'{SFX_DIR}/soundza-old-wooden-door-creak.wav')
for i, d in enumerate(DOOR_OPEN_T):
    put(creak, fromOld(d) - 0.05, 0.6 if i == len(DOOR_OPEN_T) - 1 else 0.45)
put(load(f'{SFX_DIR}/soundza-deep-bonk-hit.wav'), fromOld(KICK_T), 0.7)
music = load(f'{SFX_DIR}/soundza-pizzicato-comedy-2.wav')
stop = new[MUSIC_STOP_AFTER_LINE][1]
seg = music[:int(stop * MSR)].copy(); f = int(0.05 * MSR); seg[-f:] *= np.linspace(1, 0, f); put(seg, 0, 0.14)
seg2 = music[int(40 * MSR):int(40 * MSR) + int((new_dur - new_cut + 0.3) * MSR)].copy()
fi, fo = int(0.8 * MSR), int(1.5 * MSR); seg2[:fi] *= np.linspace(0, 1, fi); seg2[-fo:] *= np.linspace(1, 0, fo)
put(seg2, new_cut, 0.08)
mix = mix / np.abs(mix).max() * 0.95
wav = f'{WORK}/full_mix.wav'; sf.write(wav, np.stack([mix, mix], 1), MSR)

# ---------- 6. mux ----------
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-shortest', '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT)
