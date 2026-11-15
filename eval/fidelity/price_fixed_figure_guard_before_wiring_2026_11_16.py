# -*- coding: utf-8 -*-
"""WHAT WOULD D-FIDELITY-10 REPLACE, IF WIRED TODAY?  (the guard can withhold a real user's answer, so it is priced BEFORE wiring: the
 CLAUDE.md block above R17.)

POPULATION and WHY (R22). The guard judges (question, model body) PAIRS whose question is about one of five fixed-statement topics. So:
  GOLD    every eval/accuracy_gate + refusal_gate row with a question and a human-asserted correct answer. A flag here is the strongest
          false-positive signal: the guard is over-broad, or the gold is wrong.
  PAIRED  every cleaned_pairs / sft_shaped_pairs row (question_sw + answer_sw): the prose the model was trained on, the closest offline proxy
          for what it emits.
  STORED  every recorded model reply in eval/results/*.json that sits beside its question.
Only rows whose QUESTION matches a topic are judged, and the script reports how many that is per topic: a population with no topic rows would
make "0 flags" vacuous (R20), so it asserts a floor.

CANNOT SHOW (R21): all three share vocabulary with the facts by construction; 0 flags is a lower bound on cost, not a safety verdict.
FOUNDING SPECIMENS: the five live wrong replies of 2026-11-13 must be flagged, or the instrument is inert.

R18: committed before the write-up. Artifact: eval/results/fixed_figure_guard_prewiring_2026_11_16.json
"""
import collections
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import fidelity, routing                                  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "fixed_figure_guard_prewiring_2026_11_16.json")
Q_KEYS = ("question_sw", "question", "q", "instruction", "prompt")
A_GOLD = ("correct_answer_sw", "expected_answer_sw", "answer_sw", "gold_sw", "expected_sw")
A_REPLY = ("generated", "reply", "text", "raw_text", "answer", "model_reply", "response")


def _jsonl(path):
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            try:
                yield n, json.loads(line)
            except Exception:                                        # noqa: BLE001
                continue


def _first(obj, keys):
    return next((obj[k] for k in keys if isinstance(obj.get(k), str) and obj[k].strip()), "")


def _walk(node, depth=0):
    if depth > 4:
        return
    if isinstance(node, list):
        for it in node:
            if isinstance(it, dict) and _first(it, Q_KEYS) and _first(it, A_REPLY):
                yield it
            else:
                yield from _walk(it, depth + 1)
    elif isinstance(node, dict):
        for v in node.values():
            yield from _walk(v, depth + 1)


def collect():
    rows, seen = [], set()
    for sub in ("accuracy_gate", "refusal_gate"):
        for path in sorted(glob.glob(os.path.join(REPO, "eval", sub, "*.jsonl"))):
            for n, o in _jsonl(path):
                q, a = _first(o, Q_KEYS), _first(o, A_GOLD)
                if q and a:
                    rows.append(("GOLD", str(o.get("id") or f"{os.path.basename(path)}:{n}"), q, a))
    for sub in ("cleaned_pairs", "sft_shaped_pairs"):
        for path in sorted(glob.glob(os.path.join(REPO, "datasets", "tier1a", sub, "*.jsonl"))):
            for n, o in _jsonl(path):
                q, a = _first(o, Q_KEYS), _first(o, ("answer_sw", "output"))
                if q and a:
                    rows.append(("PAIRED", f"{os.path.basename(path)}:{n}", q, a))
    for path in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        if os.path.basename(path) in (os.path.basename(OUT), "coverage_deploy_live_2026_11_13.json"):
            continue
        try:
            blob = json.load(open(path, encoding="utf-8"))
        except Exception:                                            # noqa: BLE001
            continue
        for it in _walk(blob):
            q, a = _first(it, Q_KEYS), _first(it, A_REPLY)
            if a.strip() == "[MODEL]":                    # the coverage harness's placeholder for "a model answer", not a reply
                continue
            fp = (q[:100], a[:100])
            if fp in seen:
                continue
            seen.add(fp)
            rows.append(("STORED", f"{os.path.basename(path)}:{it.get('id', '?')}", q, a))
    return rows


def main():
    rows = collect()
    by_pop = collections.Counter(p for p, *_ in rows)
    assert by_pop["GOLD"] > 300 and by_pop["PAIRED"] > 1000 and by_pop["STORED"] > 200, by_pop
    on_topic = collections.Counter()
    flagged = []
    for pop, rid, q, a in rows:
        topics = routing.fixed_statement_topics(q)
        for t in topics:
            on_topic[(pop, t)] += 1
        v = fidelity.fixed_figure_violations(q, a)
        if v:
            flagged.append({"population": pop, "id": rid, "question": q[:200], "violations": v, "body": a[:600]})
    # instrument exercised, not merely run (R20): topic rows exist in every population, and the live specimens are flagged.
    assert sum(on_topic.values()) >= 10, f"only {sum(on_topic.values())} on-topic rows: a clean result would be vacuous"
    live = json.load(open(os.path.join(REPO, "eval", "results", "coverage_deploy_live_2026_11_13.json"), encoding="utf-8"))["rows"]
    specimens = [r for r in live if fidelity.fixed_figure_violations(r["q"], r.get("reply", ""))]
    assert len(specimens) == 5, f"founding specimens flagged: {len(specimens)} (want 5)"
    print("population:", dict(by_pop))
    print("on-topic rows (population, topic):")
    for k in sorted(on_topic):
        print("  ", k, on_topic[k])
    gold = [f for f in flagged if f["population"] == "GOLD"]
    print(f"\nFLAGS: {len(flagged)}  (GOLD {len(gold)}, PAIRED {sum(f['population'] == 'PAIRED' for f in flagged)}, "
          f"STORED {sum(f['population'] == 'STORED' for f in flagged)})")
    for f in flagged:
        print(f"\n[{f['population']}] {f['id']}\n  Q: {f['question']}\n  {f['violations']}\n  A: {f['body'][:300]!r}")
    json.dump({"population": dict(by_pop), "on_topic": {f"{p}|{t}": n for (p, t), n in on_topic.items()},
               "founding_specimens_flagged": len(specimens), "flags": flagged}, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
