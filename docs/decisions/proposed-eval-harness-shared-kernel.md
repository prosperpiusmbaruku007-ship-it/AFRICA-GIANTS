# PROPOSED — a shared, tested kernel for eval harnesses

**Status:** proposed, not built. Scoped 2026-09-24 after five harness defects in one pass.
**Question asked:** *is there anything structural to do, or is "suspect the specimen" the whole
answer?*

---

## The answer, first

**"Suspect the specimen" is the last line of defence, not the whole answer.** Four of the five
defects were mechanical — the same three operations re-implemented per harness, each time
slightly differently. One was not, and the split matters more than the count.

| # | defect | class | a shared kernel prevents it? |
|---|---|---|---|
| 1 | OOC sweep's filter knew 2 of the 9 ways corpora spell *"must be refused"* → reported **34 collisions, 33 false** | corpus semantics | **YES** — one tested `is_ooc_by_design()` |
| 2 | language scan flagged English patterns without asking what language they **guard** → **200 hits**, ~29% of all guards | **definition of the defect** | **NO** | 
| 3 | route diff excluded `none`, the eval_211 harm class → **0 diversions** for every candidate | diff semantics | **YES** — `diff_routes()` treats absence as a value |
| 4 | `re.escape()` on multi-word cues, which the router substring-matches → **0 changes for every multi-word cue** | cue matching | **YES** — `matches_cue()` mirroring production exactly |
| 5 | baseline keyed by row id, **18 ids duplicated across corpora** → **11 phantom changes** | row identity | **YES** — loader returns a unique positional key |

**Four of five, which matches the founder's estimate exactly.** Defect 2 is the residue and it
is the one to keep worrying about: no helper can tell you that your *definition of the defect*
is wrong. That is what "suspect the specimen" is actually for, and narrowing its job from five
things to one is the entire value of this proposal.

---

## The measured surface

| | count |
|---|---|
| Python harnesses under `eval/` | **66** |
| load JSONL rows themselves | **28** |
| hand-pick the question field from their own key list | **29** |
| do some form of before/after diffing | **27** |
| re-implement cue matching against production semantics | **4** |
| key a dict by row `id` | **28** |

**There is no shared module today.** Every one of the 66 starts from `open()`.

### The duplicate-id trap is LATENT, not active — state it precisely

1,250 id-bearing rows, 1,232 distinct, **18 duplicated**: `cc_01`–`cc_08` across
`clarification_copy_probes_008.jsonl` + `concord_1pl_in_scope_020.jsonl`, and `hc_01`–`hc_10`
across `headcount_contradiction_probes_010.jsonl` + `headcount_extraction_probes_012.jsonl`.

**No existing harness collides today.** Only three harnesses glob all corpora — two written on
2026-09-23 — and none of those three is id-keyed. The 28 id-keyed harnesses each load a single
corpus, or a set that does not contain both members of either pair.

⚠️ **So this is NOT "28 broken harnesses", and reporting it that way would be the fabricated-
defect failure R26 warns about.** It is a trap that has been sitting in the corpora unnoticed
and that **the very first whole-corpus harness hit immediately**. The fix is to make it
structurally impossible for the next one, not to edit 28 working files.

---

## What to build

`eval/kernel.py` — one module, no dependencies beyond stdlib + `chike`, with a committed
fixture and a test file that exercises **both limbs** of every function (R26).

### 1. `load_corpus(paths=None) -> list[Row]`

One loader. Returns rows carrying:

- `key` — **unique, positional** (`<relpath>:<lineno>`). Never the row id. This is the single
  change that makes defect 5 unrepresentable.
- `id` — the row's own id, kept for reporting, never for keying.
- `question` — resolved across the known field names (`question`, `question_sw`, `q`,
  `prompt`, `hypothesis`), in one place instead of 29.
- `ooc_by_design` — from `is_ooc_by_design(row)` below.
- `file`, `raw` — provenance and the untouched dict.

**Must assert non-empty**, so a loader change cannot silently turn a sweep into a clean result
over zero rows (R20).

### 2. `is_ooc_by_design(row) -> bool`

The nine field spellings, in one tested place: `expected_refusal`, `expected_in_scope`,
`subdomain`/`true_topic`/`topic`/`boundary_topic`/`family` prefixes, `answer_type`,
`gold_route`, `difficulty_tier`, `arm`, `expect`, and the `intent_expected`/`expected_intent`/
`expect_intent` family.

**Its test is a committed fixture with one row per spelling plus rows that must NOT classify as
OOC.** Positive-only would certify a function that returns `True` for everything — which is
exactly what the secret scan had (R26).

### 3. `matches_cue(cue, text) -> bool`

**Mirrors `chike.classification` / `chike.routing` exactly**: `\b`-prefixed cues are regex,
everything else is a plain lowercase substring. No escaping, ever.

Its test asserts the property that broke defect 4 — a multi-word cue matches a phrase
containing it — **and** a differential test that this function and production agree on every
cue currently in `chike_config.json` and `routing.py`. A cue matcher that drifts from
production is worse than none, because every sweep would then measure a system we do not ship
(R12's rationale, applied to the harness layer).

### 4. `diff_routes(before: dict, after: dict) -> list[Change]`

Absence is a value. `None`/`"none"` → `"corporate_tax"` is a change and the most consequential
one. Takes two `{key: route}` maps built from `load_corpus` keys.

**Requires a determinism assertion helper**: `assert_stable(fn, rows)` runs the router twice
and fails if it disagrees, so an unstable router surfaces as an error rather than as noise
spread across every candidate.

### 5. `Sweep` result container

Carries `why_this_population` and `bound` (the R21/R22 caveats) **inside the artifact**, so
the caveat cannot be separated from the number by being quoted — the property
`ab_retriever_full.py` already demonstrates and nothing else inherits.

---

## The new risk this introduces, and how to hold it

**A shared kernel is a shared single point of failure.** If `is_ooc_by_design()` is wrong,
every sweep is wrong *together*, and consistently — which is harder to notice than five
harnesses disagreeing. Today's five defects were each caught because a *specific* result
looked implausible; a uniformly wrong kernel produces plausible results everywhere.

Three mitigations, all cheap:

1. **Both-limb tests on every function**, against a committed fixture. Non-negotiable.
2. **`load_corpus` reports its own classification census** — how many rows were classified OOC
   by which field. A silent drop from 68 to 12 is then visible in every artifact that uses it,
   rather than invisible in all of them.
3. **Register the kernel in `eval/controls/audit_control_fires.py`** (R26 requires a row per
   new control) with planted specimens, so "does the kernel still work" is answered by the
   standing census rather than by memory.

---

## Migration: additive, not a rewrite

**Non-goal: editing the 28/29/27 existing harnesses.** They work, their results are committed,
and mechanically rewriting them is precisely the R20 hazard — a scripted pass that closes
sites without reading them. Their artifacts are historical records; changing how they load
data changes what they would report, for no benefit.

- **New harnesses use the kernel.** That is the whole migration.
- **Existing harnesses migrate only when touched for another reason**, and only if their
  artifact is being regenerated anyway.
- **Three exceptions, migrated with the kernel** because they glob all corpora and are
  therefore the ones the duplicate-id trap will actually reach:
  `eval/controls/sweep_ooc_phrases_vs_inscope.py`,
  `eval/routing/sweep_corporate_gate_widening_2026_09_23.py`,
  `eval/index_quality/audit_feegroup_curation_controls_verbatim.py`.

**Size:** one module (~200 lines), one fixture, one test file, three call-site migrations.
Comparable to a single sweep from this pass.

---

## Separately, and cheaper than all of the above

**Rename the 18 duplicated ids** so the trap stops existing. `cc_01`–`cc_08` in
`clarification_copy_probes_008.jsonl` and `hc_01`–`hc_10` in
`headcount_contradiction_probes_010.jsonl` are the newer/smaller side of each pair.

⚠️ **Do NOT do this casually.** Those ids are cited in committed artifacts, in
`guards_against` notes, and in PROGRESS.md; renaming breaks the link between a recorded result
and the row it came from — which is R18's whole concern. If done, it needs a mapping file
committed alongside, and it is a separate decision from this one.

**The kernel makes the duplicates harmless without touching them, which is why it is the
better first move.**
