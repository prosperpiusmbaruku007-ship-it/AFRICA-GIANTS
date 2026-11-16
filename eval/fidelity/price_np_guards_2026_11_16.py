"""PRICE THE np_ BATCH GUARDS ON EVERY STORED REPLY, GOLD ANSWER AND TRAINING PAIR BEFORE THEY ARE CALLED SAFE (D-FIDELITY-7's lesson: green unit tests said nothing about the gold answer it would have blanked).

  D-FIDELITY-10'  annual-leave 29-60 and severance qualifying months: only NEW flags relative to the committed rule (old = the rule with the new limbs disabled)
  D-FIDELITY-13   licence-expiry date, record-keeping years, TIN deadline (constant_violations) and a derived levy amount (derived_levy_amount)

Populations as in price_followup_guards_2026_11_16.py. A flag in GOLD is the alarm; every flag is printed and read by hand. FOUNDING SPECIMENS must flag or the instrument is inert (R26/R39).

    python eval/fidelity/price_np_guards_2026_11_16.py       -> eval/results/price_np_guards_2026_11_16.json
"""
import importlib.util, io, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity                                                  # noqa: E402

spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py")); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
PROBES = [json.loads(l) for l in io.open(os.path.join(HERE, "constant_guards_probes_2026_11_16.jsonl"), encoding="utf-8") if l.strip()]


def d10_new(q, a):
    """Reasons from the two NEW limbs only."""
    return [r for _, r in fidelity.fixed_figure_violations(q, a) if r.startswith("severance/qualifying-months") or (r.startswith("annual_leave/value:") and 28 < int(r.split(":")[1]) < 61)]


def flags(q, a):
    out = {}
    r = d10_new(q, a)
    if r:
        out["D10_new"] = r
    c = fidelity.constant_violations(q, a)
    if c:
        out["D13_constant"] = [x[1] for x in c]
    d = fidelity.derived_levy_amount(q, a)
    if d:
        out["D13_amount"] = [str(x[0]) for x in d]
    return out


def main():
    dead = []
    for p in PROBES:
        if p["expect"] == "flag" and p["id"] in ("cg_01", "cg_02", "cg_03", "cg_04", "cg_05", "cg_06"):
            hit = bool(flags(p["question"], p["body"]))
            print(f"[{'FLAGS' if hit else 'INERT!'}] {p['id']} {p['guards_against'][:70]}")
            if not hit:
                dead.append(p["id"])
    stored = pf.pairs_from_results()
    gold = pf.pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pf.pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    res = {"specimens_inert": dead, "populations": {}}
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        rows = []
        for src, q, a in pop:
            f = flags(q, a)
            if f:
                rows.append({"src": src, "q": q[:200], "reply": a[:400], "flags": f})
        res["populations"][label] = {"pairs": len(pop), "flags": len(rows), "rows": rows}
        print(f"{label:<15} {len(pop):>6} pairs   flags {len(rows):>3}")
    out = os.path.join(REPO, "eval", "results", "price_np_guards_2026_11_16.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for label, d in res["populations"].items():
        for r in d["rows"]:
            print(f"--- {label} {r['src']} {r['flags']}\n   Q: {r['q'][:150]}\n   A: {r['reply'][:300]!r}")
    print("wrote", out)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
