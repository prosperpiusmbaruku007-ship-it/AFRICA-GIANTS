"""PRICE D-FIDELITY-15 (WCF-deducted-from-wages, input-VAT-on-a-passenger-car) on every stored reply, gold answer and training pair BEFORE it is called safe. A flag in GOLD is the alarm; every flag is read.

    python eval/fidelity/price_d15_2026_11_17.py -> eval/results/price_d15_2026_11_17.json
"""
import importlib.util, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity                                                  # noqa: E402
spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py")); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
PROBES = [json.loads(l) for l in io.open(os.path.join(HERE, "d15_constant_probes_2026_11_17.jsonl"), encoding="utf-8") if l.strip()]


def main():
    dead = [p["id"] for p in PROBES if p["id"] in ("d15_01", "d15_02") and not fidelity.body_contradicts_d15(p["question"], p["body"])]
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        rows = [{"src": s, "q": q[:200], "flags": fidelity.body_contradicts_d15(q, a), "reply": a[:300]} for s, q, a in pop if fidelity.body_contradicts_d15(q, a)]
        res["populations"][label] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
        print(f"{label:<15} {len(pop):>6} pairs   flags {len(rows):>3}")
        for r in rows:
            print(f"   {r['src']} | {r['q'][:90]}\n      {r['flags'][0][0]}: {r['flags'][0][1][:200]!r}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d15_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
