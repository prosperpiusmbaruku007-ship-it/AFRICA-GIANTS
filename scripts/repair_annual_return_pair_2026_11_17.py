# -*- coding: utf-8 -*-
"""REPAIR THE TRAINING PAIR THAT TEACHES THE WRONG ANNUAL-RETURN DEADLINE (founder-approved 2026-11-17, item 3). Authored `sft_shaped_pairs/cleaned_pairs_batch_011.jsonl` AND the export `sft/train_sft.jsonl`, identical text.

The pair (Q "Annual return ya BRELA inapaswa kuwasilishwa kabla ya tarehe gani kila mwaka?") opens correctly -- no 30 September, the date is the ANNIVERSARY, "si lazima mwaka wa kifedha" -- and then CONTRADICTS itself:
"Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako." (R37: read in full.) That sentence is removed and the rule the Act states (Companies Act Cap.212 R.E.2023, edition asserted: each return is made up to
the anniversary of incorporation; 28 days from that return date) takes its place. R44: the Act is named, no section number. Identified by CONTENT, never by line number (R36); idempotent; a no-op re-run never overwrites the record.

    python scripts/repair_annual_return_pair_2026_11_17.py [--dry-run]  ->  eval/results/annual_return_pair_repair_2026_11_17.json
"""
import glob
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "eval", "results", "annual_return_pair_repair_2026_11_17.json")
STAGES = ("datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl")
QUESTION = "Annual return ya BRELA inapaswa kuwasilishwa kabla ya tarehe gani kila mwaka?"
OLD_SENTENCE = "Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako."
NEW_SENTENCE = "Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo ya return, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni)."


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def main():
    dry = "--dry-run" in sys.argv
    edited = []
    for pat in STAGES:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            raw = io.open(path, encoding="utf-8", newline="").read()
            out, touched = [], False
            for n, ln in enumerate(raw.splitlines(keepends=True), 1):
                body = ln.rstrip("\r\n")
                eol = ln[len(body):]
                try:
                    r = json.loads(body) if body.strip() else None
                except ValueError:
                    r = None
                if r and r.get("instruction") == QUESTION and OLD_SENTENCE in (r.get("output") or ""):
                    new = r["output"].replace(OLD_SENTENCE, NEW_SENTENCE)
                    assert new != r["output"] and "miezi 12" not in new
                    r2 = dict(r)
                    r2["output"] = new
                    out.append(json.dumps(r2, ensure_ascii=False) + eol)
                    edited.append({"file": os.path.relpath(path, REPO).replace(os.sep, "/"), "line": n, "old_sha256": sha(r["output"]), "new_sha256": sha(new), "old": r["output"], "new": new})
                    touched = True
                else:
                    out.append(ln)
            if touched and not dry:
                io.open(path, "w", encoding="utf-8", newline="").write("".join(out))
    assert len(edited) in (0, 2), len(edited)          # the authored pair and its export copy
    if edited and not dry:
        io.open(OUT, "w", encoding="utf-8").write(json.dumps({"date": "2026-11-17", "edited": edited}, ensure_ascii=False, indent=1))
    print({"dry_run": dry, "edited": len(edited)})


if __name__ == "__main__":
    main()
