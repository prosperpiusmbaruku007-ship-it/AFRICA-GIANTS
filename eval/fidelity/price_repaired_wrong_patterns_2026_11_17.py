"""PRICE THE TWO wrong_patterns THAT WERE CORRUPT UNTIL 2026-11-17 (R39: a literal backspace where `\\b` was meant, so each compiled to a pattern that could never match).

`corporate_income_tax_return`[0] and `severance_pay_income_tax`[0] in scripts/locked_facts.json were INERT from the day they were written (2026-11-17, PROGRESS 4ao-4aq) until the permanent control-character test found
them. Now that they match, run them over every stored reply, gold answer and training pair and READ every hit: a hit in GOLD or in a correct reply is the alarm (the pattern is over-broad); a hit on a genuine wrong
claim is the corpus defect the pattern was blind to.

    python eval/fidelity/price_repaired_wrong_patterns_2026_11_17.py  ->  eval/results/price_repaired_wrong_patterns_2026_11_17.json
"""
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py"))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

FACTS = json.load(io.open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8"))
TARGETS = [("corporate_income_tax_return", 0), ("severance_pay_income_tax", 0)]


def main():
    pats = {(k, i): re.compile(FACTS[k]["wrong_patterns"][i], re.IGNORECASE) for k, i in TARGETS}
    assert all(chr(8) not in p.pattern for p in pats.values()), "a pattern still carries a backspace"
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        res[label] = {"pairs": len(pop), "hits": {}}
        print(f"\n{label}: {len(pop)} pairs")
        for key, rx in pats.items():
            rows = [{"src": s, "q": q[:140], "match": rx.search(a).group(0)[:160], "reply": a[:300]} for s, q, a in pop if rx.search(a)]
            res[label]["hits"][f"{key[0]}[{key[1]}]"] = rows
            print(f"  {key[0]}[{key[1]}]: {len(rows)} hit(s)")
            for r in rows[:12]:
                print(f"      {r['src']} | {r['q'][:70]}\n         match: {r['match']!r}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_repaired_wrong_patterns_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
