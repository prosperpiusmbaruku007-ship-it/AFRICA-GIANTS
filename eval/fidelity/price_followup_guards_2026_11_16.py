"""PRICE THE TWO NEW GUARD FAMILIES ON EVERY STORED REPLY BEFORE THEY ARE WIRED (R22 / the D-FIDELITY-7 lesson: 22 green unit tests said nothing about the gold answer they would have blanked).

  D-FIDELITY-10 extension  voluntary VAT registration / WCF accident reporting trigger / VAT withholding mixed supply  (fidelity.fixed_figure_violations, those three topics)
  D-FIDELITY-11            a PAYE band edge assigned to the wrong band                                               (fidelity.body_misnames_paye_band)

POPULATIONS (each reported separately; a flag in GOLD is the alarm):
  STORED REPLIES   every (question, reply) pair in eval/results/*.json -- 53 artifacts of live and gate replies
  GOLD             every gold answer of the three gate corpora and the probe sets, judged against its OWN question
  TRAINING         every (instruction/question, output/answer) pair of datasets/tier1a/{cleaned_pairs,sft_shaped_pairs,sft}
  FOUNDING SPECIMENS  the live wrong replies (verbatim, from the follow-up deploy artifact): each MUST flag, or the instrument is inert (R26/R39)

    python eval/fidelity/price_followup_guards_2026_11_16.py
Artifact: eval/results/price_followup_guards_2026_11_16.json.  Exit 1 if a founding specimen does not flag.
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity, routing                                        # noqa: E402

NEW_TOPICS = {"vat_voluntary_registration", "wcf_accident_reporting", "vat_withholding_mixed_supply"}
QK = ("question_sw", "q", "question", "prompt", "instruction")
AK = ("generated", "reply", "answer", "response", "text", "output", "answer_sw", "correct_answer_sw")


def pairs_from_results():
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                                # noqa: BLE001
            continue
        rows = d.get("rows") if isinstance(d, dict) else d
        if not (isinstance(rows, list) and rows and isinstance(rows[0], dict)):
            continue
        for r in rows:
            q = next((r[k] for k in QK if isinstance(r.get(k), str)), None)
            a = next((r[k] for k in ("generated", "reply", "answer", "response", "text") if isinstance(r.get(k), str)), None)
            if q and a:
                out.append((os.path.basename(f), q, a))
    return out


def pairs_from_jsonl(globs, akeys, qkeys=QK):
    out = []
    for g in globs:
        for f in sorted(glob.glob(os.path.join(REPO, g), recursive=True)):
            for line in io.open(f, encoding="utf-8", errors="replace"):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                q = next((r[k] for k in qkeys if isinstance(r.get(k), str)), None)
                a = next((r[k] for k in akeys if isinstance(r.get(k), str)), None)
                if q and a:
                    out.append((os.path.relpath(f, REPO).replace("\\", "/"), q, a))
    return out


def flag(q, a):
    v = [x for x in fidelity.fixed_figure_violations(q, a) if x[0] in NEW_TOPICS]
    paye = fidelity.paye_band_misnamings(a)
    return v, paye


def main():
    stored = pairs_from_results()
    gold = pairs_from_jsonl(["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl"], ("correct_answer_sw", "expected_behavior", "correct"))
    train = pairs_from_jsonl(["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"], ("output", "answer_sw"))
    live = json.load(io.open(os.path.join(REPO, "eval", "results", "followup_deploy_live_2026_11_16_firstrun.json"), encoding="utf-8"))["rows"]
    diag = json.load(io.open(os.path.join(REPO, "eval", "results", "followup_deploy_live_diagnostic_2026_11_16.json"), encoding="utf-8"))
    specimens = [("voluntary VAT", r["q"], r["reply"]) for r in live if "kujisajili VAT kwa hiari ukiwa" in r["q"] or "sijafikia kiwango" in r["q"]]
    specimens += [("WCF trigger", q, d["reply"]) for q, d in diag.items() if "inaanza kuhesabiwa" in q]
    specimens += [("mixed supply (rate)", q, d["reply"]) for q, d in diag.items() if "mauzo ya bidhaa na huduma pamoja" in q]
    paye_specimen = ("PAYE band narration", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi. PAYE ni kiasi gani?",
                     "Kumbuka: TZS 760,000 ni kiwango cha pili cha PAYE (8%), na TZS 40,000 ni ziada juu ya hiyo.")
    # the PAYE narration quoted verbatim in the live artifact (truncated at 220 chars in the console but stored whole)
    for r in json.load(io.open(os.path.join(REPO, "eval", "results", "followup_deploy_live_2026_11_16_firstrun.json"), encoding="utf-8"))["rows"]:
        if "PAYE ni k" in r["q"] and "760,000" in r["reply"]:
            paye_specimen = ("PAYE band narration", r["q"], r["reply"])
    specimens.append(paye_specimen)
    res = {"populations": {}, "specimens": []}
    dead = []
    for name, q, a in specimens:
        v, p = flag(q, a)
        hit = bool(v or p)
        res["specimens"].append({"specimen": name, "flagged": hit, "reasons": [x[1] for x in v] + [str(x) for x in p]})
        print(f"[{'FLAGS' if hit else 'INERT!'}] {name}: {q[:60]}")
        if not hit:
            dead.append(name)
    for label, pop in (("STORED REPLIES", stored), ("GOLD", gold), ("TRAINING", train)):
        flags = []
        for src, q, a in pop:
            v, p = flag(q, a)
            if v or p:
                flags.append({"src": src, "q": q[:140], "reply": a[:260], "reasons": [x[1] for x in v] + [str(x) for x in p]})
        res["populations"][label] = {"pairs": len(pop), "flags": len(flags), "rows": flags}
        print(f"{label:<15} {len(pop):>6} pairs  {len(flags):>3} flags")
        for f in flags[:25]:
            print(f"    {f['src'][:44]:<44} {f['q'][:60]!r} -> {f['reasons'][0][:70]}")
    io.open(os.path.join(REPO, "eval", "results", "price_followup_guards_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
    if dead:
        print("INERT specimens:", dead)
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
