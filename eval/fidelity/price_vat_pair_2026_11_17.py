"""PRICE THE TWO-FIGURE VAT READER (routing.turnover_pair_with_periods) over every question we hold, BEFORE it is called safe (R22). Every question it would answer instead of asking is READ.

    python eval/fidelity/price_vat_pair_2026_11_17.py  ->  eval/results/price_vat_pair_2026_11_17.json
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
from chike import routing, rules_engine  # noqa: E402
from chike import swahili_numbers as swn  # noqa: E402

spec = importlib.util.spec_from_file_location("_sw", os.path.join(REPO, "eval", "controls", "sweep_d18_routes_2026_11_17.py"))
sw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sw)


def main():
    qs = sw.questions()
    hits, reach = [], 0
    for q, src in qs.items():
        pair = routing.turnover_pair_with_periods(q)
        if pair is None:
            continue
        intent = routing.detect_intent(q)
        sole = swn.sole_plausible_amount(q)
        hits.append({"q": q, "src": src, "intent": intent, "annual": int(pair[0]), "six_month": int(pair[1]), "reaches_engine_pair_path": intent == "vat_registration" and sole is None and routing.turnover_with_local_period(q) is None})
    print(f"{len(qs)} questions swept; the reader returns a pair for {len(hits)}; {sum(h['reaches_engine_pair_path'] for h in hits)} of them reach the engine's pair path")
    for h in hits:
        verdict = rules_engine.vat_registration_both_limbs(h["annual"], h["six_month"])
        print(f"  [{h['src']}] intent={h['intent']} reaches={h['reaches_engine_pair_path']} annual={h['annual']:,} six={h['six_month']:,} -> {'REGISTER' if verdict.applicable else 'not yet'} | {h['q'][:130]}")
        h["verdict"] = "register" if verdict.applicable else "below both"
    json.dump({"questions_swept": len(qs), "hits": hits}, io.open(os.path.join(REPO, "eval", "results", "price_vat_pair_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
