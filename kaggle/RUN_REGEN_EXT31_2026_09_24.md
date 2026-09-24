# R15 REGEN PACKAGE — ext_31 ask-alignment (2026-09-24, second regen of the day)

Ships **one** correction staged in the repo and not in the deployed index:

| fact key | change | staged |
|---|---|---|
| `OSHA_safety_officer_threshold` | label-led `key: value` fallback → ask-aligned Swahili-first text in `CONCISE_BILINGUAL_FACTS` | `bb2c1ff` |

## Why this one is a different shape from the last two

The 2026-09-24 morning regen shipped two corrections that were **wrong strings** — `Section XII`
and the ambiguous `kodi ya chini` gloss. **This fact was entirely correct and still failed.**

The served row was the locked fact's own text, opening *"OSHA safety officer threshold:
Occupational Health and Safety Act Cap.297 s.11(1) requires…"* — **English-first and
label-led.** For the real user phrasing

> *"Kiwandani kwetu tuna wafanyakazi zaidi ya ishirini. Ni lazima tuwe na afisa maalum wa
> usalama kazini?"*

it measured at **BOUNDARY (rank 4–16)** in the bucket-E reach run, and the live reply asserted
**exactly the phrasing the fact's own text forbids** (*"must hire a safety officer above N
employees"*).

So this is a **REACH** defect fixed by content, not a content error. Re-led with the asker's
words — *afisa wa usalama kazini*, *wafanyakazi zaidi ya 20*, *kiwandani* — then the answer,
then the mechanism. The `nat_36` lever (rank 17 → 1 from vocabulary alone), applied per-row.

`locked_facts.json` is **untouched**: its citations stay where R13 `generate-from-facts` reads
them, and are kept out of the embedded text per the standing rule in
`precompute_rag_embeddings.py` (folding citations in cost `nat_05` ranks 24 → 59).

## The payload gate

`regenerate_rag_e5.py` carries a **third** payload assertion, at the stated cost of one line per
shipped correction. It asserts **reachability-shaped** content, not correctness — *a gate that
only ever checks for wrong strings would pass this row in both its broken and its fixed state:*

1. the row is **not** the label-led fallback;
2. it **leads** with `Afisa wa usalama kazini` (a row that merely *contains* the words is not
   the fix);
3. it carries **no** `Cap.297` / `s.11` citation in embedded text;
4. it still contains `NOT a professionally hired/dedicated 'safety officer'` — the `ext_31`
   needle in `bucket_e_reach_probes_014.jsonl`. Dropping it would silently break the fixture
   that *measured* this defect.

Exercised offline before shipping (R26, both limbs): clean row **passes**; pre-fix row, cited
variant and needle-dropped variant each **fail** on the right limb.

## The cell

```python
!rm -rf /kaggle/working/AFRICA-GIANTS
!git clone --depth 50 https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git /kaggle/working/AFRICA-GIANTS
%cd /kaggle/working/AFRICA-GIANTS
!git log -1 --format='CLONED AT %h %ad %s' --date=iso

!pip -q install sentence-transformers
!python kaggle/regenerate_rag_e5.py
```

The clone must contain **`bb2c1ff`** or the payload gate will fail with `[FATAL] … still the
label-led key: value fallback` — which is the gate working, not a problem to route around.

## What to check in the output

1. **`[OK] payload gate: OSHA_safety_officer_threshold is ask-aligned, uncited, needle intact`**
2. **183 rows** built — this change replaces a row, it does not add one. A different count means
   something else moved too.
3. The full verification block: **34/34** guards, as on the morning run.

## After it lands — do not skip, the index is not live until this is done

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` and commit to **both** `chike-inference/`
   and `kaggle/` in one commit (R15 step 4 — separate commits trip `artifacts_diverged`).
2. R16: `python -m modal app stop chike-inference --yes`, then deploy with
   `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`.
3. **Live check that exercises this specific change**, plus a negative:
   - ask the `ext_31` question verbatim → the reply must say *mwakilishi* / *kuteua*, and must
     **not** say *afisa maalum* or *kuajiri*;
   - **negative:** `kodi ya majengo` must still refuse (a config-only phrase absent from the
     hardcoded fallback — the pairing that separates *"the fix works"* from *"the container is
     stale"*).
4. Flip `tests/test_check_rag_index_freshness.py` back to `assert ok is True` and rename it —
   it currently asserts **STALE**, and that assertion is the only thing tracking that this
   rewrite is not live.
