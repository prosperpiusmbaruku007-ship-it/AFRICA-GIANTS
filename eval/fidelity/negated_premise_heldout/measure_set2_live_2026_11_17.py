# -*- coding: utf-8 -*-
"""MEASURE THE FROZEN NEGATED-PREMISE SET #2 LIVE (founder's decisions 2026-11-16/17). Set #1 is untouched and is only QUOTED for comparison. Nothing is proposed from this script; the replies are READ BY HAND.

Refuses to run unless FROZEN_set2.json still matches the authored file. Calls PRODUCTION `chike-inference` ChikeModel through the Modal SDK, one question at a time, writing the artifact after EVERY row and resuming.

DEFINITIONS (fixed before any reply is read; the opener classifier is set #1's, unchanged):
  opener      YES = ndiyo / ndio / ni kweli / kweli ;  NO = hapana / la / siyo / sio / sivyo / si kweli / si sahihi ;  NONE = anything else (a model-free statement that just states the rule is NONE)
  INVERTED    correct_polarity YES/NO, opener YES/NO, and not the correct polarity -- whatever follows. `exclude_from_inversion` rows (s2_06, s2_07: ambiguous polarity) are NEVER in any rate: content only.
  ROUTE       `statement` when model_calls == 0 (a model-free engine/statement answer: it has no opener to invert); `model` otherwise. The HAPANA-BIAS question is asked of the MODEL-path rows only.
GROUPS (frozen on the rows): negated, tag_only (s2_10/11/13/15), leading_no_negation (s2_17/18), control (s2_19/20), content_only (s2_06/07).
THE KEY TEST: s2_18 -- an affirmative "ndiyo?" tag on a TRUE premise. Does Chike still open "Hapana"?

    python eval/fidelity/negated_premise_heldout/measure_set2_live_2026_11_17.py
Artifact: eval/results/negated_premise_set2_live_2026_11_17.json. Exit 0 always (it measures; it does not judge).
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
OUT = os.path.join(REPO, "eval", "results", "negated_premise_set2_live_2026_11_17.json")
YES = re.compile(r"^\W*(?:ndiyo|ndio|yes|ni\s+kweli|kweli)\b", re.IGNORECASE)
NO = re.compile(r"^\W*(?:hapana|la\b|siyo\b|sio\b|sivyo\b|no\b|si\s+kweli|si\s+sahihi)", re.IGNORECASE)


def opener(reply):
    t = (reply or "").lstrip()
    return "YES" if YES.match(t) else "NO" if NO.match(t) else "NONE"


def load_set():
    spec = importlib.util.spec_from_file_location("vnp", os.path.join(HERE, "validate_negated_premise_set.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    path = os.path.join(HERE, v.PROFILES["set2"]["authored"])
    p = v.check_frozen(path, os.path.join(HERE, v.PROFILES["set2"]["frozen"]))
    if p:
        print("[REFUSED] set #2 no longer matches FROZEN_set2.json:", p)
        sys.exit(2)
    problems, rows = v.validate(path, "set2")
    assert not problems, problems
    return rows


def rate(rows):
    inv = [r for r in rows if r["inverted"]]
    wo = [r for r in rows if r["opener"] != "NONE"]
    return f"{len(inv)}/{len(wo)} with an explicit opener; {len(inv)}/{len(rows)} of all"


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
            calls = tr.get("model_calls")
            rec = dict(id=r["id"], question=r["question"], reply=reply, path=tr.get("answer_path") or tr.get("path"), model_calls=calls, guards=tr.get("guards"),
                       scoring_group=r["scoring_group"], negation_form=r["negation_form"], premise_label=r["premise_label"], correct_polarity=r["correct_polarity"], topic=r["topic"],
                       exclude=bool(r.get("exclude_from_inversion")), route="statement" if calls == 0 else "model")
        except Exception as e:                                           # noqa: BLE001
            rec = dict(id=r["id"], error=repr(e)[:300])
        art["rows"].append(rec)
        json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[{rec.get('route', 'ERR'):<9}] {r['id']} grp={r['scoring_group']:<19} want={r['correct_polarity']:<3} path={rec.get('path')} calls={rec.get('model_calls')} -> {(rec.get('reply') or rec.get('error') or '')[:140]!r}")
    got = {x["id"]: x for x in art["rows"] if "error" not in x}
    ids = [r["id"] for r in rows]
    miss = [i for i in ids if i not in got]
    if miss:
        print("MISSING (errors):", miss)
    # derive EVERY verdict now (a resume carries data, never a conclusion)
    for x in got.values():
        x["opener"] = opener(x["reply"])
        x["inverted"] = (not x["exclude"]) and x["correct_polarity"] in ("YES", "NO") and x["opener"] in ("YES", "NO") and x["opener"] != x["correct_polarity"]
    scored = [got[i] for i in ids if i in got and not got[i]["exclude"]]
    neg = [x for x in scored if x["scoring_group"] in ("negated", "tag_only", "leading_no_negation")]
    print("\n=== ROUTE: statement (model-free, no opener) vs model path ===")
    for rt in ("statement", "model"):
        print(f"  {rt:<9}", [x["id"] for x in scored + [got[i] for i in ids if i in got and got[i]["exclude"]] if x["route"] == rt])
    print("\n=== OPENER INVERSION (an explicit Ndiyo/Hapana that contradicts the correct polarity), excluded rows never counted ===")
    for label, grp in (("ALL scored yes/no rows", [x for x in scored if x["correct_polarity"] in ("YES", "NO")]),
                       ("negated + tag_only + leading (the 18 minus s2_06)", neg),
                       ("  MODEL-path only", [x for x in neg if x["route"] == "model"]),
                       ("  statement-route only", [x for x in neg if x["route"] == "statement"]),
                       ("controls (s2_19, s2_20)", [x for x in scored if x["scoring_group"] == "control"])):
        print(f"  {label:<52} {rate(grp)}")
    print("-- by scoring group (all routes / model-path only)")
    for g in ("negated", "tag_only", "leading_no_negation", "control"):
        a = [x for x in scored if x["scoring_group"] == g]
        print(f"   {g:<20} {rate(a)}   | model-path: {rate([x for x in a if x['route'] == 'model'])}")
    print("-- by negation form")
    for f in sorted({x["negation_form"] for x in neg}):
        a = [x for x in neg if x["negation_form"] == f]
        print(f"   {f:<16} {rate(a)}   | model-path: {rate([x for x in a if x['route'] == 'model'])}")
    print("\n=== THE HAPANA BIAS: openers by premise label, MODEL-path rows (set #1 quoted for comparison: true_premise inverted 3/4, false_premise 0/8) ===")
    for lab in ("true_premise", "false_premise"):
        a = [x for x in scored if x["premise_label"] == lab and x["correct_polarity"] in ("YES", "NO") and x["route"] == "model"]
        c = collections.Counter(x["opener"] for x in a)
        print(f"  {lab:<13} model-path rows {len(a):>2}: openers {dict(c)}  inverted {sum(x['inverted'] for x in a)}   ids {[x['id'] for x in a if x['inverted']]}")
    a = [x for x in scored if x["premise_label"] == "true_premise" and x["correct_polarity"] == "YES"]
    print(f"  ALL true-premise rows (any route): {len(a)}; told Hapana: {[x['id'] for x in a if x['opener'] == 'NO']}; opened Ndiyo: {[x['id'] for x in a if x['opener'] == 'YES']}; no opener: {[x['id'] for x in a if x['opener'] == 'NONE']}")
    k = got.get("s2_18")
    if k:
        print(f"\n=== KEY TEST s2_18 (affirmative 'ndiyo?' tag, TRUE premise): route={k['route']} opener={k['opener']} inverted={k['inverted']}\n    {k['reply'][:300]!r}")
    print("\n=== PAIRS side by side ===")
    by = {r["id"]: r for r in rows}
    seen = set()
    for r in rows:
        for p in r.get("pair_with", []):
            key = tuple(sorted((r["id"], p)))
            if key in seen or p not in got or r["id"] not in got:
                continue
            seen.add(key)
            a, b = got[r["id"]], got[p]
            print(f"  {a['id']} [{a['scoring_group']:<19} want {a['correct_polarity']:<3}] opener {a['opener']:<4} route {a['route']:<9} | {b['id']} [{b['scoring_group']:<19} want {b['correct_polarity']:<3}] opener {b['opener']:<4} route {b['route']}")
    print("\nCONTENT-ONLY rows (s2_06, s2_07) and every reply: READ BY HAND in the artifact.")
    art["summary"] = {"missing": miss}
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
