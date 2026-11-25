# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/three_routes_probes_2026_11_25.jsonl: the PAYE-rate, combined health+medicines and WCF-base statement routes, probes BOTH ways (R17; R21: a lower bound, authored by the routes' author, so the SWEEP over every held question is the other half).
`expect` is the fixed-statement topic the question must reach, `none`, or `not:<topic>`.
    python eval/controls/author_three_routes_probes_2026_11_25.py"""
import io
import json
import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "three_routes_probes_2026_11_25.jsonl")
PR, HM, WB = "paye_rate", "vat_health_and_medicines", "wcf_base"
P = []


def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})


# ---- PAYE rate -------------------------------------------------------------------------------------------------------------------------------------------
add("pr_01", "PAYE ni asilimia ngapi?", PR, "FOUNDING SPECIMEN (live, build ff68073): 'asilimia 30 ... punguzo'.")
add("pr_02", "Kiwango cha PAYE ni kipi?", PR, "the singular 'kiwango' form.")
add("pr_03", "What is the PAYE rate in Tanzania?", PR, "English form.")
add("pr_04", "Kodi ya PAYE ni asilimia ngapi kwa mfanyakazi?", PR, "a longer natural phrasing.")
add("pr_05", "PAYE ya mfanyakazi asiye mkazi ni asilimia ngapi?", "paye_residency", "EXPECT CHANGED 2026-11-25 (was paye_rate: a non-resident rate ask). Every RESIDENCY word is now the paye_residency route's, which states the 15% (final) AND what makes a person non-resident; paye_rate vetoes residency words so the two stay exclusive.")
add("pr_06", "PAYE ya mshahara wa TZS 800,000 ni asilimia ngapi?", "not:" + PR, "a FIGURE: the PAYE engine, never a statement.")
add("pr_07", "Bendi za PAYE ni zipi?", "paye_band_table", "a BAND word stays on the band-table route (the two are exclusive).")
add("pr_08", "Viwango vya PAYE ni vipi?", "paye_band_table", "the plural 'viwango' is the band route's word.")
add("pr_09", "PAYE na SDL ni asilimia ngapi?", "not:" + PR, "another levy named: a two-levy rate question the rate statement does not answer.")
add("pr_10", "PAYE inalipwa lini na ni asilimia ngapi?", "not:" + PR, "a DATE limb.")
add("pr_11", "PAYE inakokotolewa kwa mshahara wa msingi tu?", "paye_base", "the BASE question stays on the base route.")
add("pr_12", "Adhabu ya kuchelewa kulipa PAYE ni asilimia ngapi?", "not:" + PR, "a PENALTY rate.")
add("pr_13", "Kodi ya kampuni ni asilimia ngapi?", "not:" + PR, "corporate tax, no PAYE word.")
add("pr_14", "Cheti cha PAYE ni asilimia ngapi?", "not:" + PR, "a certificate word.")
add("pr_15", "Kiwango cha PAYE Kenya ni asilimia ngapi?", "not:" + PR, "ANOTHER COUNTRY: found by the sweep (two held questions); the Tanzanian bands must never answer it.")
add("pr_16", "Does a foreign employee pay PAYE at a different rate from a citizen?", "not:" + PR, "FOREIGN is not non-resident: found by the sweep.")
add("pr_17", "Last week PAYE figure, just add ten percent on it - what is the new answer?", "not:" + PR, "an ARITHMETIC TRAP: found by the sweep (a rate statement answers nothing here).")
add("pr_18", "Daraja la pili la PAYE linatoza asilimia ngapi?", PR, "a band-2 rate ask in the asker's words: the table answers it (kept by the sweep's reading).")
add("pr_19", "Kiwango cha juu kabisa cha PAYE Tanzania ni asilimia ngapi?", PR, "the top rate: the table answers it.")
# ---- combined health services + medicines ----------------------------------------------------------------------------------------------------------------
add("hm_01", "Huduma za afya zinatozwa VAT? Na dawa je?", HM, "FOUNDING SPECIMEN (live, build ff68073): the merged follow-up answered the medicines limb only.")
add("hm_02", "Are health services and medicines VAT-exempt?", HM, "English form.")
add("hm_03", "Kliniki inatozwa VAT kwa huduma na dawa?", HM, "a clinic: both limbs in one clause.")
add("hm_04", "Daktari anatozwa VAT kwenye dawa anazoagiza?", HM, "EXPECT INVERTED 2026-11-25 (was none in two_statements_probes mp_12: with no combined route a doctor-and-medicines question had no owner); the combined statement answers both limbs.")
add("hm_05", "Huduma za afya zinatozwa VAT?", "vat_medical_services", "health ALONE stays on the medical-services route (exclusive).")
add("hm_06", "Dawa zinatozwa VAT?", "vat_medicines", "medicines ALONE stays on the medicines route (exclusive).")
add("hm_07", "Hospitali inatakiwa kusajili VAT na dawa zinatozwa VAT?", "none", "REGISTRATION: not settled by the Act, neither statement answers it.")
add("hm_08", "Huduma za afya na dawa za TZS 5,000,000, VAT ni ngapi?", "none", "a FIGURE.")
add("hm_09", "Bima ya afya na dawa zinatozwa VAT?", "none", "health INSURANCE is another exempt item.")
add("hm_10", "Huduma za afya na dawa zinazoingizwa kutoka nje zinatozwa VAT?", "none", "IMPORTS: the statements do not cover them.")
add("hm_11", "Mhandisi na dawa, VAT inatozwa?", "not:" + HM, "no health word.")
# ---- WCF base --------------------------------------------------------------------------------------------------------------------------------------------
add("wb_01", "WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?", WB, "FOUNDING SPECIMEN (live, build ff68073): 'posho zinazolipwa kila mwezi' where the fact says FIXED.")
add("wb_02", "Msingi wa michango ya WCF ni nini?", WB, "the base, plainly.")
add("wb_03", "Is WCF calculated on basic salary only or on allowances too?", WB, "English form.")
add("wb_04", "Posho zinaingia kwenye WCF?", WB, "allowances, the asker's word.")
add("wb_05", "WCF inakokotolewa kwa fedha taslimu tu?", WB, "the old 'cash' framing the fact corrected.")
add("wb_06", "WCF ni asilimia 0.5 ya mshahara wa TZS 2,000,000, ni kiasi gani?", "not:" + WB, "a FIGURE.")
add("wb_07", "Ajali ya kazini WCF inalipa nini?", "not:" + WB, "an ACCIDENT / claim question.")
add("wb_08", "Nasajili WCF wapi, na posho zinaingia?", "not:" + WB, "a where / registration ask.")
add("wb_09", "WCF inalipwa lini?", "not:" + WB, "a DEADLINE.")
add("wb_10", "NSSF na WCF zinakatwa kwenye nini?", "not:" + WB, "another levy named.")
add("wb_11", "Sekta binafsi WCF inakatwa kwenye nini?", "not:" + WB, "a sector word: the sector rate question is not the base question.")
add("wb_12", "PAYE inakatwa kwenye nini, posho zinaingia?", "paye_base", "the PAYE base stays on the PAYE-base route (exclusive).")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
