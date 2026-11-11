#!/usr/bin/env python3
"""Vertical Shorts (1080x1920), built from scratch rather than cropped from the long film.
Words stay inside the platform-safe band (168-1330 px). Usage: gen_short.py [s1|s2]"""
import json, html, sys, wave, shutil, subprocess, array, tempfile, os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
AMBER, CYAN, RED, INK, GROUND = "#e6a94e", "#56c8f5", "#ff4b3a", "#f3efe6", "#0a0b0e"
ERA = {"a": AMBER, "c": CYAN, "n": INK}
esc = html.escape
VO = ROOT / "assets/audio/vo_en"
GAP, LEAD, TAIL = 0.22, 0.12, 1.4

SHORTS = {
    "s1": {
        "title": "One night in 1943",
        "hook_text": ("ONE NIGHT.", "1943"),
        "beats": [
            ("sh_01", "In 1943, Army agents sat outside a woman's apartment all night. The man inside was building the atomic bomb.", {"v": "three", "kind": "street", "cam": [{"t": 0, "p": [-6.0, 1.5, 14.5], "l": [-1.8, 3.4, -4]}, {"t": 8, "p": [-5.4, 1.5, 10.5], "l": [-1.6, 3.9, -6]}], "era": "a", "tag": "SPRING 1943 · SAN FRANCISCO", "recon": True}),
            ("s01_04", "Eleven years later, that night was read back to him in a closed room in Washington. He lost.", {"v": "photo", "slug": "opp_congress53", "era": "a", "tag": "1954 · WASHINGTON, D.C.", "name": "J. ROBERT OPPENHEIMER"}),
            ("s08_05", "Then comes the night. You spent the night with her, didn't you?", {"v": "three", "kind": "room", "cam": [{"t": 0, "p": [2.6, 3.0, 5.6], "l": [0, 2.0, -5.5]}, {"t": 12, "p": [-0.4, 2.6, 2.6], "l": [0, 2.0, -6.3]}], "era": "a", "tag": "HEARING TRANSCRIPT · 1954", "recon": True, "span": 4}),
            ("s08_06", "Yes.", None),
            ("s08_07", "That is when you were working on a secret war project?", None),
            ("s08_08", "Yes.", None),
            ("s01_06", "Now the man who builds the chips behind American A.I. has admitted an affair with a woman U.S. intelligence believes was recruited by China.", {"v": "photo", "slug": "huang_stanford_a", "era": "c", "tag": "NOVEMBER 2026", "name": "JENSEN HUANG · CEO, NVIDIA", "note": "ALLEGATION REPORTED BY NYT, NBC · NO CHARGES"}),
            ("s01_07", "On November eighteenth, Congress wants him in a closed room too.", {"v": "three", "kind": "door", "cam": [{"t": 0, "p": [0, 2.9, 15], "l": [0, 3.0, 0]}, {"t": 5, "p": [0.4, 2.6, 9], "l": [0, 2.9, 0]}], "era": "c", "tag": "NOV. 18, 2026 · U.S. CONGRESS", "recon": True}),
            ("sh_02", "The last time America did this, it took sixty-eight years to take it back.", {"v": "big", "big": "68", "sub": "YEARS", "era": "a", "tag": "1954 → 2022"}),
        ],
    },
    "s2": {
        "title": "The verdict said he was loyal",
        "hook_text": ("7 DAYS.", "NO DEFENSE."),
        "beats": [
            ("sh_03", "In 1954, the prosecutor spent a week alone with the judges. Before the hearing even began.", {"v": "three", "kind": "room", "cam": [{"t": 0, "p": [6.5, 4.6, 7.5], "l": [0, 1.8, -4]}, {"t": 12, "p": [1.2, 2.7, 3.4], "l": [0, 2.0, -6]}], "era": "a", "tag": "APRIL 1954 · WASHINGTON, D.C.", "recon": True, "span": 3}),
            ("s07_06", "The defense was not in the room. The defense was never allowed to see those files at all.", None),
            ("s07_03", "The F.B.I. has bugged his lawyer's office.", None),
            ("s11_03", "It finds no evidence of disloyalty. It records his love of country. And it recommends that his clearance be taken anyway.", {"v": "paper", "era": "a", "tag": "THE VERDICT · MAY 27, 1954", "head": "PERSONNEL SECURITY BOARD · 1954", "lines": ["“no evidence of disloyalty”", "“…loyalty and love of country”", "Clearance: not reinstated."]}),
            ("s12_06", "Then, on December sixteenth, 2022, the Secretary of Energy formally vacated it.", {"v": "doc", "slug": "doe_order-2", "era": "n", "tag": "DEC. 16, 2022 · THE ACTUAL ORDER", "boxes": [(41.7, 62.7, 46.6, 2.1), (11.7, 64.6, 58.2, 2.1)], "focus": (50, 64)}),
            ("sh_04", "The man was Robert Oppenheimer. And America is about to ask the same question about the C.E.O. of Nvidia.", {"v": "split", "a": "opp_portrait", "b": "huang_stanford_a", "era": "n", "tag": "1954 | 2026"}),
        ],
    },
}

CSS = f"""
#root {{ position:absolute; inset:0; background:{GROUND}; overflow:hidden; font-family:'IBM Plex Mono',monospace; color:{INK}; }}
.shot, .in {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; }}
.fill {{ position:absolute; left:0; top:0; width:1080px; height:1920px; background:radial-gradient(ellipse at 30% 20%, #22252e 0%, #111318 40%, {GROUND} 80%); }}
.cv {{ position:absolute; left:0; top:0; width:1080px; height:1920px; }}
.shade {{ position:absolute; left:0; top:0; width:1080px; height:1920px; background:linear-gradient(180deg, rgba(10,11,14,.55) 0%, rgba(10,11,14,0) 22%, rgba(10,11,14,0) 50%, rgba(10,11,14,.72) 68%, rgba(10,11,14,.94) 100%); }}
.pbg {{ position:absolute; left:-200px; top:-100px; width:1480px; height:2120px; object-fit:cover; }}
.pcard {{ position:absolute; box-shadow:0 40px 90px rgba(0,0,0,.7), 0 0 0 10px #efe8d8; background:#111; }}
.pcard img {{ display:block; width:100%; height:100%; object-fit:cover; }}
.tag {{ position:absolute; left:64px; top:196px; font-size:30px; font-weight:700; letter-spacing:.12em; padding:10px 16px 9px; border-left:6px solid currentColor; background:rgba(10,11,14,.78); }}
.recon {{ position:absolute; left:64px; top:262px; font-size:28px; font-weight:700; letter-spacing:.14em; padding:6px 12px; color:rgba(243,239,230,.85); background:rgba(10,11,14,.7); }}
.cap {{ position:absolute; left:64px; top:1090px; width:952px; font-family:'Playfair Display',serif; font-weight:700; font-size:88px; line-height:1.08; text-align:center; text-shadow:0 4px 24px rgba(0,0,0,.95), 0 0 6px rgba(0,0,0,.9); }}
.cap .w {{ display:inline-block; white-space:pre; }}
.hook {{ position:absolute; left:64px; top:560px; width:952px; text-align:center; font-family:'Playfair Display',serif; font-weight:700; line-height:1.0; }}
.name {{ position:absolute; left:64px; width:952px; text-align:center; font-size:30px; font-weight:700; letter-spacing:.1em; }}
.paper {{ position:absolute; left:90px; top:330px; width:900px; background:#ece3cf; color:#1c1a16; box-shadow:0 50px 110px rgba(0,0,0,.7); padding:56px 60px; font-size:40px; line-height:1.45; }}
.paper .ph {{ font-size:28px; letter-spacing:.1em; color:#5a5346; border-bottom:2px solid #5a5346; padding-bottom:14px; margin-bottom:26px; font-weight:700; }}
.paper .pl {{ margin-bottom:18px; font-weight:700; }}
.bar {{ position:absolute; left:0; top:1880px; width:1080px; height:40px; }}
"""

def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()

def groups(text, n=3):
    ws = text.split(" ")
    out, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= n or w[-1] in ".?!,":
            if len(cur) >= 2 or w[-1] in ".?!":
                out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out

def build(key):
    S = SHORTS[key]
    hf = ROOT / f"hf_{key}"
    (hf / "compositions").mkdir(parents=True, exist_ok=True)
    (hf / "assets/audio").mkdir(parents=True, exist_ok=True)
    for d in ("lib",):
        if (hf / d).exists(): shutil.rmtree(hf / d)
        shutil.copytree(ROOT / "hf" / d, hf / d)
    if not (hf / "assets/img").exists():
        os.symlink(ROOT / "hf/assets/img", hf / "assets/img")
    for f in ("hyperframes.json", "package.json", "meta.json"):
        shutil.copy(ROOT / "hf" / f, hf / f)
    # timing
    t, T = LEAD, []
    for wid, text, vis in S["beats"]:
        p = VO / f"{wid}.wav"
        d = wav_dur(p) if p.exists() else max(0.7, len(text) / 15.5)
        T.append((t, t + d)); t += d + GAP
    total = t - GAP + TAIL
    h, js, z = [], [], [1]
    def clip(t0, t1, inner, fade=0.2):
        z[0] += 1; cid = f"{key}-c{z[0]}"
        t1 = min(total, t1 + 0.25)
        h.append(f'<div id="{cid}" class="clip shot" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{z[0]}" style="z-index:{z[0]}"><div class="in" id="{cid}-in">{inner}</div></div>')
        if fade and t0 > 0.05:
            js.append(f'tl.fromTo("#{cid}-in",{{opacity:0}},{{opacity:1,duration:{fade},ease:"power2.out"}},{t0:.3f});')
        return cid
    # visual shots: a beat with vis=None keeps the previous visual
    i = 0
    while i < len(S["beats"]):
        wid, text, vis = S["beats"][i]
        j = i + 1
        while j < len(S["beats"]) and S["beats"][j][2] is None:
            j += 1
        t0 = 0 if i == 0 else T[i][0] - 0.1
        t1 = (T[j][0] - 0.1) if j < len(S["beats"]) else total
        d = t1 - t0 + 0.3
        era = vis["era"]
        tag = f'<div class="tag" style="color:{ERA[era]}">{esc(vis["tag"])}</div>' + ('<div class="recon">3D RECONSTRUCTION</div>' if vis.get("recon") else "")
        bar = f'<div class="bar" style="background:{ERA[era]}" data-layout-ignore></div>'
        uid = f"{key}-v{i}"
        if vis["v"] == "three":
            cam = [dict(c) for c in vis["cam"]]; cam[-1]["t"] = d
            inner = f'<canvas class="cv" id="{uid}" width="810" height="1440"></canvas><div class="shade"></div>{tag}{bar}'
            js.append(f'(function(){{var dr=EM3D.{vis["kind"]}(document.getElementById("{uid}")),st={{t:0}},o={{cam:{json.dumps(cam)}}};var f=function(){{dr(st.t,o);}};tl.fromTo(st,{{t:0}},{{t:{d:.3f},duration:{d:.3f},ease:"none",onUpdate:f}},{t0:.3f});st.t=0;f();}})();')
        elif vis["v"] == "photo":
            w_, h_ = Image.open(ROOT / f"hf/assets/img/{vis['slug']}_g.jpg").size
            ph = 700; pw = min(880, ph * w_ / h_); ph = min(ph, pw * h_ / w_) if pw == 880 else ph
            x, y = (1080 - pw) / 2, 300
            nm = f'<div class="name" style="top:{y + ph + 28:.0f}px;color:{ERA[era]}">{esc(vis.get("name", ""))}</div>'
            if vis.get("note"):
                nm += f'<div class="name" style="top:1340px;font-size:28px;color:rgba(243,239,230,.8)" data-layout-allow-caption-zone>{esc(vis["note"])}</div>'
            inner = f'<img class="pbg" id="{uid}-bg" src="assets/img/{vis["slug"]}_bg.jpg" alt=""><div class="shade"></div><div class="pcard" id="{uid}" style="left:{x:.0f}px;top:{y}px;width:{pw:.0f}px;height:{ph:.0f}px"><img src="assets/img/{vis["slug"]}_g.jpg" alt="" style="object-position:50% 25%"></div>{nm}{tag}{bar}'
            js.append(f'tl.fromTo("#{uid}",{{rotationY:-6,scale:0.97,transformPerspective:1400}},{{rotationY:5,scale:1.05,duration:{d:.3f},ease:"sine.inOut"}},{t0:.3f});')
            js.append(f'tl.fromTo("#{uid}-bg",{{x:-30,scale:1.04}},{{x:30,scale:1.1,duration:{d:.3f},ease:"none"}},{t0:.3f});')
        elif vis["v"] == "big":
            inner = f'<div class="fill"></div><div class="hook" id="{uid}" style="top:380px;font-size:420px;color:{ERA[era]}">0</div><div class="name" style="top:800px;font-size:70px;color:{INK}">{esc(vis["sub"])}</div>{tag}{bar}'
            js.append(f'(function(){{var el=document.getElementById("{uid}"),o={{v:0}};var f=function(){{el.textContent=Math.round(o.v);}};tl.fromTo(o,{{v:0}},{{v:{vis["big"]},duration:1.5,ease:"power3.out",onUpdate:f}},{t0 + 1.4:.3f});f();}})();')
        elif vis["v"] == "paper":
            lines = "".join(f'<div class="pl" id="{uid}-l{k}">{esc(l)}</div>' for k, l in enumerate(vis["lines"]))
            inner = f'<div class="fill"></div><div class="paper" id="{uid}"><div class="ph">{esc(vis["head"])}</div>{lines}</div>{tag}{bar}'
            n = len(vis["lines"])
            for k in range(n):
                js.append(f'tl.fromTo("#{uid}-l{k}",{{opacity:0}},{{opacity:1,duration:0.25}},{t0 + 0.3 + k * (t1 - t0 - 1.5) / n:.3f});')
            js.append(f'tl.fromTo("#{uid}",{{rotationX:10,rotationY:-6,scale:0.95,transformPerspective:1500}},{{rotationX:0,rotationY:3,scale:1.02,duration:{d:.3f},ease:"sine.inOut"}},{t0:.3f});')
        elif vis["v"] == "doc":
            w_, h_ = Image.open(ROOT / f"hf/assets/img/{vis['slug']}_g.jpg").size
            pw = 900; ph = pw * h_ / w_
            fx, fy = vis["focus"]
            bars = ""
            for k, (bx, by, bw, bh) in enumerate(vis["boxes"]):
                bars += f'<div id="{uid}-h{k}" style="position:absolute;left:{bx}%;top:{by}%;width:{bw}%;height:{bh}%;background:rgba(255,75,58,.45);mix-blend-mode:multiply"></div>'
                js.append(f'tl.fromTo("#{uid}-h{k}",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:0.6,ease:"power2.out"}},{t0 + 2.2 + k * 0.8:.3f});')
            zf = 1.3
            dx, dy = 540 - (90 + pw / 2) - (fx - 50) / 100 * pw * zf, 640 - (90 + ph / 2) - (fy - 50) / 100 * ph * zf
            inner = f'<div class="fill" style="background:#14130f"></div><div id="{uid}" style="position:absolute;left:90px;top:90px;width:{pw}px;height:{ph:.0f}px;transform-origin:50% 50%;box-shadow:0 50px 120px rgba(0,0,0,.75)"><img src="assets/img/{vis["slug"]}_g.jpg" alt="" style="display:block;width:100%;height:100%">{bars}</div><div class="shade" style="background:linear-gradient(180deg, rgba(10,11,14,.6) 0%, rgba(10,11,14,0) 20%, rgba(10,11,14,0) 50%, rgba(10,11,14,.95) 56%, rgba(10,11,14,.98) 100%)"></div>{tag}{bar}'
            js.append(f'tl.fromTo("#{uid}",{{scale:0.9,x:0,y:60,rotationX:12,transformPerspective:1600}},{{scale:{zf},x:{dx:.0f},y:{dy:.0f},rotationX:0,duration:2.0,ease:"power2.inOut"}},{t0:.3f});')
        elif vis["v"] == "split":
            cards = ""
            for k, (slug, col, yy) in enumerate(((vis["a"], AMBER, 330), (vis["b"], CYAN, 700))):
                cards += f'<div class="pcard" id="{uid}-{k}" style="left:{140 + k * 320}px;top:{yy - k * 330}px;width:440px;height:560px;box-shadow:0 40px 90px rgba(0,0,0,.7), 0 0 0 8px {col}"><img src="assets/img/{slug}_g.jpg" alt="" style="object-position:50% 22%"></div>'
                js.append(f'tl.fromTo("#{uid}-{k}",{{rotationY:{8 - 16 * k},scale:0.95,transformPerspective:1400}},{{rotationY:{2 - 4 * k},scale:1.02,duration:{d:.3f},ease:"sine.inOut"}},{t0:.3f});')
            inner = f'<div class="fill"></div>{cards}{tag}{bar}'
        clip(t0, t1, inner)
        i = j
    # hook text: on frame 0, different words from the spoken line
    a, b = S["hook_text"]
    z[0] += 1
    h.append(f'<div id="{key}-hook" class="clip" data-start="0" data-duration="2.6" data-track-index="{z[0]}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:400"><div id="{key}-hook-in" style="position:absolute;left:0;top:0;width:1080px;height:1920px"><div class="hook" style="top:380px;font-size:150px;color:{INK}">{esc(a)}</div><div class="hook" style="top:540px;font-size:150px;color:{AMBER}">{esc(b)}</div></div></div>')
    js.append(f'tl.fromTo("#{key}-hook-in",{{opacity:1}},{{opacity:0,duration:0.25,ease:"power2.in"}},2.3);')
    # captions: one group at a time, inside the safe band
    for bi, (wid, text, vis) in enumerate(S["beats"]):
        t0, t1 = T[bi]
        gs = groups(text)
        tot = sum(len(g) for g in gs)
        cur = t0
        for gi, g in enumerate(gs):
            gd = (t1 - t0) * len(g) / tot
            st, en = max(cur, 2.35 if bi == 0 else 0), cur + gd + (0.12 if gi == len(gs) - 1 else 0)
            cur += gd
            if en - st < 0.2:
                continue
            gid = f"{key}-g{bi}-{gi}"
            z[0] += 1
            col = RED if g.strip() in ("Yes.", "He lost.") else INK
            size = 150 if g.strip() == "Yes." else 88
            h.append(f'<div id="{gid}" class="clip" data-start="{st:.3f}" data-duration="{en - st:.3f}" data-track-index="{z[0]}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:500"><div class="cap" id="{gid}-in" style="color:{col};font-size:{size}px">{esc(g)}</div></div>')
            js.append(f'tl.fromTo("#{gid}-in",{{opacity:0,scale:0.94}},{{opacity:1,scale:1,duration:0.12,ease:"power2.out"}},{st:.3f});')
    body, code = "\n    ".join(h), "\n      ".join(js)
    (hf / "compositions" / f"{key}.html").write_text(f"""<template>
  <style>{CSS}</style>
  <div id="root" data-composition-id="{key}" data-width="1080" data-height="1920">
    {body}
  </div>
  <script src="lib/em3d.js"></script>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {code}
      window.__timelines["{key}"] = tl;
    }})();
  </script>
</template>
""", encoding="utf-8")
    # audio: narration laid on the short's own timeline + a slice of the music bed
    SR = 24000
    buf = array.array("h", bytes(2 * int(total * SR) + 2))
    for (wid, text, vis), (t0, t1) in zip(S["beats"], T):
        p = VO / f"{wid}.wav"
        if not p.exists(): continue
        with wave.open(str(p)) as w:
            a = array.array("h"); a.frombytes(w.readframes(w.getnframes()))
        i0 = int(t0 * SR)
        for k in range(min(len(a), len(buf) - i0)):
            buf[i0 + k] = max(-32768, min(32767, buf[i0 + k] + a[k]))
    raw = tempfile.mktemp(suffix=".wav")
    with wave.open(raw, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(buf.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "highpass=f=70,loudnorm=I=-15:TP=-1.5:LRA=9", "-ar", "48000", "-ac", "2", str(hf / "assets/audio/vo.wav")], check=True)
    bed = "dark-suspense-underscore-3.wav" if key == "s1" else "dark-suspense-underscore-2.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "8", "-i", str(ROOT / "assets/audio/sfx" / bed), "-t", f"{total:.2f}", "-af", f"loudnorm=I=-27:TP=-3,afade=t=in:d=0.4,afade=t=out:st={total - 1.5:.2f}:d=1.5", "-ar", "48000", "-ac", "2", str(hf / "assets/audio/music.wav")], check=True)
    (hf / "index.html").write_text(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="lib/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {GROUND}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920">
      <div id="{key}" data-composition-id="{key}" data-composition-src="compositions/{key}.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="{total:.3f}" data-track-index="40" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/audio/music.wav" data-start="0" data-duration="{total:.3f}" data-track-index="41" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")
    print(key, f"{total:.1f}s", "missing audio:", [w for w, _, _ in S["beats"] if not (VO / f"{w}.wav").exists()])

for k in (sys.argv[1:] or list(SHORTS)):
    build(k)
