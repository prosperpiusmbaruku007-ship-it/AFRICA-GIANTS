# -*- coding: utf-8 -*-
"""QUARANTINE THE PAIR THAT CALLS 33.4% "TAKWIMU RASMI ILIYOTOLEWA NA PKF EASTERN AFRICA" (founder-approved 2026-11-17: "read it first, R37; mark, don't delete"; every copy including datasets/tier1a/sft/ -- R36).

THE DEFECT. Q "Takwimu rasmi ya ongezeko la wastani ... GN 605A ni asilimia 33.4 -- kwa nini si 33.5?" is answered "Asilimia 33.4 ni takwimu rasmi iliyotolewa na PKF Eastern Africa ... Tumia 33.4% kama takwimu rasmi".
  * GN 605A is the Labour Institutions (Minimum Wage for Private Sector) Order, 2025 (Special Supplement 9, 13 Oct 2025; read in full 2026-11-17, sha256 3a139908). It contains NO average-increase figure and names no consultancy.
    So the figure is not an "official statistic issued by" anyone named in the Order; it rests on press / advisory sources (locked fact gn605a_average_increase, `_source_tier_note`). PKF is an advisory commentator.
  * R37 (read before removing, in the OPPOSITE direction): the NUMBER (33.4, TZS 275,060 -> 358,322) is the locked value and is right; the pair is removed for the ATTRIBUTION ("takwimu rasmi ... iliyotolewa na PKF", repeated as an instruction: "Tumia 33.4% kama takwimu rasmi"), which is the defect the D-FIDELITY GN 605A issuer repair exists for. It does not deny the attribution anywhere. Removed whole;
    a corrected replacement is a separate, authorable job.
  * NOT touched, seen only: the sibling GN 605A pairs end "Thibitisha na PKF Eastern Africa au TanzLII / MLYWF" (a consultancy and a host with no DNS as authorities) -- outside the approved list.
SCOPE (R36): REMOVED from sft_shaped_pairs/cleaned_pairs_batch_010.jsonl:48 and sft/train_sft.jsonl:1494; MARKED, NOT REMOVED: raw_sources/raw_pairs_batch_010.jsonl:50 and raw_sources/batch_010_checkpoints/checkpoint_002.jsonl:20 (pre-cleaning input, feed no training).

    python scripts/quarantine_pkf_issuer_pair_2026_11_17.py [--dry-run]
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "pkf_issuer_pair_quarantine_2026_11_17.jsonl")
OUT = os.path.join(REPO, "eval", "results", "pkf_issuer_pair_quarantine_2026_11_17.json")
DEFECT = "GN605A_AVERAGE_ATTRIBUTED_TO_PKF_AS_OFFICIAL_ISSUER"
CORRECT = ("GN 605A is the Labour Institutions (Minimum Wage for Private Sector) Order, 2025; it contains no average-increase figure and names no consultancy (locked facts gn605a_issuer, gn605a_average_increase). The 33.4% rests on press/advisory sources.")
T = "datasets/tier1a/"
HEAD = "Takwimu rasmi ya ongezeko la wastani la mishahara ya chini chini ya GN 605A"
SENTENCE = "takwimu rasmi iliyotolewa na PKF Eastern Africa"
ROWS = [
    (T + "sft_shaped_pairs/cleaned_pairs_batch_010.jsonl", 48, "remove"),
    (T + "sft/train_sft.jsonl", 1494, "remove"),
    (T + "raw_sources/raw_pairs_batch_010.jsonl", 50, "mark"),
    (T + "raw_sources/batch_010_checkpoints/checkpoint_002.jsonl", 20, "mark"),
]


def _head(o):
    return o.get("instruction") or o.get("question_sw") or ""


def main():
    dry = "--dry-run" in sys.argv
    files = {}
    for f, *_ in ROWS:
        files.setdefault(f, io.open(os.path.join(REPO, f), encoding="utf-8", newline="").read().splitlines())
    already = set()
    if os.path.exists(QUARANTINE):
        for ql in io.open(QUARANTINE, encoding="utf-8"):
            if ql.strip():
                already.add((json.loads(ql)["source_file"], json.loads(ql)["source_line_at_quarantine"]))
    planned = []
    for f, ln, action in ROWS:
        if (f, ln) in already:
            continue
        raw = files[f][ln - 1] if ln <= len(files[f]) else ""
        o = json.loads(raw) if raw.strip() else {}
        if not _head(o).startswith(HEAD) or SENTENCE not in raw:
            print(f"[ABORT] {f}:{ln} no longer holds the adjudicated row (head {_head(o)[:60]!r}). A line number pins a POSITION; re-adjudicate by content.")
            return 1
        planned.append((f, ln, action, hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest(), o))
    print(f"planned {len(planned)} rows ({sum(1 for p in planned if p[2] == 'remove')} remove, {sum(1 for p in planned if p[2] == 'mark')} mark-only); already recorded {len(already)}")
    if dry or not planned:
        return 0
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8", newline="\n") as fh:               # record FIRST
        for f, ln, action, h, o in planned:
            fh.write(json.dumps({"source_file": f, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus" if action == "remove" else "marked_raw_not_removed",
                                 "defect_class": DEFECT, "reason": f"calls the GN 605A average an official statistic issued by PKF Eastern Africa: '...{SENTENCE}...'. {CORRECT}",
                                 "adjudicated": "individually, by reading the full row and the Act text (2026-11-17) -- not matched by pattern", "row_sha256": h, "row": o}, ensure_ascii=False) + "\n")
    removed = {}
    for f, ln, action, *_ in planned:
        if action == "remove":
            removed.setdefault(f, set()).add(ln)
    for f, lns in removed.items():                                                    # THEN the live files
        kept = [l for i, l in enumerate(files[f], 1) if i not in lns]
        with io.open(os.path.join(REPO, f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(kept) + "\n")
    for f in removed:
        lines = io.open(os.path.join(REPO, f), encoding="utf-8").read().splitlines()
        assert not any(HEAD in l and SENTENCE in l for l in lines), f"the asserting row survives in {f}"
    rep = {"measured": "2026-11-17", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in removed.values()), "rows_marked_raw": sum(1 for p in planned if p[2] == "mark"),
           "lines_removed": {k: sorted(v) for k, v in removed.items()}, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
