# Sources and methods

Trade date: 2026-10-09. Analysis date: 2026-10-12.

Market source: https://query2.finance.yahoo.com/v8/finance/chart/IREN?range=2y&interval=1d
Retrieved: 2026-10-12T07:34:59.348031+00:00

The required dated historical daily bar is used consistently for OHLCV. SMA20/50/150/200 are arithmetic means of complete daily closes. RSI14 and ATR14 use Wilder smoothing initialized by 14-period arithmetic averages. CCI14 uses typical price and mean absolute deviation with scale constant 0.015. All calculations use two years of history. The candle body, wicks and close position are computed directly from OHLC. Relative volume uses the last 20 sessions including this session. Confirmed swings compare three bars on each side. A rising support line is shown only if observed subsequent lows do not cross below it; otherwise a labelled horizontal historical-low reference is used.

News: reported headlines in the last 14 days with title, publisher and publication timestamp; full articles are not independently verified. Missing positive/risk items and an unverified earnings date are disclosed. The headline categories are editorial, not assertions of price causality.

Animated camera and drawing tools do not represent real-time ticks. Historical data remains fixed. English narration is synthetic, with no voice cloning. Music is an original synthesized ambient bed. All text and numbers are drawn in code; the bull/bear background contains no numeric data.

Raw market data, reviewed daily.csv, analysis.json and timing.json are retained in the workflow artifact.

- positive: [Stocktwits reports speculation linking IREN to Anthropic; no confirmed deal verified.](https://finance.yahoo.com/technology/ai/articles/irens-mystery-customer-anthropic-fresh-015734164.html), Stocktwits via Yahoo Finance headline feed, 2026-10-12T01:57:34+00:00.
