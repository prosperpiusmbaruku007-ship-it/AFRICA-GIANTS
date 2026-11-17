# -*- coding: utf-8 -*-
"""Builds eval/fidelity/d16_followup_probes_2026_11_17.jsonl (R17: the founding specimens are VERBATIM live replies; the must-pass limbs the founder named are the clean half).
    python eval/fidelity/make_d16_probes_2026_11_17.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = []


def add(i, g, q, b, e, why):
    P.append({"id": i, "guard": g, "question": q, "body": b, "expect": e, "guards_against": why})


LQ = "Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?"
add("d16_lic_01", "licence", LQ, "Hapana, leseni ya biashara huisha kila mwaka ifikapo tarehe 30 Juni. Huwezi kuendelea nayo bila kuihuisha. Thibitisha na BRELA (brela.go.tz).", "flag", "s2_07 live, VERBATIM: 30 June asserted as the expiry (the pre-2014 rule; Cap.101 R.E.2023 s.7(1) is twelve months from issuance)")
add("d16_lic_02", "licence", "Leseni ya biashara ya LGA inahuishwa lini?", "Kila leseni ya biashara huisha tarehe 30 Juni kila mwaka, kwa hiyo huhuishwa kila mwaka kabla ya tarehe hiyo (Sheria ya Leseni za Biashara). Thibitisha na mamlaka ya leseni (halmashauri yako).", "flag", "np_batch live: the OLD restatement text itself -- the guard used to REQUIRE this sentence")
add("d16_lic_03", "licence", "Leseni ya biashara inaisha lini?", "Leseni ya biashara inaisha tarehe 31 Desemba kila mwaka.", "flag", "a different fixed calendar date is equally wrong")
add("d16_lic_04", "licence", "Leseni ya biashara inaisha lini?", "Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa.", "clean", "the corrected statement")
add("d16_lic_05", "licence", LQ, "Hapana. Leseni ya biashara ni halali kwa miezi 12 tangu ilipotolewa, si tarehe 30 Juni. Thibitisha na halmashauri yako.", "clean", "a correction that names the old date under negation (the asker's premise) must pass")
add("d16_lic_06", "licence", "Leseni yangu ilitolewa 15 Machi 2026, itaisha lini?", "Leseni yako ya biashara ni halali kwa miezi 12, hadi 14 Machi 2027.", "clean", "a FULL dated computation is not a fixed calendar expiry")
add("d16_lic_07", "licence", "Return ya kodi ya mapato ya mtu binafsi ni lini?", "Return iwasilishwe ndani ya miezi 6, yaani kufikia 30 Juni ya mwaka unaofuata.", "clean", "30 June as a RETURN date on a question that is not about a licence")
add("d16_lic_08", "licence", "Leseni ya biashara inaisha lini?", "Kila leseni huisha tarehe 30 Juni. Ada hulipwa kila mwaka.", "flag", "the specimen shape without any authority tail")

DQ = "Kampuni yangu haijaorodheshwa kwenye soko la hisa la DSE. Nikigawa gawio kwa wanahisa, withholding tax yake ni 10%, si ndiyo?"
add("d16_div_01", "dividend", DQ, "Kwa kampuni ambayo haijaorodheshwa kwenye soko la hisa la DSE, kiwango cha withholding tax kwa gawio ni 10% kwa wakazi na 15% kwa wasio wakazi. Thibitisha na tra.go.tz.", "flag", "wrongtopic live, VERBATIM: 15% attached to a non-resident's dividend")
add("d16_div_02", "dividend", "Gawio kwa mwekezaji wa nje linakatwa kiasi gani?", "Gawio kwa asiye mkazi linakatwa asilimia 15.", "flag", "the plain wrong statement")
add("d16_div_03", "dividend", "Ada ya huduma kwa kampuni ya nje ni asilimia ngapi?", "Kodi ya zuio kwa ada ya huduma kwa asiye mkazi ni asilimia 15.", "clean", "MUST PASS (founder): a non-resident SERVICE FEE at 15% is correct (para 4(c)(i))")
add("d16_div_04", "dividend", "Gawio na malipo mengine kwa mgeni yanakatwa kiasi gani?", "Malipo mengine kwa asiye mkazi yanakatwa asilimia 15.", "clean", "MUST PASS (founder): 'other payments' at 15% (para 4(b)(iv)); the dividend subject is in the QUESTION")
add("d16_div_05", "dividend", DQ, "Gawio hukatwa 5% au 10%; 15% si kiwango cha gawio, hata kwa asiye mkazi.", "clean", "MUST PASS (founder): the correct dividend statement (it names 15% and a non-resident under negation)")
add("d16_div_06", "dividend", DQ, "Kiwango ni 10% kwa wakazi na 10% kwa wasio wakazi. Thibitisha na tra.go.tz.", "clean", "the correct figures for both payees")
add("d16_div_07", "dividend", "Royalty kwa asiye mkazi na gawio?", "Mrabaha kwa asiye mkazi ni asilimia 15; gawio ni 10%.", "clean", "a royalty at 15% beside a correct dividend rate")
add("d16_div_08", "dividend", "Mkurugenzi asiye mkazi analipwa ada, gawio pia?", "Ada za mkurugenzi kwa asiye mkazi: asilimia 15.", "clean", "a non-resident DIRECTOR's fee at 15% (para 4(a)(iii))")

RQ = "Muda wa mwisho wa kuwasilisha return ya kodi ya mapato ya kampuni TRA ni lini?"
add("d16_ret_01", "return", RQ, "Kampuni lazima iwasilishe return ya kodi ya mapato ndani ya miezi 12 baada ya mwisho wa mwaka wake wa mapato. Kwa kampuni yenye mwaka wa mapato wa kalenda, muda wa mwisho ni 30 Septemba ya mwaka unaofuata. Thibitisha na TRA.", "flag", "wrongtopic live, VERBATIM: 12 months and 30 September as the company return deadline")
add("d16_ret_02", "return", RQ, "Return ya kampuni inawasilishwa kufikia 30 Septemba.", "flag", "30 September alone, with the return named")
add("d16_ret_03", "return", "Return ya kodi ya mapato ya kampuni ni lini, na awamu?", "Return iwasilishwe ndani ya miezi 6. Awamu ya tatu ya kodi ya mapato ni 30 Septemba.", "clean", "MUST PASS (founder): provisional-tax instalment dates incl. 30 September")
add("d16_ret_04", "return", "Return ya kodi ya mapato ya kampuni ni lini?", "Mauzo ya miezi 12 yakizidi TZS 200,000,000 lazima ujisajili VAT, na return ya VAT ni tarehe 20.", "clean", "MUST PASS (founder): the VAT 12-month threshold")
add("d16_ret_05", "return", "Return ya kodi ya mapato ya kampuni ni lini, na severance?", "Severance inalipwa baada ya miezi 12 ya kazi mfululizo.", "clean", "MUST PASS (founder): severance's 12 months")
add("d16_ret_06", "return", RQ, "Return ya kampuni iwasilishwe ndani ya miezi 6; kampuni ya kawaida kufikia 30 Juni ya mwaka unaofuata.", "clean", "MUST PASS (founder): the correct return statement")
add("d16_ret_07", "return", RQ, "Si miezi 12 wala 30 Septemba; return ya kampuni ni miezi 6 baada ya mwisho wa mwaka.", "clean", "a correction that names both stale values under negation")
add("d16_ret_08", "return", "Return ya kodi ya mapato ya mtu binafsi ni lini?", "Return ya mtu binafsi ni ndani ya miezi 6 baada ya mwisho wa mwaka.", "clean", "an individual return (the subject is not a company)")

SQ = "Malipo ya fidia ya kuachishwa kazi (severance pay) hayapigwi kodi — je, ni kweli?"
add("d16_sev_01", "severance", SQ, "Hapana, si kweli kabisa. Sehemu ya malipo ya fidia ya kuachishwa kazi inaweza kuwa exempt kutokana na sheria ya Tanzania, lakini si yote. Sehemu inayozidi kiwango cha chini cha kisheria kinachotajwa inatozwa kodi ya asilimia 15 (PAYE). Thibitisha na TRA (tra.go.tz).", "flag", "np_batch live, VERBATIM: a flat 15% PAYE on severance")
add("d16_sev_02", "severance", "Severance inakatwa kodi gani?", "Severance inakatwa PAYE ya asilimia 15.", "flag", "the plain wrong statement")
add("d16_sev_03", "severance", "Mfanyakazi asiye mkazi analipwa severance, kodi ni ngapi?", "Kwa asiye mkazi kodi ya zuio ni asilimia 15.", "clean", "MUST PASS (founder): a NON-RESIDENT's 15% (para 4(a)(ii)); the question names a non-resident")
add("d16_sev_04", "severance", "Mkurugenzi akiachishwa kazi, severance na ada zake zinakatwa kodi gani?", "Ada za mkurugenzi zinakatwa asilimia 15.", "clean", "MUST PASS (founder): directors' fees at 15% (para 4(a)(iii))")
add("d16_sev_05", "severance", SQ, "Severance ni mapato ya ajira na hakuna kiwango maalum cha asilimia 15; inakatwa PAYE kwa viwango vya kawaida.", "clean", "the correct statement (names 15% under negation)")
add("d16_sev_06", "severance", "Severance inakatwa kodi gani?", "Severance huchangiwa NSSF asilimia 15 kwa baadhi ya kesi.", "clean", "another levy in the sentence")
add("d16_sev_07", "severance", "Severance inakatwa kodi gani?", "PAYE ni 0% hadi 30% kulingana na bendi za mshahara.", "clean", "no 15% at all")

GQ = "Mwajiri anagundua vipi kiwango cha mshahara wa chini cha GN 605A kinachofaa kwa kila mfanyakazi wake?"
add("d16_pkf_01", "pkf", GQ, "Kila mwajiri lazima atumie jedwali la GN 605A lililotolewa na PKF Eastern Africa kwa kila mfanyakazi wake. Thibitisha na Ofisi ya Kazi (kazi.go.tz).", "repair", "np_batch live, VERBATIM: PKF named as the issuer of GN 605A")
add("d16_pkf_02", "pkf", "PKF ilitoa nini kuhusu GN 605A?", "PKF ilitoa jedwali la GN 605A.", "repair", "the active-voice form")
add("d16_pkf_03", "pkf", GQ, "Kulingana na uchambuzi wa PKF Eastern Africa, wastani wa ongezeko la GN 605A ni 33.4%.", "clean", "an ANALYSIS cited as an analysis is not an issuer claim")
add("d16_pkf_04", "pkf", "Kodi ya kampuni ni kiasi gani?", "Ripoti ya PKF ilichapishwa mwaka 2025 kuhusu kodi ya kampuni.", "clean", "a sentence not about GN 605A is never touched")

AQ = "Nataka leseni ya biashara ya duka langu, nipate wapi?"
add("d16_auth_01", "licauth", AQ, "Omba leseni ya biashara kupitia mfumo wa leseni. Thibitisha na BRELA (brela.go.tz).", "repair", "s2_07's shape: a lone BRELA citation for an ordinary trader")
add("d16_auth_02", "licauth", AQ, "Omba leseni ya biashara kupitia mfumo wa leseni. Thibitisha na TRA (tra.go.tz).", "repair", "a tax authority named for a licence")
add("d16_auth_03", "licauth", AQ, "Omba leseni kwa halmashauri yako. Thibitisha na BRELA (brela.go.tz).", "clean", "already names the council: not rewritten (idempotence)")
add("d16_auth_04", "licauth", AQ, "Thibitisha na BRELA (brela.go.tz) au TRA (tra.go.tz).", "clean", "two authorities: not judged")
add("d16_auth_05", "licauth", "Nawezaje kusajili kampuni?", "Sajili kampuni BRELA. Thibitisha na BRELA (brela.go.tz).", "clean", "a company-registration question is not a licence question")
add("d16_auth_06", "licauth", "Leseni ya biashara inahitaji TIN?", "Ndiyo, TIN inahitajika. Thibitisha na TRA (tra.go.tz).", "clean", "a licence question carrying a tax cue is ambiguous: not judged")

if __name__ == "__main__":
    with io.open(os.path.join(HERE, "d16_followup_probes_2026_11_17.jsonl"), "w", encoding="utf-8") as f:
        for p in P:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(len(P), "probes written")
