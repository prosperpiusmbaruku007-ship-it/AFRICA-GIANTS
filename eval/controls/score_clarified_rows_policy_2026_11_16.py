# -*- coding: utf-8 -*-
"""A2 UNDER TWO CLARIFICATION POLICIES, OLD BESIDE NEW (2026-11-16, founder's decision 2a).

OLD  (the harness: kaggle/eval_gate_production_2026_10_09.py::_score_both_keys)  `if clarified: new_pass = False` -- every clarification is a miss.
NEW  a clarification is CORRECT only when BOTH hold:
       (1) the GOLD is itself a clarification: it contains an ask cue (nipe / niambie / nihitaji / tafadhali / badilisha / sina taarifa ...) and states NO computed levy result (`= TZS <n>`) -- a gold that
           computes or answers is not a clarification, even if it also asks;
       (2) the REPLY asks for the SAME missing piece: the sets of pieces {conversion, headcount, payroll} the two texts ask for intersect, and if the gold asks for a currency conversion the reply must too.
Every promoted row is printed; nothing is promoted silently. This does not touch the harness or any key: it is a re-scoring of an existing artifact.

    python eval/controls/score_clarified_rows_policy_2026_11_16.py [gate_artifact.json ...]
"""
import io, json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ASK = re.compile(r"\b(?:nipe|niambie|nihitaji|nahitaji|tafadhali|badilisha|ubadilishe|toa|niandikie|sina\s+(?:taarifa|kumbukumbu|ujumbe|hesabu)|sikumbuki|sipati\s+kukokotoa)\b", re.I)
RESULT = re.compile(r"=\s*TZS\s*[\d,]+", re.I)
CONV = re.compile(r"sarafu|badilisha|kubadilisha|badilishe|ubadilishaji|kuwa\s+shilingi", re.I)
HEAD = re.compile(r"idadi\s+ya\s+wafanyakazi|wafanyakazi\s+wangapi|idadi\s+ya\s+watu|idadi\s+yao", re.I)
PAY = re.compile(r"mshahara|mishahara|jumla\s+ya\s+mishahara|payroll|kiasi\s+cha", re.I)


def pieces(t):
    return {k for k, rx in (("conversion", CONV), ("headcount", HEAD), ("payroll", PAY)) if rx.search(t or "")}


def promoted(r):
    g, rep = r["correct_answer_sw"], r["generated"]
    if not ASK.search(g) or RESULT.search(g):
        return False, "gold is not a pure clarification"
    gp, rp = pieces(g), pieces(rep)
    if "conversion" in gp and "conversion" not in rp:
        return False, "gold asks for a conversion, reply does not"
    if not (gp & rp):
        return False, f"different missing piece (gold {sorted(gp)}, reply {sorted(rp)})"
    return True, f"same piece {sorted(gp & rp)}"


def main():
    for path in (sys.argv[1:] or [os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json")]):
        d = json.load(io.open(path, encoding="utf-8"))
        inc = [r for r in d["rows"] if r["subdomain"] != "out_of_corpus"]
        old = sum(str(r["pass"]) == "True" for r in inc)
        clar = [r for r in inc if str(r["clarified"]) == "True"]
        prom, kept = [], []
        for r in clar:
            ok, why = promoted(r)
            (prom if ok else kept).append((r["id"], why))
        print(f"\n{os.path.basename(path)}: n={len(inc)}  clarified={len(clar)}")
        print(f"  A2 OLD (clarified => fail)      {old}/{len(inc)} = {old / len(inc):.1%}")
        print(f"  A2 NEW (matching clarification) {old + len(prom)}/{len(inc)} = {(old + len(prom)) / len(inc):.1%}   (+{len(prom)})")
        print("  PROMOTED:", ", ".join(i for i, _ in prom))
        for i, w in kept:
            print(f"  stays a miss: {i}: {w}")
        json.dump({"artifact": os.path.basename(path), "n": len(inc), "old": old, "new": old + len(prom), "promoted": dict(prom), "kept_as_miss": dict(kept)},
                  io.open(os.path.join(REPO, "eval", "results", "clarified_policy_" + os.path.basename(path)), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
