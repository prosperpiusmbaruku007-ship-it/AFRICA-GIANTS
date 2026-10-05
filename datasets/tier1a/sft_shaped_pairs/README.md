# `sft_shaped_pairs/` — pairs that do NOT carry the 18-field contract

**Moved here from `cleaned_pairs/` on 2026-10-05.** 8 files, 2,705 rows.

## Why they moved

Two pipeline generations were writing into `datasets/tier1a/cleaned_pairs/`, separated only by a
filename convention:

```
batch_NNN_cleaned.jsonl          10 files   1,715 pairs   18-field schema  <- stayed
cleaned_pairs_batch_NNN.jsonl     8 files   2,705 pairs   SFT-shaped       <- moved here
```

The rows here carry `instruction` / `input` / `output` / `system` and **no provenance metadata at
all** — no `primary_source_url`, no `verified_by`, no `effective_date`, no `eval_set`.
`cleaned_pairs/` asserts, by R3, that everything in it has all 18 fields. These rows never did, so
the directory name was making a promise the contents could not keep — and that mismatch is what
made `validate_dataset.py` fail on everything and go inert for an unknown length of time.

**They were NOT backfilled into the 18-field schema.** Inventing `primary_source_url` and
`verified_by` values for rows whose provenance was never recorded would be reconstructing
evidence rather than recovering it — the opposite of what the schema exists for. A fabricated
citation is worse than an absent one, because an absent one is visible.

## They are still in the training set, deliberately

`scripts/generate_sft.py` reads **both** directories (`CLEANED_DIRS`), and its `fmt_pair` already
supported both shapes. These 2,705 rows are **61% of the 4,410 non-eval pairs** the current
training set is built from, so dropping them would be a far bigger change than the directory
move. Verified byte-identical across the move: the generated `train_sft.jsonl` and
`val_sft.jsonl` hash the same before and after.

## ⚠️ What cannot be enforced on these rows

- **Gate 1 (schema + whitelist)** — not applicable. `validate_dataset.py` does not scan this
  directory, and would reject every row if it did.
- **Gate 2 (expert sign-off on a 10% sample)** — a reviewer cannot check a claim with no cited
  source.
- **Gate 3 (eval-set exclusion)** — **these rows have no `eval_set` field**, so
  `p.get("eval_set", False)` is always `False` and every one of them is unconditionally
  training data. **None of them can be held out**, which also means none can ever be used as
  eval without first acquiring the field.

That is the real cost of the missing metadata, and it is why this directory is a holding area
rather than a second home. The way out is re-deriving each row from a source document under the
current pipeline, not editing fields onto the rows that exist.
