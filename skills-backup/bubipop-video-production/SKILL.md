---
name: bubipop-video-production
description: End-to-end production pipeline for Ilia's educational kids videos on the BubiPop Kids channel — writing the script, generating animation clips (Hailuo AI / MiniMax H3, max 15s per clip), chaining clips so motion stays continuous with no frozen or morphing frames, assembling them into one finished film, and deriving properly framed vertical Shorts from it. Use this skill whenever Ilia mentions making a video, a new episode, Bubi, a script, a scene, animation prompts, Hailuo, MiniMax, generating or stitching clips, transitions, voiceover, background music, a call to action, or turning a film into Shorts — and also whenever he asks for help improving a video that already exists. Proactively suggest concrete quality improvements every time; never just execute the request as given.
---

# BubiPop Kids — Video Production

This skill turns an educational idea into a finished film, and the film into
Shorts. It exists because the failure modes in AI animation are specific and
predictable: frozen frames, characters that morph between shots, hard cuts that
read as glitches, and Shorts that are cropped from landscape and come out with
heads cut off and grey bars.

Every rule below exists to prevent one of those.

Speak Hebrew to Ilia. Write all prompts and on-screen text in English.

## What the channel is making

Educational kids content that a **parent actively wants their child to watch**.
That framing decides everything: the parent is the buyer, the child is the
viewer. A video that entertains but teaches nothing loses the parent; a video
that teaches but bores loses the child. Every episode must do both.

Bubi is a lavender baby dragon. Recurring friends: Mia, Leo, Pip, Puffy (a
fluffy cloud). Existing episodes cover electrical safety, helping an injured
animal safely, and colour/rainbow adventures. The safety-lesson format is the
strongest — it gives parents an explicit reason to press play and it earns
higher ad rates than generic animation.

## Constraints that shape everything

- **Made for Kids.** No end screens, no cards, no comments, no notification
  bell. Any call to action must be *inside* the video — spoken and shown — or
  it does not exist. Never write "comment below" or "click the card."
- **15 seconds maximum per generated clip.** A film is a chain of clips, so
  continuity between them is the central engineering problem, not an afterthought.
- **Inauthentic content policy.** YouTube enforces hard against mass-produced
  AI output. A run of near-identical episodes is a demonetization risk that
  would end the channel. If the next episode is the fifth variation of the same
  template, say so and change something real — this outranks shipping speed.

## Two production paths

**Path A — Hailuo web tool** (`hailuoai.video`), driven by you through Claude in
Chrome. Verified working: navigating the site, reading the page and his
generation history, clicking controls, and typing into the prompt field. The
site is set to English and his session stays logged in.

Ilia has given standing permission to operate the site on his behalf, with one
absolute exception below. Use the English URLs (`/create/image-to-video`,
`/tools/...`) — the `/zh-Intl/` paths render in Chinese.

Practical notes from the first session:

- Credits are a small, finite, paid resource — he had 136 with a single 5s 2K
  generation priced at 60. **Read the balance before planning any sequence**
  and tell him what a run will cost before starting it. Not for permission —
  he's given that — but because a plan that silently exhausts his balance
  halfway through a film is a failed plan.
- **Check the aspect ratio control before generating.** It was left on 21:9,
  which letterboxes badly on YouTube. 16:9 for the film, 9:16 for Shorts.
- Screenshots on this site sometimes time out. `get_page_text`, `find`, and
  `read_page` work reliably — use those instead of retrying screenshots.
- His existing prompts are already strong (cast bibles, explicit character
  preservation, `@Image1` references, stated continuity between scenes).
  Build on them rather than replacing them; his constraint is credits, not
  technique.

**Path B — vidIQ, run directly by you.** `vidiq_generate_video` with
`model: "minimax-h3"` is the same MiniMax model family behind Hailuo, 4–15s,
768p or 2k. This path also unlocks `vidiq_compose` for assembly,
`vidiq_voiceover_generate`, `vidiq_generate_music`, and `vidiq_edit_media`.
It costs vidIQ credits — check `vidiq_balance` before committing to a long
sequence, and tell him the cost before spending it.

Default to Path B when he wants it done now, Path A when he wants control over
each clip. Ask which if it isn't obvious.

### Never buy anything

Do not purchase credits, tokens, top-ups, plans, or subscriptions on
`hailuoai.video`, on vidIQ, or anywhere else — not with a saved payment method,
not with a card, not "just this once" because a render stalled mid-sequence for
want of 40 credits. Ilia excluded purchasing explicitly when granting access,
and entering payment details is outside what you do on anyone's behalf
regardless.

When the balance runs short, stop and tell him the number. He tops up himself.
This is the one place where running out of credits mid-task is the correct
outcome rather than a problem to solve.

## The pipeline

Work in this order. Skipping ahead is what produces films that need re-doing.

1. **Lesson** — one concrete thing the child learns. Not a theme, a rule.
2. **Script** — beats, voiceover lines, and shot list. Write it to feature
   standard: character wants something, is blocked, chooses, and the ending
   follows from the choice. See `references/script-template.md` for structure
   and `references/cinematic-craft.md` for the storytelling, shot grammar, and
   voice-casting standard. Read the cinematic file before writing anything —
   it governs steps 2 through 6.

   **A film is not a long Short.** A film gets a cold open, a title card, acts,
   a payoff and an outro card — never the mid-action open of a Short. Shorts
   are *derived from* the finished film, not the shape the film is built in.
   `references/example-film-script.md` is a complete worked example of the
   film structure, background-population blocks, pacing blocks and locked
   character/voice blocks all in one place — read it before scripting a new
   episode and follow its shape.
3. **Continuity lock** — fix the character and style paragraphs before
   generating anything. See `references/continuity-bible.md`.
4. **Clip prompts** — one action per clip, motion in every layer.
   See `references/prompt-craft.md`. For any shot with more than one named
   character, dialogue, or an object changing hands, read
   `references/precision-prompting.md` first — it covers staging complexity
   in stages, exact timestamp formatting, and how to iterate on a near-miss
   without burning credits on unfocused retries.
5. **Chain** — each clip starts from the previous clip's last frame.
6. **Assemble** — voiceover, music, transitions, CTA.
   See `references/assembly-and-shorts.md`.
7. **Derive Shorts** — vertical-native, never cropped.
   Same reference file.
8. **Quality gate** — the checklist at the end of this file.

## The frozen-frame problem — read this before writing any prompt

The single most common failure is a clip where nothing really moves: the model
produces a near-still image with a slow zoom, or the character holds a pose
while only the background drifts. It reads as broken, and on a kids channel it
kills retention in the first two seconds.

It happens when the prompt describes a *scene* instead of an *action*. Fix it
structurally: every prompt specifies motion in four layers — the character's
body, a secondary element (wings, hair, cloth, bubbles, sparkles), the
environment, and the camera. If you can't name motion in all four, the prompt
isn't finished.

Full prompt structure, with worked examples: `references/prompt-craft.md`.

## Direction of motion — vertical beats

A viewer reads climbing or descending from the character's position **inside the
frame**, not from the body. If the character stays the same size at the same
height while the camera pushes in, the movement cancels out and the shot reads
as a child standing still holding a bar. Ilia caught this on S13/S14 of Episode
01 and it is the second most common failure after the frozen frame.

Any beat whose story point is "where is this going" — a ladder, a slide, a
swing, stairs — gets all six of these in the prompt:

1. **Travel inside the frame.** State it explicitly: starts LOW in frame near
   the bottom edge, ends HIGH in the upper third. Reverse for descending.
2. **A fixed reference that stays in shot.** The grass, the base of the
   structure, a platform edge. Without a ruler there is nothing to measure
   against.
3. **A locked camera.** No push in, no zoom, no pan during a vertical beat — a
   push in cancels exactly the size change that tells the eye what happened.
   Low angle looking slightly up for climbing, slightly down for descending.
4. **Feet, not hands.** "His foot leaves the lower rung and plants on the next
   rung ABOVE it, repeated twice." Hands on a bar are a still image.
5. **Eyeline in the direction of travel.** Climbing looks up at the next bar;
   descending looks down at the landing. This is the fastest cue a child reads.
6. **Weight.** "pulling his body upward with his arms, effort visible in his
   shoulders" versus "lowering himself slowly, arms extended above him".

### The insert shot — fix a sequence without regenerating it

When two clips are individually good but the beat between them doesn't read,
the cheap fix is a short **insert (cutaway)** between them, not a regeneration.
This was Ilia's call on Episode 01 and it should be the default.

It wins three ways: both existing clips are kept, the insert absorbs any framing
jump between a wide and a close shot, and — because an insert carries no
dialogue — it removes lip-sync and gibberish from the riskiest part of the
sequence. A 4–6s insert costs roughly 28–42 credits against 56 for a full
re-generation, and it adds information instead of replacing it.

Build it with: locked camera, one mechanical action, no speech, the six rules
above, and the same background cast as the shots on either side.

### Teach the rule where the rule is needed

A safety rule lands when the child sees the moment that calls for it, not only
the correct outcome. The working structure is: the action → the mistake → the
correction → the payoff. If an insert shows the behaviour already done
correctly, the character's instruction afterwards has nothing to attach to —
add the small lapse (one hand lifted to wave, a foot skipping a rung) before
the correction. Keep the lapse calm. Never show a near-fall, a scare, or an
injury: it frightens preschoolers and draws Made for Kids scrutiny.

## Keep a running lessons log

Every episode surfaces a failure mode that wasn't obvious before. Write it down
rather than re-learning it. When a clip disappoints, name the mechanism — not
"it looked odd" but "the push in cancelled the vertical travel" — and turn it
into a prompt rule for every later shot in that class.

Two habits carry this between sessions:

- **Add the rule to this skill** once it has held up on a real shot, so it
  applies before the mistake can repeat.
- **Save the fact to memory**, since a session ends and its scratch files do
  not survive. The prompts themselves live in Hailuo's history and can always
  be pulled back from there — that is the recovery path when a session's
  context is gone.

Known lessons so far, in the order they were learned:

| Failure | Mechanism | Rule now applied |
|---|---|---|
| Duplicated background girl | Vague background descriptions let the model reuse a main character | Every background figure is described as a distinct person |
| Slow, floaty movement | Scene described instead of action | Motion in four layers, plus explicit real-time pacing |
| Character drift across clips | Reworded character blocks between prompts | Blocks are fixed strings, pasted verbatim |
| Climb unreadable as up or down | Push in cancelled the travel; no fixed reference | The six vertical-motion rules above |
| Framing jump between wide and close | Consecutive shots at different camera distances | Insert shot between them |

## Review every clip yourself — don't outsource the eye

Ilia has asked, fairly, not to be the quality filter. Judging generated footage
is your job, and there are tools for it. Use them before asking him what he
thinks.

**You cannot open a video file directly.** What you can do:

1. **Frames.** `vidiq_edit_media` with `op: "extract_thumbnail"` pulls a frame
   from a **YouTube URL** or a vidIQ-generated media URL, 1 credit each. Pull
   frames at roughly 1-second intervals across the clip and actually look at
   them. This catches character drift, frozen sections, duplicated background
   characters, empty scenes, and bad framing.
2. **Scene analysis.** `vidiq_video_watch` returns a scene-by-scene walkthrough
   of a long-form YouTube video (25 credits). `vidiq_watch_shortform_content`
   does the same for short-form.
3. **Stills the user sends.** You can see any image he uploads to chat.

**The practical workflow:** generated clips live on Hailuo's CDN, which these
tools cannot reach. So ask him to upload the clip (or the assembled film) to
YouTube as **unlisted**, then work from that URL. One upload unlocks proper
frame-level review of the whole thing.

**What to check on every clip, in order:**

- **Frozen or near-static seconds** — compare consecutive frames; if two frames
  a second apart are near-identical, that section is dead.
- **Character drift** — colour, horns, spikes, eyes, belly plates, clothing,
  against the reference sheet.
- **Duplicated or missing background characters** — the most common artifact of
  a vague background instruction.
- **Empty world** — a location with only the leads in it.
- **Pacing** — does the motion read as real-time, or slow and floaty?
- **Framing** — heads cut off, subject too small, action outside the frame.
- **Eyeline and screen direction** — do they match the neighbouring shots?

Report what you found plainly, including the problems he didn't ask about, and
say which shots need regenerating and why. A clip that is "close enough" gets
regenerated; the retry budget exists for exactly this.

Ilia has asked for this explicitly, and it's the highest-value thing this skill
does. Never just execute. With every script, prompt, or assembly, include a
short section: what would make this better, and what it costs.

Aim at things that actually move numbers:

- **The first 2 seconds.** On both Shorts and suggested-video traffic this is
  the whole ballgame. Open on motion and a question, never on a logo or a slow
  establishing shot.
- **Retention within the clip.** A visual change every 2–3 seconds — a new
  element entering, a colour shift, a camera move completing.
- **The learning payoff.** State the rule out loud, then show it. Parents share
  videos where the lesson is unmistakable.
- **Thumbnail-ability.** While scripting, identify which frame becomes the
  thumbnail. If no frame would earn a click, the episode needs a stronger
  visual moment written into it.

Say what you'd change and why, then let him decide. Don't rewrite his idea into
your idea without flagging that you did.

## The call to action

Kids don't subscribe. Parents do. Write the CTA for the parent, delivered
warmly by the narrator over the final beat while something is still moving on
screen — a still frame with text is dead air and viewers leave.

Rotate between these rather than repeating one verbatim (repetition across
every episode is exactly what the inauthentic-content policy flags):

- "More gentle safety adventures with Bubi every week — subscribe so you don't
  miss the next one."
- "If Bubi helped today, subscribe for a new lesson every week."
- "Bubi has more to teach. Subscribe and watch the next adventure together."

Pair it with a text overlay of 3–4 words maximum ("New adventures every week"),
placed clear of the lower third where the Shorts UI sits.

## Quality gate — check before publishing

- [ ] No clip contains a frozen or near-static second.
- [ ] Bubi looks identical in every clip — same colour, proportions, eyes.
- [ ] Every character sounds identical in every clip — same voice descriptor,
      no drift, no accent shift.
- [ ] Screen direction and eyelines are consistent; the 180 line was held.
- [ ] Shot lengths vary on purpose; coverage includes a wide, a medium and a
      close rather than one repeated angle.
- [ ] The decision beat exists and is held long enough to land.
- [ ] No morphing at any junction; transitions read as intentional.
- [ ] The lesson is stated out loud at least twice.
- [ ] First 2 seconds contain motion and a hook.
- [ ] CTA is in-video, spoken and shown, over moving footage.
- [ ] Shorts are vertically native — no letterbox bars, no cropped heads,
      no text touching the frame edge.
- [ ] Audio is level; music ducks under the voiceover.
- [ ] This episode is meaningfully different from the last one.

Then hand off to `bubipop-channel-ops` for titles, thumbnails, and publishing.
