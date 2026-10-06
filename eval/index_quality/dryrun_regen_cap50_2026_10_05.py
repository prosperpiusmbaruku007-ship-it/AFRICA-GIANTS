# -*- coding: utf-8 -*-
"""LOCAL OFFLINE DRY RUN OF THE Cap.50 R.E.2023 R15 PACKAGE, BEFORE KAGGLE.

Second regen of 2026-10-05. The first shipped Part XII / rent_wht_rate / ext_31 and is live at
184 rows; this one ships the Cap.50 corrections read from the NSSF Act R.E.2023.

WHY A DRY RUN AT ALL -- the measured reason, not a precaution. The first package's Kaggle run
BLOCKED on an anchor it had not touched: `asilimia 10` became ambiguous because a new, correct
row also stated a 10% rate. Everything substantive had passed (184 facts, 0 self-retrieval
failures, all 36 critical queries, rank gate 39/17/6) and nothing uploaded. The harness checked
the anchors the change ADDED; the fault was in an anchor the change never named.

So this run checks EVERY committed anchor against the prospective index. That is the
generalisation the last cycle paid for: a per-change check that only inspects the change is
blind, by construction, to the change's effect on everything else.

WHAT THIS PACKAGE CHANGES, and both were LIVE AND WRONG in the 184-row index:
  row 159  `fine limit: one hundred thousand TZS`  -> 100x understated. That string is R.E.2015
           s.72(1)'s actual text; R.E.2023 s.76(1) reads "ten million shillings".
  row  63  `NSSF inalipwa ifikapo tarehe 10 ...`   -> the 10th, where s.14(1) says within one
           month after the end of the payroll month. The fact itself was corrected on
           2026-09-02 and its own verified_by records that the "10th" traces to "somewhere else
           in the corpus" -- this row IS that somewhere else, and nothing was watching it.
plus an ask-led CONCISE entry for `imprisonment_term_limit` (same statutory sentence as the
fine, led by the imprisonment vocabulary so the two rows win different questions).

THE NEW ANCHORS DELIBERATELY AVOID BARE MAGNITUDES. `milioni kumi` is unusable:
gn487a_penalty_noncitizen also reads 'TZS 10,000,000 (milioni kumi)', so an anchor on the
magnitude could pass on an unrelated levy -- the same two-row ambiguity that ruled out bare
'ss.437-447' for the Part XII guard and bare 'asilimia 10' for the NSSF employer guard.
"""
import importlib.util
import json
import os
import re
import sys

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "dryrun_regen_cap50_2026_10_05.json")


def _load_precompute():
    path = os.path.join(REPO, "scripts", "precompute_rag_embeddings.py")
    spec = importlib.util.spec_from_file_location("precompute_rag_embeddings", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["precompute_rag_embeddings"] = mod
    spec.loader.exec_module(mod)
    return mod


NEW_GUARDS = [
    {"name": "NSSF fine ceiling is ten million, not one hundred thousand (Cap.50 s.76(1))",
     "query": "query: Nisipolipa michango ya NSSF kabisa, nitatozwa faini ya kiasi gani?",
     "anchor": "kosa la NSSF ni TZS 10,000,000",
     "from": "authored for this package; the live defect was index row 159",
     "why_this_anchor": "carries the SUBJECT (kosa la NSSF) and the CLAIM (10,000,000) "
                        "together. Bare 'milioni kumi' matches gn487a_penalty_noncitizen too."},
    {"name": "NSSF deadline is one month after month-end, not the 10th (Cap.50 s.14(1))",
     "query": "query: Michango ya NSSF ya mwezi huu inatakiwa kulipwa lini?",
     "anchor": "ndani ya MWEZI MMOJA baada ya mwisho wa mwezi",
     "from": "authored for this package; the live defect was index row 63",
     "why_this_anchor": "the statutory period IS the claim under guard, not a proxy for it."},
]

# Keys whose embedded TEXT this package changes. Each must still self-retrieve, so a rewrite
# that makes a row unreachable by its own content fails here rather than in production.
CHANGED_TEXT_KEYS = ["fine_limit", "imprisonment_term_limit", "nssf_payment_deadline",
                     "efd_threshold_tzs_11m"]

# The superseded value each rewritten row must CONTRADICT but never ASSERT. Both rows name the
# old figure deliberately, under a negation, because four training rows assert the old fine and
# the model carries a prior for it -- an explicit contradiction is what overrides that, where a
# bare restatement of the right number merely competes with it.
SUPERSEDED = [
    ("fine_limit", r"one hundred thousand|laki moja|100[,.]?000(?![,.\d])"),
    # `tarehe 10`, NOT `ifikapo tarehe 10`. The first draft used the longer form -- the exact
    # wording of the row being REPLACED -- and the contradiction limb then reported False on a
    # row that does contradict it ("si tarehe 10"), because the replacement does not repeat the
    # old row's verb. A ban pattern must match the CLAIM (the date), not one phrasing of it.
    ("nssf_payment_deadline", r"tarehe 10\b|the 10th"),
    # Added 2026-10-06. Row 57's fabricated TZS 11,000,000 "EFD threshold", re-verified against
    # TAA Cap.438 s.44 on 2026-08-29 and found invented. The row must NAME it in order to
    # reject it -- corpus rows assert it and a bare restatement only competes with the trained
    # prior -- and must never assert it.
    ("efd_threshold_tzs_11m", r"11[,.]?000[,.]?000|milioni kumi na moja"),
]
NEGATED = r"(?:\bsi\b|\bnot\b|\bsio\b)[\s:,]*(?:TZS\s*)?$"

# ⛔ GUARDS WHOSE ANCHOR THIS PACKAGE CHANGES, mapped to the anchor they USED TO carry.
#
# Without this the displacement arm MISFILES them, and it did: the 'EFD threshold' guard came
# back "[pre-existing fail] <- fails on deployed index too", which reads as "not this package's
# doing". It is an artefact of the comparison. The baseline arm looks for the CURRENT anchor in
# the DEPLOYED index, and a newly-written anchor is by definition absent from it -- so base_hit
# is always False and any genuine failure is laundered into "pre-existing".
#
# That is the R24 shape in the diagnostic layer: an arm that agrees with the comforting answer
# for a reason unrelated to the question. The baseline must be asked with the OLD anchor, which
# is the only version of the guard the deployed index could ever have satisfied.
CHANGED_ANCHORS = {
    "EFD threshold": "milioni kumi na moja",
}


def main():
    precompute = _load_precompute()
    assert precompute.EMBED_MODEL == "intfloat/multilingual-e5-base", \
        f"unexpected embedder: {precompute.EMBED_MODEL}"

    # THE PRODUCTION BUILDER, called exactly as regenerate_rag_e5.py calls it (R24) -- never a
    # hand-rolled reconstruction. Its contract is (texts, keys, dropped).
    texts, keys, dropped = precompute.build_fact_texts()
    assert texts and keys and len(texts) == len(keys), (
        f"builder returned {len(texts)} texts for {len(keys)} keys -- shape changed")
    missing = [k for k in CHANGED_TEXT_KEYS if k not in keys]
    assert not missing, (
        f"{missing} are not in the built index at all. They were present in the 184-row index "
        f"this package replaces, so their disappearance is a defect, not a skippable check.")
    print(f"prospective index: {len(texts)} rows")

    deployed = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                              encoding="utf-8"))

    # --- A. anchor uniqueness: the new guards, then EVERY committed guard -------------------
    anchor_rows = []
    for g in NEW_GUARDS:
        hits = [(i, keys[i]) for i, t in enumerate(texts) if g["anchor"].lower() in t.lower()]
        anchor_rows.append({"guard": g["name"], "anchor": g["anchor"], "matches": len(hits),
                            "rows": [{"row": i, "key": k} for i, k in hits]})
    ambiguous = [a for a in anchor_rows if a["matches"] != 1]
    assert not ambiguous, (
        f"a new guard's anchor does not resolve to exactly one fact: {ambiguous}. A dead anchor "
        f"never fires; an ambiguous one can pass on a fact it does not mean.")

    # ACCEPTED_AMBIGUOUS is read FROM the regen rather than re-listed, so the two cannot drift.
    # A local re-derivation by regex silently missed an entry across intervening comment lines
    # last cycle and reported a false second ambiguity -- a bad specimen in the instrument,
    # where the Kaggle log was right. Asserted non-empty so a parse failure cannot masquerade
    # as "no exceptions".
    src = open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
    blk = re.search(r"ACCEPTED_AMBIGUOUS\s*=\s*\{(.*?)\n\}", src, re.S)
    assert blk, "could not locate ACCEPTED_AMBIGUOUS in the regen -- refusing to guess it empty"
    accepted = set(re.findall(r"^\s*'([^']+)',", blk.group(1), re.M))
    assert accepted, ("parsed ACCEPTED_AMBIGUOUS as EMPTY. It is not empty in the regen, so this "
                      "is a parse failure, and an empty exception set would report every "
                      "adjudicated-benign guard as a fresh defect.")

    committed = re.findall(
        r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", src)
    assert committed, "parsed zero committed critical queries -- the regex no longer matches"

    all_anchor_faults = []
    for name, _query, anchors in committed:
        for a in re.findall(r"'([^']*)'", anchors):
            hits = [(i, keys[i]) for i, t in enumerate(texts) if a.lower() in t.lower()]
            if len(hits) == 1:
                continue
            all_anchor_faults.append({
                "guard": name, "anchor": a,
                "kind": "DEAD" if not hits else "AMBIGUOUS",
                "matches": [{"row": i, "key": k} for i, k in hits][:6],
                "accepted_benign": name in accepted})
    blocking_anchor_faults = [f for f in all_anchor_faults if not f["accepted_benign"]]

    # --- embed ------------------------------------------------------------------------------
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(precompute.EMBED_MODEL)
    emb = model.encode([f"passage: {t}" for t in texts], batch_size=16,
                       show_progress_bar=False, convert_to_numpy=True)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    def top(query, n=3):
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        s = emb @ q
        return [(int(i), float(s[i])) for i in np.argsort(s)[-n:][::-1]]

    # --- B. the new guards reach their row --------------------------------------------------
    print("\nnew guards:")
    new_results = []
    for g in NEW_GUARDS:
        t3 = top(g["query"])
        hit = any(g["anchor"].lower() in texts[i].lower() for i, _ in t3)
        q = model.encode([g["query"]], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        order = np.argsort(emb @ q)[::-1]
        rank = next((r for r, i in enumerate(order, 1)
                     if g["anchor"].lower() in texts[i].lower()), None)
        new_results.append({**{k: g[k] for k in ("name", "anchor", "from", "why_this_anchor")},
                            "in_top3": bool(hit), "rank": rank,
                            "top3": [texts[i][:110] for i, _ in t3]})
        print(f"  [{'PASS' if hit else 'FAIL'}] {g['name'][:60]}  rank={rank}")

    # --- C. DISPLACEMENT, against the DEPLOYED index as baseline ----------------------------
    # ⛔ THE BASELINE ARM IS MANDATORY, NOT A REFINEMENT (R24). The first run of the sibling
    # harness reported 4 "displacement regressions" and a DO-NOT-RUN verdict; all four already
    # failed on the DEPLOYED index, so the package would have been abandoned on failures it did
    # not cause. A guard failing here is displacement only if it PASSES on the deployed index.
    base_emb = model.encode([f"passage: {t}" for t in deployed], batch_size=16,
                            show_progress_bar=False, convert_to_numpy=True)
    base_emb = base_emb / (np.linalg.norm(base_emb, axis=1, keepdims=True) + 1e-10)

    def base_top(query, n=3):
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        s = base_emb @ q
        return [(int(i), float(s[i])) for i in np.argsort(s)[-n:][::-1]]

    print(f"\ndisplacement over {len(committed)} committed guards (prospective vs DEPLOYED):")
    regressions, preexisting = [], []
    for name, query, anchors in committed:
        want = [a for a in re.findall(r"'([^']*)'", anchors) if a.strip()]
        if not want:
            continue
        t3 = top(query)
        if any(any(a.lower() in texts[i].lower() for a in want) for i, _ in t3):
            continue
        b3 = base_top(query)
        # Ask the baseline with the anchor the deployed index could actually have satisfied.
        base_want = [CHANGED_ANCHORS[name]] if name in CHANGED_ANCHORS else want
        base_hit = any(any(a.lower() in deployed[i].lower() for a in base_want)
                       for i, _ in b3)
        rec = {"guard": name, "anchors": want,
               "baseline_anchor_used": base_want,
               "anchor_changed_by_this_package": name in CHANGED_ANCHORS,
               "prospective_top3": [texts[i][:100] for i, _ in t3],
               "deployed_top3": [deployed[i][:100] for i, _ in b3],
               "passes_on_deployed_index": base_hit}
        if base_hit:
            regressions.append(rec)
            print(f"  [REGRESSED] {name[:52]}  <- passes on deployed, fails here")
        else:
            preexisting.append(rec)
            print(f"  [pre-existing fail] {name[:46]}  <- fails on deployed index too")

    # --- D. every REWRITTEN row self-retrieves ----------------------------------------------
    print("\nself-retrieval of rewritten rows:")
    self_results = []
    for k in CHANGED_TEXT_KEYS:
        i = keys.index(k)
        ok = i in [j for j, _ in top(f"query: {texts[i]}")]
        self_results.append({"key": k, "row": i, "self_retrieves": bool(ok),
                             "text": texts[i][:170]})
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    self_ok = all(r["self_retrieves"] for r in self_results)

    # --- E. POLARITY, not presence ----------------------------------------------------------
    # The regen's payload gate runs this same check; re-derived here against the built texts
    # rather than trusted, so a disagreement between the two surfaces in the dry run rather
    # than on Kaggle. A presence gate and a polarity gate are indistinguishable until the
    # protected text contains the banned string, and then they are opposites.
    print("\npolarity of the superseded values:")
    polarity = []
    for k, stale in SUPERSEDED:
        row = texts[keys.index(k)]
        asserted = [m.group(0) for m in re.finditer(stale, row, re.I)
                    if not re.search(NEGATED, row[max(0, m.start() - 14):m.start()], re.I)]
        contradicts = bool(re.search(stale, row, re.I))
        polarity.append({"key": k, "asserts_superseded_value": asserted,
                         "explicitly_contradicts_it": contradicts, "text": row})
        print(f"  [{'ok' if not asserted and contradicts else 'FAIL'}] {k}: "
              f"asserted={asserted} contradicts={contradicts}")
    polarity_ok = all(not p["asserts_superseded_value"] and p["explicitly_contradicts_it"]
                      for p in polarity)

    out = {
        "_what": "Local offline dry run of the Cap.50 R.E.2023 R15 regen package "
                 "(second package of 2026-10-05), before Kaggle.",
        "_model": precompute.EMBED_MODEL,
        "_offline": "HF_HUB_OFFLINE=1; weights already cached locally. The regen header's "
                    "'weights do not download locally' is true of DOWNLOADING, not of loading.",
        "_two_live_defects_this_closes": {
            "row_159": "fine limit: one hundred thousand TZS -- R.E.2015 s.72(1) text, 100x "
                       "understated against R.E.2023 s.76(1)'s ten million shillings",
            "row_63": "NSSF inalipwa ifikapo tarehe 10 -- the 10th, where s.14(1) says within "
                      "one month after month-end; the fact's own verified_by says the 10th "
                      "appears in no source",
        },
        "prospective_row_count": len(texts),
        "deployed_row_count": len(deployed),
        "⚠️_rag_fact_count": {
            "from": len(deployed), "to": len(texts),
            "where": "kaggle/chike_config.json rag_fact_count",
            "⛔_WHEN": "IN THE SAME COMMIT AS THE FETCHED .npy/.json ARTIFACTS, NEVER BEFORE. "
                      "modal_app.py asserts this count against the loaded index and REFUSES TO "
                      "SERVE on a mismatch (verified live 2026-08-24: HTTP 500). The config is "
                      "fetched from GitHub at runtime, so bumping it while production still "
                      "holds the old index takes production DOWN.",
        },
        "builder_dropped_keys": sorted(dropped) if dropped else [],
        "anchor_uniqueness_new_guards": anchor_rows,
        "anchor_faults_ALL_committed_guards": all_anchor_faults,
        "anchor_faults_blocking": blocking_anchor_faults,
        "new_guards": new_results,
        "displacement_regressions_caused_by_this_package": regressions,
        "pre_existing_failures_not_caused_by_this_package": preexisting,
        "rewritten_rows_self_retrieve": self_results,
        "superseded_value_polarity": polarity,
        "verdict": ("SAFE TO RUN"
                    if not regressions and not blocking_anchor_faults
                    and all(r["in_top3"] for r in new_results) and self_ok and polarity_ok
                    else "DO NOT RUN -- see regressions / anchor faults / failed guards"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"\nrows {len(deployed)} -> {len(texts)}  (rag_fact_count follows, WITH the artifacts)")
    print(f"anchor faults across all committed guards: {len(all_anchor_faults)} "
          f"({len(blocking_anchor_faults)} blocking, "
          f"{len(all_anchor_faults) - len(blocking_anchor_faults)} adjudicated-benign)")
    for f in blocking_anchor_faults:
        print(f"   [{f['kind']}] {f['guard']}: {f['anchor']!r} -> {f['matches']}")
    print(f"displacement regressions CAUSED BY THIS PACKAGE: {len(regressions)}")
    print(f"pre-existing failures (fail on the deployed index too): {len(preexisting)}")
    print(f"self-retrieval: {self_ok};  polarity clean: {polarity_ok}")
    print(f"\nVERDICT: {out['verdict']}")
    print(f"wrote {OUT}")
    return 0 if out["verdict"].startswith("SAFE") else 1


if __name__ == "__main__":
    sys.exit(main())
