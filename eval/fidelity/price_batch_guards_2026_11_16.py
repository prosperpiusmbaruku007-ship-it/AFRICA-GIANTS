"""PRICE THE 2026-11-16 SAFETY GUARDS ON EVERY STORED REPLY, GOLD ANSWER AND TRAINING PAIR BEFORE THEY ARE CALLED SAFE (the D-FIDELITY-7 lesson: green unit tests said nothing about the gold answer it would have blanked).

  D-FIDELITY-12   a turnover above the VAT threshold told it need not register       fidelity.body_denies_vat_registration_above_threshold(question, body)
  D-FIDELITY-7'   the DELTA of (question-subject fallback + the `hapana,` negation narrowing) against the OLD behaviour (old regex, no question) -- only NEW flags are reported

Populations as in price_followup_guards_2026_11_16.py (it is imported for them). A flag in GOLD is the alarm. FOUNDING SPECIMENS must flag or the instrument is inert (R26/R39).

    python eval/fidelity/price_batch_guards_2026_11_16.py       -> eval/results/price_batch_guards_2026_11_16.json
"""
import importlib.util, io, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity                                                  # noqa: E402

spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py")); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
OLD_NEG = re.compile(r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhakuna\b|\bhaina\b|\bhakina\b|\bhamna\b|\bhapana\b|\bnot\b|\bno\b|\bnever\b)[\s:,—–-]*(?:tzs\s*)?$", re.IGNORECASE)
NEW_NEG = fidelity._THRESHOLD_NEGATION


def old_flag(a):
    fidelity._THRESHOLD_NEGATION = OLD_NEG
    try:
        return bool(fidelity.stated_wrong_thresholds(a))
    finally:
        fidelity._THRESHOLD_NEGATION = NEW_NEG


def flags(q, a):
    f12 = fidelity.body_denies_vat_registration_above_threshold(q, a)
    f7new = bool(fidelity.stated_wrong_thresholds(a, q)) and not old_flag(a)
    return f12, f7new


SPEC = [("D-FIDELITY-12 eval_318 VAT limb", "je nasajili VAT kama mapato ni TZS 205,000,000?",
         "Hapana, kwa mujibu wa sheria, kizingiti sahihi cha kusajili VAT ni TZS 200,000,000 tu. Mapato ya TZS 205,000,000 hayazidi kizingiti hicho, hivyo huhitajiwi kusajili VAT. Thibitisha na tra.go.tz.", 0),
        ("D-FIDELITY-7' eval_355", "Mauzo yangu ni TZS 10,999,000 kwa mwaka, je EFD ni lazima kwangu?", "Hapana, kwa sababu umefika chini ya kizingiti cha TZS 11M. Thibitisha na TRA (tra.go.tz).", 1)]


def main():
    dead = []
    for name, q, a, i in SPEC:
        hit = flags(q, a)[i]
        print(f"[{'FLAGS' if hit else 'INERT!'}] {name}")
        if not hit:
            dead.append(name)
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        r12, r7 = [], []
        for src, q, a in pop:
            f12, f7 = flags(q, a)
            if f12:
                r12.append({"src": src, "q": q[:160], "reply": a[:300]})
            if f7:
                r7.append({"src": src, "q": q[:160], "reply": a[:300]})
        res["populations"][label] = {"pairs": len(pop), "D12": {"flags": len(r12), "rows": r12}, "D7_delta": {"flags": len(r7), "rows": r7}}
        print(f"{label:<15} {len(pop):>6} pairs   D-FID-12 {len(r12):>3}   D-FID-7 delta {len(r7):>3}")
        for tag, rows in (("D12", r12), ("D7Δ", r7)):
            for f in rows[:30]:
                print(f"   {tag} {f['src'][:40]:<40} {f['q'][:50]!r} -> {f['reply'][:110]!r}")
    io.open(os.path.join(REPO, "eval", "results", "price_batch_guards_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
