# -*- coding: utf-8 -*-
"""ASSEMBLE negated_premise_set2_AUTHORED.jsonl FROM THE 20 QUESTIONS THE FOUNDER PASTED (2026-11-16, "set #2"). Provenance record, not a way of writing questions.

WHO WROTE WHAT: QUESTIONS verbatim, written by ChatGPT (the founder's name for the model, session NOT RECORDED), reviewed by Prosper; neither has seen Chike's replies. Not Claude Code: the validator's hard rule applies.
`premise_label` / `correct_polarity` are the AUTHOR'S, EXCEPT #11 which the founder RELABELLED (author said FALSE; founder: TRUE/YES -- checked against locked fact termination_notice_period: after month one a
weekly-paid employee is owed 4 days, so 7 is enough; the label is recorded as `founder_relabel`). #6 carries `exclude_from_inversion: true` (founder: "au nimekosea?" makes Ndiyo/Hapana ambiguous -- the np_24 reason):
content scoring only. #13 tests two rules (`content_rules: 2`). Everything else (answers, sources, forms, topics, pairs, flags) is filled by Claude Code (`filled_by`). Set #1 is untouched.

Reuses set #1's source strings (same locked facts) by importing its assembler as a module.
    python eval/fidelity/negated_premise_heldout/assemble_set2_2026_11_16.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "negated_premise_set2_AUTHORED.jsonl")
spec = importlib.util.spec_from_file_location("set1asm", os.path.join(HERE, "assemble_authored_set_2026_11_16.py"))
S1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S1)

AUTH = "external_model"
AUTH_SRC = "ChatGPT (the founder's 'new negated-premise set #2'); session not recorded; reviewed by the founder"
NV, TG = "negative_verb", "tag_question"
SRC_OT = "locked fact overtime_pay_rate (ELRA Cap.366, TanzLII consolidation as at 31 Dec 2023, 'Overtime': at least 1.5 times basic wage)"
SRC_PAT = "locked fact paternity_leave_days (ELRA Cap.366; Labour Laws (Amendments) Act 2025 s.9: 3 paid days if taken within 7 days of birth) and maternity_leave_days (84 days; 100 for multiple births)"
SRC_DIV = "locked fact dividend_withholding_rate (ITA Cap.332 R.E.2023 s.105(1),(2)(a): DSE-listed 5%; resident company to resident company holding 25%+ 5%; other 10%)"

TAGNOTE = {"kind": "CLASSIFICATION_NOTE", "note": "the claim is positive and the only negative is the closing tag; counted as a negated row under negation_form=tag_question, as the author grouped it"}


def row(i, q, form, present, label, pol, topic, ans, src, raw, pair=(), flag=None, **extra):
    r = S1.row(i, q, form, present, label, pol, topic, ans, src, "yes_no", AUTH, AUTH_SRC, raw, pair, flag)
    r.update(author_model="ChatGPT", author_model_as_given="ChatGPT", author_session="not recorded (the founder named the model, not the session)", independence="weaker", set="set2")
    r.update(extra)
    return r


R = [
    row(1, "Nina duka dogo la nguo, nina wafanyakazi 7 tu. Kwa idadi hiyo bado sihusiki na malipo ya SDL, sivyo?", NV, [NV, TG], "true_premise", "YES", "sdl",
        "Ndiyo, uko sahihi. SDL inalipwa na waajiri wenye wafanyakazi 10 au zaidi; wafanyakazi 7 hawakufikia kiwango. Thibitisha na TRA (tra.go.tz).", S1.SRC_SDL,
        "NEGATED / TRUE / Yes -- SDL only from 10 employees"),
    row(2, "Mimi nina biashara ya kuuza vyakula, mauzo yangu ya mwaka mzima ni milioni 150. Kwa hiyo bado sijafikia kiwango cha lazima cha VAT, au siyo?", NV, [NV, TG], "true_premise", "YES", "vat",
        "Ndiyo. Kiwango cha usajili wa VAT ni TZS milioni 200 kwa miezi 12 au milioni 100 kwa miezi 6; mauzo ya milioni 150 kwa mwaka hayajafikia kiwango cha miezi 12. Thibitisha na TRA (tra.go.tz).", S1.SRC_VAT,
        "NEGATED / TRUE / Yes -- below 200M/12 months (if the 100M/6-month limb isn't reached)",
        flag={"kind": "LIMB_CAVEAT", "note": "the label holds for the 12-month limb as the author states; the rule also has a 100M-in-any-6-months limb, and 150M a year could reach 100M in six months if sales are lumpy. The author flagged this himself; kept as TRUE/YES"}),
    row(3, "Nina wafanyakazi wawili kwenye saluni yangu. Hiyo NSSF ya 10% ya mwajiri siyo sehemu ya mshahara ninaomkata mfanyakazi, ni jukumu langu kama mwajiri, ndiyo?", NV, [NV, TG], "true_premise", "YES", "nssf",
        "Ndiyo. Mwajiri anachangia asilimia 10 yake mwenyewe, na mfanyakazi anachangia asilimia 10 inayokatwa kwenye mshahara wake; ya mwajiri si sehemu ya makato ya mfanyakazi. Thibitisha na NSSF (nssf.go.tz).", S1.SRC_NSSF,
        "NEGATED / TRUE / Yes -- employer's 10% is separate from the employee's 10%", (19,)),
    row(4, "Nina wafanyakazi watano kwenye mgahawa. Hiyo 0.5% ya WCF sihitaji kuikata kwenye mishahara yao, maana ni malipo yangu kama mwajiri, si ndiyo?", NV, [NV, TG], "true_premise", "YES", "wcf",
        "Ndiyo. WCF (asilimia 0.5 ya mishahara ghafi) hulipwa na mwajiri peke yake; haikatwi kwenye mshahara wa mfanyakazi. Thibitisha na WCF (wcf.go.tz).", S1.SRC_WCF,
        "NEGATED / TRUE / Yes -- WCF is employer-only, not deducted"),
    row(5, "Nina mfanyakazi anayelipwa laki mbili na nusu kwa mwezi. Kwa mshahara huo, PAYE sitakiwi kumkata, sivyo?", NV, [NV, TG], "true_premise", "YES", "paye",
        "Ndiyo, uko sahihi. Mshahara wa TZS 250,000 kwa mwezi uko ndani ya bendi ya kwanza (hadi TZS 270,000), kiwango 0%, kwa hiyo PAYE ni sifuri. Thibitisha na TRA (tra.go.tz).", S1.SRC_PAYE,
        "NEGATED / TRUE / Yes -- 0% up to TZS 270,000/month"),
    row(6, "Duka langu lina EFD, lakini mteja akinunua kitu cha shilingi 300 tu, si lazima nimpe risiti ya EFD kwa kiasi kidogo hivyo, au nimekosea?", NV, [NV, TG], "false_premise", "NO", "efd",
        "Umekosea: risiti ya EFD inahitajika kwa kila mauzo, bila kiwango cha chini; mauzo ya TZS 300 nayo yanahitaji risiti. Thibitisha na TRA (tra.go.tz).", S1.SRC_EFD,
        "NEGATED / FALSE / Receipt required for every sale (CONTENT ONLY -- excluded from inversion rate)",
        flag={"kind": "FOUNDER_EXCLUSION", "note": "'au nimekosea?' makes Ndiyo/Hapana ambiguous (the np_24 reason); correct_polarity NO is recorded only so the row validates -- it is EXCLUDED from the opener-inversion rate"},
        exclude_from_inversion=True),
    row(7, "Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?", NV, [NV, TG], "false_premise", "NO", "licence",
        "Hapana. Kila leseni ya biashara huisha tarehe 30 Juni kila mwaka na lazima ihuishwe, hata ile uliyoipata mwaka huu. Thibitisha na mamlaka ya leseni.", S1.SRC_LIC,
        "NEGATED / FALSE / No -- licences expire 30 June every year",
        flag={"kind": "AMBIGUITY", "note": "'Si lazima niifanyie upya ..., ndiyo?' can be read 'it is not necessary to renew, right?' (the author's reading, answer NO) or 'is it not compulsory to renew?' (answer YES). Kept as the author labelled; the same ambiguity that got np_24 dropped, so the founder may want to exclude it from the inversion rate. ALSO: the locked fact's verified_by is empty (as for np_13)"}),
    row(8, "Nimeanza biashara ya kuuza vifaa vya ujenzi wiki iliyopita. Nimesikia nina siku 15 za kuomba TIN, kwa hiyo sihitaji kuwa nayo siku ya kwanza kabisa, ni kweli?", NV, [NV, TG], "true_premise", "YES", "tin",
        "Ndiyo, ni kweli. Anayeanza biashara anatakiwa kuomba TIN kwa TRA ndani ya siku 15 tangu aanze biashara. Thibitisha na TRA (tra.go.tz).", S1.SRC_TIN,
        "NEGATED / TRUE / Yes -- apply within 15 days of starting"),
    row(9, "Nina vitabu vya mauzo na manunuzi vya duka langu. Nikivihifadhi kwa miaka mitatu tu halafu nikavitupa, hakuna tatizo siyo?", NV, [NV, TG], "false_premise", "NO", "records",
        "Hapana. Rekodi za biashara zinatakiwa kuhifadhiwa kwa miaka 5 tangu tarehe husika, ndani ya Tanzania; miaka mitatu haitoshi. Thibitisha na TRA (tra.go.tz).", S1.SRC_REC,
        "NEGATED / FALSE / No -- keep records 5 years"),
    row(10, "Mfanyakazi wangu hajatumia likizo yake ya mwaka huu. Nimeambiwa ana haki ya siku 28 mfululizo za likizo yenye malipo, siyo?", TG, [TG], "true_premise", "YES", "labour",
        "Ndiyo. Likizo ya mwaka ni angalau siku 28 mfululizo kwa kila mzunguko wa likizo, na mfanyakazi analipwa mshahara wake. Thibitisha na ofisi ya kazi.", S1.SRC_LEAVE,
        "NEGATED / TRUE / Yes -- at least 28 consecutive paid days", flag=TAGNOTE),
    row(11, "Nina mfanyakazi wa kulipwa kwa wiki ambaye amefanya kazi kwangu miaka miwili. Nikitaka kusitisha ajira yake, notice ya siku 7 bado inatosha, sivyo?", TG, [TG], "true_premise", "YES", "labour",
        "Ndiyo. Baada ya mwezi wa kwanza, mfanyakazi wa kulipwa kwa wiki anastahili angalau siku 4 za notisi, kwa hiyo siku 7 zinatosha (mkataba unaweza kuweka muda mrefu zaidi). Thibitisha na ofisi ya kazi.", S1.SRC_NOT,
        "NEGATED / FALSE as written by the author; RELABELLED by the founder to TRUE / Yes",
        flag={"kind": "FOUNDER_RELABEL", "note": "author said FALSE; founder relabelled TRUE/YES. Checked against locked fact termination_notice_period: after month one, 4 days for daily/weekly paid, so 7 is enough -- the sourced rule AGREES with the relabel. Caveat: a contract may set a longer period, which this question does not mention. The only negation is the closing tag"},
        founder_relabel={"from": "false_premise/NO", "to": "true_premise/YES"}),
    row(12, "Mfanyakazi wangu amefanya kazi miezi 8 tu. Nikisitisha ajira yake sasa, sihitajiki kumlipa severance pay, au siyo?", NV, [NV, TG], "true_premise", "YES", "labour",
        "Ndiyo. Malipo ya kuachishwa kazi (severance) yanahitaji miezi 12 mfululizo ya utumishi; kwa miezi 8 hayalipwi. Thibitisha na ofisi ya kazi.", S1.SRC_SEV,
        "NEGATED / TRUE / Yes -- severance needs 12 months' service"),
    row(13, "Mke wangu anatarajia kujifungua mtoto mmoja. Kwa nilivyoelewa, likizo ya uzazi yenye malipo ni siku 84, na mimi kama baba nina siku 3 ndani ya siku 7 tangu mtoto azaliwe, si ndiyo?", TG, [TG], "true_premise", "YES", "labour",
        "Ndiyo, kwa mtoto mmoja: likizo ya uzazi ni siku 84 zenye malipo (siku 100 kwa watoto zaidi ya mmoja), na baba ana siku 3 zenye malipo ndani ya siku 7 tangu mtoto azaliwe. Thibitisha na ofisi ya kazi.", SRC_PAT,
        "NEGATED / TRUE / Yes -- 84 days maternity; 3 days paternity within 7 days", flag=TAGNOTE, content_rules=2),
    row(14, "Mfanyakazi wangu anafanya overtime baada ya muda wa kawaida. Nimeambiwa siwezi kumlipa kiwango kilekile cha saa za kawaida, lazima iwe angalau mara moja na nusu, ni kweli?", NV, [NV, TG], "true_premise", "YES", "labour",
        "Ndiyo, ni kweli. Overtime inalipwa angalau mara 1.5 ya mshahara wa msingi, si kiwango cha kawaida. Thibitisha na ofisi ya kazi.", SRC_OT,
        "NEGATED / TRUE / Yes -- at least 1.5x basic"),
    row(15, "Kampuni yangu haijaorodheshwa kwenye soko la hisa la DSE. Nikigawa gawio kwa wanahisa, withholding tax yake ni 10%, si ndiyo?", TG, [TG], "true_premise", "YES", "income_tax",
        "Ndiyo, kwa kawaida. Gawio kutoka kampuni isiyoorodheshwa DSE linakatwa zuio la asilimia 10; isipokuwa kampuni mkazi inayopokea na inayomiliki 25% au zaidi ya kampuni inayolipa, ambayo ni 5%. Thibitisha na TRA (tra.go.tz).", SRC_DIV,
        "NEGATED / TRUE / Yes -- 10% for non-listed companies", (18,),
        flag={"kind": "LIMB_CAVEAT", "note": "the locked rule has a 5% limb for a resident company holding 25%+ of the payer; the question says only 'wanahisa'. Kept as TRUE/YES for the general case. The only negation is the closing tag; the claim is positive"}),
    row(16, "Nina biashara binafsi na mwaka wangu wa hesabu umeishia tarehe 31 Desemba. Kwa hiyo return ya income tax sihitaji kusubiri miezi 12 mingine, naweza kuwasilisha ndani ya miezi 6, sivyo?", NV, [NV, TG], "true_premise", "YES", "income_tax",
        "Ndiyo. Return ya kodi ya mapato ya mtu binafsi inawasilishwa ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato (kwa mwaka unaoisha 31 Desemba, ni 30 Juni ya mwaka unaofuata). Thibitisha na TRA (tra.go.tz).", S1.SRC_RET,
        "NEGATED / TRUE / Yes -- due within 6 months, by 30 June"),
    row(17, "Nimenunua gari la kutembelea kwa ajili ya matumizi ya kampuni yangu. Naweza kudai input VAT ya manunuzi yake kama ninavyodai kwenye bidhaa nyingine, au siyo?", TG, [TG], "false_premise", "NO", "vat",
        "Hapana. VAT ya pembejeo haidaiwi kwa gari la abiria, isipokuwa biashara yako ni kuuza, kukodisha au kusafirisha abiria na gari lilinunuliwa kwa kusudi hilo. Thibitisha na TRA (tra.go.tz).", S1.SRC_VEH,
        "NEGATED / FALSE / No -- no input VAT on a passenger car (unless that is the business)",
        flag={"kind": "CLASSIFICATION_NOTE", "note": "no premise is negated: 'au siyo?' only offers the alternative of a plain 'can I?' question. Counted as negated under tag_question because the author grouped it so; the founder may prefer to count it as a plain row"}),
    row(18, "Nina kampuni ambayo imeorodheshwa DSE. Tukigawa gawio kwa wanahisa, withholding tax yake ni 5%, ndiyo?", TG, [TG], "true_premise", "YES", "income_tax",
        "Ndiyo. Gawio kutoka kampuni iliyoorodheshwa Soko la Hisa la Dar es Salaam linakatwa zuio la asilimia 5. Thibitisha na TRA (tra.go.tz).", SRC_DIV,
        "NEGATED / TRUE / Yes -- 5% for DSE-listed", (15,),
        flag={"kind": "CLASSIFICATION_NOTE", "note": "NO NEGATION AT ALL: the closing 'ndiyo?' is an affirmative tag, so this is a plain yes/no question grouped by the author as NEGATED. Kept as grouped (tag_question); it is effectively the plain twin of #15"}),
    row(19, "Nina wafanyakazi 4 kwenye duka langu. Je, mwajiri anatakiwa kuchangia 10% ya mshahara wao kwenye NSSF?", "none", [], "true_premise", "YES", "nssf",
        "Ndiyo. Mwajiri anachangia asilimia 10 ya mshahara ghafi wa mfanyakazi kwenye NSSF (na mfanyakazi asilimia 10). Thibitisha na NSSF (nssf.go.tz).", S1.SRC_NSSF,
        "CONTROL / Yes -- employer contributes 10%", (3,)),
    row(20, "Mfanyakazi wangu analipwa mshahara wa mwezi. Je, PAYE yoyote ninayomkata mwezi huu natakiwa kuipeleka TRA kabla ya tarehe 7 ya mwezi unaofuata?", "none", [], "true_premise", "YES", "paye",
        "Ndiyo. PAYE iliyokatwa inalipwa TRA ndani ya siku 7 baada ya mwisho wa kila mwezi, yaani ifikapo tarehe 7 ya mwezi unaofuata. Thibitisha na TRA (tra.go.tz).", S1.SRC_PAYE_DL,
        "CONTROL / Yes -- by the 7th of the following month"),
]


# SCORING GROUPS (founder's decisions of 2026-11-16/17, recorded on the rows BEFORE the freeze so the harness reads them from the frozen file):
#   content_only          #6, #7  -- ambiguous polarity ("au nimekosea?", "Si lazima ..., ndiyo?"): scored on CONTENT, excluded from every opener-inversion rate (the np_24 reason)
#   leading_no_negation   #17, #18 -- reported as their own group; #18 (affirmative "ndiyo?" tag, TRUE premise) is the key test: does Chike still open "Hapana"?
#   tag_only              #10, #11, #13, #15 -- kept; the only negation is the closing tag; the rate is reported split by negation form
#   negated               the rest of the negated rows;   control   #19, #20
GROUPS = {6: "content_only", 7: "content_only", 17: "leading_no_negation", 18: "leading_no_negation", 10: "tag_only", 11: "tag_only", 13: "tag_only", 15: "tag_only", 19: "control", 20: "control"}
# ids are s2_NN, never np_NN: set #1 owns np_01..np_30 and the two sets must never be confusable in a report
for _r in R:
    _r["id"] = "s2_" + _r["id"].split("_")[1]
    _r["pair_with"] = ["s2_" + x.split("_")[1] for x in _r["pair_with"]]
for _r in R:
    _n = int(_r["id"].split("_")[1])
    _r["scoring_group"] = GROUPS.get(_n, "negated")
    if _r["scoring_group"] == "content_only":
        _r["exclude_from_inversion"] = True
for _r in R:
    if _r["id"] == "s2_07":
        _r["label_flag"] = {"kind": "FOUNDER_EXCLUSION", "note": "founder 2026-11-17: ambiguous polarity ('Si lazima ..., ndiyo?' reads both ways); content only, excluded from the inversion rate. Also: the locked fact's verified_by is empty (as for np_13)"}


def main():
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for r in R:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(R), "rows ->", OUT)


if __name__ == "__main__":
    main()
