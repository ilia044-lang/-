# PLTR cloud video

The requested cloud run is scheduled for **October 8, 2026 at 23:30 Asia/Jerusalem (20:30 UTC)**. GitHub Actions runs independently of the user's computer or this chat. Scheduled jobs can be delayed by GitHub; 23:30 is the requested trigger, not an exact completion-time guarantee.

The workflow is `.github/workflows/pltr-video.yml` and must be present on the default `main` branch for scheduling to work. Cron has no year field, so the workflow accepts the scheduled UTC date and the following UTC day before starting, so a delay across midnight does not skip production; later annual triggers exit without producing a video.

Outputs after the October 8 close is available:

- Branch `deliveries/PLTR-2026-10-08`: animated MP4, cover PNG, TikTok caption, YouTube title/description, source notes and validation receipt.
- The Actions run also retains an artifact for 30 days.
- Nothing is uploaded to YouTube or TikTok automatically.

Main-branch pushes register configuration without producing a video. A push to `codex/pltr-recovery-2026-10-08` runs production for the required October 8 close. Blank-date manual runs produce an end-to-end preview using the latest completed session. Preview output goes to `previews/PLTR-<date>` and is clearly labelled as a test, separate from the scheduled final video. Manual runs can require an explicit completed trade date.

Runtime: Python 3.12, FFmpeg, DejaVu fonts, pinned Python dependencies, Kokoro ONNX English narration and the checked-in bull/bear background. The speech model downloads from the original public GitHub release over verified TLS. No paid API credential or personal token is required. The workflow's short-lived `GITHUB_TOKEN` receives `contents: write` solely to save generated outputs in this repository.

Data: Yahoo Finance historical daily OHLCV. The scheduled run requires the exact October 8 bar and retries if the feed lags; it fails rather than pretending an older close is current. Indicators and annotation levels are calculated from the returned daily history. News uses attributable headline metadata from the last 14 days; missing facts are disclosed, and an earnings date is not invented. Market values are not animated as simulated live ticks; drawing tools, the viewport and explanatory overlays animate.

Local execution:

```bash
python -m pip install -r scripts/stock_video/requirements.txt
python scripts/stock_video/run.py --ticker PLTR --date 2026-10-08 --out /tmp/pltr-video --attempts 12
```

Omit `--date` for a preview of the latest completed session. Keep outputs outside the source checkout. Every render validates the dated input, indicator calculations, expected frame counts, complete decoding, dimensions and audio/video duration. All numerical labels and candles are drawn in code.
