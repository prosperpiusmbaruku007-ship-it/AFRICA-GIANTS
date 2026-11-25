# -*- coding: utf-8 -*-
"""LOCAL DRY-RUN of the 2026-11-24b R15 regen package, 220 -> 224 rows (a dated copy of dryrun_regen_2026_11_24.py): TWO NEW rows appended (219th: the SDL base, allowances included; 220th: medical services VAT-exempt on two conditions) and SIX rows revised IN PLACE
(row 4 p45_not_tanzanian: section number out of the served text; rows 20 and 21 the GN487A penalties in the gazetted Order's wording; row 66 wcf_threshold_no_minimum and row 89 SDL_source_law: the SDL half no longer says "cash"; row 108
form_number_payment_credit_slip: no payment form asserted). A DATED COPY of dryrun_regen_2026_11_23.py; its guard table is read from kaggle/regenerate_rag_e5.py so the two cannot disagree, and the regen's own payload gates
(scripts/rag_payload_gates.py) are EXECUTED, never re-implemented (the 2026-10-07 lesson: a dry run that re-implements the real gates is not a dry run of that run).

Loads the local e5 weights OFFLINE (HF_HUB_OFFLINE=1): `intfloat/multilingual-e5-base` is in the local cache; the regen header's "weights do not download" is true of downloading, not of loading.

    python eval/index_quality/dryrun_regen_2026_11_24.py   ->   eval/results/dryrun_regen_2026_11_24b.json
"""
import importlib.util
import json
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "dryrun_regen_2026_11_24b.json")


def parse_committed_guards(src):
    """[(name, query, [keywords])] for every critical query in the regen script, with the keyword list read by `ast.literal_eval`, i.e. EXACTLY the Python list the regen iterates (any keyword in the top 3 passes).

    ⛔ THE FIRST FIVE DRY RUNS GOT THIS WRONG, which is the whole reason this is a function with a test. They split the list text on "','" (no space), so a list written `['kuoa', 'kuolewa']` (a space after the comma) became ONE keyword, "kuoa', 'kuolewa", that no row can contain. Exactly the four multi-keyword guards (phone repair, GN487A marriage, BRELA striking-off, OSHA/WCF small-count) were reported as 'pre-existing failures that fail on the deployed index too'; on Kaggle all four PASS (2026-11-23 run: 91 guards, 0 failing). The harness was wrong about the index, not the index about itself.
    """
    import ast as _ast
    import re as _re
    out = []
    for name, query, kws in _re.findall(r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", src):
        out.append((name, query, list(_ast.literal_eval("[" + kws + "]")) if kws.strip() else []))
    return out


def _load_module(relpath, name):
    path = os.path.join(REPO, *relpath.split("/"))
    assert os.path.exists(path), (
        f"{relpath} is missing. A dry run that cannot load it must ABORT, not continue with one "
        f"fewer check -- that is the whole shape of the defect this file is being fixed for.")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_precompute():
    return _load_module("scripts/precompute_rag_embeddings.py", "precompute_rag_embeddings")


# The two NEW guards this package adds, with the fixture each question comes from.
NEW_GUARDS = [
    {"name": "Medicines are VAT-exempt, not zero-rated (the live 'Dawa zinatozwa VAT?' -> 'zero-rated (tozo 0%)')", "query": "query: Dawa zinatozwa VAT?", "anchor": "MSAMAHA, si zero-rated",
     "from": "eval/results/followup_deploy_live_2026_11_24.json, the live question of build 37cdf9d VERBATIM", "why_this_anchor": "the phrase that carries the claim, in no other row"},
    {"name": "PAYE base is employment income (the live 'PAYE ... basic salary only')", "query": "query: PAYE inakokotolewa kwa mshahara wa msingi tu au pamoja na posho?", "anchor": "MAPATO YA AJIRA yote",
     "from": "AUTHORED single-topic form (the live two-levy specimen ranked 6: a two-topic question the decomposer splits, and the SDL-base row is its natural top hit)", "why_this_anchor": "the base clause exists only in the new row"},
    {"name": "SDL deemed month of payment (the live 'si Desemba wala miezi mingine')", "query": "query: SDL ya mwezi Januari inahesabiwa kwa mshahara wa Januari au Desemba?", "anchor": "AMBAO yamelipwa",
     "from": "the live question of build 37cdf9d, verbatim in the live artifact", "why_this_anchor": "the deeming clause exists only in the new row"},
    {"name": "WCF base: earnings incl. fixed allowances, not cash only", "query": "query: WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?", "anchor": "posho zisizobadilika zinazolipwa kila mwezi",
     "from": "AUTHORED (no committed fixture asks the WCF base)", "why_this_anchor": "the base clause exists only in the new row"},
]


def main():
    precompute = _load_precompute()
    assert precompute.EMBED_MODEL == "intfloat/multilingual-e5-base", \
        f"unexpected embedder: {precompute.EMBED_MODEL}"

    # Build the prospective index text exactly as the regen does: the concise overrides where
    # present, the derived `key: value` fallback otherwise.
    # THE PRODUCTION BUILDER, called exactly as regenerate_rag_e5.py calls it -- never a
    # hand-rolled reconstruction (R24: build the context with the production call). Its contract
    # is (texts, keys, dropped); a 2-tuple unpack silently reorders them, which is what the
    # first run of this file did.
    texts, keys, dropped = precompute.build_fact_texts()
    assert texts and keys and len(texts) == len(keys), (
        f"builder returned {len(texts)} texts for {len(keys)} keys -- shape changed")
    # ── THE REGEN'S OWN PAYLOAD GATES, EXECUTED — NOT RE-IMPLEMENTED ────────────────────
    #
    # ⛔ THIS BLOCK USED TO BE FIVE HAND-WRITTEN ASSERTIONS ABOUT TWO ROWS, AND THAT IS WHY THIS
    # FILE SAID `SAFE TO RUN` ON A PACKAGE THE KAGGLE REGEN THEN REFUSED.
    #
    # On 2026-10-06 it reported 0 displacement across 40 committed guards, both new guards hit,
    # 184 -> 184 rows. The real run aborted on the same commit:
    #
    #     [FATAL] brela_foreign_late_filing_penalty ASSERTS the superseded value ['USD 25']
    #
    # Twelve facts were amended; the old block checked `brela_filing_fees` and
    # `company_registration_ladder` -- the two rows whoever wrote it remembered changing. R33 in
    # the validator layer: a check authored by the author of the change, scoped to the change the
    # author had in mind. The comment above it even said the right thing ("the regen has its own
    # payload gates, but a dry run that measures only RANKS can report SAFE TO RUN...") and then
    # answered it by re-deriving a subset.
    #
    # Sharper still: THIS FILE ALREADY KNEW NOT TO RE-DERIVE THE REGEN'S TABLES. It parses
    # ACCEPTED_AMBIGUOUS and the committed critical queries straight out of regenerate_rag_e5.py,
    # precisely so the two cannot disagree (see the two parsers below). That discipline was
    # applied to two tables and skipped for the third.
    #
    # The gates now live in scripts/rag_payload_gates.py and both runs import them, so this file
    # cannot pass a package the real run would reject. The count is asserted for the same reason
    # the regen asserts it: a gate list that silently shrinks is R20's check-that-cannot-fail.
    _gates = _load_module("scripts/rag_payload_gates.py", "rag_payload_gates")
    n_gates = _gates.run_payload_gates(keys, texts)
    assert n_gates >= 11, (
        f"only {n_gates} payload gate(s) ran; the regen enforces eleven. A dry run with fewer "
        f"gates than the run it models is the defect this block was rewritten to close.")
    print(f"payload gates executed from scripts/rag_payload_gates.py: {n_gates}")
    if dropped:
        print(f"builder dropped {len(dropped)} key(s): {sorted(dropped)[:8]}")
    print(f"prospective index: {len(texts)} rows")

    # --- A. anchor uniqueness, including the committed guards -------------------------------
    deployed = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                              encoding="utf-8"))
    anchor_rows = []
    for g in NEW_GUARDS:
        hits = [i for i, t in enumerate(texts) if g["anchor"].lower() in t.lower()]
        anchor_rows.append({"guard": g["name"], "anchor": g["anchor"], "matches": len(hits),
                            "rows": hits})
    ambiguous = [a for a in anchor_rows if a["matches"] != 1]
    assert not ambiguous, (
        f"a new guard's anchor does not resolve to exactly one fact: {ambiguous}. A dead anchor "
        f"never fires; an ambiguous one can pass on a fact it does not mean.")

    # ⛔⛔ EVERY COMMITTED ANCHOR, NOT JUST THE NEW ONES. THIS IS WHY THE 2026-10-05 KAGGLE RUN
    # FAILED AND WASTED A CYCLE.
    #
    # The first version of this harness checked only the two anchors this package ADDS. The
    # regen then blocked on an anchor this package did not touch: 'asilimia 10', the NSSF
    # employer guard's, which became ambiguous because the NEW rent_wht_rate row also states a
    # 10% rate. Everything substantive passed -- 184 facts, 0 self-retrieval failures, all 36
    # critical queries, rank gate 39/17/6 -- and nothing uploaded.
    #
    # THE PROPERTY THE HARNESS MISSED: inserting a row perturbs its neighbours' ANCHORS as well
    # as their RANKS. The displacement arm below already covers ranks; nothing covered anchors.
    # A new correct fact can therefore invalidate an OLD guard with no edit to any guard at all
    # -- which is the nat_23 45->46 lesson in the guard layer, and is exactly the shape where a
    # per-change check that only looks at the change itself is blind by construction.
    #
    # ACCEPTED_AMBIGUOUS is read FROM the regen rather than re-listed here, so the two cannot
    # drift. (My first local attempt at this check re-derived the set with a regex that silently
    # missed it across the intervening comment lines, and reported the OSHA/WCF guard as a
    # second real ambiguity -- a bad specimen in the instrument, where the Kaggle log had been
    # right all along. Parsed by name below, and asserted non-empty so a parse failure cannot
    # masquerade as "no exceptions".)
    import re as _re2
    _src = open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
    _blk = _re2.search(r"ACCEPTED_AMBIGUOUS\s*=\s*\{(.*?)\n\}", _src, _re2.S)
    assert _blk, "could not locate ACCEPTED_AMBIGUOUS in the regen -- refusing to guess it empty"
    accepted = set(_re2.findall(r"^\s*'([^']+)',", _blk.group(1), _re2.M))
    assert accepted, ("parsed ACCEPTED_AMBIGUOUS as EMPTY. It is not empty in the regen, so this "
                      "is a parse failure, and an empty exception set would report every "
                      "adjudicated-benign guard as a fresh defect.")

    all_anchor_faults = []
    for name, query, anchors in _re2.findall(
            r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", _src):
        for a in _re2.findall(r"'([^']*)'", anchors):
            hits = [(i, keys[i]) for i, t in enumerate(texts) if a.lower() in t.lower()]
            if len(hits) == 1:
                continue
            all_anchor_faults.append({
                "guard": name, "anchor": a,
                "kind": "DEAD" if not hits else "AMBIGUOUS",
                "matches": [{"row": i, "key": k} for i, k in hits][:6],
                "accepted_benign": name in accepted})
    blocking_anchor_faults = [f for f in all_anchor_faults if not f["accepted_benign"]]

    # --- embed -------------------------------------------------------------------------------
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(precompute.EMBED_MODEL)
    emb = model.encode([f"passage: {t}" for t in texts], batch_size=16,
                       show_progress_bar=False, convert_to_numpy=True)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    def top(query, n=3):
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        s = emb @ q
        idx = np.argsort(s)[-n:][::-1]
        return [(int(i), float(s[i])) for i in idx]

    # --- B. the two new guards reach their row ----------------------------------------------
    new_results = []
    for g in NEW_GUARDS:
        t3 = top(g["query"])
        hit = any(g["anchor"].lower() in texts[i].lower() for i, _ in t3)
        # full rank, so a near-miss is diagnosable rather than a bare red X
        q = model.encode([g["query"]], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        order = np.argsort(emb @ q)[::-1]
        rank = next((r for r, i in enumerate(order, 1)
                     if g["anchor"].lower() in texts[i].lower()), None)
        new_results.append({**{k: g[k] for k in ("name", "anchor", "from", "why_this_anchor")},
                            "in_top3": bool(hit), "rank": rank,
                            "top3": [texts[i][:110] for i, _ in t3]})
        print(f"  [{'PASS' if hit else 'FAIL'}] {g['name']}  rank={rank}")

    # --- C. DISPLACEMENT: no committed guard may regress ------------------------------------
    # Parsed out of the regen script's own critical_queries list so this cannot drift from it.
    src = open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
    committed = parse_committed_guards(src)
    assert len(committed) >= 91, f"parsed {len(committed)} committed critical queries; the regen runs at least 91"
    # ⛔ A BASELINE ARM IS MANDATORY HERE, NOT A REFINEMENT (R24, and this file's own precedent).
    # The first run of this script reported 4 "displacement regressions" and a DO-NOT-RUN
    # verdict. A guard failing on the PROSPECTIVE index is only displacement if it PASSES on the
    # DEPLOYED one. regenerate_rag_e5.py already records exactly this trap: nat_37/nat_38 were
    # found to "ALREADY FAIL against the currently deployed index -- confirmed independent of
    # any change in this cycle by testing them against kaggle/rag_facts_text.json as-is, before
    # any of this session's edits", and wiring guards for already-failing rows would only have
    # blocked that cycle's real wins. Without this arm the package would have been abandoned on
    # four failures it did not cause.
    base_emb = model.encode([f"passage: {t}" for t in deployed], batch_size=16,
                            show_progress_bar=False, convert_to_numpy=True)
    base_emb = base_emb / (np.linalg.norm(base_emb, axis=1, keepdims=True) + 1e-10)

    def base_top(query, n=3):
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        s = base_emb @ q
        return [(int(i), float(s[i])) for i in np.argsort(s)[-n:][::-1]]

    print(f"\ndisplacement check over {len(committed)} committed guards "
          f"(prospective vs DEPLOYED baseline):")
    regressions, preexisting = [], []
    for name, query, want in committed:
        if not want:
            continue
        t3 = top(query)
        hit = any(any(a.lower() in texts[i].lower() for a in want) for i, _ in t3)
        if hit:
            print(f"  [ok] {name[:62]}")
            continue
        b3 = base_top(query)
        base_hit = any(any(a.lower() in deployed[i].lower() for a in want) for i, _ in b3)
        rec = {"guard": name, "anchors": want,
               "prospective_top3": [texts[i][:100] for i, _ in t3],
               "deployed_top3": [deployed[i][:100] for i, _ in b3],
               "passes_on_deployed_index": base_hit}
        if base_hit:
            regressions.append(rec)            # genuine displacement caused by this package
            print(f"  [REGRESSED] {name[:52]}  <- passes on deployed, fails here")
        else:
            preexisting.append(rec)            # already broken; not this package's doing
            print(f"  [pre-existing fail] {name[:46]}  <- fails on deployed index too")

    # --- D. the two CHANGED rows still self-retrieve ----------------------------------------
    # No row is ADDED in this package, so "the new row self-retrieves" has no referent here. The
    # analogous risk for a CHANGED row is that the edit pushed it off its own text -- which is
    # what happened to electrical_test_fee_reduction (a before/after fee pair at 0.925 cosine, so
    # neither could be retrieved as itself). The ladder grew by four bands, which is the kind of
    # edit that can do it.
    self_checks = []
    for _k in ("wcf_threshold_no_minimum", "medicines_vat_exempt", "paye_base_employment_income", "sdl_deemed_month_of_payment", "wcf_contribution_base"):
        i = keys.index(_k)
        hit = i in [j for j, _ in top(f"query: {texts[i]}")]
        self_checks.append({"key": _k, "row": i, "self_retrieves": bool(hit)})
        print(f"  [{'ok' if hit else 'FAIL'}] self-retrieval: {_k} (row {i})")
    self_ok = all(c["self_retrieves"] for c in self_checks)

    out = {
        "_what": "Local offline dry-run of the 2026-11-24 R15 regen package (220 -> 224: medicines, PAYE base, SDL deemed month, WCF base; row 66 revised in place), before Kaggle.",
        "_model": precompute.EMBED_MODEL,
        "_offline": "HF_HUB_OFFLINE=1; weights already cached locally. The regen header's "
                    "'weights do not download locally' is true of DOWNLOADING, not of loading.",
        "prospective_row_count": len(texts),
        "deployed_row_count": len(deployed),
        "⚠️_rag_fact_count_must_be_bumped": {
            "from": len(deployed), "to": len(texts),
            "where": "kaggle/chike_config.json rag_fact_count",
            "⛔_WHEN": "IN THE SAME COMMIT AS THE FETCHED .npy/.json ARTIFACTS, NEVER BEFORE. "
                      "modal_app.py asserts this count against the loaded index and REFUSES TO "
                      "SERVE on a mismatch (verified live 2026-08-24: HTTP 500). The config is "
                      "fetched from GitHub at runtime, so bumping it while production still "
                      "holds the old index takes production DOWN.",
        },
        "anchor_uniqueness_new_guards": anchor_rows,
        "anchor_faults_ALL_committed_guards": all_anchor_faults,
        "anchor_faults_blocking": blocking_anchor_faults,
        "new_guards": new_results,
        "displacement_regressions_caused_by_this_package": regressions,
        "pre_existing_failures_not_caused_by_this_package": preexisting,
        "changed_rows_self_retrieve": self_checks,
        "verdict": ("SAFE TO RUN"
                    if not regressions and not blocking_anchor_faults
                    and all(r["in_top3"] for r in new_results) and self_ok
                    else "DO NOT RUN -- see regressions / anchor faults / failed guards"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"\nrows {len(deployed)} -> {len(texts)}  (rag_fact_count must follow, WITH the "
          f"artifacts)")
    print(f"changed rows self-retrieve: {self_ok}")
    print(f"anchor faults across ALL {len(all_anchor_faults) and 'committed' or 'committed'} "
          f"guards: {len(all_anchor_faults)} ({len(blocking_anchor_faults)} blocking, "
          f"{len(all_anchor_faults)-len(blocking_anchor_faults)} adjudicated-benign)")
    for f in blocking_anchor_faults:
        print(f"   [{f['kind']}] {f['guard']}: {f['anchor']!r} -> {f['matches']}")
    print(f"displacement regressions CAUSED BY THIS PACKAGE: {len(regressions)}")
    print(f"pre-existing failures (fail on the deployed index too): {len(preexisting)}")
    print(f"\nVERDICT: {out['verdict']}")
    print(f"wrote {OUT}")
    return 0 if out["verdict"].startswith("SAFE") else 1


if __name__ == "__main__":
    sys.exit(main())
