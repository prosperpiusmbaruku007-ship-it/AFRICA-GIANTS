# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/director_probes_2026_11_25.jsonl: the director_fees_wht statement route, probes BOTH ways (R17; R21: a lower bound, so the SWEEP over every held question is the other half).
    python eval/controls/author_director_probes_2026_11_25.py"""
import io
import json
import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "director_probes_2026_11_25.jsonl")
D = "director_fees_wht"
P = []


def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})


add("df_01", "WHT kwa ada ya mkurugenzi ni asilimia ngapi?", D, "the plain rate question.")
add("df_02", "Mkurugenzi mgeni anapokea ada ya mkurugenzi, WHT ni asilimia ngapi?", D, "FOUNDING SPECIMEN (live, build c50345c): the model said 'kwa wasio-wakazi ni asilimia 15', omitting the resident case. It was a model-path NEGATIVE of the last window; the statement now owns it.")
add("df_03", "Director's fees: is the withholding final for a non-resident?", D, "English, NON-RESIDENT, final.")
add("df_04", "Ada ya mkurugenzi inakatwa PAYE au WHT?", D, "PAYE named in the question is allowed (the route is levy-exempt).")
add("df_05", "Ada ya mkurugenzi kwa mkaazi wa kikodi inakatwa zuio asilimia ngapi?", D, "RESIDENT, in the founder's terminology.")
add("df_06", "Ada ya mkurugenzi kwa asiye mkaazi inakatwa zuio asilimia ngapi, na ni ya mwisho?", D, "NON-RESIDENT and 'final'.")
add("df_07", "Ada ya mkurugenzi wa muda wote inakatwa vipi?", D, "the FULL-TIME phrasing the founder named for the live check: the statement says the rate does not concern him as the Act defines him, and sends him to TRA. (A first draft vetoed 'muda' as a date word and sent it to the model: found by the probe run.)")
add("df_08", "WHT on directors' fees for residents: is it final?", D, "English, RESIDENT, final.")
add("df_09", "Kiwango cha zuio kwa ada za wakurugenzi ni kipi?", D, "the plural 'ada za wakurugenzi'.")
add("df_10", "Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?", "none", "a FIGURE: a computation, never a statement.")
add("df_11", "Gawio linakatwa zuio asilimia ngapi?", "not:" + D, "no director word: dividends are another withholding.")
add("df_12", "Mkurugenzi analipa PAYE vipi?", "not:" + D, "no 'ada' phrase: a director's SALARY question is not the fee statement.")
add("df_13", "Adhabu ya kutokata WHT kwenye ada ya mkurugenzi ni nini?", "not:" + D, "a PENALTY.")
add("df_14", "Nawasilisha lini WHT ya ada ya mkurugenzi?", "not:" + D, "a DATE.")
add("df_15", "Ada ya mkurugenzi nchini Kenya inakatwa asilimia ngapi?", "not:" + D, "ANOTHER COUNTRY.")
add("df_16", "Ada ya mkurugenzi ya Januari inakatwa asilimia ngapi?", "not:" + D, "a named month.")
add("df_17", "Mkurugenzi mgeni analipa PAYE kwa bendi au 15%?", "paye_residency", "no director-fee phrase: the residency route owns it (exclusive).")
add("df_18", "Ada ya mkurugenzi na NSSF zinakatwa kiasi gani?", "not:" + D, "another levy named.")
add("df_19", "Ada ya mkurugenzi na gawio zinakatwa zuio asilimia ngapi?", "not:" + D, "two withholdings in one question: the statement answers only one.")
add("df_20", "Mkurugenzi mgeni asiye mkazi analipa PAYE asilimia ngapi?", "paye_residency", "no 'ada': the residency route owns it (exclusive).")
add("df_21", "Mkurugenzi wa kampuni anateuliwa vipi?", "none", "appointment, no fee.")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
