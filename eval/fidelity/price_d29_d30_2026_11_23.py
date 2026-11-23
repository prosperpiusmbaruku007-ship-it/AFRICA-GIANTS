"""PRICE D-FIDELITY-29 (NSSF stated as due by the 7th) and D-FIDELITY-30 (a Kenyan "P9" asserted as a Tanzanian document) over every stored reply, gold answer and training pair BEFORE they are called safe (R22, R25).
A hit in GOLD is the alarm; every hit is READ. Founding specimens are the live replies of build b96e8a8 (eval/results/sdl_three_routes_live_2026_11_23.json), VERBATIM, and must flag or the run exits 1 (R26: a control that cannot fire).

    python eval/fidelity/price_d29_d30_2026_11_23.py  ->  eval/results/price_d29_d30_2026_11_23.json
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

LIVE = os.path.join(REPO, "eval", "results", "sdl_three_routes_live_2026_11_23.json")


def specimen(q_part, rows):
    for r in rows:
        q = r.get("question") or r.get("q") or ""
        if q_part in q:
            return q, (r.get("reply") or r.get("text") or "")
    raise SystemExit(f"specimen not found: {q_part}")


def main():
    live = json.load(io.open(LIVE, encoding="utf-8"))
    live = live.get("rows") or live.get("results") or live
    assert isinstance(live, list) and len(live) >= 20, type(live)     # a loader returning nothing must fail, not pass vacuously (R20)
    q29, r29 = specimen("SDL na NSSF ni kiasi gani", live)
    q30, r30 = specimen("SDL audit", live)
    checks = {"D29": (lambda q, a: fidelity.nssf_deadline_misstated(q, a)), "D30": (lambda q, a: fidelity.p9_asserted(a))}
    dead = []
    if not checks["D29"](q29, r29):
        dead.append("D29 founding specimen (live compute reply, b96e8a8)")
    if not checks["D30"](q30, r30):
        dead.append("D30 founding specimen (live SDL-audit reply, b96e8a8)")
    print("INERT specimens:", dead)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for guard, fn in checks.items():
        for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
            rows = [{"src": s, "q": q[:160], "hits": fn(q, a), "reply": a[:300]} for s, q, a in pop if fn(q, a)]
            res["populations"][f"{guard} {label}"] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
            print(f"\n{guard} {label}: {len(pop)} pairs, flags {len(rows)}")
            for r in rows:
                print(f"   {r['src']} | {r['q'][:80]}\n      {r['hits']}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d29_d30_2026_11_23.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
