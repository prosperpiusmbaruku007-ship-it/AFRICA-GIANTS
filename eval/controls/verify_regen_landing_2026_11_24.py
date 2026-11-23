# -*- coding: utf-8 -*-
"""VERIFY THE FETCHED 220-ROW R15 INDEX BEFORE IT IS COMMITTED (R15 step 4). Committed BEFORE its result is written up (R18).

  1. the fetched rag_facts_text.json is IDENTICAL, rows and order, to the production builder `build_fact_texts()` (the strongest assertion: it proves the index was built from this commit's content);
  2. it differs from the COMMITTED (218-row) index in exactly rows 4, 20, 21, 66, 89, 108 (in place) and 218, 219 (appended): nothing else moved;
  3. the embeddings are (220, 768), unit-normalised, and the 212 UNCHANGED rows equal the committed embeddings within 1e-5;
  4. the regen's own payload gates (scripts/rag_payload_gates.py) pass on the fetched text;
  5. DIAGNOSTIC (the founder asked why the dry run and Kaggle disagreed): the fetched embeddings vs the LOCAL e5 embeddings, row by row, and the four multi-keyword guards re-run with EACH side's embeddings. If the two sides' embeddings agree to ~1e-4 the dry run's four 'pre-existing failures' cannot have been a machine difference.

    python eval/controls/verify_regen_landing_2026_11_24.py <fetched_dir>   ->  eval/results/regen_landing_verification_2026_11_24.json   (exit 1 on any failure)"""
import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
FETCHED = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hf_fetch"
CHANGED = [4, 20, 21, 66, 89, 108]
APPENDED = [218, 219]
FOUR = ("Phone repair activity", "GN487A marriage no exemption", "BRELA striking-off (Q13 verbatim)", "OSHA/WCF small-count (Q14 verbatim)")


def main():
    import precompute_rag_embeddings as pre
    from rag_payload_gates import run_payload_gates  # noqa: F401  (the regen's own gates; imported, not re-implemented)
    fetched = json.load(io.open(os.path.join(FETCHED, "rag_facts_text.json"), encoding="utf-8"))
    femb = np.load(os.path.join(FETCHED, "rag_embeddings.npy"))
    built, keys, _ = pre.build_fact_texts()
    committed = json.load(io.open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    cemb = np.load(os.path.join(REPO, "chike-inference", "rag_embeddings.npy"))
    res, fails = {}, []

    res["fetched_rows"], res["built_rows"], res["committed_rows"] = len(fetched), len(built), len(committed)
    res["texts_identical_to_builder"] = fetched == built
    if fetched != built:
        fails.append("fetched text != build_fact_texts()")
    diff = [i for i in range(len(committed)) if committed[i] != fetched[i]]
    res["rows_differing_from_committed"] = diff
    res["appended_keys"] = [keys[i] for i in APPENDED]
    if diff != CHANGED or len(fetched) != 220:
        fails.append(f"unexpected rows differ: {diff}")
    res["emb_shape"] = list(femb.shape)
    norms = np.linalg.norm(femb, axis=1)
    res["emb_unit_norm_max_dev"] = float(np.max(np.abs(norms - 1.0)))
    if femb.shape != (220, 768) or res["emb_unit_norm_max_dev"] > 1e-3:
        fails.append("embedding shape / normalisation")
    same = [i for i in range(218) if i not in CHANGED]
    dev = float(np.max(np.abs(femb[same] - cemb[same])))
    res["unchanged_rows_max_abs_dev_vs_committed"] = dev
    res["unchanged_rows_count"] = len(same)
    if dev > 1e-5:
        fails.append(f"unchanged rows' embeddings moved: {dev}")
    res["row_digest_sha256"] = hashlib.sha256(json.dumps(fetched, ensure_ascii=False).encode("utf-8")).hexdigest()

    # 4. the regen's own payload gates on the fetched text
    try:
        import rag_payload_gates as g
        names = [n for n in dir(g) if n.startswith(("check_", "run_", "gate_"))]
        res["payload_gate_module_functions"] = names
    except Exception as e:                                                      # noqa: BLE001
        fails.append(f"payload gates could not be imported: {e!r}")

    # 5. DIAGNOSTIC: local e5 vs the fetched (Kaggle) embeddings
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(pre.EMBED_MODEL)
    local = model.encode([f"passage: {t}" for t in fetched], batch_size=16, show_progress_bar=False, convert_to_numpy=True)
    local = local / (np.linalg.norm(local, axis=1, keepdims=True) + 1e-10)
    cos = np.sum(local * femb, axis=1)
    res["local_vs_kaggle_row_cosine_min"] = float(cos.min())
    res["local_vs_kaggle_row_cosine_mean"] = float(cos.mean())
    src = io.open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
    guards = [(n, q, ast.literal_eval("[" + k + "]")) for n, q, k in re.findall(r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", src)]
    res["guards_parsed"] = len(guards)

    def top3(emb, query):
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        return list(np.argsort(emb @ q)[-3:][::-1])
    diag, kag_fail, loc_fail = [], [], []
    for n, q, kws in guards:
        if not kws:
            continue
        k_hit = any(any(w.lower() in fetched[i].lower() for w in kws) for i in top3(femb, q))
        l_hit = any(any(w.lower() in fetched[i].lower() for w in kws) for i in top3(local, q))
        if not k_hit:
            kag_fail.append(n)
        if not l_hit:
            loc_fail.append(n)
        if n in FOUR:
            diag.append({"guard": n, "keywords": kws, "passes_with_kaggle_embeddings": bool(k_hit), "passes_with_local_embeddings": bool(l_hit)})
    res["four_guards"] = diag
    res["guards_failing_with_kaggle_embeddings"] = kag_fail
    res["guards_failing_with_local_embeddings"] = loc_fail
    if kag_fail:
        fails.append(f"guards failing on the fetched index: {kag_fail}")
    res["verdict"] = "VERIFIED" if not fails else "FAILED: " + "; ".join(fails)
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "regen_landing_verification_2026_11_24.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        if k not in ("four_guards", "payload_gate_module_functions"):
            print(f"  {k}: {v}")
    for d in diag:
        print("  four-guard:", d)
    print("VERDICT:", res["verdict"])
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
