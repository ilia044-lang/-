"""Shot lists. Each function receives a Scene (see gen.py) and places shots against the narration line times:
sc.l(i) = start of line i, sc.e(i) = end of line i, sc.end(i) = start of the next line."""

def split_plate(sc, t0, t1, left, right, extra=""):
    """Two eras side by side: amber print on the left, cyan print on the right."""
    from gen import imsize
    parts = []
    for slug, x, era in ((left, 150, "a"), (right, 1050, "c")):
        if not imsize(slug):
            parts.append(f'<div style="position:absolute;left:{x}px;top:210px;width:720px;height:600px;border:2px solid rgba(243,239,230,.25)"></div>'); continue
        pid = sc.uid("p")
        parts.append(f'<div class="pcard" id="{pid}" style="left:{x}px;top:200px;width:720px;height:620px"><img src="assets/img/{slug}_g.jpg" alt="" style="object-position:50% 22%"></div>')
        rot = (6, 2) if era == "a" else (-6, -2)
        sc.tilt(pid, t0, t1 + 0.3, rot=rot, sc=(0.96, 1.02), rx=(1, 0))
    mid = sc.uid("m")
    sc.js.append(f'tl.fromTo("#{mid}",{{scaleY:0}},{{scaleY:1,duration:0.7,ease:"expo.out"}},{t0 + 0.15:.3f});')
    return sc.clip(t0, t1, '<div class="fill"></div>' + "".join(parts) + f'<div id="{mid}" class="bar" style="left:958px;top:150px;width:4px;height:720px;background:#f3efe6"></div>' + extra)

def s01(sc):
    l, e, end = sc.l, sc.e, sc.end
    # 1-3: the night (3D)
    cam = [
        {"t": 0, "p": [17, 10.5, 29], "l": [0, 4, -10]},
        {"t": l(2), "p": [6, 4.2, 17], "l": [0, 5.2, -11.8]},
        {"t": l(3), "p": [1.5, 2.3, 12], "l": [-2.6, 1.5, 5.2]},
        {"t": end(3) + 0.3, "p": [-7.2, 1.75, 8.4], "l": [0, 5.3, -11.8]},
    ]
    ex = fade_out(sc, sc.words("One night.", 0.0, 0.2, 96, 130, 1300, 150, cls="serif n") + sc.label("1943", 100, 300, 150, "serif a"), e(1) + 0.2)
    ex += sc.block(sc.label("ARMY INTELLIGENCE AGENTS · OUTSIDE UNTIL MORNING", 96, 0, 32, "mono n", 1500), l(3) + 0.3, 0, 960)
    sc.three(0, end(3), "street", cam, opts=f'{{fn:function(t){{return {{dawn:Math.max(0,(t-{l(3) + 1.5:.2f})/{(end(3) - l(3)):.2f})*0.55}};}}}}', extra=ex)
    sc.recon(0.6, end(3))
    sc.hud(l(2), end(3), "Spring 1943 · San Francisco", "a")
    # 4: the closed room
    ex = sc.words("Read back to him in a closed room.", l(4) + 1.2, l(4) + 3.2, 150, 330, 760, 62, cls="serif n")
    ex += sc.block(sc.label("HE LOST.", 0, 0, 170, "serif r", 800), e(4) - 0.75, 150, 560)
    sc.plate(l(4), end(4), "opp_congress53", side="right", name="J. ROBERT OPPENHEIMER", sub="Photographed in Washington, 1953", era="a", extra=ex)
    sc.hud(l(4), end(4), "April 1954 · Washington, D.C.", "a")
    # 5: 68 years
    ex = sc.counter(l(5) + 1.3, 0, 68, 150, 250, 400, "serif n", 900, dur=1.6)
    ex += sc.block(sc.label("YEARS", 0, 0, 90, "mono a", 800), l(5) + 2.7, 160, 690)
    ex += sc.words("to admit the process was rigged against him.", l(5) + 3.0, e(5), 160, 810, 900, 44, cls="serif dim")
    sc.plate(l(5), end(5), "doe_order-1", side="right", era="n", extra=ex, tilt=(-9, -3), credit=False)
    sc.src(l(5) + 0.5, end(5), "U.S. Secretary of Energy, order of Dec. 16, 2022")
    # 6: 2026
    ex = sc.words("“I was unfaithful to my wife.”", l(6) + 3.4, l(6) + 5.0, 1010, 300, 780, 78, cls="serif n")
    ex += sc.block(sc.label("JENSEN HUANG · MEMO TO NVIDIA STAFF · NOV. 8, 2026", 0, 0, 24, "mono c", 800), l(6) + 5.2, 1010, 590)
    ex += sc.block(sc.label("U.S. INTELLIGENCE BELIEVES THE WOMAN WAS RECRUITED BY CHINA. NO ONE HAS BEEN CHARGED.", 0, 0, 27, "mono n", 760), l(6) + 6.4, 1010, 690)
    sc.plate(l(6), end(6), "huang_stanford_a", side="left", name="JENSEN HUANG", sub="Founder and CEO, Nvidia · photo: April 2026", era="c", extra=ex, tilt=(5, -4))
    sc.hud(l(6), end(6), "November 2026", "c")
    sc.src(l(6) + 5.0, end(6), "Nvidia newsroom · New York Times · NBC News")
    # 7: the door
    cam = [{"t": 0, "p": [0, 2.6, 17], "l": [0, 2.5, 0]}, {"t": end(7) - l(7) + 0.4, "p": [0.8, 2.2, 8.2], "l": [0, 2.4, 0]}]
    ex = sc.block(sc.label("NOV 18", 0, 0, 190, "serif n", 1000), l(7) + 0.35, 110, 380)
    ex += sc.block(sc.label("CLOSED-DOOR BRIEFING REQUESTED · U.S. HOUSE", 0, 0, 30, "mono c", 1200), l(7) + 1.3, 120, 610)
    sc.three(l(7), end(7), "door", cam, extra=ex)
    sc.recon(l(7) + 0.3, end(7))
    # 8: the mirror
    ex = sc.words("What did America find the last time?", l(8) + 0.2, l(8) + 2.4, 160, 60, 1600, 58, cls="serif n", align="center")
    ex += sc.words("And why did it take it all back?", l(8) + 3.0, e(8) - 0.2, 160, 880, 1600, 58, cls="serif n", align="center")
    ex += sc.block(sc.label("1954", 0, 0, 40, "mono a", 300), l(8) + 0.5, 150, 838)
    ex += sc.block(sc.label("2026", 0, 0, 40, "mono c", 300, "right"), l(8) + 0.9, 1470, 838)
    split_plate(sc, l(8), sc.dur, "opp_portrait", "huang_stanford_a", ex)


def fade_out(sc, inner, t):
    """wrap html that is on from the start and leaves at t"""
    bid = sc.uid("f")
    sc.js.append(f'tl.fromTo("#{bid}",{{opacity:1}},{{opacity:0,duration:0.3,ease:"power2.in"}},{t:.3f});')
    return f'<div id="{bid}" style="position:absolute;left:0;top:0">{inner}</div>'

def title(sc, t0, t1, text, sub=None, era=None, size=120, t_sub=None, hi=None, y=None, span=None):
    """Full-frame statement on the ground colour."""
    era = era or sc.era
    yy = y if y is not None else (400 if sub else 440)
    ex = sc.words(text, t0 + 0.15, t0 + 0.15 + (span or min(2.2, (t1 - t0) * 0.5)), 160, yy, 1600, size, cls="serif n", align="center", hi=hi, hicls=era)
    if sub:
        ex += sc.block(sc.label(sub, 0, 0, 32, f"mono {era}", 1600, "center"), t_sub or (t0 + 1.2), 160, yy + size * 1.25 * (1 + (len(text) * size * 0.5 > 1600)) + 40)
    return sc.clip(t0, t1, '<div class="fill"></div>' + ex)

def doc_zoom(sc, t0, t1, slug, boxes, focus=(50, 50), zoom=(0.9, 1.9), extra="", w=820):
    """A real scanned page. Camera pushes toward `focus` (percent of page); boxes = [(left%, top%, width%, height%, time)] highlight bars."""
    from gen import imsize
    size = imsize(slug)
    if not size:
        return sc.clip(t0, t1, '<div class="fill"></div>' + extra)
    h = w * size[1] / size[0]
    pid = sc.uid("z")
    bars = ""
    for i, (bx, by, bw, bh, bt) in enumerate(boxes):
        bars += f'<div id="{pid}-h{i}" style="position:absolute;left:{bx}%;top:{by}%;width:{bw}%;height:{bh}%;background:rgba(255,75,58,.42);mix-blend-mode:multiply"></div>'
        sc.js.append(f'tl.fromTo("#{pid}-h{i}",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:0.6,ease:"power2.out"}},{bt:.3f});')
    x, y = (1920 - w) / 2, (1080 - h) / 2
    inner = (f'<div class="fill" style="background:#14130f"></div><div id="{pid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;height:{h:.0f}px;transform-origin:{focus[0]}% {focus[1]}%;box-shadow:0 50px 120px rgba(0,0,0,.75)">'
             f'<img src="assets/img/{slug}_g.jpg" alt="" style="display:block;width:100%;height:100%">{bars}</div><div class="shade" style="opacity:.55"></div>{extra}')
    # keep the focus point at frame centre when zoomed
    dx, dy = (50 - focus[0]) / 100 * w, (50 - focus[1]) / 100 * h
    d = t1 - t0 + 0.3
    sc.js.append(f'tl.fromTo("#{pid}",{{scale:{zoom[0]},x:0,y:0,rotationX:14,rotationY:-8,transformPerspective:1700}},{{scale:{zoom[1]},x:{dx * zoom[1]:.0f},y:{dy * zoom[1]:.0f},rotationX:0,rotationY:0,duration:{min(d, 3.2):.2f},ease:"power2.inOut"}},{t0:.3f});')
    if d > 3.4:
        sc.js.append(f'tl.to("#{pid}",{{scale:{zoom[1] * 1.06:.3f},duration:{d - 3.2:.2f},ease:"none"}},{t0 + 3.2:.3f});')
    return sc.clip(t0, t1, inner)

def ledger_rows(sc, rows, y0=250, gap=118, head=None):
    """rows = [(time, key, left, right)]"""
    out = ""
    if head:
        out += f'<div class="tx mono a" style="left:520px;top:{y0 - 78}px;width:600px;font-size:34px;left:360px">{head[0]}</div><div class="tx mono c" style="left:1010px;top:{y0 - 78}px;width:600px;font-size:34px">{head[1]}</div><div class="rule" style="left:160px;top:{y0 - 22}px;width:1600px"></div>'
    for i, (t, k, a, b) in enumerate(rows):
        rid = sc.uid("r")
        out += f'<div class="row" id="{rid}" style="top:{y0 + i * gap}px"><div class="k">{k}</div><div class="l">{a}</div><div class="rr">{b}</div></div>'
        sc.js.append(f'tl.fromTo("#{rid}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.5,ease:"expo.out"}},{t:.3f});')
    return out

def quote_plate(sc, t0, t1, slug, quote, who, era, tq0, tq1, side="left", size=64, name=None, sub=None, src=None, hi=None, focus="50% 25%"):
    tx = 1010 if side == "left" else 150
    ex = sc.words(quote, tq0, tq1, tx, 250, 770, size, cls="serif n", hi=hi, hicls=era)
    ex += sc.block(sc.label(who, 0, 0, 28, f"mono {era}", 770), tq1 + 0.2, tx, 800)
    sc.plate(t0, t1, slug, side=side, name=name, sub=sub, era=era, extra=ex, tilt=(5, -4) if side == "left" else (-5, 4), focus=focus)
    if src:
        sc.src(t0 + 0.6, t1, src)

# ------------------------------------------------------------------ S02 what is confirmed
def s02(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "November 2026 · Santa Clara", "c")
    title(sc, 0, end(1), "What is confirmed", era="c", size=130, hi={"confirmed"})
    # 2: the memo
    doc, pid = sc.paper("NVIDIA · A MESSAGE TO OUR COMPANY · NOV. 8, 2026", [
        ("From: Jensen Huang, founder and CEO", l(2) + 0.6, None),
        ("To: all employees", l(2) + 1.0, None),
        ("“[[I was unfaithful to my wife.]]”", l(2) + 4.6, l(2) + 5.4)], 180, 250, 900, size=34)
    sc.tilt(pid, l(2), end(2) + 0.3, rot=(7, 1), sc=(0.96, 1.03))
    ex = doc + sc.block(sc.label("SIX WORDS", 0, 0, 110, "serif n", 700), l(2) + 3.6, 1160, 380)
    ex += sc.block(sc.label("SUNDAY · NOV. 8, 2026", 0, 0, 32, "mono c", 700), l(2) + 0.4, 1166, 320)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(2), "Nvidia newsroom, “A Message to Our Company”")
    # 3: the board
    ex = sc.words("The board investigates its own founder.", l(3) + 1.0, e(3), 1010, 300, 770, 70, cls="serif n", hi={"founder."}, hicls="c")
    ex += sc.block(sc.label("INDEPENDENT INVESTIGATION · ANNOUNCED THE SAME DAY", 0, 0, 28, "mono c", 770), l(3) + 0.5, 1010, 240)
    sc.plate(l(3), end(3), "nvidia_hq", side="left", name="NVIDIA HEADQUARTERS", sub="Santa Clara, California", era="c", extra=ex, tilt=(5, -3))
    sc.src(l(3) + 0.5, end(3), "Statement from Nvidia Board of Directors, Nov. 8, 2026")
    # 4-5: who she is
    facts = [(l(4) + 1.7, "NO RELATION TO JENSEN HUANG"), (l(4) + 3.0, "CHINESE CITIZEN"), (l(4) + 4.6, "FORMER EXECUTIVE, MEGASPEED · SINGAPORE")]
    ex = sc.silhouette(190, 240, 560, "c") + sc.label("NO PHOTO SHOWN", 190, 818, 28, "mono dim", 420)
    ex += sc.words("Alice Huang", l(4) + 0.5, l(4) + 1.1, 720, 230, 1000, 120, cls="serif n")
    for i, (t, f) in enumerate(facts):
        ex += sc.block(sc.label(f, 0, 0, 34, "mono c", 1050), t, 726, 410 + i * 62)
    ex += sc.block(sc.counter(l(5) + 2.0, 0, 4.8, 0, 0, 150, "serif n", 1050, dur=1.5, pre="$", suf=" billion", dec=1), l(5) + 1.8, 720, 610)
    ex += sc.block(sc.label("NVIDIA EQUIPMENT BOUGHT BY MEGASPEED · AS REPORTED BY THE NEW YORK TIMES", 0, 0, 28, "mono dim", 1050), l(5) + 3.2, 726, 800)
    sc.clip(l(4), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(4) + 1.0, end(5), "Al Jazeera, Nov. 9 · CNBC, Nov. 9 · New York Times")
    # 6-8: not confirmed
    ex = sc.words("Not confirmed", l(6) + 0.2, l(6) + 1.0, 160, 150, 1600, 110, cls="serif n", hi={"not"}, hicls="r")
    rows = [(l(6) + 2.2, "THE CLAIM", "Recruited by Beijing", "An intelligence assessment"),
            (l(7) + 0.4, "REPORTED BY", "New York Times", "NBC News"),
            (l(7) + 3.2, "CRIMINAL CHARGES", "Against him: none", "Against her: none"),
            (l(8) + 0.3, "BEIJING", "“Baseless”", ""),
            (l(8) + 2.6, "NVIDIA BOARD", "“No reason to believe”", "secrets were compromised")]
    ex += ledger_rows(sc, rows, y0=330, gap=116).replace('class="l"', 'class="l" style="color:#f3efe6"').replace('class="rr"', 'class="rr" style="color:#f3efe6"')
    sc.clip(l(6), end(8), '<div class="fill"></div>' + ex)
    sc.src(l(6) + 2.0, end(8), "NBC News · Al Jazeera · Nvidia board statement")
    # 9: the sentence
    quote_plate(sc, l(9), sc.dur, "huang_stanford_b", "“…completely normal and not unusual.”", "JENSEN HUANG TO BLOOMBERG NEWS · OCTOBER 2026", "c", l(9) + 6.0, e(9), name="JENSEN HUANG", sub="Stanford University, April 30, 2026", src="Quoted by Fortune, Nov. 9, 2026", hi={"normal"})

# ------------------------------------------------------------------ S03 the stake
def s03(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, l(5), "Wall Street · November 2026", "c")
    title(sc, 0, end(1), "Why does a private affair shake a market?", era="c", size=96, hi={"market?"})
    ex = sc.words("“Jensen is not replaceable.”", l(2) + 0.4, l(2) + 2.0, 160, 200, 1600, 104, cls="serif n", align="center")
    ex += sc.block(sc.label("DAN IVES, WEDBUSH · NOV. 10, 2026", 0, 0, 30, "mono c", 1600, "center"), l(2) + 2.1, 160, 350)
    ex += sc.block(sc.label("−25% to −30%", 0, 0, 190, "serif r", 1600, "center"), l(2) + 3.6, 160, 480)
    ex += sc.block(sc.label("HIS ESTIMATE OF NVIDIA’S VALUE WITHOUT HUANG", 0, 0, 32, "mono n", 1600, "center"), l(2) + 4.4, 160, 730)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.6, end(2), "Yahoo Finance live coverage, Nov. 10, 2026")
    # 3: two red days
    bars = ""
    for i, (day, pct, hh, t) in enumerate((("MON · NOV. 9", "−4.3%", 258, l(3) + 0.6), ("TUE · NOV. 10", "−5.47%", 328, l(3) + 1.3))):
        bid = sc.uid("g")
        x = 220 + i * 330
        bars += f'<div class="bar" id="{bid}" style="left:{x}px;top:300px;width:240px;height:{hh}px;background:#ff4b3a"></div><div class="tx mono n" style="left:{x - 30}px;top:240px;width:300px;font-size:30px;text-align:center">{day}</div><div class="tx serif r" style="left:{x - 30}px;top:{310 + hh}px;width:300px;font-size:64px;text-align:center">{pct}</div>'
        sc.js.append(f'tl.fromTo("#{bid}",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,duration:0.7,ease:"power3.out"}},{t:.3f});')
    ex = bars + sc.block(sc.counter(l(3) + 3.4, 0, 500, 0, 0, 170, "serif n", 900, dur=1.5, pre="≈ $", suf="B"), l(3) + 3.2, 960, 330)
    ex += sc.block(sc.label("IN MARKET VALUE · TWO TRADING DAYS", 0, 0, 32, "mono c", 900), l(3) + 4.6, 966, 560)
    sc.clip(l(3), end(3), '<div class="fill"></div><div class="rule" style="left:160px;top:298px;width:720px"></div>' + ex)
    sc.src(l(3) + 0.5, end(3), "CNBC, Nov. 11 · NBC News, Nov. 10, 2026")
    ex = sc.words("Can he be trusted?", l(4) + 3.6, e(4), 1010, 330, 770, 96, cls="serif n", hi={"trusted?"}, hicls="c")
    sc.plate(l(4), end(4), "capitol", side="left", name="U.S. CAPITOL", sub="Washington, D.C.", era="c", extra=ex)
    ex = sc.words("America has asked this before.", l(5) + 0.1, l(5) + 2.0, 160, 380, 1600, 104, cls="serif n", align="center", hi={"before."}, hicls="a")
    ex += sc.block(sc.label("A DIFFERENT MAN", 0, 0, 36, "mono a", 780, "right"), l(5) + 3.2, 160, 620)
    ex += sc.block(sc.label("A DIFFERENT TECHNOLOGY", 0, 0, 36, "mono a", 780), l(5) + 4.4, 990, 620)
    sc.clip(l(5), sc.dur, '<div class="fill"></div>' + ex)

# ------------------------------------------------------------------ S04 the night
def s04(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "Spring 1943 · San Francisco", "a")
    ex = sc.words("The most secret project in American history.", l(1) + 3.8, e(1), 1010, 300, 770, 70, cls="serif n", hi={"secret"})
    sc.plate(0, end(1), "opp_portrait", side="left", name="J. ROBERT OPPENHEIMER", sub="Photographed c. 1944", era="a", extra=ex, tilt=(6, -3))
    facts = [(l(2) + 3.6, "HIS FIRST REAL LOVE"), (l(2) + 5.6, "MEMBER, COMMUNIST PARTY")]
    ex = sc.silhouette(190, 240, 560, "a") + sc.label("NO PHOTO SHOWN", 190, 818, 28, "mono dim", 420)
    ex += sc.words("Jean Tatlock", l(2) + 1.6, l(2) + 2.3, 720, 250, 1000, 120, cls="serif n")
    for i, (t, f) in enumerate(facts):
        ex += sc.block(sc.label(f, 0, 0, 36, "mono a", 1000), t, 726, 440 + i * 70)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 1.0, end(2), "PBS American Experience · AEC letter of charges, 1953")
    # 3-4: the watch (3D), night to dawn
    d = end(4) - l(3)
    cam = [{"t": 0, "p": [-9.5, 1.7, 9.5], "l": [0, 5.3, -11.8]}, {"t": d * 0.55, "p": [-0.5, 2.4, 13.5], "l": [-3, 1.4, 5]}, {"t": d + 0.4, "p": [6, 5.5, 18], "l": [-1, 3, -6]}]
    ex = sc.block(sc.label("AGENTS, ARMY INTELLIGENCE", 0, 0, 34, "mono n", 1200), l(3) + 4.2, 96, 890)
    ex += sc.block(sc.label("WATCHING UNTIL MORNING", 0, 0, 34, "mono a", 1200), l(3) + 5.6, 96, 940)
    ex += sc.block(sc.label("REPORT → F.B.I.", 0, 0, 120, "serif n", 1300), l(4) + 0.2, 96, 380)
    sc.three(l(3), end(4), "street", cam, opts=f'{{fn:function(t){{return {{dawn:Math.max(0,Math.min(1,(t-{d * 0.3:.2f})/{d * 0.6:.2f})),windowOff:{d * 0.62:.2f}}};}}}}', extra=ex)
    sc.recon(l(3) + 0.3, end(4))
    # 5-7
    ex = sc.words("Phone tap:", l(5) + 0.5, l(5) + 1.0, 160, 300, 1600, 90, cls="serif dim", align="center")
    ex += sc.block(sc.label("NOTHING FOUND", 0, 0, 170, "serif n", 1600, "center"), l(5) + 1.9, 160, 430)
    sc.clip(l(5), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(5) + 0.4, end(6), "PBS American Experience, “The Trials of J. Robert Oppenheimer”")
    ex = sc.silhouette(190, 240, 560, "a") + sc.label("JEAN TATLOCK · DIED JANUARY 1944", 190, 818, 28, "mono dim", 700)
    ex += sc.words("Never shown to have passed a single secret.", l(6) + 3.4, e(6), 720, 300, 1040, 84, cls="serif n", hi={"never"})
    sc.clip(l(6), end(6), '<div class="fill"></div>' + ex)
    ex = sc.words("The file stays open.", l(7), e(7), 160, 400, 1600, 130, cls="serif n", align="center", hi={"open."})
    sc.clip(l(7), sc.dur, '<div class="fill"></div>' + ex)

# ------------------------------------------------------------------ S05 the charges
def s05(sc):
    l, e, end = sc.l, sc.e, sc.end
    ex = sc.words("The most famous scientist in America.", l(1) + 4.0, e(1), 1010, 320, 770, 72, cls="serif n", hi={"famous"})
    sc.plate(0, end(1), "opp_groves_trinity", side="left", name="OPPENHEIMER AND GEN. LESLIE GROVES", sub="Trinity test site, September 1945", era="a", extra=ex, tilt=(6, -3))
    sc.hud(0.5, end(1), "1945 · New Mexico", "a")
    ex = sc.words("He argues against the crash program.", l(2) + 3.0, e(2), 150, 320, 770, 72, cls="serif n", hi={"against"})
    sc.plate(l(2), end(2), "ivymike", side="right", name="HYDROGEN BOMB TEST “IVY MIKE”", sub="Enewetak Atoll, Nov. 1, 1952", era="a", extra=ex)
    sc.hud(l(2), end(2), "1949–1952 · The hydrogen bomb", "a")
    doc, pid = sc.paper("LETTER · NOVEMBER 7, 1953", [
        ("From: William L. Borden", l(3) + 2.4, None),
        ("To: J. Edgar Hoover, Director, F.B.I.", l(3) + 5.0, None),
        ("“[[More probably than not]], J. Robert Oppenheimer is [[an agent of the Soviet Union]].”", l(4) + 0.3, l(4) + 1.0)], 180, 240, 980, size=36)
    sc.tilt(pid, l(3), end(4) + 0.3, rot=(8, 0), sc=(0.95, 1.04))
    ex = doc + sc.block(sc.label("HIS CONCLUSION", 0, 0, 34, "mono a", 600), l(4) + 0.1, 1250, 420)
    sc.clip(l(3), end(4), '<div class="fill"></div>' + ex)
    sc.hud(l(3), end(4), "November 1953 · Washington, D.C.", "a")
    sc.src(l(3) + 1.0, end(4), "Atomic Heritage Foundation · typeset excerpt")
    ex = sc.block(sc.label("DEC. 21, 1953", 0, 0, 34, "mono a", 770), l(5) + 0.3, 1010, 250)
    ex += sc.words("Clearance suspended.", l(5) + 5.6, l(5) + 6.8, 1010, 320, 770, 92, cls="serif n", hi={"suspended."}, hicls="r")
    ex += sc.block(sc.label("RESIGN QUIETLY — OR FIGHT", 0, 0, 36, "mono n", 770), l(5) + 8.4, 1010, 600)
    sc.plate(l(5), end(5), "strauss_portrait", side="left", name="LEWIS L. STRAUSS", sub="Chairman, Atomic Energy Commission", era="a", extra=ex, tilt=(5, -4))
    sc.hud(l(5), end(5), "December 1953 · Washington, D.C.", "a")
    ex = sc.block(sc.counter(l(6) + 2.9, 0, 24, 0, 0, 420, "serif n", 800, dur=1.2), l(6) + 2.7, 200, 230)
    ex += sc.block(sc.label("CHARGES", 0, 0, 100, "mono a", 900), l(6) + 3.6, 840, 400)
    ex += sc.block(sc.label("DEC. 23, 1953", 0, 0, 36, "mono n", 900), l(6) + 1.3, 846, 330)
    sc.clip(l(6), end(6), '<div class="fill"></div>' + ex)
    doc, pid = sc.paper("U.S. ATOMIC ENERGY COMMISSION · K. D. NICHOLS TO J. R. OPPENHEIMER · DEC. 23, 1953", [
        ("It was reported that in 1943 and previously you were", l(7) + 0.4, None),
        ("“[[intimately associated with Dr. Jean Tatlock]],", l(7) + 0.4, l(7) + 5.0),
        ("a member of the Communist Party in San Francisco.”", l(7) + 0.4, None)], 300, 290, 1320, size=38)
    sc.tilt(pid, l(7), sc.dur, rot=(-6, 2), sc=(0.94, 1.05))
    sc.clip(l(7), sc.dur, '<div class="fill"></div>' + doc)
    sc.src(l(7) + 0.6, sc.dur - 0.4, "AEC letter of charges, Dec. 23, 1953 · typeset excerpt")

# ------------------------------------------------------------------ S06 mirror one
def s06(sc):
    l, e, end = sc.l, sc.e, sc.end
    title(sc, 0, end(1), "Now: 2026", era="c", size=170, hi={"2026"})
    sc.hud(l(2), sc.dur - 0.4, "Spring 2026 · Washington, D.C.", "c")
    red = "".join(f'<div style="height:30px;width:{w}%;background:#1c1a16;margin-bottom:16px"></div>' for w in (92, 78, 96, 60))
    doc, pid = sc.paper("CLASSIFIED MEMO · AS DESCRIBED IN PRESS REPORTS · NOT THE ACTUAL DOCUMENT", [
        ("Subject: the relationship of Nvidia’s chief executive", l(2) + 3.0, None),
        ("Circulated inside the administration, spring 2026", l(2) + 6.0, None),
        ("Basis: [[surveillance of Alice Huang]] (reported)", l(3) + 0.2, l(3) + 0.9)], 180, 220, 1020, size=34)
    doc = doc.replace("</div></div>", f'</div><div style="margin-top:26px">{red}</div></div>', 1) if False else doc
    sc.tilt(pid, l(2), end(3) + 0.3, rot=(8, 1), sc=(0.95, 1.03))
    ex = doc + sc.block(sc.label("REPORTED", 0, 0, 96, "serif c", 600), l(2) + 0.5, 1260, 380)
    ex += sc.block(sc.label("NOT INDEPENDENTLY CONFIRMED", 0, 0, 30, "mono n", 600), l(2) + 1.6, 1264, 510)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(3), "New York Times · Axios, Nov. 10, 2026")
    ex = sc.words("“…warned the president directly.”", l(4) + 5.0, e(4), 1010, 300, 770, 72, cls="serif n", hi={"warned"}, hicls="c")
    ex += sc.block(sc.label("AS REPORTED · MAY 2026 · EN ROUTE TO BEIJING", 0, 0, 30, "mono c", 770), l(4) + 2.2, 1010, 230)
    sc.plate(l(4), end(4), "airforceone", side="left", name="AIR FORCE ONE", sub="File photo, U.S. Air Force", era="c", extra=ex)
    sc.src(l(4) + 0.8, end(5), "New York Times, as relayed by NBC News and Axios")
    ex = sc.words("“It didn’t make much of an impact on me.”", l(5) + 2.6, e(5), 150, 300, 770, 72, cls="serif n")
    ex += sc.block(sc.label("PRESIDENT TRUMP · NOV. 9, 2026", 0, 0, 30, "mono c", 770), e(5), 150, 640)
    sc.plate(l(5), end(5), "rubio", side="right", name="MARCO RUBIO", sub="Secretary of State · official portrait", era="c", extra=ex)
    ex = ledger_rows(sc, [(l(6) + 0.3, "THE FILE", "Army surveillance report", "Classified memo (reported)"),
                          (l(6) + 1.6, "WRITTEN", "1943", "Spring 2026"),
                          (l(6) + 2.9, "MADE PUBLIC", "1954", "November 2026")], y0=420, gap=130, head=("OPPENHEIMER", "HUANG"))
    ex += sc.words("The file came first.", l(6) + 3.2, e(6), 160, 150, 1600, 100, cls="serif n", align="center")
    sc.clip(l(6), sc.dur, '<div class="fill"></div>' + ex)

# ------------------------------------------------------------------ S07 the rigged room
def s07(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April 12, 1954 · Washington, D.C.", "a")
    d = end(2)
    cam = [{"t": 0, "p": [9, 5.6, 9.5], "l": [0, 1.6, -3]}, {"t": l(2), "p": [2.5, 2.6, 6.5], "l": [0, 1.8, -4.5]}, {"t": d + 0.4, "p": [0.4, 2.2, 2.4], "l": [0, 2.1, -6.3]}]
    ex = sc.block(sc.label("NO PRESS. NO PUBLIC.", 0, 0, 100, "serif n", 1500), l(1) + 9.2, 96, 780)
    ex = fade_out(sc, ex, end(1) - 0.2)
    ex += sc.block(sc.label("WHAT HE DOES NOT KNOW", 0, 0, 100, "serif a", 1700), l(2) + 3.6, 96, 780)
    sc.three(0, end(2), "room", cam, extra=ex)
    sc.recon(0.6, end(2))
    ex = sc.words("The F.B.I. has bugged his lawyer’s office.", l(3) + 0.1, e(3), 160, 180, 1600, 92, cls="serif n", align="center", hi={"bugged"}, hicls="r")
    ex += sc.block(sc.counter(l(4) + 1.2, 0, 273, 0, 0, 330, "serif n", 1600, "center", dur=1.5), l(4) + 1.0, 160, 400)
    ex += sc.block(sc.label("WIRETAP REPORTS READ BY THE PROSECUTION — AT LEAST", 0, 0, 34, "mono a", 1600, "center"), l(4) + 2.8, 160, 790)
    ex += sc.block(sc.label("INCLUDING HIS CALLS WITH HIS OWN ATTORNEYS", 0, 0, 34, "mono n", 1600, "center"), l(4) + 5.4, 160, 850)
    sc.clip(l(3), end(4), '<div class="fill"></div>' + ex)
    sc.src(l(3) + 0.6, end(4), "Atomic Heritage Foundation · PBS American Experience")
    # 5-6: the week
    days = ""
    for i in range(7):
        did = sc.uid("k")
        days += f'<div id="{did}" style="position:absolute;left:{200 + i * 220}px;top:330px;width:190px;height:190px;border:3px solid #e6a94e;background:rgba(230,169,78,.14)"><div class="tx mono a" style="left:14px;top:10px;width:160px;font-size:28px">DAY {i + 1}</div></div>'
        sc.js.append(f'tl.fromTo("#{did}",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(1.4)"}},{l(5) + 0.6 + i * 0.28:.3f});')
    ex = days + sc.words("One week. Prosecutor and judges. Alone with the F.B.I. files.", l(5) + 3.2, e(5), 160, 590, 1600, 64, cls="serif n", align="center", hi={"alone"})
    ex += sc.block(sc.label("ROGER ROBB + THE THREE-MAN BOARD", 0, 0, 34, "mono a", 1600, "center"), l(5) + 2.2, 160, 250)
    ex += sc.block(sc.label("THE DEFENSE: NOT IN THE ROOM", 0, 0, 72, "serif r", 1600, "center"), l(6) + 0.2, 160, 800)
    sc.clip(l(5), sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(5) + 0.8, sc.dur - 0.4, "U.S. Secretary of Energy, order of Dec. 16, 2022")

# ------------------------------------------------------------------ S08 cross-examination
def s08(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April 1954 · The witness chair", "a")
    d = end(3)
    cam = [{"t": 0, "p": [3.4, 3.2, 6.4], "l": [0, 2.0, -5.5]}, {"t": d * 0.6, "p": [0.9, 2.7, 3.6], "l": [0, 2.0, -6]}, {"t": d + 0.4, "p": [-0.5, 2.55, 2.5], "l": [0, 2.0, -6.3]}]
    ex = sc.block(sc.counter(0.5, 0, 27, 0, 0, 300, "serif n", 700, dur=1.4), 0.3, 96, 560)
    ex += sc.block(sc.label("HOURS OF TESTIMONY", 0, 0, 40, "mono a", 900), 1.6, 520, 760)
    ex = fade_out(sc, ex, end(1) - 0.1)
    ex += sc.block(sc.label("A SECRET RECORDING · 1943", 0, 0, 84, "serif n", 1700), l(2) + 0.8, 96, 800)
    sc.three(0, end(3), "room", cam, opts="{dim:0.5}", extra=ex)
    sc.recon(0.6, end(3))
    ex = sc.label("Q. WHY DID YOU DO THAT, DOCTOR?", 160, 250, 40, "mono a", 1600, "center")
    ex += sc.words("“Because I was an idiot.”", l(4) + 2.6, e(4), 100, 380, 1720, 170, cls="serif n", align="center", hi={"idiot.”"}, hicls="r")
    sc.clip(l(4), end(4), '<div class="fill"></div>' + ex)
    sc.src(l(4) + 0.5, end(4), "Hearing transcript, 1954, as quoted by PBS American Experience")
    qa = [("Q.", "You spent the night with her, didn’t you?", l(5) + 1.2, e(5)), ("A.", "Yes.", l(6), e(6)),
          ("Q.", "That is when you were working on a secret war project?", l(7), e(7)), ("A.", "Yes.", l(8), e(8))]
    ex = sc.label("TRANSCRIPT · IN THE MATTER OF J. ROBERT OPPENHEIMER · 1954", 160, 150, 30, "mono a", 1600)
    y = 250
    for who, text, ta, tb in qa:
        big = who == "A."
        ex += sc.block(sc.label(who, 0, 0, 60, "mono a" if not big else "mono r", 120), ta, 160, y + 6)
        ex += sc.words(text, ta + 0.05, tb, 290, y, 1450, 110 if big else 64, cls="serif n")
        y += 150 if big else (190 if len(text) > 45 else 110)
    sc.clip(l(5), sc.dur, '<div class="fill"></div><div class="rule" style="left:160px;top:210px;width:1600px"></div>' + ex)
    sc.src(l(5) + 0.5, sc.dur - 0.4, "Hearing transcript, 1954, as quoted by PBS American Experience")

# ------------------------------------------------------------------ S09 mirror two
def s09(sc):
    l, e, end = sc.l, sc.e, sc.end
    sid = sc.uid("x")
    ex = sc.label("1954", 150, 150, 44, "mono a", 700) + sc.label("2026", 1070, 150, 44, "mono c", 700)
    ex += sc.words("“Because I was an idiot.”", l(1) + 1.2, l(1) + 2.6, 150, 290, 720, 78, cls="serif a")
    ex += f'<div id="{sid}" style="position:absolute;left:1070px;top:290px;width:720px">' + sc.words("“Completely normal and not unusual.”", l(2) + 0.3, l(2) + 1.9, 0, 0, 720, 78, cls="serif c") + f'<div id="{sid}-s" class="bar" style="left:0;top:138px;width:720px;height:8px;background:#ff4b3a"></div></div>'
    sc.js.append(f'tl.fromTo("#{sid}-s",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:0.45,ease:"power3.out"}},{l(2) + 2.6:.3f});')
    sc.js.append(f'tl.to("#{sid}",{{opacity:0.45,duration:0.3}},{l(2) + 2.7:.3f});')
    ex += sc.words("“I was unfaithful to my wife.”", l(2) + 3.0, e(2), 1070, 610, 720, 78, cls="serif n")
    ex += sc.block(sc.label("WEEKS APART", 0, 0, 32, "mono c", 720), e(2), 1070, 830)
    ex += sc.block(sc.label("THE GAP IS WHAT GETS INVESTIGATED", 0, 0, 44, "mono n", 1620, "center"), l(3) + 1.6, 150, 930)
    ex += f'<div class="bar" style="left:958px;top:150px;width:4px;height:720px;background:#f3efe6"></div>'
    sc.clip(0, sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(3) + 0.3, sc.dur - 0.4, "Fortune, Nov. 9, 2026")

# ------------------------------------------------------------------ S10 witnesses
def s10(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April–May 1954 · Witnesses", "a")
    quote_plate(sc, 0, end(2), "rabi", "“We have an A-bomb and a whole series of it, and what more do you want, mermaids?”", "ISIDOR I. RABI · NOBEL LAUREATE IN PHYSICS", "a", l(2), e(2), name="I. I. RABI", sub="Nobel Prize portrait, 1944", src="AEC hearing transcript, 1954", hi={"mermaids?”"}, size=60)
    quote_plate(sc, l(3), sc.dur, "teller58", "“I would feel personally more secure if public matters would rest in other hands.”", "EDWARD TELLER · APRIL 28, 1954", "a", l(4), e(4), side="right", name="EDWARD TELLER", sub="Photographed in 1958", src="AEC hearing transcript, 1954", hi={"other", "hands.”"}, size=60)

# ------------------------------------------------------------------ S11 the verdict
def tally(sc, t, a, b, la, lb, x=160, y=300):
    ex = sc.block(sc.label(f"{a}", 0, 0, 380, "serif r", 500, "right"), t, x, y)
    ex += sc.block(sc.label("–", 0, 0, 300, "serif dim", 300, "center"), t + 0.15, x + 520, y + 40)
    ex += sc.block(sc.label(f"{b}", 0, 0, 380, "serif n", 500), t + 0.3, x + 840, y)
    ex += sc.block(sc.label(la, 0, 0, 34, "mono r", 500, "right"), t + 0.5, x, y + 430)
    ex += sc.block(sc.label(lb, 0, 0, 34, "mono n", 500), t + 0.6, x + 840, y + 430)
    return ex

def s11(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, l(4), "May 27, 1954 · The board’s verdict", "a")
    ex = tally(sc, l(1) + 1.6, 2, 1, "AGAINST HIM", "FOR HIM", x=260, y=250)
    sc.clip(0, end(1), '<div class="fill"></div>' + ex)
    doc, pid = sc.paper("PERSONNEL SECURITY BOARD · FINDINGS AND RECOMMENDATION · MAY 27, 1954", [
        ("“[[no evidence of disloyalty]]”", l(3) + 0.1, l(3) + 0.9),
        ("“much responsible and positive evidence of the loyalty and [[love of country]]”", l(3) + 2.6, l(3) + 3.4),
        ("Recommendation: clearance [[not reinstated]].", l(3) + 5.4, l(3) + 6.6)], 150, 230, 1060, size=38)
    sc.tilt(pid, l(2), end(3) + 0.3, rot=(8, 0), sc=(0.94, 1.04))
    ex = doc + sc.words("Read it slowly.", l(2) + 0.2, l(2) + 1.3, 1290, 330, 560, 84, cls="serif n")
    ex += sc.block(sc.label("LOYAL.", 0, 0, 110, "serif a", 600), l(3) + 3.6, 1290, 560)
    ex += sc.block(sc.label("REMOVED ANYWAY.", 0, 0, 60, "serif r", 620), l(3) + 6.8, 1290, 700)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.6, end(3), "Board findings, May 27, 1954, quoted in the 2022 Energy Department order")
    sc.hud(l(4), sc.dur - 0.4, "June 29, 1954 · Atomic Energy Commission", "a")
    ex = tally(sc, l(4) + 2.4, 4, 1, "TO DENY CLEARANCE", "HENRY D. SMYTH, DISSENTING", x=260, y=250)
    sc.clip(l(4), end(4), '<div class="fill"></div>' + ex)
    ex = sc.label("NOT FOR LEAKING. NOT FOR SPYING.", 160, 260, 44, "mono a", 1600, "center")
    ex += sc.words("“fundamental defects” in his character", l(5) + 2.6, e(5), 160, 400, 1600, 110, cls="serif n", align="center", hi={"“fundamental", "defects”"}, hicls="r")
    sc.clip(l(5), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(5) + 0.5, sc.dur - 0.4, "AEC decision, June 29, 1954 · 2022 Energy Department order")
    cal = ""
    for i, (day, lab, t, hot) in enumerate((("JUNE 29", "THE RULING", l(6) + 0.2, True), ("JUNE 30", "", l(6) + 1.0, False), ("JULY 1", "CONTRACT EXPIRES", l(6) + 1.6, False))):
        cid = sc.uid("k")
        col = "#ff4b3a" if hot else "#e6a94e"
        cal += f'<div id="{cid}" style="position:absolute;left:{330 + i * 430}px;top:270px;width:380px;height:380px;border:4px solid {col};background:rgba(243,239,230,.05)"><div class="tx mono" style="left:26px;top:22px;width:330px;font-size:50px;color:{col}">{day}</div><div class="tx mono n" style="left:26px;top:270px;width:330px;font-size:30px">{lab}</div></div>'
        sc.js.append(f'tl.fromTo("#{cid}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.5,ease:"expo.out"}},{t:.3f});')
    ex = cal + sc.words("They could have let it run out. They ruled anyway.", l(6) + 3.4, e(6), 160, 740, 1600, 76, cls="serif n", align="center", hi={"anyway."}, hicls="r")
    sc.clip(l(6), sc.dur, '<div class="fill"></div>' + ex)

# ------------------------------------------------------------------ S12 the turn
def s12(sc):
    l, e, end = sc.l, sc.e, sc.end
    title(sc, 0, end(1), "So, was America safer?", era="a", size=130, hi={"safer?"})
    ex = sc.block(sc.counter(l(2) + 5.6, 300, 70000, 0, 0, 330, "serif n", 1600, "center", dur=2.6), l(2) + 0.5, 160, 300)
    ex += sc.block(sc.label("U.S. NUCLEAR WEAPONS · 1954", 0, 0, 38, "mono a", 1600, "center"), l(2) + 0.8, 160, 240)
    ex += sc.block(sc.label("BUILT IN THE DECADES THAT FOLLOWED", 0, 0, 38, "mono n", 1600, "center"), l(2) + 7.4, 160, 700)
    ex += sc.block(sc.label("“THE STRONGEST VOICE FOR RESTRAINT” — SILENCED", 0, 0, 38, "mono a", 1600, "center"), l(3) + 1.0, 160, 800)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(3), "PBS American Experience, “The Trials of J. Robert Oppenheimer”")
    doc, pid = sc.paper("INTERNAL REVIEW FOR THE AEC GENERAL COUNSEL · SEPT. 9, 1959", [
        ("“[[the system failed]] …", l(4) + 5.2, l(4) + 5.9),
        ("a [[substantial injustice]] was done", l(4) + 7.0, l(4) + 7.8),
        ("to [[a loyal American]].”", l(4) + 7.0, l(4) + 9.4)], 420, 260, 1080, size=50)
    sc.tilt(pid, l(4), end(4) + 0.3, rot=(-7, 1), sc=(0.94, 1.05))
    sc.clip(l(4), end(4), '<div class="fill"></div>' + doc)
    sc.hud(l(4), end(4), "1959 · Inside the commission", "a")
    sc.src(l(4) + 0.6, end(4), "1959 memo, quoted in the 2022 Energy Department order")
    ex = sc.block(sc.label("DEC. 2, 1963", 0, 0, 34, "mono a", 770), l(5) + 0.3, 1010, 260)
    ex += sc.words("The Fermi Award.", l(5) + 2.4, l(5) + 3.4, 1010, 320, 770, 88, cls="serif n")
    ex += sc.block(sc.label("HE DIED IN 1967. THE VERDICT STOOD.", 0, 0, 40, "mono n", 770), l(5) + 5.6, 1010, 620)
    sc.plate(l(5), end(5), "fermi63_a", side="left", name="OPPENHEIMER AND PRESIDENT JOHNSON", sub="The White House, Dec. 2, 1963", era="a", extra=ex, tilt=(5, -3))
    sc.hud(l(5), end(5), "1963 · The White House", "a")
    # 6-8: the real order
    sc.hud(l(6), sc.dur - 0.4, "December 16, 2022 · U.S. Department of Energy", "n")
    ex = sc.block(sc.label("VACATED", 0, 0, 150, "serif n", 800), l(6) + 3.8, 1080, 380)
    ex += sc.block(sc.label("AFTER 68 YEARS", 0, 0, 44, "mono a", 800), l(6) + 4.6, 1086, 580)
    doc_zoom(sc, l(6), end(6), "doe_order-1", [(30, 21.3, 58, 3.4, l(6) + 2.4)], focus=(50, 22), zoom=(0.7, 1.02), extra=ex, w=820)
    ex = sc.block(sc.label("“a flawed process that violated the Commission’s own regulations”", 0, 0, 48, "serif n", 1500, "center"), l(7) + 0.6, 210, 800)
    title(sc, l(7), end(7), "The process was flawed.", era="n", size=120, hi={"flawed."}, y=300)
    sc.src(l(7) + 0.4, end(7), "Statement of Secretary Jennifer Granholm, Dec. 16, 2022")
    doc_zoom(sc, l(8), end(8), "doe_order-2", [(41.7, 62.7, 46.6, 2.1, l(8) + 5.6), (11.7, 64.6, 58.2, 2.1, l(8) + 6.6)], focus=(45, 64), zoom=(0.8, 2.25), w=820)
    sc.src(l(8) + 0.5, end(8), "The actual order, page 2 · U.S. Department of Energy")
    ex = sc.words("The private life was the tool.", l(9) + 2.6, l(9) + 4.4, 160, 300, 1600, 110, cls="serif n", align="center", hi={"tool."})
    ex += sc.words("The policy was the target.", l(9) + 4.9, e(9), 160, 520, 1600, 110, cls="serif n", align="center", hi={"target."}, hicls="r")
    sc.clip(l(9), sc.dur, '<div class="fill"></div>' + ex)

# ------------------------------------------------------------------ S13 the policy fight
def s13(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "2022–2026 · The chip war", "c")
    d = end(2)
    cam = [{"t": 0, "p": [13, 9, 15], "l": [0, 0.4, 0]}, {"t": d * 0.5, "p": [7, 5.5, 8], "l": [0, 0.5, 0]}, {"t": d + 0.4, "p": [3.4, 3.4, 4.6], "l": [0, 0.5, 0]}]
    ex = sc.words("How many chips should America sell to China?", l(2) + 3.2, e(2), 96, 760, 1500, 84, cls="serif n", hi={"china?"}, hicls="c")
    sc.three(0, end(2), "chip", cam, extra=ex)
    sc.recon(0.6, end(2))
    ex = sc.block(sc.label("DECEMBER 2025", 0, 0, 34, "mono c", 770), l(3) + 4.0, 1010, 260)
    ex += sc.words("H200 sales to China: allowed.", l(3) + 5.2, e(3), 1010, 320, 770, 84, cls="serif n", hi={"allowed."}, hicls="c")
    sc.plate(l(3), end(3), "huang_stanford_c", side="left", name="JENSEN HUANG", sub="Stanford University, April 30, 2026", era="c", extra=ex, tilt=(5, -3))
    sc.src(l(3) + 0.6, end(3), "Al Jazeera, Nov. 9, 2026 · CNBC")
    ex = sc.words("Both parties want limits.", l(4) + 0.2, e(4), 150, 300, 770, 88, cls="serif n", hi={"limits."}, hicls="c")
    ex += sc.block(sc.label("DAYS AFTER THE ADMISSION: SEN. WARREN URGES CONGRESS TO PASS THEM", 0, 0, 34, "mono n", 770), l(5) + 0.4, 150, 580)
    sc.plate(l(4), l(5) + 5.4, "capitol", side="right", name="U.S. CAPITOL", sub="Washington, D.C.", era="c", extra=ex)
    title(sc, l(5) + 5.4, sc.dur, "The fight had a new weapon.", era="c", size=120, hi={"weapon."})

# ------------------------------------------------------------------ S14 the differences
def s14(sc):
    l, e, end = sc.l, sc.e, sc.end
    ex = sc.words("The differences are real.", l(1) + 2.6, e(1), 160, 60, 1600, 84, cls="serif n", align="center")
    rows = [(l(2), "STATUS", "Government clearance", "CEO of a private company"),
            (l(3), "SECRETS LOST", "None ever claimed", "Not known yet"),
            (l(5), "THE WOMAN", "Never shown to be a spy", "An untested assessment"),
            (l(5) + 5.0, "TESTED IN COURT", "No", "No"),
            (l(6), "WHAT IT NEEDS", "Evidence", "Evidence")]
    ex += ledger_rows(sc, rows, y0=330, gap=122, head=("1954 · OPPENHEIMER", "2026 · HUANG"))
    sc.clip(0, sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(2), sc.dur - 0.4, "2022 Energy Department order · NBC News · Al Jazeera")

# ------------------------------------------------------------------ S15 the test
def s15(sc):
    l, e, end = sc.l, sc.e, sc.end
    cam = [{"t": 0, "p": [-3.6, 2.6, 18], "l": [-3.4, 2.5, 0]}, {"t": end(4) + 0.4, "p": [-4.6, 2.3, 10.5], "l": [-3.1, 2.4, 0]}]
    ex = fade_out(sc, sc.block(sc.label("NOV 18", 0, 0, 170, "serif n", 900), l(1) + 3.2, 96, 150), end(1) - 0.2)
    qs = [("1", "Was anything actually compromised — or is there only a relationship?", l(2), e(2)),
          ("2", "Does the accused get to see the file?", l(3), e(3)),
          ("3", "Who wins the policy fight if he falls?", l(4), e(4))]
    for i, (n, q, ta, tb) in enumerate(qs):
        ex += sc.block(sc.label(n, 0, 0, 120, "serif c", 120), ta, 96, 190 + i * 250)
        ex += sc.words(q, ta + 0.4, tb, 230, 205 + i * 250, 1000, 60, cls="serif n")
    sc.three(0, end(4), "door", cam, extra=ex)
    sc.recon(0.6, end(4))
    sc.hud(0.6, end(4), "November 18, 2026 · U.S. Congress", "c")
    ex = sc.words("America skipped all three.", l(5), e(5), 160, 130, 1600, 100, cls="serif n", align="center", hi={"skipped"}, hicls="r")
    stats = [(l(6) + 0.6, "68", "YEARS"), (l(6) + 2.4, "43", "SENATORS"), (l(6) + 3.6, "ALL", "LIVING LOS ALAMOS DIRECTORS")]
    for i, (t, a, b) in enumerate(stats):
        ex += sc.block(sc.label(a, 0, 0, 190, "serif a", 500, "center") + sc.label(b, 0, 250, 30, "mono n", 500, "center"), t, 190 + i * 520, 380)
    sc.clip(l(5), end(6), '<div class="fill"></div>' + ex)
    sc.src(l(6) + 0.5, end(6), "U.S. Secretary of Energy, order of Dec. 16, 2022")
    # 7-8: the two pages, then the end card (space kept free for YouTube end-screen elements on the right)
    doc, pid = sc.paper("BOARD FINDINGS · 1954", [("“no evidence of disloyalty”", l(7) + 1.8, None), ("Clearance: not reinstated.", l(7) + 2.6, None)], 150, 250, 760, size=36)
    doc2, pid2 = sc.paper("BOARD FINDINGS · 2026", [("—", l(7) + 3.8, None), ("Not yet written.", l(7) + 4.4, None)], 1010, 250, 760, size=36)
    sc.tilt(pid, l(7), sc.dur, rot=(6, 2), sc=(0.96, 1.0)); sc.tilt(pid2, l(7), sc.dur, rot=(-6, -2), sc=(0.96, 1.0))
    ex = doc + doc2 + sc.words("Watch what the next board writes.", l(7) + 3.4, e(7), 160, 760, 1600, 76, cls="serif n", align="center", hi={"next"}, hicls="c")
    ex = fade_out(sc, ex, l(8) + 0.9)
    ex += sc.block(sc.label("ERA MIRROR", 0, 0, 96, "serif n", 800), l(8) + 1.1, 150, 300)
    ex += sc.block(sc.label("THE PAST, HELD UP TO THE PRESENT", 0, 0, 32, "mono a", 800), l(8) + 1.5, 154, 430)
    ex += sc.block(sc.label("NEXT MIRROR →", 0, 0, 44, "mono c", 800), l(8) + 1.9, 154, 560)
    sc.clip(l(7), sc.dur, '<div class="fill"></div>' + ex)

SCENES = {"s01": ("a", s01), "s02": ("c", s02), "s03": ("c", s03), "s04": ("a", s04), "s05": ("a", s05), "s06": ("c", s06), "s07": ("a", s07),
          "s08": ("a", s08), "s09": ("n", s09), "s10": ("a", s10), "s11": ("a", s11), "s12": ("a", s12), "s13": ("c", s13), "s14": ("n", s14), "s15": ("c", s15)}


# Sound cues: (kind, scene-local time). boom = the few big story hits, thump = numbers landing, key = typed lines.
SFX = {
    "s01": lambda sc: [("boom", sc.e(4) - 0.75), ("thump", sc.l(5) + 2.9), ("thump", sc.l(7) + 0.35)],
    "s02": lambda sc: [("key", sc.l(2) + 0.6), ("key", sc.l(2) + 1.0), ("thump", sc.l(2) + 4.6), ("thump", sc.l(5) + 3.5), ("thump", sc.l(6) + 0.2)],
    "s03": lambda sc: [("thump", sc.l(2) + 3.6), ("thump", sc.l(3) + 0.6), ("thump", sc.l(3) + 1.3), ("boom", sc.l(5) + 0.1)],
    "s04": lambda sc: [("thump", sc.l(5) + 1.9), ("thump", sc.l(7))],
    "s05": lambda sc: [("key", sc.l(3) + 2.4), ("key", sc.l(3) + 5.0), ("thump", sc.l(4) + 1.0), ("thump", sc.l(5) + 5.6), ("thump", sc.l(6) + 4.1), ("thump", sc.l(7) + 5.0)],
    "s06": lambda sc: [("key", sc.l(2) + 3.0), ("key", sc.l(2) + 6.0), ("thump", sc.l(6) + 3.2)],
    "s07": lambda sc: [("thump", sc.l(4) + 2.7), ("thump", sc.l(6) + 0.2)],
    "s08": lambda sc: [("thump", 1.9), ("boom", sc.l(4) + 2.6), ("key", sc.l(5) + 1.2), ("thump", sc.l(6)), ("key", sc.l(7)), ("thump", sc.l(8))],
    "s09": lambda sc: [("thump", sc.l(2) + 2.6)],
    "s10": lambda sc: [],
    "s11": lambda sc: [("boom", sc.l(1) + 1.6), ("thump", sc.l(3) + 0.9), ("thump", sc.l(3) + 6.8), ("thump", sc.l(4) + 2.4)],
    "s12": lambda sc: [("thump", sc.l(2) + 8.2), ("key", sc.l(4) + 5.2), ("boom", sc.l(6) + 3.8), ("thump", sc.l(8) + 5.6), ("boom", sc.l(9) + 4.9)],
    "s13": lambda sc: [("thump", sc.l(5) + 5.5)],
    "s14": lambda sc: [("key", sc.l(2)), ("key", sc.l(3)), ("key", sc.l(5)), ("key", sc.l(6))],
    "s15": lambda sc: [("thump", sc.l(2)), ("thump", sc.l(3)), ("thump", sc.l(4)), ("thump", sc.l(5)), ("thump", sc.l(6) + 0.6), ("thump", sc.l(6) + 2.4), ("thump", sc.l(6) + 3.6)],
}
