# ADR — Replace correction-sync's borrowed detector with a superseded-value check

**Status: SCOPED, NOT BUILT.** Deliberately. The figure test has already demonstrated that a
value-level check over this corpus is context-blind, so the design question is settled before
the code exists, not after.

**Date:** 2026-10-06
**Supersedes nothing. Does not change any shipped behaviour.**

---

## The defect, measured

`scripts/check_correction_sync.py` exists for exactly one shape: a fact corrected in
`locked_facts.json` whose RAG-embedded text keeps serving the superseded value. It has missed
that shape **twice**, both times reporting `correction_sync=CLEAN` on every regen in between:

| fact | corrected | the index row kept serving | found |
|---|---|---|---|
| `nssf_payment_deadline` | 2026-09-02 (s.14(1), "within one month after the end of the month") | row 63: `NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata` | 2026-10-05, by accident, while placing a different fix |
| `efd_threshold_tzs_11m` | 2026-08-29 (TAA Cap.438 s.44 sets no turnover threshold) | row 57: `Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 ... kwa mwaka` | 2026-10-06, by a sweep looking for something else |

Diagnosis: `eval/controls/diagnose_correction_sync_miss_row63.py` →
`eval/results/correction_sync_miss_row63.json`. Three hypotheses were tested by reconstructing
all four inputs at one SHA and running the real gate. **(a) wrong key: REFUTED** — the pin
resolved straight to row 63. **(c) soft gate, flag read past: REFUTED** — never flagged; a
blocking posture would have passed it identically. **(b) the patterns never named the served
value: SUPPORTED.**

## Why it is a different check, not a tuning problem

The gate's strong signal asks *does the fact's own `wrong_patterns` match its index row?*

`wrong_patterns` are authored to catch a wrong claim **in generated text** — a model reply, a
training pair. The gate's own docstring says so. It reuses them against **index text**. Two
populations, written by different hands for different purposes, and **nothing requires the
wordings to overlap.** Both misses are that gap, not a near-miss of it:

- row 63's patterns require the literal `au` plus `mwishoni/mwisho wa mwezi` — the *ambiguous*
  "10th OR end of month" conflation someone expected a model to emit. The row asserted a bare
  10th.
- row 57's pattern requires `kizingiti cha efd` adjacent within 30 characters. The row has 25
  characters of ordinary Swahili — `kuanza kutumia mashine ya` — between the two words.

Widening the windows would have caught *these two*. It would not change the fact that the
detector's reach depends on **the correction's author having anticipated the phrasing of a
different population's text**, which is not a property anyone can audit. Recorded as R20's
sixth arrival point, and the first of the six that fails because of *where its signal comes
from* rather than how the check is written.

## The proposed check

> **For each corrected fact, assert that its own SUPERSEDED VALUE is absent from the index rows
> its key resolves to.**

The superseded value is already recorded, in the field that exists for it: `correction_note`
names what the fact used to say, and for the facts corrected in this arc it names it explicitly
(`fine_limit`: "corrected from 'one hundred thousand TZS'"; `nssf_payment_deadline`: "previously
said 'verify deadline at nssf.go.tz'"). That is the right source because it is **written by the
same hand, at the same time, about the same text** as the correction itself — the property
`wrong_patterns` lacks.

Reuses, rather than rebuilds:

- `resolve_row_texts()` — unchanged. Hypothesis (a) was refuted, so resolution is not the
  problem and must not be touched while fixing something else.
- the polarity rule already shipped in the regen's payload gates and in
  `eval/index_quality/dryrun_regen_cap50_2026_10_05.py`: a superseded value **named in order to
  reject it** is a mention, not an assertion. Three live rows (57, 63, 159) deliberately carry
  their old value under a negation, because corpus rows assert it and an explicit contradiction
  is what overrides a trained prior where a bare restatement merely competes with it. A
  presence check would fail all three.

## Why it stays SOFT until measured against all 55

Two measurements already bound what to expect, and both say *do not gate on this yet*:

1. **The figure test is context-blind by construction.** Of 55 corrected facts, only **5** are
   figure-testable (`eval/controls/measure_correction_sync_adjacency_hole.py`); 47 corrections
   are qualitative and carry no figure, 3 are unresolved. It produced 2 flags: one genuine (row
   57) and one **false positive** — `vat_threshold_200m`'s row states TZS 100,000,000 correctly
   as the **6-month** threshold while its `wrong_pattern` targets 100,000,000 *"kwa mwaka"*.
   Same number, two periods, one right. That is not fixable by widening: the `wrong_pattern`
   already encodes the context and is right to.
2. **The gate's own history.** Its unfiltered first run flagged 8 and **7 were false positives**
   (87.5%), closed only by the negation filter — which its docstring correctly calls a heuristic,
   not a proof.

A hard gate on an unproven detector blocks a regen for what may be a correct fact. Per R21 that
is the expensive direction: a mechanism that can only under-report is cheap to iterate on; one
that blocks is not. And a blocked regen here has a specific cost — the two defects above were
*both* fixed by regens, so a false block delays corrections.

**Promotion criterion, stated in advance so it is not negotiated after the fact:** one full run
over all 55 corrected facts, every flag read and adjudicated, with the false-positive count
recorded. Promote to blocking only if that count is zero, and keep the adjudication committed so
a changed flag set fails the run instead of inheriting a stale verdict.

## What this does not fix, named so it is not assumed

- **Facts with no `correction_note`.** 194 of 249. They have never been found wrong once, so
  they are outside this gate's population by design — and `fine_limit` is the reminder that
  "never found wrong" is not the same as "right".
- **Qualitative corrections.** A correction from "there is a threshold" to "there is none" has
  no superseded *value* in the extractable sense; row 57 happened to have one (11,000,000).
- **A correction_note that does not quote the old value.** The check is only as good as that
  field, and nothing currently requires it to be quotable. If this is built, that requirement
  comes with it — and it is cheap, because the note is written at correction time by someone who
  has the old text in front of them.

## Immediate action taken instead

Row 57 fixed directly, with the same two-gate treatment rows 63 and 159 received: a **payload
gate** (polarity-checked text assertion) and a **critical query**. Its old critical-query anchor
was `['milioni kumi na moja']` — **the fabricated figure** — so that guard had been *requiring*
the fabrication to be retrievable since the 2026-08-29 correction, and any regen that fixed row
57 would have tripped it and read as the regression. Third instance of the
defect-defends-itself shape in two days, after `act_section_12`'s `wrong_patterns` rejecting the
correct Part XII citation and `check_facts_index_sync`'s `PINNED` needle requiring
`ifikapo tarehe 10`.

**The common cause of all three, worth more than the three fixes:** each was authored by
searching the index for text that is **present and unique** — and a stale row is present and
unique. Nothing in anchor or needle selection asks whether the text being pinned is **true**.
