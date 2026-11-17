# -*- coding: utf-8 -*-
"""REPAIR THE 14 GN 605A TRAINING PAIRS WHOSE ANSWERS NAME A CONSULTANCY AS THE AUTHORITY (founder-approved 2026-11-17: "Edit authored files and the export in place with identical text; quarantine records").

"28" in the first count was 14 DISTINCT PAIRS counted once in the authored files (datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_010.jsonl x11, _013.jsonl x3) and once in the export (sft/train_sft.jsonl x13,
sft/val_sft.jsonl x1). Each was READ in full (R37). Dispositions, keyed by the sha256 prefix of the OLD answer:

  tail only            #1 #5 #6 #8 #10 #11   "Thibitisha na PKF/VELMA/MLYWF ..." -> "Thibitisha na Ofisi ya Kazi (kazi.go.tz) au TanzLII."   (#11 also drops "MLYWF", a host with no DNS)
  tail, TRA kept       #7 #9                 timelines that span VAT dates: "Thibitisha na TRA (tra.go.tz), Ofisi ya Kazi (kazi.go.tz), au TanzLII."
  content + tail       #2 #3                 765,900 is ENERGY / international companies in the Order, not "madini ya kimataifa na nishati" (mining and prospecting minerals is 695,000; GN 605A read 2026-11-17, edition asserted)
  content + tail       #12                   "Agizo la Serikali" -> "Tangazo la Serikali"; "GN 605B haipo" -> "hakuna GN 605B inayojulikana" (no source for the universal negative was found)
  rewritten            #13 #14               the GN 605B universal negative softened to "hakuna GN 605B inayojulikana; thibitisha na Ofisi ya Kazi" (founder's wording)
  QUARANTINED          #4                    tells a mining employer to pay "angalau TZS 765,900"; the Order's mining and prospecting rate is 695,000 (a wrong-direction amount). MARKED in the record, removed from both stages.

NOT edited (seen, listed in the record): the raw_sources/ copies of these pairs (pre-cleaning provenance, as in the 2026-11-17 PKF-issuer quarantine). The Hugging Face copy is NOT touched (a separate approval).
Idempotent: a new text already present is left alone. Identification is by CONTENT hash, never by line number (R36: a number in a generated file is not an identity).

    python scripts/repair_tail_pairs_2026_11_17.py [--dry-run]    ->  eval/results/tail_pair_repairs_2026_11_17.json,  datasets/tier1a/rejected/gn605a_mining_765900_pair_quarantine_2026_11_17.jsonl
"""
import glob
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "gn605a_mining_765900_pair_quarantine_2026_11_17.jsonl")
OUT = os.path.join(REPO, "eval", "results", "tail_pair_repairs_2026_11_17.json")
STAGES = ("datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl")
TAIL_A = "Thibitisha na Ofisi ya Kazi (kazi.go.tz) au TanzLII."
TAIL_B = "Thibitisha na TRA (tra.go.tz), Ofisi ya Kazi (kazi.go.tz), au TanzLII."
CONFIRM = "Thibitisha na "
P2_OLD, P2_NEW = "kwa sekta ya madini ya kimataifa na nishati", "kwa sekta ya nishati (kampuni za kimataifa)"
P3_OLD, P3_NEW = "(sekta ya madini ya kimataifa na nishati)", "(sekta ya nishati, kampuni za kimataifa)"
Q4_DEFECT = "MINING_EMPLOYER_TOLD_TO_PAY_AT_LEAST_765900_ENERGY_RATE"

NEW13 = ("Hapana. Hakuna GN 605B inayojulikana. Amri inayosimamia mishahara ya chini ya sekta binafsi Tanzania ni GN 605A (Government Notice 605A), iliyoanza kutumika tarehe 1 Januari 2026. "
         "Thibitisha na Ofisi ya Kazi (kazi.go.tz).")
NEW14 = ("GN 605A ndiyo amri sahihi na halali inayotumika. Hakuna GN 605B inayojulikana. GN 605A (Government Notice No.605A) iligazetishwa Oktoba 2025 na ilianza kutumika tarehe 1 Januari 2026, "
         "ikighairi Amri ya Mishahara ya 2022 kabisa. Thibitisha na Ofisi ya Kazi (kazi.go.tz).")


def _tail(text, new_tail):
    i = text.rindex(CONFIRM)
    assert text[i:].count(CONFIRM) == 1 and text.rstrip().endswith("."), text[-120:]
    return text[:i] + new_tail


def _sw(t):
    return t


def new_text(kind, old):
    if kind == "A":
        return _tail(old, TAIL_A)
    if kind == "B":
        return _tail(old, TAIL_B)
    if kind == "2":
        assert old.count(P2_OLD) == 1
        return _tail(old.replace(P2_OLD, P2_NEW), TAIL_A)
    if kind == "3":
        assert old.count(P3_OLD) == 1
        return _tail(old.replace(P3_OLD, P3_NEW), TAIL_A)
    if kind == "12":
        assert old.count("Agizo la Serikali") == 1 and old.count("GN 605B haipo -- amri sahihi ni GN 605A.") == 1
        return _tail(old.replace("Agizo la Serikali", "Tangazo la Serikali").replace("GN 605B haipo -- amri sahihi ni GN 605A.", "Hakuna GN 605B inayojulikana; amri sahihi ni GN 605A."), TAIL_A)
    if kind == "13":
        return NEW13
    if kind == "14":
        return NEW14
    raise ValueError(kind)


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def key_of_old(old):
    return sha(old)


# (kind, sha1[:10] of the OLD answer as listed by scratch/list_tail_pairs.py) -- resolved to sha256 prefixes at run time from the corpus so the table stays readable
PAIRS = [("A", "cfb0c64a83"), ("2", "f387215a74"), ("3", "d7bd061e9e"), ("Q", "3f2767d041"), ("A", "79576b22b7"), ("A", "3471f12594"), ("B", "e9983fd0ef"),
         ("A", "ce0b23fdfa"), ("B", "433b0b2e35"), ("A", "facf8e41ea"), ("A", "84f6553130"), ("12", "7337586fa0"), ("13", "079dd288d7"), ("14", "a5a7446ce6")]
BY_H = {h: k for k, h in PAIRS}


def _ans(r):
    if "messages" in r:
        return next((x["content"] for x in reversed(r["messages"]) if x["role"] == "assistant"), "")
    return r.get("output") or r.get("answer_sw") or ""


def main():
    dry = "--dry-run" in sys.argv
    result = {"date": "2026-11-17", "dry_run": dry, "edited": [], "quarantined": [], "already_applied": 0}
    qrows = []
    new_hashes = {}
    for pat in STAGES:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            raw = io.open(path, encoding="utf-8", newline="").read()
            lines = raw.splitlines(keepends=True)
            out, touched = [], False
            for n, ln in enumerate(lines, 1):
                body = ln.rstrip("\r\n")
                eol = ln[len(body):]
                try:
                    r = json.loads(body) if body.strip() else None
                except ValueError:
                    r = None
                if r is None:
                    out.append(ln)
                    continue
                a = _ans(r)
                h = hashlib.sha1(a.encode()).hexdigest()[:10]
                kind = BY_H.get(h)
                if kind is None:
                    out.append(ln)
                    continue
                rel = os.path.relpath(path, REPO).replace(os.sep, "/")
                touched = True
                if kind == "Q":
                    qrows.append({"source_file": rel, "source_line_at_quarantine": n, "row": r})
                    result["quarantined"].append({"file": rel, "line": n, "question": (r.get("instruction") or "")[:140]})
                    continue                                              # removed from the stage; the record below keeps the full row
                na = new_text(kind, a)
                r2 = dict(r)
                if "messages" in r2:
                    raise SystemExit("unexpected messages shape")
                r2["output" if "output" in r else "answer_sw"] = na
                new_hashes[sha(na)] = kind
                out.append(json.dumps(r2, ensure_ascii=False) + eol)
                result["edited"].append({"file": rel, "line": n, "kind": kind, "old_sha1": h, "new_sha256": sha(na), "old": a, "new": na})
            if touched and not dry:
                io.open(path, "w", encoding="utf-8", newline="").write("".join(out))
    n_edit, n_q = len(result["edited"]), len(result["quarantined"])
    # 13 pairs x 2 stages edited, 1 pair x 2 stages quarantined
    assert (n_edit, n_q) in ((26, 2), (0, 0)), (n_edit, n_q)
    if n_q and not dry:
        with io.open(QUARANTINE, "a", encoding="utf-8") as f:
            for q in qrows:
                f.write(json.dumps({"defect": Q4_DEFECT, "reason": "Q: mining employee's minimum wage under GN 605A. The answer states 'kwa sekta ya madini ya kimataifa na nishati ... karibu TZS 765,900' and instructs 'Hakikisha unalipa angalau TZS 765,900'. "
                                    "GN 605A (kazi.go.tz official copy, edition asserted, read 2026-11-17): energy / international companies monthly 765,900; mining and prospecting minerals monthly 695,000. A wrong-direction amount, so the pair is removed (R37 read first).",
                                    "correct_value": "energy sector, international companies: TZS 765,900/month; mining and prospecting minerals: TZS 695,000/month (primary mining licence and dealer/broker licences are lower)",
                                    "raw_sources_copies_not_touched": "datasets/tier1a/raw_sources/ (pre-cleaning provenance)", **q}, ensure_ascii=False) + "\n")
    if not n_edit and not n_q and not dry:
        result["already_applied"] = 1
    if not dry and (n_edit or n_q):                                   # a no-op re-run must NEVER overwrite the record of the real run (found when the idempotency re-run emptied it)
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, indent=1))
    print({"dry_run": dry, "edited": n_edit, "quarantined": n_q, "already_applied": result["already_applied"]})
    for e in result["edited"][:14]:
        print(e["file"].split("/")[-1], e["line"], e["kind"], "->", e["new"][-70:].replace("\n", " "))


if __name__ == "__main__":
    main()
