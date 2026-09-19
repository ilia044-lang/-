# Prompt craft — Hailuo / MiniMax H3

Read this before writing any clip prompt.

## The four-layer motion rule

Every prompt must specify motion in all four layers. This is the fix for frozen
and near-static clips, and it works because the model needs an explicit motion
anchor in each layer or it defaults to holding that layer still.

1. **Character motion** — what the body does, as a continuous action
2. **Secondary motion** — wings, hair, cloth, dust, bubbles, sparkles, water
3. **Environment motion** — grass, clouds, leaves, light shifting
4. **Camera motion** — a slow push in, orbit, tilt, or track

If you cannot name all four, the prompt is not finished.

## Prompt skeleton

```
[STYLE BLOCK — verbatim, unchanged every clip]
[CHARACTER BLOCK — verbatim, unchanged every clip]

Action: <one continuous action, present tense>
Secondary motion: <what else moves>
Environment: <setting + what moves in it>
Camera: <one camera move, slow>
Lighting: <consistent across the film>
Duration: <4-15s>
```

## Rules that matter

**One action per clip.** Two actions in a 15-second clip produce a morph in the
middle where the model tries to transition between them. If the beat needs two
actions, it needs two clips.

**Present continuous, always.** "Bubi flaps his wings and rises" generates
motion. "Bubi in a meadow" generates a photograph with parallax. Verbs are the
motion anchor — a prompt whose main clause is a noun phrase will come back
static almost every time.

**Never request a scene change mid-clip.** No "then the scene changes to," no
"cut to," no "afterwards." The model doesn't cut, it morphs, and morphing is
the artifact that makes AI animation look broken.

**Never request on-screen text.** Generated text comes out garbled. All text is
added at assembly as an overlay, where it's sharp and controllable.

**Keep the camera slow.** Fast camera moves plus a character action exceeds
what the model tracks coherently and produces smearing. One slow move per clip.

**Say what you want, not what you don't.** Negative phrasing ("no blurry
background") is unreliable across these models. Describe the positive state:
"crisp background, sharp focus throughout."

## Populate the world — count everything

A prompt that names only the main characters returns an empty world. An empty
playground, an empty street, an empty classroom — it reads as eerie and
unfinished, and it is one of the most common reasons generated footage looks
cheap.

**Never write a vague background character.** "Another child in the background"
gives the model no count, no identity and no action, so it invents — often the
same character twice, or the main character duplicated.

Instead, state exactly: **how many, who, where in frame, and what each is
doing.**

Weak: `another child is already sliding down in the background`

Strong: `Background, out of focus: three other children play — one boy in a red
shirt swings gently on the left, two girls chase each other near the sandpit on
the right. Two adults sit on a bench in the far background. Each background
character is a distinct person; none of them duplicates a main character.`

## Diversity in background characters — mandatory

A generic "child" instruction, even a well-specified one, tends to return
visually similar background characters — same skin tone, same build, same hair
— because the model defaults to a narrow interpretation unless told otherwise.
The result reads as clones or twins, which breaks the sense of a real, lived-in
world and is a second, subtler version of the duplication problem above: not
the same character rendered twice, but different characters who all look like
siblings.

**Every background-population block must specify a visibly diverse cast.**
Vary at minimum: skin tone and ethnicity, hair type and colour, build, and age
within the "child" range (toddler through ~10). Mix in incidental figures
beyond children — a parent with a stroller, an elderly grandparent on a bench,
a dog on a leash — both because real playgrounds have them and because they
break up visual repetition even further.

Worked example:

```
Background, softly out of focus: a Black boy in a red shirt swings gently on
the left; an East Asian girl and a girl with red pigtails chase each other near
the sandpit on the right; a South Asian toddler in overalls sits in a sandbox
supervised by their mother, who pushes an empty stroller nearby; an elderly
man reads on a bench in the far background; a small dog on a leash sniffs the
grass near the fence. Each figure is visually distinct in skin tone, hair, and
build; none resembles another.
```

Reuse this level of specificity in every playground or crowd shot. It costs
nothing extra to generate and materially improves how alive and real the world
feels — and it avoids an all-same-looking background cast reading as
accidentally exclusionary, which undermines a channel selling itself to a wide
audience of parents.

## Lock the background cast per scene — never re-invent it per shot

This is as important as locking the main characters, and it's a mistake that's
easy to make by accident: writing a *fresh* background-population block for
each new shot, even a well-diversified one, silently swaps out who's in the
world from shot to shot. The result is a series of similar-but-different
playgrounds rather than one continuous place — extras who were on the bench
in shot 2 are gone in shot 4, replaced by a mother with a stroller who was
never there before. Viewers feel this as "the scenes don't connect," even
when they can't name why.

**The fix: write the background-population block once per scene/location, then
paste it verbatim into every shot in that scene** — exactly like the character
and voice blocks. If the scene runs long enough that background figures should
plausibly move (a swinger finishes and leaves, a new child arrives), change it
deliberately and once, not shot-by-shot by accident.

Add the same explicitness to any recurring element: how many benches, how many
trees, whether the sky has birds.

## Pacing — stop the slow-motion default

These models drift toward slow, floaty, dreamlike motion. For kids content that
reads as lifeless and drags retention down.

Put a pacing instruction in every prompt:

```
Natural real-time speed, lively and energetic, normal human motion, no slow
motion, no dreamlike floating, no time-lapse. Characters move with real weight
and momentum.
```

For a character action, name the tempo: "quickly but gently", "in one brisk
step", "with a small bounce". Vague verbs produce vague, slow motion.

## Multi-character scenes — object handoffs and overlapping dialogue

Two specific failure patterns showed up once scenes grew past two characters
(a five-character ice-cream scene): a physical object described as changing
hands stayed with the giver instead, and dialogue meant to be sequential came
out overlapping, making individual lines hard to follow. Both are common,
documented failure modes for AI video models, not unique to this project —
and both have a specific fix.

### Object handoffs need before/after states, not a verb

"Mom hands one to Maya" describes an event, not a physical state change, and
the model has nothing to anchor the object's position to at the end of the
shot. Models are much more reliable when the handoff is written as an
explicit state transition, naming the hand on each side:

Weak: `Dad hands Leo an ice cream cone.`

Strong: `Dad's ice cream cone starts in his RIGHT hand. Leo reaches up with
his LEFT hand. Dad places the cone into Leo's LEFT hand. By the end of the
action, Leo is holding the cone in his left hand and eating it; Dad's right
hand is now empty.`

State the **end state** explicitly ("Dad's hand is now empty," "Leo is now
holding the cone") — don't rely on the handoff verb alone to imply it.

### Multi-speaker scenes need explicit sequential timing, not a stacked list

Listing several lines of dialogue in sequence in the prose ("Maya says X, Leo
says Y, Bubi says Z") reads to the model as roughly simultaneous unless the
timing is broken out. This is a known limitation across AI video/dialogue
models — natural conversational overlap is the default the model reaches for
unless told explicitly not to.

**Fix: give each line an explicit time window within the shot, and state that
every other character is silent during it.**

Weak (what produced the overlap problem):
```
Maya says brightly: "Thank you, Mom!" Leo grins and says: "Yes! Ice cream!"
Bubi says warmly: "Thank you so much!"
```

Strong:
```
0.0–2.5s: Maya speaks alone: "Thank you, Mom!" Leo and Bubi are silent,
reacting with expressions only.
2.5–5.0s: Leo speaks alone, immediately after Maya finishes: "Yes! Ice cream!"
Maya and Bubi are silent.
5.0–7.5s: Bubi speaks alone: "Thank you so much!" Maya and Leo are silent,
already starting to eat.
```

State outright: **"Dialogue is strictly sequential — only one character
speaks at a time, with no overlap. Every character who isn't speaking is
silent."** This one sentence, placed near the audio direction, is worth more
than careful timing alone.

### Cap speaking characters per shot

Even with perfect sequential timing, five characters each getting a line in
an 8–10 second shot leaves under 2 seconds per line — too tight for clear
delivery at the brisk-but-clear pacing this project uses (see the dialogue
pacing section above). **Prefer 2–3 speaking characters per shot.** If a
beat genuinely needs more voices, split it into two shots rather than
compressing every character's line into one.

### General MiniMax H3 precision checklist

Before submitting a multi-character prompt on this site, check:

- [ ] Every physical object transfer states the start hand, the end hand, and
      the end state explicitly.
- [ ] Every line of dialogue has an explicit time window and names who is
      silent during it.
- [ ] No more than 2–3 characters speak in a single shot; more voices means
      split the shot.
- [ ] The sentence "dialogue is strictly sequential, no overlapping speech"
      appears explicitly, not just implied by listing lines in order.
- [ ] Camera and action beats are similarly broken into a short timed
      sequence (as already practiced in `example-film-script.md`) rather than
      one paragraph of simultaneous description — this is what a MiniMax H3
      prompt guide (community-sourced) recommends: direct speakers, actions,
      a readable prop, camera movement, and a timed reaction shot explicitly,
      rather than relying on one well-written but ambiguous scene description.

## Dialogue pacing — close-ups drag more than you'd expect

Close, single-character "decision beat" shots (a character speaking a rule or
instruction slowly and clearly to camera) are the shots most likely to feel
slow even when the pacing block above is present — because "slowly and clearly
for a young child to follow" as a delivery note pulls against "lively and
energetic" as a general pacing note, and models tend to resolve that conflict
by slowing everything down, not just the line reading.

**Fix:** don't ask for slow, careful delivery. Ask for a **brisk, warm, and
concise** line instead — clear diction achieves readability for a young
viewer without needing the pace itself to drag. State the shot length matters
and should feel tight: "deliver the line at a natural brisk pace, not
drawn-out; the shot should feel short and energetic even though it's an
instructional moment." If a script line reads as more than about 2 words per
second of shot length, either shorten the line or lengthen the shot — a long
line crammed into a short shot forces slow delivery to fit.

## Worked example — weak vs strong

**Weak (will come back static):**
```
Bubi the purple baby dragon in a meadow with bubbles, cute cartoon style
```
No verb, no camera, no secondary motion. Expect a still with a slow zoom.

**Strong:**
```
[style block]
[character block]

Action: Bubi bounces on his back legs and swats at a floating bubble with
his front paw, ears bouncing with each hop.
Secondary motion: bubbles drift upward and wobble, wings flutter continuously,
sparkles trail from each popped bubble.
Environment: soft meadow grass sways in a light breeze, pastel clouds drift
slowly behind.
Camera: slow push in from a wide shot to a medium shot.
Lighting: warm afternoon sunlight, soft shadows.
Duration: 8s
```

## Chaining clips for smooth transitions

This is the mechanism that makes a sequence of separate clips look like one
continuous film. Do not rely on transitions at assembly to hide discontinuity —
fix it at generation.

For each clip after the first:

1. Take the previous clip's final frame with `vidiq_edit_media`
   (`op: "extract_thumbnail"`, `atSeconds` = the clip's duration minus 0.1).
2. Pass it as `startFrameB64` to `vidiq_generate_video` for the next clip.
3. Write the next prompt as a *continuation* of the pose in that frame — begin
   the action from where the character already is, not from a neutral stance.

The result is that clip N+1 opens on exactly the pixels clip N closed on, so a
straight cut at assembly is invisible. Where chaining isn't possible (Path A,
manual Hailuo), write the prompts so consecutive clips share the same camera
distance and character position, and use a short fade at assembly instead.

Note: on `minimax-h3`, `startFrameB64`/`endFrameB64` and `ingredients` are
mutually exclusive — use one or the other, never both.

## Style and character blocks

These are the continuity mechanism and are defined in
`references/continuity-bible.md`. Paste them **verbatim** into every prompt.
Rewording them between clips — even slightly, even to improve them — is the
main cause of a character that drifts across a film. If a block needs
improving, change it once and regenerate the whole sequence.

## Model selection

- `minimax-h3` — default. 4–15s, 768p or 2k. Same family as Hailuo H3.
- `veo-3.1` — 4/6/8s only, 720p/1080p. Reach for it when a specific shot needs
  higher fidelity; note the duration constraint before planning the beat.
- `seedance-2` — 1–15s, 720p/1080p. Useful alternative if h3 keeps producing
  a static result for a particular shot.

Costs scale with duration. Quote the cost before generating a long sequence.
