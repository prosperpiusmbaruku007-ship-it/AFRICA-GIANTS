# -*- coding: utf-8 -*-
"""2026-11-17 locked-fact edit (founder-approved, item 4 of the batch): ONE NEW fact, `company_annual_return_deadline`. Idempotent (R27: an existing object is AMENDED field by field, never replaced).
Run: python scripts/apply_annual_return_fact_2026_11_17.py

Primary source is cached and edition-declared in data/source_documents/MANIFEST.json (brela/companies_act_cap212_re2023.pdf, sha256 3bce27e4..., edition 'R.E. 2023' read from the page header).
The wrong_patterns use look-arounds, never a word-boundary escape (R39); tests/test_no_control_characters_in_source.py loads this file's strings and fails on a backspace."""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(REPO, "scripts", "locked_facts.json")
d = json.load(io.open(P, encoding="utf-8"))
TODAY = "2026-11-17"

NEW = {
    "fact": ("Annual return ya BRELA kwa kampuni inapaswa kuwasilishwa lini? Kila mwaka: kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni (au ya return iliyotangulia). "
             "Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni). Si miezi 12 tangu usajili, na si 30 Septemba. "
             "A company's annual return is made up to the anniversary of its incorporation (or of the date of its last return) and delivered within 28 days of that return date; "
             "the company and every officer in default are liable to a fine."),
    "correct_value": ("each annual return is made up to the 'return date' = the anniversary of incorporation (or of the date the last return was made up to) and delivered within 28 days of that return date; "
                      "failing that the company and every officer in default are liable to a fine (and a default fine for continued failure). NOT '12 months from registration', NOT 30 September"),
    "wrong_patterns": [
        r"annual\s+returns?[^.?!]{0,80}(?:ndani\s+ya\s+miezi\s+(?:12|kumi\s+na\s+mbili)|within\s+12\s+months|miezi\s+12\s+(?:kutoka|baada))",
        r"annual\s+returns?[^.?!]{0,60}(?:ifikapo|kufikia|by)\s+(?:30\s+septemba|september\s+30)",
    ],
    "primary_source": ("Companies Act Cap.212 R.E.2023 (brela.go.tz copy, data/source_documents/brela/companies_act_cap212_re2023.pdf, sha256 3bce27e4, edition asserted in the manifest from the running page header "
                       "'[CAP. 212 R.E. 2023]'): Part 'ANNUAL RETURN', s.131(1) 'A company shall deliver to the Registrar, successive annual returns each of which is made up to a date not later than the \"return date\", "
                       "that is- (a) the anniversary of the company's incorporation; or (b) if the company's last return delivered in accordance with this Chapter was made up to a different date, the anniversary of that date'; "
                       "s.131(3) 'Where a company fails to deliver an annual return in accordance with this Chapter within twenty eight days of the return date, the company and every officer of the company who is in default "
                       "shall be liable to a fine and, in the case of a continued failure to deliver an annual return, to a default fine.'"),
    "verified_by": ("Direct read 2026-11-17 of the R.E.2023 text in pdftotext RAW mode (the file carries a 2025 OAG copyright watermark that scrambles layout mode). The 28-day limb already stood in locked fact "
                    "annual_return_form_number ('28-day filing deadline from the return date', s.131), which this fact makes reachable in the asker's own vocabulary. LIMITS: the AMOUNT of the fine was not read "
                    "(the BRELA late-filing penalty of TZS 2,500 a month stays in its own fact); which date is the FIRST return date for a company that changes its return date was not worked through; "
                    "Part XII (foreign companies) has its own return rules and is not covered. CORRECTS: a live reply 'annual return ... hasa ndani ya miezi 12 kutoka tarehe ya usajili wake' (gate c2143c0 and 0e11c3d, "
                    "eval_072) and a training pair (cleaned_pairs_batch_011) that taught 'ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako', repaired 2026-11-17."),
    "status": "CONFIRMED", "verified_date": TODAY, "verified_as_at": TODAY, "effective_date": "Cap.212 R.E.2023",
    "coverage_batch": "2026-11-17 batch 3 (BRELA annual-return deadline)",
}
KEY = "company_annual_return_deadline"
if KEY in d:
    d[KEY].update(NEW)                                   # R27: amend, never replace the object
else:
    d[KEY] = NEW
io.open(P, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("applied; facts:", len(d))
