# PROPOSAL (not built) — route recall R1 and R2: two no-figure "kiasi gani" questions that should reach a statement and don't
2026-11-26. Definitions are the founder's (clarified 2026-11-26 after the crash). **Propose only; nothing in `chike/` is changed.** Harness: `eval/routing/sweep_R1_R2_kiasi_gani_2026_11_26.py` → `eval/results/sweep_R1_R2_kiasi_gani_2026_11_26.json` (committed with this note, R18).

## The two live rows (2026-11-25 answer-path check, `eval/results/answer_path_live_table_2026_11_26.md`)
| | question | live | should be |
|---|---|---|---|
| **R1** (row 17) | "Mfanyakazi mgeni analipa PAYE kiasi gani?" | logged `clarification`, 0 model calls: a generic reply asking for the salary | the `paye_residency` statement (residency, not being a foreigner, decides the regime) |
| **R2** (row 18) | "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?" | `fact_model`, 1 call: *"Kiwango cha kodi ya zuio kwa ada ya mkurugenzi ni asilimia 15. Thibiti…"* — the rate without the resident/non-resident credit split | the `director_fees_wht` statement |

## Cause (read from `chike/routing.py`, not inferred)
Both topics already exist (`paye_residency`, `director_fees_wht`) with an own-ask gate. **Each lists `kiasi\s+gani` in its VETO pattern as a "calculation / amount ask"** (written when the topics were built 2026-11-25), so the very phrasing a user types for "what is the rate" is vetoed. R31's pattern again: the statement exists, the route's veto rejects its natural ask. Before: `detect_intent` = `none` for both.

## The proposal
Remove the `kiasi\s+gani|` alternative from the veto of those two topics **only**. The figure vetoes stay (`[0-9]{4,}`, `tzs`, `milioni`, `elfu`, `kokotoa`, `hesabu`, …), so **a question with an amount is unchanged** by construction:
- R1 with an amount ("…analipwa TZS 2,000,000, PAYE kiasi gani?") → still `paye` engine, resident bands + residency note (measured: `paye_residency_unclear` False, so no clarification).
- R2 with an amount ("Ada ya mkurugenzi ni TZS 5,000,000, …") → still none → model path, as you asked ("for now").

## Measured (sweep, candidate applied in memory)
- **Population (R22 named):** 6,287 unique questions from every `eval/**/*.jsonl` and `datasets/**/*.jsonl` (139 files). This is the population the change can touch: only a question that names PAYE+foreign or a director fee, with a withholding/rate ask, no figure.
- **Diversions in the corpora: 0.** Zero both ways: the change moves **no existing row**, so there is nothing to read in the corpora, **and the route is untestable on them (R21)**: the evidence is the authored probes, which I wrote (R33). Treat 0 as "no corpus row has this shape", not "safe".
- **Probes, both directions — all asserted ones pass:** R1/R1b/R2/"Ada ya wakurugenzi hukatwa kodi kiasi gani?" → their statements (`none → topic`); amount in digits / in words, Kenya, no PAYE word, PAYE+SDL, "nilipwe kiasi gani" with no tax word → **unchanged (`none → none`)**.
- **End to end:** `detect_intent` = `fixed_statement` for R1 and R2 (was `none`); the amount-bearing R1 stays `paye`, R2 stays `none`.
- **Recorded reach limit:** "Mkurugenzi akilipwa ada, kodi ya zuio inakatwa kiasi gani?" stays `none` — the director cue needs the noun phrase "ada ya mkurugenzi". Not part of this proposal; a candidate for a later cue.

## ⚠️ One decision for you: first-person, no figure
"Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?" **would divert to the residency statement** (`none → paye_residency`). The person is asking for *their own amount* without giving a salary; today they get the generic "give me your salary" clarification, which arguably answers them better than a regime statement. Options: (1) accept; (2) **add a first-person keep-veto** (`mimi|yangu|wangu|nikatwe|ninakatwa|nakatwa|nilipe`) to the residency topic so those keep the clarification — my recommendation, since R1 is about a third person ("mfanyakazi mgeni"). It costs one alternative in the veto and one more probe. Say which and I will carry it into the build.

## If approved, the build is
One veto edit per topic (plus the first-person limb if chosen), the sweep re-run as a test (planted: put `kiasi gani` back and R1/R2 must fail; clean limbs for the amount-bearing rows), R12c's enumerated blast radius with unchanged-route prompt-identity controls (R24b), and a `chike-inference` window (R16) with a live check of R1, R2 and one amount-bearing negative each. Nothing here touches `chike-whatsapp`.
