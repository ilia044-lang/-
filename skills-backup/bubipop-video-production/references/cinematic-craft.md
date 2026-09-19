# Cinematic craft — writing and directing to feature standard

The brief is explicit: these episodes should be written and shot like real
films, not like generated clips stitched together. This file is the standard.

The gap between "AI clips in a row" and "a film" is almost never resolution or
prompt length. It's craft decisions that were made before anything was
generated: what the character wants, why the camera moves, whether shot 4 is
looking the right direction. Those decisions cost nothing and can't be added
afterwards.

## Story — the part most AI content skips

**A character must want something and be prevented from getting it.** Bubi
wanting to touch the glowing bottle and being stopped by a rule is a story.
Bubi explaining a rule is a lecture. Children sit through stories; they leave
lectures — and so do parents.

**Give Bubi agency.** He should solve it, not have it solved for him. He can
ask an adult for help — that's the lesson — but *choosing* to ask is his
action. A protagonist things merely happen to is why a film feels flat even
when every frame is beautiful.

**Raise a real question in the first shot.** Not "what is this video about"
but "what is Bubi going to do?" Curiosity is the only thing holding a
four-year-old through the second act.

**Make the turn visible.** There is one moment where Bubi decides. Give it its
own shot, hold it a beat longer than feels comfortable, and let the music drop
out under it. That silence is the most cinematic tool available and it costs
nothing.

**Earn the ending.** The good outcome must follow from the choice. If Buddy is
fine regardless of what the children did, the lesson has no weight.

## Shot grammar

**Coverage, not one angle per beat.** Real scenes are built from a wide that
establishes geography, a medium where the action plays, and a close for the
emotional or instructional moment. A film made entirely of medium shots reads
as generated no matter how good each shot is.

**Every camera move needs a motivation.** Push in when a character realizes
something. Pull back to reveal consequence or scale. Track with movement. A
slow push on a static beat is the visual equivalent of a shrug — and it's the
default the model reaches for when the prompt doesn't say otherwise.

**Hold the 180-degree line.** Pick which side of the action the camera lives on
and stay there for the scene. If Bubi faces screen-right toward Nia in shot 2,
he still faces screen-right in shot 3. Crossing the line makes characters
appear to swap places and is the single most common reason a sequence feels
subtly wrong without a viewer being able to say why.

**Match eyelines.** If Bubi looks up at an adult, the reverse shot looks down
at Bubi. State the eyeline direction in every prompt where two characters
interact — the model will not infer it.

**Consistent screen direction.** A character walking left-to-right keeps
walking left-to-right across cuts, or the audience reads it as turning back.

**Vary shot length deliberately.** Rhythm is built from contrast: several
shorter shots into one longer held shot creates emphasis. Every shot the same
length produces a metronome, and a metronome puts children to sleep.

## Lighting and colour as storytelling

Pick a look per scene and name it identically in every prompt for that scene.
Then use change meaningfully: the cool blue of the hazard giving way to warm
light when the situation is resolved is doing narrative work. Random variation
between shots is just a continuity error wearing a costume.

## The voice bible — never change a character's voice

A character whose voice changes between shots stops being a character. This
matters more than visual continuity, because audio inconsistency is noticed
immediately even by viewers not paying attention.

**Fix each voice once, then never vary the wording.** Maintain the casting
table below and paste the descriptor verbatim into every prompt that character
speaks in.

```
Bubi:   warm, bright young voice, gentle and slightly breathy, unhurried,
        neutral English, curious tone
Nia:    lively young child voice, higher pitch than Bubi, quick and eager,
        neutral English
Mia:    calm young girl's voice, clear and steady, neutral English
Leo:    bright young boy's voice, slightly lower than Mia, neutral English
Pip:    small squeaky voice, quick and light, neutral English
Adult:  calm reassuring adult voice, warm and measured, neutral English
Narr.:  warm gentle storyteller, unhurried, neutral English
```

Fill in new characters on first appearance and freeze the wording immediately.

**Always specify "neutral English, accurate lip sync, no accent"** — it's
already in the existing prompts and it's the right call; keep it.

**Voices louder than music, never overlapping.** Also already in the existing
prompts. Keep it in every one.

**On Path B (vidIQ voiceover):** consistency is easier — reuse the same
`voiceId` from `vidiq_voiceover_list_voices` for a character across every
episode. Record the chosen voiceId in this file the first time it's picked, so
episode 12 sounds like episode 1.

## Continuity checklist before generating a sequence

- [ ] Same character descriptor block, word for word, in every prompt
- [ ] Same voice descriptor, word for word, in every prompt
- [ ] Same lighting phrase within a scene
- [ ] Screen direction consistent across shots
- [ ] Eyelines stated and matched
- [ ] Props persist — a bandage present in shot 5 is present in shot 9
- [ ] Camera side of the 180 line unchanged within a scene
- [ ] Shot lengths varied on purpose

## Directing the model toward "alive"

The note "make it more alive" almost always means one of these is missing:

- **Anticipation and follow-through.** Bodies wind up before they move and
  settle after. Say so: "he dips slightly before hopping, ears settling after
  he lands."
- **Micro-motion during dialogue.** A character talking with a still body looks
  animatronic. Specify blinks, weight shifts, tail movement, breathing.
- **Overlapping action.** Something in frame should already be moving when the
  shot begins — no shot starts from stillness.
- **Reaction shots.** Cutting to a listener's face is what makes a scene feel
  performed rather than narrated.
- **Environmental life.** Grass, dust motes, drifting clouds, flickering light.
  A world where only the protagonist moves reads as a diorama.
