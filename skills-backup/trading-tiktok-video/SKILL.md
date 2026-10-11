---
name: trading-tiktok-video
description: Produce finished, ready-to-upload vertical (9:16) educational trading videos for Ilia's TikTok channel — accurate code-rendered candlestick/price charts, AI voiceover (free Kokoro model), original background music, all mixed into one MP4. Use this skill whenever Ilia asks for a TikTok/Reels/Shorts video about any trading or stock-market concept (candles, trends, support/resistance, order types, stop loss, indicators, risk management, "What is X?", "How to spot Y?"), gives a topic title in English, asks to redo/improve one of these videos, or asks for a Grok/AI video prompt about trading — even if he doesn't say "skill". Prefer this over Grok/AI video generators for anything involving charts, because generators draw inaccurate candles.
---

# Trading TikTok Video Pipeline

Everything here is free: Python + matplotlib for visuals, Kokoro (open-source) for voice, generated music, ffmpeg for mixing. Never introduce a paid service unless Ilia explicitly asks.

## Why code, not Grok
Grok and similar generators were tested and failed: they drew lines instead of candles, missed red candles, and cannot place labels accurately. Chart accuracy is the channel's credibility — an experienced trader in the comments will spot a wrong chart. Use Grok only for decorative non-chart b-roll if ever.

## Workflow (follow in order)

1. **Script first (5–6 short narration lines, English).** Structure: hook question → concept step 1 → step 2 → the twist/trap (e.g. "a wick is not a break") → summary rule → risk-management line when relevant. Keep each line under ~12 words. Content must be technically correct and show both sides (e.g. market order: fill guaranteed, price not; limit: price guaranteed, fill not). No hype, no profit promises.
2. **Generate voice BEFORE animating** with `vidlib.tts(lines)`, read durations, then `vidlib.schedule()` (or hand-tune) start times. The animation timeline is built around the voice, never the reverse — this is what made the videos feel synced.
3. **Design the chart data by hand** (explicit OHLC tuples) so the lesson is unambiguous: e.g. uptrend = green waves + small red pullbacks with clearly higher highs/lows. Map every visual beat to the narration line that describes it.
4. **Render** with matplotlib FuncAnimation at 1080×1920, 30 fps (`vidlib.save_anim`). Start from the closest example in `scripts/examples/` and adapt it rather than writing from scratch.
5. **Preview frames** with `vidlib.preview()` and LOOK at them. Fix label/candle overlaps, text leaving safe zones, confusing elements. Iterate until clean — it always needed at least one fix pass.
6. **Music + mix:** `vidlib.make_music(path, total_duration)` then `vidlib.mix(video, wavs, starts, out, music=...)`. Extend the video (ffmpeg `tpad=stop_mode=clone`) if the last line runs past the animation.
7. **Deliver** to `/mnt/user-data/outputs/<topic>_tiktok.mp4` with present_files, then a short Hebrew summary: timeline of what happens when, one professional note, one suggestion for the next topic.

## Style rules (channel identity — keep consistent)
- Theme constants in `vidlib.py` (dark navy BG, green/red candles, gold = highs/key points, blue = lows/limit, white = lines). Same look every video.
- Title at top (`TITLE_Y`), chart in `CHART_RECT`, one caption at `CAPTION_Y`. Keep all text between y=0.13 and y=0.88 of the frame — TikTok UI covers the rest.
- End card: rounded box with the one-sentence rule (e.g. "Higher Highs + Higher Lows = UPTREND").
- Voice: `am_michael` (calm male) by default; `af_heart` if Ilia asks for female.
- Length: 15–30 s. Labels short (1–3 words). Captions ≤ 6 words.
- 3D option: `examples/uptrend_3d_orbit.py` (extruded candles + orbiting camera). Best as a 2–3 s eye-catching opener, then switch to flat 2D for the explanation — 3D makes precise labels hard.

## Examples (proven, working)
- `scripts/examples/uptrend_2d.py` — candles grow in, HH/HL dots, trend line, end card.
- `scripts/examples/support_break.py` — story format: holds → false wick → real break → retest → support becomes resistance.
- `scripts/examples/market_vs_limit.py` — multi-scene (buttons → market slippage → limit fill / no fill → comparison cards).
- `scripts/examples/uptrend_3d_orbit.py` + `candles3d_helpers.py` — 3D candles.
Examples use absolute paths from the original session; adjust paths and import `vidlib` for voice/music/mix.

## Gotchas
- Download Kokoro files sequentially (parallel curl lost a file once). `setup_voice()` handles it.
- Hugging Face is blocked in the sandbox; model files come from GitHub releases (URLs in vidlib).
- ✓ ✗ → ≠ glyphs render fine in DejaVu Sans.
- When a label collides with candles, move it into empty chart space (extend xlim to create room) instead of shrinking it.

## Scope limits to state honestly when asked
- No connector exists for posting to or reading Ilia's own TikTok account; he uploads manually (free, ~1 min). vidIQ (already connected) can research what performs in the TikTok/Instagram trading niche.
- TikTok Creator Rewards is not available in Israel (as of 2026: US, UK, DE, FR, JP, KR, BR, MX). Do not suggest switching account region — it violates TikTok terms. Profitability paths are indirect (audience → own tools/products/affiliates), and take months.
