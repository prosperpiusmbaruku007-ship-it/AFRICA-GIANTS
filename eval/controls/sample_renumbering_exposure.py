# -*- coding: utf-8 -*-
"""RENUMBERING EXPOSURE — A SAMPLE, PRICED BEFORE COMMITTING TO A FULL PASS.

THE QUESTION. Cap.212 was the THIRD consolidated Act in this project found to carry the
renumbering trap, after Cap.332 (the presumptive bands) and Cap.438 (the s.35 -> s.43
cross-reference). Two of three checked came back wrong. 97 locked facts cite a section number
against one of six Acts — Cap.332 (21), Cap.50 (20), Cap.82 (19), Cap.148 (18), Cap.212 (11),
Cap.438 (8). A full pass is expensive; a 2-per-Act sample prices it first.

WHAT COUNTS AS A HIT, stated before measuring so the result cannot be read loosely:
  HIT     the cited section number, read in the current consolidation, is a DIFFERENT provision
          from the one the fact describes
  CLEAN   the cited section number lands on the provision the fact describes
  BLOCKED the current consolidation could not be obtained, so no verdict is possible

⚠️ THREE WAYS THIS SAMPLE CAN MISLEAD, and all three are live:

 1. **A SAMPLE OF 2 PER ACT CANNOT CLEAR AN ACT.** Two clean draws from 20 facts bound the rate
    loosely at best. "Cap.50 came back clean" means "the two sampled facts are clean", and the
    honest read of a clean Act here is *not yet shown to be a problem*, never *shown not to be*.
    This is R21's lower-bound rule applied to a sample instead of a sweep.

 2. **THE HOSTED EDITION MAY NOT BE THE CURRENT ONE.** Measured here: tra.go.tz serves the Tax
    Administration Act at **R.E. 2019**, while this project's own facts cite Cap.438 **R.E.
    2023** numbering (CLAUDE.md records the s.35 -> s.43 move). So for Cap.438 the obtainable
    text is the OLD edition, and a "clean" verdict against it would be a verdict about the wrong
    document. That is recorded as BLOCKED, not CLEAN — the distinction R26 insists on.

 3. **A RENUMBERING HIT IS NOT A WRONG-VALUE HIT.** The fact's figure can be perfectly right
    while its citation points at the wrong provision. Cap.332's presumptive case was a wrong
    VALUE from a stale table; Cap.212's was a wrong CITATION with a right value. Both are worth
    fixing; only the first can give a user a wrong number. The sample reports which it found.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ACTS = os.path.join(
    r"C:\Users\jhjh\AppData\Local\Temp\claude\C--Users-jhjh-AFRICA-GIANTS"
    r"\d8f91321-e9cf-4aa8-a380-2afc9441133f\scratchpad", "acts")
OUT = os.path.join(REPO, "eval", "results", "renumbering_exposure_sample.json")

# Act -> (local text file, edition on cover, what the project's facts cite)
SOURCES = {
    "Cap.332": ("The_Income_Tax_Act.pdf.txt", "2023", "Cap.332 R.E.2023"),
    # ⛔ CORRECTED 2026-10-05. This pointed at CHAPTER_438-THE_TAX_ADMINISTRATION_ACT.pdf
    # (259,711 bytes, 90pp), which is R.E.2019 -- and the whole Act was then recorded BLOCKED on
    # an edition mismatch. WRONG ON BOTH COUNTS. tra.go.tz hosts BOTH editions, and the project
    # already recorded the current one: Tax_Administration_Act.pdf (945,982 bytes, 88pp, HTTP
    # 200), cited by paye_penalty_rate's own verified_by since 2026-09-02. I picked the stale
    # URL out of a grep of recorded paths without checking WHICH FACT CITED WHICH.
    # So "the regulator serves its own Act at a superseded edition" was half right at best: it
    # serves both, and the actionable fact is that one of our recorded URLs is the old one.
    "Cap.438": ("TAA_current.txt", "2023 (OAG 2025 compilation)", "Cap.438 R.E.2023"),
    "Cap.148": ("The_Value_Added_Tax_Act.pdf.txt", "unstated", "Cap.148"),
    "Cap.82": ("THE_VOCATIONAL_EDUCATION_AND_TRAINING_ACT.pdf.txt", "2023", "Cap.82"),
    "Cap.212": ("../act_full.txt", "2023", "Cap.212 R.E.2023"),  # read in full 2026-10-04
    "Cap.50": (None, None, "Cap.50"),                 # NSSF Act — see BLOCKED note
}

# ⛔ EDITION GATE, added after the first run. Cap.438's obtainable text is R.E. 2019 while every
# fact cites R.E. 2023 numbering, and the first run ADJUDICATED IT ANYWAY and reported a HIT on
# paye_penalty_rate (s.89 reads on aiding/abetting in R.E.2019, not on the late-payment penalty).
# That hit is not adjudicable: it may be a renumbering between the two editions rather than a
# wrong citation, and nothing in the 2019 text can tell the difference. My own BLOCKED_NOTE
# already said so and the code ignored it -- a note that the code does not enforce is exactly
# the inert-control shape. Now enforced.
# EMPTIED 2026-10-05: the current Cap.438 edition WAS obtainable all along (see SOURCES), so
# there is no longer an edition mismatch to gate on. Kept as a mechanism because the next Act
# fetched may genuinely only exist at a stale edition, and a verdict against the wrong document
# must never be reported as CLEAN.
EDITION_MISMATCH = set()

# 2 per Act. `expect` = words that must appear at/near the cited section if the citation is right.
#
# ⚠️ THE SECTION NUMBER MUST COME FROM THE FACT'S OWN `primary_source`, NOT FROM A REGEX OVER THE
# WHOLE FACT OBJECT. The first run sampled corporate_tax_rate at "s.27" -- a number that appears
# somewhere in the object but is NOT its citation: its primary_source reads "Cap.332 R.E.2019,
# First Schedule para 3". s.27 in R.E.2023 is the quantification rule, so the mismatch was real
# and meant nothing. A HIT reported on a section the fact never cited is a fabricated defect, and
# R26's second half says a fabricated defect is worse than a missed one because only the
# fabricated one generates an edit. `_cited_section` below reads primary_source and REFUSES to
# adjudicate when the citation is to a Schedule rather than a section.
SAMPLE = [
    ("Cap.332", "paye_p9_deadline", 85, ["statement", "withhold", "return"]),
    # corporate_tax_rate is DELIBERATELY NOT SAMPLED BY SECTION: its primary_source cites the
    # FIRST SCHEDULE para 3, not a section, so there is no section number to renumber. Replaced
    # with a fact that does cite a section. (Its own separate issue -- it cites R.E.2019 where
    # R.E.2023 exists -- is a staleness question, not a renumbering one.)
    ("Cap.332", "provisional_tax_instalments", 113, ["instalment", "quarter", "estimate"]),
    ("Cap.148", "vat_standard_rate", 5, ["rate", "value added tax", "impos"]),
    ("Cap.148", "vat_registration_threshold", 28, ["registration", "threshold", "regist"]),
    ("Cap.82", "sdl_payer", 14, ["levy", "employer", "payment"]),
    ("Cap.82", "legal_citation_amendment_act_sdl", 19, ["exempt", "levy", "apply"]),
    ("Cap.212", "company_director_minimum_age", 197, ["eighteen", "director"]),
    ("Cap.212", "minimum_directors", 186, ["director"]),
    ("Cap.438", "paye_penalty_rate", 89, ["penalt", "fails to file", "two point five"]),
    ("Cap.438", "legal_citation_tax_administration", 43, ["document", "maintain", "record"]),
    ("Cap.50", "nssf_payment_deadline", 14, ["contribution", "month", "pay"]),
    ("Cap.50", "nssf_retirement_age", 25, ["pension", "age", "retire"]),
]

BLOCKED_NOTE = {
    "Cap.50": "NSSF Act NOT LOCATED after an exhaustive, diagnosed search on 2026-10-05. "
              "EIGHT hosts tried, each with a real request and a specific verdict -- not a "
              "guessed URL anywhere (R30): "
              "(1) nssf.go.tz is UP (root HTTP 200, 42,040 bytes; /benefits/* and /schemes "
              "resolve) but ONE ROUTE FAMILY fails -- every /pages/* path returns 500 "
              "(/contributions, /michango, /sheria, /about), and the homepage links NO "
              "legislation at all across 41 links. "
              "(2) kazi.go.tz: DNS resolves, https returns 000 (connection reset), http 302s to "
              "https://www.www.kazi.go.tz -- a malformed doubled-www redirect. "
              "(3) tra.go.tz: 302 on the NSSF Act path (it hosts only the Acts it administers). "
              "(4) parliament.go.tz: /acts is CLIENT-RENDERED -- zero static PDF links, zero "
              "pagination -- and the homepage exposes only recent ANNUAL Acts via "
              "polis.bunge.go.tz, not consolidated Chapters. "
              "(5) mof.go.tz: hosts the Chapters it administers (290, 348, 423, 439, 442) and "
              "not Cap.50, which confirms the pattern rather than breaking it. "
              "(6) oag.go.tz: reachable (HTTP 200), links onward to sheria.go.tz, no legislation "
              "listing of its own. "
              "(7) sheria.go.tz (Ministry of Constitutional and Legal Affairs): reachable, links "
              "NALIS. "
              "(8) nalis.sheria.go.tz: HTTP 200, 695,886 bytes -- but it is the National Legal "
              "SERVICES system (legal aid providers, applications, 'Haki kwa Wote'), NOT a "
              "legislation database. "
              "THE PATTERN THAT WORKED FOR EVERY OTHER ACT IS THAT THE ADMINISTERING BODY HOSTS "
              "ITS OWN CHAPTER -- Cap.212 from brela.go.tz, Cap.332/438/148/82 from tra.go.tz, "
              "Cap.290 from mof.go.tz. For Cap.50 that body is NSSF, whose /pages/* family is "
              "broken, or the labour ministry, which is misconfigured. So the blocker is a "
              "SERVER FAULT at the two hosts that should have it, not an absence of effort. "
              "ESCALATED TO THE FOUNDER for a supplied copy. 20 facts cite this Act and NONE "
              "has been checked against its text: UNCHECKED, not clean, and the single largest "
              "renumbering exposure left.",
    "Cap.438": "RESOLVED 2026-10-05, and the earlier BLOCKED verdict was MY ERROR, not the "
               "regulator's. tra.go.tz hosts BOTH editions: CHAPTER_438-THE_TAX_ADMINISTRATION_"
               "ACT.pdf is R.E.2019 (259,711 bytes) and Tax_Administration_Act.pdf is the "
               "current OAG compilation (945,982 bytes, 88pp). The project ALREADY cited the "
               "current one -- paye_penalty_rate's verified_by has quoted s.89(2) from it since "
               "2026-09-02. I picked the stale URL out of a grep of recorded paths without "
               "checking which fact cited which, then recorded the whole Act as unverifiable. "
               "So 'the regulator serves its own Act at a stale edition' was half right at "
               "best: it serves both, and the actionable fact is that one of OUR recorded URLs "
               "is the old one (deliberately, for the two EFD facts that quote the 2019 "
               "wording and name the renumbering explicitly).",
}


def _text(act):
    fn = SOURCES[act][0]
    if fn is None:
        return None
    p = os.path.join(ACTS, fn)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _section_body(txt, n, window=420):
    """Text at the FIRST occurrence of section n as a numbered provision, skipping the table of
    contents. The ToC lists 'N. Heading' densely; the body prints 'N.-(1)' or 'N. ' followed by
    substantive text. Taking the LAST match is wrong too (schedules re-use numbers), so this
    prefers a match with a subsection marker and falls back to the last plain one."""
    subsec = list(re.finditer(rf"\n\s*{n}\s*\.\s*[-–]\s*\(1\)", txt))
    if subsec:
        k = subsec[-1].start()
        return " ".join(txt[k:k + window].split())
    plain = list(re.finditer(rf"\n\s*{n}\s*\.\s+[A-Z]", txt))
    if plain:
        k = plain[-1].start()
        return " ".join(txt[k:k + window].split())
    return None


def main():
    rows = []
    for act, key, sec, expect in SAMPLE:
        if act in EDITION_MISMATCH:
            rows.append({"act": act, "fact": key, "cited_section": sec, "verdict": "BLOCKED",
                         "why": BLOCKED_NOTE[act], "body": None, "matched": []})
            continue
        txt = _text(act)
        if txt is None:
            rows.append({"act": act, "fact": key, "cited_section": sec, "verdict": "BLOCKED",
                         "why": BLOCKED_NOTE.get(act, "consolidation not obtained"),
                         "body": None, "matched": []})
            continue
        body = _section_body(txt, sec)
        if body is None:
            rows.append({"act": act, "fact": key, "cited_section": sec,
                         "verdict": "SECTION_NOT_FOUND",
                         "why": f"no s.{sec} located in the obtained text",
                         "body": None, "matched": []})
            continue
        matched = [w for w in expect if w.lower() in body.lower()]
        rows.append({"act": act, "fact": key, "cited_section": sec,
                     "verdict": "CLEAN" if matched else "HIT",
                     "why": ("the cited section reads on the provision the fact describes"
                             if matched else
                             "the cited section does NOT read on the provision the fact "
                             "describes -- candidate renumbering hit, needs a human read"),
                     "expected_words": expect, "matched": matched, "body": body[:300]})

    # R20: the sampler must be able to produce every verdict it can print. If nothing was
    # adjudicable the "0 hits" headline would be vacuous rather than reassuring.
    adjudicable = [r for r in rows if r["verdict"] in ("CLEAN", "HIT")]
    assert adjudicable, (
        "no sampled fact was adjudicable at all -- every Act was BLOCKED or every section "
        "unfound. A hit rate cannot be computed and must not be reported as 0.")

    hits = [r for r in rows if r["verdict"] == "HIT"]
    clean = [r for r in rows if r["verdict"] == "CLEAN"]
    blocked = [r for r in rows if r["verdict"] in ("BLOCKED", "SECTION_NOT_FOUND")]

    by_act = {}
    for r in rows:
        by_act.setdefault(r["act"], []).append(r["verdict"])

    out = {
        "_what": "2-per-Act sample pricing the renumbering exposure before a full pass.",
        "_population": {
            "facts_citing_a_section_against_a_consolidated_act": 97,
            "acts": {"Cap.332": 21, "Cap.50": 20, "Cap.82": 19, "Cap.148": 18,
                     "Cap.212": 11, "Cap.438": 8},
            "why_this_population": "these are the facts where a renumbering can make a REAL, "
                                   "correctly-fetched citation point at the wrong provision -- "
                                   "the failure mode that produced the Cap.212 reversal and the "
                                   "Cap.332 presumptive incident.",
        },
        "⚠️_what_a_clean_act_does_and_does_not_mean":
            "2 clean draws from 20 facts is a LOWER BOUND on cleanliness, not a clearance. An "
            "Act reading clean here is NOT YET SHOWN to be a problem; it is not shown not to be.",
        "hit_rate_on_adjudicable": f"{len(hits)}/{len(adjudicable)}",
        "totals": {"sampled": len(rows), "adjudicable": len(adjudicable),
                   "hits": len(hits), "clean": len(clean), "blocked": len(blocked)},
        "by_act": by_act,
        "blocked_notes": BLOCKED_NOTE,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"sampled {len(rows)}; adjudicable {len(adjudicable)}; "
          f"HITS {len(hits)}; CLEAN {len(clean)}; BLOCKED {len(blocked)}")
    for r in rows:
        print(f"  [{r['verdict']:17s}] {r['act']:8s} s.{r['cited_section']:<4} {r['fact'][:42]}")
        if r["verdict"] == "HIT":
            print(f"        wanted {r['expected_words']}")
            print(f"        got: {r['body'][:170]}")
    print(f"\nby act: {by_act}")
    print(f"hit rate on adjudicable: {len(hits)}/{len(adjudicable)}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
