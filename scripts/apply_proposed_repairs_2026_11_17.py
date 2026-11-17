# -*- coding: utf-8 -*-
"""APPLY THE FOUNDER-APPROVED PROPOSALS (2026-11-17: "All proposals in tail_conflation_proposals_2026_11_17.json ... Ship the gold-key and reply/training repairs TOGETHER ... in-place identical edits, quarantine records,
reach test"; plus "correct [the 175,000 low-end wording] in all rows and in CLAUDE.md s11, from the Order itself").

Reads eval/results/tail_conflation_proposals_2026_11_17.json (the approved artifact: OLD and NEW text per row, action repair | quarantine) and applies it IN PLACE, identically, to:
  * datasets/tier1a/cleaned_pairs/*.jsonl     (schema-valid corpus: answer_sw AND answer_en)
  * datasets/tier1a/sft_shaped_pairs/*.jsonl  (authored SFT-shaped: output)
  * datasets/tier1a/sft/*.jsonl               (the EXPORT that trains: output)
  * eval/accuracy_gate/eval_questions_001.jsonl  (gold keys eval_116 / 117 / 119 / 120 / 126: correct_answer_sw AND _en; the old key is kept in `_scoring_key_correction`, chained to any earlier one)
  * eval/accuracy_gate/edge_probe_natural_048.jsonl  (nat_42's `expected_behavior`; the old text kept in `_correction`)
Rows are identified by the sha256 prefix of the OLD answer, NEVER by line number (R36: a number in a generated file is not an identity). A quarantined row is REMOVED from every stage and preserved whole in
datasets/tier1a/rejected/gn605a_mining_400k_pair_quarantine_2026_11_17.jsonl; raw_sources/ copies are not touched (pre-cleaning provenance). Idempotent; a no-op re-run NEVER overwrites the record of the real run
(the 2026-11-17 lesson). The Hugging Face copy is not touched (a separate approval).

    python scripts/apply_proposed_repairs_2026_11_17.py [--dry-run]   ->  eval/results/applied_proposed_repairs_2026_11_17.json
"""
import glob
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPOSALS = os.path.join(REPO, "eval", "results", "tail_conflation_proposals_2026_11_17.json")
OUT = os.path.join(REPO, "eval", "results", "applied_proposed_repairs_2026_11_17.json")
QUAR = os.path.join(REPO, "datasets", "tier1a", "rejected", "gn605a_mining_400k_pair_quarantine_2026_11_17.jsonl")
STAGES = ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl")
GOLD_FILE = "eval/accuracy_gate/eval_questions_001.jsonl"
NAT_FILE = "eval/accuracy_gate/edge_probe_natural_048.jsonl"
BATCH = "approved-proposals-2026-11-17"
BASIS = ("D-FIDELITY-18 (a practitioner firm is not the authority a user confirms with) + GN 605A (kazi.go.tz official copy, edition asserted, read 2026-11-17): energy / international companies monthly 765,900, mining and "
         "prospecting minerals 695,000, the LOWEST monthly rate 80,000 (Domestic Work 4(d) other domestic workers), 175,000 = Agriculture 1(a) and item 16 'any other sector not specified' (all 50 rate blocks parsed).")


def sha(t):
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()[:16]


def _eol(ln):
    body = ln.rstrip("\r\n")
    return body, ln[len(body):]


def main():
    dry = "--dry-run" in sys.argv
    prop = json.load(io.open(PROPOSALS, encoding="utf-8"))
    by_sha = {}
    for r in prop["rows"]:
        # the SAME Swahili answer sits in several stages and only the schema-valid corpus carries an English twin: a row WITH a new_en must never be overwritten by one without (found when the first apply left answer_en unrepaired)
        if r["old_sha256"] not in by_sha or (by_sha[r["old_sha256"]].get("new_en") is None and r.get("new_en") is not None):
            by_sha[r["old_sha256"]] = r
    result = {"date": "2026-11-17", "dry_run": dry, "edited": [], "quarantined": [], "gold": [], "nat_42": None}
    quarantine_rows = []
    for pat in STAGES:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            raw = io.open(path, encoding="utf-8", newline="").read()
            out, touched = [], False
            rel = os.path.relpath(path, REPO).replace(os.sep, "/")
            for n, ln in enumerate(raw.splitlines(keepends=True), 1):
                body, eol = _eol(ln)
                try:
                    r = json.loads(body) if body.strip() else None
                except ValueError:
                    r = None
                fld = None if r is None else ("answer_sw" if "answer_sw" in r else "output" if "output" in r else None)
                prow = by_sha.get(sha(r.get(fld))) if fld else None
                if not prow:
                    out.append(ln)
                    continue
                touched = True
                if prow["action"] == "quarantine":
                    quarantine_rows.append({"source_file": rel, "source_line_at_quarantine": n, "row": r})
                    result["quarantined"].append({"file": rel, "line": n, "question": prow["question"][:120]})
                    continue
                r2 = dict(r)
                r2[fld] = prow["new_sw"]
                if "answer_en" in r2 and prow.get("new_en") is not None:
                    r2["answer_en"] = prow["new_en"]
                out.append(json.dumps(r2, ensure_ascii=False) + eol)
                result["edited"].append({"file": rel, "line": n, "old_sha256": prow["old_sha256"], "reason": prow["reason"], "new_sha256": sha(prow["new_sw"]), "old": r[fld], "new": prow["new_sw"]})
            if touched and not dry:
                io.open(path, "w", encoding="utf-8", newline="").write("".join(out))
    # ---- gold keys -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    gold = {g["id"]: g for g in prop["gold"]}
    raw = io.open(os.path.join(REPO, GOLD_FILE), encoding="utf-8", newline="").read()
    out = []
    for ln in raw.splitlines(keepends=True):
        body, eol = _eol(ln)
        try:
            r = json.loads(body) if body.strip() else None
        except ValueError:
            r = None
        if r and r.get("id") in gold:
            g = gold[r["id"]]
            corr = r.get("_scoring_key_correction")
            if isinstance(corr, dict) and corr.get("batch") == BATCH:
                out.append(ln)
                result["gold"].append({"id": r["id"], "status": "already applied"})
                continue
            assert r["correct_answer_sw"] == g["old_sw"] and r["correct_answer_en"] == g["old_en"], (r["id"], "the live key is not the one the proposal was built on")
            new = dict(r)
            new["correct_answer_sw"], new["correct_answer_en"] = g["new_sw"], g["new_en"]
            entry = {"date": "2026-11-17", "batch": BATCH, "what_changed": "founder-approved: authority tail (no practitioner firm) and/or the Order's range", "basis": BASIS,
                     "old": {"correct_answer_sw": g["old_sw"], "correct_answer_en": g["old_en"]}}
            if corr:
                entry["earlier_correction"] = corr
            new["_scoring_key_correction"] = entry
            out.append(json.dumps(new, ensure_ascii=False) + eol)
            result["gold"].append({"id": r["id"], "status": "applied", "old": g["old_sw"], "new": g["new_sw"]})
        else:
            out.append(ln)
    if not dry:
        io.open(os.path.join(REPO, GOLD_FILE), "w", encoding="utf-8", newline="").write("".join(out))
    n42 = prop["nat_42"]
    raw = io.open(os.path.join(REPO, NAT_FILE), encoding="utf-8", newline="").read()
    out = []
    for ln in raw.splitlines(keepends=True):
        body, eol = _eol(ln)
        try:
            r = json.loads(body) if body.strip() else None
        except ValueError:
            r = None
        if r and r.get("id") == "nat_42":
            if isinstance(r.get("_correction"), dict) and r["_correction"].get("batch") == BATCH:
                out.append(ln)
                result["nat_42"] = "already applied"
                continue
            assert r["expected_behavior"] == n42["old"], "nat_42 is not the text the proposal was built on"
            r2 = dict(r)
            r2["expected_behavior"] = n42["new"]
            r2["_correction"] = {"date": "2026-11-17", "batch": BATCH, "basis": BASIS, "old_expected_behavior": n42["old"]}
            out.append(json.dumps(r2, ensure_ascii=False) + eol)
            result["nat_42"] = "applied"
        else:
            out.append(ln)
    if not dry:
        io.open(os.path.join(REPO, NAT_FILE), "w", encoding="utf-8", newline="").write("".join(out))
    n_edit, n_q = len(result["edited"]), len(result["quarantined"])
    expect_edit = sum(1 for r in prop["rows"] if r["action"] == "repair")
    expect_q = sum(1 for r in prop["rows"] if r["action"] == "quarantine")
    assert (n_edit, n_q) in ((expect_edit, expect_q), (0, 0)), f"edited/quarantined ({n_edit}, {n_q}) != proposals ({expect_edit}, {expect_q})"
    if n_q and not dry:
        with io.open(QUAR, "a", encoding="utf-8") as f:
            for q in quarantine_rows:
                f.write(json.dumps({"defect": "MINING_PREMISE_DENIAL_ANSWERED_WITH_THE_ENERGY_RATE",
                                    "reason": next(r["reason"] for r in prop["rows"] if r["action"] == "quarantine"),
                                    "correct_value": "GN 605A: energy sector, international companies 765,900/month; mining and prospecting minerals 695,000/month; the mining sector has further sub-sector rates (primary mining licence, dealer and broker licences)",
                                    "raw_sources_copies_not_touched": "datasets/tier1a/raw_sources/ (pre-cleaning provenance)", **q}, ensure_ascii=False) + "\n")
    if not dry and (n_edit or n_q or any(g.get("status") == "applied" for g in result["gold"])):
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, indent=1))
    print({"dry_run": dry, "edited": n_edit, "quarantined": n_q, "gold": [(g["id"], g["status"]) for g in result["gold"]], "nat_42": result["nat_42"]})


if __name__ == "__main__":
    main()
