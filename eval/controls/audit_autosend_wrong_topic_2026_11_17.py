# -*- coding: utf-8 -*-
"""WRONG-TOPIC AUDIT OF EVERY AUTO-SEND-ELIGIBLE ENGINE ROUTE (founder, 2026-11-17, after set #2 s2_15/s2_18: a dividend-withholding question was answered model-free by engine:corporate_tax with the CORPORATE
INCOME TAX rate, and that route was auto-send eligible).

ARMS (R12c, R17, R21):
  POPULATION  every committed question string that routes to an eligible engine AND carries neighbouring-topic vocabulary, answered OFFLINE by the real Orchestrator with a scripted model; only a reply with
              model_calls == 0 can auto-send, so only those are printed. READ BY HAND; a corpus is a LOWER bound (R21).
  PROBES      authored NEIGHBOURING-topic questions for each route (withholding, dividends, rent vs rent WHT, VAT vs VAT withholding, presumptive vs the income return, penalties, registration, other-country...) with the
              set of routes that is ACCEPTABLE; and CONTROLS (the route's own question, must still route). A probe that routes to an eligible engine it is not about FAILS.
A route that cannot be cleared stays OUT of auto-send (handler_core.AUTOSEND_EXCLUDED_ENGINE_ROUTES). corporate_tax goes back IN only on the founder's explicit word.

    python eval/controls/audit_autosend_wrong_topic_2026_11_17.py     -> eval/results/autosend_wrong_topic_audit_2026_11_17.json   (exit 1 if a probe fails)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ELIGIBLE = {"sdl", "nssf", "paye", "wcf", "minimum_wage", "vat_registration", "efd_requirement", "presumptive", "partnership_tax", "rent_wht", "corporate_tax"}
N = "none"
# (route under test, question, acceptable routes, why)
PROBES = [
    # ---- corporate_tax: the neighbours that were captured
    ("corporate_tax", "Kampuni yangu haijaorodheshwa kwenye soko la hisa la DSE. Nikigawa gawio kwa wanahisa, withholding tax yake ni 10%, si ndiyo?", {N}, "s2_15 verbatim: dividend WHT"),
    ("corporate_tax", "Nina kampuni ambayo imeorodheshwa DSE. Tukigawa gawio kwa wanahisa, withholding tax yake ni 5%, ndiyo?", {N}, "s2_18 verbatim: dividend WHT, DSE-listed (the listing cue fired)"),
    ("corporate_tax", "Kiwango cha kodi ya zuio ya gawio kwa kampuni zilizoorodheshwa DSE ni asilimia ngapi?", {N}, "dividend WHT rate"),
    ("corporate_tax", "Kampuni yangu ikigawa mgao kwa wanahisa, nikate kodi kiasi gani?", {N}, "'mgao' = dividend"),
    ("corporate_tax", "Dividend withholding tax kwa kampuni isiyoorodheshwa DSE ni ngapi?", {N}, "English dividend"),
    ("corporate_tax", "Kampuni ya Tanzania inapokea dividendi kutoka kampuni nyingine. Je, inatozwa kodi ya kampuni?", {N}, "dividend received"),
    ("corporate_tax", "Muda wa mwisho wa kuwasilisha return ya kodi ya mapato ya kampuni TRA ni lini?", {N}, "return deadline, not the rate"),
    ("corporate_tax", "Kampuni yangu imechelewa kuwasilisha tamko la kodi ya kampuni, faini ni ngapi?", {N}, "late-filing penalty"),
    ("corporate_tax", "Kampuni ambayo haikufanya biashara mwaka mzima hailazimiki kuwasilisha tamko la kodi ya kampuni kwa TRA, sivyo?", {N}, "nil return"),
    ("corporate_tax", "Kampuni inajaza return ya kodi ya mapato kwenye mfumo gani wa TRA?", {N}, "filing system"),
    ("corporate_tax", "Kodi ya zuio ya huduma za kitaalamu kwa kampuni ni asilimia ngapi?", {N}, "service-fee withholding"),
    ("corporate_tax", "Kampuni inayolipa royalty kwa kampuni ya nje inakata zuio kiasi gani?", {N}, "royalty withholding"),
    ("corporate_tax", "Kodi ya kampuni inapigwa faida ya mauzo ya hisa (capital gains) kiasi gani?", {N}, "capital gains (also out-of-scope: the OOC classifier refuses it before routing; WAS expected none only -- history)"),
    ("corporate_tax", "Kodi ya mapato ya kampuni ni asilimia ngapi?", {"corporate_tax"}, "CONTROL: the rate question"),
    ("corporate_tax", "Kampuni yangu imeorodheshwa DSE, tunalipa kodi ya mapato asilimia ngapi?", {"corporate_tax"}, "CONTROL: DSE-listed corporate rate (not a dividend)"),
    ("corporate_tax", "Kampuni yangu ina hasara miaka mitatu, je tunalipa AMT?", {"corporate_tax"}, "CONTROL: AMT"),
    # ---- rent_wht
    ("rent_wht", "Ninalipa pango la ofisi TZS 800,000 kwa mwezi, nimkate mwenye nyumba kiasi gani?", {"rent_wht"}, "CONTROL: rent withholding"),
    ("rent_wht", "Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye hesabu ya SDL?", {"sdl", N}, "eval_258: rent in the SDL base is an SDL question"),
    ("rent_wht", "Pango la ofisi TZS 800,000, VAT inaongezwa juu yake?", {N}, "VAT on rent, not rent WHT"),
    ("rent_wht", "Nina nyumba nimepangisha, kodi ya mapato ninayolipa mimi mwenye nyumba ni ngapi?", {N}, "the LANDLORD's own income tax, not the tenant's withholding"),
    ("rent_wht", "Kodi ya ardhi ninayolipa serikalini kwa kiwanja changu ni kiasi gani?", {N}, "land rent/ground rent to government"),
    ("rent_wht", "Mkataba wa pango la ofisi unatakiwa kuwa na stamp duty?", {N}, "stamp duty on a lease"),
    # ---- vat_registration
    ("vat_registration", "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT?", {"vat_registration"}, "CONTROL"),
    ("vat_registration", "VAT withholding kwa huduma ni asilimia ngapi?", {N, "fixed_statement"}, "VAT withholding is not VAT registration"),
    ("vat_registration", "Nimesajiliwa VAT, return ya VAT inawasilishwa lini?", {N}, "VAT return deadline"),
    ("vat_registration", "Nimesajiliwa VAT, nikichelewa kulipa faini ni ngapi?", {N}, "VAT late penalty"),
    ("vat_registration", "VAT ya kuagiza bidhaa kutoka nje (import VAT) ni ngapi?", {N}, "import VAT"),
    ("vat_registration", "Nimeuza kwa mkopo milioni 30, VAT inalipwa lini?", {N, "fixed_statement"}, "VAT time of supply"),
    ("vat_registration", "Kampuni yangu ina mauzo ya milioni 300, kodi ya mapato ya kampuni ni ngapi?", {N, "corporate_tax"}, "income tax of a company that also exceeds the VAT threshold"),
    ("vat_registration", "Mauzo yangu ni milioni 250, naweza kudai input VAT ya gari la kampuni?", {N}, "input VAT on a car"),
    # ---- presumptive
    ("presumptive", "Mauzo yangu ni milioni 50 kwa mwaka, kodi ya makadirio ni kiasi gani?", {"presumptive"}, "CONTROL"),
    ("presumptive", "Mauzo yangu ni milioni 50 kwa mwaka, return ya kodi ya mapato niwasilishe lini?", {N, "presumptive"}, "return deadline for a small trader (the presumptive engine states a rate, not a deadline)"),
    ("presumptive", "Mauzo yangu ni milioni 50, nikichelewa kulipa kodi ya makadirio faini ni ngapi?", {N, "presumptive"}, "late penalty"),
    ("presumptive", "Mauzo yangu ni milioni 50 kwa mwaka, lazima nijisajili VAT?", {"vat_registration"}, "the VAT neighbour of a turnover figure"),
    ("presumptive", "Mauzo yangu ni milioni 50 kwa mwaka, nahitaji EFD?", {"efd_requirement", N}, "the EFD neighbour of a turnover figure"),
    # ---- paye
    ("paye", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, PAYE ni ngapi?", {"paye"}, "CONTROL"),
    ("paye", "Nimemlipa mkandarasi TZS 5,000,000 kwa huduma, nikate withholding kiasi gani?", {N}, "contractor service WHT, not PAYE"),
    ("paye", "Mfanyakazi wangu amelipwa bonus ya TZS 2,000,000, kodi yake ni ngapi?", {N, "paye"}, "bonus: PAYE or a clarification, never another engine"),
    ("paye", "PAYE ikichelewa kulipwa faini ni kiasi gani?", {N}, "PAYE penalty"),
    ("paye", "Mshahara wa mfanyakazi ni TZS 800,000, nikate zuio la kodi?", {N, "paye"}, "'zuio' in a payroll sentence"),
    # ---- sdl / nssf / wcf
    ("sdl", "Nina wafanyakazi 12 na mishahara TZS 6,000,000, SDL ni kiasi gani?", {"sdl"}, "CONTROL"),
    ("sdl", "Nikiacha kulipa SDL kwa wafanyakazi wangu 15, nitatozwa faini kiasi gani?", {N, "sdl"}, "SDL penalty with a headcount"),
    ("sdl", "SDL inalipwa na nani, mwajiri au mfanyakazi?", {N, "sdl"}, "incidence"),
    ("nssf", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", {"nssf"}, "CONTROL"),
    ("nssf", "Nitapata pensheni kiasi gani nikistaafu NSSF?", {N}, "benefits, not contributions"),
    ("nssf", "Nikichelewa kulipa NSSF kwa mfanyakazi mwenye mshahara 800,000, faini ni ngapi?", {N, "nssf"}, "penalty beside a wage"),
    ("nssf", "Mafao ya uzazi NSSF ni kiasi gani?", {N}, "maternity benefit"),
    ("wcf", "Mishahara ya wafanyakazi wangu ni TZS 3,000,000 kwa mwezi, WCF ni ngapi?", {"wcf"}, "CONTROL"),
    ("wcf", "Mfanyakazi ameumia kazini, nitoe taarifa WCF ndani ya siku ngapi?", {"fixed_statement", N}, "accident reporting"),
    ("wcf", "Mfanyakazi aliyeumia kazini anastahili fidia ya kiasi gani?", {N}, "compensation benefit, not the contribution"),
    # ---- minimum_wage / efd / partnership
    ("minimum_wage", "Mshahara wa chini wa sekta ya kilimo ni kiasi gani?", {"minimum_wage", "fixed_statement", N}, "CONTROL-ish: sector minimum. 2026-11-22: was {minimum_wage, none}; the no-figure sector ask now routes to the sector-wage STATEMENT (fixed_statement), which is the right answer and is excluded from auto-send"),
    ("minimum_wage", "Mshahara wa chini Kenya ni kiasi gani?", {N}, "another country"),
    ("minimum_wage", "Mshahara wa chini wa wafanyakazi wa serikali ni kiasi gani?", {N, "minimum_wage"}, "public sector (500,000) vs the private order"),
    ("minimum_wage", "Nikimlipa mfanyakazi wa duka TZS 150,000 kwa mwezi, ni chini ya mshahara wa chini?", {"minimum_wage", N}, "compliance check"),
    ("efd_requirement", "TRA inaweza kunipiga faini kwa kutokuwa na EFD wakati mauzo yangu yako TZS 15M kwa mwaka?", {"efd_requirement"}, "CONTROL (a corpus row that routes; my first control phrasing, 'Je, EFD ni lazima kwangu...', did not route: a probe-wording miss recorded as history)"),
    ("efd_requirement", "Mashine ya EFD inagharimu kiasi gani?", {N}, "EFD price"),
    ("efd_requirement", "EFD yangu imeharibika, nifanye nini?", {N}, "EFD breakdown"),
    ("efd_requirement", "Mteja amenunua kwa shilingi 300, nimpe risiti ya EFD?", {N, "efd_requirement"}, "receipt on a small sale"),
    ("partnership_tax", "Ubia wetu unalipa kodi ya mapato kiasi gani?", {"partnership_tax"}, "CONTROL"),
    ("partnership_tax", "Mimi ni sole proprietor, kodi ya mapato yangu ni ngapi?", {N, "presumptive"}, "a sole trader is not a partnership"),
    ("partnership_tax", "Kampuni mbili zimeungana kwa ubia wa mradi (joint venture), kodi ya mapato inalipwaje?", {N, "partnership_tax", "corporate_tax"}, "a JV of companies"),
]

NEIGH = re.compile(r"gawio|dividend|mgao|zuio|withhold|royalt|riba|interest|mrabaha|huduma za kitaalamu|capital gain|return|tamko|pensheni|faini|adhabu|penalt|deadline|ubia|kuwasilisha", re.I)


def main():
    import sweep_parser_scale_order_2026_11_12 as sw
    from chike import routing
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator

    class _S(ModelBackend):
        def generate(self, prompt, params=None):
            return "MODEL_BODY"

    def offline(q):
        return Orchestrator(backend=_S(), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)

    bad, rows = [], []
    print("== PROBES ==")
    for route, q, ok, why in PROBES:
        got = routing.detect_intent(q)
        passed = got in ok
        rep = offline(q) if got in ELIGIBLE else None
        sendable = bool(rep is not None and rep.model_calls == 0 and not any(getattr(s, "needs_clarification", False) for s in rep.sub_answers))
        bad += [] if passed else [q]
        rows.append(dict(route=route, q=q, got=got, ok=sorted(ok), passed=passed, model_free_engine_reply=sendable, head=(rep.text[:160] if sendable else None), why=why))
        print(f"{'ok ' if passed else 'BAD'} [{route:<16}] got={got:<16} ok={sorted(ok)} {why} :: {q[:70]}" + (f"\n        -> {rep.text[:150]!r}" if sendable and not passed else ""))
    print("\n== POPULATION: corpus strings on an eligible route with neighbouring vocabulary, model-free replies only ==")
    qs, _ = sw.corpus()
    pop = []
    for q in sorted(set(qs)):
        if len(q) > 400:
            continue
        try:
            r = routing.detect_intent(q)
        except Exception:                                            # noqa: BLE001
            continue
        if r in ELIGIBLE and NEIGH.search(q):
            rep = offline(q)
            if rep.model_calls == 0:
                pop.append(dict(route=r, q=q, head=rep.text[:200]))
    for p in pop:
        print(f"  [{p['route']}] {p['q'][:130]}\n       -> {p['head'][:150]!r}")
    out = os.path.join(REPO, "eval", "results", "autosend_wrong_topic_audit_2026_11_17.json")
    json.dump({"probes": rows, "failed": bad, "population_model_free_neighbour_replies": pop}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{len(PROBES)} probes, {len(bad)} failed; population {len(pop)} model-free replies. wrote {out}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
