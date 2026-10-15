# Sources and methods

Trade date: 2026-10-15. Analysis date: 2026-10-15.

Market source: https://query1.finance.yahoo.com/v8/finance/chart/USO?range=2y&interval=1d
Retrieved: 2026-10-15T20:38:08.267450+00:00

The required dated historical daily bar is used consistently for OHLCV. SMA20/50/150/200 are arithmetic means of complete daily closes. RSI14 and ATR14 use Wilder smoothing initialized by 14-period arithmetic averages. CCI14 uses typical price and mean absolute deviation with scale constant 0.015. All calculations use two years of history. The candle body, wicks and close position are computed directly from OHLC. Relative volume uses the last 20 sessions including this session. Confirmed swings compare three bars on each side. A rising support line is shown only if observed subsequent lows do not cross below it; otherwise a labelled horizontal historical-low reference is used.

News: reported headlines in the last 14 days with title, publisher and publication timestamp; full articles are not independently verified. Missing positive/risk items and an unverified earnings date are disclosed. The headline categories are editorial, not assertions of price causality.

Animated camera and drawing tools do not represent real-time ticks. Historical data remains fixed. English narration is synthetic, with no voice cloning. Music is an original synthesized ambient bed. All text and numbers are drawn in code; the bull/bear background contains no numeric data.

Raw market data, reviewed daily.csv, analysis.json and timing.json are retained in the workflow artifact.

- positive: [U.S. Crude Futures Gain on Potential Tanker Relief, Inventory Draw](https://finance.yahoo.com/m/ba12c28c-2e85-3987-9a8e-d3538add3666/u.s.-crude-futures-gain-on.html), The Wall Street Journal, 2026-10-15T19:53:00+00:00.

- risk: [Canada Commodities: Oil Prices Mixed as Middle East Fighting Continues; Gold Climbs](https://finance.yahoo.com/markets/commodities/articles/canada-commodities-oil-prices-mixed-134822284.html), MT Newswires, 2026-10-15T13:48:22+00:00.


Edition-specific corrections: support is the latest ten-session low, not an automatically confirmed bottom. News slots are ITEM 1 / ITEM 2, not positive / negative sentiment judgments. All relevant feed records and query sources are preserved in news_review.json. USO futures exposure differs from spot oil.
