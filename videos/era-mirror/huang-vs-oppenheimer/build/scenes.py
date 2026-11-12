"""Shot lists (photo and document driven; no 3D). Each function receives a Scene (see gen.py):
sc.l(i) = start of line i, sc.e(i) = end of line i, sc.end(i) = start of the next line."""

def split_plate(sc, t0, t1, left, right, extra=""):
    """Two eras side by side: amber print on the left, cyan print on the right."""
    from gen import imsize
    parts = []
    for slug, x, era in ((left, 150, "a"), (right, 1050, "c")):
        if not imsize(slug):
            parts.append(f'<div style="position:absolute;left:{x}px;top:210px;width:720px;height:600px;border-radius:28px;background:#1c1c1e"></div>'); continue
        pid = sc.uid("p")
        parts.append(f'<div class="pcard" id="{pid}" style="left:{x}px;top:200px;width:720px;height:620px"><img src="assets/img/{slug}_g.jpg" alt="" style="object-position:50% 22%"></div>')
        sc.tilt(pid, t0 + (0.0 if era == "a" else 0.15), t1 + 0.3)
    mid = sc.uid("m")
    sc.js.append(f'tl.fromTo("#{mid}",{{scaleY:0}},{{scaleY:1,duration:0.7,ease:"expo.out"}},{t0 + 0.15:.3f});')
    return sc.clip(t0, t1, '<div class="fill"></div>' + "".join(parts) + f'<div id="{mid}" class="bar" style="left:959px;top:200px;width:2px;height:620px;background:rgba(255,255,255,.35)"></div>' + extra)

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
        ex += sc.block(sc.label(sub, 0, 0, 34, f"mono {era}", 1600, "center"), t_sub or (t0 + 1.2), 160, yy + size * 1.25 * (1 + (len(text) * size * 0.5 > 1600)) + 40)
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
    inner = (f'<div class="fill"></div><div id="{pid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;height:{h:.0f}px;transform-origin:{focus[0]}% {focus[1]}%;box-shadow:0 50px 120px rgba(0,0,0,.75);border-radius:10px;overflow:hidden">'
             f'<img src="assets/img/{slug}_g.jpg" alt="" style="display:block;width:100%;height:100%">{bars}</div><div class="shade" style="opacity:.55"></div>{extra}')
    # keep the focus point at frame centre when zoomed
    dx, dy = (50 - focus[0]) / 100 * w, (50 - focus[1]) / 100 * h
    d = t1 - t0 + 0.3
    sc.js.append(f'tl.fromTo("#{pid}",{{scale:{zoom[0]},x:0,y:0,rotationX:0,rotationY:0}},{{scale:{zoom[1]},x:{dx * zoom[1]:.0f},y:{dy * zoom[1]:.0f},rotationX:0,rotationY:0,duration:{min(d, 3.2):.2f},ease:"power2.inOut"}},{t0:.3f});')
    if d > 3.4:
        sc.js.append(f'tl.to("#{pid}",{{scale:{zoom[1] * 1.06:.3f},duration:{d - 3.2:.2f},ease:"none"}},{t0 + 3.2:.3f});')
    return sc.clip(t0, t1, inner)

def ledger_rows(sc, rows, y0=250, gap=118, head=None):
    """rows = [(time, key, left, right)]"""
    out = ""
    if head:
        out += f'<div class="tx mono a" style="left:360px;top:{y0 - 78}px;width:600px;font-size:34px">{head[0]}</div><div class="tx mono c" style="left:1010px;top:{y0 - 78}px;width:600px;font-size:34px">{head[1]}</div><div class="rule" style="left:160px;top:{y0 - 22}px;width:1600px"></div>'
    for i, (t, k, a, b) in enumerate(rows):
        rid = sc.uid("r")
        out += f'<div class="row" id="{rid}" style="top:{y0 + i * gap}px"><div class="k">{k}</div><div class="l">{a}</div><div class="rr">{b}</div></div>'
        sc.js.append(f'tl.fromTo("#{rid}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.5,ease:"expo.out"}},{t:.3f});')
    return out

def quote_plate(sc, t0, t1, slug, quote, who, era, tq0, tq1, side="left", size=64, name=None, sub=None, src=None, hi=None, focus="50% 25%"):
    tx = 1010 if side == "left" else 150
    ex = sc.words(quote, tq0, tq1, tx, 250, 770, size, cls="serif n", hi=hi, hicls=era)
    ex += sc.block(sc.label(who, 0, 0, 30, f"mono {era}", 770), tq1 + 0.2, tx, 820)
    sc.plate(t0, t1, slug, side=side, name=name, sub=sub, era=era, extra=ex, tilt=(5, -4) if side == "left" else (-5, 4), focus=focus)
    if src:
        sc.src(t0 + 0.6, t1, src)

def tally(sc, t, a, b, la, lb, x=160, y=300):
    ex = sc.block(sc.label(f"{a}", 0, 0, 360, "serif r", 500, "right"), t, x, y)
    ex += sc.block(sc.label("–", 0, 0, 280, "serif dim", 300, "center"), t + 0.15, x + 520, y + 40)
    ex += sc.block(sc.label(f"{b}", 0, 0, 360, "serif n", 500), t + 0.3, x + 840, y)
    ex += sc.block(sc.label(la, 0, 0, 34, "mono r", 500, "right"), t + 0.5, x, y + 430)
    ex += sc.block(sc.label(lb, 0, 0, 34, "mono n", 500), t + 0.6, x + 840, y + 430)
    return ex


def box_cards(sc, items, y=300, w=380, h=340, x0=None, gap=50):
    """Rounded tiles: items = [(big, small, time, accent_class)]"""
    n = len(items); x0 = x0 if x0 is not None else (1920 - n * w - (n - 1) * gap) / 2
    out = ""
    for i, (big, small, t, cls) in enumerate(items):
        cid = sc.uid("k")
        out += (f'<div id="{cid}" style="position:absolute;left:{x0 + i * (w + gap):.0f}px;top:{y}px;width:{w}px;height:{h}px;border-radius:32px;background:#1c1c1e;box-shadow:inset 0 0 0 1px rgba(255,255,255,.12)">'
                f'<div class="tx serif {cls}" style="left:34px;top:30px;width:{w - 60}px;font-size:{64 if len(big) > 5 else 110}px">{big}</div>'
                f'<div class="tx mono dim" style="left:36px;top:{h - 96}px;width:{w - 60}px;font-size:30px">{small}</div></div>')
        sc.js.append(f'tl.fromTo("#{cid}",{{opacity:0,y:40,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.7,ease:"expo.out"}},{t:.3f});')
    return out

def s01(sc):
    l, e, end = sc.l, sc.e, sc.end
    # 1: hero, on screen from frame 0
    ex = fade_out(sc, sc.label("One night.", 1010, 300, 150, "serif n", 800) + sc.label("1943", 1010, 470, 150, "serif a", 800), end(1) - 0.25)
    sc.plate(0, end(1), "opp_portrait", side="left", name="J. Robert Oppenheimer", sub="Photographed c. 1944", era="a", extra=ex)
    # 2: the street
    ex = sc.words("A night with a woman the government suspected.", l(2) + 2.6, e(2), 1010, 300, 780, 82, cls="serif n", hi={"suspected."})
    sc.plate(l(2), end(2), "sf_montgomery", side="left", name="Montgomery Street, San Francisco", sub="Archive photograph, c. 1930s–40s", era="a", extra=ex)
    sc.hud(l(2), end(3), "Spring 1943 · San Francisco", "a")
    # 3: the watchers
    ex = sc.words("Army agents. Outside until morning.", l(3) + 0.2, l(3) + 2.4, 150, 300, 780, 96, cls="serif n", hi={"outside"})
    ex += sc.block(sc.label("They wrote it all down.", 0, 0, 40, "mono dim", 780), l(3) + 3.4, 154, 640)
    sc.plate(l(3), end(3), "silence_poster", side="right", name="Atomic Energy Commission security poster", sub="U.S. Army Corps of Engineers, 1947", era="a", extra=ex)
    # 4: the closed room
    ex = sc.words("Read back to him in a closed room.", l(4) + 1.2, l(4) + 3.4, 150, 300, 760, 76, cls="serif n")
    ex += sc.block(sc.label("He lost.", 0, 0, 170, "serif r", 800), e(4) - 0.8, 146, 580)
    sc.plate(l(4), end(4), "opp_congress53", side="right", name="J. Robert Oppenheimer", sub="Washington, 1953", era="a", extra=ex)
    sc.hud(l(4), end(4), "April 1954 · Washington, D.C.", "a")
    # 5: 68 years
    ex = sc.counter(l(5) + 1.3, 0, 68, 150, 230, 400, "serif n", 900, dur=1.6)
    ex += sc.block(sc.label("years", 0, 0, 100, "serif a", 800), l(5) + 2.7, 160, 650)
    ex += sc.words("to admit the process was rigged against him.", l(5) + 3.0, e(5), 164, 800, 800, 44, cls="mono dim")
    sc.plate(l(5), end(5), "doe_order-1", side="right", era="n", extra=ex, credit=False, focus="50% 0%")
    sc.src(l(5) + 0.5, end(5), "U.S. Secretary of Energy, order of Dec. 16, 2022")
    # 6: 2026
    ex = sc.words("“I was unfaithful to my wife.”", l(6) + 3.4, l(6) + 5.0, 1010, 280, 780, 84, cls="serif n")
    ex += sc.block(sc.label("Jensen Huang · memo to Nvidia staff · Nov. 8, 2026", 0, 0, 30, "mono c", 780), l(6) + 5.2, 1014, 580)
    ex += sc.block(sc.label("U.S. intelligence believes the woman was recruited by China. No one has been charged.", 0, 0, 34, "mono dim", 760), l(6) + 6.6, 1014, 680)
    sc.plate(l(6), end(6), "huang_stanford_a", side="left", name="Jensen Huang", sub="Founder and CEO, Nvidia · photo: April 2026", era="c", extra=ex)
    sc.hud(l(6), end(6), "November 2026", "c")
    sc.src(l(6) + 5.0, end(6), "Nvidia newsroom · New York Times · NBC News")
    # 7: the date
    ex = sc.block(sc.label("Nov 18", 0, 0, 210, "serif n", 800), l(7) + 0.3, 1006, 300)
    ex += sc.block(sc.label("Closed-door briefing requested by the U.S. House", 0, 0, 36, "mono c", 760), l(7) + 1.3, 1014, 560)
    sc.plate(l(7), end(7), "capitol", side="left", name="U.S. Capitol", sub="Washington, D.C.", era="c", extra=ex)
    # 8: the mirror
    ex = sc.words("What did America find the last time?", l(8) + 0.2, l(8) + 2.6, 160, 60, 1600, 68, cls="serif n", align="center")
    ex += sc.words("And why did it take it all back?", l(8) + 3.2, e(8) - 0.2, 160, 880, 1600, 68, cls="serif n", align="center")
    ex += sc.block(sc.label("1954", 0, 0, 40, "mono a", 300), l(8) + 0.5, 150, 834)
    ex += sc.block(sc.label("2026", 0, 0, 40, "mono c", 300, "right"), l(8) + 0.9, 1470, 834)
    split_plate(sc, l(8), sc.dur, "opp_portrait", "huang_stanford_a", ex)

def s02(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "November 2026 · Santa Clara", "c")
    title(sc, 0, end(1), "What is confirmed", era="c", size=150, hi={"confirmed"})
    doc, pid = sc.paper("Nvidia · A Message to Our Company · Nov. 8, 2026", [
        ("From: Jensen Huang, founder and CEO", l(2) + 0.6, None),
        ("To: all employees", l(2) + 1.0, None),
        ("“[[I was unfaithful to my wife.]]”", l(2) + 6.0, l(2) + 6.8)], 150, 270, 900, size=40)
    sc.tilt(pid, l(2), end(2) + 0.3)
    ex = doc + sc.block(sc.label("Six words.", 0, 0, 130, "serif n", 700), l(2) + 5.0, 1130, 380)
    ex += sc.block(sc.label("Sunday · Nov. 8, 2026", 0, 0, 34, "mono c", 700), l(2) + 0.4, 1136, 310)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(2), "Nvidia newsroom, “A Message to Our Company”")
    ex = sc.words("The board investigates its own founder.", l(3) + 1.0, e(3), 1010, 300, 770, 84, cls="serif n", hi={"founder."}, hicls="c")
    ex += sc.block(sc.label("Independent investigation · announced the same day", 0, 0, 32, "mono c", 770), l(3) + 0.5, 1014, 230)
    sc.plate(l(3), end(3), "nvidia_hq", side="left", name="Nvidia headquarters", sub="Santa Clara, California", era="c", extra=ex)
    sc.src(l(3) + 0.5, end(3), "Statement from Nvidia Board of Directors, Nov. 8, 2026")
    facts = [(l(4) + 2.0, "No relation to Jensen Huang"), (l(4) + 3.4, "Chinese citizen"), (l(4) + 5.2, "Former executive, Megaspeed · Singapore")]
    ex = sc.silhouette(190, 240, 560, "c") + sc.label("No photo shown", 190, 822, 30, "mono dim", 420)
    ex += sc.words("Alice Huang", l(4) + 0.5, l(4) + 1.1, 720, 220, 1000, 130, cls="serif n")
    for i, (t, f) in enumerate(facts):
        ex += sc.block(sc.label(f, 0, 0, 38, "mono c", 1050), t, 726, 400 + i * 64)
    ex += sc.block(sc.counter(l(5) + 2.4, 0, 4.8, 0, 0, 150, "serif n", 1050, dur=1.5, pre="$", suf=" billion", dec=1), l(5) + 2.2, 720, 610)
    ex += sc.block(sc.label("Nvidia equipment bought by Megaspeed, as reported by the New York Times", 0, 0, 30, "mono dim", 1000), l(5) + 3.8, 726, 800)
    sc.clip(l(4), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(4) + 1.0, end(5), "Al Jazeera, Nov. 9 · CNBC, Nov. 9 · New York Times")
    ex = sc.words("Not confirmed", l(6) + 0.2, l(6) + 1.0, 160, 130, 1600, 120, cls="serif n", hi={"not"}, hicls="r")
    rows = [(l(6) + 2.6, "The claim", "Recruited by Beijing", "An intelligence assessment"),
            (l(7) + 0.4, "Reported by", "New York Times", "NBC News"),
            (l(7) + 4.0, "Criminal charges", "Against him: none", "Against her: none"),
            (l(8) + 0.3, "Beijing", "“Baseless”", ""),
            (l(8) + 3.0, "Nvidia board", "“No reason to believe”", "secrets were compromised")]
    ex += ledger_rows(sc, rows, y0=330, gap=116).replace('class="l"', 'class="l" style="color:#f5f5f7"').replace('class="rr"', 'class="rr" style="color:#f5f5f7"')
    sc.clip(l(6), end(8), '<div class="fill"></div>' + ex)
    sc.src(l(6) + 2.0, end(8), "NBC News · Al Jazeera · Nvidia board statement")
    quote_plate(sc, l(9), end(9), "huang_stanford_b", "“…completely normal and not unusual.”", "Jensen Huang to Bloomberg News · October 2026", "c", l(9) + 6.4, e(9), name="Jensen Huang", sub="Stanford University, April 30, 2026", src="Quoted by Fortune, Nov. 9, 2026", hi={"normal"}, size=78)
    # 10-11: the second report
    ex = sc.block(sc.label("Nov. 11, 2026", 0, 0, 36, "mono c", 1600, "center"), l(10) + 0.3, 160, 150)
    ex += sc.words("A second relationship is reported.", l(10) + 3.0, l(10) + 5.0, 160, 220, 1600, 110, cls="serif n", align="center", hi={"reported."}, hicls="r")
    ex += box_cards(sc, [("Who", "A senior Nvidia executive who reports to him", l(10) + 5.6, "n"),
                         ("Source", "New York Times, citing unnamed people inside the company", l(11) + 0.3, "n"),
                         ("Status", "Not confirmed by Huang or by Nvidia", l(11) + 3.4, "r")], y=470, w=480, h=330)
    sc.clip(l(10), sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(10) + 1.0, sc.dur - 0.4, "New York Times, as reported by Axios and ABC News, Nov. 11, 2026")

def s03(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, l(6), "Wall Street · November 2026", "c")
    title(sc, 0, end(1), "Why does a private affair shake a market?", era="c", size=104, hi={"market?"})
    ex = sc.words("“Jensen is not replaceable.”", l(2) + 0.4, l(2) + 2.2, 160, 190, 1600, 110, cls="serif n", align="center")
    ex += sc.block(sc.label("Dan Ives, Wedbush · Nov. 10, 2026", 0, 0, 34, "mono c", 1600, "center"), l(2) + 2.3, 160, 340)
    ex += sc.block(sc.label("−25% to −30%", 0, 0, 200, "serif r", 1600, "center"), l(2) + 4.2, 160, 470)
    ex += sc.block(sc.label("His estimate of Nvidia’s value without Huang", 0, 0, 36, "mono dim", 1600, "center"), l(2) + 5.2, 160, 720)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.6, end(2), "Yahoo Finance live coverage, Nov. 10, 2026")
    ex = box_cards(sc, [("−4.3%", "Monday, Nov. 9", l(3) + 0.6, "r"), ("−5.47%", "Tuesday, Nov. 10", l(3) + 1.5, "r")], y=300, w=400, h=300, x0=160)
    ex += sc.block(sc.counter(l(3) + 4.0, 0, 500, 0, 0, 170, "serif n", 800, dur=1.5, pre="≈ $", suf="B"), l(3) + 3.8, 1060, 300)
    ex += sc.block(sc.label("in market value, two trading days", 0, 0, 36, "mono dim", 800), l(3) + 5.2, 1068, 520)
    sc.clip(l(3), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(3) + 0.5, end(3), "CNBC, Nov. 11 · NBC News, Nov. 10, 2026")
    ex = box_cards(sc, [("≈ −7%", "After hours, Nov. 11, after the second report", l(4) + 1.6, "r"), ("The board", "Reported to be meeting on his future", l(4) + 6.0, "n")], y=300, w=560, h=340, x0=160)
    ex += sc.block(sc.label("Reported. No decision announced.", 0, 0, 36, "mono dim", 1200), l(4) + 8.0, 164, 700)
    sc.clip(l(4), end(4), '<div class="fill"></div>' + ex)
    sc.src(l(4) + 0.6, end(4), "Axios, Nov. 11 · Wall Street Journal, as reported by ABC News")
    ex = sc.words("Can he be trusted?", l(5) + 3.8, e(5), 1010, 330, 770, 110, cls="serif n", hi={"trusted?"}, hicls="c")
    sc.plate(l(5), end(5), "whitehouse", side="left", name="The White House", sub="Washington, D.C.", era="c", extra=ex)
    ex = sc.words("America has asked this before.", l(6) + 0.1, l(6) + 2.2, 160, 360, 1600, 116, cls="serif n", align="center", hi={"before."}, hicls="a")
    ex += sc.block(sc.label("A different man.", 0, 0, 40, "mono a", 780, "right"), l(6) + 3.6, 160, 620)
    ex += sc.block(sc.label("A different technology.", 0, 0, 40, "mono a", 780), l(6) + 5.0, 990, 620)
    sc.clip(l(6), sc.dur, '<div class="fill"></div>' + ex)

def s04(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "Spring 1943 · San Francisco", "a")
    ex = sc.words("The most secret project in American history.", l(1) + 4.4, e(1), 150, 300, 770, 84, cls="serif n", hi={"secret"})
    sc.plate(0, end(1), "la_gate", side="right", name="Los Alamos Project, main gate", sub="U.S. Army photograph, c. 1943", era="a", extra=ex)
    facts = [(l(2) + 4.2, "His first real love"), (l(2) + 6.4, "Member, Communist Party")]
    ex = sc.silhouette(190, 240, 560, "a") + sc.label("No photo shown", 190, 822, 30, "mono dim", 420)
    ex += sc.words("Jean Tatlock", l(2) + 1.8, l(2) + 2.6, 720, 240, 1000, 130, cls="serif n")
    for i, (t, f) in enumerate(facts):
        ex += sc.block(sc.label(f, 0, 0, 40, "mono a", 1000), t, 726, 440 + i * 70)
    sc.clip(l(2), end(2), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 1.0, end(2), "PBS American Experience · AEC letter of charges, 1953")
    ex = sc.words("He stays the night.", l(3) + 0.2, l(3) + 1.6, 1010, 280, 780, 100, cls="serif n")
    ex += sc.block(sc.label("Army intelligence waits outside until morning.", 0, 0, 40, "mono a", 760), l(3) + 4.4, 1014, 540)
    sc.plate(l(3), end(3), "sf_montgomery", side="left", name="Montgomery Street, San Francisco", sub="Archive photograph, c. 1930s–40s", era="a", extra=ex)
    ex = sc.words("The report goes to the F.B.I.", l(4), e(4), 150, 320, 780, 100, cls="serif n", hi={"f.b.i."})
    sc.plate(l(4), end(4), "hoover", side="right", name="J. Edgar Hoover", sub="Director of the F.B.I.", era="a", extra=ex)
    ex = sc.words("Phone tap:", l(5) + 0.5, l(5) + 1.0, 160, 290, 1600, 90, cls="serif dim", align="center")
    ex += sc.block(sc.label("Nothing found.", 0, 0, 190, "serif n", 1600, "center"), l(5) + 2.2, 160, 420)
    sc.clip(l(5), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(5) + 0.4, end(6), "PBS American Experience, “The Trials of J. Robert Oppenheimer”")
    ex = sc.silhouette(190, 240, 560, "a") + sc.label("Jean Tatlock · died January 1944", 190, 822, 30, "mono dim", 700)
    ex += sc.words("Never shown to have passed a single secret.", l(6) + 3.8, e(6), 720, 300, 1040, 96, cls="serif n", hi={"never"})
    sc.clip(l(6), end(6), '<div class="fill"></div>' + ex)
    ex = sc.words("The file stays open.", l(7), e(7), 160, 400, 1600, 150, cls="serif n", align="center", hi={"open."})
    sc.clip(l(7), sc.dur, '<div class="fill"></div>' + ex)

def s05(sc):
    l, e, end = sc.l, sc.e, sc.end
    ex = sc.words("The most famous scientist in America.", l(1) + 4.6, e(1), 1010, 320, 770, 84, cls="serif n", hi={"famous"})
    sc.plate(0, end(1), "opp_groves_trinity", side="left", name="Oppenheimer and Gen. Leslie Groves", sub="Trinity test site, September 1945", era="a", extra=ex)
    sc.hud(0.5, end(1), "1945 · New Mexico", "a")
    ex = sc.words("He argues against the crash program.", l(2) + 3.4, e(2), 150, 320, 770, 84, cls="serif n", hi={"against"})
    sc.plate(l(2), end(2), "ivymike", side="right", name="Hydrogen bomb test “Ivy Mike”", sub="Enewetak Atoll, Nov. 1, 1952", era="a", extra=ex)
    sc.hud(l(2), end(2), "1949–1952 · The hydrogen bomb", "a")
    doc, pid = sc.paper("Letter · November 7, 1953", [
        ("From: William L. Borden", l(3) + 2.8, None),
        ("To: J. Edgar Hoover, Director, F.B.I.", l(3) + 5.8, None),
        ("“[[More probably than not]], J. Robert Oppenheimer is [[an agent of the Soviet Union]].”", l(4) + 0.3, l(4) + 1.2)], 150, 250, 1000, size=42)
    sc.tilt(pid, l(3), end(4) + 0.3)
    ex = doc + sc.block(sc.label("His conclusion", 0, 0, 40, "mono a", 600), l(4) + 0.1, 1230, 420)
    sc.clip(l(3), end(4), '<div class="fill"></div>' + ex)
    sc.hud(l(3), end(4), "November 1953 · Washington, D.C.", "a")
    sc.src(l(3) + 1.0, end(4), "Atomic Heritage Foundation · typeset excerpt")
    ex = sc.block(sc.label("Dec. 21, 1953", 0, 0, 36, "mono a", 770), l(5) + 0.3, 1014, 240)
    ex += sc.words("Clearance suspended.", l(5) + 6.4, l(5) + 7.8, 1010, 310, 770, 100, cls="serif n", hi={"suspended."}, hicls="r")
    ex += sc.block(sc.label("Resign quietly, or fight.", 0, 0, 42, "mono dim", 770), l(5) + 9.6, 1014, 600)
    sc.plate(l(5), end(5), "strauss_ike54", side="left", name="President Eisenhower and Lewis Strauss", sub="The White House, March 30, 1954", era="a", extra=ex)
    sc.hud(l(5), end(5), "December 1953 · Washington, D.C.", "a")
    ex = sc.block(sc.counter(l(6) + 3.4, 0, 24, 0, 0, 440, "serif n", 800, dur=1.2), l(6) + 3.2, 190, 220)
    ex += sc.block(sc.label("charges", 0, 0, 120, "serif a", 900), l(6) + 4.2, 860, 420)
    ex += sc.block(sc.label("Dec. 23, 1953", 0, 0, 38, "mono dim", 900), l(6) + 1.5, 868, 350)
    sc.clip(l(6), end(6), '<div class="fill"></div>' + ex)
    doc, pid = sc.paper("U.S. Atomic Energy Commission · K. D. Nichols to J. R. Oppenheimer · Dec. 23, 1953", [
        ("It was reported that in 1943 and previously you were", l(7) + 0.4, None),
        ("“[[intimately associated with Dr. Jean Tatlock]],", l(7) + 0.4, l(7) + 6.0),
        ("a member of the Communist Party in San Francisco.”", l(7) + 0.4, None)], 280, 290, 1360, size=44)
    sc.tilt(pid, l(7), sc.dur)
    sc.clip(l(7), sc.dur, '<div class="fill"></div>' + doc)
    sc.src(l(7) + 0.6, sc.dur - 0.4, "AEC letter of charges, Dec. 23, 1953 · typeset excerpt")

def s06(sc):
    l, e, end = sc.l, sc.e, sc.end
    title(sc, 0, end(1), "Now: 2026", era="c", size=200, hi={"2026"})
    sc.hud(l(2), sc.dur - 0.4, "Spring 2026 · Washington, D.C.", "c")
    doc, pid = sc.paper("Classified memo · as described in press reports · not the actual document", [
        ("Subject: the relationship of Nvidia’s chief executive", l(2) + 3.4, None),
        ("Circulated inside the administration, spring 2026", l(2) + 7.0, None),
        ("Basis: [[surveillance of Alice Huang]] (reported)", l(3) + 0.2, l(3) + 1.0)], 150, 240, 1040, size=40)
    sc.tilt(pid, l(2), end(3) + 0.3)
    ex = doc + sc.block(sc.label("Reported.", 0, 0, 110, "serif c", 600), l(2) + 0.5, 1250, 380)
    ex += sc.block(sc.label("Not independently confirmed", 0, 0, 34, "mono dim", 600), l(2) + 1.8, 1256, 520)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(3), "New York Times · Axios, Nov. 10, 2026")
    ex = sc.words("“…warned the president directly.”", l(4) + 5.6, e(4), 1010, 300, 770, 84, cls="serif n", hi={"warned"}, hicls="c")
    ex += sc.block(sc.label("As reported · May 2026 · en route to Beijing", 0, 0, 32, "mono c", 770), l(4) + 2.4, 1014, 230)
    sc.plate(l(4), l(4) + (end(4) - l(4)) * 0.55, "airforceone", side="left", name="Air Force One", sub="File photo, U.S. Air Force", era="c", extra=ex)
    ex2 = sc.label("“…warned the president directly.”", 1010, 300, 84, "serif n", 770) + sc.label("As reported · May 2026 · en route to Beijing", 1014, 230, 32, "mono c", 770)
    sc.plate(l(4) + (end(4) - l(4)) * 0.55, end(4), "rubio", side="left", name="Marco Rubio", sub="Secretary of State · official portrait", era="c", extra=ex2)
    sc.src(l(4) + 0.8, end(5), "New York Times, as relayed by NBC News and Axios")
    ex = sc.words("“It didn’t make much of an impact on me.”", l(5) + 3.0, e(5), 150, 300, 770, 84, cls="serif n")
    ex += sc.block(sc.label("President Trump · Nov. 9, 2026", 0, 0, 32, "mono c", 770), e(5), 154, 700)
    sc.plate(l(5), end(5), "trump", side="right", name="Donald Trump", sub="Official portrait, 2025", era="c", extra=ex)
    ex = ledger_rows(sc, [(l(6) + 0.3, "The file", "Army surveillance report", "Classified memo (reported)"),
                          (l(6) + 1.8, "Written", "1943", "Spring 2026"),
                          (l(6) + 3.3, "Made public", "1954", "November 2026")], y0=440, gap=130, head=("Oppenheimer", "Huang"))
    ex += sc.words("The file came first.", l(6) + 3.6, e(6), 160, 150, 1600, 120, cls="serif n", align="center")
    sc.clip(l(6), sc.dur, '<div class="fill"></div>' + ex)

def s07(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April 12, 1954 · Washington, D.C.", "a")
    ex = sc.block(sc.label("No press. No public.", 0, 0, 110, "serif n", 800), l(1) + 10.4, 1006, 300)
    ex += sc.block(sc.label("An office turned into a courtroom", 0, 0, 38, "mono a", 780), l(1) + 6.6, 1014, 230)
    sc.plate(0, end(1), "aec_doc_p1", side="left", name="In the Matter of J. Robert Oppenheimer", sub="U.S. Atomic Energy Commission, 1954 · title page", era="a", extra=ex, focus="50% 20%")
    ex = sc.words("What he does not know.", l(2) + 4.0, e(2), 150, 320, 780, 110, cls="serif n", hi={"not"})
    sc.plate(l(2), end(2), "opp_congress53", side="right", name="J. Robert Oppenheimer", sub="Washington, 1953", era="a", extra=ex)
    ex = sc.words("The F.B.I. has bugged his lawyer’s office.", l(3) + 0.1, e(3), 160, 170, 1600, 100, cls="serif n", align="center", hi={"bugged"}, hicls="r")
    ex += sc.block(sc.counter(l(4) + 1.4, 0, 273, 0, 0, 340, "serif n", 1600, "center", dur=1.5), l(4) + 1.2, 160, 380)
    ex += sc.block(sc.label("wiretap reports read by the prosecution, at least", 0, 0, 38, "mono a", 1600, "center"), l(4) + 3.2, 160, 770)
    ex += sc.block(sc.label("including his calls with his own attorneys", 0, 0, 38, "mono dim", 1600, "center"), l(4) + 6.2, 160, 830)
    sc.clip(l(3), end(4), '<div class="fill"></div>' + ex)
    sc.src(l(3) + 0.6, end(4), "Atomic Heritage Foundation · PBS American Experience")
    ex = sc.block(sc.label("One week.", 0, 0, 150, "serif n", 800), l(5) + 1.0, 1006, 240)
    ex += sc.block(sc.label("Prosecutor and judges, alone with the F.B.I. files", 0, 0, 40, "mono a", 780), l(5) + 6.0, 1014, 440)
    ex += sc.block(sc.label("The defense: not in the room.", 0, 0, 80, "serif r", 800), l(6) + 0.2, 1010, 600)
    sc.plate(l(5), sc.dur, "robb", side="left", name="Roger Robb", sub="The commission’s prosecutor · later portrait", era="a", extra=ex)
    sc.src(l(5) + 0.8, sc.dur - 0.4, "U.S. Secretary of Energy, order of Dec. 16, 2022")

def s08(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April 1954 · The witness chair", "a")
    ex = sc.block(sc.counter(0.6, 0, 27, 0, 0, 330, "serif n", 800, dur=1.4), 0.4, 1000, 220)
    ex += sc.block(sc.label("hours of testimony", 0, 0, 44, "mono a", 780), 1.8, 1014, 590)
    ex = fade_out(sc, ex, end(1) - 0.2)
    ex += sc.words("A secret recording from 1943.", l(2) + 0.8, l(2) + 3.0, 1010, 300, 780, 96, cls="serif n", hi={"secret"})
    ex += sc.block(sc.label("Parts of the story he told were invented.", 0, 0, 40, "mono dim", 760), l(2) + 8.0, 1014, 640)
    sc.plate(0, end(3), "opp_einstein", side="left", name="Oppenheimer with Albert Einstein", sub="Princeton, c. 1950", era="a", extra=ex)
    ex = sc.label("Q. Why did you do that, Doctor?", 160, 240, 44, "mono a", 1600, "center")
    ex += sc.words("“Because I was an idiot.”", l(4) + 3.0, e(4), 100, 370, 1720, 170, cls="serif n", align="center", hi={"idiot.”"}, hicls="r")
    sc.clip(l(4), end(4), '<div class="fill"></div>' + ex)
    sc.src(l(4) + 0.5, end(4), "Hearing transcript, 1954, as quoted by PBS American Experience")
    qa = [("Q.", "You spent the night with her, didn’t you?", l(5) + 1.4, e(5)), ("A.", "Yes.", l(6), e(6)),
          ("Q.", "That is when you were working on a secret war project?", l(7), e(7)), ("A.", "Yes.", l(8), e(8))]
    ex = sc.label("Transcript · In the Matter of J. Robert Oppenheimer · 1954", 160, 150, 32, "mono dim", 1600)
    y = 250
    for who, text, ta, tb in qa:
        big = who == "A."
        ex += sc.block(sc.label(who, 0, 0, 60, "serif a" if not big else "serif r", 120), ta, 160, y + 6)
        ex += sc.words(text, ta + 0.05, tb, 290, y, 1450, 120 if big else 70, cls="serif n")
        y += 160 if big else (200 if len(text) > 45 else 120)
    sc.clip(l(5), sc.dur, '<div class="fill"></div><div class="rule" style="left:160px;top:214px;width:1600px"></div>' + ex)
    sc.src(l(5) + 0.5, sc.dur - 0.4, "Hearing transcript, 1954, as quoted by PBS American Experience")

def s09(sc):
    l, e, end = sc.l, sc.e, sc.end
    sid = sc.uid("x")
    ex = sc.label("1954", 150, 150, 44, "mono a", 700) + sc.label("2026", 1070, 150, 44, "mono c", 700)
    ex += sc.words("“Because I was an idiot.”", l(1) + 1.4, l(1) + 3.0, 150, 280, 720, 88, cls="serif a")
    ex += f'<div id="{sid}" style="position:absolute;left:1070px;top:280px;width:720px">' + sc.words("“Completely normal and not unusual.”", l(2) + 0.3, l(2) + 2.2, 0, 0, 720, 88, cls="serif c") + f'<div id="{sid}-s" class="bar" style="left:0;top:140px;width:720px;height:8px;border-radius:4px;background:#ff453a"></div></div>'
    sc.js.append(f'tl.fromTo("#{sid}-s",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:0.45,ease:"power3.out"}},{l(2) + 2.9:.3f});')
    sc.js.append(f'tl.to("#{sid}",{{opacity:0.4,duration:0.3}},{l(2) + 3.0:.3f});')
    ex += sc.words("“I was unfaithful to my wife.”", l(2) + 3.4, e(2), 1070, 620, 720, 88, cls="serif n")
    ex += sc.block(sc.label("Weeks apart", 0, 0, 34, "mono c", 720), e(2), 1074, 840)
    ex += sc.block(sc.label("The gap is what gets investigated.", 0, 0, 48, "mono n", 1620, "center"), l(3) + 1.8, 150, 930)
    ex += '<div class="bar" style="left:959px;top:150px;width:2px;height:720px;background:rgba(255,255,255,.3)"></div>'
    sc.clip(0, sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(3) + 0.3, sc.dur - 0.4, "Fortune, Nov. 9, 2026")

def s10(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "April–May 1954 · Witnesses", "a")
    quote_plate(sc, 0, end(2), "rabi", "“We have an A-bomb and a whole series of it, and what more do you want, mermaids?”", "Isidor I. Rabi · Nobel laureate in physics", "a", l(2), e(2), name="I. I. Rabi", sub="Nobel Prize portrait, 1944", src="AEC hearing transcript, 1954", hi={"mermaids?”"}, size=66)
    quote_plate(sc, l(3), sc.dur, "teller58", "“I would feel personally more secure if public matters would rest in other hands.”", "Edward Teller · April 28, 1954", "a", l(4), e(4), side="right", name="Edward Teller", sub="Photographed in 1958", src="AEC hearing transcript, 1954", hi={"other", "hands.”"}, size=66)

def s11(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, l(4), "May 27, 1954 · The board’s verdict", "a")
    ex = sc.block(sc.label("2–1", 0, 0, 300, "serif n", 800), l(1) + 1.8, 1000, 250)
    ex += sc.block(sc.label("against him", 0, 0, 60, "serif r", 780), l(1) + 2.4, 1012, 580)
    sc.plate(0, end(1), "gray_oath", side="left", name="Gordon Gray (right), chairman of the board", sub="Taking an earlier oath of office, 1951", era="a", extra=ex)
    doc, pid = sc.paper("Personnel Security Board · Findings and Recommendation · May 27, 1954", [
        ("“[[no evidence of disloyalty]]”", l(3) + 0.1, l(3) + 1.0),
        ("“much responsible and positive evidence of the loyalty and [[love of country]]”", l(3) + 3.0, l(3) + 3.9),
        ("Recommendation: clearance [[not reinstated]].", l(3) + 6.2, l(3) + 7.4)], 150, 240, 1060, size=44)
    sc.tilt(pid, l(2), end(3) + 0.3)
    ex = doc + sc.words("Read it slowly.", l(2) + 0.2, l(2) + 1.5, 1290, 300, 560, 96, cls="serif n")
    ex += sc.block(sc.label("Loyal.", 0, 0, 130, "serif a", 600), l(3) + 4.2, 1286, 540)
    ex += sc.block(sc.label("Removed anyway.", 0, 0, 64, "serif r", 620), l(3) + 7.8, 1290, 710)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.6, end(3), "Board findings, May 27, 1954, quoted in the 2022 Energy Department order")
    sc.hud(l(4), sc.dur - 0.4, "June 29, 1954 · Atomic Energy Commission", "a")
    ex = sc.block(sc.label("4–1", 0, 0, 300, "serif n", 800), l(4) + 2.6, 150, 250)
    ex += sc.block(sc.label("to deny clearance", 0, 0, 60, "serif r", 780), l(4) + 3.2, 160, 580)
    sc.plate(l(4), end(4), "smyth", side="right", name="Henry D. Smyth", sub="The one commissioner who dissented", era="a", extra=ex)
    ex = sc.label("Not for leaking. Not for spying.", 160, 250, 48, "mono a", 1600, "center")
    ex += sc.words("“fundamental defects” in his character", l(5) + 3.0, e(5), 160, 390, 1600, 120, cls="serif n", align="center", hi={"“fundamental", "defects”"}, hicls="r")
    sc.clip(l(5), end(5), '<div class="fill"></div>' + ex)
    sc.src(l(5) + 0.5, sc.dur - 0.4, "AEC decision, June 29, 1954 · 2022 Energy Department order")
    ex = box_cards(sc, [("June 29", "The ruling", l(6) + 0.2, "r"), ("June 30", "", l(6) + 1.2, "n"), ("July 1", "Contract expires", l(6) + 2.0, "a")], y=250, w=420, h=320)
    ex += sc.words("They could have let it run out. They ruled anyway.", l(6) + 4.0, e(6), 160, 690, 1600, 84, cls="serif n", align="center", hi={"anyway."}, hicls="r")
    sc.clip(l(6), sc.dur, '<div class="fill"></div>' + ex)

def s12(sc):
    l, e, end = sc.l, sc.e, sc.end
    title(sc, 0, end(1), "So, was America safer?", era="a", size=150, hi={"safer?"})
    ex = sc.block(sc.counter(l(2) + 6.4, 300, 70000, 0, 0, 340, "serif n", 1600, "center", dur=2.6), l(2) + 0.5, 160, 280)
    ex += sc.block(sc.label("U.S. nuclear weapons, 1954", 0, 0, 42, "mono a", 1600, "center"), l(2) + 0.8, 160, 220)
    ex += sc.block(sc.label("built in the decades that followed", 0, 0, 42, "mono dim", 1600, "center"), l(2) + 8.6, 160, 690)
    ex += sc.block(sc.label("The strongest voice for restraint: silenced.", 0, 0, 48, "mono a", 1600, "center"), l(3) + 1.0, 160, 800)
    sc.clip(l(2), end(3), '<div class="fill"></div>' + ex)
    sc.src(l(2) + 0.8, end(3), "PBS American Experience, “The Trials of J. Robert Oppenheimer”")
    doc, pid = sc.paper("Internal review for the AEC General Counsel · Sept. 9, 1959", [
        ("“[[the system failed]] …", l(4) + 6.0, l(4) + 6.8),
        ("a [[substantial injustice]] was done", l(4) + 8.0, l(4) + 8.9),
        ("to [[a loyal American]].”", l(4) + 8.0, l(4) + 10.6)], 400, 270, 1120, size=60)
    sc.tilt(pid, l(4), end(4) + 0.3)
    sc.clip(l(4), end(4), '<div class="fill"></div>' + doc)
    sc.hud(l(4), end(4), "1959 · Inside the commission", "a")
    sc.src(l(4) + 0.6, end(4), "1959 memo, quoted in the 2022 Energy Department order")
    ex = sc.block(sc.label("Dec. 2, 1963", 0, 0, 36, "mono a", 770), l(5) + 0.3, 1014, 250)
    ex += sc.words("The Fermi Award.", l(5) + 2.8, l(5) + 4.0, 1010, 310, 770, 104, cls="serif n")
    ex += sc.block(sc.label("He died in 1967. The verdict stood.", 0, 0, 44, "mono dim", 770), l(5) + 6.4, 1014, 620)
    sc.plate(l(5), end(5), "fermi63_a", side="left", name="Oppenheimer and President Johnson", sub="The White House, Dec. 2, 1963", era="a", extra=ex)
    sc.hud(l(5), end(5), "1963 · The White House", "a")
    sc.hud(l(6), sc.dur - 0.4, "December 16, 2022 · U.S. Department of Energy", "n")
    ex = sc.block(sc.label("Vacated.", 0, 0, 170, "serif n", 800), l(6) + 4.4, 1000, 300)
    ex += sc.block(sc.label("After 68 years", 0, 0, 48, "mono a", 800), l(6) + 5.4, 1012, 520)
    sc.plate(l(6), end(6), "granholm", side="left", name="Jennifer Granholm", sub="U.S. Secretary of Energy · official portrait", era="n", extra=ex)
    ex = sc.block(sc.label("“a flawed process that violated the Commission’s own regulations”", 0, 0, 52, "mono dim", 1500, "center"), l(7) + 0.6, 210, 760)
    title(sc, l(7), end(7), "The process was flawed.", era="n", size=140, hi={"flawed."}, y=300)
    sc.src(l(7) + 0.4, end(7), "Statement of Secretary Jennifer Granholm, Dec. 16, 2022")
    doc_zoom(sc, l(8), end(8), "doe_order-2", [(41.7, 62.7, 46.6, 2.1, l(8) + 6.4), (11.7, 64.6, 58.2, 2.1, l(8) + 7.6)], focus=(45, 64), zoom=(0.8, 2.25), w=820)
    sc.src(l(8) + 0.5, end(8), "The actual order, page 2 · U.S. Department of Energy")
    ex = sc.words("The private life was the tool.", l(9) + 3.0, l(9) + 5.0, 160, 290, 1600, 120, cls="serif n", align="center", hi={"tool."})
    ex += sc.words("The policy was the target.", l(9) + 5.6, e(9), 160, 520, 1600, 120, cls="serif n", align="center", hi={"target."}, hicls="r")
    sc.clip(l(9), sc.dur, '<div class="fill"></div>' + ex)

def s13(sc):
    l, e, end = sc.l, sc.e, sc.end
    sc.hud(0.5, sc.dur - 0.4, "2022–2026 · The chip war", "c")
    ex = sc.words("How many chips should America sell to China?", l(2) + 3.6, e(2), 150, 300, 780, 92, cls="serif n", hi={"china?"}, hicls="c")
    sc.plate(0, end(2), "h100", side="right", name="Nvidia H100 accelerators", sub="Photo: Geekerwan, 2023", era="c", extra=ex)
    ex = sc.block(sc.label("December 2025", 0, 0, 36, "mono c", 770), l(3) + 4.6, 1014, 250)
    ex += sc.words("H200 sales to China: allowed.", l(3) + 6.0, e(3), 1010, 310, 770, 96, cls="serif n", hi={"allowed."}, hicls="c")
    sc.plate(l(3), end(3), "great_hall", side="left", name="Great Hall of the People", sub="Beijing", era="c", extra=ex)
    sc.src(l(3) + 0.6, end(3), "Al Jazeera, Nov. 9, 2026 · CNBC")
    ex = sc.words("Both parties want limits.", l(4) + 0.2, e(4), 150, 300, 770, 100, cls="serif n", hi={"limits."}, hicls="c")
    ex += sc.block(sc.label("Days after the admission, Sen. Warren urges Congress to pass them.", 0, 0, 40, "mono dim", 770), l(5) + 0.4, 154, 600)
    sc.plate(l(4), l(5) + 6.2, "warren", side="right", name="Sen. Elizabeth Warren", sub="Official portrait", era="c", extra=ex)
    title(sc, l(5) + 6.2, sc.dur, "The fight had a new weapon.", era="c", size=130, hi={"weapon."})

def s14(sc):
    l, e, end = sc.l, sc.e, sc.end
    ex = sc.words("The differences are real.", l(1) + 3.0, e(1), 160, 60, 1600, 96, cls="serif n", align="center")
    rows = [(l(2), "Status", "Government clearance", "CEO of a private company"),
            (l(3), "Secrets lost", "None ever claimed", "Not known yet"),
            (l(5), "The woman", "Never shown to be a spy", "An untested assessment"),
            (l(5) + 5.6, "Tested in court", "No", "No"),
            (l(6) + 4.0, "A subordinate", "No parallel", "Reported · a board matter"),
            (l(7), "What it needs", "Evidence", "Evidence")]
    ex += ledger_rows(sc, rows, y0=320, gap=110, head=("1954 · Oppenheimer", "2026 · Huang"))
    sc.clip(0, sc.dur, '<div class="fill"></div>' + ex)
    sc.src(l(2), sc.dur - 0.4, "2022 Energy Department order · NBC News · Al Jazeera · Axios")

def s15(sc):
    l, e, end = sc.l, sc.e, sc.end
    ex = fade_out(sc, sc.block(sc.label("Nov 18", 0, 0, 200, "serif n", 900), l(1) + 3.6, 1000, 300), end(1) - 0.2)
    qs = [("1", "Was anything actually compromised, or is there only a relationship?", l(2), e(2)),
          ("2", "Does the accused get to see the file?", l(3), e(3)),
          ("3", "Who wins the policy fight if he falls?", l(4), e(4))]
    for i, (n, q, ta, tb) in enumerate(qs):
        ex += sc.block(sc.label(n, 0, 0, 110, "serif c", 100), ta, 1000, 200 + i * 230)
        ex += sc.words(q, ta + 0.4, tb, 1110, 212 + i * 230, 700, 50, cls="serif n")
    sc.plate(0, end(4), "capitol", side="left", name="U.S. Capitol", sub="Washington, D.C.", era="c", extra=ex)
    sc.hud(0.6, end(4), "November 18, 2026 · U.S. Congress", "c")
    ex = sc.words("And if the board removes him first:", l(5), l(5) + 2.6, 160, 300, 1600, 84, cls="serif dim", align="center")
    ex += sc.words("which of the two stories was it for?", l(5) + 2.8, e(5), 160, 440, 1600, 110, cls="serif n", align="center", hi={"which"}, hicls="c")
    sc.clip(l(5), end(5), '<div class="fill"></div>' + ex)
    ex = sc.words("America skipped all three.", l(6), e(6), 160, 110, 1600, 110, cls="serif n", align="center", hi={"skipped"}, hicls="r")
    ex += box_cards(sc, [("68", "years", l(7) + 0.6, "a"), ("43", "senators", l(7) + 2.8, "a"), ("All", "living Los Alamos directors", l(7) + 4.2, "a")], y=380, w=440, h=330)
    sc.clip(l(6), end(7), '<div class="fill"></div>' + ex)
    sc.src(l(7) + 0.5, end(7), "U.S. Secretary of Energy, order of Dec. 16, 2022")
    doc, pid = sc.paper("Board findings · 1954", [("“no evidence of disloyalty”", l(8) + 2.0, None), ("Clearance: not reinstated.", l(8) + 3.0, None)], 150, 260, 760, size=42)
    doc2, pid2 = sc.paper("Board findings · 2026", [("—", l(8) + 4.4, None), ("Not yet written.", l(8) + 5.0, None)], 1010, 260, 760, size=42)
    sc.tilt(pid, l(8), sc.dur); sc.tilt(pid2, l(8) + 0.15, sc.dur)
    ex = doc + doc2 + sc.words("Watch what the next board writes.", l(8) + 3.8, e(8), 160, 740, 1600, 88, cls="serif n", align="center", hi={"next"}, hicls="c")
    ex = fade_out(sc, ex, l(9) + 0.9)
    ex += sc.block(sc.label("Era Mirror", 0, 0, 120, "serif n", 800), l(9) + 1.1, 150, 300)
    ex += sc.block(sc.label("The past, held up to the present", 0, 0, 38, "mono dim", 800), l(9) + 1.5, 156, 450)
    ex += sc.block(sc.label("Next mirror →", 0, 0, 48, "mono c", 800), l(9) + 1.9, 156, 570)
    sc.clip(l(8), sc.dur, '<div class="fill"></div>' + ex)

SCENES = {"s01": ("a", s01), "s02": ("c", s02), "s03": ("c", s03), "s04": ("a", s04), "s05": ("a", s05), "s06": ("c", s06), "s07": ("a", s07),
          "s08": ("a", s08), "s09": ("n", s09), "s10": ("a", s10), "s11": ("a", s11), "s12": ("a", s12), "s13": ("c", s13), "s14": ("n", s14), "s15": ("c", s15)}

# Sound cues: (kind, scene-local time). boom = the few big story hits, thump = numbers landing, key = typed lines.
SFX = {
    "s01": lambda sc: [("boom", sc.e(4) - 0.8), ("thump", sc.l(5) + 2.9), ("thump", sc.l(7) + 0.3)],
    "s02": lambda sc: [("key", sc.l(2) + 0.6), ("key", sc.l(2) + 1.0), ("thump", sc.l(2) + 6.0), ("thump", sc.l(5) + 3.9), ("thump", sc.l(6) + 0.2), ("thump", sc.l(10) + 3.0)],
    "s03": lambda sc: [("thump", sc.l(2) + 4.2), ("thump", sc.l(3) + 0.6), ("thump", sc.l(3) + 1.5), ("thump", sc.l(4) + 1.6), ("boom", sc.l(6) + 0.1)],
    "s04": lambda sc: [("thump", sc.l(5) + 2.2), ("thump", sc.l(7))],
    "s05": lambda sc: [("key", sc.l(3) + 2.8), ("key", sc.l(3) + 5.8), ("thump", sc.l(4) + 1.2), ("thump", sc.l(5) + 6.4), ("thump", sc.l(6) + 4.6), ("thump", sc.l(7) + 6.0)],
    "s06": lambda sc: [("key", sc.l(2) + 3.4), ("key", sc.l(2) + 7.0), ("thump", sc.l(6) + 3.6)],
    "s07": lambda sc: [("thump", sc.l(4) + 2.9), ("thump", sc.l(6) + 0.2)],
    "s08": lambda sc: [("thump", 2.0), ("boom", sc.l(4) + 3.0), ("key", sc.l(5) + 1.4), ("thump", sc.l(6)), ("key", sc.l(7)), ("thump", sc.l(8))],
    "s09": lambda sc: [("thump", sc.l(2) + 2.9)],
    "s10": lambda sc: [],
    "s11": lambda sc: [("boom", sc.l(1) + 1.8), ("thump", sc.l(3) + 1.0), ("thump", sc.l(3) + 7.8), ("thump", sc.l(4) + 2.6)],
    "s12": lambda sc: [("thump", sc.l(2) + 9.0), ("key", sc.l(4) + 6.0), ("boom", sc.l(6) + 4.4), ("thump", sc.l(8) + 6.4), ("boom", sc.l(9) + 5.6)],
    "s13": lambda sc: [("thump", sc.l(5) + 6.3)],
    "s14": lambda sc: [("key", sc.l(2)), ("key", sc.l(3)), ("key", sc.l(5)), ("key", sc.l(6) + 4.0), ("key", sc.l(7))],
    "s15": lambda sc: [("thump", sc.l(2)), ("thump", sc.l(3)), ("thump", sc.l(4)), ("thump", sc.l(6)), ("thump", sc.l(7) + 0.6), ("thump", sc.l(7) + 2.8), ("thump", sc.l(7) + 4.2)],
}
