# Precision prompting for MiniMax H3 / Hailuo

Read this before writing any prompt more complex than a single character in a
static shot. It synthesizes patterns that converge across independent
prompting guides for this specific model family, plus what actually failed
and got fixed on this project (the S12B ice-cream scene). Treat it as the
authoritative method — the other reference files describe *what* to put in a
prompt; this one describes *how much at once* and *in what order*.

## The core principle: treat the prompt as a spec for change over time

A weak prompt describes what the video should look like. A strong prompt
describes **what changes, in what order, and what the end state is** — cause
and effect, not a snapshot. Every prompt in this project should be readable
as a short sequence of state transitions, not a mood board in prose.

## Add complexity in stages — this is the single most important rule

Every one of the failures on this project so far (the confused first slide
attempt, the frozen-object ice cream handoff, the overlapping five-way
dialogue) came from stacking too many kinds of complexity into one
generation at once. The fix isn't cleverer wording — it's fewer simultaneous
demands on the model.

**The dimensions of complexity, roughly in order of how much they strain a
single generation:**
1. Number of named characters in frame
2. Number of characters speaking
3. Object handoffs / physical state changes
4. Camera movement complexity (static < push-in < tracking < multi-move)
5. Number of distinct beats/actions within the shot

**Rule of thumb:** a shot can carry *one or two* of these at high complexity,
not all of them at once. A five-character shot with an object handoff *and*
three-way dialogue *and* a tracking camera is exactly the failure pattern we
saw — pick which one or two matter most for this beat and simplify the rest.

When a shot genuinely needs several complex elements (the ice cream moment
does: five characters, a handoff, dialogue), don't fight the model into doing
it all naturally in one pass — **over-specify relentlessly** instead (see the
handoff and dialogue-timing sections in `prompt-craft.md`), and expect to
need a retry or two. That's a deliberate tradeoff, not a failure.

## Structure every prompt as six questions, answered in order

1. **Opening frame** — what does the shot look like at 0:00, concretely?
   Framing, subject position, setting, light. State this before any action
   starts, the same way a shot description in a screenplay opens on a still
   before the verbs begin.
2. **Visible action** — what changes, described as cause and effect, in
   chronological order.
3. **Camera path** — one primary movement, named and sequenced, not a list of
   camera-move vocabulary. "Push in, then hold" is readable; "dolly, orbit,
   push, pan" with no order is not.
4. **Lighting and style** — only after the shot itself is clear. Style labels
   on top of an ambiguous action don't fix the ambiguity.
5. **Sound, dialogue, and timing** — with explicit timestamps whenever more
   than one thing happens (see timestamp format below).
6. **Ending state** — what the frame looks like when the shot ends. State it
   explicitly; don't let the last described action imply it.

## Timestamp format — precise rules, not just "early / then / later"

When a shot has more than one beat, use explicit numeric timestamps in
`0.0-2.0s` style (or `00:00.000` for longer multi-shot sequences), and follow
these constraints:

- **Ranges must be sequential — no gaps, no overlaps.** The end of one range
  is the start of the next.
- **The first range starts at 0.0s; the last range ends at the shot's total
  duration.** Don't leave an undescribed tail.
- **Each beat should be roughly 1.5–5 seconds.** Shorter than about 1.5s
  doesn't give the model enough frames to render the beat distinctly; much
  longer than 5s and a single beat starts absorbing more than one idea.
- For dialogue specifically, state explicitly who is silent during each
  other speaker's window (see `prompt-craft.md`'s multi-speaker section) —
  the timestamp alone doesn't guarantee the other characters stay quiet.

## Reference roles — name what each image controls, explicitly

"Give every reference a clear role" is the single most repeated piece of
advice across independent guides for this model. When multiple reference
images are attached, don't just list them — for any prompt where it isn't
obvious, state what each one is *for*:

```
@Image1 controls Bubi's identity — face, colour, proportions, no backpack.
@Image2 controls Maya's identity — face, colours, proportions, clothing.
```

This project's convention of "@ImageN is the strict character reference for
X" already does this. Keep doing it explicitly even as the reference count
grows — don't let it collapse into a bare list once there are four or five
images attached.

## Iterating on a near-miss — change one thing at a time

When a generation is close but not right, resist rewriting the whole prompt.
**Keep every part that worked and revise only the specific element that
failed** — camera, one action beat, one line of timing, the ending state.
Changing several things at once on a retry makes it impossible to tell which
change fixed (or broke) the result, and burns credits on generations that
don't isolate the actual problem.

This is why the earlier slide-rule debugging in this project (isolating
"is it the girl's position" from "is it the queue-and-push staging") worked —
each retry changed exactly one variable.

## Applying this to the ice cream shot (S12B) specifically

The revised S12B prompt already applies most of this:
- Explicit opening state (Mom and Dad each hold two cones, named hand)
- Explicit handoff timestamps with named hands and stated end-empty state
- Explicit sequential dialogue timestamps with stated silence
- Capped speaking cast to three rather than five

What it's still stacking: five characters in frame, a handoff, *and*
sequential dialogue, all in one 10s shot — three complexity dimensions at
once, at the upper edge of what one generation should carry. If results are
still inconsistent after the retry, the next simplification is to **split
the beat into two shots**: one for the handoff (no dialogue), one for the
thank-yous (no handoff, cones already distributed) — trading one dense shot
for two simple, reliable ones. That trade is usually worth it for anything
this layered.
