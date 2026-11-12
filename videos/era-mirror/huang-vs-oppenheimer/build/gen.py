#!/usr/bin/env python3
"""Era Mirror generator: script.json + narration WAVs -> HyperFrames project (hf/index.html + hf/compositions/*.html).
Every on-screen time is derived from the real narration timing, so re-running after a new voice take re-syncs the film."""
import json, html, os, sys, wave, array, math, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
HF = ROOT / "hf"
IMG = HF / "assets" / "img"
ONLY = sys.argv[1:]  # optional scene ids to build (style tests)
LINE_GAP, SCENE_GAP, LEAD, TAIL = 0.30, 0.75, 0.35, 9.0
SR = 24000
AMBER, CYAN, RED, INK, GROUND, PAPER = "#f0c36a", "#2997ff", "#ff453a", "#f5f5f7", "#000000", "#1c1c1e"
GREY = "#86868b"
ERA = {"a": AMBER, "c": CYAN, "n": INK}

script = json.load(open(ROOT / "script/script.json", encoding="utf-8"))
credits = json.load(open(ROOT / "assets/credits.json")) if (ROOT / "assets/credits.json").exists() else {}

# ---------------------------------------------------------------- timing
def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()

timeline, t = [], LEAD
missing = 0
for sc in script["scenes"]:
    L, E, t0 = [], [], (t if timeline else 0.0)
    for i, line in enumerate(sc["lines"], 1):
        p = ROOT / f"assets/audio/vo_en/{sc['id']}_{i:02d}.wav"
        if p.exists():
            d = wav_dur(p)
        else:
            d = max(0.7, len(line) / 15.5); missing += 1
        L.append(t - t0); E.append(t - t0 + d); t += d + LINE_GAP
    t += SCENE_GAP - LINE_GAP
    timeline.append({"id": sc["id"], "start": t0, "dur": t - t0, "L": L, "E": E})
timeline[-1]["dur"] += TAIL
TOTAL = timeline[-1]["start"] + timeline[-1]["dur"]
TL = {x["id"]: x for x in timeline}
json.dump({"total": TOTAL, "scenes": timeline, "estimated_lines": missing}, open(ROOT / "build/timeline.json", "w"), indent=1)

def r2(x):
    return f"{x:.3f}"

esc = html.escape
_imgsize = {}
def imsize(slug):
    if slug not in _imgsize:
        p = IMG / f"{slug}_g.jpg"
        _imgsize[slug] = Image.open(p).size if p.exists() else None
    return _imgsize[slug]

CSS = f"""
#root {{ position:absolute; inset:0; background:{GROUND}; overflow:hidden; font-family:'Inter',sans-serif; color:{INK}; }}
.shot {{ position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:hidden; }}
.in {{ position:absolute; left:0; top:0; width:1920px; height:1080px; }}
.fill {{ position:absolute; left:0; top:0; width:1920px; height:1080px; background:radial-gradient(ellipse at 50% -10%, #1d1d1f 0%, #0a0a0b 45%, {GROUND} 80%); }}
.pbg {{ position:absolute; left:-120px; top:-70px; width:2160px; height:1220px; object-fit:cover; opacity:.55; }}
.shade {{ position:absolute; left:0; top:0; width:1920px; height:1080px; background:radial-gradient(ellipse at 50% 45%, rgba(0,0,0,.25) 0%, rgba(0,0,0,.92) 100%); }}
.pcard {{ position:absolute; border-radius:28px; overflow:hidden; box-shadow:0 40px 100px rgba(0,0,0,.7), 0 0 0 1px rgba(255,255,255,.14); background:#111; }}
.pcard img {{ display:block; width:100%; height:100%; object-fit:cover; }}
.tx {{ position:absolute; line-height:1.06; }}
.tx .w {{ display:inline-block; white-space:pre; }}
.serif {{ font-family:'Inter',sans-serif; font-weight:700; letter-spacing:-.035em; }}
.mono {{ font-family:'Inter',sans-serif; font-weight:600; letter-spacing:.02em; line-height:1.2; }}
.a {{ color:{AMBER}; }} .c {{ color:{CYAN}; }} .n {{ color:{INK}; }} .r {{ color:{RED}; }} .dim {{ color:{GREY}; }}
.hud {{ position:absolute; left:96px; top:60px; font-size:28px; font-weight:600; letter-spacing:.01em; padding:12px 26px; border-radius:999px; background:rgba(255,255,255,.1); box-shadow:inset 0 0 0 1px rgba(255,255,255,.16); }}
.src {{ position:absolute; left:96px; top:984px; font-size:28px; font-weight:500; color:{GREY}; }}
.src b {{ color:#d2d2d7; font-weight:600; }}
.cred {{ position:absolute; right:96px; top:70px; font-size:17px; color:rgba(245,245,247,.5); text-align:right; }}
.flood {{ position:absolute; left:0; top:0; width:1920px; height:1080px; }}
.paper {{ position:absolute; background:{PAPER}; color:{INK}; border-radius:32px; box-shadow:0 50px 110px rgba(0,0,0,.7), inset 0 0 0 1px rgba(255,255,255,.12); padding:60px 68px; font-family:'Inter',sans-serif; font-weight:500; font-size:30px; line-height:1.4; letter-spacing:-.01em; }}
.paper .ph {{ font-size:28px; font-weight:600; color:{GREY}; padding-bottom:18px; margin-bottom:26px; border-bottom:1px solid rgba(255,255,255,.14); letter-spacing:0; }}
.paper .pl {{ margin-bottom:14px; }}
.paper .hl {{ background-image:linear-gradient(rgba(255,69,58,.5),rgba(255,69,58,.5)); background-repeat:no-repeat; background-position:0 92%; background-size:0% 14%; font-weight:700; }}
.row {{ position:absolute; left:160px; width:1600px; height:108px; }}
.row .k {{ position:absolute; left:0; top:0; width:330px; font-size:28px; line-height:1.25; color:{GREY}; font-weight:600; padding-top:10px; }}
.row .l, .row .rr {{ position:absolute; top:0; width:610px; font-family:'Inter',sans-serif; font-weight:700; letter-spacing:-.03em; font-size:44px; line-height:1.1; }}
.row .l {{ left:360px; color:{AMBER}; }} .row .rr {{ left:1010px; color:{CYAN}; }}
.rule {{ position:absolute; height:1px; background:rgba(255,255,255,.18); }}
.bar {{ position:absolute; }}
.sil {{ position:absolute; }}
"""

class Scene:
    def __init__(self, sid, era, nxt_era):
        self.id, self.era, self.nxt = sid, era, nxt_era
        tl = TL[sid]
        self.dur, self.L, self.E = tl["dur"], tl["L"], tl["E"]
        self.h, self.js, self.n, self.z = [], [], 0, 1
    def uid(self, p="e"):
        self.n += 1
        return f"{self.id}-{p}{self.n}"
    def l(self, i):
        return self.L[i - 1]
    def e(self, i):
        return self.E[min(i, len(self.E)) - 1]
    def end(self, i):
        """time the next line starts (or scene end)"""
        return self.L[i] if i < len(self.L) else self.dur
    # ---- primitives
    def clip(self, t0, t1, inner, fade=0.3, cls="shot", hold=0.3):
        """A full-frame shot. It stays `hold` seconds under the next shot so cuts never show the ground."""
        cid = self.uid("s")
        t1 = min(self.dur, t1 + hold)
        self.z += 1
        self.h.append(f'<div id="{cid}" class="clip {cls}" data-start="{r2(t0)}" data-duration="{r2(t1 - t0)}" data-track-index="{self.z}" style="z-index:{self.z}"><div class="in" id="{cid}-in">{inner}</div></div>')
        if fade and not (self.id == "s01" and t0 < 0.05):
            self.js.append(f'tl.fromTo("#{cid}-in",{{opacity:0}},{{opacity:1,duration:{fade},ease:"power2.out"}},{r2(t0)});')
        return cid
    def over(self, t0, t1, inner, fade=0.25):
        """An overlay element (HUD, source chip, label): not full-frame."""
        cid = self.uid("o")
        self.z += 1
        t1 = min(self.dur, t1)
        self.h.append(f'<div id="{cid}" class="clip" data-start="{r2(t0)}" data-duration="{r2(t1 - t0)}" data-track-index="{self.z}" style="position:absolute;left:0;top:0;width:1920px;height:1080px;z-index:{500 + self.z}"><div id="{cid}-in" style="position:absolute;left:0;top:0;width:1920px;height:1080px">{inner}</div></div>')
        self.js.append(f'tl.fromTo("#{cid}-in",{{opacity:0}},{{opacity:1,duration:{fade},ease:"power2.out"}},{r2(t0)});')
        if t1 < self.dur - 0.05:
            self.js.append(f'tl.to("#{cid}-in",{{opacity:0,duration:0.18,ease:"power2.in"}},{r2(t1 - 0.19)});')
        return cid
    def hud(self, t0, t1, text, era=None):
        self.over(t0, t1, f'<div class="hud {era or self.era}">{esc(text)}</div>')
    def src(self, t0, t1, text):
        self.over(t0, t1, f'<div class="src" data-layout-allow-caption-zone><b>SOURCE</b> · {esc(text)}</div>')
    def recon(self, t0, t1):
        return

    def words(self, text, t0, t1, x, y, w, size, cls="serif n", align="left", stagger=None, lh=1.12, hold_to=None, hi=None, hicls="a"):
        """Text block whose words arrive between t0 and t1 (spoken pace). Returns html; tweens are queued."""
        tid = self.uid("t")
        ws = text.split(" ")
        spans = []
        for i, wd in enumerate(ws):
            c = f' class="w {hicls}"' if hi and wd.strip('.,?!"“”').lower() in hi else ' class="w"'
            spans.append(f'<span{c} id="{tid}-{i}">{esc(wd)}{" " if i < len(ws) - 1 else ""}</span>')
        step = stagger if stagger else max(0.05, (t1 - t0) / max(1, len(ws)))
        for i in range(len(ws)):
            self.js.append(f'tl.fromTo("#{tid}-{i}",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:0.2,ease:"power2.out"}},{r2(t0 + i * step)});')
        return f'<div id="{tid}" class="tx {cls}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;text-align:{align};line-height:{lh}">{"".join(spans)}</div>'

    def label(self, text, x, y, size=26, cls="mono n", w=1200, align="left"):
        return f'<div class="tx {cls}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;text-align:{align}">{esc(text)}</div>'

    def pop(self, sel_id, t, y=26, dur=0.5):
        self.js.append(f'tl.fromTo("#{sel_id}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{dur},ease:"expo.out"}},{r2(t)});')

    def block(self, inner, t, x=0, y=0):
        """wrap html so it appears at t"""
        bid = self.uid("b")
        self.pop(bid, t)
        return f'<div id="{bid}" style="position:absolute;left:{x}px;top:{y}px">{inner}</div>'

    # ---- shots
    def plate(self, t0, t1, slug, side="center", name=None, sub=None, era=None, extra="", tilt=(-5, 4), boxw=None, boxh=None, credit=True, focus="50% 30%"):
        """Archive photo as a tilted print floating over its own blurred copy (2.5D parallax)."""
        era = era or self.era
        size = imsize(slug)
        if not size:
            print("  ! missing image", slug)
            return self.clip(t0, t1, f'<div class="fill"></div>{extra}')
        bw = boxw or (1500 if side == "center" else 900)
        bh = boxh or (800 if side == "center" else 730)
        ar = size[0] / size[1]
        w, h = (bw, bw / ar) if bw / ar <= bh else (bh * ar, bh)
        if h < bh * 0.72 and side != "center":  # very wide image in a tall slot: crop to fill a bit
            h = bh * 0.72; w = min(bw, h * ar)
        x = {"center": (1920 - w) / 2, "left": 120 + (bw - w) / 2, "right": 1920 - 120 - bw + (bw - w) / 2}[side]
        y = (1080 - h) / 2 - 45
        cid = self.uid("p")
        d = t1 - t0 + 0.3
        lab = ""
        if name:
            lx = x if side != "center" else x
            lab = f'<div class="tx mono {era}" style="left:{lx:.0f}px;top:{y + h + 26:.0f}px;width:{max(w, 700):.0f}px;font-size:32px;font-weight:600">{esc(name)}' + (f'<div class="dim" style="font-size:28px;margin-top:6px;letter-spacing:.04em;font-weight:400;text-transform:none">{esc(sub)}</div>' if sub else "") + "</div>"
        cr = ""
        if credit and slug in credits:
            c = credits[slug]
            who = c["artist"].replace("Unknown authorUnknown author", "Unknown author")[:60] or c["credit"][:60]
            cr = f'<div class="cred" data-layout-ignore>{esc(who)} · {esc(c["license"])}</div>'
        inner = (f'<img class="pbg" id="{cid}-bg" src="assets/img/{slug}_bg.jpg" alt=""><div class="shade"></div>'
                 f'<div class="pcard" id="{cid}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"><img src="assets/img/{slug}_g.jpg" alt="" style="object-position:{focus}"></div>{lab}{cr}{extra}')
        sid = self.clip(t0, t1, inner)
        self.js.append(f'tl.fromTo("#{cid}-bg",{{x:-36,scale:1.04}},{{x:36,scale:1.1,duration:{r2(d)},ease:"none"}},{r2(t0)});')
        self.js.append(f'tl.fromTo("#{cid}",{{scale:0.965,y:14}},{{scale:1.0,y:0,duration:0.9,ease:"expo.out"}},{r2(t0)});')
        self.js.append(f'tl.fromTo("#{cid} img",{{scale:1.0}},{{scale:1.09,duration:{r2(d)},ease:"none"}},{r2(t0)});')
        return sid

    def three(self, t0, t1, kind, cam, opts="{}", extra="", hold=0.3):
        cid = self.uid("c")
        d = t1 - t0 + hold
        sid = self.clip(t0, t1, f'<canvas class="cv" id="{cid}" width="1440" height="810"></canvas><div class="shade" style="opacity:.75"></div>{extra}', hold=hold)
        self.js.append(f'(function(){{var dr=EM3D.{kind}(document.getElementById("{cid}")),st={{t:0}},o=Object.assign({{cam:{json.dumps(cam)}}},{opts});var f=function(){{dr(st.t,o.fn?Object.assign({{}},o,o.fn(st.t)):o);}};tl.fromTo(st,{{t:0}},{{t:{r2(d)},duration:{r2(d)},ease:"none",onUpdate:f}},{r2(t0)});st.t=0;f();}})();')
        return sid

    def counter(self, t, frm, to, x, y, size, cls="serif n", w=1400, align="left", dur=1.4, pre="", suf="", dec=0, comma=True):
        cid = self.uid("n")
        fmt = f'v.toFixed({dec})' if not comma else f'Number(v.toFixed({dec})).toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})'
        self.js.append(f'(function(){{var el=document.getElementById("{cid}"),o={{v:{frm}}};var f=function(){{var v=o.v;el.textContent={json.dumps(pre)}+{fmt}+{json.dumps(suf)};}};tl.fromTo(o,{{v:{frm}}},{{v:{to},duration:{dur},ease:"power3.out",onUpdate:f}},{r2(t)});f();}})();')
        return f'<div id="{cid}" class="tx {cls}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;text-align:{align};font-variant-numeric:tabular-nums">{esc(pre)}{frm}{esc(suf)}</div>'

    def paper(self, header, lines, x, y, w, rot=(-2, 5), size=30, t_in=None):
        """Typeset excerpt on paper. lines: list of (text_with_[[highlight]], appear_t, highlight_t or None)"""
        pid = self.uid("d")
        out = [f'<div class="ph">{esc(header)}</div>']
        for i, (text, ta, th) in enumerate(lines):
            lid = f"{pid}-l{i}"
            if "[[" in text:
                parts = re.split(r"\[\[(.+?)\]\]", text)
                body = ""
                for j, part in enumerate(parts):
                    if j % 2 == 0:
                        body += esc(part)
                    else:
                        body += f'<span class="hl" id="{lid}-h{j}">{esc(part)}</span>'
                        if th is not None:
                            self.js.append(f'tl.fromTo("#{lid}-h{j}",{{backgroundSize:"0% 14%"}},{{backgroundSize:"100% 14%",duration:0.55,ease:"power2.out"}},{r2(th + (j // 2) * 1.3)});')
            else:
                body = esc(text)
            out.append(f'<div class="pl" id="{lid}">{body}</div>')
            self.js.append(f'tl.fromTo("#{lid}",{{opacity:0}},{{opacity:1,duration:0.25,ease:"power2.out"}},{r2(ta)});')
        return f'<div class="paper" id="{pid}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px">{"".join(out)}</div>', pid

    def tilt(self, el_id, t0, t1, rot=(-3, 4), sc=(0.97, 1.03), rx=(3, 0)):
        self.js.append(f'tl.fromTo("#{el_id}",{{scale:0.96,y:24}},{{scale:1.0,y:0,duration:0.9,ease:"expo.out"}},{r2(t0)});')

    def silhouette(self, x, y, h, era):
        """A generic figure outline. Used where no freely licensed photo exists; never a likeness."""
        w = h * 0.72
        return (f'<svg class="sil" style="left:{x}px;top:{y}px" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 72 100">'
                f'<rect x="0.5" y="0.5" width="71" height="99" rx="6" fill="#1c1c1e" stroke="rgba(255,255,255,.16)" stroke-width="0.4"/>'
                f'<circle cx="36" cy="38" r="14" fill="#3a3a3c"/><path d="M10 99 C10 72 23 60 36 60 C49 60 62 72 62 99 Z" fill="#3a3a3c"/></svg>')

    def build(self):
        flood_in = f'<div id="{self.id}-fi" class="flood" style="background:#000;z-index:900" data-layout-ignore></div>'
        flood_out = f'<div id="{self.id}-fo" class="flood" style="background:#000;z-index:901" data-layout-ignore></div>' if self.nxt else ""
        first = self.id == "s01"
        if first:
            flood_in = f'<div id="{self.id}-fi" class="flood" style="background:#000;z-index:900;opacity:0" data-layout-ignore></div>'
        js = [] if first else [f'tl.fromTo("#{self.id}-fi",{{opacity:1}},{{opacity:0,duration:0.45,ease:"power2.out"}},0);']
        if self.nxt:
            js.append(f'tl.fromTo("#{self.id}-fo",{{opacity:0}},{{opacity:1,duration:0.3,ease:"power2.in"}},{r2(self.dur - 0.3)});')
        else:
            js.append(f'tl.set("#{self.id}-fi",{{opacity:0}},{r2(self.dur)});')
        body = "\n    ".join(self.h)
        code = "\n      ".join(self.js + js)
        return f"""<template>
  <style>{CSS}</style>
  <div id="root" data-composition-id="{self.id}" data-width="1920" data-height="1080">
    {body}
    {flood_in}{flood_out}
  </div>
  <script src="lib/em3d.js"></script>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {code}
      window.__timelines["{self.id}"] = tl;
    }})();
  </script>
</template>
"""

from scenes import SCENES, SFX  # noqa: E402  (scene functions use the Scene API above)

def main():
    (HF / "compositions").mkdir(exist_ok=True)
    order = [s["id"] for s in script["scenes"]]
    hosts = []
    fx = []
    for i, sid in enumerate(order):
        if ONLY and sid not in ONLY:
            continue
        era, fn = SCENES[sid]
        nxt = SCENES.get(order[i + 1], ("a",))[0] if i + 1 < len(order) else None
        sc = Scene(sid, era, nxt if not ONLY else None)
        fn(sc)
        for kind, tt in SFX.get(sid, lambda s: [])(sc):
            fx.append({"kind": kind, "t": round(TL[sid]["start"] + tt, 3)})
        fx.append({"kind": "whoosh", "t": round(TL[sid]["start"], 3)} if i else {"kind": "none", "t": 0})
        (HF / "compositions" / f"{sid}.html").write_text(sc.build(), encoding="utf-8")
        hosts.append((sid, TL[sid]["start"], TL[sid]["dur"]))
        print(f"{sid} {TL[sid]['start']:7.2f} +{TL[sid]['dur']:6.2f}  shots={sc.z}")
    off = hosts[0][1] if ONLY else 0
    total = (hosts[-1][1] + hosts[-1][2] - off) if ONLY else TOTAL
    host_html = "\n      ".join(
        f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{r2(st - off)}" data-duration="{r2(du)}" data-track-index="{k + 1}" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:{k + 1}"></div>'
        for k, (sid, st, du) in enumerate(hosts))
    audio = ""
    if (HF / "assets/audio/vo_en.wav").exists() and not ONLY:
        audio += f'\n      <audio id="vo" class="clip" src="assets/audio/vo_en.wav" data-start="0" data-duration="{r2(total)}" data-track-index="40" data-volume="1"></audio>'
    if (HF / "assets/audio/vo_test.wav").exists() and ONLY:
        audio += f'\n      <audio id="vo" class="clip" src="assets/audio/vo_test.wav" data-start="0" data-duration="{r2(total)}" data-track-index="40" data-volume="1"></audio>'
    if (HF / "assets/audio/music.wav").exists():
        audio += f'\n      <audio id="music" class="clip" src="assets/audio/music.wav" data-start="0" data-duration="{r2(total)}" data-track-index="41" data-volume="1"></audio>'
    if (HF / "assets/audio/sfx.wav").exists() and (not ONLY or ONLY == ["s01"]):
        audio += f'\n      <audio id="sfx" class="clip" src="assets/audio/sfx.wav" data-start="0" data-duration="{r2(total)}" data-track-index="42" data-volume="1"></audio>'
    (HF / "index.html").write_text(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="lib/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {GROUND}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{r2(total)}" data-width="1920" data-height="1080">
      {host_html}{audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")
    if not ONLY:
        json.dump({"total": TOTAL, "eras": [{"id": s, "era": SCENES[s][0], "start": TL[s]["start"], "dur": TL[s]["dur"]} for s in order], "fx": fx}, open(ROOT / "build/audio_plan.json", "w"), indent=1)
    print(f"total {total:.1f}s  ({total / 60:.2f} min)  estimated lines: {missing}")

if __name__ == "__main__":
    main()
