#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EVERY CACHED SOURCE CARRIES ITS EDITION, AND ANY CHECK AGAINST ONE ASSERTS THE EDITION FIRST.

Usage:
    python scripts/check_source_editions.py            # verify the manifest (exit 1 on drift)
    python scripts/check_source_editions.py --build     # regenerate the manifest from content
    assert_edition("data/source_documents/nssf/nssf_act_cap50.pdf", "R.E. 2015")   # from code

WHY, and it is not hypothetical. `fine_limit` said TZS 100,000 because it was read from
data/source_documents/nssf/nssf_act_cap50.pdf -- which is REVISED EDITION 2015, where s.72(1)
genuinely says "one hundred thousand shillings". R.E.2023 s.76(1) says ten million. The fact
was not unchecked; it was CHECKED AGAINST THE WRONG EDITION, and nothing in the filename, the
`source` field or the fact's own metadata said which edition the file was.

⛔ THE TWO FORMS OF THE RENUMBERING TRAP, both present in Cap.50, and the reason an edition
assertion has to come FIRST rather than alongside:

    POINTS AT NOTHING ....... s.5A does not exist in R.E.2023. Four facts cited the First
                              Schedule as made under "ss.5A(c), 12(1)"; R.E.2023's own rubric
                              reads "sections 5(2)(c) and 12(1) and (5)". A reader checking
                              s.5A finds no such section. FAILS LOUDLY.
    POINTS AT THE WRONG THING  The offences clause is s.72 in R.E.2015 and s.76 in R.E.2023.
                              In R.E.2015, s.76 is "Protection of contributions" -- a
                              different provision. A reader checking "s.76(1)" against the
                              cached R.E.2015 PDF reads the wrong section and comes away
                              CONFIDENTLY CONFIRMED.

The second is the form that was actually operating, and it means **checking a citation against
a cached PDF can certify an error**. A verification pass that does not first establish which
edition it is holding is not a verification pass; it is a coin flip whose result is reported as
evidence.

WHAT AN "EDITION" IS, PER KIND -- because most of these files are not statutes:
    statute   the Revised Edition printed on its cover ("REVISED EDITION OF 2015")
    gazette   the GN number and publication date printed on it
    portal    the CAPTURE DATE -- a regulator's page has no edition, so the only honest answer
              is when we fetched it. Where the page embeds dated news items, those bound the
              capture from below and are recorded as evidence rather than asserted.
    advisory  the tax year on its cover ("2025/2026")

R26 both directions: tests/test_source_editions.py plants a swapped file (must block) and a
clean tree (must pass).
"""
import argparse
import hashlib
import html
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "data", "source_documents")
MANIFEST = os.path.join(ROOT, "MANIFEST.json")

# ── EDITION FACTS, each READ FROM THE DOCUMENT and quoted, never inferred from a filename ──
# A file absent from here is reported as UNDECLARED rather than skipped: an undeclared cached
# source is exactly the state fine_limit was verified against.
DECLARED = {
    "nssf/nssf_act_cap50.pdf": {
        "kind": "statute",
        "edition": "R.E. 2015",
        "edition_evidence": "cover: 'CHAPTER 50 THE NATIONAL SOCIAL SECURITY FUND ACT, "
                            "[PRINCIPAL LEGISLATION] REVISED EDITION OF 2015 ... incorporates "
                            "all amendments made up to and including 31st December, 2015'",
        "superseded": True,
        "superseded_by": "Cap.50 R.E. 2023 (OAG 2025 compilation), sha256 2a820e67ed109cd36059, "
                         "773,203 bytes, 50pp, at "
                         "https://www.nssf.go.tz/uploads/publications/"
                         "en-1771921274-NSSF%20ACT%20CAP%2050%20RE.%202023.pdf and "
                         "https://oagmis.oag.go.tz/portal/acts/revised/155/download "
                         "(byte-identical)",
        "do_not_verify_against": "THIS FILE PRODUCED THE fine_limit 100x ERROR. s.72(1) here is "
                                 "s.76(1) in R.E.2023, and this edition's s.76 is a DIFFERENT "
                                 "provision ('Protection of contributions'). Renumbering "
                                 "offsets confirmed from R.E.2023's own bracketed notes: "
                                 "s.23<-[21] s.25<-[23] s.29<-[27] s.46<-[44] s.47<-[45] "
                                 "s.50<-[48] s.51<-[49] s.76<-[72]; s.11/s.12/s.14 unmoved.",
    },
    "immigration/gn487a_official_gazette.pdf": {
        "kind": "gazette",
        "edition": "GN No. 487A, published 28/7/2025",
        "edition_evidence": "page 1: 'GOVERNMENT NOTICE No. 487A published on 28/7/2025 THE "
                            "BUSINESS LICENSING ACT, (CAP. 101)'",
        "superseded": False,
    },
    "brela/brela_ada_kampuni.html": {
        "kind": "portal",
        "edition": "capture of brela.go.tz/pages/tozo-za-kampuni, not earlier than 10 Jun 2026",
        "edition_evidence": "embedded news items dated '10 Jun 2026' and '02 Jun 2026' bound "
                            "the capture from below. A regulator's page has no edition, so the "
                            "capture date is the only honest answer and is recorded as a BOUND, "
                            "not as a date we know.",
        "superseded": True,
        "superseded_by": "data/source_documents/brela/brela_ada_kampuni_20261006T140442Z.html "
                         "-- a live re-fetch on 2026-10-06 which is NOT byte-identical and on "
                         "which several fees DIFFER. This capture is the OLDER evidence and "
                         "R29 gives the newer reading.",
        "note": "⭐ THIS CAPTURE BEARS ON THREE DISPUTES OPEN IN CLAUDE.md Section 11, and is "
                "quoted here so the next reader does not have to re-derive it:\n"
                "  item 14 ('Ada zinazolipwa na kampuni ambapo KIFUNGU XII cha Sheria "
                "kinahusika'), fourth bullet: 'Ada ya kuchelewa kufungua jalada/usajili wa "
                "waraka wowote inalipwa kwa Msajili (kwa mwezi au sehemu ya siku za mwezi) ni "
                "Dola za Kimarekani 25 /=' -- USD 25, under PART XII. The string '70,000' "
                "appears NOWHERE in this capture.\n"
                "  item 2: 'Usajili wa kampuni ambayo haina mtaji wa hisa ... Tsh. 300,000 /=' "
                "-- and '500,000' appears NOWHERE in this capture.\n"
                "  item 10: 'Gharama za kujaza taarifa ya mwaka Tsh. 22,000 /=' and item 9: "
                "late filing 'TSHS 2,500 /=' per month -- both already locked, re-confirmed.\n"
                "⚠️ THIS DOES NOT DISPROVE THE 2026-10-04 READING of TZS 70,000. It establishes "
                "that NO CACHED ARTIFACT SUPPORTS IT and that the one capture we hold says USD "
                "25. A live page can change; an unsaved live reading cannot be checked by "
                "anyone, which is the whole argument for capturing before citing.\n"
                "🔴 RESOLVED 2026-10-06 BY RE-FETCHING: the page DID change. See the "
                "timestamped capture below. Every figure quoted above is accurate FOR THIS "
                "CAPTURE and superseded as a statement about the current page.",
    },
    "brela/brela_ada_kampuni_20261006T140442Z.html": {
        "kind": "portal",
        "edition": "live capture of brela.go.tz/pages/tozo-za-kampuni at 2026-10-06T14:04:42Z",
        "edition_evidence": "fetched with curl, HTTP 200, 57,804 bytes, sha256 "
                            "8d5543ac68eb4d3dc72fd1762dc7cc9c037870df65ac33f3654eb3c11c73b52c. "
                            "The capture timestamp is IN THE FILENAME, so the edition cannot be "
                            "separated from the file. Embedded news item '28 Sep 2026' is "
                            "consistent with it.",
        "superseded": False,
        "note": "⭐ THIS CAPTURE RESOLVES THE BRELA FEE DISPUTES, AND IT RESOLVES THEM AGAINST "
                "THE CACHED JUNE EVIDENCE.\n"
                "The dispute was never two contradictory readings of one page -- IT WAS A REAL "
                "AMENDMENT BETWEEN TWO DATES. The June capture (mtime 2026-06-30 04:42, "
                "re-fetched 16:44 the same day to byte-identical bytes) and this one differ, so "
                "'disputed' was the wrong frame: both readings were correct, at different "
                "times. That dissolves the conflict; what remains is a provenance question, "
                "not a contradiction.\n\n"
                "THE WHOLE PART XII SCHEDULE IS NOW DENOMINATED IN TZS, not USD -- which is why "
                "this is a substantive amendment and not a rounding, exactly as CLAUDE.md "
                "Section 11 anticipated. Item 15, 'Ada chini ya Masharti ya SEHEMU YA XII ya "
                "Sheria (Makampuni ya Nje)':\n"
                "  (i)   certified copy of the constitution ............ TZS 2,000,000  (was USD 750)\n"
                "  (ii)  any Part XII document except the balance sheet . TZS 600,000  (was USD 220)\n"
                "  (iii) balance sheet .............................. TZS 600,000  (was USD 220)\n"
                "  (iv)  failure/delay to file, per month or part month . TZS 70,000   (was USD 25)\n"
                "⭐ So '15(iv)' is EXACTLY the right citation, and the June capture's 'item 14' "
                "was the OLD numbering -- the item numbers moved with the redenomination.\n\n"
                "  item 2  company without share capital .............. TZS 500,000  (was 300,000)\n\n"
                "UNCHANGED, and worth recording as unchanged so the next reader need not "
                "re-derive it:\n"
                "  item 1(a) incorporation, share capital up to 1,000,000 .. TZS 95,000\n"
                "  item 7    annual return ............................. TZS 22,000\n"
                "  item 6    late filing, per month or part month ....... TZS 2,500\n"
                "  item 3    company NAME fee .......................... TZS 50,000 (label is "
                "now 'utunzaji' = maintenance, where June read 'kulinda' = reservation; same "
                "figure, different word -- flagged because the locked fact says 'reservation')\n\n"
                "⚠️ WHAT THIS STILL DOES NOT SETTLE. This is a REGULATOR SUMMARY PAGE, not the "
                "instrument. Companies Act Cap.212 s.458 and s.489(3) delegate every fee amount "
                "to the Minister's regulations, so no fee is settleable from the Act and the "
                "Companies (Fees) Regulations remain unlocated. The page-level evidence is now "
                "consistent, dated, saved and hashed; the amending instrument is still the open "
                "question.",
    },
    "brela/brela_ada_kampuni_v2.html": {
        "kind": "portal",
        "edition": "BYTE-IDENTICAL to brela_ada_kampuni.html -- NOT a second capture",
        "edition_evidence": "sha256 equal to brela/brela_ada_kampuni.html.",
        "superseded": False,
        "note": "⛔ THE '_v2' SUFFIX ASSERTS A SECOND OBSERVATION THAT DOES NOT EXIST. Two "
                "files, one capture. Anything that reads these as two readings of the page at "
                "two times is reading a filename, not a document (R34). Kept rather than "
                "deleted so the duplication is recorded instead of quietly resolved.",
    },
    "nssf/nssf_ulipaji_mchango.txt": {
        "kind": "portal",
        "edition": "NONE -- THE FILE IS 0 BYTES",
        "edition_evidence": "size 0. There is no content and therefore no edition.",
        "superseded": False,
        "note": "⛔ AN EMPTY CACHED SOURCE IS THE R26 INERT-CONTROL SHAPE IN THE SOURCE LAYER. "
                "Anything recorded as 'verified against' this path was verified against "
                "nothing, and the verification would have looked exactly like a successful one. "
                "Kept and declared rather than deleted so the gap is visible; re-fetch or "
                "remove deliberately.",
    },
    "nssf/nssf_go_contributions.html": {
        "kind": "portal",
        "edition": "capture of nssf.go.tz/pages/payment-of-contributions; the page itself "
                   "cites 'R.E. 2018'",
        "edition_evidence": "the string 'R.E. 2018' appears in the page body.",
        "superseded": False,
        "note": "The Fund's own portal cites R.E.2018 on this page and R.E 2023 on "
                "nssf_go_registration.html -- TWO EDITIONS OF ITS OWN ACT across two pages of "
                "one site. Neither is the statute; use Cap.50 R.E.2023 for any section number.",
    },
    "nssf/nssf_go_registration.html": {
        "kind": "portal",
        "edition": "capture of nssf.go.tz registration overview; the page itself cites "
                   "'R.E 2023'",
        "edition_evidence": "the string 'R.E 2023' appears in the page body.",
        "superseded": False,
    },
    "tra/tra_taxes_duties_2025_2026.pdf": {
        "kind": "advisory",
        "edition": "TRA 'Taxes and Duties at a Glance' July 2025 (FY 2025/2026)",
        "edition_evidence": "cover: 'TAXES FOR OUR DEVELOPMENT JULY, 2025'",
        "superseded": False,
        "note": "A regulator SUMMARY, not the statute. CLAUDE.md Section 4 records that this "
                "family's Class A transport row could not be verified against primary text.",
    },
    "tra/habib_advisory_tax_guide_2025_26.pdf": {
        "kind": "advisory",
        "edition": "Hanif Habib & Co. tax guide 2025/2026",
        "edition_evidence": "cover text names the firm and the 2025/2026 year.",
        "superseded": False,
    },
    # ---- 2026-11-16 four-unanswered-questions follow-up: every file below was READ for a fact and its edition is quoted from it ----
    'wcf/wca_cap263_re2023_osg.pdf': {
        'kind': 'statute',
        'edition': 'R.E. 2023',
        'edition_evidence': "page header of every page after the first: 'THE WORKERS COMPENSATION ACT [CAP . 263 R.E. 2023]'; first page 'CHAPTER 263 THE WORKERS COMPENSATION ACT [PRINCIPAL LEGISLATION]', footer '(c)2025 Government of Tanzania. All rights reserved ... OAG'. Fetched 2026-11-16 from https://elibrary.osg.go.tz/server/api/core/bitstreams/d71ef688-13fb-466d-ac95-ccb03e455514/content (host ownership verified from osg.go.tz, which links to http://elibrary.osg.go.tz/). s.34(1) reads 'within seven  days after receiving a notice of an accident from the employee or having learned in some other way that an accident has occurred'.",
    },
    'wcf/gn185_2016_workers_compensation_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 185, published 27/5/2016',
        'edition_evidence': "page 1: 'Supplement No. 21 27th May, 2016 ... GOVERNMENT NOTICE NO. 185 published on 27/5/2016 THE WORKERS' COMPENSATION REGULATIONS, 2016'. Fetched 2026-11-16 from the Parliament of Tanzania copy (www.parliament.go.tz/uploads/documents/sw-1738841389-1476206253-GN 185-...pdf). Reg.15 'Notification of accident by employee or employer'.",
    },
    'wcf/gn668_2021_wc_amendment_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 668, published 10/9/2021',
        'edition_evidence': "page 1: 'GOVERNMENT NOTICE No. 668 Published On. 10/9/2021 ... THE WORKERS COMPENSATION (AMENDMENT) REGULATIONS, 2021'. Amends regulations 13, 26(1), 36, 38, 41(1) ...; does NOT amend regulation 15. Fetched 2026-11-16 from wcf.go.tz.",
    },
    'labour/gn47_2017_elr_general_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 47, published 24/02/2017',
        'edition_evidence': "page 1: 'Supplement No. 8 24th February, 2017 ... GOVERNMENT NOTICE NO. 47 published on 24/02/2017 THE EMPLOYMENT AND LABOUR RELATIONS (GENERAL) REGULATIONS'. The only written-contract requirement in it is Reg.10(1) (a child's employment). Fetched 2026-11-16 from commons.laws.africa.",
    },
    'tra/vat_act_cap148_re2023.pdf': {
        'kind': 'statute',
        'edition': 'R.E. 2023',
        'edition_evidence': "page header from the first section onward: 'THE VALUE ADDED TAX ACT [CAP. 148 R.E. 2023]'; first page 'CHAPTER 148 THE VALUE ADDED TAX ACT [PRINCIPAL LEGISLATION]'. Fetched from tra.go.tz/images/uploads/acts/The_Value_Added_Tax_Act.pdf. Amended after this edition by Finance Acts 2024 (s.105 -> s.29(4),(5)), 2025 (s.126 -> s.29(5),(6)) and 2026 (s.91 -> s.5(5),(7)); this file does NOT contain those amendments.",
        'superseded': False,
        'note': 'A consolidated Act is a snapshot: read the amending Finance Acts before encoding anything from it.',
    },
    'tra/income_tax_act_cap332_re2023.pdf': {
        'kind': 'statute',
        'edition': 'R.E. 2023',
        'edition_evidence': "page header: 'THE INCOME TAX ACT [CAP. 332 R.E. 2023]'. Fetched from tra.go.tz/images/uploads/acts/The_Income_Tax_Act.pdf. Amended after this edition by the Finance Acts 2024-2026; this file does NOT contain those amendments. s.106(4) proviso (3:2 ratio) is [s. 83] in R.E.2019.",
        'note': 'A consolidated Act is a snapshot: read the amending Finance Acts before encoding any rate or schedule from it.',
    },
    'tra/gn714_2021_vat_general_amendment_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 714, published 8/10/2021',
        'edition_evidence': "page 1: 'GOVERNMENT NOTICE No. 714 Published On. 8/10/2021 ... THE VALUE ADDED TAX (GENERAL) (AMENDMENT) REGULATIONS, 2021'. Replaces regulation 36B (refund for goods bought in Zanzibar). No registration provision.",
    },
    'tra/gn448y_2023_vat_general_amendment_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 448Y, published 30/6/2023',
        'edition_evidence': "page 1: 'GOVERNMENT NOTICE NO. 448Y published on 30/6/2023 THE VALUE ADDED TAX ACT, (CAP.148) ... REGULATIONS'. No registration provision.",
    },
    'tra/gn352k_2025_vat_general_amendment_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 352K, published 30/6/2025',
        'edition_evidence': "page 1: 'GOVERNMENT NOTICE No. 352K published on 30/6/2025 THE VALUE ADDED TAX ACT, (CAP. 148) ... REGULATIONS'. No registration provision.",
    },
    'tra/tra_faq_57_2026_11_16.html': {
        'kind': 'portal',
        'edition': 'capture of tra.go.tz/ajax/faq/57 on 2026-11-16',
        'edition_evidence': "fetched 2026-11-16 (this session; a regulator FAQ has no edition, so the capture date is the honest answer). States: 'Voluntary registration is also allowed for certain specific economic activities' and names none.",
    },
    'tra/tra_vat_page_2026_11_16.html': {
        'kind': 'portal',
        'edition': 'capture of tra.go.tz/page/value-added-tax-vat on 2026-11-16',
        'edition_evidence': "fetched 2026-11-16; embedded news items dated '06 November, 2026' bound the capture from below. States the registration rules (threshold, professionals / Government entities / intending traders) with no mention of voluntary registration.",
    },
    'tra/finance_act_2026_no2.pdf': {
        'kind': 'gazette',
        'edition': 'Finance Act 2026 (No. 2), 30th June 2026',
        'edition_evidence': "page 1: 'No. 2 The Finance Act, 2026 ... THE UNITED REPUBLIC OF TANZANIA No. 2 30th June, 2026 ACT SUPPLEMENT To The Special Gazette of the United Republic of Tanzania No. 8 Vol. 107 Dated 30th June, 2026'; s.2 'This Act shall come into operation on the 1st day of July, 2026'. s.91(b) adds VAT Act s.5(7) (3:2 goods:services apportionment of the value subject to withholding); s.27(a)(iii) adds First Schedule para 2(4) of the Income Tax Act. Fetched from tra.go.tz.",
    },
    'tra/finance_act_2025_no11.pdf': {
        'kind': 'gazette',
        'edition': 'Finance Act 2025 (No. 11), 30th June 2025',
        'edition_evidence': "page 1: 'No. 11 The Finance Act, 2025 ... THE UNITED REPUBLIC OF TANZANIA No. 11 30th June, 2025 ACT SUPPLEMENT to the Special Gazette ... No.6 Vol.106 dated 30th June, 2025'; s.2 'This Act shall come into operation on the 1st day of July, 2025'. Part XIII amends the Income Tax Act: s.59 amends s.117(3)(b) (CPA threshold: individual turnover > 500 million, corporation gross income > 100 million); s.60(e) amends First Schedule para 4(c) only (NOT 4(b) dividends). Its s.14 'section 20' and s.109 'section 54' belong to other Acts. Fetched from tra.go.tz (THE_FINANCE_ACT,_2025.pdf) 2026-11-17 by search-located URL, not a guess.",
    },
    'tra/finance_act_2024_no6.pdf': {
        'kind': 'gazette',
        'edition': 'Finance Act 2024 (No. 6), 1st July 2024',
        'edition_evidence': "page 1: 'No. 6 The Finance Act, 2024 ... THE UNITED REPUBLIC OF TANZANIA'; s.2 'This Act shall come into operation on the 1st day of July, 2024'. Part X amends the Income Tax Act USING THE PRE-REVISION NUMBERING (its s.91 = R.E.2023 s.117, its s.82 = s.105, bracket notes in the R.E. confirm): s.44 adds a nine-month return limb for a person whose financial statement is audited by the Controller and Auditor General and renumbers old s.91(2) as (3), so R.E.2023 s.117(2) is FA2025's s.117(3); s.46(b) amends First Schedule para 4(b) by adding a royalty-to-sports-entity limb, leaving dividends untouched. No amendment to s.20 (year of income). Fetched from tra.go.tz (Finance_Act_2024_(1).pdf) 2026-11-17, located by search.",
    },
    'brela/business_licensing_act_cap101_re2023.pdf': {
        'kind': 'statute',
        'edition': 'R.E. 2023',
        'edition_evidence': "page header on every page: 'THE BUSINESS LICENSING ACT [CAP. 101 R.E. 2023]'; cover 'CHAPTER 101 THE BUSINESS LICENSING ACT [PRINCIPAL LEGISLATION]'. CHAPTER NUMBER: the same Act (No. 25 of 1972) was Cap. 208 in the 2002 print and is Cap. 101 here; the number 208 now belongs to the Business Activities Registration Act (elibrary.osg.go.tz item 2700d1bd..., 'Chapter 208 R.E. 2023'). Cap. 101 is confirmed independently by Finance Act 2025 Part VI ('AMENDMENT OF THE BUSINESS LICENSING ACT, (CAP. 101)') and by GN 487A. s.7(1) 'A business licence granted under this Act shall be valid for a period of twelve months from the date of issuance', s.7(2) up to three consecutive years' fee; its history note for s.7 lists Acts 20 of 1978 s.30, 11 of 2000 s.4, 2 of 2014 s.6 (none later). Does NOT incorporate Finance Act 2025 Part VI (no 'non-citizen' in the text) -- which amends ss.3, 4 and adds 14A and does not touch s.7. Fetched from brela.go.tz 2026-11-17, located by search.",
        'superseded': False,
    },
    'brela/business_licensing_act_cap208_2002_tanzlii.pdf': {
        'kind': 'statute',
        'edition': 'Cap. 208 as at 31 July 2002',
        'edition_evidence': "cover: 'Tanzania Business Licensing Act Chapter 208 Legislation as at 31 July 2002. Note: There are outstanding amendments that have not yet been applied: Act 2 of 2014, Act 15 of 2015, Act 4 of 2018, Act 12 of 2023'. s.7 'Every business licence granted under this Act shall expire on the thirtieth day of June next following the date of issue.'",
        'superseded': True,
        'superseded_by': 'Cap. 101 R.E. 2023, brela/business_licensing_act_cap101_re2023.pdf (sha256 650aa1c7...). s.7 (Validity of licences) was amended by Act 2 of 2014 s.6 to twelve months from issuance; the section number did not move (s.7 in both).',
        'do_not_verify_against': 'THIS EDITION PRODUCED THE 30 JUNE ERROR in locked fact business_licence_expiry_30_june, which read CONFIRMED for three months. s.7 here says 30 June; s.7 of R.E.2023 says twelve months. The chapter number also changed (208 -> 101), so a search for Cap.208 now finds a different Act.',
    },
    'brela/brela_matrix_business_licensing_act_2021.pdf': {
        'kind': 'portal',
        'edition': 'BRELA proposed-amendments matrix, 25 Nov 2021',
        'edition_evidence': "file name 'MATRIX-BUSINESS LICENSING ACT-25 NOV 2021'; states 'amendment of Section 7 by Finance Act 2014 which provided the Validity of Business License to be 12 Months from the date of issuance'. A regulator's own working paper: corroborates the statute, does not replace it.",
        'superseded': False,
    },
    'brela/brela_newsletter_no10_licensing_2024.pdf': {
        'kind': 'portal',
        'edition': 'BRELA Newsletter No. 10 (English), file stamped 2024-10-29',
        'edition_evidence': "article 'THE ROLE OF BUSINESS LICENSING SYSTEMS IN SIMPLIFYING THE ISSUANCE OF BUSINESS LICENCES IN TANZANIA': 'Business licences category A are issued ... by BRELA'; 'Since 1st July 2017, the responsibility for issuing business licences Category A ... was transferred' to BRELA; category B by Local Government Authorities. The Act itself (s.6) delegates the appointment of licensing authorities to a Gazette order that was not located.",
        'superseded': False,
    },
    'labour/gn605a_2025_minimum_wage_order.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 605A of 2025, published 13 October 2025 (Special Supplement 9)',
        'edition_evidence': "TanzLII/Laws.Africa reproduction of 'Labour Institutions (Minimum Wage for Private Sector) Order, 2025 (Government Notice 605A of 2025)', 'Published in Special Supplement 9 on 13 October 2025. Assented to on 23 September 2025. Commenced on 1 January 2026', '[Made under section 39(1)]' of the Labour Institutions Act. Names no consultancy; contains no average-increase figure. Fetched from the media.tanzlii.org mirror recorded in locked fact gn605a_average_increase (reachable by plain curl; the HTML front end is the CAPTCHA'd one).",
        'superseded': False,
    },
    'labour/gn605a_2025_kazi_go_tz_official.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 605A, published 13/10/2025 (Special Gazette No. 6 Vol. 106, official copy on kazi.go.tz)',
        'edition_evidence': "page 1: 'GOVERNMENT NOTICE No. 605A published on 13/10/2025 LABOUR INSTITUTIONS ACT, (CAP. 300) ORDER (Made under section 39(1)) THE LABOUR INSTITUTIONS (MINIMUM WAGE FOR PRIVATE SECTOR) ORDER, 2025'; 'Special Gazette of the United Republic of Tanzania No. 6 Vol. 106 Dated 13th October, 2025'; final page signature block 'Dodoma, 23th September, 2025 ... Minister of State, Prime Minister's Office - Labour, Youth, Employment and Persons with Disability'. The OFFICIAL copy: unlike the TanzLII reproduction it carries the signature block. Fetched from kazi.go.tz 2026-11-17 (search-located URL).",
        'superseded': False,
    },
    'labour/labour_institutions_act_cap300_2019_tanzlii.pdf': {
        'kind': 'statute',
        'edition': 'Cap. 300 as at 30 November 2019 (Act 3 of 2020 not applied)',
        'edition_evidence': "cover: 'Tanzania Labour Institutions Act Chapter 300 Legislation as at 30 November 2019. Note: There are outstanding amendments that have not yet been applied: Act 3 of 2020'. s.39(1) 'After considering the report and recommendations of the wage board and the Council, the Minister shall make a wage order determining the minimum wage and other conditions of employment ...'; 'Minister' means the Minister for the time being responsible for labour matters. A 2019 consolidation: s.39 has NOT been checked against Act 3 of 2020 or later amendments.",
        'superseded': False,
    },
    'tra/gn225_2015_vat_general_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 225, published 19/06/2015',
        'edition_evidence': "OCR of page 1: 'Value Added Tax (General) Regulations, 2015 G.N. No. 225 ... GOVERNMENT NOTICE NO. 225 published on 19/06/2015 VALUE ADDED TAX (GENERAL) REGULATIONS, 2015'. IMAGE-ONLY PDF (no text layer): read by machine OCR 2026-11-16; Part IV regs 11-16 = registration. Fetched from tra.go.tz/images/uploads/regulations/.",
    },
    'tra/gn608_2018_vat_general_amendment_regulations.pdf': {
        'kind': 'gazette',
        'edition': 'GN No. 608, published 19/10/2018',
        'edition_evidence': "OCR of page 1: 'Supplement No. 40 19th October, 2018 ... GOVERNMENT NOTICE No. 608 published on 19/10/2018 THE VALUE ADDED TAX ACT (CAP. ...)'. IMAGE-ONLY PDF: machine OCR 2026-11-16; no registration provision.",
    },
    'tra/gn225_2015_vat_general_regulations_OCR.json': {
        'kind': 'portal',
        'edition': 'machine OCR (rapidocr-onnxruntime) of gn225_2015_vat_general_regulations.pdf, 2026-11-16',
        'edition_evidence': "A DERIVED artifact, not a source: per-page OCR text of the sibling PDF (40 pages). Spacing is degraded ('Applicationbyintending trader'); quote the PDF, never this file. Kept so the claim 'no voluntary route in the 2015 Regulations' can be re-checked without re-running OCR.",
    },
    'tra/gn608_2018_vat_general_amendment_regulations_OCR.json': {
        'kind': 'portal',
        'edition': 'machine OCR (rapidocr-onnxruntime) of gn608_2018_vat_general_amendment_regulations.pdf, 2026-11-16',
        'edition_evidence': 'A DERIVED artifact (8 pages), see the GN 225 OCR entry.',
    },
}

# Files whose edition is simply "the capture", with no in-document marker to quote. Declared as
# a CLASS rather than individually, because inventing a per-file date we do not have would be
# worse than saying plainly that we do not have one.
UNDATED_PORTAL_CAPTURE = (
    "A portal/press capture with no edition or date marker in the document. The honest edition "
    "is 'whenever this was fetched', and that is NOT recorded anywhere -- so it may not be used "
    "to settle a figure on its own. Capture provenance was not kept when these were saved; "
    "re-fetch with a dated record if one of them needs to carry a claim.")


def _hash(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _walk():
    out = []
    for root, _, files in os.walk(ROOT):
        for f in sorted(files):
            if f in (".gitkeep", "MANIFEST.json"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            out.append((rel, full))
    return sorted(out)


def build():
    entries = {}
    for rel, full in _walk():
        d = DECLARED.get(rel)
        size = os.path.getsize(full)
        # THE LOCAL MTIME IS THE ONLY CAPTURE-DATE EVIDENCE MOST OF THESE HAVE, and it lives on
        # one laptop. Committing it into the manifest is the whole point: it is the difference
        # between "fetched at some time" and a date the next reader can reason about. It also
        # exposed that brela_ada_kampuni_v2.html was fetched 12 HOURS after its sibling and
        # returned identical bytes -- a genuine re-fetch that found no change, not a mislabel.
        entries[rel] = {
            "sha256": _hash(full),
            "bytes": size,
            "captured_local_mtime_utc": __import__("datetime").datetime.utcfromtimestamp(
                os.path.getmtime(full)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "kind": d["kind"] if d else "portal",
            "edition": d["edition"] if d else "UNDECLARED",
            "edition_evidence": d["edition_evidence"] if d else UNDATED_PORTAL_CAPTURE,
            "superseded": bool(d and d.get("superseded")),
        }
        for opt in ("superseded_by", "do_not_verify_against", "note"):
            if d and d.get(opt):
                entries[rel][opt] = d[opt]
    payload = {
        "_what": "Edition manifest for every cached source document. An edition is a property "
                 "of the DOCUMENT, read from it and quoted -- never inferred from a filename.",
        "_why": "fine_limit said TZS 100,000 because it was read from nssf_act_cap50.pdf, which "
                "is R.E.2015. Checking a citation against a cached PDF CAN CERTIFY AN ERROR "
                "when the edition renumbered: Cap.50's offences clause is s.72 in R.E.2015 and "
                "s.76 in R.E.2023, and R.E.2015's s.76 is a different provision entirely.",
        "_contract": "Any check that reads a cached source MUST call assert_edition(path, "
                     "expected) first. A file whose edition is UNDECLARED may not be used to "
                     "settle a figure.",
        "_generated_by": "scripts/check_source_editions.py --build",
        "counts": {
            "files": len(entries),
            "declared": sum(1 for e in entries.values() if e["edition"] != "UNDECLARED"),
            "undeclared": sum(1 for e in entries.values() if e["edition"] == "UNDECLARED"),
            "superseded": sum(1 for e in entries.values() if e["superseded"]),
        },
        "files": entries,
    }
    with io.open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return payload


def load_manifest():
    with io.open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def assert_edition(path, expected):
    """THE CONTRACT. Call this BEFORE reading a cached source to settle anything.

    `path` may be absolute, repo-relative, or relative to data/source_documents/.
    Raises AssertionError if the file is unknown, if its bytes no longer match the manifest
    (someone swapped the file under its name), or if the declared edition does not contain
    `expected`.
    """
    man = load_manifest()["files"]
    norm = str(path).replace("\\", "/")
    for cand in (norm, norm.split("data/source_documents/")[-1]):
        if cand in man:
            rel = cand
            break
    else:
        raise AssertionError(
            f"{path} is not in the source manifest. An undeclared cached source has no known "
            f"edition, and an unknown edition is how the fine_limit 100x error happened. Add it "
            f"to DECLARED in scripts/check_source_editions.py, with the edition QUOTED from the "
            f"document.")
    entry = man[rel]
    full = os.path.join(ROOT, rel)
    actual = _hash(full)
    assert actual == entry["sha256"], (
        f"{rel} no longer matches the manifest (sha256 {actual[:12]} vs {entry['sha256'][:12]}) "
        f"-- the FILE CHANGED UNDER ITS NAME, so its declared edition is not a claim about "
        f"these bytes. Re-read the document and rebuild the manifest before using it.")
    assert expected.lower() in entry["edition"].lower(), (
        f"{rel} is edition {entry['edition']!r}, not {expected!r}.\n"
        f"  evidence: {entry['edition_evidence']}\n"
        + (f"  ⛔ {entry['do_not_verify_against']}\n"
           if entry.get("do_not_verify_against") else "")
        + "Reading a renumbered edition returns a CONFIDENT WRONG confirmation, not an error.")
    return entry


def check():
    if not os.path.exists(MANIFEST):
        print("[FATAL] no MANIFEST.json -- run with --build")
        return 2
    man = load_manifest()
    declared_files = man["files"]
    on_disk = {rel for rel, _ in _walk()}
    problems = []

    for rel in sorted(on_disk - set(declared_files)):
        problems.append(("UNMANIFESTED", rel, "present on disk, absent from the manifest"))
    for rel in sorted(set(declared_files) - on_disk):
        problems.append(("MISSING", rel, "in the manifest, absent from disk"))
    for rel in sorted(on_disk & set(declared_files)):
        actual = _hash(os.path.join(ROOT, rel))
        if actual != declared_files[rel]["sha256"]:
            problems.append(("CHANGED", rel,
                             f"sha256 {actual[:12]} != manifest {declared_files[rel]['sha256'][:12]}"))

    undeclared = sorted(r for r, e in declared_files.items() if e["edition"] == "UNDECLARED")
    superseded = sorted(r for r, e in declared_files.items() if e["superseded"])

    print(f"source documents: {len(on_disk)}")
    print(f"  edition declared : {len(declared_files) - len(undeclared)}")
    print(f"  UNDECLARED       : {len(undeclared)}  (may NOT settle a figure on their own)")
    print(f"  SUPERSEDED       : {len(superseded)} -> {superseded}")
    if problems:
        print("\nPROBLEMS:")
        for kind, rel, why in problems:
            print(f"  [{kind}] {rel}: {why}")
        return 1
    print("\nMANIFEST OK -- every cached source accounted for and unchanged.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.build:
        p = build()
        print(json.dumps(p["counts"], indent=2))
        print(f"[built] {MANIFEST}")
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
