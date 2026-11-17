# -*- coding: utf-8 -*-
"""WRITE THE TWO SIDECAR CORRECTION FILES (founder's instruction 2026-11-17: the frozen sets are NOT edited; a label or answer correction goes in a sidecar next to each).

    python eval/fidelity/negated_premise_heldout/make_sidecars_2026_11_17.py

Each sidecar pins the sha256 of the FROZEN set it corrects, so the rescore refuses to run if the frozen file was touched. Both corrections have ONE cause: the locked fact business_licence_expiry_30_june stated the
pre-2014 rule (every licence expires 30 June); Business Licensing Act Cap.101 R.E.2023 s.7(1) makes a licence valid twelve months from the date of issuance. The two rows were AUTHORED OUTSIDE THIS REPOSITORY (np_13 by a
claude.ai advisor session, s2_07 by ChatGPT) from that fact, so the error spread into the test labels -- and np_13's own `label_flag` had warned on 2026-11-16 that the fact's verified_by was EMPTY and the Act should be
re-read before the row was trusted as a key."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = ("Business Licensing Act Cap.101 R.E.2023 s.7(1) 'A business licence granted under this Act shall be valid for a period of twelve months from the date of issuance' "
            "(data/source_documents/brela/business_licensing_act_cap101_re2023.pdf, sha256 650aa1c7); the 30 June rule is Cap.208 as at 31 July 2002 s.7 (superseded in the manifest). "
            "Locked fact business_licence_expiry_30_june corrected 2026-11-17.")
WHEN = "2026-11-17"


def pin(frozen):
    d = json.load(io.open(os.path.join(HERE, frozen), encoding="utf-8"))
    return {"frozen_file": frozen, "frozen_sha256": d["sha256"], "authored_file": d["file"]}


SET1 = dict(pin("FROZEN.json"), recorded=WHEN, why_a_sidecar="the frozen set is not edited (founder, 2026-11-17); this file records what the corrected key says.", corrections=[{
    "id": "np_13",
    "change": "ANSWER TEXT only; the label (false_premise / NO) is UNCHANGED",
    "original": {"premise_label": "false_premise", "correct_polarity": "NO",
                 "correct_answer_sw": "Hapana. Kila leseni ya biashara huisha tarehe 30 Juni kila mwaka na lazima ihuishwe. Thibitisha na mamlaka ya leseni."},
    "corrected": {"premise_label": "false_premise", "correct_polarity": "NO",
                  "correct_answer_sw": "Hapana. Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa, kisha lazima ihuishwe; haidumu mpaka uifute. Thibitisha na mamlaka ya leseni."},
    "reason": "the premise ('a licence never expires') is still false, so polarity NO stands; the stated expiry was the stale 30 June rule",
    "evidence": EVIDENCE}])
SET2 = dict(pin("FROZEN_set2.json"), recorded=WHEN, why_a_sidecar="the frozen set is not edited (founder, 2026-11-17); this file records what the corrected key says.", corrections=[{
    "id": "s2_07",
    "change": "LABEL: false_premise / NO -> true_premise / YES, and the answer text. `exclude_from_inversion` is NOT changed by this sidecar (the founder's 2026-11-17 exclusion for ambiguous polarity stands; the rescore reports the rates both with it kept and with it lifted)",
    "original": {"premise_label": "false_premise", "correct_polarity": "NO",
                 "correct_answer_sw": "Hapana. Kila leseni ya biashara huisha tarehe 30 Juni kila mwaka na lazima ihuishwe, hata ile uliyoipata mwaka huu. Thibitisha na mamlaka ya leseni."},
    "corrected": {"premise_label": "true_premise", "correct_polarity": "YES",
                  "correct_answer_sw": "Ndiyo. Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa, si tarehe maalum ya kalenda; kwa hiyo leseni uliyoipata mwaka huu huhitaji kuihuisha tarehe 30 Juni, bali miezi 12 baada ya kutolewa. Thibitisha na mamlaka ya leseni."},
    "reason": "the premise ('a licence obtained this year need not be renewed before 30 June') is TRUE under a twelve-months-from-issuance rule",
    "evidence": EVIDENCE}])

for name, obj in (("FROZEN_sidecar_2026_11_17.json", SET1), ("FROZEN_set2_sidecar_2026_11_17.json", SET2)):
    io.open(os.path.join(HERE, name), "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1))
    print("wrote", name)
