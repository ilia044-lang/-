---
name: kdp-factory
description: End-to-end publishing machine for Ilia's Amazon KDP books, workbooks, coloring books and activity books — niche research, unit economics, page-count and trim decisions, interior and cover production, KDP compliance QA, listing metadata, pricing and launch. Use this skill whenever Ilia mentions KDP, Amazon publishing, self-publishing, a book, workbook, coloring book, activity book, journal, planner, low-content book, trim size, bleed, margins, spine width, print cost, royalties, ISBN, book cover, book description, book keywords or categories, or asks things like "how much would this book earn", "how many pages should it be", "is this niche worth it", or "get this ready to upload" — even if he does not name KDP or this skill explicitly. Also use it whenever he ties a book idea to the BubiPop Kids channel or to a revenue target, so the idea gets checked against the real print-cost and sales math instead of accepted at face value.
---

# KDP Factory

Runs the whole pipeline from niche to upload-ready files. Ilia's money goal is real
and his stated weakness is chasing fast money — so this skill's first job is to kill
bad ideas cheaply with arithmetic, and only then to build.

Talk to Ilia in Hebrew. Produce book content in English (US market).

## Non-negotiables

1. **Never invent a market number.** BSR, review counts, competitor prices, search
   volume — either you searched for it, or you write `UNVERIFIED — assumption:` and
   state a confidence %. A fabricated BSR poisons the entire economic model.
2. **Show every money formula with the numbers substituted**, never just a result.
3. **Run the economics before writing a single page.** Use
   `scripts/kdp_calc.py`. If the realistic 12-month profit is below the value of
   the hours invested, say so in one blunt sentence and recommend killing it.
4. **Never advise under-declaring AI content** on the KDP form.
5. **No trademarked characters, brands, or lookalike covers.** Ever. That is an
   account-closure risk, not a style note.

## The decision rules that actually move money

Full verified tables: `references/kdp-specs.md`. The rules that decide a book:

- **Print cost is flat inside a tier.** B&W large trim (>6.12"W or >9"H) costs
  **$2.84 for 24–110 pages** — a 64-page book and a 110-page book cost the same to
  print. Always land on the **top of the flat tier** (110 pages B&W large trim,
  or 110 pages B&W regular trim at $2.30). Above it, cost goes per-page.
- **Never price a print book below $9.99.** Royalty drops 60% → 50% there.
- **Color destroys margin.** Premium color large trim is $0.08/page. A 300-page
  color book has a legal minimum list price of $41.67. Interiors go B&W; the
  cover is always full color at no extra cost.
- **Single-sided printing is a selling point, not waste** — "no bleed-through" is
  the #1 complaint in toddler coloring-book reviews. It also makes cut-out pages work.
- **eBook 70% band is $2.99–$12.99** (US, since 2026-07-07), and the eBook must be
  priced ≥20% below the print edition.
- **Low-content books** (blank/repetitive interiors): no free ISBN, no Expanded
  Distribution. Adding real content moves the book out of that bucket — do it.
- **Max 3 new titles per calendar day** (resets 00:00 PT).

## Pipeline

Work the roles in order. Do not ask permission between them; stop only at the gates.
The full standalone version, for pasting into any chat, is `references/master-prompt.md`.

1. **Researcher** — 12 candidate sub-niches, each a phrase a buyer would actually
   type. For the top ones pull competitor count, BSR of #1/#5/#10, price, page
   count, review count, publish date. Kill anything where the top 3 are trademarked
   properties or the top 10 are all pre-2022 with 500+ reviews.
   **GATE 1:** present top 3 + one recommendation.
2. **Economist** — full per-unit P&L at 3 configurations via `scripts/kdp_calc.py`.
   Pessimistic/realistic/optimistic units at months 1/3/6/12, anchored to the BSR
   data. Portfolio math to the revenue target. **GATE 2:** go or kill, bluntly.
3. **Architect** — read competitors' 1★ and 3★ reviews; those complaints are the
   spec. Fix trim, page count, ink, paper, bleed, margins, page-by-page map, and
   the one structural hook the top 10 lack. Design it as a 5-title series from day one.
4. **Creator** — produce 100% of the content. No "…and 47 more like this."
   Build the interior with `scripts/build_interior.py` (parameterized so titles 2–5
   reuse it) and assert the final page count.
5. **Cover designer** — spine = pages × 0.002252 (white paper); spine text only
   above 79 pages. Full wrap = (2 × trim W) + spine + 0.25" bleed, height + 0.25".
   Test the title's readability at 200px against 3 competitor thumbnails.
6. **Editor/QA** — run `references/qa-checklist.md`. Fix every FAIL yourself and
   re-run. Never hand Ilia a FAIL.
7. **Publisher** — title/subtitle, 7 keyword fields (exactly ≤50 chars each, show
   counts, no words already in the title), 3 categories per format with the current
   #1's BSR, ~1,800-char description, pricing per marketplace, honest AI disclosure,
   ISBN and Expanded Distribution decisions.
8. **Growth** — 30-day launch plan, TOS-compliant review acquisition (no
   incentivized or swapped reviews), Amazon Ads with an ACOS ceiling derived from
   the actual per-unit royalty, and 5 weekly KPIs each tied to a decision.
   **GATE 3:** go/no-go with a confidence %.

## Branding rule for Bubi books

The BubiPop Kids channel had **3 subscribers / 268 views** as of 2026-09. Re-check it
with vidIQ before assuming otherwise. Until it is meaningfully larger:

- **Bubi never leads the title or the front cover.** Nobody searches "Bubi".
  Titles lead with what parents type: "scissor skills", "cut and paste",
  "animal habitats", "ages 3-6".
- Bubi is the guide character *inside* — that builds recall for the next book.
- A QR code pointing at a 3-subscriber channel hurts trust. Point it at a landing
  page Ilia controls, so the destination can change without reprinting.
- The book drives traffic to the channel, not the reverse.

## Scripts

```bash
python3 scripts/kdp_calc.py --pages 110 --ink bw --trim large --price 9.99 --target 500
python3 scripts/kdp_calc.py --pages 60 --ink premium_color --trim large   # min legal price
python3 scripts/kdp_calc.py --ebook --price 9.99 --mb 2
python3 scripts/build_interior.py --art ./art --out interior.pdf           # needs reportlab
```

## References

- `references/kdp-specs.md` — verified trim/bleed/margin tables, print-cost tables,
  royalty bands, content and AI rules, low-content limits, sources.
- `references/master-prompt.md` — the 8-role prompt as a standalone paste-in block.
- `references/qa-checklist.md` — the pre-upload PASS/FAIL gate.
