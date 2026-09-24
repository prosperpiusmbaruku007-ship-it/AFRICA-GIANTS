# BUCKET E REACH MEASUREMENT — Kaggle package

**The question:** on rows where the model answered **wrong** and the supporting fact **is in
the shipped index**, does that fact actually reach the context production sends to the model?

**Why it gates the retrain:** if the facts are not reaching the model, retraining spends the
most expensive resource in the project on the wrong layer. This distinguishes *never
retrieved* from *retrieved and ignored* — two failures that look identical from a reply.

Runs on Kaggle because `intfloat/multilingual-e5-base` does not download on the local network.

---

## The fixture, and how it was built

`eval/grounding/bucket_e_reach_probes_014.jsonl` — **14 rows**.

Every one of the 15 bucket-E rows was checked by direct index lookup first, not just a sample.
Result: **14 have a supporting fact in the shipped index; 1 does not.**

**`ext_06` (partnership taxation) was DROPPED.** The only matching rows are BRELA
*registration* structures — nothing states that a partnership is not taxed at entity level or
that partners are taxed at their own rates. **It is a coverage gap, not a reach question.**
Leaving it in would have produced a number that reads as reach failure when it is absence.

Two calls changed on the full pass, which is the argument for doing it:

- **`ext_11` was nearly dropped as "no fact" and is in fact covered** — the new-business
  exemption condition (*"lazima aombe kwa Kamishna na aidhinishwe"*) sits inside the
  presumptive-bands row, which the first needle search missed.
- **`ext_31` is the sharpest row in the fixture.** Index row 86 explicitly says: *"Do NOT
  phrase this as 'must hire a safety officer above N employees'"*. The live reply said exactly
  that. **If that row reaches the context and the reply still says it, the defect is not
  reach** — and that single row does more to separate the two hypotheses than the other
  thirteen.

All 14 needles verified to resolve to **exactly one** index row before freezing.

---

## The cell

```python
!rm -rf /kaggle/working/AFRICA-GIANTS
!git clone --depth 50 https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git /kaggle/working/AFRICA-GIANTS
%cd /kaggle/working/AFRICA-GIANTS
!git log -1 --format='CLONED AT %h %ad %s' --date=iso

!pip -q install sentence-transformers

!python eval/grounding/measure_fact_reach.py \
    --probes-jsonl eval/grounding/bucket_e_reach_probes_014.jsonl \
    --out eval/results/bucket_e_reach_2026_09_24.json
```

No HF token needed — it reads the index from the repo (`chike-inference/`, which is what
production loads) and only downloads the embedder.

---

## What to check in the output

1. **`[probes] 14 loaded from eval/grounding/bucket_e_reach_probes_014.jsonl`**
   followed by the population line naming it outcome-conditioned on failure. If it says
   *"34 loaded ... survivorship-biased floor fixture"*, the `--probes-jsonl` flag did not take
   and it measured the wrong population entirely.

2. **`[index] deployed: 183 rows from .../chike-inference`** — the index shipped today.

3. **The per-probe categories.** `IN_TOP3` / `IN_POOL` / `BOUNDARY` (rank 4–16) / `ABSENT`.
   The split is the whole result:
   - **mostly `IN_TOP3`** → the facts DO reach the model and it is not using them. The problem
     is not retrieval, and the next investment is not retrieval.
   - **mostly `BOUNDARY`/`ABSENT`** → the facts do not reach. Retrieval work is indicated and
     the retrain should wait.
   - **split** → the most likely outcome, and the per-row detail matters more than the ratio.

4. **`ext_31` specifically.** Note its category by name when you paste back.

---

## What to paste back

The whole cell output. The per-probe table matters more than the summary — the decision turns
on which rows fail, not how many.

---

## The caveat, which lives in the artifact rather than only here

The artifact carries `fixture_caveat` stating: this establishes reach on an **authored
edge-probe population**, outcome-conditioned on failure, **not** a corpus-wide or gate-level
claim. It is the correct scope for an investment decision and the wrong scope for a headline.
It ships inside the JSON so it cannot be separated from the number by being quoted.
