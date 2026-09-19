# The BubiPop Kids theme — original intro, every episode

Read this whenever building or referencing the show's opening. This intro is
**mandatory and identical** on every episode — that repetition is the entire
point. A theme song only works if a child can hum it after the second viewing,
and that only happens through exact, unwavering repetition.

## What makes a kids' theme song actually stick — the research

Looked at what holds up across generations of successful kids' intros (Arthur,
SpongeBob SquarePants, Bluey, Phineas and Ferb) rather than copying any one of
them. The pattern that repeats across all of them:

- **Short.** 20–45 seconds. Long enough to feel like an event, short enough
  that a toddler's attention survives it.
- **The protagonist's name lands early and often.** A child should know whose
  show this is within the first five seconds.
- **One hook line carries the whole song.** Everything else is scaffolding
  around a single repeated phrase simple enough to shout back.
- **Call-and-response or a direct question works better than narration.**
  "Are you ready, kids?" out-performs a scene-setting verse — it makes the
  child a participant, not a spectator.
- **Vocal range stays inside what a 4-year-old can actually sing** — no big
  jumps, mostly stepwise motion, a narrow comfortable range.
- **Visuals move in lockstep with the beat.** The animation isn't just playing
  under the song, it's choreographed to hit accents on the beat.
- **Exact repetition across episodes is what builds recognition** — a new
  arrangement each time defeats the purpose. The tune is the brand.

None of this is copied from any existing show — those are structural
observations, and everything below is written fresh for Bubi.

## The hook line

```
Bubi, Bubi, come and play —
Adventure's waiting, every day!
```

That's the line a kid should be able to shout back after two episodes. Short,
rhymes, states the character's name twice up front, and promises something
concrete (adventure, every day — implying a reason to come back).

## Full lyric — ~25 seconds

```
[Verse — playful, rising energy]
Who's got horns and a great big smile?
Who can make a bad day worthwhile?

[Hook — the line that repeats]
Bubi, Bubi, come and play —
Adventure's waiting, every day!

[Tag — friend group + call to action]
With Maya and Leo by his side,
Come along for the BubiPop ride!
```

Total: 4 short lines + repeated hook + 2-line tag. Simple AABB rhyme scheme
throughout, no line longer than 8 syllables — deliberately within a young
child's singable range.

## Musical direction

- **Tempo:** upbeat, ~120–130 BPM — energetic but not frantic.
- **Instrumentation:** ukulele and marimba as the bed (matches the score
  already used across the film), plus a light hand-percussion pulse and a
  bright synth or glockenspiel accent on the hook line.
- **Vocal:** a warm, bright children's-choir-style vocal (or a single clear
  child-adjacent voice) — never adult-sounding or slick. Should sound
  achievable, not polished — that's part of what invites a child to sing along.
- **Key:** major key throughout, no minor inflections — unambiguous
  cheerfulness.
- **Dynamics:** the hook line ("Bubi, Bubi, come and play") gets the fullest
  instrumentation and clearest vocal — it's the line that must be memorable
  above all others.

Generate with `vidiq_generate_music`, describing tempo, instrumentation and
mood from this section — the tool writes original instrumental/vocal music
from a text prompt, so feed it this direction rather than the lyric sheet
verbatim, and iterate on the render rather than expecting one-shot perfection.

## The signature move — why this sequence is designed to be sticky

What makes a kids' intro genuinely addictive isn't the melody alone — it's a
**single simple body movement a child can copy along with.** A tune a child
recognizes only by ear is forgettable; a tune paired with one signature gesture
becomes something the child's *body* remembers, and that's what pulls them
back to press play again.

**Bubi's signature move:** on every chorus hit ("Bubi, Bubi, come and play"),
Bubi raises the same open-palm gesture already established inside the show
itself (the "stop and think" gesture from the safety-rule episodes) — but here
it becomes a **dance beat**: palm up, a quick spin, then point forward on
"play!" Reusing the in-show gesture as the intro's dance move is deliberate —
a child who knows the intro recognizes Bubi's hand the moment it appears
inside an episode, and vice versa. That's the through-line that makes the
brand sticky across formats, not just within one song.

**Maya and Leo get their own small copyable moves** on the same beat: Maya
does one quick spin with her puff-bun ties flying out; Leo jumps with both
arms thrown straight up. Three simple, different, easily-imitated gestures —
not one complicated group choreography.

## Visual sequence — the 38-second sung adventure

The trio **sings the lyric live**, on-camera, lip-synced, throughout — this
is a sung sequence, not a montage under the track. Same three-location
adventure as before, now built around the vocal performance and the signature
gestures.

```
0:00–0:09  PLAYGROUND (established location, existing character sheets)
           Bubi bursts in at a run on the downbeat, singing the opening verse
           lines directly to camera with clear lip sync; Maya and Leo run in
           to flank him mid-stride, joining the vocal on the last word of the
           verse. Slide and swings visible, matching the established world.

0:09–0:19  CHORUS 1 — SCHOOL YARD
           As the chorus hits, all three perform the signature gesture in
           sync: Bubi's palm-up spin-and-point, Maya's spin, Leo's double-arm
           jump — while dashing past a cheerful, colourful school building
           (bright primary-toned brick, arched entrance, school bell,
           flowering bushes) and leaping a low hedge together on the beat
           accent. Full vocal, big smiles, direct address to camera on the
           hook line.

0:19–0:28  VERSE 2 — FOUNTAIN PLAZA
           They arrive at a small park with a playful splash fountain (low
           jets, bright and safe), pastel paving, colourful flags overhead.
           Bubi sings the second verse while hopping through a low arc of
           water on the beat; Maya and Leo sing along, laughing and dodging
           the spray.

0:28–0:38  CHORUS 2 + REUNION + LOGO
           Running into an open grassy clearing, all three repeat the
           signature gesture together in perfect sync on the final chorus,
           then strike a joyful freeze-frame pose as the last line resolves.
           Title treatment ("BUBIPOP KIDS") settles into frame over them on
           the final beat.
```

Every location transition happens on a strong beat (a chorus hit or drum
accent) — hard cuts on the beat, not crossfades, keep the energy up and match
the vocal phrasing.

## Production notes for this cut

- Four generated clips, ~9–10s each, matching the four beats above.
- **Playground clip** reuses the established character sheets and locked
  world exactly as the rest of the film — same slide, same swings, consistent
  with every other playground shot in the catalogue.
- **School and fountain clips** are new locations with no existing reference
  sheet. Describe them richly and consistently within this sequence (same
  wording reused if any clip needs a retry), but they don't need a permanent
  asset the way the playground does unless a future episode is set there.
- Assemble with the trimmed 38-second track as the audio bed via
  `vidiq_compose`; do not regenerate the music per shot.
- Captions/lyrics, if used over this sequence, are added at assembly as
  rounded, colourful text overlays timed to the lyric line — never as
  generated on-screen text in the clips themselves (see the standing rule in
  `assembly-and-shorts.md`).

## Where this fits in the pipeline

This replaces the plain "Title Card — motion graphic" step in
`script-template.md`'s Structure A for any episode where the full theme is
used. For episodes on a tighter budget, a 6-second instrumental sting (see
the title card spec in `script-template.md`) remains an acceptable shorter
placeholder — but the full theme is the standard once produced, and should be
reused identically across the whole catalogue from that point on.

## Discipline going forward

Once this theme is produced and approved, **do not vary it.** No new
arrangement for a "special" episode, no alternate lyric for a themed film. The
entire value of a theme song is Pavlovian — a child hears the first three
notes and knows what's coming. Changing it resets that recognition to zero.

## Status

Produced. Full track: `BubiPop_Kids_Theme_Song.mp3`, 76 seconds, MiniMax
Music-3.0. Approved by Ilia. **Official intro cut: `bubipop_intro_35s_fade.mp3`,
35 seconds**, trimmed from the full track with a 3-second fade-out starting at
0:32 — a clean professional trim, not a hard cut, chosen specifically because
an abrupt cutoff read as jarring. This 35-second file is the show's standing
open; reuse it unchanged across the whole catalogue rather than re-cutting or
regenerating it per episode.
