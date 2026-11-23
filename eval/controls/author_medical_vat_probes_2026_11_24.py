# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/medical_vat_probes_2026_11_24.jsonl (R17: probes BOTH ways; R21: a lower bound, authored by the route's author).
    python eval/controls/author_medical_vat_probes_2026_11_24.py"""
import io, json, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "medical_vat_probes_2026_11_24.jsonl")
T = "vat_medical_services"
P = []
def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})

add("mv_01", "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", T, "FOUNDING SPECIMEN (live, 84d8621): the model answered 'Ndiyo ... anatakiwa kusajili VAT'.")
add("mv_02", "Je, huduma za kliniki zinatozwa VAT?", T, "clinic, is it charged.")
add("mv_03", "Do doctors have to register for VAT?", T, "English form.")
add("mv_04", "Daktari binafsi aliyefungua kliniki ndogo anahitaji kusajili VAT?", T, "a clinic owner asking about registration: the statement (exempt on two conditions, registration not settled) is the right answer. First draft wrote none: a wrong expectation.")
add("mv_05", "Huduma za meno zimesamehewa VAT?", T, "dental, exempt?")
add("mv_06", "Muuguzi anayetoa huduma nyumbani anatakiwa kusajili VAT?", T, "nurse, registration (a service outside an approved institution: the statement says both limbs are required).")
add("mv_07", "Daktari mwenye mauzo ya TZS 30,000,000 anatakiwa kusajili VAT?", "none", "a figure: the registration engine.")
add("mv_08", "Dawa zinatozwa VAT?", "none", "medicines are a DIFFERENT exempt item.")
add("mv_09", "Bima ya afya inatozwa VAT?", "none", "health INSURANCE is another exempt item.")
add("mv_10", "Daktari akichelewa kusajili VAT adhabu ni nini?", "none", "a penalty.")
add("mv_11", "Daktari anasajili VAT hiari?", "none", "voluntary registration.")
add("mv_12", "Mhandisi anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", "vat_professional_services", "an ENGINEER stays on the professional-services route (mutual exclusion).")
add("mv_13", "Wakili anatakiwa kusajili VAT bila kujali mauzo?", "vat_professional_services", "a lawyer stays on the professional-services route.")
add("mv_14", "Huduma za afya zinatozwa VAT kiasi gani?", T, "a RATE ask about health services: the exempt statement answers it (not charged when both limbs hold). First draft wrote none: a wrong expectation.")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
