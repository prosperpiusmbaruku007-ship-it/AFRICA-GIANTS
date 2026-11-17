"""PRICE D-FIDELITY-22 (first priced as a CANDIDATE; founder approved building it 2026-11-17): a sentence about VAT withholding (zuio) that puts 1 September 2025 on its START / implementation date. The fixed rule: VAT withholding on goods (3%) and
services (6%) is effective 1 JULY 2025 (Finance Act 2025, locked facts vat_withholding_goods / vat_withholding_services, served index rows 16-17), with no deferral; the 1 September 2025 date belongs to the B2C e-payment VAT
(16%), a different rule. Specimen: the live reply to eval_041 ("... ulianza rasmi tarehe 1 Julai 2025 ... lakini utekelezaji wake ulicheleweshwa hadi 1 Septemba 2025").

Nothing is wired. Every hit is READ: a hit that is a CORRECT sentence (it names the B2C e-payment rule, or negates the date) is the alarm.

    python eval/fidelity/price_vat_withholding_sept_2026_11_17.py  ->  eval/results/price_vat_withholding_sept_2026_11_17.json
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
sys.path.insert(0, REPO)
from chike import fidelity  # noqa: E402

WH = re.compile(r"vat\s+withholding|vat\s+ya\s+zuio|zuio\s+la\s+vat|zuio\s+wa\s+vat|utaratibu\s+wa\s+zuio|withholding\s+(?:vat|agent)", re.IGNORECASE)
SEP = re.compile(r"1\s+septemba(?:\s+2025)?|septemba\s+1|1(?:st)?\s+september(?:\s+2025)?|september\s+1", re.IGNORECASE)
B2C = re.compile(r"e-?payment|kidijitali|digital|b2c|mteja\s+wa\s+mwisho|16\s*%|asilimia\s+16|malipo\s+ya\s+kielektroniki", re.IGNORECASE)
NEG = re.compile(r"(?<![a-z])(?:si|sio|siyo|sivyo|hakuna|haikuanza|not|no)(?![a-z])", re.IGNORECASE)
SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
SPECIMEN_Q = "Je, utaratibu wa VAT withholding wa Finance Act 2025 ulianza kutumika tangu 1 Januari 2025?"


START = re.compile(r"cheleweshw|ulianza|ilianza|kuanza|kuanzia|ulipoanza|utekelezaji|implementation|effective|delayed|postponed|deferred|hadi", re.IGNORECASE)


def hits(q, a):
    """the REAL guard (D-FIDELITY-22, wired 2026-11-17); the candidate this file priced as a proposal is now fidelity.vat_withholding_start_misstated"""
    return [sent for topic, sent in fidelity.body_contradicts_d16(q, a) if topic == "vat_withholding_start_date"]


def main():
    live = next(r for r in json.load(io.open(os.path.join(REPO, "eval", "results", "targeted_gate4_2026_11_17.json"), encoding="utf-8"))["rows"] if r["id"] == "eval_041")["reply"]
    print("specimen (the live eval_041 reply) hits:", hits(SPECIMEN_Q, live))
    res = {"specimen": hits(SPECIMEN_Q, live), "populations": {}}
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        rows = [{"src": s, "q": q[:140], "sentences": hits(q, a)} for s, q, a in pop if hits(q, a)]
        res["populations"][label] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
        print(f"\n{label}: {len(pop)} pairs, flags {len(rows)}")
        for r in rows:
            print(f"   {r['src']} | {r['q'][:70]}\n      {r['sentences']}")
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_vat_withholding_sept_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
