"""PRICE D-FIDELITY-20 (the company annual-return deadline constant) over every stored reply, gold answer and training pair BEFORE it is called safe (R22). A hit in GOLD is the alarm; every hit is READ.

    python eval/fidelity/price_d20_2026_11_17.py  ->  eval/results/price_d20_2026_11_17.json   (exit 1 if the founding specimen does not flag)
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
TOPIC = "brela_annual_return_deadline"
SPECIMEN_Q = "Mara ngapi kampuni iliyosajiliwa na BRELA inahitajika kuwasilisha annual return (ripoti ya kila mwaka)?"


def hits(q, a):
    return [s for t, s in fidelity.body_contradicts_d16(q, a) if t == TOPIC]


def main():
    gates = [r for r in json.load(io.open(os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json"), encoding="utf-8"))["rows"] if r["id"] == "eval_072"]
    dead = [] if gates and hits(SPECIMEN_Q, gates[0]["generated"]) else ["founding specimen (eval_072, gate c2143c0)"]
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        rows = [{"src": s, "q": q[:160], "sentences": hits(q, a), "reply": a[:300]} for s, q, a in pop if hits(q, a)]
        res["populations"][label] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
        print(f"\n{label}: {len(pop)} pairs, flags {len(rows)}")
        for r in rows:
            print(f"   {r['src']} | {r['q'][:80]}\n      {r['sentences']}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d20_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
