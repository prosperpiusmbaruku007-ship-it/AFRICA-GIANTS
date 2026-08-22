# R10 CHANGE — fix the regen verification guards

**Status: ✅ APPROVED BY THE FOUNDER AND APPLIED, 2026-08-22.** Applied to
`kaggle/regenerate_rag_e5.py`, plus the follow-up pass over the remaining ambiguous guards, which
the founder directed to be done immediately rather than deferred.

**Two departures from the proposal below, both recorded rather than silently absorbed:**

1. **`KNOWN_FAILING` needed TWO entries, not one.** The proposal listed only the `nat_27` guard.
   Once `nat_36`'s guard uses verbatim phrasing it fails too (its fact is rank 17 on the real
   question, rank 2 only on the paraphrase). Both are bucketed.
2. **A third fault class was found during the follow-up pass: DEAD ANCHORS.** `elfu 22`,
   `28 julai` and `efd threshold tzs 11m` match **zero** index facts and could never have fired.
   Each hid behind a live ambiguous sibling that always passed. A `[DEAD-ANCHOR]` check was added
   and blocks.

**Also added beyond the proposal:** `[ORPHAN-KNOWN-FAIL]` (a bucketed name matching no guard) and
`ACCEPTED_AMBIGUOUS` (one guard whose ambiguity is adjudicated benign — see §5 below).

Verified by local dry-run before any Kaggle run: `eval/index_quality/verify_regen_guards_local.py`
→ **24 PASS · 0 FAIL · 2 KNOWN-FAIL · 0 STALE · 0 ORPHAN · 0 ambiguous · 0 dead · regen not
blocked.**

---

## Original proposal follows

Evidence: `eval/index_quality/audit_regen_guards.py` → `eval/results/regen_guard_audit.json`
(read-only AST parse of the regen script; no import, no execution, no network).

---

## 1. What the audit found

All 26 critical-query guards were checked for the two faults found by accident. **2 of 26 are
clean.**

| fault | count | meaning |
|---|---|---|
| `AMBIGUOUS_KEYWORD` | **18** | the expected keyword appears in **more than one** index fact, so the guard can pass on a fact it does not mean |
| `MULTIPLE_SATISFIERS_IN_TOP3` | **8** | right now, **more than one fact in the guard's own top-3 satisfies it** — it cannot tell which one it passed on |
| `NON_VERBATIM_NEAR` | **5** | differs from the real eval row by **case and/or a question mark only** — all five are the displacement guards |
| `NON_VERBATIM` | 17 | query text appears in no corpus. **Not automatically a fault** — most are deliberate synthetic probes for named failures. Recorded as risk, per R17's "a paraphrase passed here but missed on the real phrasing" |
| `CURRENTLY_FAILING` | 0 | every guard passes today, which is the problem |

**Worst ambiguity:** `SDL rate` expects `3.5` (**6** facts); `BRELA annual return` expects `22,000`
(**6**); `Facilitator penalty` expects `5,000,000` (**6**); `VAT standard rate` expects `18%` (**6**).

**The two concrete failures already proven:**

- **`nat_36`** — guard phrasing puts fact [57] at **rank 2**; the verbatim eval text puts it at
  **rank 17**. One capital letter and one `?`.
- **`nat_27`** — guard tests `'18%' in fact_text`; its top-3 contains [64]
  *vat withholding formula correct* ("the standard 18% VAT is split…"), which satisfies it.
  **It reports [13] as retrieved when [13] is at rank 8** on the guard's own phrasing, and rank 15
  on the real one.

---

## 2. Proposed change

### 2a. Displacement guards use VERBATIM eval text

Five guards, changed to the exact question string from
`eval/accuracy_gate/edge_probe_natural_048.jsonl` (lowercase, no trailing `?`).

### 2b. Keywords become substrings VERIFIED UNIQUE in the index

Each guard asserts a string that occurs in exactly one fact, so it cannot pass on a neighbour.
All five verified unique against the deployed 221-fact index:

| guard | intended fact | proposed keyword | uniqueness |
|---|---|---|---|
| nat_27 VAT standard rate | [13] | `NEVER 14%` (or `unchanged since 2015`) | ✅ unique |
| nat_36 EFD threshold | [57] | `milioni kumi na moja` | ✅ unique |
| nat_43 GN605A sectors | [72] | `hakina kiwango kimoja` | ✅ unique |
| nat_26 VAT 6-month | [146] | `100,000,000 kwa miezi 6` | ✅ unique |
| nat_34 company reg fee | [114] / [130] | `company registration fee 1` / `company name reservation fee` | ✅ unique |

**The remaining 13 ambiguous guards** should get the same treatment. Their intended fact is not
declared anywhere, so each needs one decision from someone who knows what it was meant to protect.
Proposed as a follow-up pass, not bundled here.

### 2c. A KNOWN-FAILING bucket

`nat_27`'s guard **will fail** once it is verbatim + unique-keyword — [13] is at rank 15. That is
the correct result. A failing critical query currently sets `critical_pass = False` and blocks the
regen, so the bucket holds it without blocking:

```python
# Guards that are EXPECTED to fail today. A row here is a KNOWN, TRACKED retrieval defect,
# not a passing guard and not an absent one. Removing a row from this set is how the defect
# gets closed; adding one requires a PROGRESS entry naming why.
KNOWN_FAILING = {
    # [13] (VAT standard rate) is rank 15 for the verbatim nat_27 question. nat_27 answers
    # correctly from model weights, not from retrieval — see PROGRESS 2026-08-22 grounding
    # entry. Closing this means rewriting [13] ask-first (measured: rank 15 -> 2).
    'VAT standard rate (nat_27 displacement guard)',
}
```

and in the loop:

```python
    status = 'PASS' if found else 'FAIL'
    if not found and name in KNOWN_FAILING:
        status = 'KNOWN-FAIL'          # visible, tracked, does not block
    elif not found:
        critical_pass = False
    print(f'[{status}] {name}')
```

Plus a summary line so the count is visible rather than buried:
`print(f'{len(KNOWN_FAILING)} known-failing guard(s): {sorted(KNOWN_FAILING)}')`

and an assertion that the set does not silently grow stale — a name in `KNOWN_FAILING` that
actually **passes** should be reported as a defect too (the guard was fixed and nobody removed it):

```python
    if found and name in KNOWN_FAILING:
        print(f'[STALE-KNOWN-FAIL] {name} now PASSES — remove it from KNOWN_FAILING')
        critical_pass = False
```

---

## 3. Why this is worth an R10 exception

The regen gate is what certifies the index that production serves. **A gate that passes on a
phrasing production never sends, and one that matches the wrong fact by substring, are worse than
no gate — they have been actively certifying an index with known unretrievable facts.** Both
defects are proven, not suspected, and 18 of 26 guards share the second one.

**Risk of the change:** it makes the regen stricter, so the next regen may surface further
failures. That is the intended effect. The `KNOWN_FAILING` bucket keeps that from blocking a regen
while leaving each defect visible.

**Scope:** `kaggle/regenerate_rag_e5.py` only. No change to `chike_config.json`, the notebooks, or
any other `kaggle/` file. No change to the index, the facts, or production.

---

## 4. What I need

Explicit approval to edit `kaggle/regenerate_rag_e5.py` for 2a, 2b (the five displacement guards)
and 2c (the bucket). The 13 remaining ambiguous guards are proposed as a separate follow-up, since
each needs a decision about what it was meant to protect.

---

## 5. FOLLOW-UP PASS — the remaining ambiguous guards (done 2026-08-22, same session)

It was **14**, not 13 — `VAT registration threshold (displacement guard)` is also ambiguous and was
not in the original five. Each was resolved by identifying the fact it was meant to protect and
anchoring to a substring unique to that fact:

| guard | intended fact | new anchor |
|---|---|---|
| GN487A penalty | [20] | `Faini kwa mgeni` |
| SDL rate | [5] | `asilimia tatu na nusu` |
| NSSF employer | [9] | `asilimia 10` (dropped ambiguous `10%`) |
| BRELA annual return | [134] | `kila mwaka ni TZS 22,000` (dropped dead `elfu 22`) |
| VAT withholding services | [17] | `services is 6` (dropped ambiguous `6%`) |
| Zero-rated input VAT | [89] | `input vat` (dropped ambiguous `ndiyo`) |
| GN487A effective date | [19] | `came into effect on 28 July` (dropped dead `28 julai`) |
| GN487A full name | [173] | `gn487a full legal name` |
| Facilitator penalty | [21] | `milioni tano` (dropped ambiguous `5,000,000`) |
| License lending facilitation | [22] | `kukopesha` (dropped ambiguous `leseni`) |
| PAYE 800K band | [211] | `78,000` (dropped ambiguous `760`, `25%`) |
| EFD threshold | [57] | `milioni kumi na moja` (dropped dead `efd threshold tzs 11m`) |
| VAT registration threshold | [145] | `200,000,000 kwa miezi 12` |
| OSHA/WCF small-count | [68] **or** [69] | **left ambiguous — adjudicated benign** |

**Every guard's purpose was identifiable, so none was deleted.** The founder's instruction was that
a guard nobody can state the purpose of should be deleted rather than repaired; that case did not
arise. All 26 have a stateable purpose and a fact they protect.

**One finding worth carrying:** the `VAT registration threshold` guard **passes while the
displacement it was written to catch is happening.** [57] (the EFD fact, which mentions 200M only as
a contrast) is at **rank 1** for the VAT-registration query, above [145], the fact actually asked
for. The old `200,000,000` anchor matched [15], [57] and [145] alike, so the guard could not see its
own feared displacement had occurred. It now anchors to [145] and still passes at rank 2 — but a
further slip will be caught.

**The general rule, from the one accepted ambiguity:** *ambiguity is a fault when the alternative
fact would be a **wrong** answer, not merely when more than one fact matches.* `OSHA/WCF
small-count` matches [68] and [69]; both state the thing it protects, so pinning it to one would
fail spuriously on the other.
