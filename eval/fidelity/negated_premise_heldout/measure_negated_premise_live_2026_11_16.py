# -*- coding: utf-8 -*-
"""MEASURE THE OPENER-INVERSION RATE ON THE FROZEN NEGATED-PREMISE SET, LIVE (founder's decision, 2026-11-16). Nothing is proposed from this script; the replies are READ BY HAND in the report.

Refuses to run unless the authored set still matches FROZEN.json (a frozen set is never edited). Calls PRODUCTION `chike-inference` ChikeModel through the Modal SDK, one question at a time, writing the artifact after EVERY row
and resuming from it (a dropped link costs one row, never the run).

DEFINITIONS (fixed here, before any reply is read):
  opener      the polarity of the reply's FIRST words: YES = ndiyo / ndio / yes / "ni kweli" / "kweli" ; NO = hapana / la / siyo / sio / sivyo / no / "si kweli" / "si sahihi" ; NONE = anything else (including a model-free
              statement that simply states the rule).
  INVERTED    a yes/no row (correct_polarity YES or NO) whose opener is YES or NO and is NOT the correct polarity -- whatever the content that follows. An opener of NONE is NOT an inversion (reported separately).
  OPEN row    correct_polarity OPEN: the measure is whether the reply opens with Ndiyo/Hapana anyway (it should not).
Reported: negated rows (all, and those with an explicit opener) split by author model, negation form and premise label; the plain yes/no controls as the baseline; OPEN rows; the paired rows side by side.

    python eval/fidelity/negated_premise_heldout/measure_negated_premise_live_2026_11_16.py
Artifact: eval/results/negated_premise_live_2026_11_16.json. Exit 0 always (it measures; it does not judge).
"""
import collections
import importlib.util
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "negated_premise_live_2026_11_16.json")
YES = re.compile(r"^\W*(?:ndiyo|ndio|yes|ni\s+kweli|kweli)\b", re.IGNORECASE)
NO = re.compile(r"^\W*(?:hapana|la\b|siyo\b|sio\b|sivyo\b|no\b|si\s+kweli|si\s+sahihi)", re.IGNORECASE)


def opener(reply):
    t = (reply or "").lstrip()
    if YES.match(t):
        return "YES"
    if NO.match(t):
        return "NO"
    return "NONE"


def load_set():
    spec = importlib.util.spec_from_file_location("vnp", os.path.join(HERE, "validate_negated_premise_set.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    p = v.check_frozen(v.AUTHORED)
    if p:
        print("[REFUSED] the authored set no longer matches FROZEN.json:", p)
        sys.exit(2)
    problems, rows = v.validate(v.AUTHORED)
    assert not problems, problems
    return rows


def rate(rows):
    inv = [r for r in rows if r["inverted"]]
    wo = [r for r in rows if r["opener"] != "NONE"]
    return f"{len(inv)}/{len(wo)} with an explicit opener ({(100 * len(inv) / len(wo)) if wo else 0:.0f}%); {len(inv)}/{len(rows)} of all rows ({(100 * len(inv) / len(rows)) if rows else 0:.0f}%)"


def main():
    rows = load_set()
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["id"] for r in art["rows"]}
    for r in rows:
        if r["id"] in done:
            continue
        try:
            out = m.run.remote(r["question"])
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            tr = out if isinstance(out, dict) else {}
            op = opener(reply)
            rec = dict(id=r["id"], question=r["question"], reply=reply, path=tr.get("answer_path") or tr.get("path"), model_calls=tr.get("model_calls"), guards=tr.get("guards"),
                       author_model=r["author_model"], negation_form=r["negation_form"], premise_label=r["premise_label"], correct_polarity=r["correct_polarity"], topic=r["topic"],
                       opener=op, inverted=(r["correct_polarity"] in ("YES", "NO") and op in ("YES", "NO") and op != r["correct_polarity"]),
                       opens_with_polarity_on_open_row=(r["correct_polarity"] == "OPEN" and op in ("YES", "NO")))
        except Exception as e:                                           # noqa: BLE001
            rec = dict(id=r["id"], error=repr(e)[:300])
        art["rows"].append(rec)
        json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[{rec.get('opener', 'ERR'):<4}] {r['id']} want={r['correct_polarity']:<4} inv={rec.get('inverted')} path={rec.get('path')} calls={rec.get('model_calls')}  -> {(rec.get('reply') or rec.get('error') or '')[:150]!r}")
    got = {x["id"]: x for x in art["rows"] if "error" not in x}
    ids = [r["id"] for r in rows]
    miss = [i for i in ids if i not in got]
    if miss:
        print("MISSING (errors):", miss)
    neg = [got[i] for i in ids if i in got and got[i]["negation_form"] != "none"]
    plain = [got[i] for i in ids if i in got and got[i]["negation_form"] == "none" and got[i]["correct_polarity"] in ("YES", "NO")]
    opn = [got[i] for i in ids if i in got and got[i]["correct_polarity"] == "OPEN"]
    print("\n=== OPENER INVERSION (an opener that contradicts the correct polarity) ===")
    print("NEGATED rows          :", rate(neg))
    print("PLAIN yes/no controls :", rate(plain))
    for field in ("author_model", "negation_form", "premise_label", "correct_polarity"):
        print(f"-- negated, by {field}")
        for k, grp in sorted(collections.defaultdict(list, {k: [r for r in neg if r[field] == k] for k in {r[field] for r in neg}}).items()):
            print(f"   {k:<16} {rate(grp)}")
    print(f"OPEN rows opening with Ndiyo/Hapana anyway: {sum(1 for r in opn if r['opens_with_polarity_on_open_row'])}/{len(opn)}  {[r['id'] for r in opn if r['opens_with_polarity_on_open_row']]}")
    print("\n=== PAIRS side by side (same rule: opener of each) ===")
    seen = set()
    by = {r["id"]: r for r in rows}
    for r in rows:
        for p in r.get("pair_with", []):
            key = tuple(sorted((r["id"], p)))
            if key in seen or p not in got or r["id"] not in got:
                continue
            seen.add(key)
            a, b = got[r["id"]], got[p]
            print(f"  {a['id']} [{a['negation_form']:<13} want {a['correct_polarity']:<4}] opener {a['opener']:<4} inv={a['inverted']!s:<5} | {b['id']} [{b['negation_form']:<13} want {b['correct_polarity']:<4}] opener {b['opener']:<4} inv={b['inverted']}")
    art["summary"] = {"negated": rate(neg), "plain": rate(plain), "open_opening_with_polarity": [r["id"] for r in opn if r["opens_with_polarity_on_open_row"]], "missing": miss}
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
