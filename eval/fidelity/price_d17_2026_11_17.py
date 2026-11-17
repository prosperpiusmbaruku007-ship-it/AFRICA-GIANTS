"""PRICE THE 2026-11-17 BATCH on every stored reply, gold answer and training pair BEFORE it is called safe (R22 / D-FIDELITY-7 lesson). A flag in GOLD is the alarm; every flag is read.

  names              fidelity.strip_unsupported_names: how many bodies would LOSE a personal name (supported = nothing: the worst case for a body, since no served fact is available offline)
  licence_period     fidelity.licence_validity_period_violations
  licence_authority  fidelity.repair_licence_authority (the fixed cue, lga/mlywf hosts)
  authority_repair   fidelity.repair_authority: bodies it changes NOW that it did not change under the previous topic rule (tax-wins-over-labour)
  gn605a             fidelity.repair_gn605a_issuer (office replacement)

    python eval/fidelity/price_d17_2026_11_17.py  ->  eval/results/price_d17_2026_11_17.json   (exit 1 if a founding specimen does not flag)
"""
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity  # noqa: E402

spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py"))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
PROBES = [json.loads(l) for l in io.open(os.path.join(HERE, "d17_batch_probes_2026_11_17.jsonl"), encoding="utf-8") if l.strip()]


def _old_authority_topic(question):
    """The rule BEFORE 2026-11-17: exactly one topic row, else none."""
    hits = [t for t in fidelity._AUTH_TOPICS if t[1].search(question or "")]
    return hits[0] if len(hits) == 1 else None


def _repair_under_old_topic(q, b):
    orig = fidelity.authority_topic
    fidelity.authority_topic = _old_authority_topic
    try:
        return fidelity.repair_authority(q, b)
    finally:
        fidelity.authority_topic = orig


GUARDS = (
    ("names", lambda q, a: [n for n in fidelity.strip_unsupported_names(a, q, "")[1]]),
    ("licence_period", lambda q, a: fidelity.licence_validity_period_violations(q, a)),
    ("licence_authority", lambda q, a: ["changed"] if fidelity.repair_licence_authority(q, a) != a else []),
    ("authority_repair_newly_changed", lambda q, a: ["changed"] if fidelity.repair_authority(q, a) != _repair_under_old_topic(q, a) else []),
    ("gn605a", lambda q, a: ["changed"] if fidelity.repair_gn605a_issuer(q, a) != a else []),
)


def main():
    dead = []
    for p in PROBES:
        if p["id"] in ("d17_nm_01", "d17_pd_01", "d17_cue_01", "d17_tx_06", "d17_gn_01"):
            g = p["guard"]
            hit = {"names": lambda: fidelity.strip_unsupported_names(p["body"], p["question"], "")[1], "period": lambda: fidelity.licence_validity_period_violations(p["question"], p["body"]),
                   "licauth": lambda: fidelity.repair_licence_authority(p["question"], p["body"]) != p["body"], "authrepair": lambda: fidelity.repair_authority(p["question"], p["body"]) != p["body"],
                   "gn605a": lambda: fidelity.repair_gn605a_issuer(p["question"], p["body"]) != p["body"]}[g]()
            if not hit:
                dead.append(p["id"])
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        res["populations"][label] = {"pairs": len(pop), "guards": {}}
        print(f"\n{label}: {len(pop)} pairs")
        for gname, fn in GUARDS:
            rows = [{"src": s, "q": q[:200], "flags": fn(q, a), "reply": a[:300]} for s, q, a in pop if fn(q, a)]
            res["populations"][label]["guards"][gname] = {"flags": len(rows), "rows": rows}
            print(f"  {gname:<32} flags {len(rows):>3}")
            for r in rows[:14]:
                print(f"      {r['src']} | {r['q'][:70]}\n         {str(r['flags'][0])[:60]}: {r['reply'][:150]!r}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d17_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
