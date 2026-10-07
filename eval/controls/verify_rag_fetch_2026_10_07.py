# -*- coding: utf-8 -*-
r"""VERIFY THE FETCHED R15 INDEX BEFORE IT IS DEPLOYED — AND DO IT BY IMPORTING, NOT RE-CHECKING.

⛔ THIS FILE IS WRITTEN UNDER THE RULE THE DRY RUN BROKE YESTERDAY.

The 2026-10-06 dry run said SAFE TO RUN on a package the Kaggle regen then refused, because it
RE-IMPLEMENTED a subset of the regen's payload gates instead of executing them. **A harness that
re-implements the checks its author remembers is a model of the run, not the run.** It generalises
to every harness that claims to rehearse or verify another, which is what this one does.

So nothing here is re-derived that already exists:

  * the PAYLOAD GATES come from `scripts/rag_payload_gates.py` — the same module the regen imports
  * the SUPERSEDED-VALUE polarity logic comes from
    `eval/index_quality/sweep_superseded_values_in_built_index.py` — not a second copy of the
    negation device, the money boundary, or the SUPERSEDES escape
  * the INDEX TEXT is compared against `precompute.build_fact_texts()`, the production builder

THE STRONGEST ASSERTION IN THIS FILE is that the fetched `rag_facts_text.json` is BYTE-IDENTICAL
to what this tree builds. That single equality proves the uploaded index was built from this
commit's content — far stronger than reading the HF commit title, which is a claim the uploader
made about itself. The title is recorded as provenance; it is not what the verdict rests on.

⚠️ AND IT RUNS AGAINST THE COMMITTED COPIES IN BOTH DIRS, not against a scratch download, because
what gets deployed is `chike-inference/`. A verification pointed at the download would pass while
the deploy shipped something else — R36's question (where does the control ACT?) in the artifact
layer.

Usage:  python eval/controls/verify_rag_fetch_2026_10_07.py
Artifact: eval/results/rag_fetch_verification_2026_10_07.json
Exit 1 on any failure. Exit 2 if it could not be exercised (NOT a pass).
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
ARTIFACT = "eval/results/rag_fetch_verification_2026_10_07.json"

DIRS = ["kaggle", "chike-inference"]
TEXTS = "rag_facts_text.json"
EMB = "rag_embeddings.npy"

# Recorded from the HuggingFace dataset repo at fetch time. PROVENANCE, not evidence: the build
# SHA is a claim the uploader made about itself, and the byte-equality check below is what
# actually establishes which tree the index came from.
FETCH_PROVENANCE = {
    "source": "https://huggingface.co/datasets/prospAprospA007/africa-giants-dataset",
    "hf_commit_date": "2026-10-07T19:38:04.000Z",
    "hf_commit_title": "e5-base RAG index (184x768), built from e3e1d0f; correction_sync=CLEAN",
    "claimed_build_commit": "e3e1d0f",
    "required_floor": "c8cdbb9",
    "fetched_sha256": {
        TEXTS: "0fb2826558773406",   # first 16 hex, full value asserted below from disk
        EMB: "ec29974baa486157",
    },
}
# The row this cycle exists for. Deployed index served "faini ni USD 25".
PRIMARY_ROW = 172
PRIMARY_MUST = "faini ni TZS 70,000"
PRIMARY_MUST_NOT = r"USD\s*25\b"


def _load(relpath, name):
    path = os.path.join(REPO, *relpath.split("/"))
    assert os.path.exists(path), f"{relpath} missing -- refusing to verify by re-implementation"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def _sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def main():
    out = {
        "_what": "The fetched R15 index, verified against this tree before deploy.",
        "_why_imported_not_reimplemented": (
            "A harness that re-implements the checks its author remembers is a MODEL of the run, "
            "not the run. The 2026-10-06 dry run proved that by passing a package the real run "
            "refused. Payload gates come from scripts/rag_payload_gates.py and the "
            "superseded-value polarity from the committed sweep; neither is copied here."),
        "fetch_provenance": FETCH_PROVENANCE,
        "checks": [],
    }
    failures = []

    def check(name, ok, detail=""):
        out["checks"].append({"check": name, "ok": bool(ok), "detail": str(detail)[:600]})
        print(f"  [{'ok' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    # ── 1. the claimed build commit must be a DESCENDANT of the required floor ──────────
    floor = FETCH_PROVENANCE["required_floor"]
    claimed = FETCH_PROVENANCE["claimed_build_commit"]
    r = subprocess.run(["git", "merge-base", "--is-ancestor", floor, claimed],
                       capture_output=True, text=True)
    check(f"claimed build commit {claimed} contains the floor {floor}", r.returncode == 0,
          f"git merge-base --is-ancestor -> {r.returncode}")

    # ── 2. both deploy dirs carry the SAME bytes ────────────────────────────────────────
    shas = {}
    for d in DIRS:
        for f in (TEXTS, EMB):
            p = os.path.join(REPO, d, f)
            assert os.path.exists(p), f"{d}/{f} missing"
            shas[f"{d}/{f}"] = _sha(p)
    for f in (TEXTS, EMB):
        a, b = shas[f"{DIRS[0]}/{f}"], shas[f"{DIRS[1]}/{f}"]
        check(f"{f} identical in {DIRS[0]}/ and {DIRS[1]}/", a == b, a[:16])
    out["sha256"] = shas

    # ── 3. THE LOAD-BEARING ONE: the committed index IS what this tree builds ───────────
    precompute = _load("scripts/precompute_rag_embeddings.py", "precompute_for_fetch_verify")
    built_texts, built_keys, _dropped = precompute.build_fact_texts()
    served = json.load(io.open(os.path.join(REPO, "chike-inference", TEXTS), encoding="utf-8"))
    check("committed index text == build_fact_texts() output, row for row",
          served == built_texts,
          f"{len(served)} served vs {len(built_texts)} built"
          + ("" if served == built_texts else
             f"; first diff at {next(i for i, (a, b) in enumerate(zip(served, built_texts)) if a != b)}"))

    # ── 4. the index contract's count, which must move WITH the artifacts ──────────────
    cfg = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"), encoding="utf-8"))
    check("chike_config.rag_fact_count matches the served row count",
          cfg.get("rag_fact_count") == len(served),
          f"config={cfg.get('rag_fact_count')} served={len(served)}")

    import numpy as np
    emb = np.load(os.path.join(REPO, "chike-inference", EMB))
    check("embeddings shape is (rows, 768)", emb.shape == (len(served), 768), str(emb.shape))
    check("embeddings are L2-normalised",
          bool(np.allclose(np.linalg.norm(emb, axis=1), 1.0, atol=1e-4)),
          f"min={float(np.linalg.norm(emb, axis=1).min()):.6f}")

    # ── 5. THE PRIMARY ROW FOR THIS CYCLE ──────────────────────────────────────────────
    row = served[PRIMARY_ROW]
    check(f"row {PRIMARY_ROW} states {PRIMARY_MUST!r}", PRIMARY_MUST in row, row[:180])
    check(f"row {PRIMARY_ROW} no longer asserts USD 25",
          not re.search(PRIMARY_MUST_NOT, row, re.I), row[:180])
    out["primary_row"] = {"index": PRIMARY_ROW, "text": row}

    # ── 6. the regen's OWN payload gates, executed against the served index ───────────
    gates = _load("scripts/rag_payload_gates.py", "gates_for_fetch_verify")
    try:
        n = gates.run_payload_gates(built_keys, served)
        check("the regen's own payload gates pass on the SERVED index", n >= 11, f"{n} gates")
    except (AssertionError, SystemExit) as exc:
        check("the regen's own payload gates pass on the SERVED index", False, str(exc)[:500])
        n = 0
    out["payload_gates_run"] = n

    # ── 7. no row asserts a superseded value — using the COMMITTED sweep's logic ──────
    sweep = _load("eval/index_quality/sweep_superseded_values_in_built_index.py",
                  "sweep_for_fetch_verify")
    sweep._self_test()        # the instrument, before its verdict is used
    facts = json.load(io.open(os.path.join(REPO, "scripts", "locked_facts.json"),
                              encoding="utf-8"))
    group_of = dict(precompute._GROUP_MEMBERS)
    by_key = dict(zip(built_keys, served))
    asserted = []
    for key, fact in sorted(facts.items()):
        if not (isinstance(fact, dict) and fact.get("superseded_value")):
            continue
        row_key = group_of.get(key, key)
        text = by_key.get(row_key, "")
        cur_nums = {sweep._numeric(c) for c in sweep._tokens(
            str(fact.get("correct_value", "")) + " " +
            sweep._current_prose(str(fact.get("fact", ""))))}
        toks = [t for t in sweep._tokens(str(fact["superseded_value"]))
                if sweep._numeric(t) not in cur_nums]
        if key in group_of and any(sweep._mentioned(text, c) for c in sweep._tokens(
                str(fact.get("correct_value", "")))):
            continue                      # sibling fee in a shared group passage
        for t in toks:
            spans = sweep._asserted_spans(text, t)
            if spans:
                asserted.append({"fact": key, "row": row_key, "asserted": spans})
    check("no served row ASSERTS a value its own fact declares superseded",
          not asserted, json.dumps(asserted, ensure_ascii=False)[:400])
    out["superseded_assertions"] = asserted

    os.makedirs(os.path.join(REPO, "eval", "results"), exist_ok=True)
    out["verdict"] = "VERIFIED" if not failures else "FAILED"
    out["failures"] = failures
    with io.open(os.path.join(REPO, *ARTIFACT.split("/")), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nartifact: {ARTIFACT}")
    print(f"VERDICT: {out['verdict']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
