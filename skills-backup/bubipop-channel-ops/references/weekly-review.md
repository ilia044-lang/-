# Weekly review procedure

Read this when running a channel review, or when Ilia asks "what's happening
with the channel" / "check my numbers" / "מה קורה עם הערוץ".

The point of a fixed procedure is that it produces comparable numbers week over
week. Improvised reviews produce impressions, and impressions at this channel
size are almost always wrong — a single video moving 200 views feels like a
trend and isn't one.

## Step 1 — Pull the data

Open YouTube Studio in Chrome and read the dashboard:
`https://studio.youtube.com`

If the Chrome extension isn't connected, stop and tell him. Do not fill the gap
from memory or from the last review — stale numbers produce confident wrong
advice, which is worse than no advice.

Capture, at minimum:

- Subscribers (total, and change over 28 days)
- Views (28 days)
- Watch hours (28 days)
- Average view duration — compute views ÷ watch time if not shown directly
- Top content (48 hours and 28 days)
- The most recent upload's first-day performance and its ranking out of 10

Then go one level deeper on the top video: **traffic sources**. This is the
single most informative screen on the channel right now, because it answers
whether views came from the Shorts feed (algorithmic, repeatable), browse
(algorithmic, repeatable), or external/direct (a one-off share, teaches nothing).

## Step 2 — Compute the ratios

Absolute numbers at this size are noise. Ratios are signal:

- **Seconds per view** = watch hours × 3600 ÷ views.
  Below ~15 seconds on Shorts means viewers are swiping away. This is the
  number that determines whether YouTube pushes anything.
- **Subscriber conversion** = new subs ÷ views.
  At 1 sub per 111 views, effectively nobody is converting.
- **Concentration** = top video's views ÷ total views.
  If one video is >70% of traffic, the channel is not growing — one video is.

## Step 3 — Compare to last week

Write down the deltas. If deltas are flat or negative and a change was made last
week, the change didn't work — say so directly rather than looking for an
encouraging reading of the data.

If no change was made last week, that's the finding: nothing was tested, so
nothing was learned.

## Step 4 — Name the single binding constraint

Pick exactly one from:

- **Retention** — people click but leave. Fix the first 3 seconds, pacing, or
  the payoff. Symptom: low seconds-per-view.
- **Packaging** — people don't click. Fix title and thumbnail. Symptom:
  impressions exist but CTR is low.
- **Distribution** — nobody sees it at all. Symptom: near-zero impressions.
  Usually downstream of retention on a small channel, because YouTube stops
  showing content that doesn't hold.

Naming five problems is the same as naming none. Pick the one that, if fixed,
makes the others matter.

## Step 5 — One change, one window

Recommend a single change with:
- what changes
- what stays fixed (everything else)
- the success criterion, as a number
- the date to check

Two-week windows are the default for format changes. A single upload is not a
test — it's a data point with enormous variance at this scale.

If a window is currently open, the recommendation is to wait, and the reason
should be stated: abandoning tests early is the specific habit that prevents
learning. He has asked to be stopped on this.

## Step 6 — Report

Use the template in SKILL.md, in Hebrew. Keep it short. Include what *not* to do
this week — for an impatient operator that line does more work than the
recommendation itself.

## Optional — competitive context

When the format question is genuinely open (Gate 0/1), vidIQ helps:

- `vidiq_outliers` with a kids/animation keyword — what's breaking out now
- `vidiq_similar_thumbnails` — how common a visual concept is
- `vidiq_keyword_research` — whether anyone searches the topic at all

Use this to inform format decisions, not to generate a list of videos to copy.
Copying a format without understanding why it retains produces the same
0-2 view results at higher volume.
