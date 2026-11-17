"""PRICE D-FIDELITY-19 (comparison fidelity) AND THE MONTHLY-AVERAGE VAT ROUTE on every stored reply, gold answer, training pair and held question BEFORE wiring is called safe (R22). A flag in GOLD is the alarm; every flag is read.

    python eval/fidelity/price_d19_2026_11_17.py  ->  eval/results/price_d19_2026_11_17.json   (exit 1 if the founding specimen does not flag)
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
from chike import fidelity, routing  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pf = _load("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py"))
sw = _load("_sw", os.path.join(REPO, "eval", "controls", "sweep_d18_routes_2026_11_17.py"))
SPECIMEN = ("Kulingana na taarifa uliyotoa, mauzo ya wastani ya milioni 18 kwa mwezi ni sawa na mauzo ya TZS 216,000,000 kwa mwaka. Hii ni chini ya kiwango cha milioni 200 kinachohitajika ili kusajiliwa kwa VAT. Thibitisha na tra.go.tz.")


def main():
    dead = [] if fidelity.comparison_violations(SPECIMEN) else ["founding specimen (live d644c71)"]
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        rows = [{"src": s, "q": q[:160], "violations": [(str(a), str(b), c) for a, b, c in fidelity.comparison_violations(a_)], "reply": a_[:360]} for s, q, a_ in pop if fidelity.comparison_violations(a_)]
        res["populations"][label] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
        print(f"\n{label}: {len(pop)} pairs, flags {len(rows)}")
        for r in rows[:15]:
            print(f"   {r['src']} | {r['q'][:70]}\n      {r['violations']}  {r['reply'][:230]!r}")
    qs = sw.questions()
    hits = [(q, src, routing.turnover_with_local_period(q)) for q, src in qs.items() if routing.turnover_with_local_period(q)]
    avg = [(q, s, r) for q, s, r in hits if r[1] == "monthly_average"]
    res["monthly_average"] = {"questions_swept": len(qs), "resolved_any": len(hits), "resolved_monthly_average": [{"q": q, "src": s, "amount": int(r[0])} for q, s, r in avg]}
    print(f"\nRESOLVER over {len(qs)} questions: {len(hits)} resolve; monthly_average {len(avg)}")
    for q, s, r in avg:
        print(f"   [{s}] {int(r[0]):,} | {q[:160]}")
    # the SINGLE-AMOUNT path: which held questions would now be answered by the engine instead of the never-guess exit
    single = [(q, s) for q, s in qs.items() if routing.detect_intent(q) == "vat_registration" and routing.turnover_period(q) == "monthly" and routing.monthly_average_stated(q)]
    res["monthly_average_single_amount"] = [{"q": q, "src": s} for q, s in single]
    print(f"\nSINGLE-AMOUNT monthly-average route: {len(single)}")
    for q, s in single:
        print(f"   [{s}] {q[:170]}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d19_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
