"""PRICE D-FIDELITY-21 (GN 605A sector count -> 16) over every stored reply, gold answer and training pair BEFORE it is called safe (R22). A change in GOLD is the alarm; every change is READ.

    python eval/fidelity/price_d21_2026_11_17.py  ->  eval/results/price_d21_2026_11_17.json   (exit 1 if the founding specimen is not repaired)
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


def main():
    art = json.load(io.open(os.path.join(REPO, "eval", "results", "targeted_gate4_2026_11_17.json"), encoding="utf-8"))["rows"]
    live = next(r for r in art if r["id"] == "eval_117")["reply"]
    q117 = "GN 605A inashughulikia sekta ngapi na sekta ndogo ngapi za mishahara ya chini?"
    dead = [] if fidelity.repair_gn605a_sector_count(q117, live) != live else ["founding specimen (live eval_117, build e9e429e)"]
    print("INERT specimens:", dead)
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", pf.pairs_from_results()),
                       ("GOLD", pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))),
                       ("TRAINING", pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw")))):
        rows = [{"src": s, "q": q[:140], "old": a[:240], "new": fidelity.repair_gn605a_sector_count(q, a)[:240]} for s, q, a in pop if fidelity.repair_gn605a_sector_count(q, a) != a]
        res["populations"][label] = {"pairs": len(pop), "changed": len(rows), "rows": rows}
        print(f"\n{label}: {len(pop)} pairs, changed {len(rows)}")
        for r in rows:
            print(f"   {r['src']} | {r['q'][:70]}\n      OLD {r['old']!r}\n      NEW {r['new']!r}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d21_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
