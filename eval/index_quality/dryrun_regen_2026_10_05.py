# -*- coding: utf-8 -*-
"""LOCAL DRY-RUN VERIFICATION OF THE 2026-10-05 R15 REGEN PACKAGE, BEFORE IT RUNS ON KAGGLE.

WHY THIS CAN RUN AT ALL, which corrects a standing note in this repo. `regenerate_rag_e5.py`'s
own header says the e5 weights "do not download on the local Tanzania connection", and that is
TRUE OF DOWNLOADING. It is not true of loading: `intfloat/multilingual-e5-base` -- the exact
model the regen uses -- is already in the local HuggingFace cache WITH complete
`model.safetensors`. With `HF_HUB_OFFLINE=1` it loads without touching the network, so the
displacement check below is possible locally and does not have to wait for Kaggle.

(R30, applied to our own tooling: "the weights don't download" was recorded as a property of the
connection and became a reason not to verify locally. The weights are already here. Checked, not
assumed -- the sibling `e5-base-v2` cache IS incomplete, which is probably where the belief came
from, and it is not the model in use.)

WHAT THIS PACKAGE SHIPS, and the two items have different risk shapes:

  1. the Part XII citation reversal -- rows 101 and 171. A CORRECTNESS fix. Low retrieval risk:
     the text changes by a few characters and the row already reaches its question.
  2. `rent_wht_rate` -- a BRAND NEW row. This is the risky one, and the risk is DISPLACEMENT,
     not correctness.

⚠️ THE DISPLACEMENT PRECEDENT IS IN THIS REPO AND IT IS THE REASON THIS FILE EXISTS.
`precompute_rag_embeddings.py` holds TWO VAT-withholding entries deliberately HELD BACK because
a withholding-flavoured Swahili rewrite pulled `nat_27` -- a correct STANDARD-rate row -- out of
its own top-3. Three phrasings were tried and all three displaced it. `rent_wht_rate`'s new text
is withholding-flavoured ("kodi ya zuio", "mkate", "asilimia 10"), so it sits in exactly that
neighbourhood. A new row that answers its own question while costing a currently-correct row is
a net loss, and the only way to know is to measure.

WHAT IS CHECKED, all four against the FULL prospective index rather than a sample:
  A. every committed critical-query anchor still resolves to exactly ONE fact
  B. the two NEW guards reach their target row in top-3, on VERBATIM committed questions
  C. NO existing critical-query guard regresses out of top-3  <- the displacement check
  D. the new row self-retrieves

Queries use verbatim text from committed fixtures, never paraphrases -- the measured reason is
in regenerate_rag_e5.py: for nat_36 a paraphrased guard phrasing put its fact at rank 2 and the
verbatim eval text at rank 17.
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
OUT = os.path.join(REPO, "eval", "results", "dryrun_regen_2026_10_05.json")


def _load_precompute():
    path = os.path.join(REPO, "scripts", "precompute_rag_embeddings.py")
    spec = importlib.util.spec_from_file_location("precompute_rag_embeddings", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["precompute_rag_embeddings"] = mod
    spec.loader.exec_module(mod)
    return mod


# The two NEW guards this package adds, with the fixture each question comes from.
NEW_GUARDS = [
    {"name": "Part XII foreign-company citation (ext_15 verbatim)",
     "query": "query: Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. "
              "Adhabu ni tofauti na kampuni za huku?",
     "anchor": "Part XII, ss.437-447",
     "from": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_15",
     "why_this_anchor": "it IS the citation under guard, not a proxy for it. Verified unique "
                        "to one fact: 'ss.437-447' alone matches TWO rows (101 and 171) and "
                        "would let the guard pass on the wrong one."},
    {"name": "rent WHT 10% both parties (ext_44 verbatim)",
     "query": "query: Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi "
              "kabla ya kumpa fedha?",
     "anchor": "hakuna tofauti ya ukaazi kwenye pango",
     "from": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_44",
     "why_this_anchor": "the no-residency-split clause is the DEFECT the locked fact exists to "
                        "prevent, and it is unique to the new row. A bare 'asilimia 10' anchor "
                        "would match several facts."},
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
    assert "rent_wht_rate" in keys, (
        "rent_wht_rate is not in the built index at all. It is one of the three facts this "
        "package exists to ship, so a dry run that cannot find it is measuring the wrong thing.")
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
    import re as _re
    committed = _re.findall(
        r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", src)
    assert committed, "parsed zero committed critical queries -- the regex no longer matches"
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
    for name, query, anchors in committed:
        want = [a.strip().strip("'\"") for a in anchors.split("','")] if anchors else []
        want = [a.strip().strip("'\"") for a in want if a.strip()]
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

    # --- D. the new row self-retrieves ------------------------------------------------------
    rent_idx = next(i for i, k in enumerate(keys) if k == "rent_wht_rate")
    self_t3 = top(f"query: {texts[rent_idx]}")
    self_ok = rent_idx in [i for i, _ in self_t3]

    out = {
        "_what": "Local offline dry-run of the 2026-10-05 R15 regen package, before Kaggle.",
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
        "anchor_uniqueness": anchor_rows,
        "new_guards": new_results,
        "displacement_regressions_caused_by_this_package": regressions,
        "pre_existing_failures_not_caused_by_this_package": preexisting,
        "new_row_self_retrieves": bool(self_ok),
        "verdict": ("SAFE TO RUN" if not regressions and all(r["in_top3"] for r in new_results)
                    and self_ok else "DO NOT RUN -- see regressions / failed guards"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"\nrows {len(deployed)} -> {len(texts)}  (rag_fact_count must follow, WITH the "
          f"artifacts)")
    print(f"new row self-retrieves: {self_ok}")
    print(f"displacement regressions CAUSED BY THIS PACKAGE: {len(regressions)}")
    print(f"pre-existing failures (fail on the deployed index too): {len(preexisting)}")
    print(f"\nVERDICT: {out['verdict']}")
    print(f"wrote {OUT}")
    return 0 if out["verdict"].startswith("SAFE") else 1


if __name__ == "__main__":
    sys.exit(main())
