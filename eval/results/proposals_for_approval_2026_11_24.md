# Proposals awaiting approval, 2026-11-24 (NOTHING below is encoded, packaged or deployed)

## A. Medical services and VAT (item 6) -- SOURCE FOR YOUR REVIEW

**Source (edition asserted):** `data/source_documents/tra/vat_act_cap148_re2023.pdf`, `assert_edition` = "R.E. 2023" (sha256 `f2354897...`).
The Act's Schedule, headed "(Made under section 6(1)) PART I SUPPLIES AND IMPORTS EXEMPT FROM VALUE ADDED TAX", item **10. Health care**, para 1, verbatim:

> "A supply of medical, dental, nursing, convalescent, rehabilitation, midwifery, paramedical, optical, or other similar services where the services are provided:
> (a) by or in an institution approved for the provision of those services by the Government; and
> (b) by, or under the supervision and control of, a person who is registered as being qualified to perform that service under Tanzania laws, or whose qualifications to perform the services are recognised in Tanzania."

**Both limbs are required** ("and"). So "doctors' services are exempt" is too broad: a service outside an approved institution, or not by/under a registered practitioner, is not covered by this item.
**Amendment check (R29):** Finance Act 2024 (No.6): no health item. Finance Act 2025 (No.11) s.135 amends Part I items 1, 2, 3, 9, 13, 15, 17, 21, 27, 31, 34 and renumbers items 21-35 only; item 10 untouched and not renumbered. Finance Act 2026 (No.2) s.96 amends items 3, 4, 6, 27, 31(b) and adds after 35; item 10 untouched.
**What the Act text does NOT settle (so it is hedged, not asserted):** s.29(1) (professional services must register) has no exempt-supply carve-out in its words, while s.28(6)(a) excludes non-taxable supplies from the registration TURNOVER. Whether a practitioner who makes ONLY exempt supplies must register under s.29 is therefore not stated; confirm with TRA.

**Proposed fact `medical_services_vat_exempt`:** "Huduma za afya (tiba, meno, uuguzi, ukunga, ukarabati, macho au zinazofanana) ni MSAMAHA wa VAT zinapotolewa (a) na au ndani ya taasisi iliyoidhinishwa na Serikali kwa huduma hizo, NA (b) na, au chini ya usimamizi na udhibiti wa, mtu aliyesajiliwa kuwa na sifa chini ya sheria za Tanzania (au anayetambuliwa kuwa na sifa) (Sheria ya VAT, Jedwali, Sehemu ya I, kipengele cha 10). Masharti yote mawili lazima yatimie. Sheria ya usajili wa huduma za kitaalamu haisemi wazi kama mtoa huduma wa afya anayetoa huduma zilizosamehewa tu anatakiwa kujisajili VAT: HAIJATHIBITISHWA hapa, thibitisha na TRA."
**Proposed statement route `vat_medical_services`** (model-free, excluded from auto-send): cue = VAT AND a health-service word (daktari, madaktari, doctor, kliniki, clinic, hospitali, hospital, muuguzi, nurse, meno, dental, matibabu); ask = registration / tax / exempt; vetoes = digits and money, voluntary, penalties, how-to. The professional-services route keeps its health vetoes, so the two are exclusive.
**Live defect it fixes:** "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?" -> "Ndiyo ..." (build 84d8621).

## B. The invented "TZS 150,000" in the SDL compute reply (item 7) -- DESIGN ONLY

**Specimen (live, b96e8a8 and 84d8621):** compute reply to "SDL na NSSF ni kiasi gani?" (15 staff, TZS 6,000,000): the body says "SDL ... TZS 210,000 (**TZS 150,000** kwa mwajiri)". The engine produced 210,000 (SDL) and 1,200,000 / 600,000 / 600,000 (NSSF); 150,000 appears in neither the question nor any working. `guards=[]` on the first run; D-FIDELITY-9 is off because its gate is "the question supplies no figure at all" and this question supplies one.
**Design (D-FIDELITY-31, compute path only, body sentence blanked, the working still renders):** a money amount in a model-written body is SUPPORTED if it equals (1) a question amount, (2) any amount in ANY engine working of the same request (fan-out siblings included: a sibling's figure is not an invention), or (3) a ONE-STEP result of two supported amounts: x + y, x - y, x * y, x / y, or x * r for r a rate present in the question, the workings or the locked rates. 150,000 is 2.5% of 6,000,000 and 2.5% is in none of those, so it is UNSUPPORTED; eval_395's net pay (800,000 - 78,000), eval_092's per-head breakdown and eval_296's 18,000 x 26 are all one-step results and are SUPPORTED. Rule 3 is what the memo's loose rule lacked (it was 1/14 precise because it had no rule 3).
**Before any wiring (R22/R25):** price it over the 62 working-bearing stored replies + 66 gold answers used for the memo (`eval/fidelity/scope_render_body_working_disagreement_2026_10_10.py`), require the founding specimen to flag and **0 GOLD flags**, read every flag; add authored probes that are CORRECT bodies with two-step derivations (the hole in rule 3) to see what it wrongly blanks. The honest expectation: it removes a fabrication and cannot supply the missing "SDL ni TZS 210,000 kwa mwajiri" sentence (a guard stops a wrong answer, it does not produce a right one).
**Known limit:** a two-step derivation by the model (e.g. 6,000,000 x 3.5% x 12) is flagged although correct; blanking a correct annual figure costs one sentence, the working still shows the monthly one.

## C. Fact texts for the ONE regen (what is already in `scripts/locked_facts.json` uncommitted, and what is not)

| # | fact | status in the working tree |
|---|---|---|
| 1 | `sdl_base_includes_allowances` (NEW) | **written** (VETA Act s.14(3), edition asserted, FA2024/25/26 checked) |
| 2 | `sdl_rate` fact wording ("cash" -> total gross monthly emoluments) + `correction_note`; `SDL_source_law`; the SDL half of `wcf_threshold_no_minimum` (the WCF half says "cash" against a DIFFERENT Act that was not read: untouched) | **written** |
| 3 | `form_number_payment_credit_slip` reworded: no form asserted, ITX 300.01.E unconfirmed as current (row 108) | **written** |
| 4 | TRA SDL captures cached + declared in the manifest | **done** (`tra_sdl_page_{en,sw}_2026_11_23.html`; raw hashes differ from the 11-22 record because the pages embed a per-request csrf_token; substance re-compared, unchanged) |
| 5 | `medical_services_vat_exempt` (NEW) | **NOT written** (section A; your approval of the source first) |
| 6 | the 13 SDL-exemption training rows | **NOT touched** (report-first; proposal in the report) |
| 7 | **found while reading, NOT written:** `p45_not_tanzanian` cites ITA "s.85(3)(b)" (the R.E.2015 number); `paye_p9_deadline` records **s.110(3)(b)** for R.E.2023: the renumbering trap inside a locked fact (metadata only) | proposed |
| 8 | **found, NOT written:** `gn487a_penalty_noncitizen` says "AND/OR" and `gn487a_penalty_citizen_facilitator` is "LOCKED" on practitioner sources; the gazetted Order says fine OR imprisonment, with revocation added, a MINIMUM fine and no maximum | proposed |

Committing facts 1-3 moves the served-index builder from 218 to 219 rows, so `tests/test_check_rag_index_freshness.py` fails until the regen is packaged: that coupling is why none of this is committed yet.
