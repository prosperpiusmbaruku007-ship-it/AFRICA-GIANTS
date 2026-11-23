# -*- coding: utf-8 -*-
"""R36 REACH ASSERTION for corpus_repairs_2026_11_24.py: the OLD answers of every repaired or quarantined row must be GONE from the training export AND from every authored stage, and the two guards (D-FIDELITY-29/30) are re-run over the export.
Old answers are read from the two records the repair script wrote (datasets/tier1a/rejected/p9_nssf7_sdl_exemption_quarantine_2026_11_24.jsonl and eval/results/corpus_rewrites_2026_11_24.jsonl); the 'present' count is also asserted non-zero for the NEW texts, so a harness that finds nothing cannot pass (R20).
    python eval/controls/assert_export_reach_2026_11_24.py   (exit 1 on any survivor)"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from chike import fidelity  # noqa: E402

REJ = os.path.join(REPO, "datasets", "tier1a", "rejected")


def jl(path):
    return [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]


def main():
    q = jl(os.path.join(REJ, "p9_nssf7_sdl_exemption_quarantine_2026_11_24.jsonl"))
    r = jl(os.path.join(REPO, "eval", "results", "corpus_rewrites_2026_11_24.jsonl"))
    old, new = set(), set()
    for x in q:
        row = x["row"]
        old.add((row.get("answer_sw") or row.get("output") or "").strip())
    for x in r:
        for k in ("answer_sw", "output"):
            if k in x["old"]:
                old.add(x["old"][k].strip())
            if k in x["new"]:
                new.add(x["new"][k].strip())
    assert len(old) >= 20 and len(new) >= 10, (len(old), len(new))                      # a loader returning nothing must fail, not pass (R20)
    stages = glob.glob(os.path.join(REPO, "datasets/tier1a/cleaned_pairs/*.jsonl")) + glob.glob(os.path.join(REPO, "datasets/tier1a/sft_shaped_pairs/*.jsonl")) \
        + glob.glob(os.path.join(REPO, "datasets/tier1a/raw_sources/*.jsonl")) + glob.glob(os.path.join(REPO, "datasets/tier1a/sft/*.jsonl"))
    survivors, new_present, export_rows = [], 0, 0
    for f in stages:
        for i, line in enumerate(io.open(f, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            a = (row.get("answer_sw") or row.get("output") or "").strip()
            if a in old:
                survivors.append(os.path.relpath(f, REPO) + ":" + str(i))
            if a in new:
                new_present += 1
            if f.endswith("train_sft.jsonl"):
                export_rows += 1
    exp = jl(os.path.join(REPO, "datasets", "tier1a", "sft", "train_sft.jsonl"))
    p9 = [i for i, x in enumerate(exp) if fidelity.p9_asserted(x["output"])]
    n7 = [i for i, x in enumerate(exp) if fidelity.nssf_deadline_misstated(x["instruction"], x["output"])]
    print(f"old answers {len(old)}; NEW texts present {new_present}x; survivors of an OLD answer: {len(survivors)}; export rows {export_rows}")
    print(f"export rows still flagged: D-FIDELITY-30 (P9) {len(p9)}, D-FIDELITY-29 (NSSF 7th) {len(n7)}")
    for s in survivors:
        print("  SURVIVOR", s)
    for i in p9 + n7:
        print("  STILL FLAGGED export row", i, exp[i]["instruction"][:80])
    assert new_present >= 10, "the new texts were not found anywhere: the harness cannot see its own work"
    return 1 if survivors or p9 or n7 else 0


if __name__ == "__main__":
    sys.exit(main())
