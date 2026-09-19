# Continuity bible — BubiPop Kids

The purpose of this file is that Bubi looks like the same dragon in clip 9 as in
clip 1. AI video models re-interpret a character from scratch on every
generation, so the only thing holding a character together across a film is
identical wording. Treat these blocks as fixed strings, not as prose to improve.

Paste them **verbatim** into every prompt. If a block genuinely needs changing,
change it once and regenerate the entire sequence — a film with two versions of
Bubi is worse than a film with an imperfect but consistent Bubi.

## Text blocks are not enough — the character sheet is mandatory

Text alone reduces drift; it does not prevent it. The model rebuilds the
character from words on every generation, and "lavender baby dragon with green
horns" describes hundreds of different dragons. Across 16–20 clips, drift is
the default outcome, not a risk.

**The fix is an image reference on every single generation.**

1. **Build one character sheet per character.** A single image showing the
   character from front, profile, three-quarter and back, plus two or three
   expressions, on a plain white background.
2. **Pass that exact file to every clip** — Omni Reference in Hailuo, or
   `ingredients` in `vidiq_generate_video` (up to 9 reference images on
   minimax-h3). Not an improved version at clip 12. The same file.
3. **Build an environment sheet too.** Otherwise the slide changes colour
   between scene 1 and scene 3.
4. **Layer frame chaining on top.** The sheet holds identity; chaining holds
   motion. They solve different problems and you need both.

Anchor the sheet on a frame from an existing published video rather than
generating a fresh character. That keeps the new work looking like a
continuation of the channel instead of a reboot.

**Verification is not optional.** Compare every returned clip against the
sheet — colour, proportions, eyes, horns — and report drift to Ilia even when
he hasn't asked. A drifted clip gets regenerated, never kept as close enough.
Budget roughly 40% of generation credits for retries; that is a planned line
item, not waste.

Even with a sheet, some clips will drift slightly. Nobody gets 20 out of 20.
What the method buys is small correctable drift instead of a different dragon
by minute three.

## STYLE BLOCK

```
3D animated children's cartoon, soft rounded shapes, pastel colour palette,
gentle rim lighting, shallow depth of field, glossy toy-like surfaces,
Pixar-adjacent lighting, bright and cheerful, no text, no logos,
crisp focus throughout.
```

## CHARACTER BLOCK — Bubi

Read directly from Ilia's own character sheets (`555.jpg`), not inferred. Use
verbatim.

```
Bubi is a small lavender-purple baby dragon with darker purple speckles on his
cheeks and body. Two pale sage-green horns curve back from his head. A row of
darker purple spikes runs from his forehead down the back of his head; green
spikes continue along his back and tail. His belly and chest are pale sage
green and segmented into horizontal plates. Large blue eyes with black pupils
and bright white highlights, pink blushed cheeks, a small upturned pinkish
snout, and small pointed ears with pale pink insides. Small wings with sage
green membranes and purple arms. Purple tail ending in a green spade tip. Pale
green-cream paw pads. Two small fangs and a pink tongue when his mouth is open.
Glossy 3D toy-like finish. Roughly the size of a house cat.
```

**Costume note:** Bubi appears both with and without a red backpack (scrolls,
tool pockets, small potion bottle) across the sheets. Pick one per film and
hold it. Mixing the two sheets as reference makes the backpack appear and
disappear between shots.

## Reference images — what goes in, what stays out

**Use `character-sheets/bubi.jpg` as the primary Bubi anchor.** The official
multi-angle sheet — front, side, back, expressions, palette. It is a stronger
identity anchor than any single frame.

**Never include in a Bubi reference bundle:**
- The **adult purple dragon** (larger, mature proportions, big wings, tan
  belly). It is not Bubi. Including it makes Bubi age mid-film.
- The **colour variation dragons** (green, yellow, red, blue). Useful for
  design, but as reference they invite the model to recolour Bubi.

## Cast — unresolved conflict, settle before generating

The character sheets and the existing scripts describe different casts:

| Scripts say | Sheets show |
|---|---|
| Pip — a small hedgehog | a turtle child in a yellow raincoat; no hedgehog |
| Nia — orange fox child in teal overalls | an adult fox in a mustard jacket and denim overalls on a hoverboard |
| (not in any script) | an owl wizard in a purple robe with brass goggles |

Confirmed matches: **Mia** — brown skin, dark curly hair in two puff buns with
beaded ties, coral hoodie, purple leggings, mint sneakers. **Leo** — brown
skin, dark curly hair, teal hoodie, orange shorts, blue sneakers.

Resolve who is actually in a film before writing its script. A character named
in dialogue but absent from the sheets has no reliable visual reference.

## SUPPORTING CHARACTERS

Fill these in as episodes establish them, then freeze the wording. An
inconsistent supporting cast is less damaging than an inconsistent Bubi, but it
still reads as sloppy to a returning viewer.

```
Puffy: a small white fluffy cloud creature with two dot eyes and a soft smile,
drifting slightly above the ground, trailing tiny wisps.
```

```
Mia: [define on first appearance, then freeze]
Leo: [define on first appearance, then freeze]
Pip: [define on first appearance, then freeze]
```

## Official character sheets — the locked cast

Ilia's professional multi-angle character sheets are saved in
`references/character-sheets/` (bubi, leo, maya, mom, dad). Each has front,
side, back, expressions and a colour palette. These are the visual source of
truth — they override any earlier text description, and any earlier conflicting
name. Attach the relevant sheet as the reference image for every shot a
character appears in.

**Two corrections the sheets settle:**
- The girl's name is **Maya**, not Mia. Use Maya everywhere.
- Mom has **no hat** — an earlier description gave her a blue cap; the sheet
  does not. The sheet wins.

### BUBI (`character-sheets/bubi.jpg`)
```
Bubi is a small lavender-purple baby dragon with darker purple flower-shaped
speckles, pale sage-green horns, purple spikes along his head and back, purple
ears with pink insides, large blue-teal eyes, pink blushed cheeks, a small
upturned snout, a pale sage-green segmented belly and chest, small wings with
pinkish membranes, and a purple tail with green spikes and a green tip. Glossy
toy-like finish. Roughly the size of a house cat.
```

### MAYA (`character-sheets/maya.jpg`)
```
Maya is a young girl with brown skin and dark curly hair in two puff buns tied
with purple bands. She wears a yellow t-shirt under purple dungaree shorts with
a heart pocket, and purple and white sneakers.
```

### LEO (`character-sheets/leo.jpg`)
```
Leo is a young boy with brown skin and short dark curly hair. He wears a teal
t-shirt, khaki beige shorts, and teal and white sneakers.
```

### MOM (`character-sheets/mom.jpg`)
```
Mom is a young woman with brown skin and dark curly hair in an updo, a
lavender-purple long-sleeve top, mint green rolled jeans, and lavender sneakers.
A small gold pendant necklace. No hat. Calm, warm expression.
```

### DAD (`character-sheets/dad.jpg`)
```
Dad is a young man with brown skin and short dark curly hair, a teal polo shirt,
khaki trousers, and teal and white sneakers. Warm, friendly.
```

## Consistency rules

**Lighting stays fixed across a film.** Pick one — warm afternoon, soft
morning, golden hour — and repeat that exact phrase in every clip. Lighting
shifts between clips read as continuity errors even when the character is
perfect.

**Camera distance follows the beat, not variety.** Wide for establishing,
medium for action, close for the emotional or instructional moment. Don't vary
distance for its own sake; each change should carry meaning.

**Colour discipline.** Bubi is lavender. Not purple, not violet, not mauve.
Word drift produces colour drift.

**One environment per episode where possible.** Every new environment is a new
chance for the model to reinterpret the character. Fewer locations means
stronger continuity and a faster shoot.

## When Bubi drifts anyway

If a clip returns a Bubi that doesn't match:

1. Regenerate with the same prompt — variance alone often fixes it.
2. If it drifts again, pass a good frame from an earlier clip as
   `startFrameB64` so the model anchors on the established design.
3. If it still drifts, the environment or action is pulling the model toward a
   different interpretation — simplify the action and try once more.
4. Do not keep a drifted clip because it's "close enough." Children notice
   character inconsistency immediately, and it's the difference between a
   channel that looks made and one that looks generated.
