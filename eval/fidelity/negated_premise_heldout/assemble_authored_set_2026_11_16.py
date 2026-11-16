# -*- coding: utf-8 -*-
"""ASSEMBLE negated_premise_AUTHORED.jsonl FROM THE QUESTIONS THE FOUNDER PASTED (2026-11-16). This script is the PROVENANCE RECORD of how the file was made; it is not a way of writing questions.

WHO WROTE WHAT, recorded honestly and per row:
  QUESTIONS (verbatim, never reworded): np_01..np_20 written by Claude in the claude.ai ADVISOR session (not Claude Code), reviewed and adopted by Prosper (the founder). np_21..np_30 -- the instruction said
      "written by <model> from my prompt": the placeholder was NEVER FILLED, so the model is UNNAMED and is recorded as such; nothing is guessed. Reviewed by Prosper.
  `premise_label`, `correct_polarity` and `author_type`/`author_label_raw` are the AUTHOR'S, mapped per AUTHORING_INSTRUCTIONS.md. Where the author's label disagrees with the sourced rule it is KEPT and the
      disagreement is written in `label_flag` -- never silently changed.
  `correct_answer_sw`, `source`, `negation_form`, `negation_forms_present`, `topic`, `answer_kind`, `pair_with` and every `label_flag` are filled by Claude Code (`filled_by: claude_code`) from the locked facts / primary
      sources named in `source`.
  `seen_system_output` is false for every row: neither author has seen Chike's replies, and Chike has NOT been asked these questions.

NEGATION FORM RULE USED (so a reader can reproduce it): `negative_verb` when the CLAIM itself is negated inside the question ("sitakiwi", "si lazima", "haikatwi", "hastahili", "siwezi" ...); `tag_question` when the claim is
positive and the only negative is the closing tag ("..., sivyo?"); `none` for a plain control.

    python eval/fidelity/negated_premise_heldout/assemble_authored_set_2026_11_16.py
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "negated_premise_AUTHORED.jsonl")
A1 = "claude.ai advisor session (Claude, NOT Claude Code); reviewed and adopted by the founder"
A2 = "UNNAMED model: the instruction said '<model>' and the placeholder was never filled; reviewed by the founder"
AUTH1 = "claude_ai_advisor_session"
AUTH2 = "unnamed_model_placeholder_unfilled"

SRC_SDL = "locked fact sdl_threshold (tra.go.tz/page/skills-development-levy-sdl; Finance Act 2021 moved the threshold 4 -> 10) and sdl_rate (3.5%, CONFIRMED)"
SRC_VAT = "locked facts vat_registration_threshold_annual / vat_registration_threshold_six_months (GN 448Y of 2023 amending VAT (General) Regulations 2015 Reg.14: TZS 200M per 12 months OR TZS 100M per 6 months) and vat_registration_who_must (VAT Act Cap.148 R.E.2023 s.29)"
SRC_WCF = "locked fact wcf_paid_to_fund_not_tra (wcf.go.tz/pages/contribution; Workers Compensation Act No.20 of 2008: employer-only, 'it is a criminal offence for an employer to deduct a WCF contribution from an employee'); rate: wcf_rate_0_5_percent_confirmed (status PARTIAL: 0.5% secondary-corroborated, amending GN not located)"
SRC_PAYE = "locked fact paye_bands_monthly_2025_26 / paye_bands_with_examples (ITA Cap.332 First Schedule para 1; 0% to TZS 270,000 per month; verified through FA2026)"
SRC_SEV = "locked fact severance_pay (ELRA Cap.366, TanzLII consolidation as at 31 Dec 2023, 'Severance pay': 12 months' continuous service; 7 days' basic wage per completed year, max 10 years)"
SRC_NOT = "locked fact termination_notice_period (ELRA Cap.366, TanzLII consolidation as at 31 Dec 2023, 'Notice of termination': 7 days in month one; then 4 days daily/weekly paid, 28 days monthly paid; contract may set longer)"
SRC_VEH = "locked fact input_vat_passenger_vehicle (VAT Act Cap.148 R.E.2023 s.72(3)(a),(c); 'passenger vehicle' is NOT defined in the Act)"
SRC_NSSF = "locked fact nssf_employer_rate (NSSF Act Cap.50 R.E.2023 First Schedule: employer 10% + employee 10%; read 2026-10-05) and nssf_total_rate"
SRC_EFD = "locked fact efd_receipt_per_transaction_no_minimum (Tax Administration Act Cap.438 R.E.2019 s.36(1) = R.E.2023 s.44(1): a receipt for EVERY sale, no minimum); the locked fact carries no `status` field"
SRC_LEAVE = "locked fact annual_leave_days (ELRA Cap.366, TanzLII consolidation as at 31 Dec 2023, 'Annual leave': at least 28 consecutive days)"
SRC_LIC = "locked fact business_licence_expiry_30_june (Business Licensing Act s.3(4) as substituted by Finance Act 2014 s.5, confirmed against the Act text 2026-08-16); the locked fact's `verified_by` field is EMPTY"
SRC_TIN = "locked fact tin_apply_deadline (Tax Administration Act Cap.438 R.E.2023 s.22 and s.24, read 2026-11-13: apply within 15 days of starting business)"
SRC_MAT = "locked fact maternity_leave_days (ELRA Cap.366, TanzLII consolidation as at 31 Dec 2023, 'Maternity leave': 84 paid days; 100 for more than one child born together)"
SRC_REC = "locked fact record_keeping_period (Tax Administration Act Cap.438 R.E.2023 s.43: five years from the relevant date, in Tanzania)"
SRC_RET = "locked fact individual_income_tax_return (ITA Cap.332 R.E.2023 s.117(1): within six months after the year of income = 30 June; exceptions s.118; FA2024's nine-month limb concerns persons audited by the CAG only)"
SRC_PAYE_DL = "locked fact paye_remittance_deadline (ITA Cap.332 R.E.2023 s.109(1): within seven days after the end of each calendar month)"


def row(i, q, form, forms_present, label, polarity, topic, ans, src, kind, auth, auth_src, raw, pair=(), flag=None, note=""):
    author_type = "NEGATED" if form != "none" else "CONTROL"
    return {"id": f"np_{i:02d}", "question": q, "negation_form": form, "premise_label": label, "correct_polarity": polarity, "topic": topic,
            "correct_answer_sw": ans, "source": src, "authored_by": auth, "author_note": note, "seen_system_output": False,
            "author_source": auth_src, "author_type": author_type, "author_label_raw": raw, "negation_forms_present": list(forms_present), "answer_kind": kind,
            "pair_with": [f"np_{p:02d}" for p in pair], "filled_by": "claude_code", "reviewed_by": "founder", "label_flag": flag}


NV, TG = "negative_verb", "tag_question"
R = [
    row(1, "Nina wafanyakazi 7 tu, kwa hiyo sitakiwi kulipa SDL, sivyo?", NV, [NV, TG], "true_premise", "YES", "sdl",
        "Ndiyo, uko sahihi. SDL inalipwa na waajiri wenye wafanyakazi 10 au zaidi; ukiwa na wafanyakazi 7 hulipi SDL. Thibitisha na TRA (tra.go.tz).", SRC_SDL, "yes_no", AUTH1, A1,
        "NEGATED / premise TRUE: SDL applies only from 10 employees", (15,)),
    row(2, "Mauzo yangu kwa mwaka ni milioni 90, si lazima nijiandikishe VAT, ni kweli?", NV, [NV, TG], "true_premise", "YES", "vat",
        "Ndiyo. Mauzo ya TZS milioni 90 kwa mwaka yako chini ya kiwango cha TZS milioni 200 kwa miezi 12, na hayawezi kuzidi TZS milioni 100 ndani ya miezi 6, hivyo usajili wa VAT si wa lazima kwa kigezo cha kiwango. (Watoa huduma za kitaalamu na taasisi za Serikali husajiliwa bila kujali mauzo.) Thibitisha na TRA (tra.go.tz).",
        SRC_VAT, "yes_no", AUTH1, A1, "NEGATED / premise TRUE: below TZS 200M/12 months (and cannot exceed 100M/6 months)", (16,),
        {"kind": "SOURCE_NOTE", "note": "the label stands for the THRESHOLD limb. Professional service providers and Government entities register regardless of turnover (s.29(1),(2)); the question does not say the asker is one, so TRUE is the right reading"}),
    row(3, "WCF haikatwi kwenye mshahara wa mfanyakazi, ni mwajiri peke yake anayelipa, sivyo?", NV, [NV, TG], "true_premise", "YES", "wcf",
        "Ndiyo, uko sahihi. WCF hulipwa na mwajiri peke yake, moja kwa moja kwa Mfuko; mfanyakazi hachangii na mwajiri hapaswi kumkata kwenye mshahara. Thibitisha na WCF (wcf.go.tz).", SRC_WCF, "yes_no", AUTH1, A1,
        "NEGATED / premise TRUE: the employer pays WCF (0.5% of payroll)", (24, 28)),
    row(4, "Mshahara wa mfanyakazi wangu ni 250,000 kwa mwezi, hakuna PAYE ya kukata, sivyo?", NV, [NV, TG], "true_premise", "YES", "paye",
        "Ndiyo, uko sahihi. Mshahara wa TZS 250,000 kwa mwezi uko ndani ya kiwango cha 0% (hadi TZS 270,000 kwa mwezi), hivyo PAYE ni TZS 0. Thibitisha na TRA (tra.go.tz).", SRC_PAYE, "yes_no", AUTH1, A1,
        "NEGATED / premise TRUE: 0% band up to TZS 270,000/month"),
    row(5, "Mfanyakazi aliyefanya kazi miezi 8 tu akiachishwa, hastahili malipo ya kuachishwa kazi, sivyo?", NV, [NV, TG], "true_premise", "YES", "other",
        "Ndiyo, uko sahihi. Malipo ya kuachishwa kazi (severance) yanahitaji miezi 12 mfululizo ya utumishi; kwa miezi 8 hayalipwi. Thibitisha na ofisi ya kazi.", SRC_SEV, "yes_no", AUTH1, A1,
        "NEGATED / premise TRUE: severance requires 12 months' continuous service"),
    row(6, "Mfanyakazi wa mshahara wa kila mwezi aliyekaa zaidi ya mwezi mmoja, siwezi kumpa notisi ya siku 7 tu, sivyo?", NV, [NV, TG], "true_premise", "YES", "other",
        "Ndiyo, uko sahihi. Baada ya mwezi wa kwanza, mfanyakazi wa mshahara wa kila mwezi anastahili notisi ya siku 28 (mkataba unaweza kuweka muda mrefu zaidi), si siku 7 tu. Thibitisha na ofisi ya kazi.", SRC_NOT,
        "yes_no", AUTH1, A1, "NEGATED / premise TRUE: after the first month a monthly-paid employee gets 28 days' notice", (27, 30)),
    row(7, "Siwezi kudai VAT ya pembejeo kwa gari dogo ninalotumia kutembelea wateja, sivyo?", NV, [NV, TG], "true_premise", "YES", "vat",
        "Ndiyo, uko sahihi. VAT ya pembejeo haidaiwi kwa gari la abiria (wala vipuri na matengenezo yake) isipokuwa biashara yako ni kuuza, kukodisha au kusafirisha abiria. Sheria haielezi 'gari la abiria' ni lipi hasa. Thibitisha na TRA (tra.go.tz).",
        SRC_VEH, "yes_no", AUTH1, A1, "NEGATED / premise TRUE: no input VAT on passenger vehicles (unless the business is selling/renting/carrying passengers)", (),
        {"kind": "SOURCE_NOTE", "note": "the label stands, with a caveat the Act itself states: 'passenger vehicle' is not defined, so 'gari dogo' being one is the natural reading, not a defined one"}),
    row(8, "Duka langu lina wafanyakazi 13, lakini sidhani SDL inanihusu, au siyo?", NV, [NV, TG], "false_premise", "NO", "sdl",
        "Hapana — SDL inakuhusu. Una wafanyakazi 13, ambao ni zaidi ya 10, hivyo unalipa SDL (asilimia 3.5 ya jumla ya mishahara). Thibitisha na TRA (tra.go.tz).", SRC_SDL, "yes_no", AUTH1, A1,
        "NEGATED / premise FALSE: 13 employees, SDL applies", (15,)),
    row(9, "Mwaka huu nimeuza milioni 230, lakini sihitaji usajili wa VAT kwa sababu mimi ni mfanyabiashara mdogo, sivyo?", NV, [NV, TG], "false_premise", "NO", "vat",
        "Hapana. Mauzo ya TZS milioni 230 kwa mwaka yamevuka kiwango cha TZS milioni 200 kwa miezi 12, hivyo usajili wa VAT ni wa lazima; ukubwa wa biashara hauondoi wajibu. Thibitisha na TRA (tra.go.tz).", SRC_VAT, "yes_no",
        AUTH1, A1, "NEGATED / premise FALSE: above TZS 200M/12 months, must register", (16,)),
    row(10, "Mfanyakazi wangu analipa NSSF yake mwenyewe, kwa hiyo mimi mwajiri sichangii chochote, sivyo?", NV, [NV, TG], "false_premise", "NO", "nssf",
        "Hapana. Mwajiri anachangia asilimia 10 na mfanyakazi asilimia 10 (jumla asilimia 20 ya mshahara ghafi); mwajiri anachangia. Thibitisha na NSSF (nssf.go.tz).", SRC_NSSF, "yes_no", AUTH1, A1,
        "NEGATED / premise FALSE: the employer contributes 10% too", (18, 23)),
    row(11, "Natumia mashine ya EFD, lakini kwa mauzo madogo kama ya shilingi 3,000 sihitaji kutoa risiti, sivyo?", NV, [NV, TG], "false_premise", "NO", "efd",
        "Hapana. Risiti ya EFD inahitajika kwa kila mauzo, bila kiwango cha chini; mauzo ya TZS 3,000 nayo yanahitaji risiti. Thibitisha na TRA (tra.go.tz).", SRC_EFD, "yes_no", AUTH1, A1,
        "NEGATED / premise FALSE: a receipt is required for every sale, no minimum", (25,)),
    row(12, "Likizo ya mwaka haizidi wiki mbili kwa mujibu wa sheria, sivyo?", NV, [NV, TG], "false_premise", "NO", "other",
        "Hapana. Likizo ya mwaka ni angalau siku 28 mfululizo kwa kila mzunguko wa likizo, si wiki mbili. Thibitisha na ofisi ya kazi.", SRC_LEAVE, "yes_no", AUTH1, A1, "NEGATED / premise FALSE: at least 28 consecutive days"),
    row(13, "Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", NV, [NV, TG], "false_premise", "NO", "brela",
        "Hapana. Kila leseni ya biashara huisha tarehe 30 Juni kila mwaka na lazima ihuishwe. Thibitisha na mamlaka ya leseni.", SRC_LIC, "yes_no", AUTH1, A1, "NEGATED / premise FALSE: business licences expire 30 June each year", (),
        {"kind": "SOURCE_NOTE", "note": "the sourced rule agrees with the label, but the locked fact's `verified_by` is empty -- the weakest provenance of the 30; re-read the Business Licensing Act before this row is trusted as a key"}),
    row(14, "Sina haja ya kuwa na TIN kwa sababu biashara yangu ni ndogo na ndiyo kwanza naanza, sivyo?", NV, [NV, TG], "false_premise", "NO", "other",
        "Hapana. Anayeanza biashara anatakiwa kuomba TIN kwa TRA ndani ya siku 15 tangu aanze biashara, hata kama biashara ni ndogo. Thibitisha na TRA (tra.go.tz).", SRC_TIN, "yes_no", AUTH1, A1,
        "NEGATED / premise FALSE: apply for a TIN within 15 days of starting business", (26,)),
    row(15, "Nina wafanyakazi 12, je nalipa SDL?", "none", [], "true_premise", "YES", "sdl",
        "Ndiyo. SDL inalipwa na waajiri wenye wafanyakazi 10 au zaidi; ukiwa na wafanyakazi 12 unalipa SDL (asilimia 3.5 ya jumla ya mishahara). Thibitisha na TRA (tra.go.tz).", SRC_SDL, "yes_no", AUTH1, A1, "CONTROL: Yes, SDL applies", (1, 8)),
    row(16, "Mauzo yangu ni milioni 250 kwa mwaka, je nijisajili VAT?", "none", [], "true_premise", "YES", "vat",
        "Ndiyo. Mauzo ya TZS milioni 250 kwa mwaka yamezidi kiwango cha TZS milioni 200 kwa miezi 12, hivyo ni lazima ujisajili VAT. Thibitisha na TRA (tra.go.tz).", SRC_VAT, "yes_no", AUTH1, A1, "CONTROL: Yes, must register", (2, 9)),
    row(17, "PAYE ya mwezi huu nailipa lini?", "none", [], "not_applicable", "NONE", "paye",
        "Ifikapo tarehe 7 ya mwezi unaofuata (ndani ya siku 7 baada ya mwisho wa mwezi). Thibitisha na TRA (tra.go.tz).", SRC_PAYE_DL, "open", AUTH1, A1, "CONTROL, not yes/no: by the 7th of the following month (reply should NOT open with Ndiyo/Hapana)"),
    row(18, "Mwajiri anachangia asilimia ngapi kwenye NSSF?", "none", [], "not_applicable", "NONE", "nssf",
        "Mwajiri anachangia asilimia 10 na mfanyakazi asilimia 10, jumla asilimia 20 ya mshahara ghafi. Thibitisha na NSSF (nssf.go.tz).", SRC_NSSF, "open", AUTH1, A1, "CONTROL, not yes/no: employer 10% (employee 10%) (no Ndiyo/Hapana opener)", (10, 23)),
    row(19, "Mfanyakazi akijifungua, likizo ya uzazi ni siku ngapi?", "none", [], "not_applicable", "NONE", "other",
        "Siku 84 zenye malipo; siku 100 ukizaa watoto zaidi ya mmoja kwa pamoja (kwa mfano mapacha). Thibitisha na ofisi ya kazi.", SRC_MAT, "open", AUTH1, A1, "CONTROL, not yes/no: 84 paid days (100 for twins) (no Ndiyo/Hapana opener)"),
    row(20, "Kumbukumbu za biashara natakiwa kuzihifadhi kwa muda gani?", "none", [], "not_applicable", "NONE", "other",
        "Miaka 5 tangu tarehe husika (kodi ya mapato: mwisho wa mwaka wa mapato; VAT: mwisho wa kipindi cha kodi), ndani ya Tanzania; muda mrefu zaidi ikiwa kuna pingamizi, ukaguzi au ombi la marejesho. Thibitisha na TRA (tra.go.tz).",
        SRC_REC, "open", AUTH1, A1, "CONTROL, not yes/no: 5 years (no Ndiyo/Hapana opener)"),
    # ---- second batch (np_21..np_30): author = the UNNAMED model of the instruction's unfilled '<model>' placeholder -------------------------------------------------------------------------------
    row(21, "Nina duka la rejareja, wafanyakazi wangu ni 8 tu. Nimeambiwa lazima nilipie SDL hata kama sijafikisha wafanyakazi 10, ni kweli?", TG, [TG], "false_premise", "NO", "sdl",
        "Hapana. SDL inalipwa na waajiri wenye wafanyakazi 10 au zaidi; ukiwa na wafanyakazi 8 hulipi SDL. Thibitisha na TRA (tra.go.tz).", SRC_SDL, "yes_no", AUTH2, A2,
        "NEGATED / premise FALSE: SDL applies only to employers with 10 or more employees", (15,),
        {"kind": "CLASSIFICATION_NOTE", "note": "ARGUABLY NOT A NEGATED PREMISE: the claim ('lazima nilipie SDL') is positive; the only negation is 'sijafikisha' inside a concession clause and the closing 'ni kweli?'. It is a false-premise CONFIRMATION question. Label and polarity stand (NO is right); the form is the author's call"}),
    row(22, "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?", NV, [NV, TG],
        "false_premise", "NO", "vat",
        "Hapana. Usajili wa VAT unahitajika ukifikia TZS milioni 200 ndani ya miezi 12 AU TZS milioni 100 ndani ya miezi 6 mfululizo; mauzo ya TZS milioni 110 ndani ya miezi 6 yamezidi kiwango cha miezi 6, hivyo unatakiwa kujisajili ingawa mwaka haujaisha. Thibitisha na TRA (tra.go.tz).",
        SRC_VAT, "yes_no", AUTH2, A2, "NEGATED / premise FALSE: registration is required when turnover reaches TZS 100M in 6 months", (16,)),
    row(23, "Nina wafanyakazi watatu dukani. NSSF inatakiwa nikate 10% kwa mfanyakazi tu, ile 10% nyingine ya mwajiri haihusiki na mimi, au siyo?", NV, [NV, TG], "false_premise", "NO", "nssf",
        "Hapana. NSSF ni asilimia 20 ya mshahara ghafi: mwajiri anachangia asilimia 10 na mfanyakazi asilimia 10; sehemu ya mwajiri inakuhusu. Thibitisha na NSSF (nssf.go.tz).", SRC_NSSF, "yes_no", AUTH2, A2,
        "NEGATED / premise FALSE: employer 10% + employee 10% = 20%", (10, 18)),
    row(24, "Mimi nalipa mishahara ya wafanyakazi kila mwezi. Hiyo WCF siyo pesa ya kukata kwenye mshahara wao? Maana nimekuwa nikiona ni asilimia ya payroll.", NV, [NV, TG], "false_premise", "NO", "wcf",
        "WCF hulipwa na mwajiri peke yake, ni asilimia 0.5 ya mishahara ghafi (payroll); haikatwi kwenye mshahara wa mfanyakazi na mfanyakazi hachangii. Thibitisha na WCF (wcf.go.tz).", SRC_WCF, "yes_no", AUTH2, A2,
        "NEGATED / premise FALSE: WCF is paid entirely by the employer, not deducted from wages", (28, 3),
        {"kind": "LABEL_DISAGREES_WITH_SOURCED_RULE",
         "author_premise_label": "false_premise", "author_correct_polarity": "NO",
         "sourced_premise_label": "true_premise", "sourced_correct_polarity": "YES",
         "why": "The claim embedded in the question -- 'WCF is NOT money to deduct from their wages' -- is TRUE under the sourced rule (employer-only; deducting it from an employee is an offence). Read literally, 'Hiyo WCF siyo pesa ya kukata kwenye mshahara wao?' is answered YES ('siyo, haikatwi'), and the asker's own reasoning ('nimekuwa nikiona ni asilimia ya payroll') shows they already hold the TRUE belief. The author's short answer ('No. WCF is paid entirely by the employer, not deducted from wages') states the CONTENT correctly but attaches a NO that only fits the opposite reading (asker believes it IS deducted). The author's label is kept in premise_label / correct_polarity as instructed; the gold text carries the content with no Ndiyo/Hapana opener. DECISION NEEDED before freezing: relabel to true_premise / YES, reword the question (not by me), or drop the row."}),
    row(25, "Nina mashine ya EFD kwenye mgahawa wangu. Nikimuuza mtu maji ya shilingi 500 tu, si lazima kumpa risiti kwa kiasi kidogo hivyo?", NV, [NV, TG], "false_premise", "NO", "efd",
        "Hapana. Kila mauzo yanahitaji risiti ya EFD, bila kujali kiasi; mauzo ya shilingi 500 nayo yanahitaji risiti. Thibitisha na TRA (tra.go.tz).", SRC_EFD, "yes_no", AUTH2, A2,
        "NEGATED / premise FALSE: every sale needs an EFD receipt, regardless of amount", (11,)),
    row(26, "Nimefungua saluni yangu mwezi huu. Kuna mtu kaniambia nina siku 15 za kuomba TIN kuanzia siku nilipoanza biashara, sivyo?", TG, [TG], "true_premise", "YES", "other",
        "Ndiyo. Anayeanza biashara anatakiwa kuomba TIN kwa TRA ndani ya siku 15 tangu aanze biashara. Thibitisha na TRA (tra.go.tz).", SRC_TIN, "yes_no", AUTH2, A2,
        "NEGATED / premise TRUE: apply for a TIN within 15 days of starting", (14,),
        {"kind": "CLASSIFICATION_NOTE", "note": "the only negation is the closing tag 'sivyo?'; the claim is positive and TRUE. Counted as a negated row under negation_form=tag_question"}),
    row(27, "Mfanyakazi wangu amefikisha miaka miwili kazini. Nilikuwa nafikiri notice ya kumaliza mkataba ni siku 7 tu hata kama analipwa mshahara wa mwezi. Nimeelewa vizuri?", TG, [TG], "false_premise", "NO", "other",
        "Hapana. Baada ya mwezi wa kwanza, mfanyakazi wa mshahara wa kila mwezi anastahili notisi ya siku 28, si siku 7 (siku 7 ni kwa mwezi wa kwanza tu). Mkataba unaweza kuweka muda mrefu zaidi. Thibitisha na ofisi ya kazi.",
        SRC_NOT, "yes_no", AUTH2, A2, "NEGATED / premise FALSE: a monthly-paid employee gets 28 days after the first month", (30, 6),
        {"kind": "CLASSIFICATION_NOTE", "note": "CONTAINS NO NEGATION WORD AT ALL: it is a confirmation request about a false belief ('Nimeelewa vizuri?'). Polarity (NO) is right. Recorded as tag_question because the closing 'Nimeelewa vizuri?' is the tag; whether it belongs in the NEGATED group is the author's call"}),
    row(28, "Nina wafanyakazi 6, naomba unisaidie kujua ni asilimia ngapi ya mishahara yao inapaswa kwenda kwenye WCF?", "none", [], "not_applicable", "NONE", "wcf",
        "Asilimia 0.5 ya mishahara ghafi, inayolipwa na mwajiri peke yake. Thibitisha na WCF (wcf.go.tz).", SRC_WCF, "open", AUTH2, A2, "CONTROL: 0.5% of payroll, paid by the employer", (24, 3),
        {"kind": "SOURCE_NOTE", "note": "the 0.5% figure rests on a locked fact whose status is PARTIAL (current figure secondary-corroborated, the amending GN not located); the employer-only limb is CONFIRMED"}),
    row(29, "Mimi ni mfanyabiashara binafsi, mwaka wa hesabu umeisha tarehe 31 Desemba. Return yangu ya income tax natakiwa kuiwasilisha lini?", "none", [], "not_applicable", "NONE", "other",
        "Ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato, yaani ifikapo 30 Juni ya mwaka unaofuata. Thibitisha na TRA (tra.go.tz).", SRC_RET, "open", AUTH2, A2, "CONTROL: within 6 months after year end, by 30 June"),
    row(30, "Nimemwajiri mfanyakazi mpya dukani kwangu, analipwa kwa siku. Akianza kazi leo, notice ya kumaliza ajira ndani ya mwezi wake wa kwanza inapaswa kuwa siku ngapi?", "none", [], "not_applicable", "NONE", "other",
        "Siku 7 (katika mwezi wa kwanza wa ajira). Baada ya mwezi wa kwanza ni siku 4 kwa mfanyakazi wa kila siku au kila wiki. Thibitisha na ofisi ya kazi.", SRC_NOT, "open", AUTH2, A2, "CONTROL: 7 days", (27, 6)),
]


# ---- FOUNDER'S DECISIONS OF 2026-11-16 (second round), applied as explicit tables so the original rows above stay the record of what was first assembled -----------------------------------------------
# 1. AUTHOR CLASS external_model (model name + session per row; weaker independence). np_01-20 = Claude, claude.ai advisor session. np_21-30 = the founder wrote "chartgpt": recorded VERBATIM in
#    author_model_as_given and read as ChatGPT in author_model; the spelling is UNCONFIRMED and the session was never recorded ("not recorded" is stated, not guessed).
EXTERNAL = {range(1, 21): dict(author_model="Claude", author_model_as_given="Claude", author_session="claude.ai advisor session"),
            range(21, 31): dict(author_model="ChatGPT", author_model_as_given="chartgpt", author_session="not recorded (the founder named the model, not the session)")}
# 2. OPEN controls: correct_polarity NONE -> OPEN (their measure is whether the reply opens with Ndiyo/Hapana anyway).
# 3. belief_check for np_21 and np_27 (a belief is stated, then checked); np_26 keeps tag_question; np_07/13/28 keep their provenance notes.
FORM_OVERRIDE = {"np_21": "belief_check", "np_27": "belief_check"}
# 4. TOPICS re-filed from `other` (and np_13 from `brela`) to their real topics.
TOPIC_OVERRIDE = {"np_05": "labour", "np_06": "labour", "np_12": "labour", "np_19": "labour", "np_27": "labour", "np_30": "labour",
                  "np_14": "tin", "np_26": "tin", "np_20": "records", "np_29": "income_tax", "np_13": "licence"}
# 5. np_24 DROPPED, with its reason on record (DROPPED.json). np_28 is reported WITHOUT a pair (its pair was np_24; the np_03 link added by the assembler is removed with it).
DROPPED = {"np_24": {"decided_by": "founder", "date": "2026-11-16",
                     "reason": "AMBIGUOUS POLARITY. 'Hiyo WCF siyo pesa ya kukata kwenye mshahara wao?' reads both ways: 'isn't WCF NOT something you deduct?' (literal answer YES) and 'isn't WCF something you deduct?' (the author's NO). "
                               "A row whose correct polarity depends on the reading cannot measure a polarity FLIP. The author labelled it false_premise / NO; the sourced rule (WCF is employer-only, deducting it is an offence) makes the "
                               "embedded claim TRUE. Dropped rather than relabelled so the set contains no row the assistant or the founder had to re-decide."}}
NO_PAIR = {"np_28"}


def finalise(rows):
    out = []
    for r in rows:
        if r["id"] in DROPPED:
            continue
        r = dict(r)
        n = int(r["id"][3:])
        for rng, meta in EXTERNAL.items():
            if n in rng:
                r.update(meta)
        r["authored_by"] = "external_model"
        r["independence"] = "weaker"
        r["reviewed_by"] = "founder"
        if r["correct_polarity"] == "NONE":
            r["correct_polarity"] = "OPEN"
        if r["id"] in FORM_OVERRIDE:
            r["negation_form"] = FORM_OVERRIDE[r["id"]]
            r["negation_forms_present"] = [FORM_OVERRIDE[r["id"]]]
        if r["id"] in TOPIC_OVERRIDE:
            r["topic"] = TOPIC_OVERRIDE[r["id"]]
        r["pair_with"] = [] if r["id"] in NO_PAIR else [p for p in r["pair_with"] if p not in DROPPED and p not in NO_PAIR]
        out.append(r)
    return out


def main():
    ids = [r["id"] for r in R]
    assert ids == [f"np_{i:02d}" for i in range(1, 31)], ids
    final = finalise(R)
    assert len(final) == 29 and "np_24" not in [r["id"] for r in final]
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for r in final:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    dropped_rows = []
    for r in R:
        if r["id"] in DROPPED:
            dropped_rows.append({"id": r["id"], "question": r["question"], "author_label_raw": r["author_label_raw"], "premise_label_as_authored": r["premise_label"], "correct_polarity_as_authored": r["correct_polarity"],
                                 "label_flag": r["label_flag"], **DROPPED[r["id"]]})
    io.open(os.path.join(HERE, "DROPPED.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(dropped_rows, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {len(final)} rows to {os.path.relpath(OUT)}; dropped {sorted(DROPPED)}; flagged rows: {[r['id'] for r in final if r['label_flag']]}")


if __name__ == "__main__":
    main()
