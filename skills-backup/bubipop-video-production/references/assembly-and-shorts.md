# Assembly and Shorts

## Assembling the film

Use `vidiq_compose`. It takes ordered scenes, a voiceover, music, and overlays,
and renders one MP4.

Key parameters and why they matter here:

- **`format`** — `landscape` for the main film, `vertical` for Shorts. Set this
  correctly at generation time; it cannot be fixed later without damage.
- **`scenes[].source`** — the clip URLs, in order, each with its `duration`.
  Total across all scenes is the film length; audio longer than that gets cut
  off at the end, so size the scenes to fit the voiceover, not the reverse.
- **`keepNativeAudio`** — leave it off. Generated clips have no useful audio;
  sound comes from the voiceover and music tracks.
- **`transitionIn`** — with properly chained clips (see `prompt-craft.md`), use
  `cut`. Reach for a short `fade` (0.3–0.5s) only at junctions where chaining
  wasn't possible. Long fades between every clip read as a slideshow, which is
  the opposite of the goal.
- **`layout`** — `fill` scales and centre-crops; `fit` letterboxes with bars.
  For a film whose clips were generated at the output aspect, this never
  matters. It only matters when aspect ratios mismatch — and the answer to a
  mismatch is to regenerate, not to letterbox.

**Voiceover:** `vidiq_voiceover_generate`, after picking a voice from
`vidiq_voiceover_list_voices`. For kids content choose a warm, unhurried voice
and keep the script short — silence between lines is fine and lets the
animation breathe.

**Music:** `vidiq_generate_music` for an original royalty-free track. Set
`duckTo` around 0.25 with `fadeMs` about 400 so the music drops under the
narration and comes back up between lines. Music at full level under a
voiceover is the most common amateur audio mistake.

**Overlays:** text overlays are how any on-screen words get added — never
generate text inside a clip. Keep them to 3–4 words, high contrast, clear of
the bottom quarter of the frame.

Rendering is asynchronous: `vidiq_compose` returns an `mcpJobId`, then poll
`vidiq_job_poll` until it completes and read the signed `videoUrl`. Signed URLs
expire — use them promptly and don't try to reconstruct them later.

## Shorts — the framing rule

**Never crop a landscape film into a Short.** Cropping 16:9 to 9:16 throws away
about two thirds of the width, which is exactly what produces cut-off heads and
off-centre subjects. Letterboxing instead produces grey bars. Both look
amateurish, and both are avoidable.

Correct approaches, in order of quality:

**1. Generate the Short natively vertical (best).** Re-generate the chosen beat
with `aspectRatio: "9:16"` and the same style and character blocks. The
composition is built for the frame instead of salvaged from it. Costs an extra
generation; worth it every time.

**2. Plan vertical from the start.** When an episode is likely to yield Shorts,
generate the key beats twice — landscape for the film, vertical for the Short —
in the same session while continuity is locked. This is the efficient version
of option 1.

**3. `vidiq_generate_clips` (fast, lower quality).** It takes a YouTube URL and
produces vertical clips with burned-in captions automatically. It crops, so
expect framing compromises. Reasonable for volume; not for the video meant to
represent the channel.

## Shorts composition rules

- **Subject in the upper two thirds.** The bottom of a Short is covered by the
  title, channel name, and buttons. Anything important down there is hidden.
- **Safe margins.** Keep text and key action at least 10% in from every edge.
  Different devices crop differently, and text touching an edge gets clipped.
- **Hook in the first second.** Shorts viewers swipe faster than they decide.
  Open mid-action, never on an establishing shot.
- **Vertical-native motion.** Design the action to travel up and down rather
  than left and right — lateral motion runs out of frame immediately in 9:16.
- **Legible at thumb size.** If the subject isn't clear on a phone held at
  arm's length, it's too small.

## Deriving a Short from an existing film

1. Pick the single strongest beat — one complete idea with a visual payoff.
   A Short is not a trailer; it's one moment that works alone.
2. Re-generate that beat vertically (approach 1 above).
3. Assemble with `vidiq_compose`, `format: "vertical"`.
4. Add the spoken CTA over the final beat while motion continues.
5. Check against the framing rules before publishing.
