# -*- coding: utf-8 -*-
"""Apply the founder-approved batch 2026-11-24b to scripts/locked_facts.json and data/source_documents/MANIFEST.json (R18: committed with its result).
Four NEW facts (appended, so they are the last trailing index rows) and two in-place WCF corrections (R27: amend the named fields, leave every other field).
The NSSF fact is HELD by the founder (the page image of the 'wages' definition reads 'in respect of living')."""
import hashlib
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FACTS = os.path.join(REPO, "scripts", "locked_facts.json")
MAN = os.path.join(REPO, "data", "source_documents", "MANIFEST.json")
D = "2026-11-24"

NEW = {
    "medicines_vat_exempt": {
        "fact": ("Dawa muhimu za binadamu na za mifugo, dawa (drugs), vifaa tiba na vifungashio vyake VILIVYOIDHINISHWA na Waziri husika ni MSAMAHA wa VAT, si zero-rated (Sheria ya VAT). Si kila dawa au kifaa: kinahitaji idhini ya Waziri; vifungashio vinahusika tu vikiwa vimeundwa mahsusi kufungia bidhaa za dawa. "
                 "Msamaha maana yake VAT haitozwi kwenye mauzo hayo; mkopo wa input VAT unatolewa kwa manunuzi yaliyofanywa kwa ajili ya kutoa bidhaa au huduma zinazotozwa VAT (taxable supplies), na kwa matumizi ya sehemu hugawanywa kwa fomula. "
                 "Zero-rated (0%) ni aina nyingine, kama mauzo ya nje; bidhaa ikiwa na msamaha na zero-rating kwa pamoja inakuwa zero-rated (kwa mfano dawa zinazouzwa nje ya nchi). Thibitisha na TRA. "
                 "(English: essential human and veterinary medicine, drugs, medical equipment and packaging approved by the Minister are EXEMPT, not zero-rated; a supply that is both exempt and zero-rated is zero-rated, so exported medicines are zero-rated.)"),
        "correct_value": "medicines, drugs, medical equipment and packaging approved by the Minister: VAT-EXEMPT (not zero-rated); exempt + zero-rated = zero-rated (exports)",
        "wrong_patterns": [r"(?:dawa|vifaa tiba|medicines?|medical equipment)(?![^.;:]{0,40}(?:si|not)\s+zero)[^.;:]{0,50}\bzero[- ]rated(?!\s+(?:kwa\s+pamoja|ni\s+aina))"],
        "primary_source": "Value Added Tax Act, Cap.148 R.E.2023, Schedule (made under section 6(1)), Part I (supplies and imports exempt from VAT), item 7 'Medicine or pharmaceutical products'; s.5(3) (exempt + zero-rated = zero-rated); s.74(1)-(2) (partial input tax credit)",
        "verified_by": ("Direct read 2026-11-24 of data/source_documents/tra/vat_act_cap148_re2023.pdf (assert_edition 'R.E. 2023', sha256 f2354897...). Item 7 verbatim: 'Medicine or pharmaceutical products. 1. Essential Human and veterinary medicine, drugs, medical equipment and packaging material which have been approved by the responsible Minister. Provided that, the packaging material is specifically designed for packing pharmaceutical products.' "
                        "s.5(3): 'Where a supply is both exempt and zero-rated, the supply shall be zero-rated'. APPORTIONMENT (quoted at the founder's request): s.74(1) 'This section shall apply to input tax incurred on goods, services, or immovable property acquired or imported ... by a taxable person in the course of the person's economic activity but only partly for the purpose of making taxable supplies.' s.74(2) 'The amount of the credit allowed for input tax to which this section relates shall be calculated according to the following formula - I x T / A' (I the input tax, T the value of taxable supplies in the period, A the value of all supplies). "
                        "R29 amendment check: Finance Acts 2024/2025/2026 do not name item 7 (FA2025 s.135 amends Part I items 1, 2, 3, 9, 13, 15, 17, 21, 27, 31, 34; FA2026 s.96 items 3, 4, 6, 27, 31(b)). Corrects live replies of build 37cdf9d that called medicines and vifaa tiba 'zero-rated' (eval/results/followup_deploy_live_2026_11_24.json)."),
        "verified_date": D, "verified_as_at": D, "status": "CONFIRMED",
    },
    "paye_base_employment_income": {
        "fact": ("PAYE hukatwa kwenye MAPATO YA AJIRA ya mfanyakazi, si mshahara wa msingi pekee (Sheria ya Kodi ya Mapato). Yanajumuisha mshahara, malipo badala ya likizo, ada, kamisheni, bonasi, kiinua mgongo (gratuity) na posho yoyote ya safari, malazi, burudani au nyingine, pamoja na faida zisizo za fedha (benefits in kind) zilizokokotolewa kisheria. "
                 "Vichache vimeondolewa kisheria, kwa mfano posho inayorudisha tu gharama zilizotumika kikamilifu kuzalisha mapato, na faida ya matumizi ya gari ambapo mwajiri hadai makato wala nafuu kuhusu umiliki, matengenezo au uendeshaji wa gari hilo; orodha kamili iko kwenye Sheria. "
                 "Tofauti na SDL: kwa SDL faida zisizo za fedha hazijatajwa kwenye Sheria. Thibitisha na TRA. "
                 "(English: PAYE is withheld on employment income, not basic salary only; allowances and quantified benefits in kind are included; a few items are excluded.)"),
        "correct_value": "PAYE base = employment income (wages, salary, bonuses, commissions, allowances, quantified benefits in kind), not basic salary only; a few statutory exclusions",
        "wrong_patterns": [r"PAYE[^.;]{0,90}(?<!si )(?<!not )(?:mshahara wa msingi pekee|basic salary only|basic salary alone)"],
        "primary_source": "Income Tax Act, Cap.332 R.E.2023, s.7(2)-(3) (income from employment) and s.104(1) (withholding by a resident employer)",
        "verified_by": ("Direct read 2026-11-24 of data/source_documents/tra/income_tax_act_cap332_re2023.pdf (assert_edition 'R.E. 2023', sha256 a128d329...). s.7(2) includes '(a) payments of wages, salary, payment in lieu of leave, fees, commissions, bonuses, gratuity or any subsistence travelling entertainment or other allowance received in respect of employment or service rendered' and '(f) other payment made in respect of employment including benefits in kind quantified in accordance with section 27'. "
                        "EXCLUSIONS quoted: s.7(3)(d) 'any subsistence, travelling, entertainment or other allowance that represents solely the reimbursement to the recipient of any amount expended by him wholly and exclusively in the production of his income from his employment or services rendered'; s.7(3)(e) 'benefits derived from the use of motor vehicle where the employer does not claim any deduction or relief in relation to the ownership, maintenance or operation of the vehicle' (page 578 of the R.E.2023 print). "
                        "s.104(1): 'A resident employer who makes a payment that is to be included in calculating the chargeable income of an employee from the employment shall withhold income tax from the payment'. R29: neither s.7 nor s.104 is amended by Finance Acts 2024/2025/2026 (checked under both numberings). Corrects the live reply 'PAYE inakokotolewa kwa msingi wa mshahara wa msingi pekee (basic salary)' (build 37cdf9d). No locked fact stated the PAYE base before this one."),
        "verified_date": D, "verified_as_at": D, "status": "CONFIRMED",
    },
    "sdl_deemed_month_of_payment": {
        "fact": ("SDL ya mwezi inakokotolewa kwa jumla ya mishahara ghafi ya mwezi huo. Malipo yoyote yaliyolipwa kwa kazi iliyofanywa mwezi MWINGINE yanahesabiwa kama ya mwezi AMBAO yamelipwa (Sheria ya Elimu na Mafunzo ya Ufundi). Kwa hiyo SDL ya Januari ni ya malipo yaliyolipwa Januari, hata kama sehemu yake ni ya kazi ya Desemba. Thibitisha na TRA. "
                 "(English: an amount paid for work done in another month is deemed to belong to the calendar month in which it is PAID.)"),
        "correct_value": "payments are deemed emoluments of the calendar month in which they are PAID, even if for work of another month",
        "wrong_patterns": [r"SDL[^.;]{0,100}(?:inahesabiwa|hukokotolewa|huhesabiwa)[^.;]{0,60}(?:mwezi ambao kazi ilifanywa|mwezi wa kazi|mwezi husika tu)"],
        "primary_source": "Vocational Education and Training Act, Cap.82 R.E.2023, s.14(2)-(3)",
        "verified_by": ("Direct read 2026-11-24 of data/source_documents/tra/veta_act_cap82_re2023.pdf (assert_edition 'R.E. 2023'). s.14(3) last limb verbatim: '...and any amount paid in respect of employment or services rendered by the employee in any month other than the month in which it is paid, shall be deemed to be emoluments in respect of the calendar month in which it is paid.' s.14(2): the levy is 3.5% of the 'total gross monthly emoluments payable by the employer to his employees in respect of that month'. "
                        "R29: unamended by Finance Acts 2024/2025/2026 (FA2024 s.112 and FA2026 s.98 amend s.19(1) only). Replaces the live reply 'inahesabiwa kwa mishahara ya mwezi husika tu - si Desemba wala miezi mingine' (build 37cdf9d), which the deeming limb contradicts."),
        "verified_date": D, "verified_as_at": D, "status": "CONFIRMED",
    },
    "wcf_contribution_base": {
        "fact": ("Msingi wa michango ya WCF ni MAPATO YA KILA MWAKA (annual earnings) ya wafanyakazi: kiasi anacholipa mwajiri kwa wafanyakazi wake, kinachojumuisha mshahara wa msingi NA posho nyingine ZISIZOBADILIKA zinazolipwa kila mwezi pamoja na mshahara (Kanuni za Fidia kwa Wafanyakazi, 2016); si 'fedha taslimu' tu. "
                 "Ritani ya mwaka inaonyesha mapato hadi kiwango cha juu ambacho Waziri anaweza kukitangaza kwenye Gazeti (Sheria ya Fidia kwa Wafanyakazi). Kiwango (tariff) cha asilimia kinatolewa na Mkurugenzi Mkuu kwa kuzingatia mapato na kiwango cha hatari; kiwango cha sasa ni asilimia 0.5 kwa mujibu wa WCF. "
                 "Michango ya mwezi hulipwa ndani ya mwezi mmoja baada ya mwisho wa mwezi huo. Mwajiri haruhusiwi kukata mchango huu kutoka kwenye mshahara wa mfanyakazi (Sheria ya Fidia kwa Wafanyakazi). Thibitisha na WCF. "
                 "(English: the base is annual earnings = basic salary plus fixed monthly allowances paid with it, not cash only; the rate is 0.5% per WCF; paid monthly; the employer may not deduct it from the employee's earnings.)"),
        "correct_value": "WCF base = earnings (basic salary + fixed monthly allowances), not cash only; 0.5% per WCF; monthly; no deduction from the employee",
        "wrong_patterns": [r"WCF[^.;]{0,90}(?:fedha taslimu|cash)\s*(?:emoluments|pekee)"],
        "primary_source": "Workers Compensation Act, Cap.263 R.E.2023, ss.60(1), 73(1)(a), 74(1),(7); Workers Compensation Regulations 2016 (GN 185/2016) regs 3, 11, 13; WCF contribution page https://www.wcf.go.tz/pages/contribution (captured 2026-11-24T08:31:54Z)",
        "verified_by": ("Act: data/source_documents/wcf/wca_cap263_re2023_osg.pdf (assert_edition 'R.E. 2023'). s.74(1) 'according to a tariff of assessment calculated on the basis of the percentage of the annual earnings of the employer's employees as the Board may ... deem necessary'; s.73(1)(a) the annual return shows 'the amount of earnings up to the maximum contemplated in section 74(7)'; s.74(7) the Minister may prescribe a maximum. "
                        "NO DEDUCTION (the founder asked for the provision): s.60(1) 'An employer shall not deduct from the earnings of an employee any amount or receive any amount from the employee to compensate the employer directly or indirectly for any amount which the employer is liable to pay under this Act.' s.60(2): offence, fine not exceeding five million shillings or imprisonment not exceeding seven years or both. "
                        "GN 185/2016 (data/source_documents/wcf/gn185_2016_workers_compensation_regulations.pdf; edition not declared in the manifest): reg 3 'annual earnings' means 'the annual amount which is paid by an employer to his employees ... and include basic salaries and other fixed allowances which are paid on monthly basis along with basic salaries'; reg 13(1) 'Tariff determined under regulation 11 shall be paid on monthly basis'; reg 13(3) payment 'within a period of one month after the end of the month'. "
                        "RATE (primary portal, dated): wcf.go.tz/pages/contribution, fetched 2026-11-24T08:31:54Z, HTTP 200, 98,436 bytes, saved as data/source_documents/wcf/wcf_contribution_2026_11_24.html (sha256 in the manifest): 'michango katika sekta binafsi ni asilimia 0.5% na sekta ya umma asilimia 0.5% ya mapato ya mfanyakazi kila mwezi'; the same page: 'Mapato ghafi ya mfanyakazi yanajumuisha mshahara (basic salary) na posho anazolipwa sambamba na mshahara wa kila mwezi na zisizobadilika'. "
                        "LIMITS: later WCF regulations were not searched; GN 668/2021 amends compensation maxima, not these definitions; the amending GN that set 0.5% for all sectors is still unlocated (the rate rests on the portal, not on a regulation text). Corrects the 'gross cash emoluments' wording of wcf_threshold_no_minimum and wcf_rate_0_5_percent_confirmed."),
        "verified_date": D, "verified_as_at": D, "status": "CONFIRMED",
    },
}


def main():
    raw = io.open(FACTS, encoding="utf-8", newline="").read()
    facts = json.loads(raw)
    assert json.dumps(facts, ensure_ascii=False, indent=2) + "\n" == raw.replace("\r\n", "\n"), "round-trip must be exact or the diff is noise"
    n0 = len(facts)
    for k, v in NEW.items():
        assert k not in facts, k
        facts[k] = v
    # R27: amend named fields only
    t = facts["wcf_threshold_no_minimum"]
    assert "0.5% of gross cash emoluments, from employee 1" in t["fact"]
    t["fact"] = t["fact"].replace("0.5% of gross cash emoluments, from employee 1", "0.5% of earnings (basic salary and fixed monthly allowances), paid monthly, from employee 1")
    t["verified_by"] += f" | {D}: the WCF base wording corrected from 'gross cash emoluments' to earnings (basic salary and fixed monthly allowances), paid monthly: GN 185/2016 reg 3 and reg 13, and wcf.go.tz/pages/contribution (dated capture 2026-11-24); see wcf_contribution_base."
    t["correction_note"] = (t.get("correction_note") or "") + f" | {D}: 'gross cash emoluments' replaced by 'earnings (basic salary and fixed monthly allowances), paid monthly' (see wcf_rate_0_5_percent_confirmed)."
    r = facts["wcf_rate_0_5_percent_confirmed"]
    assert "0.5% of gross cash emoluments for ALL employers" in r["fact"]
    r["fact"] = r["fact"].replace("0.5% of gross cash emoluments for ALL employers", "0.5% of earnings (basic salary and fixed monthly allowances), paid monthly, for ALL employers")
    r["verified_by"] += f" | {D}: the current 0.5% for both sectors is now stated by the primary portal in a dated capture (wcf.go.tz/pages/contribution, 2026-11-24T08:31:54Z: 'sekta binafsi ... asilimia 0.5% na sekta ya umma asilimia 0.5% ya mapato ya mfanyakazi kila mwezi'); the amending GN is still unlocated. The base wording 'gross cash emoluments' corrected to earnings (basic salary and fixed monthly allowances), paid monthly."
    r["correction_note"] = (r.get("correction_note") or "") + f" | {D}: 'gross cash emoluments' was the wrong base (GN 185/2016 reg 3: basic salaries and other fixed allowances paid monthly with them; the portal says the same); now 'earnings (basic salary and fixed monthly allowances), paid monthly'. Not 'annual earnings': that reads as a once-a-year charge (founder)."
    out = json.dumps(facts, ensure_ascii=False, indent=2) + "\n"
    io.open(FACTS, "w", encoding="utf-8", newline="").write(out.replace("\n", "\r\n"))
    print("facts", n0, "->", len(facts))

    mraw = io.open(MAN, encoding="utf-8", newline="").read()
    man = json.loads(mraw)
    sep = "\r\n" if "\r\n" in mraw else "\n"
    assert json.dumps(man, ensure_ascii=False, indent=2) + "\n" == mraw.replace("\r\n", "\n"), "manifest round-trip must be exact"
    path = os.path.join(REPO, "data", "source_documents", "wcf", "wcf_contribution_2026_11_24.html")
    b = open(path, "rb").read()
    man["files"]["wcf/wcf_contribution_2026_11_24.html"] = {
        "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "captured_local_mtime_utc": "2026-11-24T08:31:54Z", "kind": "portal",
        "edition": "captured 2026-11-24T08:31:54Z (live page https://www.wcf.go.tz/pages/contribution; the site gives no edition or date)",
        "edition_evidence": "Fetched by curl, HTTP 200, 98,436 bytes. wcf.go.tz is the Workers Compensation Fund's own portal (whitelisted; ownership verified 2026-10-05). Reads: 'michango katika sekta binafsi ni asilimia 0.5% na sekta ya umma asilimia 0.5% ya mapato ya mfanyakazi kila mwezi'. DATED, UNLIKE wcf/wcf_michango.html (capture date unrecorded, edition UNDECLARED), which carries the same text.",
        "superseded": False,
    }
    ff = man["files"]
    man["counts"] = {"files": len(ff), "declared": sum(v["edition"] != "UNDECLARED" for v in ff.values()), "undeclared": sum(v["edition"] == "UNDECLARED" for v in ff.values()), "superseded": sum(bool(v.get("superseded")) for v in ff.values())}
    mo = json.dumps(man, ensure_ascii=False, indent=2) + "\n"
    io.open(MAN, "w", encoding="utf-8", newline="").write(mo.replace("\n", sep))
    print("manifest ok")


if __name__ == "__main__":
    sys.exit(main())
