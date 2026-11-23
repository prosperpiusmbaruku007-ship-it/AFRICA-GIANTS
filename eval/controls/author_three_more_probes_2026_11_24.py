# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/three_more_statements_probes_2026_11_24.jsonl (R17: probes BOTH WAYS; R21: authored by the person who wrote the routes, so a LOWER bound).
`expect` = the topic the question must route to, or "none" = it must reach NO fixed-statement route (or the named older route).
    python eval/controls/author_three_more_probes_2026_11_24.py"""
import io, json, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "three_more_statements_probes_2026_11_24.jsonl")
P = []
def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})

T = "sdl_base"
add("sb_01", "Msingi wa kukokotoa SDL ni nini — posho zinaingia?", T, "natural base ask with allowances.")
add("sb_02", "Are allowances included in the SDL base?", T, "English form.")
add("sb_03", "SDL inakokotolewa kwa jumla ya mishahara ghafi au mshahara wa msingi tu?", T, "gross vs basic.")
add("sb_04", "Bonasi na kamisheni zinahesabiwa kwenye SDL?", T, "bonus + commission.")
add("sb_05", "How does an employer calculate the SDL amount payable each month?", T, "FOUNDING SPECIMEN (live, b96e8a8): the reply said 'gross payroll (cash basis) ... si pamoja na posho za fedha'.")
add("sb_06", "Posho za safari zinahesabiwa kwenye mshahara ghafi wa SDL?", T, "travel allowance.")
add("sb_07", "SDL inakokotolewa kwa mshahara wa TZS 6,000,000 — msingi ni upi?", "none", "a figure: the SDL engine.")
add("sb_08", "SDL ni asilimia ngapi?", "none", "a RATE question: the rate statement, not the base.")
add("sb_09", "Pesa za SDL zinakwenda wapi?", "none", "where the money goes.")
add("sb_10", "Nalipa SDL wapi na kwa fomu gani?", "sdl_how_to_file_pay", "filing route stays on its own route.")
add("sb_11", "Posho za NSSF zinahesabiwa kwenye msingi wa NSSF?", "none", "another levy's base: not the SDL base.")
add("sb_12", "Shule inalipa SDL kwenye posho za walimu?", "sdl_exemptions", "an exemption category: it must reach the EXEMPTIONS statement, not the base (first draft wrote none: a wrong expectation, the older route owns it).")
add("sb_13", "How does TRA conduct an SDL audit and what do they examine?", "sdl_audit_hedge", "audit stays on the audit hedge.")

T = "levy_rates_three"
add("lr3_01", "SDL, NSSF na PAYE ni asilimia ngapi?", T, "FOUNDING SPECIMEN (live, b96e8a8): 'PAYE ni asilimia 8 (0%-270%...) ... 14%'.")
add("lr3_02", "Viwango vya SDL, NSSF na PAYE ni vipi?", T, "plural 'viwango'.")
add("lr3_03", "What are the rates of SDL, NSSF and PAYE?", T, "English form.")
add("lr3_04", "SDL, NSSF na PAYE ni asilimia ngapi ya mshahara wa 800000?", "none", "a figure: the engine / model.")
add("lr3_05", "SDL, NSSF na PAYE zinakatwa kwa mfanyakazi?", "sdl_nssf_paye_party", "the party question stays on the party route.")
add("lr3_06", "SDL, NSSF na PAYE zinalipwa lini?", "levy_deadlines_three", "the deadline question reaches the deadline route, not the rate one.")
add("lr3_07", "SDL, NSSF, PAYE na WCF ni asilimia ngapi?", "none", "a FOURTH levy named.")
add("lr3_08", "SDL na NSSF ni asilimia ngapi?", "none", "two levies: the older rate paths, not this three-levy statement.")
add("lr3_09", "SDL, NSSF na PAYE nikichelewa adhabu ni asilimia ngapi?", "none", "a penalty rate, not the levy rates.")

T = "levy_deadlines_three"
add("ld3_01", "SDL na NSSF na PAYE zinalipwa lini?", T, "FOUNDING SPECIMEN (live, b96e8a8): '...michango ya NSSF, ifikapo tarehe 7'.")
add("ld3_02", "Je, SDL, NSSF na PAYE zote zinalipwa tarehe 7?", T, "premise with the NSSF-7th error: the statement corrects it.")
add("ld3_03", "Tarehe ya mwisho ya SDL, NSSF na PAYE ni ipi?", T, "last-date form.")
add("ld3_04", "When are SDL, NSSF and PAYE due?", T, "English form.")
add("ld3_05", "SDL na PAYE zinalipwa lini?", "sdl_paye_deadline", "two levies stay on the two-levy route.")
add("ld3_06", "SDL, NSSF na PAYE zinalipwa wapi?", "none", "where to pay: model.")
add("ld3_07", "SDL, NSSF na PAYE nikichelewa kulipa adhabu ni nini?", "none", "a penalty.")
add("ld3_08", "SDL, NSSF, PAYE na WCF zinalipwa lini?", "none", "a fourth levy.")
add("ld3_09", "Ninaweza kulipa SDL, NSSF na PAYE siku tofauti?", "none", "a permission ask.")

with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
