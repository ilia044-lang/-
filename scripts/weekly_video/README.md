# Market Mind weekly edition — October 9, 2026

Authorized deliverables: 5–8 minute English weekly briefing in 1920×1080, two separately composed English Shorts in 1080×1920, burned subtitles plus SRT files, thumbnail, publishing copy and source notes. Review October 5–9; outlook October 12–16. No presenter, no automatic social-media publication.

The requested one-time GitHub Actions trigger is October 9 at 23:30 Asia/Jerusalem (20:30 UTC). The workflow must be present on the default main branch. GitHub scheduled runs may be delayed; a bounded date/time gate accepts an overnight delay. The script requires the exact October 9 equity bars and fails on stale core data. This schedule is distinct from a guarantee of completion time.

The old PLTR scheduled trigger has been removed. Its manual workflow remains for archival reruns.

Sources: Yahoo Finance OHLCV and attributed headline metadata; BLS release calendar; Nasdaq estimated earnings calendar; Treasury official yield curve; TradingView S5FI snapshot when available. Explicitly label missing sources, dated observations, calendar estimates and Bitcoin's continuously traded snapshot. The user's intraday screenshot is a watchlist reference, not closing-price evidence. October statistics use 15 completed Octobers, 2011–2025, from adjusted month-end prices. Current October is excluded.

Rendering: verified-hash Kokoro models, deterministic animated Python/Pillow graphics, FFmpeg, original ambient audio, generated editorial artwork, timing from each synthesized caption unit. Two workers render chunks no longer than 14 seconds. Final validation covers dimensions, duration, complete video decoding, audio timing, motion and subtitles. No secrets are needed beyond GitHub's job token to publish a delivery branch.

Run a short end-to-end preview:

```bash
python scripts/weekly_video/run.py --date 2026-10-08 --out /tmp/weekly-preview --smoke
```

Production after the specified close:

```bash
python scripts/weekly_video/run.py --date 2026-10-09 --out /tmp/weekly-final --attempts 12
```

Final files are published to `deliveries/WEEKLY-2026-10-09`. Short automation tests go to `previews/WEEKLY-2026-10-09` and are explicitly labelled. Neither branch is a promise that a future run has already completed.
