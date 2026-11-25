# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/residency_probes_2026_11_25.jsonl: the paye_residency statement route, probes BOTH ways (R17; R21: a lower bound, so the SWEEP over every held question is the other half).
`expect` is the fixed-statement topic the question must reach, `none`, or `not:<topic>`.
    python eval/controls/author_residency_probes_2026_11_25.py"""
import io
import json
import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "residency_probes_2026_11_25.jsonl")
R = "paye_residency"
P = []


def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})


add("rs_01", "Does a foreign employee pay PAYE at a different rate from a citizen?", R, "FOUNDING SPECIMEN (live, build 16f0a43): the model answered 'a foreigner ... pays a flat rate of 15%'.")
add("rs_02", "Mgeni anayefanya kazi Tanzania analipa PAYE vipi?", R, "Swahili, the asker's word 'mgeni'.")
add("rs_03", "Mfanyakazi mgeni analipa PAYE kwa kiwango gani, tofauti na raia?", R, "'kiwango' + foreign: the rate route vetoes foreign / citizen words, so the two are exclusive.")
add("rs_04", "Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?", R, "the 183-day limb, in the asker's words (found by the sweep of the money regex: '183,' was read as a money figure and vetoed it).")
add("rs_05", "PAYE ya mfanyakazi asiye mkazi ni asilimia ngapi?", R, "EXPECT INVERTED 2026-11-25 (was paye_rate in three_routes_probes pr_05): every RESIDENCY word is now the residency route's, which also states the non-resident 15% (final) and what makes a person non-resident.")
add("rs_06", "Tofauti ya mkaazi wa kikodi na asiye mkaazi kwenye PAYE ni nini?", R, "the difference question, in the founder's terminology.")
add("rs_07", "Is a resident foreigner taxed on the PAYE bands?", R, "the RESIDENT-FOREIGNER question the founder named for the live check. (A first draft expected the band route; with the band-word veto the question reached NO route at all.)")
add("rs_08", "Expatriate employee: PAYE flat 15% or progressive?", R, "'expatriate'.")
add("rs_09", "Mgeni mwenye makazi ya kudumu Tanzania analipa PAYE kwa bendi au 15%?", R, "the resident-foreigner question with a BAND word in it. EXPECT CHANGED 2026-11-25 (first draft: the band route; found by the probe run: the band route needs its own ask word, so the question reached the MODEL, the very path the live defect came from). The residency route now owns every residency question and the band route vetoes residency words, so they stay exclusive.")
add("rs_10", "Bendi za PAYE kwa wageni ni zipi?", R, "band words AND foreign: the residency statement answers the regime (bands for a resident, 15% for a non-resident); LIMIT, stated: it does not print the band table (the plain band question does).")
add("rs_10b", "Bendi za PAYE ni zipi?", "paye_band_table", "no residency word: the band route still owns the plain band question (control).")
add("rs_11", "Mshahara wa mgeni TZS 800,000, PAYE ni kiasi gani?", "none", "a FIGURE: the PAYE engine, never a statement.")
add("rs_12", "Mkurugenzi mgeni, ada ya mkurugenzi ni asilimia ngapi?", "not:" + R, "DIRECTOR'S FEES are another 15% withholding; the founder's live negative.")
add("rs_13", "Kiwango cha PAYE Kenya ni asilimia ngapi?", "not:" + R, "ANOTHER COUNTRY.")
add("rs_14", "Ninahitaji kibali cha ukaazi cha uhamiaji, PAYE inaathirikaje?", "not:" + R, "IMMIGRATION: a residence PERMIT is not tax residency (the founder's terminology point); this question is not the statement's.")
add("rs_15", "PAYE ni asilimia ngapi?", "paye_rate", "no residency word: the rate route keeps it (exclusive).")
add("rs_16", "Mgeni analipa PAYE mwezi Januari kiasi gani?", "not:" + R, "a named month and an amount ask.")
add("rs_17", "PAYE inakokotolewa kwa mshahara wa msingi kwa mgeni?", "not:" + R, "the BASE vocabulary.")
add("rs_18", "NSSF ya mgeni ni kiasi gani, na PAYE?", "not:" + R, "another levy named.")
add("rs_19", "Mfanyakazi asiye mkazi analipa PAYE lini?", "not:" + R, "a DATE ask.")
add("rs_20", "Kodi ya kampuni ya kigeni ni asilimia ngapi?", "not:" + R, "corporate tax, no PAYE word.")
# ---- the wrong-topic classes found by READING the first sweep (55 diversions, 24 wrong) ----
add("rs_21", "A foreign employee confused about PAYE law: where can they get help?", "not:" + R, "WHERE / HELP.")
add("rs_22", "A foreign employee has resigned: when must the employer pay the final PAYE?", "not:" + R, "an English 'when', leaving.")
add("rs_23", "A foreign employee leaves Tanzania before year end: how is their PAYE handled?", "not:" + R, "LEAVING mid-year.")
add("rs_24", "A foreign employee of an NGO: does PAYE apply?", "not:" + R, "an NGO / exemption question.")
add("rs_25", "A foreign employee says they pay taxes in the UK: can they avoid Tanzania PAYE?", "not:" + R, "ANOTHER COUNTRY'S TAX and avoidance (the DTA omission was accepted by the founder, so a treaty question must not get this statement).")
add("rs_26", "Can a foreign employee claim to be self-employed to avoid PAYE?", "not:" + R, "AVOIDANCE.")
add("rs_27", "A foreign employee with company share options: is the value subject to PAYE?", "not:" + R, "SHARE OPTIONS.")
add("rs_28", "A foreign employee's salary paid outside Tanzania: does Tanzania PAYE apply?", "not:" + R, "income paid OUTSIDE Tanzania (a source question).")
add("rs_29", "Does a foreign employee need a Tanzania TIN for PAYE?", "not:" + R, "a TIN.")
add("rs_30", "Does redundancy pay for a foreign employee carry PAYE?", "not:" + R, "REDUNDANCY.")
add("rs_31", "Is the PAYE personal relief available to foreign employees?", "not:" + R, "PERSONAL RELIEF.")
add("rs_32", "An employer pays PAYE on behalf of a foreign employee: does the value of that tax also carry PAYE?", "not:" + R, "TAX ON TAX.")
add("rs_33", "Why is it important to handle a foreign employee's PAYE correctly?", "not:" + R, "a WHY question.")
add("rs_34", "Does a foreign (expatriate) employee in Tanzania pay PAYE like a Tanzanian?", R, "KEPT by the sweep's reading: the statement answers it.")
add("rs_35", "PAYE for a non-resident employee is 30%, right?", R, "KEPT by the sweep's reading: a PREMISE check; the statement states the 15% (final) and the test for non-residence.")
add("rs_36", "Je, kuna tofauti kati ya kiwango cha kodi cha kwanza na cha pili kwa PAYE?", "paye_rate", "REGRESSION found by the sweep: my 'tofauti' veto on paye_rate took a plain band-difference question off the rate route; removed.")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
