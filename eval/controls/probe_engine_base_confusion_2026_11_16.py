# -*- coding: utf-8 -*-
"""DOES ANY ENGINE'S EXTRACTOR READ A FIGURE THAT IS NOT ITS BASE AS ITS BASE? (2026-11-16, after eval_257: "Mapato ya biashara yangu yalifika TZS 12,300,000 ... NSSF ya jumla ni ngapi?"
was computed as 20% of business income, by the NSSF engine, with no model word in the reply -- the shape that auto-sends after 15 minutes.)

Each probe carries ONE figure that is not the engine's base (profit, loan, capital, cost, income, a customer's payment ...). EXPECT: no engine computation from it (a clarification, a refusal or a fact
answer are all fine). BAD = a computation exists. CONTROLS carry the right base and MUST still compute -- a rule that blocks everything is not a fix (R26). Regex extraction only: the
model-fallback extractor is not reachable offline (the backend returns ""), which is stated here rather than discovered later.

    python eval/controls/probe_engine_base_confusion_2026_11_16.py
Artifact: eval/results/engine_base_confusion_probe_2026_11_16.json.  Exit 1 if any probe is BAD or any control fails to compute.
"""
import io, json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike.model_abstraction import ModelBackend           # noqa: E402
from chike.orchestrator import Orchestrator                # noqa: E402


class _B(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


NON_WAGE = [
    "Mapato ya biashara yangu yalifika TZS 12,300,000 mwezi jana, {L} ni ngapi?",
    "Biashara imepata pato la TZS 9,000,000 mwezi huu, {L} ni ngapi?",
    "Kipato cha duka letu ni TZS 7,500,000 kwa mwezi, {L} yake ni ngapi?",
    "Nimekopa benki mkopo wa TZS 20,000,000, {L} ni ngapi?",
    "Faida yangu halisi ni TZS 3,000,000, {L} ni ngapi?",
    "Gharama zangu za mafuta ni TZS 4,000,000 kwa mwezi, {L} ni ngapi?",
    "Bajeti ya kampuni ni TZS 50,000,000 kwa mwaka, {L} ni ngapi?",
    "Mteja amenilipa TZS 6,000,000 kwa oda, {L} ni ngapi?",
    "Nina amana ya TZS 15,000,000, {L} ni ngapi?",
    "Ada ya shule ni TZS 2,500,000, {L} ni ngapi?",
    "Mapato ya kampuni yetu ni TZS 40,000,000, {L} ni ngapi?",
    "Mapato ya duka ni TZS 5,000,000 kwa mwezi, {L} ni ngapi?",
]
LEVIES = ("NSSF", "SDL", "WCF", "PAYE")
OTHER = [  # (engine, question)
    ("vat_registration", "Nina mtaji wa TZS 250,000,000, je nijisajili VAT?"),
    ("vat_registration", "Faida yangu ni TZS 250,000,000 kwa mwaka, je ni lazima nijisajili VAT?"),
    ("vat_registration", "Nimekopa TZS 250,000,000, je ni lazima nijisajili VAT?"),
    ("presumptive", "Faida yangu ni TZS 20,000,000 kwa mwaka, nalipa kodi ya makadirio kiasi gani?"),
    ("presumptive", "Mtaji wangu ni TZS 20,000,000, nalipa kodi ya makadirio kiasi gani?"),
    ("rent_wht", "Mauzo yangu ni TZS 10,000,000, kodi ya zuio ya pango ni ngapi?"),
    ("rent_wht", "Nimekopa TZS 10,000,000, withholding tax ya pango ni kiasi gani?"),
    ("minimum_wage", "Mapato ya biashara yangu ni TZS 300,000 kwa mwezi, je ni chini ya mshahara wa chini wa mlinzi?"),
    ("corporate_tax", "Mtaji wa kampuni ni TZS 100,000,000, kodi ya kampuni ni ngapi?"),
]
CONTROLS = [("nssf", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?"),
            ("paye", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, PAYE ni ngapi?"),
            ("paye", "Mapato yangu ya ajira ni TZS 800,000 kwa mwezi, PAYE ni ngapi?"),
            ("wcf", "Mishahara ya wafanyakazi wangu ni TZS 4,000,000 kwa mwezi, WCF ni ngapi?"),
            ("sdl", "Nina wafanyakazi 12 na mishahara TZS 6,000,000 kwa mwezi, SDL ni ngapi?"),
            ("vat_registration", "Mauzo yangu ni milioni 250 kwa mwaka, je ni lazima nijisajili VAT?")]


def computed(q):
    r = Orchestrator(backend=_B(), retriever=lambda *_a, **_k: [], system_prompt="x").answer(q)
    # BAD = an engine produced a computation WITH AN AMOUNT. A computation object with amount None is an applicability/refusal verdict ("Kiasi ulichotaja si mshahara ...") or a rate
    # statement -- the wrong-base veto working, not the defect.
    any_comp = any(s.computation is not None for s in r.sub_answers)
    comps = [s.computation for s in r.sub_answers if s.computation is not None and getattr(s.computation, "amount", None) is not None]
    return bool(comps), any_comp, (r.text or "")[:160].replace("\n", " ")


def main():
    rows, bad = [], 0
    probes = [(lv, t.format(L=lv)) for t in NON_WAGE for lv in LEVIES] + OTHER
    for eng, q in probes:
        c, _any, t = computed(q)
        rows.append({"kind": "probe", "engine": eng, "q": q, "computed": c, "text": t})
        bad += c
        if c:
            print(f"BAD  [{eng}] {q}\n       -> {t}")
    ctl_fail = 0
    for eng, q in CONTROLS:
        _amt, c, t = computed(q)
        rows.append({"kind": "control", "engine": eng, "q": q, "computed": c, "text": t})
        ctl_fail += (not c)
        print(f"{'ok  ' if c else 'FAIL'} control [{eng}] {q}")
    print(f"\n{len(probes)} probes, BAD {bad}; {len(CONTROLS)} controls, failed to compute {ctl_fail}")
    io.open(os.path.join(REPO, "eval", "results", "engine_base_confusion_probe_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps({"probes": len(probes), "bad": bad, "controls_failed": ctl_fail, "rows": rows}, ensure_ascii=False, indent=1))
    return 1 if (bad or ctl_fail) else 0


if __name__ == "__main__":
    sys.exit(main())
