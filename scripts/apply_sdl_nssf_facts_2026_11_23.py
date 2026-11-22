# -*- coding: utf-8 -*-
"""2026-11-23 locked-fact edits (founder-approved texts): THREE NEW facts and ONE correction. Idempotent (R27: an existing object is AMENDED field by field, never replaced).
Run: python scripts/apply_sdl_nssf_facts_2026_11_23.py

  NEW  sdl_domestic_workers_scope           (HEDGE: whether household workers count toward the 10-employee threshold is not settled by any source held; the premises rule is invented)
  NEW  nssf_contributions_age_60            (age 60 = pension eligibility; the Act sets no age at which contributions start or stop; s.20)
  NEW  exemption_category_water_authorities (SDL s.19(1)(k), added by Finance Act 2024 s.112; kept OUT of the index like its nine siblings, absorbed by the consolidated row)
  FIX  sdl_exemption_categories             ('9 categories ... TaESA is NOT present' was read from the R.E.2019 print; R.E.2023 s.19(1) has (a)-(j); FA2024 s.112 adds (k); FA2026 s.98 rewords (a); s.19(3) Gazette power)

SOURCES, all cached and edition-declared in data/source_documents/MANIFEST.json: tra/veta_act_cap82_re2023.pdf (sha256 eac6e92d...), nssf/nssf_act_cap50_re2023.pdf (sha256 2a820e67...), tra/finance_act_2024_no6.pdf, tra/finance_act_2025_no11.pdf,
tra/finance_act_2026_no2.pdf. The wrong_patterns use look-arounds, never a word-boundary escape (R39), and are written to match an ASSERTION of the superseded claim, not the row's own denial of it."""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(REPO, "scripts", "locked_facts.json")
d = json.load(io.open(P, encoding="utf-8"))
TODAY = "2026-11-23"

FA_CHECK = ("FINANCE ACTS CHECKED for amendments to the VETA Act (Cap.82) s.14 and s.19, read directly 2026-11-23: Finance Act 2024 (No.6) Part XXIX s.112 ADDS s.19(1)(k) (water supply and sanitation authority, on payment to casual labourers engaged in "
            "implementation of water and sanitation projects); Finance Act 2025 (No.11): NO amendment to the VETA Act; Finance Act 2026 (No.2) Part XXVII s.98 REWORDS s.19(1)(a) ('by the Government' -> 'through Government subvention'). s.14 (the levy and the "
            "ten-employee condition) is amended by NONE of the three. R.E.2023 s.19(3): the Minister responsible for finance may, by Gazette order and in the public interest, exempt any person.")

NEW = {
    "sdl_domestic_workers_scope": {
        "fact": ("Wafanyakazi wa nyumbani wanahesabiwa kwenye kizingiti cha SDL? Haijathibitishwa. SDL hutozwa kila mwajiri mwenye wafanyakazi 10+; si kwa 'maeneo ya biashara' tu. Thibitisha na TRA. "
                 "Whether a household employer's domestic workers count toward the 10-employee SDL threshold is NOT settled by any source held. The levy is charged on every employer with ten or more employees; the Act has no commercial-premises limb."),
        "correct_value": ("NOT SETTLED by any source held: whether domestic workers count toward the ten-employee threshold -- confirm with TRA. SETTLED: the levy is charged on every employer who has ten or more employees (s.14(1)); the Act contains no "
                          "'commercial premises' / place-of-business limb (the words 'domestic' and 'premises' appear nowhere in it); a household employer is not among the s.19(1) exemptions (a)-(k)."),
        "wrong_patterns": [
            r"sdl\s+inalenga[^.?!]{0,100}(?:maeneo\s+ya\s+biashara|commercial\s+premises)",
            r"sdl\s+(?:applies|is\s+charged|is\s+levied)\s+(?:only\s+)?(?:to|on)\s+(?:employers\s+(?:at|in)\s+)?(?:commercial|business)\s+premises",
            r"wafanyakazi\s+wa\s+nyumbani[^.?!]{0,60}(?:hawaingii|hawahesabiwi)[^.?!]{0,40}(?:kizingiti|sdl)",
        ],
        "primary_source": ("Vocational Education and Training Act Cap.82 R.E.2023 (tra.go.tz copy, data/source_documents/tra/veta_act_cap82_re2023.pdf, sha256 eac6e92d, edition asserted in the manifest from the running page header '[CAP . 82 R.E. 2023]'): "
                           "s.14(1) 'there shall be charged, levied and payable to the Commissioner at the end of every month, from every employer who has in his employment ten or more employees, a levy to be known as the skills and development levy'; "
                           "s.19(1) exemptions; s.19(3). Cross-read: TRA's SDL page ('Mwajiri yeyote mwenye wafanyakazi kumi (10) au zaidi'; counts permanent, temporary, casual staff)."),
        "verified_by": ("Direct read 2026-11-22 and 2026-11-23 of the R.E.2023 text. " + FA_CHECK + " LIMITS: the Act's definition of 'employee' was not located in the extracted text, so whether a household's domestic workers are 'employees' counted toward the ten is "
                        "deliberately NOT asserted either way. CORRECTS: a live reply (build a78f5d0, eval/results/d25_deploy_live_2026_11_22.json) that said 'SDL inalenga waajiri wenye wafanyakazi 10+ katika MAENEO YA BIASHARA (commercial premises)' -- "
                        "a rule that appears in no source held."),
        "status": "HEDGE -- the premises rule is refuted; whether domestic workers count is unresolved (confirm with TRA)",
        "verified_date": TODAY, "verified_as_at": TODAY, "effective_date": "Cap.82 R.E.2023 (s.14); exemptions as amended by FA2024 s.112 and FA2026 s.98",
        "coverage_batch": "2026-11-23 (SDL scope / NSSF age 60)",
    },
    "nssf_contributions_age_60": {
        "fact": ("Michango ya NSSF inakoma ukifika miaka 60? Sheria haisemi hivyo wala kinyume; 60 ni umri wa pensheni (michango 180). Mwajiri hajaondolewa wajibu kwa anayestahili manufaa. Thibitisha na NSSF. "
                 "Age 60 is the NSSF 'pensionable age' (when retirement pension becomes available, with at least 180 monthly contributions; early retirement within five years of it). The Act sets no age at which contributions start or stop, and does not "
                 "relieve a contributing employer of liability for an employee in receipt of or entitled to a benefit."),
        "correct_value": ("age 60 = pensionable age = pension ELIGIBILITY (s.2, s.25, s.29); the Act sets NO age at which contributions begin or end (Parts III-IV, ss.6-20); s.20: the Act 'shall not be construed as relieving a contributing employer from "
                          "liability to make contributions ... in respect of any employee who is in receipt of or becomes entitled to any benefit'. NOT 'contributions continue until 60' and NOT 'contributions stop at 60'. Whether a worker past 60 who keeps working "
                          "is contributed for in practice: confirm with NSSF."),
        "wrong_patterns": [
            r"michango[^.?!]{0,70}(?:huendelea|zinaendelea|inaendelea)[^.?!]{0,40}(?:hadi|mpaka)\s+(?:umri\s+wa\s+)?(?:miaka\s+)?60(?![0-9])",
            r"(?:ukifikisha|ukifika|akifikisha|akifika)\s+(?:umri\s+wa\s+)?(?:miaka\s+)?60(?![0-9])[^.?!]{0,60}(?:hahitaji|huhitaji|hauhitaji)\s+(?:kuchangia|kulipa)",
        ],
        "primary_source": ("National Social Security Fund Act Cap.50 R.E.2023 (nssf.go.tz copy, data/source_documents/nssf/nssf_act_cap50_re2023.pdf, sha256 2a820e67, edition asserted in the manifest from the running page header '[CAP . 50 R.E. 2023]'): "
                           "s.2 'pensionable age means the age of sixty years'; s.25 retirement pension; s.28 lump sum for 'a member who has attained pensionable age and has retired from employment'; s.29 early retirement within five years of pensionable age; "
                           "s.12(1) contributions 'for every contribution period following the date of appointment of an insured person'; s.11(5); s.20."),
        "verified_by": ("Direct read 2026-11-22 and 2026-11-23 of the R.E.2023 text, ss.6-20 end to end and every age reference. No provision in Parts III-IV ties membership or contributions to an age. LIMITS (stated, not hidden): the Social Security Schemes (Benefits) "
                        "Regulations 2018 (GN 467/2018) and the Social Security Act Cap.135 were NOT read and may carry age-related rules; s.25's three limbs are joined by 'and' although limb (c) reads as an early-retirement alternative (a drafting oddity, "
                        "not relied on). CORRECTS: a live reply (build a78f5d0) 'michango ya NSSF huendelea hadi umri wa miaka 60'."),
        "status": "CONFIRMED (the Act is silent on any age cut-off; the claim 'until 60' is unsupported) -- Benefits Regulations GN 467/2018 and Cap.135 not read",
        "verified_date": TODAY, "verified_as_at": TODAY, "effective_date": "Cap.50 R.E.2023",
        "coverage_batch": "2026-11-23 (SDL scope / NSSF age 60)",
    },
    "exemption_category_water_authorities": {
        "fact": ("SDL exemption (k): a water supply and sanitation authority, on payment to casual labourers engaged in implementation of water and sanitation projects -- ADDED by Finance Act 2024 (No.6) s.112, "
                 "which amends the Vocational Education and Training Act Cap.82 s.19(1) by adding paragraph (k) after (j)"),
        "correct_value": "water supply and sanitation authority, on payment to casual labourers on water and sanitation projects -- CONFIRMED, s.19(1)(k) as added by Finance Act 2024 s.112",
        "primary_source": "Vocational Education and Training Act, Cap.82, s.19(1)(k), AS ADDED by Finance Act 2024 (Act No.6 of 2024) s.112",
        "verified_by": ("Direct read 2026-11-23 of tra/finance_act_2024_no6.pdf (edition asserted in the manifest): Part XXIX 'AMENDMENT OF THE VOCATIONAL EDUCATION AND TRAINING ACT, (CAP. 82)', s.112: 'The principal Act is amended in section 19(1) "
                        "by adding immediately after paragraph (j) the following: (k) water supply and sanitation authority on payment to casual labourers engaged in implementation of water and sanitation project.' NOT in the R.E.2023 consolidation, "
                        "which predates it (its s.19(1) ends at (j))."),
        "status": "CONFIRMED 2026-11-23", "verified_as_at": TODAY, "effective_date": "2024-07-01",
    },
}

FIX_KEY = "sdl_exemption_categories"
FIX = {
    "fact": ("SDL exemptions (VETA Act Cap.82 s.19(1), ELEVEN paragraphs as at Finance Act 2026): (a) a Government department or public institution wholly financed THROUGH GOVERNMENT SUBVENTION (wording as amended by Finance Act 2026 s.98); "
             "(b) diplomatic missions; (c) the United Nations and its organisations; (d) international and other foreign institutions dealing with aid or technical assistance; (e) religious institutions whose employees are solely employed to administer places "
             "of worship, give religious instruction/administer religion, or provide public health; (f) charitable organisations (per s.19(2)); (g) registered educational institutions (nursery through higher learning); (h) local government authorities; "
             "(i) intern students under the Tanzania Employment Service Agency (TaESA) programme; (j) farm employers, for employees directly and solely engaged in farming (excluding management and processing staff); (k) a water supply and sanitation "
             "authority, on payment to casual labourers on water and sanitation projects (added by Finance Act 2024 s.112). In addition s.19(3): the Minister responsible for finance may, by Gazette order and in the public interest, exempt any person. "
             "Household employers are in none of these."),
    "correct_value": ("ELEVEN exemption paragraphs: (a)-(j) in Cap.82 R.E.2023 s.19(1) (TaESA interns are (i)), plus (k) water authorities (Finance Act 2024 s.112), with (a) reworded by Finance Act 2026 s.98; plus the s.19(3) Gazette power. "
                      "NOT nine; NOT 'TaESA absent'."),
    "status": "CONFIRMED 2026-11-23 against Cap.82 R.E.2023 s.19(1)-(3) read directly, with Finance Act 2024 s.112 and Finance Act 2026 s.98 read directly (Finance Act 2025: no VETA amendment)",
    "primary_source": ("Vocational Education and Training Act Cap.82 R.E.2023 s.19 (data/source_documents/tra/veta_act_cap82_re2023.pdf, sha256 eac6e92d) as amended by Finance Act 2024 s.112 (adds (k)) and Finance Act 2026 s.98 (rewords (a)); "
                       "source of the 11 individual exemption_category_* keys"),
    "verified_by": ("Direct read 2026-11-23. " + FA_CHECK),
    "verified_as_at": TODAY,
}
FIX_CORRECTION_NOTE_APPEND = (" || CORRECTED 2026-11-23: this fact said '9 categories ... TaESA is NOT present in the 2019 primary text' -- true of the R.E.2019 print it was read from, FALSE of R.E.2023, whose s.19(1) has ten paragraphs (TaESA interns are (i)); "
                              "Finance Act 2024 s.112 then added (k) and Finance Act 2026 s.98 reworded (a); s.19(3) gives the Minister of Finance a Gazette exemption power. R29 mode 2 (an out-of-date edition). The per-category facts already carried "
                              "TaESA as CONFIRMED (2026-09-02) and (a)'s FA2026 wording; the AGGREGATE served in the index had not caught up.")

for k, v in NEW.items():
    if k in d:
        d[k].update(v)                                   # R27: amend, never replace the object
    else:
        d[k] = v
fx = d[FIX_KEY]
for field, val in FIX.items():
    fx[field] = val
keys = fx.get("source_keys") or []
if "exemption_category_water_authorities" not in keys:
    keys.append("exemption_category_water_authorities")
fx["source_keys"] = keys
note = fx.get("correction_note") or ""
if "CORRECTED 2026-11-23" not in note:
    fx["correction_note"] = note + FIX_CORRECTION_NOTE_APPEND
io.open(P, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("applied; facts:", len(d))
