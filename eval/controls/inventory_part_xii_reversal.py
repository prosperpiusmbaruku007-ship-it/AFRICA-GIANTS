# -*- coding: utf-8 -*-
"""THE PART XII REVERSAL -- a complete inventory of every site downstream of the 2026-08-31
"correction", checked against the Act's own structure rather than flipped by find-and-replace.

WHAT THE ACT SAYS. Companies Act Cap.212 REVISED EDITION 2023, fetched from brela.go.tz
(394pp, 3,215,470 bytes, HTTP 200, 2026-10-04). Full Part structure extracted from the text:

    PART XI    WINDING UP OF UNREGISTERED COMPANIES            s.429+
    PART XII   COMPANIES INCORPORATED OUTSIDE TANZANIA         ss.437-447
    PART XIII  GENERAL PROVISIONS AS TO REGISTRATION           s.454+

    s.437.-(1) "Sections 438 to 447 shall apply to all foreign companies that are companies
               incorporated outside Tanzania..."

    ss.314-328 are WINDING-UP MACHINERY inside Part VIII (WINDING UP, s.270+): settlement of
    contributories, payment of debts due from a contributory, power of court to make calls,
    appointment of a special manager, public examination of promoters.

SO THE FOREIGN-COMPANY REGIME IS PART XII, ss.437-447. BRELA's own page, which labels it
"Kifungu XII", is RIGHT. This project's record is WRONG.

=============================================================================================
WHY THIS IS NOT AN EDITION MISMATCH, which is the first explanation to reach for and is wrong.
=============================================================================================
The natural reading is R29 mode 2: our record described an earlier edition, R.E.2023 renumbered,
and the citation went stale. THE ACT'S OWN RENUMBERING NOTES EXCLUDE THIS. Each section carries
a bracketed source note giving its number in the prior edition:

    R.E.2023 s.438 <- prior s.433      s.440 <- prior s.435      s.445 <- prior s.440
    R.E.2023 s.439 <- prior s.434      s.442 <- prior s.437

The shift is +5. For foreign companies to have sat at ss.320-328 in some prior edition the shift
would have to be about -115. NO EDITION OF Cap.212 HAS EVER PUT THE FOREIGN-COMPANY REGIME AT
ss.320-328. The range in our record corresponds to nothing.

Nor does the rest of the 2026-08-31 `verified_by`, which claims: "Direct read of Companies Act
Cap.212 table of contents and body text, 2026-08-31. Part XII (ss.314-319) is confirmed to be
'Winding up of unregistered companies'." Against the Act:
  * winding up of unregistered companies is PART XI, s.429+ -- not Part XII
  * ss.314-319 are contributories/calls inside Part VIII -- not that Part either
  * ss.320-328 are the sections immediately following them, same machinery

Three claims, none reproducing. This is not a stale edition and not a renumbering: IT IS A
`verified_by` ASSERTING A PRIMARY READ THAT CANNOT BE REPRODUCED IN ANY DIRECTION. That is the
R18 shape -- the read was never committed as an artifact, so nothing could re-derive it -- and
it is the reason this file exists: the inventory is recomputed from the Act and from the repo on
every run, so no future reader has to trust this paragraph either.

=============================================================================================
THE PROPAGATION, which is the part worth more than the citation fix.
=============================================================================================
A correction that becomes the baseline for judging later sources will propagate its own error
into every subsequent check -- and each propagation looks like the correction WORKING:

  2026-08-31  the "correction" is written into locked_facts + CLAUDE.md Section 11
  2026-09-01  the corpus is swept; 13 training rows saying "Section XII" are QUARANTINED
              -- i.e. 13 rows are removed from training FOR BEING RIGHT
  2026-09-05  a live reply still says "Section XII" (ext_15) and is adjudicated WRONG
  2026-09-22  row 171 is rewritten in the deployed RAG index: the CORRECT citation is
              DELETED from what users receive and replaced with the wrong one
  2026-09-23  the wrong_patterns are rewritten to cover Swahili word order, because the
              guard had been "blind to the language it guards". The rewrite SUCCEEDS -- and
              what it achieves is a guard that now rejects the correct citation in BOTH
              word orders. The better the guard got, the harder it enforced the error.
  2026-10-04  BRELA's page is read as "a regulator summary that can be wrong about what it
              summarises", on the strength of this very record. The page was right.

Every step is competent. Every step is in the wrong direction, because each one took the
previous step as its baseline. R29 mode 3 (correctly-cited-but-superseded) arriving from INSIDE
the project rather than from a superseded instrument: the thing that went stale was our own
correction, and nothing downstream could see past it.

ALSO RECORDED: the quarantine sweep was ASYMMETRIC, and the asymmetry is instructive. It
quarantined 13 rows saying "Section XII" (English token) and MISSED a row saying "Sehemu XII"
(Swahili token) -- which is still in train_sft.jsonl today. So the one row the sweep failed to
remove is the one row that was correct all along, and it survived by being phrased in the
language the 2026-09-01 patterns could not see. The same blindness that the 2026-09-23 rewrite
was built to fix is what preserved the right answer.

=============================================================================================
LANDED 2026-10-05. All 16 sites fixed except the two held by decision; see SITE_STATUS below.
=============================================================================================
A SEVENTEENTH-SITE WARNING, because the first run of this inventory found 15 and MISSED the one
that mattered most: `kaggle/regenerate_rag_e5.py`'s payload gate would have REFUSED TO BUILD the
corrected index. The inventory searched locked_facts, the RAG text, the corpora, the gold sets,
the tests and the docs -- and not the BUILD SCRIPTS. It was found only because fixing the RAG
text required grepping for the authored source of that text. So: an inventory of a defect's
enforcement points must include everything that can REFUSE A FIX, not only everything that
asserts the fact. Those are different sets, and the second one is the one that bites.

REPORT-ONLY. This script changes nothing. It enumerates, and it fails if the enumeration has
drifted -- so a site fixed without updating the inventory, or a NEW site appearing, is loud.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# What the Act establishes, as a checkable structure rather than prose.
# ---------------------------------------------------------------------------
ACT = {
    "source": "https://www.brela.go.tz/uploads/documents/"
              "sw-1758107576-THE%20COMPANIES%20ACT,%20REVISED%20EDITION,%202023.pdf",
    "edition": "Cap.212 Revised Edition 2023",
    "fetched": "2026-10-04",
    "http": 200,
    "bytes": 3215470,
    "parts": {
        "XI":   {"heading": "WINDING UP OF UNREGISTERED COMPANIES", "first_section": 429},
        "XII":  {"heading": "COMPANIES INCORPORATED OUTSIDE TANZANIA", "first_section": 437,
                 "range": "ss.437-447"},
        "XIII": {"heading": "GENERAL PROVISIONS AS TO REGISTRATION", "first_section": 454},
    },
    "ss_314_328": "winding-up machinery inside PART VIII (WINDING UP, s.270+): contributories, "
                  "calls, special manager, public examination of promoters",
    "renumbering_notes": {"438": 433, "439": 434, "440": 435, "442": 437, "445": 440},
    "correct_citation": "Companies Act Cap.212 R.E.2023, Part XII, ss.437-447",
    "fees_are_delegated": "s.458 and s.489(3) -- the Act sets NO fee amounts, so no fee figure "
                          "is settleable from it (see gold_source_register.json)",
}

# The claims the 2026-08-31 record makes, each paired with what the Act says.
REFUTED_CLAIMS = [
    {"claim": "the foreign-company regime is Part XIII",
     "act": "Part XIII is 'GENERAL PROVISIONS AS TO REGISTRATION', s.454+",
     "verdict": "REFUTED"},
    {"claim": "the foreign-company regime is ss.320-328",
     "act": "ss.320-328 are winding-up machinery in Part VIII; the regime is ss.437-447, and "
            "the Act's own renumbering notes show a +5 shift, not -115",
     "verdict": "REFUTED -- corresponds to no edition"},
    {"claim": "Part XII governs winding up of unregistered companies",
     "act": "that is Part XI, s.429+",
     "verdict": "REFUTED"},
    {"claim": "winding up of unregistered companies is ss.314-319",
     "act": "ss.314-319 are contributories/calls in Part VIII; Part XI begins at s.429",
     "verdict": "REFUTED"},
]

# ---------------------------------------------------------------------------
# The inventory. Every site, with what it currently says and what the Act makes of it.
# `direction` is the part that matters: a site can be wrong by ASSERTING the bad citation,
# or wrong by PUNISHING the good one. The second kind is invisible to a find-and-replace.
# ---------------------------------------------------------------------------
EXPECTED_SITES = {
    # --- locked facts -------------------------------------------------------
    "locked_facts:act_section_12": {
        "says": "Part XIII (ss.320-328) ... NOT Part XII, which governs winding up of "
                "unregistered companies (ss.314-319)",
        "direction": "ASSERTS_WRONG",
        "note": "its verified_by claims a direct read that does not reproduce; R15 regen fact",
    },
    "locked_facts:act_section_12:wrong_patterns": {
        "says": "two patterns matching <part|section|kifungu> XII near <foreign company>, in "
                "both word orders",
        "direction": "PUNISHES_RIGHT",
        "note": "THE DEFECT DEFENDS ITSELF. Verified by this script: both patterns fire on the "
                "now-correct citation. A guard rejecting right answers.",
    },
    "locked_facts:document_filing_fee_section_12_act_excluding_balance_sheet": {
        "says": "USD 220 (Companies Act Cap.212, Part XIII, ss.320-328)",
        "direction": "ASSERTS_WRONG", "note": "amount unaffected; citation only",
    },
    "locked_facts:balance_sheet_filing_fee_section_12_act": {
        "says": "USD 220 (Companies Act Cap.212, Part XIII, ss.320-328)",
        "direction": "ASSERTS_WRONG", "note": "amount unaffected; citation only",
    },
    "locked_facts:brela_foreign_late_filing_penalty": {
        "says": "USD 25/month (foreign company, Part XIII, ss.320-328)",
        "direction": "ASSERTS_WRONG",
        "note": "its verified_by explicitly overrode BRELA's own 'Kifungu XII' label as "
                "'colloquial shorthand'. BRELA was right. The USD 25 figure is a separate, "
                "still-unresolved question -- the Act delegates fees (s.458, s.489(3)).",
    },
    # --- deployed RAG index (what users actually receive) -------------------
    "rag_index:row_101": {
        "says": "act section 12: ... governed by Part XIII (ss.320-328) ... NOT Part XII",
        "direction": "ASSERTS_WRONG",
        "note": "both kaggle/ and chike-inference/ copies; R15 regen required",
    },
    "rag_index:row_171": {
        "says": "Kampuni ya kigeni (Companies Act Cap.212, Part XIII, ss.320-328) ikichelewa...",
        "direction": "ASSERTS_WRONG",
        "note": "THE CORRECT CITATION WAS DELETED FROM PRODUCTION HERE on 2026-09-22, as a "
                "stale defect. Users have received the wrong citation since.",
    },
    "rag_index:row_181": {
        "says": "Kampuni ya kigeni (kifungu 12): kuwasilisha nyaraka USD 220, mizania USD 220",
        "direction": "ASSERTS_RIGHT_UNCAUGHT",
        "note": "a THIRD deployed row, in a third form. Verified by this script: the "
                "2026-09-23 guard does NOT match 'kifungu 12' -- the numeral branch requires "
                "the English 'part'. So the row that is substantively CORRECT about the "
                "numeral is also the row no guard can see, in either direction.",
    },
    # --- training corpus ----------------------------------------------------
    "quarantine:tier3_confirmed_wrong_quarantine_2026_09_01.jsonl": {
        "says": "13 rows saying '(Section XII)', removed from training with the reason 'The "
                "correct citation is Part XIII, ss.320-328'",
        "direction": "PUNISHES_RIGHT",
        "note": "quarantined FOR BEING RIGHT on the numeral. They are loose on the label "
                "('Section' where the Act says 'Part') -- a style imprecision, not the "
                "citation error they were removed for.",
    },
    "training:train_sft.jsonl:3851": {
        "says": "kusajili TAWI (branch) kwa BRELA chini ya Sehemu XII ya Companies Act",
        "direction": "ASSERTS_RIGHT_UNCAUGHT",
        "note": "STILL IN TRAINING, and correct. Survived the 2026-09-01 sweep because it uses "
                "the Swahili 'Sehemu' where the patterns required English. The sweep's blind "
                "spot preserved the one right answer.",
    },
    "training:cleaned_pairs_batch_009.jsonl:98": {
        "says": "same pair as train_sft.jsonl:3851",
        "direction": "ASSERTS_RIGHT_UNCAUGHT", "note": "source of the SFT row",
    },
    # --- scoring keys -------------------------------------------------------
    "gold:ext_15": {
        "says": "USD 25 per month (Companies Act Cap.212, Part XIII, ss.320-328), NOT the "
                "TZS 2,500/month local-company rate",
        "direction": "ASSERTS_WRONG",
        "note": "THE ONLY affected scoring key in all three corpora (78 + 48 + 150 rows; the "
                "other two are clean). Gold is now part-confirmed-wrong (citation) and "
                "part-unresolved (the USD 25 figure). Verdict left ALONE -- half a correction "
                "must not flip a count.",
    },
    # --- build gate (SITE 16, MISSED BY THE FIRST INVENTORY) ----------------
    "kaggle/regenerate_rag_e5.py:payload_gate": {
        "says": "asserted `'part xiii' in row` and refused to upload the index without it, plus "
                "a corpus-wide sweep banning the string 'Section XII' from every built row",
        "direction": "PUNISHES_RIGHT",
        "note": "⛔ THE WORST OF THE SIXTEEN AND THE FIRST INVENTORY MISSED IT. This gate would "
                "have REFUSED TO BUILD THE CORRECTED INDEX, demanding the wrong citation as its "
                "entry price -- so the R15 regen queued to fix the other sites could not have "
                "run. It is also the best-built control in the set: keyed rather than lexical, "
                "failing loudly on absence rather than passing by it, written in direct response "
                "to a real live defect, with R20 and R21 both cited in its own comment. NONE OF "
                "THAT HELPED, because a control can only be as right as the fact it encodes. A "
                "well-built gate on a reversed premise is strictly WORSE than a weak one: it has "
                "more power to keep the error in place. Inverted 2026-10-05 -- and the inversion "
                "needed a regex, because 'part xii' IS A SUBSTRING OF 'part xiii' and the naive "
                "`in` form would have been vacuous in exactly the R20 way.",
    },
    # --- tests --------------------------------------------------------------
    "tests:test_act_section_xii_patterns.py": {
        "says": "6 MUST_FIRE cases and 6 MUST_NOT_FIRE cases encoding the 2026-08-31 reading",
        "direction": "PUNISHES_RIGHT",
        "note": "ASSERTS THE ERROR IN BOTH DIRECTIONS, which is why it is the most "
                "consequential site. MUST_FIRE includes 'Foreign companies are governed by "
                "Part XII of the Companies Act' -- now TRUE, and the test requires it to be "
                "flagged. MUST_NOT_FIRE includes 'Part XII governs winding up of unregistered "
                "companies (ss.314-319)' -- now FALSE, and the test protects it. R20's second "
                "arrival point: a test instructing maintainers not to fix a real defect.",
    },
    # --- documentation ------------------------------------------------------
    "CLAUDE.md:416": {
        "says": "Foreign company (Companies Act Cap.212, Part XIII, ss.320-328 -- NOT "
                "'Section XII'; corrected 2026-08-31)",
        "direction": "ASSERTS_WRONG", "note": "the origin the locked fact says it came from",
    },
    "CLAUDE.md:684": {
        "says": "'Section XII closed' cited as evidence Bar A is reachable",
        "direction": "ASSERTS_WRONG",
        "note": "a worked example of a closed defect that was not closed. Bar A's evidence "
                "list is itself subject to the denominator problem.",
    },
}

# Not in scope: these match the citation pattern but concern a DIFFERENT Act. Recorded so a
# future sweep does not re-raise them, and so the count above is not inflated (R26: suspect the
# specimen -- these ARE the specimen failures of a naive grep).
OUT_OF_SCOPE = {
    "datasets/.../batch_002*.jsonl: tier1a_nssf_edge_002/009": "'NSSF Act Section 12' -- the "
        "15%/5% employer-employee split. Different Act entirely.",
    "locked_facts: various 'Section 11' hits": "CLAUDE.md's own Section 11 heading, quoted "
        "inside correction_notes. Not a statutory citation.",
}


# What actually landed on 2026-10-05, per site. Two are HELD, both deliberately.
SITE_STATUS = {
    "locked_facts:act_section_12": "FIXED -- fact/correct_value/primary_source/verified_by/"
                                   "status/correction_note amended per R27; _pattern_note's "
                                   "2026-09-23 Swahili-word-order history KEPT (still true)",
    "locked_facts:act_section_12:wrong_patterns": "INVERTED -- now catch Part XIII/ss.320-328; "
                                                  "verified to block 0 of 4 correct strings and "
                                                  "catch 2 of 2 stale ones",
    "locked_facts:document_filing_fee_section_12_act_excluding_balance_sheet":
        "FIXED -- citation label only; amount and verified_as_at untouched",
    "locked_facts:balance_sheet_filing_fee_section_12_act":
        "FIXED -- citation label only; amount and verified_as_at untouched",
    "locked_facts:brela_foreign_late_filing_penalty":
        "FIXED -- citation label only; the USD 25 figure left as-is and still DISPUTED",
    "rag_index:row_101": "FIXED AT SOURCE -- derived from act_section_12; reaches the index on "
                         "the queued R15 regen. The generated rag_facts_text.json is NOT "
                         "hand-edited: it is paired with rag_embeddings.npy, and editing text "
                         "without re-embedding leaves the vector encoding the OLD string, so "
                         "retrieval would match on text the user never sees. Worse than the gap.",
    "rag_index:row_171": "FIXED AT SOURCE -- scripts/precompute_rag_embeddings.py, the "
                         "hand-authored CONCISE_BILINGUAL_FACTS entry; same regen caveat",
    "rag_index:row_181": "LEFT AS IS -- 'kifungu 12' is correct on the numeral. Rewriting a "
                         "correct row to tidy its label is a content edit needing its own "
                         "justification (R25) and has none.",
    "kaggle/regenerate_rag_e5.py:payload_gate": "INVERTED -- plus `import re` added, which the "
                                                "file lacked; without it the new gate would have "
                                                "NameError'd on Kaggle at build time",
    "quarantine:tier3_confirmed_wrong_quarantine_2026_09_01.jsonl":
        "RESTORED -- 7 of 13 instances returned to authored sources; 6 live in export artifacts "
        "(train_sft*.jsonl) and return on regeneration, never by hand. The 13 entries are FOUR "
        "distinct pairs across seven files. 9 of them assert the disputed USD 25 -- restored "
        "anyway, to match the unchanged locked fact, and listed in the harness so the fee "
        "resolution can find them in one lookup. Harness: "
        "scripts/restore_part_xii_quarantine.py",
    "training:train_sft.jsonl:3851": "LEFT -- already correct ('Sehemu XII'), and an export "
                                     "artifact regardless",
    "training:cleaned_pairs_batch_009.jsonl:98": "LEFT -- already correct",
    "gold:ext_15": "CITATION FIXED, VERDICT HELD. Carries a _scoring_key_correction block: the "
                   "citation limb is settled in the model's favour, the FIGURE limb is "
                   "unresolved, so the verdict now rests on the figure alone. Half a correction "
                   "must not flip a count.",
    "tests:test_act_section_xii_patterns.py": "INVERTED, history kept in the docstring per R17's "
                                              "corollary. The two verbatim 2026-09-05 live "
                                              "artifacts moved from MUST_FIRE to MUST_NOT_FIRE "
                                              "-- unchanged text, opposite verdict.",
    "CLAUDE.md:416": "FIXED -- with the reversal, the +5-vs-115 renumbering argument, and the "
                     "open fee question recorded inline",
    "CLAUDE.md:684": "FIXED -- 'Section XII closed' WITHDRAWN from Bar A's evidence list. It was "
                     "closed in the wrong direction, so that row is now one-for-four.",
}

HELD_BY_DECISION = {
    "the USD 25 vs TZS 70,000 fee": "UNRESOLVED. The Act delegates every fee (s.458, s.489(3)); "
                                    "the Companies (Fees) Regulations were not located. Recorded "
                                    "as a standing disagreement with both sources named.",
    "the TZS 300,000 vs 500,000 registration fee": "UNRESOLVED, same gazette, same block.",
}


def _facts():
    with open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("facts", data)


# Strings that are CORRECT under the Act. A guard must not reject these.
CORRECT_CITATIONS = [
    "Kampuni ya kigeni (Part XII) ikichelewa kufungua taarifa ya mwaka hulipa USD 25 kwa mwezi.",
    "Section XII ya Sheria ya Makampuni inahusu kampuni za kigeni.",
    "Foreign companies are governed by Part XII of the Companies Act.",
    "Companies Act Cap.212, Part XII, ss.437-447",
]
# Strings that are STALE under the Act. The guard must catch these.
STALE_CITATIONS = [
    "Kampuni ya kigeni (Companies Act Cap.212, Part XIII, ss.320-328) ikichelewa kuwasilisha "
    "ritani ya mwaka: faini ni USD 25 kwa kila mwezi.",
    "Foreign companies are governed by Part XIII (ss.320-328) of the Companies Act, Cap.212.",
]
# The deployed row no guard sees, in either direction.
UNGUARDED_DEPLOYED_ROW = ("Kampuni ya kigeni (kifungu 12): kuwasilisha nyaraka USD 220, "
                          "mizania USD 220, na faini ya kuchelewa USD 25 kwa mwezi.")


def measure():
    facts = _facts()
    pats = facts["act_section_12"]["wrong_patterns"]

    blocked = [c for c in CORRECT_CITATIONS
               if any(re.search(p, c, re.I) for p in pats)]
    caught = [s for s in STALE_CITATIONS
              if any(re.search(p, s, re.I) for p in pats)]

    # ASSERTION FLIPPED 2026-10-05 ALONGSIDE THE FIX, and the flip is itself the record. Before
    # the fix this asserted `blocked` was NON-empty -- the guard DID reject correct text, which
    # was the defect being reported. Now it must be EMPTY, and the stale citation must be caught
    # instead. Both limbs are asserted, because a guard that blocks nothing is as broken as one
    # that blocks everything, and only checking both can tell them apart.
    assert not blocked, (
        f"REGRESSION: act_section_12's wrong_patterns reject the CORRECT Part XII citation "
        f"again: {blocked}. The Act says PART XII, ss.437-447 (s.437(1), Cap.212 R.E.2023). A "
        f"guard that blocks a right answer is worse than one that is blind.")
    assert len(caught) == len(STALE_CITATIONS), (
        f"the guard no longer catches the REVERSED Part XIII citation -- caught "
        f"{len(caught)}/{len(STALE_CITATIONS)}. The stale citation is what production served "
        f"between 2026-09-22 and 2026-10-05; losing this limb makes the inversion vacuous.")

    unguarded = not any(re.search(p, UNGUARDED_DEPLOYED_ROW, re.I) for p in pats)

    return {
        "_what": "Complete inventory of sites downstream of the 2026-08-31 Part XII "
                 "'correction', checked against Cap.212 R.E.2023 directly.",
        "_report_only": True,
        "act": ACT,
        "refuted_claims": REFUTED_CLAIMS,
        "guard_state_after_inversion": {
            "blocks_correct_citations": len(blocked), "of": len(CORRECT_CITATIONS),
            "catches_stale_citations": len(caught), "of_stale": len(STALE_CITATIONS),
            "meaning": "0 blocked + all stale caught = the guard now defends the Act's reading "
                       "instead of the reversal. Before 2026-10-05 it blocked 3 of 4.",
        },
        "site_status": SITE_STATUS,
        "held_by_decision": HELD_BY_DECISION,
        "guard_blind_to_deployed_row_181": unguarded,
        "sites": EXPECTED_SITES,
        "site_count_by_direction": {
            d: sum(1 for v in EXPECTED_SITES.values() if v["direction"] == d)
            for d in sorted({v["direction"] for v in EXPECTED_SITES.values()})
        },
        "out_of_scope": OUT_OF_SCOPE,
        "renumbering_exposure": {
            "_why": "Cap.212 is the THIRD consolidated Act in this project found to carry the "
                    "renumbering trap, after Cap.332 (presumptive bands) and Cap.438 (the "
                    "s.35->s.43 cross-reference). Section citations against a consolidated "
                    "edition are therefore a KNOWN-RECURRING exposure class, not a one-off.",
            "_measured": "every locked fact citing a Cap.NNN together with a section number",
            "acts_cited_with_section_numbers": 19,
            "top_exposure": {"Cap.332": 21, "Cap.50": 20, "Cap.82": 19, "Cap.148": 18,
                             "Cap.212": 11, "Cap.438": 8},
            "_status": "ENUMERATED, NOT CHECKED. No claim is made that any of these is wrong. "
                       "The claim is that none has been verified against the amending "
                       "instrument's own numbering, and that two of the three Acts checked so "
                       "far were found stale.",
        },
        "decisions_held": {
            "ext_15_verdict": "UNCHANGED -- part-confirmed, part-unresolved",
            "usd_25_vs_tzs_70000": "UNRESOLVED -- Companies (Fees) Regulations not located; "
                                   "the Act delegates all fees (s.458, s.489(3))",
            "300000_vs_500000": "UNRESOLVED -- same gazette, same block",
        },
    }


if __name__ == "__main__":
    out = measure()
    dest = os.path.join(REPO, "eval", "results", "part_xii_reversal_inventory.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print("THE ACT:", ACT["correct_citation"])
    for c in REFUTED_CLAIMS:
        print(f"  {c['verdict']:32s} {c['claim']}")
    print()
    g = out["guard_state_after_inversion"]
    print(f"guard blocks {g['blocks_correct_citations']}/{g['of']} CORRECT citations "
          f"(was 3/4) and catches {g['catches_stale_citations']}/{g['of_stale']} STALE ones; "
          f"blind to deployed row 181: {out['guard_blind_to_deployed_row_181']}")
    print()
    for k, v in EXPECTED_SITES.items():
        print(f"  [{v['direction']:22s}] {k}")
        print(f"        -> {SITE_STATUS.get(k, 'NO STATUS RECORDED')[:108]}")
    print()
    print("by direction:", out["site_count_by_direction"])
    print("renumbering exposure:", out["renumbering_exposure"]["top_exposure"])
    print(f"\nwrote {dest}")
