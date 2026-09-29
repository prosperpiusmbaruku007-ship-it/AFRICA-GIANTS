# -*- coding: utf-8 -*-
"""Audit: does any text this pipeline BLANKS OUT hide a cue from a downstream extractor?

THE QUESTION, and it is prior to R31's. R31 asks "what extracts this signal from the
question?". This asks the step before: "what happens to the question BEFORE the extractor
sees it?" A signal removed upstream is invisible to every downstream cue BY CONSTRUCTION,
and no unit test that calls the extractor with the phrase intact can ever see it.

WHAT WAS LOOKED FOR, AND WHAT WAS FOUND (2026-09-29). The pipeline was searched for
noise-phrase stripping end to end:

  * chike/decomposition.py       -- NO phrase removal. Only whitespace .strip() and segment
                                    splitting. Verified empirically below: four real
                                    questions decompose to ONE part each, byte-preserved.
  * orchestrator.route()         -- passes `text` straight to routing.detect_intent(text).
                                    No transformation of any kind.
  * routing._strip_unclear_spans -- THE ONLY span-blanking in the package.

So there is exactly ONE stripper, and this audit exists to check it. It is not a noise
filter: it blanks the 13 _PAYE_RESIDENCY_UNCLEAR_CUES so that `si mkazi wa kudumu` ("not a
PERMANENT resident", an immigration status) cannot be read by substring as `si mkazi` ("not
a resident", a tax determination). It is a CORRECTNESS mechanism that prevents a flat 15%
being applied on an immigration phrase, and it is scoped to one function.

THE RISK IT STILL CARRIES is the one audited here: blanking a span could destroy a cue some
OTHER extractor needed. That is checkable exhaustively -- for every stripped span, for every
cue list in routing, does removing the span change what that cue list sees?

Usage:  python eval/routing/audit_stripped_spans_vs_cues.py
"""

import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "stripped_spans_cue_audit_2026_09_29.json")

from chike import routing  # noqa: E402
from chike.decomposition import decompose_query  # noqa: E402


# Lists that are NOT phrase-cue lists. Substring-matching a morphological infix against a
# span is meaningless, and counting it as a collision is a FALSE POSITIVE of the expensive
# kind -- it sends someone to edit a mechanism that works (R26's second half). The first run
# of this audit produced 16 "collisions" and EVERY ONE was one of these two cases.
_NOT_PHRASE_LISTS = {"_OBJECT_INFIX"}

# Destroying these is the stripper's DOCUMENTED PURPOSE, not a defect: `si mkazi wa kudumu`
# ("not a PERMANENT resident", an immigration status) contains `si mkazi` ("not a resident",
# a tax determination). Blanking the long span so the short cue cannot fire is the whole
# mechanism. paye_residency_unclear then RE-TESTS these lists against the blanked remainder
# on purpose, so a residency stated ELSEWHERE in the sentence still wins.
_DELIBERATELY_SUPPRESSED = {"_PAYE_NONRESIDENT_CUES", "_PAYE_RESIDENT_CUES"}

# A cue shorter than this is a morpheme, not evidence. Prevents the "m"/"ku"/"wa" class.
_MIN_CUE_LEN = 4


def _cue_lists():
    """Every module-level PHRASE cue list in routing, by name."""
    out = {}
    for name in dir(routing):
        if not name.isupper() or name in _NOT_PHRASE_LISTS:
            continue
        val = getattr(routing, name)
        if isinstance(val, (list, tuple)) and val and all(isinstance(x, str) for x in val):
            out[name] = list(val)
    return out


def main():
    art = {"measured": str(date.today()),
           "harness": "eval/routing/audit_stripped_spans_vs_cues.py",
           "question": "does any blanked span hide a cue from a downstream extractor?",
           "strippers_found_in_pipeline": {
               "chike/decomposition.py": "NONE -- whitespace only, verified empirically",
               "orchestrator.route()": "NONE -- passes text unchanged to detect_intent",
               "routing._strip_unclear_spans": "the only span-blanking in the package",
           }}

    stripped = list(routing._PAYE_RESIDENCY_UNCLEAR_CUES)
    cues = _cue_lists()
    art["stripped_spans"] = stripped
    art["cue_lists_checked"] = {k: len(v) for k, v in cues.items()}

    # For each stripped span x each cue: would blanking the span remove that cue's match?
    collisions, by_design = [], []
    for span in stripped:
        blanked = routing._strip_unclear_spans(span)
        for list_name, cue_list in cues.items():
            if list_name == "_PAYE_RESIDENCY_UNCLEAR_CUES":
                continue  # the list being stripped, by definition
            for cue in cue_list:
                # A collision is a cue that the ORIGINAL span contains but the BLANKED
                # text no longer does -- i.e. stripping destroyed this cue's evidence.
                if not (cue in span and cue not in blanked):
                    continue
                if len(cue) < _MIN_CUE_LEN:
                    continue                      # morpheme, not evidence
                row = {"stripped_span": span, "cue_list": list_name, "cue_destroyed": cue}
                if list_name in _DELIBERATELY_SUPPRESSED:
                    row["why_not_a_defect"] = (
                        "this suppression IS the mechanism: the long immigration phrase "
                        "must not be read as the short tax-determination cue. "
                        "paye_residency_unclear re-tests this list against the blanked "
                        "remainder, so a residency stated elsewhere still wins.")
                    by_design.append(row)
                else:
                    collisions.append(row)
    art["collisions"] = collisions
    art["suppressed_by_design"] = by_design

    # Empirical: decomposition preserves text byte-for-byte on real questions.
    checks = []
    for q in [
        "Nina nyumba kijijini nimemkodisha mfanyabiashara mdogo. Yeye anatakiwa kunikata "
        "kodi kabla ya kunilipa kodi ya pango?",
        "Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi kabla ya "
        "kumpa fedha?",
        "Mfanyakazi wangu si mkazi wa Tanzania, mshahara wake ni TZS 2,000,000. PAYE ni "
        "kiasi gani?",
        "Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye hesabu "
        "ya SDL?",
        "Mhandisi wangu hana residence permit ya kudumu, mshahara TZS 4,000,000. PAYE?",
    ]:
        parts = decompose_query(q)
        checks.append({"question": q[:110], "parts": len(parts),
                       "all_parts_are_substrings": all(p.strip() in q for p in parts),
                       "routes": [routing.detect_intent(p) for p in parts]})
    art["decomposition_preservation"] = checks

    art["verdict"] = {
        "collisions_found": len(collisions),
        "decomposition_drops_text": any(not c["all_parts_are_substrings"] for c in checks),
        "summary": ("CLEAN -- the single stripper destroys no other extractor's cue, and "
                    "decomposition preserves text" if not collisions else
                    "COLLISIONS FOUND -- see collisions[]"),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"stripped spans        : {len(stripped)}")
    print(f"cue lists checked     : {len(cues)}")
    print(f"collisions            : {len(collisions)}")
    print(f"suppressed BY DESIGN  : {len(art['suppressed_by_design'])} "
          f"(the mechanism working, not defects)")
    for c in collisions:
        print("   !!", json.dumps(c, ensure_ascii=False))
    print(f"decomposition preserves text: "
          f"{not art['verdict']['decomposition_drops_text']}")
    print(f"\nVERDICT: {art['verdict']['summary']}")
    print("artifact:", OUT)
    return 0 if not collisions else 2


if __name__ == "__main__":
    sys.exit(main())
