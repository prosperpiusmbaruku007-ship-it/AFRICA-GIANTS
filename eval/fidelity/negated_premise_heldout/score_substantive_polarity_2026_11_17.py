# -*- coding: utf-8 -*-
"""STAGE 3 (READ-ONLY): THE SUBSTANTIVE-POLARITY CHECK, applied retroactively to frozen negated-premise sets #1 and #2.

PROTOCOL, FIXED BEFORE ANY REPLY WAS ADJUDICATED (R18 / R22):
  POPULATION   every row of both sets with a stored live reply (set #1: 29, eval/results/negated_premise_live_2026_11_16.json; set #2: 20, eval/results/negated_premise_set2_live_2026_11_17.json), judged against the GOLD with the
               2026-11-17 sidecar corrections applied (np_13's answer text; s2_07 -> TRUE/YES). The replies are those of the BUILDS THAT PRODUCED THEM: this measures the METRIC, not today's system.
  SUBSTANTIVE VERDICT (all sentences of the reply, not the opener) on the point the question turns on:
      RIGHT    consistent with the gold, no sentence contradicting it or a locked fact on the point asked
      WRONG    a sentence asserts something that contradicts the gold / a locked fact on the point asked (a wrong figure, an inverted rule, a fabricated rule or figure)
      PARTIAL  right on the asked point but omits a limb the gold needs, adds an unsupported claim without contradicting it, or is self-contradictory
      NONE     no stance on the asked point (a non-answer, a clarification request, a wrong-topic answer)
  SUBSTANTIVE POLARITY (yes/no rows): YES / NO / NONE = the polarity the CONTENT implies about the user's premise, independent of the opener.
  THE THREE DISAGREEMENT CLASSES with the opener metric (the reason stage 3 exists):
      A  opener RIGHT, content WRONG       (s2_04-type: "Ndiyo, ... unapaswa kuikata kutoka kwa mishahara")
      B  opener INVERTED, content RIGHT    (an opener that contradicts a body that is correct)
      C  NO opener, content WRONG          (s2_17-type: a substantive inversion no opener metric can see)
  EVERY row is READ and adjudicated by hand: eval/fidelity/negated_premise_heldout/stage3_adjudication_2026_11_17.json (verdict, polarity, reason per row). This script NEVER classifies a reply; it re-derives the OPENER
  (the existing classifier, imported not re-implemented), applies the sidecars, and tabulates the hand verdicts against it.

    python eval/fidelity/negated_premise_heldout/score_substantive_polarity_2026_11_17.py  ->  eval/results/substantive_polarity_stage3_2026_11_17.json
"""
import collections
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "substantive_polarity_stage3_2026_11_17.json")


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    opener = _load("m2", "measure_set2_live_2026_11_17.py").opener
    adj = json.load(io.open(os.path.join(HERE, "stage3_adjudication_2026_11_17.json"), encoding="utf-8"))["rows"]
    rows = []
    for sid, authored, art, side in (("set1", "negated_premise_AUTHORED.jsonl", "negated_premise_live_2026_11_16.json", "FROZEN_sidecar_2026_11_17.json"),
                                     ("set2", "negated_premise_set2_AUTHORED.jsonl", "negated_premise_set2_live_2026_11_17.json", "FROZEN_set2_sidecar_2026_11_17.json")):
        gold = {json.loads(l)["id"]: json.loads(l) for l in io.open(os.path.join(HERE, authored), encoding="utf-8") if l.strip()}
        corr = {c["id"]: c["corrected"] for c in json.load(io.open(os.path.join(HERE, side), encoding="utf-8"))["corrections"]}
        for r in json.load(io.open(os.path.join(REPO, "eval", "results", art), encoding="utf-8"))["rows"]:
            if "error" in r:
                continue
            g = dict(gold[r["id"]])
            g.update(corr.get(r["id"], {}))
            a = adj[r["id"]]
            op = opener(r["reply"])
            want = g["correct_polarity"]
            excluded = bool(g.get("exclude_from_inversion"))
            calls = r.get("model_calls")
            rows.append(dict(set=sid, id=r["id"], want=want, opener=op, verdict=a["verdict"], pol=a["pol"], excluded=excluded, route="statement/engine (0 calls)" if calls == 0 else "model path",
                             opener_inverted=(not excluded) and want in ("YES", "NO") and op in ("YES", "NO") and op != want,
                             subst_flip=(not excluded) and want in ("YES", "NO") and a["pol"] in ("YES", "NO") and a["pol"] != want, why=a["why"]))
    assert len(rows) == 49 and set(adj) == {r["id"] for r in rows}, "adjudication and artifacts disagree"
    wrong = [r for r in rows if r["verdict"] == "WRONG"]
    # classes are defined over rows whose verdict is hand-adjudicated, EXCLUDED rows included for A/B/C reporting but never in the rates
    A = [r for r in rows if r["verdict"] == "WRONG" and r["want"] in ("YES", "NO") and r["opener"] == r["want"]]
    B = [r for r in rows if r["verdict"] == "RIGHT" and r["want"] in ("YES", "NO") and r["opener"] in ("YES", "NO") and r["opener"] != r["want"]]
    C = [r for r in rows if r["verdict"] == "WRONG" and r["opener"] == "NONE"]
    res = {"n": len(rows), "by_verdict": collections.Counter(r["verdict"] for r in rows), "by_set": {}, "classes": {"A_opener_right_content_wrong": [r["id"] for r in A], "B_opener_inverted_content_right": [r["id"] for r in B], "C_no_opener_content_wrong": [r["id"] for r in C]}}
    print(f"{len(rows)} rows adjudicated by hand.   verdicts: {dict(res['by_verdict'])}")
    for sid in ("set1", "set2"):
        s = [r for r in rows if r["set"] == sid]
        res["by_set"][sid] = dict(collections.Counter(r["verdict"] for r in s))
        print(f"  {sid}: {len(s)} rows  {res['by_set'][sid]}")
    print("\n=== THE TWO METRICS ON THE SAME ROWS (excluded rows s2_06 / s2_07 are in NEITHER rate) ===")
    scored = [r for r in rows if not r["excluded"] and r["want"] in ("YES", "NO")]
    oi = [r["id"] for r in scored if r["opener_inverted"]]
    sf = [r["id"] for r in scored if r["subst_flip"]]
    res["opener_inverted"], res["substantive_flip"] = oi, sf
    print(f"  yes/no rows scored: {len(scored)}")
    print(f"  OPENER metric (explicit Ndiyo/Hapana contradicts the correct polarity): {len(oi)}  {oi}")
    print(f"  SUBSTANTIVE polarity flip (the CONTENT implies the opposite):         {len(sf)}  {sf}")
    print(f"  in the opener metric but NOT a substantive flip (the opener over-counts): {[i for i in oi if i not in sf]}")
    print(f"  substantive flip the opener metric MISSES:                                {[i for i in sf if i not in oi]}")
    print("\n=== ANY substantive WRONG content, vs what the opener metric can see (all 49 rows) ===")
    seen = [r["id"] for r in wrong if r["opener_inverted"]]
    print(f"  WRONG-content rows: {len(wrong)}  {[r['id'] for r in wrong]}")
    print(f"  of which the opener metric flags (inverted opener, scored): {seen}")
    print(f"  INVISIBLE to the opener metric: {[r['id'] for r in wrong if r['id'] not in seen]}")
    print(f"\n  CLASS A  opener RIGHT, content WRONG   : {[r['id'] for r in A]}")
    print(f"  CLASS B  opener INVERTED, content RIGHT: {[r['id'] for r in B]}")
    print(f"  CLASS C  NO opener, content WRONG      : {[r['id'] for r in C]}")
    print("\n=== BY ROUTE (substantive verdicts) ===")
    for rt in ("statement/engine (0 calls)", "model path"):
        s = [r for r in rows if r["route"] == rt]
        print(f"  {rt:<28} {len(s):>2} rows  {dict(collections.Counter(r['verdict'] for r in s))}")
        res.setdefault("by_route", {})[rt] = dict(collections.Counter(r["verdict"] for r in s))
    mp_true = [r for r in rows if r["route"] == "model path" and r["want"] == "YES" and not r["excluded"]]
    print(f"\n=== THE 'HAPANA BIAS' RE-READ BY CONTENT: model-path TRUE-premise (YES) rows ===")
    print(f"  {len(mp_true)} rows; opener Hapana: {[r['id'] for r in mp_true if r['opener'] == 'NO']}; of those the CONTENT is wrong/stance-inverted: {[r['id'] for r in mp_true if r['opener'] == 'NO' and r['subst_flip']]}")
    print(f"  content stance NO (inverted) on a TRUE premise, whatever the opener: {[r['id'] for r in mp_true if r['pol'] == 'NO']}")
    res["rows"] = rows
    json.dump(res, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    return 0


if __name__ == "__main__":
    sys.exit(main())
