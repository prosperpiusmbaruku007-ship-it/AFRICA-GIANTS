"""PRICE THE 2026-11-17 GUARDS on every stored reply, gold answer and training pair BEFORE they are called safe (R22 / D-FIDELITY-7 lesson). A flag in GOLD is the alarm; every flag is read.

  licence (FLIPPED)   fidelity.constant_violations, topic business_licence_expiry: a fixed calendar date asserted as a licence expiry (30 June is now the stale one)
  D-FIDELITY-16       fidelity.body_contradicts_d16: dividend_nonresident_rate / corporate_return_deadline / severance_flat_15
  repairs             fidelity.repair_gn605a_issuer, fidelity.repair_licence_authority: how many stored bodies each would CHANGE

    python eval/fidelity/price_d16_2026_11_17.py  ->  eval/results/price_d16_2026_11_17.json   (exit 1 if a founding specimen does not flag)
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity  # noqa: E402

spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py"))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
PROBES = [json.loads(l) for l in io.open(os.path.join(HERE, "d16_followup_probes_2026_11_17.jsonl"), encoding="utf-8") if l.strip()]


def licence_flags(q, a):
    return [r for t, r in fidelity.constant_violations(q, a) if t == "business_licence_expiry"]


GUARDS = (
    ("licence_fixed_date", lambda q, a: licence_flags(q, a)),
    ("d16", lambda q, a: [t for t, _ in fidelity.body_contradicts_d16(q, a)]),
    ("repair_gn605a_issuer", lambda q, a: ["changed"] if fidelity.repair_gn605a_issuer(q, a) != a else []),
    ("repair_licence_authority", lambda q, a: ["changed"] if fidelity.repair_licence_authority(q, a) != a else []),
)


def main():
    # R26: the founding specimens MUST flag or this instrument is inert.
    dead = []
    for p in PROBES:
        if p["expect"] == "clean" or not p["id"].endswith(("_01", "_02")):
            continue
        hit = {"licence": licence_flags, "dividend": lambda q, b: fidelity.body_contradicts_d16(q, b), "return": lambda q, b: fidelity.body_contradicts_d16(q, b),
               "severance": lambda q, b: fidelity.body_contradicts_d16(q, b),
               "pkf": lambda q, b: fidelity.repair_gn605a_issuer(q, b) != b, "licauth": lambda q, b: fidelity.repair_licence_authority(q, b) != b}[p["guard"]](p["question"], p["body"])
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
            rows = [{"src": s, "q": q[:200], "flags": fn(q, a), "reply": a[:320]} for s, q, a in pop if fn(q, a)]
            res["populations"][label]["guards"][gname] = {"flags": len(rows), "rows": rows}
            print(f"  {gname:<26} flags {len(rows):>3}")
            for r in rows:
                print(f"      {r['src']} | {r['q'][:80]}\n         {r['flags'][0]}: {r['reply'][:170]!r}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d16_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
