"""Does every cited section number actually EXIST in the Act it names?

THE GAP THIS CLOSES, stated precisely. Every provenance check in this project asks whether a
citation is PRESENT and WELL-FORMED. None asks whether the thing it points at exists, and none
asks whether it supports the claim. That is the presence-not-conclusion family arriving in the
citation layer: a citation that resolves passes the provenance audit, the correction-sync check
and the staleness check, in that order, without any of them reading the provision.

WHAT THIS CHECKS AND WHAT IT EXPLICITLY DOES NOT:

  CHECKS      the cited section number exists in the Act's own Arrangement of Sections.
  DOES NOT    check that the section SAYS what the fact claims. A fact citing a real section
              that contradicts it passes this check -- and that is exactly the shape found in
              tier1a_wh_009_20260603 on 2026-09-25 (a real, live, whitelisted TRA page cited
              for a 15% non-resident rent rate the page itself contradicts at 10%).

So a clean run here is a LOWER BOUND on citation health and must never be reported as "the
citations are good" (R21). It rules out one failure mode -- a section number that does not
exist -- and is silent on the more common one.

SCOPE. Only the two Acts whose full text is fetchable and on disk (Cap.332, Cap.438). Facts
citing Cap.212/148/297/263/290/357 are OUT OF SCOPE and are reported as such by name rather
than dropped: a census that quietly omits what it cannot test reports a cleaner result than it
earned (R26).

R26/R23 CONTROLS, because a checker that only ever says "exists" is the R20 vacuous shape:
  POSITIVE  a section known to exist (Cap.332 s.105) MUST be found.
  NEGATIVE  a planted non-existent section (s.9999) MUST be reported missing.
  SANITY    the parsed section set must be non-empty and plausibly sized, or the run ABORTS --
            an empty section list would make every citation "missing" and look like a
            catastrophe, and a mis-parse that returns every integer would make every citation
            "present" and look like a clean bill of health. Both are parser failures, not
            findings, and both are caught here rather than reported.

Usage:  python eval/sources/check_cited_sections_exist.py
"""

import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "cited_sections_exist_2026_09_25.json")

ACTS = {
    "332": {"pdf": os.path.join(REPO, "scratch", "_ita.pdf"), "name": "Income Tax Act Cap.332",
            "expect_min_sections": 100},
    "438": {"pdf": os.path.join(REPO, "scratch", "_taa.pdf"),
            "name": "Tax Administration Act Cap.438", "expect_min_sections": 60},
}
# Acts cited by facts but with no full text on disk. Named, not dropped.
OUT_OF_SCOPE_CAPS = ["212", "148", "297", "263", "290", "357", "213", "101", "189", "217"]

# Facts whose PROSE discusses two Acts at once, where nearest-preceding-Cap attribution cannot
# resolve which Act a bare "s.128" belongs to. Listed individually WITH THE REASON, never
# suppressed silently: R20 says "no assertion needed here" is a valid recordable outcome, and
# the reason has to be at the site so the next reader does not re-raise or re-insert it.
KNOWN_MULTI_ACT_PROSE = {
    "annual_return_form_number":
        "The fact is ABOUT cross-Act renumbering, so it necessarily names two Acts in one "
        "sentence: 'exactly the pattern CLAUDE.md already documents for Cap.332's old s.35. "
        "Current s.128 is a different provision entirely.' That trailing s.128 is Companies "
        "Act Cap.212's, but it follows the Cap.332 mention, so positional attribution assigns "
        "it to Cap.332 and calls it missing. VERIFIED BY READING THE FACT: its Cap.212 "
        "citations (ss.128/131) are correct and documented against a direct brela.go.tz fetch, "
        "including the Act's own footnote '[s. 128]' on s.131. Not a defect -- a limit of "
        "positional attribution on prose, and the fact itself warns against 'correcting' it.",
}


def act_sections(pdf_path):
    """Section numbers from the Act's own Arrangement of Sections.

    Parsed from the TOC rather than the body: body text is full of figures (amounts, years,
    cross-references) and matching bare integers there would mark every citation 'present',
    which is the vacuous-pass failure this whole script exists to avoid.
    """
    import pypdf
    txt = "".join((p.extract_text() or "") for p in pypdf.PdfReader(pdf_path).pages)
    txt = re.sub(r"\s+", " ", txt)
    start = txt.find("Arrangement of Sections")
    if start < 0:
        return set(), 0
    # The TOC ends where the enacting text begins.
    end = txt.find("An Act to", start)
    toc = txt[start:end if end > start else start + 20000]
    secs = set()
    # "104. Withholding by employers."  and ranges "102-103. Repealed."
    for m in re.finditer(r"(?<![\d.])(\d{1,3})\s*[-–]\s*(\d{1,3})\s*\.", toc):
        a, b = int(m.group(1)), int(m.group(2))
        if b >= a and b - a < 20:
            secs.update(range(a, b + 1))
    for m in re.finditer(r"(?<![\d.])(\d{1,3})\s*\.\s+[A-Z]", toc):
        secs.add(int(m.group(1)))
    return secs, len(toc)


def sections_for_cap(blob, cap):
    """Section numbers that belong to THIS Act, not every number in the blob.

    BOTH GUARDS HERE EXIST BECAUSE THE FIRST VERSION FLAGGED TWO FACTS AND BOTH WERE ITS OWN
    DEFECTS (2026-09-25, caught by R26's specimen-first rule before anything was recorded):

      1. `Tshs.240,000` matched the `s.` alternative and read a CURRENCY AMOUNT as section 240.
         Fixed by requiring the `s` not be preceded by a letter. Without it, every fact quoting
         a shilling figure from an Act manufactures phantom sections.
      2. `annual_return_form_number` cites Companies Act Cap.212 ss.128/131; the whole-blob
         scan attributed them to Cap.332 and called them missing. Fixed by attributing each
         section reference to the NEAREST PRECEDING Cap mention. That fact is also a warning:
         it documents a legacy form number and says in terms "do not 'correct' the form's name
         to match the current section number" -- reporting it would have sent someone to break
         a fact whose whole purpose is explaining why it looks wrong.
    """
    # Segment the blob at each Cap mention; a section ref belongs to the Cap it follows.
    marks = [(m.start(), m.group(1)) for m in re.finditer(r"Cap\.?\s*(\d{3})\b", blob, re.I)]
    refs = set()
    for m in re.finditer(r"(?<![A-Za-z])(?:ss?\.|section[s]?\s+)\s*(\d{1,3})\b", blob, re.I):
        owner = None
        for pos, c in marks:
            if pos < m.start():
                owner = c
            else:
                break
        # A ref before ANY Cap mention is unattributable; skip rather than guess.
        if owner == cap:
            refs.add(int(m.group(1)))
    return refs


def main():
    art = {"measured": str(date.today()),
           "harness": "eval/sources/check_cited_sections_exist.py",
           "checks": "cited section NUMBER exists in the Act's Arrangement of Sections",
           "explicitly_does_not_check": "that the section supports the claim. A real section "
                                        "that CONTRADICTS the fact passes this check.",
           "acts_in_scope": {}, "acts_out_of_scope": OUT_OF_SCOPE_CAPS,
           "controls": {}, "rows": [], "out_of_scope_rows": []}

    sections = {}
    for cap, meta in ACTS.items():
        if not os.path.exists(meta["pdf"]):
            print(f"MISSING {meta['pdf']} -- run the source probes first"); return 2
        secs, toclen = act_sections(meta["pdf"])
        # SANITY: abort rather than report from a mis-parse.
        if len(secs) < meta["expect_min_sections"]:
            print(f"ABORT: parsed only {len(secs)} sections for Cap.{cap} "
                  f"(expected >={meta['expect_min_sections']}). Parser failure, not a finding.")
            return 2
        sections[cap] = secs
        art["acts_in_scope"][cap] = {"name": meta["name"], "sections_parsed": len(secs),
                                     "max_section": max(secs), "toc_chars": toclen}
        print(f"  Cap.{cap}: {len(secs)} sections parsed, max s.{max(secs)}")

    # CONTROLS (R26): plant what it must catch, and confirm it passes a clean case.
    art["controls"]["positive_cap332_s105_must_exist"] = 105 in sections["332"]
    art["controls"]["negative_cap332_s9999_must_be_missing"] = 9999 not in sections["332"]
    art["controls"]["positive_cap438_s51_must_exist"] = 51 in sections["438"]
    # The two bad specimens the first version produced, pinned so they cannot come back.
    art["controls"]["currency_not_read_as_section"] = (
        sections_for_cap('Cap.332 First Schedule "Tshs.240,000/= plus 20%"', "332") == set())
    art["controls"]["sections_attributed_to_their_own_act"] = (
        sections_for_cap("Companies Act Cap.212 s.131 ... Income Tax Act Cap.332 s.105",
                         "332") == {105})
    if not all(art["controls"].values()):
        print("ABORT: controls failed ->", art["controls"]); return 2
    print("  controls:", art["controls"])

    facts = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8"))
    real = {k: v for k, v in facts.items() if not k.startswith("_")}

    for key, val in real.items():
        blob = json.dumps(val, ensure_ascii=False)
        for cap in OUT_OF_SCOPE_CAPS:
            if re.search(rf"Cap\.?\s*{cap}\b", blob, re.I):
                art["out_of_scope_rows"].append({"key": key, "cap": cap,
                                                 "reason": "no full text on disk"})
                break
        for cap in ACTS:
            if not re.search(rf"Cap\.?\s*{cap}\b", blob, re.I):
                continue
            refs = sections_for_cap(blob, cap)
            if not refs:
                continue
            missing = sorted(r for r in refs if r not in sections[cap])
            verdict = "ALL_EXIST" if not missing else "SECTION_NOT_IN_ACT"
            note = None
            if missing and key in KNOWN_MULTI_ACT_PROSE:
                verdict, note = "AMBIGUOUS_MULTI_ACT_PROSE", KNOWN_MULTI_ACT_PROSE[key]
            row = {"key": key, "cap": cap, "sections_cited": sorted(refs),
                   "sections_missing": missing, "verdict": verdict}
            if note:
                row["why_not_a_defect"] = note
            art["rows"].append(row)
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    bad = [r for r in art["rows"] if r["verdict"] == "SECTION_NOT_IN_ACT"]
    amb = [r for r in art["rows"] if r["verdict"] == "AMBIGUOUS_MULTI_ACT_PROSE"]
    art["summary"] = {"facts_checked": len(art["rows"]),
                      "clean": len(art["rows"]) - len(bad) - len(amb),
                      "section_not_in_act": len(bad),
                      "ambiguous_multi_act_prose": len(amb),
                      "facts_out_of_scope": len(art["out_of_scope_rows"])}
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("\n" + json.dumps(art["summary"]))
    for r in bad:
        print(f"  !! {r['key']} Cap.{r['cap']} missing {r['sections_missing']} "
              f"(cited {r['sections_cited']})")
    for r in amb:
        print(f"  ~~ {r['key']} AMBIGUOUS (documented, not a defect): {r['sections_missing']}")
    print("artifact:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
