# Publishing checklist

Run this before any upload, and when Ilia asks for help with a title, thumbnail,
description, or "should I publish this".

This checklist exists because of a documented failure on the channel: the
single best-performing video went live titled
`BubiPop Bubble Beat Full Adventure.mp4` — the raw filename with the extension
still attached. The channel's only working asset was packaged like a file
transfer. Everything below is cheaper than repeating that.

## Blocking checks — do not publish if any fail

- [ ] **Title is a title, not a filename.** No `.mp4`, no underscores, no
      export naming, no version numbers.
- [ ] **Made for Kids designation is correct.** Misclassification carries FTC
      exposure and YouTube now reclassifies retroactively. If the content is
      clearly directed at under-13s, it's Made for Kids. Don't game this.
- [ ] **The first 3 seconds contain the hook.** On Shorts, the decision to stay
      is made before a viewer has consciously processed the video. If the first
      3 seconds are a logo, an intro, or a slow establishing shot, re-cut it.
- [ ] **Content isn't mass-produced-looking.** Under the "inauthentic content"
      policy, a run of near-identical generated shorts is a demonetization
      risk. If this upload is the fifth variation of the same template, the
      answer is to make something different, not to publish it.

## Packaging

- [ ] **Title** is under ~60 characters, front-loads the concept, and is
      readable by a parent scanning a feed. Score it with `vidiq_score_title`
      if useful, but treat the score as a hint, not a verdict.
- [ ] **Thumbnail** has one clear subject, high contrast, and reads at phone
      size. Check with `vidiq_score_thumbnail`. For Shorts the first frame
      often serves as the thumbnail — verify what it actually shows.
- [ ] **No reliance on disabled features.** End screens, cards, comments, and
      the notification bell do not exist on Made for Kids content. Don't write
      a call to action that depends on them ("comment below" is dead text).
      Verbal "watch the next one" plus strong end-of-video pacing is what's
      left.
- [ ] **Description** states what the video is in the first line. Nobody reads
      past it, but the first line is indexed.

## Positioning

- [ ] **Educational angle considered.** Educational kids content and toy-adjacent
      content command higher CPMs than generic animation, because advertisers
      are reaching parents with purchase intent. "Bubi Learns Electrical Safety"
      is worth more per view than "Bubi's Magical Adventure Part 5" — same
      effort, better economics. Prefer the educational framing when the content
      allows it honestly.
- [ ] **Part numbers questioned.** "Part 5" tells a new viewer they've missed
      four things. On a channel with no returning audience, sequential
      numbering suppresses clicks. Number things only once there's a reason to
      come back.

## After publishing

- [ ] Note the publish time and the current test window.
- [ ] Check first-24-hour performance and where traffic came from.
- [ ] Do **not** change the title or thumbnail within the test window unless
      performance is zero — mid-test edits destroy the ability to read the
      result.
- [ ] Log what was different about this upload, in one line. Without a log,
      week four looks exactly like week one.
