# -*- coding: utf-8 -*-
"""2026-11-17 locked-fact edits (founder-approved): licence validity CORRECTED (R27: amend fields, never replace the object), dividend withholding clarified,
and five NEW facts. Idempotent. Run: python scripts/apply_licence_and_followup_facts_2026_11_17.py
Primary sources are cached and edition-declared in data/source_documents/MANIFEST.json (sha256 prefixes quoted below)."""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(REPO, "scripts", "locked_facts.json")
d = json.load(io.open(P, encoding="utf-8"))
TODAY = "2026-11-17"

# ---- 1. LICENCE: 30 June -> twelve months from issuance (R29 mode 2: a superseded EDITION). The key is kept (renaming would orphan every anchor); it now carries a stale value, so a note says so.
f = d["business_licence_expiry_30_june"]
f["fact"] = ("Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa; si tarehe maalum ya kalenda. SI 30 Juni (hiyo ilikuwa sheria ya zamani, ilibadilishwa). "
             "Mwenye leseni anaweza kuchagua kulipia ada ya hadi miaka 3 mfululizo (Sheria ya Leseni za Biashara). "
             "A business licence is valid for twelve months from the date of issuance (the former 30 June rule was replaced); the holder may pay the fee for up to three consecutive years.")
f["correct_value"] = "valid for 12 months from the date of issuance; option to pay the licence fee for up to 3 consecutive years. NOT 30 June, NOT 31 March, NOT 31 December"
f["wrong_patterns"] = ["leseni.*huisha.*disemba", "leseni.*expire.*december", "leseni.*huisha.*30 juni", "leseni.*huisha.*31 machi", "leseni.*ifikapo.*30 juni",
                       "licen[cs]e.*expires?.*30 june", "licen[cs]e.*expires?.*31 march", "licen[cs]e.*expir.*every year on 30"]
f["primary_source"] = ("Business Licensing Act Cap.101 R.E.2023 (brela.go.tz copy, data/source_documents/brela/business_licensing_act_cap101_re2023.pdf, sha256 650aa1c7, edition asserted in the manifest), "
                       "s.7(1) 'A business licence granted under this Act shall be valid for a period of twelve months from the date of issuance', s.7(2) fee for up to three consecutive years; its history note for s.7: "
                       "Acts 20 of 1978 s.30, 11 of 2000 s.4, 2 of 2014 s.6. Corroborated by BRELA's own proposed-amendments matrix of 25 Nov 2021 ('amendment of Section 7 by Finance Act 2014 which provided the Validity of Business License to be 12 Months from the date of issuance').")
f["verified_by"] = ("Direct read 2026-11-17 of Cap.101 R.E.2023 s.7. CHAPTER NUMBER: the same Act (No. 25 of 1972) was Cap.208 in the 2002 print and is Cap.101 in R.E.2023 (the number 208 now belongs to the Business Activities Registration Act); "
                    "Cap.101 is confirmed independently by Finance Act 2025 Part VI and by GN 487A. LATER AMENDMENT SEARCH: Finance Acts 2024 and 2026 do not mention the Act; Finance Act 2025 Part VI amends ss.3, 4 and adds s.14A and does not touch s.7; "
                    "Finance Acts 2015-2023 were NOT read individually -- R.E.2023's own history note for s.7 lists none later than Act 2 of 2014 s.6, and the copy incorporates Act 12 of 2023 (s.8 fee note). "
                    "THE PRIOR RECORD: 'confirmed against the Act text 2026-08-16', citing 's.3(4) as substituted by the Finance Act 2014 s.5', with NO verified_by field (tests/test_locked_facts_finance_act_freshness.py listed it as 'never checked against primary text'). "
                    "The 30 June rule is the text of Cap.208 as at 31 July 2002 s.7 (data/source_documents/brela/business_licensing_act_cap208_2002_tanzlii.pdf, superseded in the manifest); which edition was read on 2026-08-16 is not recorded.")
f["status"] = "CORRECTED 2026-11-17 -- the prior value (30 June) was wrong"
f["verified_date"] = TODAY
f["verified_as_at"] = TODAY
f["superseded_value"] = "every business licence expires on 30 June each year (Business Licensing Act Cap.208 R.E.2002 s.7; replaced by Act 2 of 2014 s.6)"
f["effective_date"] = "Act 2 of 2014 s.6 (commencement not read); text as at Cap.101 R.E.2023"
f["correction_note"] = ("2026-11-17: this fact read CONFIRMED for three months and stated the pre-2014 rule. R29 mode 2 (an out-of-date edition); the amending instrument governs. The KEY still says 30_june and is kept: "
                        "renaming it would orphan the index anchors, the sync check and the tests (R27). Frozen test sets np_13 / s2_07 recorded the same error in their answer text and label: see their sidecar files.")
f["_key_note"] = "the key embeds a SUPERSEDED value (30 June); read the fact, not the key"

# ---- 2. DIVIDEND WITHHOLDING: non-residents and treaties (the model said 15% for a non-resident).
f = d["dividend_withholding_rate"]
f["fact"] = ("Gawio (dividend) linakatwa kodi ya zuio asilimia ngapi? Kampuni iliyoorodheshwa Soko la Hisa la Dar es Salaam: 5%; kampuni mkazi kwenda kampuni mkazi inayomiliki 25% au zaidi: 5%; kampuni nyingine: 10%. "
             "15% si kiwango cha gawio; viwango hivi ni vilevile kwa mpokeaji asiye mkazi (hukatwa 5% au 10%). Mkataba wa kuepusha kodi mara mbili unaweza kuweka kiwango tofauti: thibitisha na TRA. "
             "Mtu binafsi anayelipa nje ya biashara hahusiki (Sheria ya Kodi ya Mapato).")
f["correct_value"] = "5% (DSE-listed, or resident company holding >=25%); 10% (other corporations); the same whether the payee is resident or non-resident; a double-tax treaty may set a different rate (confirm with TRA)"
if "gawio.*asiye mkazi.*15%" not in f.get("wrong_patterns", []):
    f["wrong_patterns"] = list(f.get("wrong_patterns", [])) + ["gawio.*asiye mkazi.*15%", "gawio.*wasio wakazi.*15%", "gawio.*wasio wakazi.*asilimia 15", "dividend.*non-resident.*15%", "dividend.*non-resident.*15 percent"]
if "2026-11-17 re-read" not in f["primary_source"]:
    f["primary_source"] = (f["primary_source"] + " | 2026-11-17 re-read: Income Tax Act Cap.332 R.E.2023 First Schedule para 4(b)(i) states 5% / 10% with NO resident/non-resident limb; s.105(1) applies to any payee of a resident payer. The 15% in para 4(b) is sub-paragraph (iv), 'other payments'. "
                           "Finance Act 2024 s.46(b), Finance Act 2025 s.60 and Finance Act 2026 s.27(c) were read (data/source_documents/tra/finance_act_2024_no6.pdf, finance_act_2025_no11.pdf, finance_act_2026_no2.pdf): none amends para 4(b)(i). "
                           "TRA's withholding page (2026-07-01 capture) lists non-resident dividends at 5% / 5% / 10%.")
    f["verified_by"] = (f["verified_by"] + " | 2026-11-17: FA2024 and FA2025 now READ, not relied on from the earlier note. Double-tax-treaty rates were not examined (the fact says to confirm with TRA).")
f["verified_as_at"] = TODAY
f["correction_note"] = "2026-11-17: the fact was silent on non-residents and a model reply filled the gap with '15% kwa wasio wakazi' (the 'other payments' rate). Clarified, not corrected: 5% / 10% are unchanged."

# ---- 3. NEW: company income-tax return deadline.
d["corporate_income_tax_return"] = {
    "fact": ("Kampuni inawasilisha return ya kodi ya mapato lini? Ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato. Mwaka wa mapato ni mwaka wa kalenda, hivyo kampuni ya kawaida iwasilishe kufikia 30 Juni ya mwaka unaofuata; "
             "kampuni iliyoidhinishwa na Kamishna kutumia mwaka tofauti wa mapato iwasilishe miezi 6 baada ya mwisho wa mwaka huo. Mtu ambaye hesabu zake zinakaguliwa na Mdhibiti na Mkaguzi Mkuu (CAG) ana miezi 9. "
             "Kampuni yenye mapato jumla zaidi ya TZS 100,000,000 kwa mwaka lazima iwe na return iliyoandaliwa au kuthibitishwa na mhasibu CPA anayefanya kazi kwa umma. "
             "Si miezi 12, si 30 Septemba: 30 Septemba ni tarehe ya awamu ya kodi ya awamu, si ya return (Sheria ya Kodi ya Mapato)."),
    "correct_value": "within six months after the end of the year of income (30 June for a calendar-year company); nine months for a person audited by the CAG; an approved different year of income moves the date; CPA-prepared/certified when a corporation's gross income exceeds TZS 100,000,000",
    "wrong_patterns": [r"(?:return|tamko)[^.?!]{0,60}(?:ndani ya|baada ya|ni)\s+miezi\s+(?:12|kumi na mbili)", r"(?:return|tamko)[^.?!]{0,60}(?:30 septemba|septemba 30)", r"corporate[^.?!]{0,40}return[^.?!]{0,40}(?:12 months|30 september)"],
    "primary_source": ("Income Tax Act Cap.332 R.E.2023 (tra.go.tz, sha256 a128d329, edition asserted in the manifest): s.117(1) 'every person shall file ... not later than six months after the end of each year of income a return of income'; "
                       "s.20(1) 'the year of income for every person shall be the calendar year', s.20(2)-(3) the Commissioner may approve another twelve-month year. AMENDED by: Finance Act 2024 No.6 s.44 (its 's.91'; adds a nine-month limb for 'a person whose financial statement is audited by the Controller and Auditor General' and renumbers old (2) as (3) -- so R.E.2023 s.117(2)(b) is s.117(3)(b) thereafter); "
                       "Finance Act 2025 No.11 s.59 (s.117(3)(b): CPA prepared or certified only for 'an individual whose turnover ... exceeds five hundred million shillings and a corporation whose gross income in a year of income exceeds one hundred million shillings', from 1 July 2025). Finance Act 2026 s.26 amends s.118(a) only."),
    "verified_by": ("Direct read 2026-11-17 of the R.E.2023 text, Finance Act 2024, Finance Act 2025 and Finance Act 2026 (all cached, editions asserted in the manifest). s.20 is not amended by any of the three (FA2025's 's.20' is the Bank of Tanzania Act). "
                    "30 September: provisional tax is payable in four instalments at the end of the 3rd, 6th, 9th and 12th months of the year of income (fact provisional_tax_instalments); that is where a '30 Septemba' comes from."),
    "status": "CONFIRMED", "verified_date": TODAY, "verified_as_at": TODAY,
    "effective_date": "six months: Cap.332 R.E.2023 s.117(1); CPA threshold: 1 July 2025; CAG nine months: 1 July 2024",
    "coverage_batch": "2026-11-17 follow-up (unsourced-figure check)",
}

# ---- 4. NEW: who issues a business licence.
d["business_licence_authority"] = {
    "fact": ("Leseni ya biashara inatolewa na nani? Leseni za kawaida (kundi B) hutolewa na halmashauri ya eneo la biashara; kwa duka au biashara ya kawaida, wasiliana na halmashauri yako. "
             "Leseni za kundi A (biashara za kitaifa au kimataifa: uagizaji na usafirishaji nje, benki, usafirishaji wa abiria na mizigo, clearing and forwarding) hutolewa na BRELA tangu 1 Julai 2017. "
             "Sheria inamwachia Waziri kuteua mamlaka ya leseni kwa tangazo la Gazeti (Sheria ya Leseni za Biashara)."),
    "correct_value": "Category B licences: the local government authority (council) of the business's area; Category A (national/international businesses): BRELA since 1 July 2017; the Act delegates the appointment of licensing authorities to a Ministerial Gazette order",
    "wrong_patterns": ["leseni ya biashara.*hutolewa na brela pekee", "leseni.*brela.*kila biashara"],
    "primary_source": ("Business Licensing Act Cap.101 R.E.2023 s.6(1): 'The Minister shall, by order published in the Gazette, appoint a public officer or any authority to be a licensing authority either generally or in relation to any area, or in relation to the businesses or categories of businesses specified'; "
                       "BRELA Newsletter No.10 (brela.go.tz, stamped 2024-10-29): category A licences are issued by BRELA (since 1 July 2017), category B by Local Government Authorities through their Councils."),
    "verified_by": ("2026-11-17: statute tier is SILENT on who the authorities are (s.6 delegates to a Gazette order that was NOT located); the category split rests on BRELA's own published newsletter, a regulator portal source (PORTAL TIER, not statute). "
                    "Do not state it as statute."),
    "status": "CONFIRMED -- portal tier (statute delegates to a Gazette order not located)", "verified_date": TODAY, "verified_as_at": TODAY,
    "effective_date": "BRELA responsibility for category A: 2017-07-01 (BRELA newsletter)",
    "coverage_batch": "2026-11-17 follow-up (BRELA vs licence authority)",
}

# ---- 5. NEW: who issued GN 605A (a model invented 'PKF Eastern Africa').
d["gn605a_issuer"] = {
    "fact": ("Jedwali la kima cha chini cha mshahara (GN 605A) limetolewa na nani? Ni Amri ya Kima cha Chini cha Mshahara kwa Sekta Binafsi, 2025 (Labour Institutions (Minimum Wage for Private Sector) Order, 2025, GN 605A), "
             "iliyotolewa na Serikali chini ya Sheria ya Taasisi za Kazi, ilichapishwa 13 Oktoba 2025 na inaanza kutumika 1 Januari 2026. Si PKF wala kampuni ya ushauri: hizo ni vyanzo vya uchambuzi tu."),
    "correct_value": "GN 605A is the Labour Institutions (Minimum Wage for Private Sector) Order, 2025, made under the Labour Institutions Act, published in Special Supplement 9 on 13 October 2025, in force 1 January 2026; not issued by PKF or any consultancy",
    "wrong_patterns": ["605a.*lililotolewa na pkf", "605a.*iliyotolewa na pkf", "pkf.*ilitoa.*605a", "605a.*issued by pkf", "605a.*published by pkf"],
    "primary_source": ("Labour Institutions (Minimum Wage for Private Sector) Order, 2025, Government Notice 605A of 2025 (TanzLII/Laws.Africa reproduction via the media.tanzlii.org mirror, data/source_documents/labour/gn605a_2025_minimum_wage_order.pdf, sha256 3a139908): "
                       "'Published in Special Supplement 9 on 13 October 2025. Assented to on 23 September 2025. Commenced on 1 January 2026. [Made under section 39(1)]', Labour Institutions Act."),
    "verified_by": ("Direct read 2026-11-17 of the Order. It names no consultancy and contains NO average-increase figure: the 33.4% average (TZS 275,060 -> 358,322) in gn605a_average_increase rests on PRESS and ADVISORY sources (BHRRC / the Minister's briefing / PKF Eastern Africa), NOT on the Order. "
                    "Who signed the Order was not read; the fact says 'Serikali' accordingly."),
    "status": "CONFIRMED", "verified_date": TODAY, "verified_as_at": TODAY, "effective_date": "2026-01-01",
    "coverage_batch": "2026-11-17 follow-up (GN 605A attribution)",
}
g = d["gn605a_average_increase"]
g["_source_tier_note"] = ("2026-11-17: the 33.4% average and the TZS 275,060 -> 358,322 figures are NOT in GN 605A (read in full, sha256 3a139908); they rest on press/advisory sources named in verified_by. "
                          "Also: the media.tanzlii.org PDF mirror IS reachable by plain curl (HTTP 200, 381,668 bytes) -- the 'PERMANENT hedge' in verified_by concerned the HTML front end only (R30).")

# ---- 6. NEW: severance tax treatment (a model said 15% PAYE).
d["severance_pay_income_tax"] = {
    "fact": ("Malipo ya kuachishwa kazi (severance, redundancy) yanakatwa kodi kiasi gani? Ni mapato ya ajira: yanajumuishwa kwenye mapato ya mfanyakazi na kodi (PAYE) hukokotolewa kwa viwango vya kawaida vya mshahara kwa mkazi; "
             "hakuna kiwango maalum cha asilimia 15. Sheria ina kanuni za kugawa malipo ya miaka ya nyuma na fidia ya mkataba; thibitisha kiasi chako na TRA (Sheria ya Kodi ya Mapato)."),
    "correct_value": "a redundancy/termination payment is employment income, included in total income and taxed through the ordinary resident PAYE bands; there is no flat 15% rate; allocation/spreading rules may apply (confirm with TRA)",
    "wrong_patterns": [r"(?:severance|kuachishwa kazi)[^.?!]{0,80}(?:ni|ya|kwa|hukatwa)\s+(?:asilimia\s+15|15\s*%)", r"severance[^.?!]{0,60}flat 15"],
    "primary_source": ("Income Tax Act Cap.332 R.E.2023 (tra.go.tz, sha256 a128d329), s.7(2)(e) 'payment for redundancy or loss or termination of employment' is included in an individual's gains or profits from employment; s.7(4) allocation of such a payment over the preceding years of income; "
                       "s.7(5) compensation for termination of a contract; First Schedule para 1(1) the graduated rates. The flat 10% in First Schedule para 1(3)(b) is for investment gains and a commuted pension only; the 15% limbs are para 4(a)(ii) (a NON-RESIDENT payee) and 4(a)(iii) (director's fees)."),
    "verified_by": ("Direct read 2026-11-17 of the R.E.2023 text. Searched the Act for 'redundan', 'retrench', 'terminal', 'lump sum' and 'severance': no exemption or special rate for termination payments was found (the Act text only; Finance Acts 2024-2026 were not individually searched for amendments to s.7 on this subject). "
                    "The spreading rules were not worked through: the fact says to confirm with TRA."),
    "status": "CONFIRMED", "verified_date": TODAY, "verified_as_at": TODAY, "effective_date": "Cap.332 R.E.2023",
    "coverage_batch": "2026-11-17 follow-up (severance tax)",
}

io.open(P, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("applied; facts:", len(d))
