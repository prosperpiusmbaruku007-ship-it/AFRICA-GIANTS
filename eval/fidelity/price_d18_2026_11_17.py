"""PRICE THE NEXT-SMALL-BATCH CODE (2026-11-17) on every stored reply, gold answer, training pair and question we hold BEFORE it is called safe (R22). A flag in GOLD is the alarm; every flag is read.

  firm_repair       fidelity.repair_firm_authority: bodies it would CHANGE (a practitioner firm named as the authority to confirm with)
  confirm_dedupe    fidelity._drop_redundant_confirm_tail: bodies whose last 'Thibitisha na X.' sentence it would drop
  vat_resolver      routing.turnover_with_local_period over EVERY question we hold: the questions the VAT engine would now answer instead of asking

    python eval/fidelity/price_d18_2026_11_17.py  ->  eval/results/price_d18_2026_11_17.json   (exit 1 if a founding specimen does not flag)
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
PROBES = {json.loads(l)["id"]: json.loads(l) for l in io.open(os.path.join(HERE, "d18_batch_probes_2026_11_17.jsonl"), encoding="utf-8") if l.strip()}

GUARDS = (
    ("firm_repair", lambda q, a: ["changed"] if fidelity.repair_firm_authority(q, a) != a else []),
    ("confirm_dedupe", lambda q, a: ["changed"] if fidelity._drop_redundant_confirm_tail(a) != a else []),
)


def main():
    p1, p4, v1 = PROBES["d18_fm_01"], PROBES["d18_dd_01"], PROBES["d18_vat_01"]
    dead = []
    if fidelity.repair_firm_authority(p1["question"], p1["body"]) == p1["body"]:
        dead.append("d18_fm_01")
    if fidelity._drop_redundant_confirm_tail(p4["body"]) == p4["body"]:
        dead.append("d18_dd_01")
    if routing.turnover_with_local_period(v1["question"]) is None:
        dead.append("d18_vat_01")
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        res["populations"][label] = {"pairs": len(pop), "guards": {}}
        print(f"\n{label}: {len(pop)} pairs")
        for gname, fn in GUARDS:
            rows = [{"src": s, "q": q[:200], "reply": a[:300]} for s, q, a in pop if fn(q, a)]
            res["populations"][label]["guards"][gname] = {"flags": len(rows), "rows": rows}
            print(f"  {gname:<16} flags {len(rows):>3}")
            for r in rows[:12]:
                print(f"      {r['src']} | {r['q'][:70]}\n         {r['reply'][:170]!r}")
    qs = sw.questions()
    hits = [(q, src, routing.turnover_with_local_period(q)) for q, src in qs.items() if routing.turnover_with_local_period(q)]
    res["vat_resolver"] = {"questions_swept": len(qs), "resolved": [{"q": q, "src": s, "amount": int(a[0]), "period": a[1]} for q, s, a in hits]}
    print(f"\nVAT RESOLVER over {len(qs)} questions: resolves {len(hits)}")
    for q, s, a in hits:
        print(f"   [{s}] {int(a[0]):,} {a[1]} | {q[:150]}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d18_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
