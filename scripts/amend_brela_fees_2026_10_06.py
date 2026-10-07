# -*- coding: utf-8 -*-
"""AMEND THE BRELA COMPANY-FEE FACTS TO THE CURRENT SCHEDULE. FIELD-LEVEL, NEVER OBJECT-LEVEL (R27).

AUTHORISED: all six facts, with both amendments, 2026-10-06. The founder's proposal was to move
the served figures at PORTAL TIER on the strength of a dated, hashed capture of BRELA's own fee
page, with the June values recorded as superseded. Agreed, with two amendments that are now
applied here:

  AMENDMENT 1 — `effective_date` STAYS EXPLICITLY UNKNOWN. 2026-10-06 is our OBSERVATION date.
      All we know is that the schedule changed somewhere inside 2026-06-30 → 2026-10-06. Putting
      the observation date in `effective_date` would manufacture exactly the R29 mode-3 error: a
      correctly-cited figure carrying an unsourced currency date. A trader asking "was I
      overcharged in August?" needs the effective date, and we do not have it.
      `brela_foreign_late_filing_penalty` already carried `effective_date: "2025-01-01"`, which
      was never sourced from anything; it is corrected to unknown here rather than left.
  AMENDMENT 2 — THE REDENOMINATION IS A SEARCH LEAD, not just a caveat. Recorded in
      `_unresolved_items.brela_companies_fees_regulations`.

⚖️ WHY PORTAL TIER IS ENOUGH TO MOVE A SERVED FIGURE, stated because it was asked.
Companies Act Cap.212 ss.458 and 489(3) delegate every fee AMOUNT to Minister's regulations, so
no fee in this family is settleable from the Act at all — the statute tier is not merely harder
to reach here, it is structurally silent. What remains is the gazetted Fees Regulations (not
located; brela.go.tz law pages 500, tanzlii search is a client-rendered SPA) and the regulator's
own published schedule. A trader pays what BRELA charges at the counter, and BRELA publishes that
schedule itself. Leaving `USD 25` served when the page says `TZS 70,000/=` is not caution — it is
a known-wrong answer preserved by inaction.

⛔ THE SCHEDULE WAS REPLACED, NOT RE-PRICED, AND THAT CHANGES WHAT THE EDIT HAS TO SAY.
Both captures were read, not remembered (R34):

  JUNE   data/source_documents/brela/brela_ada_kampuni_v2.html
         sha256 cb1353fcce53b93c72247a8007430af51f8ec4e6b81b7acefaf2e100bacd810e, 37,719 bytes
         15 items. Share-capital table has FIVE bands, top one OPEN-ENDED:
         "Zaidi ya Tsh..50,000,000/= Tsh. 440,000 /=". Foreign-company block is ITEM 14,
         in USD: 750 / 220 / 220 / 25. Latest news item on the page: 10 Jun 2026.
  OCTOBER data/source_documents/brela/brela_ada_kampuni_20261006T140442Z.html
         sha256 8d5543ac68eb4d3dc72fd1762dc7cc9c037870df65ac33f3654eb3c11c73b52c, 57,804 bytes
         15 items, DIFFERENT CONTENT. Share-capital table has NINE bands, top one closed-ended
         at 10bn. Foreign-company block has MOVED TO ITEM 15 and is entirely in TZS:
         2,000,000 / 600,000 / 600,000 / 70,000. Latest news item: 28 Sep 2026.

Three consequences the edit must carry, each of which would otherwise produce a confident wrong
verdict in a later pass:
  1. THE ITEM NUMBERS MOVED. Every June `verified_by` says "Item 14 (foreign companies)". On the
     live page item 14 is now "Kurejesha jina la kampuni katika Daftari la Msajili (Restoration)
     50,000/=". A future reader checking "item 14" would find a restoration fee and conclude the
     fact was fabricated. Both numbers are stated at each site.
  2. "BAND 5" NO LONGER MEANS WHAT IT MEANT. `company_registration_fee_5` was the OPEN-ENDED top
     band (above TZS 50,000,000 → 440,000). It is now the CLOSED band (e), 50,000,000 to
     100,000,000 → 400,000, with four further bands above it. Editing 440,000 to 400,000 alone
     would leave a fact that is numerically current and structurally wrong — it would still imply
     a company with TZS 2bn share capital pays the band-5 fee. So the table is RE-AUTHORED as one
     new fact and the two legacy keys are narrowed to point at it.
  3. STAMP DUTY AND FILE-OPENING LINE ITEMS PRESENT IN JUNE ARE ABSENT IN OCTOBER (June items
     3/4/5: file-opening 66,000, stamp duty 10,000, Form 14b 1,200). Not amended here — no locked
     fact cites them — but recorded in the unresolved item, because a line item VANISHING from a
     fee schedule is a different claim from a line item changing price, and neither capture says
     which instrument did it.

Usage:  python scripts/amend_brela_fees_2026_10_06.py
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
FACTS = os.path.join(REPO, "scripts", "locked_facts.json")

JUNE = "data/source_documents/brela/brela_ada_kampuni_v2.html"
JUNE_SHA = "cb1353fcce53b93c72247a8007430af51f8ec4e6b81b7acefaf2e100bacd810e"
OCT = "data/source_documents/brela/brela_ada_kampuni_20261006T140442Z.html"
OCT_SHA = "8d5543ac68eb4d3dc72fd1762dc7cc9c037870df65ac33f3654eb3c11c73b52c"

# Shared provenance sentence, so every amended fact carries the same checkable claim.
PROV = (
    f" || UPDATED 2026-10-06 to the CURRENT published schedule. Read directly from a dated, "
    f"hashed capture of BRELA's own 'Ada za Kampuni' page: {OCT} (sha256 {OCT_SHA[:24]}..., "
    f"57,804 bytes, fetched 2026-10-06T14:04:42Z). The SUPERSEDED value is preserved and is "
    f"itself evidenced by the June capture {JUNE} (sha256 {JUNE_SHA[:24]}..., 37,719 bytes). "
    f"⚠️ THE PAGE WAS RESTRUCTURED, NOT JUST RE-PRICED: the foreign-company block moved from "
    f"ITEM 14 (June) to ITEM 15 (October), and item 14 is now Restoration (50,000/=). Checking "
    f"'item 14' on the live page finds the wrong row. ⚠️ effective_date remains UNKNOWN: "
    f"2026-10-06 is the OBSERVATION date; the change happened somewhere in 2026-06-30 to "
    f"2026-10-06 and no instrument has been located (see "
    f"_unresolved_items.brela_companies_fees_regulations)."
)

SUPERSEDED_NOTE = (
    "2026-10-06: value changed on BRELA's own published schedule. This is a SUPERSESSION, not a "
    "correction of a misreading -- the June value was read correctly from the page as it then "
    "stood, and is quoted verbatim from the June capture. R29 mode 3 (CORRECTLY-CITED-BUT-"
    "SUPERSEDED): the old figure was right as at its own date and simply predates a later "
    "instrument. The gold row ext_15 is therefore STALE, not wrong, and is corrected as a dated "
    "scoring-key change rather than scored as a model failure."
)

AMENDMENTS = {
    # --- the foreign-company (Part XII) block, item 15 in October -----------------------------
    "late_filing_penalty_monthly_fee_section_12_act": {
        "fact": ("Faini ya kampuni ya kigeni kuchelewa kuwasilisha nyaraka BRELA ni TZS 70,000 kwa "
                 "kila mwezi au sehemu ya mwezi (BRELA fee schedule item 15(iv), as at "
                 "2026-10-06; Companies Act Cap.212 R.E.2023, Part XII, ss.437-447). SUPERSEDES USD 25/month, which was the "
                 "published figure as at 2026-06-30. Distinct from the TZS 2,500/month penalty "
                 "for LOCAL companies (item 6), which is unchanged."),
        "correct_value": "TZS 70,000 per month or part month (foreign company, item 15(iv))",
        "superseded_value": "USD 25 per month (published as at 2026-06-30, June capture item 14)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "correction_note": SUPERSEDED_NOTE + (
            " Verbatim October: item 15(iv) 'Kwa kutowasilisha au kucheleweshakuwasilisha hati "
            "yoyote inayotakiwa kuwasilishwa kwa Msajili, kwa kila mwezi au sehemu ya mwezi wa "
            "kuchelewa. 70,000/='. Verbatim June: item 14 'Ada ya kuchelewa kufungua "
            "jalada/usajili wa waraka wowote inalipwa kwa Msajili (kwa mwezi au sehemu ya siku "
            "za mwezi) ni Dola za Kimarekani 25/='."),
        "_APPEND_VERIFIED_BY": PROV,
    },
    "brela_foreign_late_filing_penalty": {
        "fact": ("Faini ya kampuni ya kigeni kuchelewa kuwasilisha taarifa ya mwaka ni TZS 70,000 kwa "
                 "kila mwezi au sehemu ya mwezi (BRELA fee schedule item 15(iv), as at "
                 "2026-10-06; Companies Act Cap.212 R.E.2023, Part XII, ss.437-447). SUPERSEDES "
                 "USD 25/month (published as at 2026-06-30). Distinct from the TZS 2,500/month "
                 "penalty for local companies, which is unchanged."),
        "correct_value": "TZS 70,000/month (foreign company, Part XII, ss.437-447)",
        "superseded_value": "USD 25/month (published as at 2026-06-30)",
        # ⛔ WAS "2025-01-01", which no source in this fact ever supported. An unsourced
        # effective_date is worse than none: it is the figure a trader would rely on to decide
        # whether they were overcharged, and it was invented.
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV + (
            " ALSO: the October capture's own heading for this block reads 'Ada chini ya Masharti "
            "ya Sehemu ya XII ya Sheria (Makampuni ya Nje)' -- BRELA still labels it Part XII, "
            "independently re-confirming the 2026-10-05 reversal. The former effective_date "
            "'2025-01-01' is removed: no source in this fact ever supported it."),
    },
    "certified_copy_agreement_law_constitution_fee": {
        "fact": ("Ada ya kuwasilisha nakala iliyothibitishwa ya katiba ya kampuni ya nje kwa Msajili "
                 "ni TZS 2,000,000 (BRELA fee schedule item 15(i), as at 2026-10-06; Companies "
                 "Act Cap.212 R.E.2023, Part XII). SUPERSEDES USD 750 "
                 "(published as at 2026-06-30)."),
        "correct_value": "TZS 2,000,000 (item 15(i))",
        "superseded_value": "USD 750 (published as at 2026-06-30, June capture item 14)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "correction_note": SUPERSEDED_NOTE + (
            " Verbatim October: 'Kuwasilisha nakala iliyothibitishwa ya katiba ya kampuni ya nje "
            "2,000,000/='."),
        "_APPEND_VERIFIED_BY": PROV,
    },
    "document_filing_fee_section_12_act_excluding_balance_sheet": {
        "fact": ("Ada ya kampuni ya kigeni kuwasilisha waraka wowote kwa Msajili, bila kujumuisha "
                 "taarifa ya mizania, ni TZS 600,000 (BRELA fee schedule item 15(ii), as at "
                 "2026-10-06; Companies Act Cap.212 R.E.2023, Part XII, ss.437-447). SUPERSEDES USD 220 "
                 "(published as at 2026-06-30)."),
        "correct_value": "TZS 600,000 (item 15(ii), Companies Act Cap.212 Part XII, ss.437-447)",
        "superseded_value": "USD 220 (published as at 2026-06-30, June capture item 14)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV + (
            " ⚠️ THE JUNE verified_by SAID 'two distinct USD 220 line items ... Document filing "
            "and File opening'. The October schedule has no file-opening line item for foreign "
            "companies at all; items 15(ii) and 15(iii) are 'hati yoyote ... isipokuwa taarifa "
            "ya mizania' (600,000) and 'taarifa ya mizania' (600,000). The pairing is now "
            "document-vs-balance-sheet, which is what the two keys were always meant to be."),
    },
    "balance_sheet_filing_fee_section_12_act": {
        "fact": ("Ada ya kampuni ya kigeni kuwasilisha taarifa ya mizania (balance sheet) kwa Msajili "
                 "ni TZS 600,000 (BRELA fee schedule item 15(iii), as at 2026-10-06; Companies "
                 "Act Cap.212 R.E.2023, Part XII, ss.437-447). SUPERSEDES USD 220 (published as at 2026-06-30)."),
        "correct_value": "TZS 600,000 (item 15(iii), Companies Act Cap.212 Part XII, ss.437-447)",
        "superseded_value": "USD 220 (published as at 2026-06-30, June capture item 14)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV,
    },
    # --- the local-company items -------------------------------------------------------------
    "company_registration_fee_no_share_capital": {
        "fact": ("Registration fee for a company WITHOUT share capital is TZS 500,000 "
                 "(BRELA fee schedule item 2, as at 2026-10-06). SUPERSEDES TZS 300,000 "
                 "(published as at 2026-06-30). This resolves the DISPUTE recorded in CLAUDE.md "
                 "Section 11 -- the two readings were not contradictory, they were two dates."),
        "correct_value": "TZS 500,000 (item 2)",
        "superseded_value": "TZS 300,000 (published as at 2026-06-30)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier; the recorded dispute is RESOLVED as a "
                  "supersession, not a misreading",
        "correction_note": SUPERSEDED_NOTE + (
            " ⛔ AND IT SETTLES A DISPUTE THE PROJECT HAD FRAMED WRONGLY. CLAUDE.md recorded "
            "'300,000 -- DISPUTED: the same BRELA fee page item 2 reads TZS 500,000', treating "
            "it as two irreconcilable readings of one page and therefore as a reliability "
            "problem. It was never that: the June capture says 300,000 and the October capture "
            "says 500,000, both correctly read, four months apart. A 'dispute' between two "
            "undated readings of a living page is a DATE problem wearing the costume of an "
            "accuracy problem -- and the fix is to date every capture, not to adjudicate between "
            "them. Verbatim October: 'Usajili wa Kampuni ambayo haina mtaji wa hisa 500,000/='."),
        "_APPEND_VERIFIED_BY": PROV,
    },
    # --- the band table: narrowed to point at the re-authored fact ----------------------------
    "company_registration_fee_5": {
        "fact": ("Ada ya kusajili kampuni kwa mtaji wa hisa zaidi ya TZS 50,000,000 hadi TZS "
                 "100,000,000 ni TZS 400,000 (BRELA fee schedule item 1(e), as at 2026-10-06). "
                 "⚠️ THIS IS NO LONGER THE TOP BAND. SUPERSEDES TZS 440,000, which was the fee "
                 "for an OPEN-ENDED 'above TZS 50,000,000' band in the five-band June schedule. "
                 "The October schedule has NINE bands and four of them sit above this one -- see "
                 "company_registration_fee_bands for the whole table."),
        "correct_value": "TZS 400,000 (band 1(e): above 50,000,000 up to 100,000,000)",
        "superseded_value": ("TZS 440,000 for an open-ended 'above TZS 50,000,000' band "
                             "(published as at 2026-06-30)"),
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "RE-AUTHORED 2026-10-06 -- the band structure changed, not only the amount",
        "correction_note": SUPERSEDED_NOTE + (
            " ⛔ RE-AUTHORED RATHER THAN EDITED, and the reason is the whole point. Changing "
            "440,000 to 400,000 would have produced a fact that is numerically current and "
            "STRUCTURALLY WRONG: it would still describe the fee as applying to everything above "
            "TZS 50,000,000, so a company with TZS 2,000,000,000 of share capital would be quoted "
            "400,000 instead of 600,000. A band edge is not a number, it is an interval, and a "
            "schedule that goes from five intervals to nine cannot be patched one figure at a "
            "time."),
        "_APPEND_VERIFIED_BY": PROV,
    },
    "company_share_value_threshold_5_min": {
        "fact": ("TZS 50,000,000 is the FLOOR of share-capital registration band 1(e) in BRELA's "
                 "fee schedule as at 2026-10-06 -- a CLOSED band running to TZS 100,000,000. "
                 "The figure is unchanged from June; its MEANING is not. In the June schedule "
                 "this was the floor of the open-ended top band. See "
                 "company_registration_fee_bands for the full nine-band table."),
        "correct_value": "TZS 50,000,000 -- floor of band 1(e), which closes at 100,000,000",
        "verified_as_at": "2026-10-06",
        "status": "RE-AUTHORED 2026-10-06 -- same figure, different band structure",
        "correction_note": (
            "2026-10-06: THE VALUE DID NOT CHANGE AND THE FACT DID. This is the shape an "
            "amount-only sweep cannot see: 50,000,000 is still a band floor, so every check that "
            "compares figures passes, while the band it floors went from OPEN-ENDED to CLOSED at "
            "100,000,000. A fact can go stale without any of its numbers moving."),
        "_APPEND_VERIFIED_BY": PROV,
    },
    # --- SCOPE EXPANSION, REPORTED NOT ASSUMED ------------------------------------------------
    #
    # Six facts were authorised; a scope check raised it to nine. Reading the capture line by
    # line raises it to TWELVE, and the three below are the same act of reading the same page:
    # their values changed too, and leaving them is knowingly serving a wrong figure for exactly
    # the reason the authorisation rejected for USD 25. Amended here and reported as an expansion.
    #
    # ⛔ THREE MORE FACTS HAVE NO SUPPORT AT ALL ON THE OCTOBER PAGE AND ARE DELIBERATELY NOT
    # TOUCHED: memorandum_articles_of_association_filing_fee (June item 3, TZS 66,000),
    # stamp_duty_per_copy_memorandum_articles_copy (June item 4, TZS 10,000) and
    # stamp_duty_form_14b_fee (June item 5, TZS 1,200). They are ABSENT from the October
    # schedule, and absence is not a value. Whether a vanished line item was abolished, folded
    # into another fee, or moved to a page we have not fetched is a question no capture answers,
    # and guessing would be the mirror of the effective_date error: inventing a fact to avoid
    # recording an unknown. Flagged in _unresolved_items.brela_vanished_fee_line_items.
    "file_search_fee": {
        "fact": ("Ada ya kutafuta jalada la kampuni yoyote BRELA ni TZS 5,000 "
                 "(BRELA fee schedule item 9, as at 2026-10-06). SUPERSEDES TZS 3,000 "
                 "(published as at 2026-06-30, June item 12)."),
        "correct_value": "TZS 5,000 (item 9)",
        "superseded_value": "TZS 3,000 (published as at 2026-06-30)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV + (
            " Verbatim October item 9: 'Gharama za kutafuta jalada la kampuni yoyote 5,000/='; "
            "June item 12: 'Gharama za kutafuta jalada lolote/au kupekua kitu chochote ni Tsh. "
            "3,000'."),
    },
    "file_search_report_fee": {
        "fact": ("Ada ya kupata ripoti maalum ya taarifa za kampuni BRELA ni TZS 30,000 "
                 "(BRELA fee schedule item 10, as at 2026-10-06). SUPERSEDES TZS 22,000 "
                 "(published as at 2026-06-30, June item 13)."),
        "correct_value": "TZS 30,000 (item 10)",
        "superseded_value": "TZS 22,000 (published as at 2026-06-30)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV + (
            " Verbatim October item 10: 'Kupata ripoti maalum ya taarifa za kampuni 30,000/='. "
            "⚠️ THE WORDING ALSO MOVED: June item 13 read 'Gharama kwa ajili ya ripoti ya "
            "utafutaji kwa faili ni Tsh. 22,000' (a file SEARCH report); October says 'ripoti "
            "maalum ya taarifa za kampuni' (a special report of company information). Treated as "
            "the same line item re-worded, which is a judgement and is recorded as one."),
    },
    "certified_copy_certificate_of_registration_fee": {
        "fact": ("Ada ya kupata nakala ya Cheti cha Usajili au Cheti cha Uzingatiaji wa Sheria "
                 "BRELA ni TZS 10,000 (BRELA fee schedule item 12, as at "
                 "2026-10-06). SUPERSEDES TZS 4,000 (published as at 2026-06-30, June item 15)."),
        "correct_value": "TZS 10,000 (item 12)",
        "superseded_value": "TZS 4,000 (published as at 2026-06-30)",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_as_at": "2026-10-06",
        "status": "UPDATED 2026-10-06 -- portal tier, dated and hashed capture",
        "_APPEND_VERIFIED_BY": PROV + (
            " Verbatim October item 12: 'Kupata nakala ya Cheti cha Usajili au Cheti cha "
            "Uzingatiaji wa Sheria 10,000/=' -- the October line covers a compliance certificate "
            "too, which June's 'nakala ya Cheti cha Usajili' did not mention."),
    },
    # --- citation fact: CONFIRMED, not changed ------------------------------------------------
    "act_section_12": {
        # ⛔ NO VALUE CHANGE. This fact is the CITATION, not a fee, and the October capture
        # CONFIRMS it: the page's own heading for the foreign-company block reads "Ada chini ya
        # Masharti ya Sehemu ya XII ya Sheria (Makampuni ya Nje)". An earlier scoping note of
        # mine listed this key under "USD 25 -> TZS 70,000", which was wrong -- it holds no fee.
        # Recording the confirmation is the correct action, not an edit (R28: a pass that only
        # ever edits never earns the confidence to also NOT edit).
        "verified_as_at": "2026-10-06",
        "_APPEND_VERIFIED_BY": (
            " || RE-CONFIRMED 2026-10-06, independently and from the regulator's own current "
            f"page: {OCT} (sha256 {OCT_SHA[:24]}..., fetched 2026-10-06T14:04:42Z) heads its "
            "foreign-company fee block 'Ada chini ya Masharti ya Sehemu ya XII ya Sheria "
            "(Makampuni ya Nje)' and repeats 'Sehemu ya XII ya Sheria' inside item 15(ii). "
            "BRELA still says Part XII, four months after this project overruled it and five "
            "weeks after the statute itself was read to confirm Part XII. NO VALUE CHANGE: this "
            "fact holds a citation, not a fee, and the correct action on a fact that survives "
            "verification is to upgrade its provenance, not to edit it (R28)."),
    },
}

# --- the re-authored band table, as a NEW fact ------------------------------------------------
NEW_FACTS = {
    "company_registration_fee_bands": {
        "fact": ("Ada ya kusajili kampuni yenye mtaji wa hisa inategemea THAMANI YA HISA, na BRELA "
                 "ina mikondo TISA: zaidi ya TZS 20,000 hadi 1,000,000 = TZS 95,000; hadi 5,000,000 = 175,000; hadi 20,000,000 = 260,000; hadi "
                 "50,000,000 = 290,000; hadi 100,000,000 = 400,000; hadi 500,000,000 = 450,000; "
                 "hadi 1,000,000,000 = 500,000; hadi 10,000,000,000 = 600,000; zaidi ya "
                 "10,000,000,000 = TZS 1,000,000."),
        "correct_value": ("9 bands: 95,000 / 175,000 / 260,000 / 290,000 / 400,000 / 450,000 / "
                          "500,000 / 600,000 / 1,000,000 TZS"),
        "superseded_value": ("5 bands ending in an OPEN-ENDED 'above TZS 50,000,000 = 440,000' "
                             "(published as at 2026-06-30)"),
        "primary_source": "https://www.brela.go.tz/pages/tozo-za-kampuni",
        "source_type": "government_portal",
        "effective_date": "unknown -- changed between 2026-06-30 and 2026-10-06",
        "verified_by": (
            "Read directly from a dated, hashed capture of BRELA's own 'Ada za Kampuni' page: "
            f"{OCT} (sha256 {OCT_SHA}, 57,804 bytes, fetched 2026-10-06T14:04:42Z). Verbatim "
            "item 1 'Usajili wa Kampuni yenye Mtaji wa Hisa (Kulingana na Thamani)': "
            "(a) Zaidi ya Tsh. 20,000 hadi Tsh. 1,000,000 95,000/=; (b) ... hadi Tsh. 5,000,000 "
            "175,000/=; (c) ... hadi Tsh. 20,000,000 260,000/=; (d) ... hadi Tsh. 50,000,000 "
            "290,000/=; (e) ... hadi Tsh. 100,000,000 400,000/=; (f) ... hadi Tsh. 500,000,000 "
            "450,000/=; (g) ... hadi Tsh. 1,000,000,000 500,000/=; (h) ... hadi Tsh. "
            "10,000,000,000 600,000/=; (i) Zaidi ya Tsh. 10,000,000,000 1,000,000/=. "
            "effective_date UNKNOWN: 2026-10-06 is the observation date. The June capture "
            f"{JUNE} (sha256 {JUNE_SHA}) shows the superseded five-band table."),
        "verified_as_at": "2026-10-06",
        "status": "NEW 2026-10-06 -- re-authored because the band STRUCTURE changed",
        "correction_note": (
            "AUTHORED RATHER THAN PATCHED, on instruction and for a reason worth keeping: the "
            "June schedule had five bands with an open-ended top; the October schedule has nine "
            "with a closed top. The two legacy keys company_registration_fee_5 and "
            "company_share_value_threshold_5_min described 'band 5' as 'above TZS 50,000,000', "
            "which is now band (e) of nine -- so editing their amounts would have left facts "
            "that are numerically current and structurally wrong, quoting the 50M-100M fee to a "
            "company with billions in share capital. Swahili-first and ask-led: it opens with "
            "what the user asks about (ada ya kusajili kampuni, thamani ya hisa), not with the "
            "schedule's own label."),
    },
}

UNRESOLVED = {
    "brela_companies_fees_regulations": {
        "status": "SEARCH LEAD -- NOT LOCATED",
        "question": ("Which instrument replaced BRELA's company fee schedule between 2026-06-30 "
                     "and 2026-10-06?"),
        "why_it_matters": (
            "Companies Act Cap.212 ss.458 and 489(3) delegate every fee AMOUNT to Minister's "
            "regulations, so NO fee in this family is settleable from the Act. The Fees "
            "Regulations are the only statute-tier target, and locating them is also the only "
            "way to give any of these facts an effective_date instead of 'unknown'."),
        "the_lead": (
            "⛔ THE REDENOMINATION IS THE STRONGEST SIGNAL THIS PROJECT HAS HAD ON THIS QUESTION, "
            "and it is a signal rather than a caveat. The ENTIRE foreign-company block switched "
            "from USD to TZS (750/220/220/25 USD -> 2,000,000/600,000/600,000/70,000 TZS) inside "
            "a known four-month window. A currency denomination change across a whole block is a "
            "SUBSTANTIVE AMENDMENT by a dated instrument, not a price adjustment and not a "
            "rounding -- 'USD 25 is about TZS 70k' is arithmetic, not evidence. Alongside it: "
            "the share-capital table went 5 bands -> 9; the foreign block moved from item 14 to "
            "item 15; and three June line items VANISHED (file-opening 66,000, stamp duty "
            "10,000, Form 14b 1,200). A schedule that is renumbered, redenominated and re-banded "
            "at once was replaced wholesale."),
        "search_terms": ("Companies (Fees) Regulations 2026; Kanuni za Ada za Makampuni; GN "
                         "gazetted between 2026-06-30 and 2026-10-06; Companies Act Cap.212 "
                         "s.458 / s.489(3) regulations"),
        "routes_already_closed": (
            "brela.go.tz law pages return HTTP 500 (2026-10-04). tanzlii.org search is a "
            "client-rendered SPA behind Cloudflare Turnstile -- a genuine block, not a tool bug "
            "(R30, tested). NOT YET TRIED: the Government Gazette index for Jul-Sep 2026, and "
            "the Ministry of Industry and Trade site."),
        "recorded": "2026-10-06",
    },
    "brela_vanished_fee_line_items": {
        "status": "OPEN -- three locked facts now have NO support on the regulator's own page",
        "facts_affected": ["memorandum_articles_of_association_filing_fee (TZS 66,000)",
                           "stamp_duty_per_copy_memorandum_articles_copy (TZS 10,000)",
                           "stamp_duty_form_14b_fee (TZS 1,200)"],
        "question": ("Were these line items abolished, folded into another fee, or moved to a "
                     "page we have not fetched?"),
        "why_not_edited": (
            "⛔ ABSENCE IS NOT A VALUE, and inventing one would be the mirror of the "
            "effective_date error these same amendments were careful to avoid. All three are "
            "present in the June capture (items 3, 4, 5) and absent from the October capture. "
            "Three readings are all consistent with that and they imply different advice: "
            "abolished (the fee is now zero), folded in (the fee still exists inside another "
            "line), or relocated (the fee exists and we are looking at the wrong page). Nothing "
            "in either capture distinguishes them, so the facts are left AS THEY STAND with this "
            "item recording that their source no longer carries them -- which is strictly more "
            "honest than either editing them to a guess or deleting them."),
        "what_would_settle_it": (
            "the Companies (Fees) Regulations located under the lead above; or BRELA's "
            "incorporation-steps page (brela.go.tz/pages/hatua-za-usajili, cached at "
            "data/source_documents/brela/brela_hatua_10.html from June) re-fetched live, which "
            "may itemise what an applicant pays today."),
        "recorded": "2026-10-06",
    },
}


def main():
    raw = io.open(FACTS, encoding="utf-8").read()
    facts = json.loads(raw)
    before = {k: json.loads(json.dumps(facts[k])) for k in AMENDMENTS}

    # ---- the captures must be the bytes this script claims they are (R34, and the manifest
    # ---- lesson: an edition/version is a claim about BYTES, not about a path) ---------------
    import hashlib
    for path, want in ((JUNE, JUNE_SHA), (OCT, OCT_SHA)):
        full = os.path.join(REPO, *path.split("/"))
        assert os.path.exists(full), f"{path} is missing -- refusing to cite a capture I cannot read"
        got = hashlib.sha256(open(full, "rb").read()).hexdigest()
        assert got == want, (
            f"{path} sha256 is {got}, this script asserts {want}. The file changed under its own "
            f"name, so every verbatim quotation below is unverified. REFUSING TO AMEND.")

    # ---- and the quoted figures must actually be IN the captures, not just in my notes -----
    oct_text = open(os.path.join(REPO, *OCT.split("/")), encoding="utf-8",
                    errors="replace").read()
    june_text = open(os.path.join(REPO, *JUNE.split("/")), encoding="utf-8",
                     errors="replace").read()
    for needle in ("70,000", "2,000,000", "600,000", "500,000", "400,000", "1,000,000",
                   "Sehemu ya XII"):
        assert needle in oct_text, f"{needle!r} is not in the October capture -- do not cite it"
    for needle in ("440,000", "300,000", "750", "220", "25", "Kifungu XII"):
        assert needle in june_text, f"{needle!r} is not in the June capture -- do not cite it"

    for key, patch in AMENDMENTS.items():
        assert key in facts, f"{key} is not in locked_facts.json -- refusing to create it here"
        for field, value in patch.items():
            if field == "_APPEND_VERIFIED_BY":
                existing = facts[key].get("verified_by") or ""
                assert existing, f"{key}: nothing to append to -- verified_by is empty"
                if value.strip() not in existing:
                    facts[key]["verified_by"] = existing.rstrip() + value
                continue
            if field == "correction_note" and facts[key].get("correction_note"):
                # ⛔ NEVER OVERWRITE AN EXISTING correction_note. Several of these facts carry
                # the 2026-10-05 Part XII reversal note, which is the only record of how that
                # error entered and was undone. R27's whole point: a correction amends, it does
                # not replace. The new note is PREPENDED and the old one kept behind " || ".
                if value.strip() not in facts[key]["correction_note"]:
                    facts[key]["correction_note"] = (
                        value + " || PRIOR NOTE, KEPT: " + facts[key]["correction_note"])
                continue
            facts[key][field] = value

    # ---- R27 GUARD: every pre-existing field NOT named in the patch must be untouched -------
    violations = []
    for key, patch in AMENDMENTS.items():
        for field, old in before[key].items():
            if field in patch or (field == "verified_by" and "_APPEND_VERIFIED_BY" in patch):
                continue
            if facts[key].get(field) != old:
                violations.append((key, field, str(old)[:80], str(facts[key].get(field))[:80]))
        if "_APPEND_VERIFIED_BY" in patch:
            if not (facts[key].get("verified_by") or "").startswith(
                    (before[key].get("verified_by") or "").rstrip()):
                violations.append((key, "verified_by APPEND DID NOT PRESERVE THE ORIGINAL",
                                   "", ""))
            assert "_APPEND_VERIFIED_BY" not in facts[key], (
                f"{key}: the append marker leaked into the stored fact")
        # a prepended correction_note must still CONTAIN the old one
        if "correction_note" in patch and before[key].get("correction_note"):
            assert before[key]["correction_note"][:120] in facts[key]["correction_note"], (
                f"{key}: the prior correction_note was lost. On several of these facts that note "
                f"is the only record of the 2026-10-05 Part XII reversal.")
        lost = [f for f in before[key] if f not in facts[key]]
        if lost:
            violations.append((key, f"FIELDS DROPPED: {lost}", "", ""))
    assert not violations, (
        "R27 VIOLATION -- an amendment changed or dropped a field it did not name:\n"
        + "\n".join(map(str, violations)))

    # ---- new facts ---------------------------------------------------------------------------
    for key, obj in NEW_FACTS.items():
        assert key not in facts, f"{key} already exists -- amend it, do not re-create it"
        facts[key] = obj

    # ---- unresolved items -------------------------------------------------------------------
    facts.setdefault("_unresolved_items", {})
    for key, obj in UNRESOLVED.items():
        facts["_unresolved_items"][key] = obj

    # ---- invariants the suite already enforces, checked here so the failure names the cause --
    for key in list(AMENDMENTS) + list(NEW_FACTS):
        for pat in facts[key].get("wrong_patterns") or []:
            try:
                re.compile(pat)
            except re.error as exc:
                raise AssertionError(f"{key}: wrong_patterns does not compile: {pat!r} ({exc})")
        v = facts[key].get("verified_as_at")
        if v and v != "unknown":
            assert v in (facts[key].get("verified_by") or ""), (
                f"{key}: verified_as_at={v} does not appear in its own verified_by text")
        # ⚠️ effective_date must NOT silently become the observation date. Amendment 1.
        ed = facts[key].get("effective_date")
        if ed and ed != "unknown" and not ed.startswith("unknown"):
            raise AssertionError(
                f"{key}: effective_date={ed!r}. These facts have NO located instrument, so the "
                f"only honest value is 'unknown -- changed between ...'. Putting the observation "
                f"date here is R29 mode 3 in the making.")

    with io.open(FACTS, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"amended {len(AMENDMENTS)} BRELA facts; added {len(NEW_FACTS)} re-authored fact; "
          f"recorded {len(UNRESOLVED)} search lead")
    for key, patch in AMENDMENTS.items():
        print(f"  {key:60s} {', '.join(sorted(patch))}")
    for key in NEW_FACTS:
        print(f"  + {key}")
    print("\nR27 guard: clean. Both captures sha256-verified. Every quoted figure present in "
          "the capture it is attributed to.")
    print(f"total facts now: {len([k for k in facts if not k.startswith('_')])}")


if __name__ == "__main__":
    main()
