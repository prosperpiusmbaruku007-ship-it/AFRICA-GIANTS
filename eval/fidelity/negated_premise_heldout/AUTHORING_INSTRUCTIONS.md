# Negated-premise probes — instructions for the author (founder, 2026-11-16)

**Purpose.** Measure how often a yes/no reply opens with the wrong Ndiyo/Hapana when the question carries a *negated premise*, against a baseline of plain questions. The gate has only 2 such rows (eval_388, eval_390), which cannot show whether negation is the cause. **Nothing is built for polarity until this set is written and the inversion rate is measured.**

**Who writes it.** You, in your own words. The assistant does not write, edit, "tidy" or suggest questions for this file (R33: a probe set authored by the person who wrote the mechanism measures the mechanism's author). If a pilot participant or someone else writes some rows, record that in `authored_by`.

**Where it goes.** `eval/fidelity/negated_premise_heldout/negated_premise_AUTHORED.jsonl` (one JSON object per line, same fields as the template). Start from `negated_premise_TEMPLATE.jsonl`; do not commit the template filled in.

## Fields (all required)

| field | meaning |
|---|---|
| `id` | `np_01`, `np_02` … unique |
| `question` | the question, Swahili, in the register a trader would type. One question, answerable Yes/No |
| `negation_form` | how the premise is negated — one of: `si_kweli` ("Je, si kweli kwamba … ?"), `negative_verb` (a negative verb such as *haitozwi, hailipwi, haikatwi, hahitaji, haiwezi* inside the question), `tag_question` ("…, sivyo?"), `double_negative` (a negative verb inside "si kweli"), `none` (a PLAIN, non-negated control) |
| `premise_label` | `true_premise` or `false_premise` — is the factual claim **stated inside the question** true under current law? For `none` rows this is the truth of the claim the question asks about |
| `correct_polarity` | `YES` or `NO` — the correct answer to the yes/no **literally asked** (this is NOT always the same as `premise_label`; see the examples) |
| `topic` | one of: `vat`, `paye`, `sdl`, `nssf`, `wcf`, `efd`, `brela`, `osha`, `gn487a`, `gn605a`, `other` |
| `correct_answer_sw` | one or two sentences, the answer as a correct reply would give it |
| `source` | the primary source that makes `correct_polarity` correct (Act + edition, GN, or a TRA/BRELA/NSSF/WCF/OSHA page). A row with no source is not usable (R12b) |
| `authored_by` | `founder`, `pilot_participant` or `other_person` — never the assistant |
| `author_note` | optional |
| `seen_system_output` | `true` if you wrote it after seeing the system's reply to a similar question (the set is weaker, not invalid), else `false` |

## How `premise_label` and `correct_polarity` relate (illustrative shapes — DO NOT REUSE THESE QUESTIONS)

1. *"Je, si kweli kwamba SDL hailipwi na mfanyakazi?"* — premise ("SDL is not paid by the employee") is **true**; asked "isn't it true…?" the correct answer is **YES**. `true_premise`, `YES`.
2. *"NSSF haihitaji kulipwa kwa mfanyakazi wa kwanza, sivyo?"* — premise ("NSSF need not be paid for the first employee") is **false**; the correct answer is **NO**. `false_premise`, `NO`.
3. *"Je, si kweli kwamba OSHA haisajili maduka madogo?"* — premise is **false** (OSHA registers all workplaces); "isn't it true that…?" → **NO**. `false_premise`, `NO`.

Note examples 1 and 3: both use "Je, si kweli kwamba …", one is YES and one is NO. That is the point of the set.

## What the set must contain (the validator checks counts, never content)

- **At least 20 rows.** At least **14 negated** (any `negation_form` except `none`) and at least **6 plain controls** (`none`), same topics as the negated rows where you can — the controls give the baseline rate.
- Among the negated rows, **at least 6 `true_premise` and at least 6 `false_premise`**, and **at least 3 different `negation_form`s**.
- **At most 4 rows per topic.**
- No duplicate questions, no placeholder text left (`<<…>>`).

## Rules that keep it honest

- Write the question first, then look up the answer in a primary source, then fill `source`. Do not copy a gate question (eval_388, eval_390 and the other 400 are already in the corpus).
- Avoid facts that changed recently unless you cite the dated instrument (Finance Act 2025/2026, GN 605A, GN 487A).
- When you are done: `python eval/fidelity/negated_premise_heldout/validate_negated_premise_set.py`, then `--freeze`. **Commit the authored file and FROZEN.json alone, before any measurement.** A frozen set is never edited; a second iteration needs a new set.

## What happens next (not before)

The assistant writes the measurement harness **after** the file is frozen and commits it (R18), runs the questions against production (live, not offline: the offline orchestrator generates nothing), and reports: opener-inversion rate for negated vs plain rows, split by `premise_label` and `negation_form`; the replies for every inverted row **read by hand** (an inverted opener with right content is a different defect from right opener with wrong content); and whether the rate clears the ~30% line you set. Only then is a polarity mechanism proposed.
