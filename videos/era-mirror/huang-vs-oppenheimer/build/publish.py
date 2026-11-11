#!/usr/bin/env python3
"""Write out/PUBLISH.md: title, description with chapters from the real timeline, tags, Shorts text."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
T = {s["id"]: s for s in json.load(open(ROOT / "build/timeline.json"))["scenes"]}
def mmss(x): x = int(x); return f"{x // 60}:{x % 60:02d}"
CH = [("s01", "One night in 1943"), ("s02", "What is confirmed about Jensen Huang"), ("s03", "Why one man moves a market"), ("s04", "Oppenheimer and Jean Tatlock"),
      ("s05", "The 24 charges"), ("s06", "The file came first"), ("s07", "A hearing rigged before it began"), ("s08", "“Because I was an idiot”"),
      ("s10", "Rabi and Teller"), ("s11", "Loyal, and removed anyway"), ("s12", "2022: the government takes it back"), ("s13", "The chip fight around Huang"),
      ("s14", "How the two cases differ"), ("s15", "Three questions for November 18")]
chapters = "\n".join(f"{mmss(0 if k == 's01' else T[k]['start'])} {name}" for k, name in CH)
credits = (ROOT / "assets/CREDITS.md").read_text(encoding="utf-8").split("```")[1].strip()
out = f"""# Publish kit — Era Mirror: Huang 2026 vs Oppenheimer 1954

## Title (pick one)

1. **Nvidia's Spy Scandal Already Happened in 1954** — 45 characters, title.py score 94
2. The 1943 Night That Explains the Nvidia Spy Scandal — 51 characters, score 94
3. America Took 68 Years to Admit This. It's Happening Again — 57 characters, score 94

## Thumbnail

- `thumbnails/thumb-A-it-happened-before.png` — text: IT HAPPENED BEFORE
- `thumbnails/thumb-B-loyal-ruined-anyway.png` — text: LOYAL. RUINED ANYWAY

The Huang photo is CC BY-SA 4.0 (Anderseidesvik): keep the credit line in the description.

## Description

```
Jensen Huang admitted an affair with a woman U.S. intelligence believes was recruited by China. In 1954, America put Robert Oppenheimer through the same kind of closed hearing, and in 2022 the government took the verdict back.

This video puts the two cases side by side, using the original 1953 charge letter, the 1954 hearing transcript and the 2022 Department of Energy order. What is confirmed, what is only reported, and what the 1954 case says to watch for on November 18.

{chapters}

What is confirmed and what is not (as of November 11, 2026):
- Confirmed: Huang's memo to staff of Nov. 8, 2026, and the Nvidia board's independent investigation.
- Reported, not proven: that Alice Huang was recruited by Chinese intelligence (New York Times, NBC News). No one has been charged. China denies it. Nvidia's board says it has no reason to believe secrets were compromised.

Sources:
Nvidia newsroom, "A Message to Our Company" and board statement, Nov. 8, 2026
NBC News, Al Jazeera, CNBC, Fortune, Axios, Yahoo Finance, Nov. 8-11, 2026
AEC letter of charges, K. D. Nichols to J. R. Oppenheimer, Dec. 23, 1953
"In the Matter of J. Robert Oppenheimer", hearing transcript, 1954
U.S. Secretary of Energy, order vacating the 1954 decision, Dec. 16, 2022
PBS American Experience, "The Trials of J. Robert Oppenheimer"
Atomic Heritage Foundation, "Oppenheimer Security Hearing"

{credits}

Audio tracks: English, Russian, Spanish, Mandarin.
```

## Tags

```
Jensen Huang, Nvidia, Nvidia spy scandal, Alice Huang, Megaspeed, Oppenheimer, Oppenheimer security hearing, 1954, Lewis Strauss, Jean Tatlock, Edward Teller, chip export controls, China chips, history explained, Era Mirror
```

## The three searches this video should win

1. nvidia spy scandal explained
2. jensen huang oppenheimer
3. oppenheimer security hearing 1954

All three are covered by the title plus the first two lines of the description.

## Extra audio tracks and subtitles

Upload `huang-vs-oppenheimer-EN.mp4`, then in YouTube Studio → Languages add the audio files `audio_ru.m4a`, `audio_es.m4a`, `audio_zh.m4a` and the matching `subtitles_*.srt`. On-screen text stays in English in every version.

## Short 1 — `short-1-one-night-1943.mp4`

- Title: One night in 1943 ended his career. Now it's Nvidia's CEO
- New first line: "In 1943, Army agents sat outside a woman's apartment all night."
- On screen in the first two seconds: ONE NIGHT. 1943
- Loop: the last line ("it took sixty-eight years to take it back") sets up the first.
- Description: Full story: Nvidia's Spy Scandal Already Happened in 1954 (link the long video as the related video).

## Short 2 — `short-2-seven-days-no-defense.mp4`

- Title: The prosecutor spent a week alone with the judges
- New first line: "In 1954, the prosecutor spent a week alone with the judges."
- On screen in the first two seconds: 7 DAYS. NO DEFENSE.
- Loop: the last line names Oppenheimer and Nvidia, the first line is the 1954 hearing.
- Description: Full story: Nvidia's Spy Scandal Already Happened in 1954.

## Before you press publish

1. Check the news for Nov. 16-18 (earnings, the House briefing). If Huang resigns, is charged or is cleared, the opening and the last scene need an update.
2. Nvidia's Q3 earnings date is reported as Nov. 16 by one outlet and Nov. 17 by another. The film does not state it.
3. The "$1.7 trillion" figure is not in the film: it is measured from the October 6 record high, before the scandal.
"""
(ROOT / "out/PUBLISH.md").write_text(out, encoding="utf-8")
print("PUBLISH.md written")
