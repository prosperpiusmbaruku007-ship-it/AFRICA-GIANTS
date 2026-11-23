# -*- coding: utf-8 -*-
"""REPAIR 8 + 11 + 1 ROWS, QUARANTINE 3 + 2 (founder-approved 2026-11-24), then PROVE THE EXPORT CHANGED (R36).

  P9 / NSSF-7th  : 8 REPAIRS (#1,#3,#4,#5,#6,#7,#8,#11) + 3 QUARANTINES (#2,#9,#10)          eval/results/p9_nssf7_repair_proposal_2026_11_24.json
  SDL exemptions : 2 QUARANTINES (export rows 400, 1227) + 11 REWRITES from the exemptions statement (sdl_exemption_categories)
  SDL base       : tier1a_sdl_ext_004 REWRITTEN so allowances are IN the SDL base (VETA Act s.14(3)) while TaESA interns stay a SEPARATE exempt category (s.19(1)(i))

TARGETS ARE RESOLVED BY CONTENT (question + the OLD ANSWER), never by line number, in EVERY stage that holds the row: cleaned_pairs, raw_sources duplicates, sft_shaped_pairs (R36: the export is generated from these).
A target that resolves to nothing, or a rewrite whose old answer is already gone, FAILS LOUDLY: a silently moved row must not take a neighbour with it.
WHERE IT ACTS (R36): authored files -> generate_sft.py -> assertion that no OLD answer remains in datasets/tier1a/sft/. That assertion is part of THIS script.
REPORT-ONLY BY DEFAULT. Writes only under --write. Every old row is kept in datasets/tier1a/rejected/ (quarantines) or in the repair record (rewrites), reversible.

    python eval/controls/corpus_repairs_2026_11_24.py            # report
    python eval/controls/corpus_repairs_2026_11_24.py --write    # apply, regenerate the export, assert reach"""
import glob
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WRITE = "--write" in sys.argv
STAGES = ["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/raw_sources/*.jsonl"]
EXPORT = os.path.join(REPO, "datasets", "tier1a", "sft", "train_sft.jsonl")
REJ = os.path.join(REPO, "datasets", "tier1a", "rejected")

PROP = json.load(io.open(os.path.join(REPO, "eval", "results", "p9_nssf7_repair_proposal_2026_11_24.json"), encoding="utf-8"))
P9 = {r["n"]: r for r in PROP["rows"]}
EXP = json.load(io.open("/tmp/sdl_targets.json", encoding="utf-8")) if os.path.exists("/tmp/sdl_targets.json") else None

# ── ENGLISH for the P9 / NSSF repairs (the Swahili is the approved proposal text, read from the proposal file) ─────────────────────────────────────────────────────────
P9_EN = {
 1: "The employer must keep: the list of employees and their TINs, payroll calculations, PAYE calculations for each employee, TRA payment receipts, and copies of the annual withholding certificates issued to employees. These records are kept for 5 years. Confirm with TRA.",
 3: "No. Form P45 is a UK form and does NOT exist in Tanzania. What corresponds to it in Tanzania is the annual employment-income withholding certificate (Income Tax Act), issued by the employer to the employee; there is no form called 'P9' in Tanzania (that is a Kenyan term), nor a verified special 'leaving certificate' form. Confirm with TRA.",
 4: "No. 'P9' is not a Tanzanian term (it is Kenyan, KRA) and TRA has no form by that name. The employee's annual document is the annual withholding certificate, which the employer gives to the employee (not through SMS). Confirm the correct channel with TRA (tra.go.tz).",
 5: "When a foreign employee leaves Tanzania before the tax year ends: (1) compute PAYE for the whole period worked in Tanzania; (2) make the final PAYE adjustment for the last month; (3) give them the annual withholding certificate showing the period worked; (4) remove the employee's registration from the TRA PAYE system. Confirm the final steps with TRA.",
 6: "Yes: an employee with a TIN, correctly withheld PAYE and NSSF contributions has good tax standing in Tanzania. This is the right structure to follow. The employer also needs SDL (if 10 or more staff) and WCF (0.5%) paid. Keep all withholding certificates and payment records for any TRA audit.",
 7: "PAYE on the final salary (terminal benefits: final pay, severance allowance, accrued leave paid) must be computed, withheld and remitted to TRA by the 7th of the month following the final payment. Give the employee the annual withholding certificate after the final payment.",
 8: "No, not on the same date. SDL is due by the 7th of the following month (to TRA), and NSSF within one month after the end of the payroll month (to NSSF). They are DIFFERENT institutions, so pay each to its own institution: paying SDL to NSSF or the reverse will cause reconciliation problems. Confirm with TRA and NSSF.",
 11: "'P9' is not a Tanzanian term: it is Kenyan (KRA) and TRA has no form by that name. Tanzania has the annual employment-income withholding certificate: a document showing the total income tax withheld from an employee's pay for the year, which the employer must serve by 30 January of the following year (Income Tax Act). Confirm with TRA.",
}

# ── SDL exemption REWRITES: (question prefix) -> (Swahili, English). Built from the founder-approved exemptions statement (sdl_exemption_categories, VETA Act s.19(1)(a)-(k) + s.19(3)); no section numbers (R44). ─────
LIST_SW = "Waliosamehewa kisheria ni makundi yaliyoorodheshwa tu: taasisi au idara ya Serikali inayofadhiliwa kikamilifu kupitia ruzuku ya Serikali, balozi, Umoja wa Mataifa, taasisi za misaada za kimataifa au za kigeni, taasisi za dini (kwa wafanyakazi walioajiriwa tu kuendesha ibada, kutoa mafundisho ya dini au huduma ya afya ya jamii), mashirika ya hisani kama sheria inavyoyafafanua, taasisi za elimu zilizosajiliwa, halmashauri za serikali za mitaa, wanafunzi wa mafunzo kwa vitendo walio chini ya mpango wa TaESA, na waajiri wa mashambani kwa wafanyakazi wa kilimo tu; Waziri wa Fedha pia anaweza kusamehe kwa tangazo la Gazeti."
LIST_EN = "The exempt groups are only those the law lists: a Government department or institution wholly financed through Government subvention, diplomatic missions, the United Nations, international or foreign aid and technical-assistance institutions, religious institutions (for employees solely employed to run worship, give religious instruction or provide public health), charitable organisations as the law defines them, registered educational institutions, local government authorities, intern students under the TaESA programme, and farm employers for employees directly engaged in farming only; the Minister for Finance may also exempt by Gazette notice."
ZONE_SW = ("Sheria ya SDL haitaji eneo la uchumi (EPZ au SEZ) kama kundi lililosamehewa, na hakuna chanzo tulichonacho kinachosema kampuni za {z} hazilipi SDL. " + LIST_SW + " Mwajiri mwenye wafanyakazi 10 au zaidi ambaye hayuko kwenye orodha hiyo wala hajasamehewa kwa Gazeti hutozwa SDL. Kama mkataba wako na mamlaka ya {z} unasema vinginevyo, thibitisha na TRA (tra.go.tz).")
ZONE_EN = ("The SDL law does not name a special economic area ({z}) as an exempt group, and no source we hold says {z} companies do not pay SDL. " + LIST_EN + " An employer with 10 or more employees that is on neither the list nor a Gazette exemption is charged SDL. If your agreement with the {z} authority says otherwise, confirm with TRA (tra.go.tz).")
REWRITES = [
 ("NGO yetu ina wafanyakazi 15.",
  "Jina 'NGO' peke yake halitoi msamaha wa SDL. " + LIST_SW + " Hakuna ombi la 'uthibitisho wa msamaha' kwa TRA lililotajwa na sheria. NGO yenye wafanyakazi 15 isiyo kwenye orodha hiyo wala haijasamehewa kwa Gazeti hutozwa SDL. Thibitisha na TRA (tra.go.tz).",
  "The name 'NGO' on its own gives no SDL exemption. " + LIST_EN + " The law mentions no application for an 'exemption confirmation' from TRA. An NGO with 15 employees that is on neither the list nor a Gazette exemption is charged SDL. Confirm with TRA (tra.go.tz)."),
 ("Taasisi ya serikali (government agency)",
  "Si kila taasisi ya Serikali husamehewa SDL. Sheria inasamehe taasisi au idara ya Serikali inayofadhiliwa KIKAMILIFU kupitia ruzuku ya Serikali, na halmashauri za serikali za mitaa; taasisi ya Serikali isiyofadhiliwa kikamilifu hivyo, yenye wafanyakazi 10 au zaidi, hutozwa SDL. Thibitisha hali ya taasisi yako na TRA (tra.go.tz).",
  "Not every Government institution is exempt from SDL. The law exempts a Government department or institution WHOLLY financed through Government subvention, and local government authorities; a Government institution not wholly financed that way, with 10 or more employees, is charged SDL. Confirm your institution's status with TRA (tra.go.tz)."),
 ("Kampuni ya EPZ (Export Processing Zone) inalipa SDL?", ZONE_SW.format(z="EPZ"), ZONE_EN.format(z="EPZ")),
 ("Waajiri wa EPZ (Export Processing Zone) wanaweza kusamehewa SDL?", ZONE_SW.format(z="EPZ"), ZONE_EN.format(z="EPZ")),
 ("Kampuni yetu iko katika Eneo la Usindikaji wa Uuzaji Nje (EPZ).", ZONE_SW.format(z="EPZ"), ZONE_EN.format(z="EPZ")),
 ("Kampuni ya uwekezaji wa nje iliyopo kwenye SEZ", ZONE_SW.format(z="SEZ"), ZONE_EN.format(z="SEZ")),
 ("Kampuni inayomilikiwa na Serikali (parastatal) inalipa SDL?",
  "Kampuni inayomilikiwa na Serikali (parastatal) haisamehewi SDL kwa sababu tu inamilikiwa na Serikali. Msamaha ni kwa taasisi au idara ya Serikali inayofadhiliwa KIKAMILIFU kupitia ruzuku ya Serikali; parastatal inayojiendesha kwa mapato yake, yenye wafanyakazi 10 au zaidi, hutozwa SDL kama waajiri wengine isipokuwa Waziri wa Fedha amemsamehe kwa tangazo la Gazeti. Thibitisha na TRA (tra.go.tz).",
  "A State-owned company (parastatal) is not exempt from SDL merely because the State owns it. The exemption is for a Government department or institution WHOLLY financed through Government subvention; a parastatal that runs on its own income, with 10 or more employees, is charged SDL like other employers unless the Minister for Finance has exempted it by Gazette notice. Confirm with TRA (tra.go.tz)."),
 ("Shule au chuo binafsi chenye walimu 20",
  "Hapana: taasisi za elimu zilizosajiliwa (shule za awali, msingi na sekondari, vyuo vya ufundi na elimu, vyuo vikuu na taasisi za elimu ya juu) ni kundi lililosamehewa SDL kisheria. Shule au chuo binafsi kilichosajiliwa kama taasisi ya elimu hakitozwi SDL hata kikiwa na walimu 20. Thibitisha usajili wa taasisi yako na TRA (tra.go.tz).",
  "No: registered educational institutions (nursery, primary and secondary schools, vocational and training schools, universities and higher learning institutions) are an exempt group by law. A private school or college registered as an educational institution is not charged SDL even with 20 teachers. Confirm your institution's registration with TRA (tra.go.tz)."),
 ("Mwalimu wa shule ya msingi ya binafsi",
  "Shule binafsi za msingi zinaweza kuwa na wajibu wa: (1) PAYE kwa walimu waliohiriwa; (2) NSSF na WCF (SDL haitozwi kwa taasisi ya elimu iliyosajiliwa); (3) Usajili wa biashara BRELA na leseni ya elimu kutoka Wizara ya Elimu; (4) VAT kama mauzo ya ada yanafikia kizingiti (ingawa elimu inaweza kuwa na msamaha — thibitisha). TIN ya shule inahitajika.",
  "Private primary schools may have duties for: (1) PAYE on hired teachers; (2) NSSF and WCF (SDL is not charged on a registered educational institution); (3) BRELA business registration and an education licence from the Ministry of Education; (4) VAT if fee sales reach the threshold (although education may be exempt: confirm). The school needs a TIN."),
 ("Nina shule ya binafsi, wafanyakazi 30",
  "Shule iliyosajiliwa kama taasisi ya elimu HAITOZWI SDL, kwa sababu taasisi za elimu zilizosajiliwa ni kundi lililosamehewa kisheria; thibitisha usajili wa shule yako na TRA. PAYE hukatwa kwa wafanyakazi wanaopata zaidi ya TZS 270,000, na NSSF (20%), WCF (0.5%) na OSHA huanza tangu mfanyakazi wa kwanza. Thibitisha na TRA (tra.go.tz), NSSF (nssf.go.tz), WCF (wcf.go.tz) na OSHA (osha.go.tz).",
  "A school registered as an educational institution is NOT charged SDL, because registered educational institutions are an exempt group by law; confirm your school's registration with TRA. PAYE is withheld for employees earning more than TZS 270,000, and NSSF (20%), WCF (0.5%) and OSHA apply from the first employee. Confirm with TRA (tra.go.tz), NSSF (nssf.go.tz), WCF (wcf.go.tz) and OSHA (osha.go.tz)."),
 ("Shirika lisilo la faida (NGO au asasi ya kiraia) linalipa SDL?",
  "Jina 'NGO' au 'lisilo la faida' peke yake halitoi msamaha wa SDL, wala hakuna uthibitisho wa kila mwaka kwa TRA uliotajwa na sheria. " + LIST_SW + " NGO yenye wafanyakazi 10 au zaidi isiyo kwenye orodha hiyo wala haijasamehewa kwa Gazeti hutozwa SDL. Thibitisha na TRA (tra.go.tz).",
  "The name 'NGO' or 'non-profit' on its own gives no SDL exemption, and the law mentions no yearly proof to TRA. " + LIST_EN + " An NGO with 10 or more employees that is on neither the list nor a Gazette exemption is charged SDL. Confirm with TRA (tra.go.tz)."),
 ("Kampuni yangu inafunza wanafunzi (apprentices)",
  "Posho zote anazolipa mwajiri kuhusiana na ajira ziko kwenye msingi wa SDL: jumla ya mishahara ghafi ya mwezi inajumuisha posho za safari, malazi, burudani na nyinginezo (Sheria ya Elimu na Mafunzo ya Ufundi). Kwa hiyo posho ya mafunzo haitoki kwenye msingi kwa sababu tu inaitwa 'posho'. Kuna kundi TOFAUTI lililosamehewa kisheria: wanafunzi wanaofanya mafunzo kwa vitendo (interns) kutoka taasisi za elimu ya juu au za ufundi stadi walio chini ya mpango wa Wakala wa Huduma za Ajira Tanzania (TaESA). Msamaha huo ni wa kundi hilo lenyewe, si wa aina ya malipo. Mwanafunzi asiye kwenye mpango wa TaESA, anayelipwa na mwajiri kuhusiana na ajira au huduma, malipo yake yako kwenye msingi, na SDL inatozwa kwa mwajiri mwenye wafanyakazi 10 au zaidi. Mpango wa serikali usio wa TaESA haujatajwa kuwa na msamaha: thibitisha na TRA (tra.go.tz).",
  "Every allowance an employer pays in connection with employment is in the SDL base: gross monthly emoluments include subsistence, travelling, entertainment and other allowances (VETA Act). So a training allowance does not drop out of the base merely because it is called an 'allowance'. A SEPARATE category is exempt by law: intern students from higher learning or technical and vocational training institutions who are under the Tanzania Employment Services Agency (TaESA) programme. That exemption attaches to that group, not to a type of payment. A student outside the TaESA programme who is paid by the employer in connection with employment or services has those payments in the base, and SDL is charged on an employer with 10 or more employees. A non-TaESA government scheme is not named as exempt: confirm with TRA (tra.go.tz)."),
]
QUARANTINE_Q = {  # (question prefix) -> (defect class, reason quoting the row)
 "Mwajiri anaweza kuomba msamaha wa SDL vipi?": ("SDL_INVENTED_EXEMPTION_APPLICATION", "teaches a formal application to the Commissioner citing EPZ status as a ground ('...aandike ombi rasmi kwa Kamishna wa TRA akitoa sababu ... kama vile hadhi ya EPZ'): VETA Act Cap.82 R.E.2023 s.19 lists the exempt groups and a Minister's Gazette power; it provides no application route and does not name EPZ."),
 "Faida za kufanya biashara ndani ya Eneo Maalum la Uchumi": ("SDL_UNSUPPORTED_SEZ_EXEMPTION", "lists an SDL exemption among SEZ benefits: no source we hold says so, and s.19 does not name a special economic zone."),
}


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def rows_of(path):
    out = []
    for i, line in enumerate(read(path).splitlines(), 1):
        if line.strip():
            try:
                out.append((i, json.loads(line), line))
            except ValueError:
                out.append((i, None, line))
    return out


def ans_keys(r):
    return [k for k in ("answer_sw", "output") if k in r], [k for k in ("answer_en",) if k in r]


def qtext(r):
    return (r.get("question_sw") or r.get("instruction") or "").strip()


def atext(r):
    return (r.get("answer_sw") or r.get("output") or "").strip()


def stage_files():
    fs = []
    for g in STAGES:
        fs += glob.glob(os.path.join(REPO, g))
    return sorted(set(fs))


def plan():
    """[(kind, file, lineno, row, spec)] resolved by CONTENT across every stage."""
    acts = []
    files = stage_files()
    loaded = {f: rows_of(f) for f in files}

    def find(qpre=None, old=None):
        hits = []
        for f, rows in loaded.items():
            for ln, r, raw in rows:
                if r is None:
                    continue
                if (old is not None and atext(r) == old.strip()) or (qpre is not None and qtext(r).startswith(qpre)):
                    hits.append((f, ln, r))
        return hits
    # P9 / NSSF-7th
    for n, row in P9.items():
        hits = find(old=row["old_answer"])
        assert hits, f"P9 row #{n}: old answer resolves to NOTHING (already changed, or moved)"
        for f, ln, r in hits:
            if row["action"] == "REPAIR":
                acts.append(("repair", f, ln, r, {"sw": row["new_answer"], "en": P9_EN[n], "tag": f"p9_nssf7_#{n}"}))
            else:
                acts.append(("quarantine", f, ln, r, {"cls": "P9_OR_UNSOURCED_CLAIM_TAUGHT", "reason": row["reason_and_R37_check"], "tag": f"p9_nssf7_#{n}"}))
    # SDL exemption rewrites / quarantines (question prefix; the old answer must be an OLD one: it must NOT already equal the new text)
    for qpre, sw, en in REWRITES:
        hits = [h for h in find(qpre=qpre) if atext(h[2]) not in (sw.strip(),)]
        assert hits, f"SDL rewrite '{qpre}': resolves to NOTHING"
        for f, ln, r in hits:
            acts.append(("repair", f, ln, r, {"sw": sw, "en": en, "tag": "sdl_exemption_rewrite:" + qpre[:40]}))
    for qpre, (cls, reason) in QUARANTINE_Q.items():
        hits = find(qpre=qpre)
        assert hits, f"SDL quarantine '{qpre}': resolves to NOTHING"
        for f, ln, r in hits:
            acts.append(("quarantine", f, ln, r, {"cls": cls, "reason": reason, "tag": "sdl_exemption_quarantine:" + qpre[:40]}))
    return acts, loaded


def main():
    acts, loaded = plan()
    by = {}
    for a in acts:
        by.setdefault((a[0], a[4]["tag"]), []).append(os.path.relpath(a[1], REPO).replace("\\", "/").replace("datasets/tier1a/", "") + ":" + str(a[2]))
    print(f"{len(acts)} location-actions; {sum(1 for a in acts if a[0]=='repair')} repair, {sum(1 for a in acts if a[0]=='quarantine')} quarantine")
    for (k, t), locs in sorted(by.items()):
        print(f"  {k:<10} {t:<62} {len(locs)} loc: {', '.join(locs)[:150]}")
    ext = [a for a in acts if a[4]["tag"].startswith("sdl_exemption_rewrite:Kampuni yangu inafunza")]
    print("\nSHOWN FOR APPROVAL (tier1a_sdl_ext_004), NEW answer_sw:\n ", ext[0][4]["sw"], "\nNEW answer_en:\n ", ext[0][4]["en"])
    if not WRITE:
        print("\n(report only; --write applies)")
        return 0
    os.makedirs(REJ, exist_ok=True)
    record_q, record_r = [], []
    # apply per file, from the bottom up so line numbers stay valid
    per = {}
    for a in acts:
        per.setdefault(a[1], []).append(a)
    for f, items in per.items():
        lines = read(f).split("\n") if "\r\n" not in read(f) else read(f).split("\r\n")
        eol = "\r\n" if "\r\n" in read(f) else "\n"
        for kind, _, ln, r, spec in sorted(items, key=lambda x: -x[2]):
            rel = os.path.relpath(f, REPO).replace("\\", "/")
            if kind == "quarantine":
                record_q.append({"source_file": rel, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus", "defect_class": spec["cls"], "reason": spec["reason"], "row": r})
                del lines[ln - 1]
            else:
                new = dict(r)
                sw_keys, en_keys = ans_keys(r)
                for k in sw_keys:
                    new[k] = spec["sw"]
                for k in en_keys:
                    new[k] = spec["en"]
                record_r.append({"source_file": rel, "source_line": ln, "action": "answer_rewritten_in_place", "tag": spec["tag"], "old": {k: r[k] for k in sw_keys + en_keys}, "new": {k: new[k] for k in sw_keys + en_keys}})
                lines[ln - 1] = json.dumps(new, ensure_ascii=False)
        io.open(f, "w", encoding="utf-8", newline="").write(eol.join(lines))
    with io.open(os.path.join(REJ, "p9_nssf7_sdl_exemption_quarantine_2026_11_24.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for x in record_q:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    with io.open(os.path.join(REPO, "eval", "results", "corpus_rewrites_2026_11_24.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for x in record_r:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"\nWRITTEN: {len(record_q)} removals, {len(record_r)} rewrites; records in datasets/tier1a/rejected/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
