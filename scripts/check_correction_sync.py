#!/usr/bin/env python3
"""
CORRECTION <-> RAG INDEX SYNC CHECK.
Usage: python scripts/check_correction_sync.py
Exit code: 0 = no corrected fact is provably serving stale content, 1 = at least one is

WHY THIS EXISTS (2026-09-04). `efd_not_every_business` was corrected in locked_facts.json
on 2026-08-29 -- the fabricated "TZS 11,000,000 turnover threshold" framing was found and
explicitly rejected, with `wrong_patterns` written specifically to reject it. Its RAG-
embedded rendering (CONCISE_BILINGUAL_FACTS in precompute_rag_embeddings.py) was NEVER
updated to match, and kept serving the debunked framing verbatim from its original
authoring (2026-07-28) straight through to 2026-09-03/04 -- five weeks, undetected,
because check_facts_index_sync.py only verifies a fact is REACHABLE (a row exists), never
that the row's CONTENT still reflects the fact's CURRENT correct_value. The one place a
content check already existed -- _grouped_verdict, for FACT_GROUPS members -- does not
cover ordinary CONCISE_BILINGUAL_FACTS or default key:value-rendered entries, which is
most of the corpus.

This script closes that gap for the class of fact most likely to carry it: any fact with
a `correction_note` -- i.e., one that has ALREADY been found wrong once. A fact corrected
once is not protected against silently reverting to its old, wrong rendering; nothing
about "already corrected" makes the propagation step reliable. 51 of 250 locked facts
carry a correction_note as of this writing.

METHOD, TWO SIGNALS, DELIBERATELY NOT EQUAL WEIGHT:

  1. STRONG (blocks the gate): does the fact's OWN `wrong_patterns` match the text of its
     resolved row(s) in the deployed index, WITH NO NEGATION CUE NEARBY? These regexes
     are author-curated, specific to the exact wrong claim each fact was corrected away
     from -- a match here means the deployed text still asserts something its own owner
     already said was wrong. This is the same class of evidence check_facts_index_sync.py's
     `_grouped_verdict` uses for FACT_GROUPS members, generalised to every corrected fact.

     ⛔ THE NEGATION FILTER IS NOT OPTIONAL -- FIRST RUN WITHOUT IT FLAGGED 8, AND 7 WERE
     FALSE POSITIVES. `wrong_patterns` were authored to catch a WRONG CLAIM APPEARING IN
     GENERATED TEXT (a model reply or training pair asserting it). Many of THIS corpus's
     correct facts are deliberately written as "X is WRONG, Y is correct" -- fighting a
     specific known hallucination by naming it -- so the wrong claim's own words appear
     INSIDE the correct row, immediately followed or preceded by "NOT", "WRONG", "hakuna",
     "si", etc. A bare regex match cannot distinguish "the wrong figure is asserted" from
     "the wrong figure is named in order to reject it", and on first run it did not try to.
     Checked by hand against all 8 first-run flags (not just assumed): a window of 40
     chars before the match to 60 chars after, searched for a negation cue
     (not/wrong/no/never/hakuna/si/siyo/sio/haiwezekani/hairuhusiwi/haipaswi, word-
     boundaried), correctly separated the ONE genuine defect (`efd_not_every_business`,
     no negation cue anywhere near its match) from all seven correct rejections
     (`paye_personal_relief`, `p45_not_tanzanian`, `stamp_duty_property_transfer`,
     `paye_nonresident_flat_rate`, `wcf_disease_reporting_deadline`,
     `permit_class_d_does_not_exist`, `vat_threshold_200m_july2024_increase`) --
     eval/results/correction_sync_negation_check_2026_09_04.json has the full per-row
     evidence. Matches WITH a nearby negation cue are reported in `negated_mention`
     (visible, not silently dropped) rather than either bucket that affects exit code.

     A negation match is still a HEURISTIC, not proof: it is possible for a match to have
     an unrelated negation word nearby by coincidence and be genuinely stale regardless.
     `negated_mention` entries are visible in the report for exactly this reason -- read
     them, don't just trust the bucket.

     KNOWN LIMITATION, not hidden: `efd_not_every_business`'s own wrong_patterns regex
     ("chini ya (tzs )?(11|14),?000,?000[^.?!]{0,40}(efd|risiti za mkono)") did NOT match
     its own stale, pre-fix text -- the 40-char window was too narrow for the actual
     sentence structure. Widened here (see the regression test) as part of building this
     checker, but the general lesson stands: a wrong_patterns MISS is not proof the
     content is fine, only that this particular regex didn't catch it. Treat a CLEAN
     result as "no known-wrong phrase detected", not "verified correct".

  2. WEAK (reported, does NOT block the gate): does the fact's own asserted FIGURE
     (`_figure_of`, the first number found in `correct_value` or `fact`) appear anywhere
     in its resolved row(s)? This is noisy by construction -- `_figure_of` takes the FIRST
     number in the text, which for a fact like `efd_not_every_business` whose correction
     is qualitative ("no TZS figure excuses a business") picks up a stray section number
     ("44" from "s.44(2)") instead of a real regulatory figure. A miss here is a prompt to
     look, not a proven defect -- per R20, a check that fails on noise is worse than one
     that reports nothing, so this signal is advisory only and does not set exit code 1.

A fact this script cannot resolve to any row at all (absent/fragment/pending_r15/genuine
drift) is skipped, not flagged -- check_facts_index_sync.py already owns reachability; this
script only asks, of facts that ARE reachable, whether what's actually being served still
matches what the fact says is correct.

R18: committed before its result is written up.
Artifact: eval/results/correction_sync_audit.json
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_HERE = os.path.dirname(__file__)
_REPO = os.path.normpath(os.path.join(_HERE, ".."))

FACTS_PATH = os.path.join(_REPO, "scripts", "locked_facts.json")
INDEX_PATH = os.path.join(_REPO, "kaggle", "rag_facts_text.json")

sys.path.insert(0, _HERE)
from check_facts_index_sync import (  # noqa: E402
    PINNED,
    _is_sibling,
    _key_slug,
    _match_needle,
)
from precompute_rag_embeddings import (  # noqa: E402
    FACT_GROUPS as _FACT_GROUPS,
    _GROUP_MEMBERS,
    _figure_of,
    fact_value as _fact_value,
)


_NEGATION_CUE = re.compile(
    r'\b(not|wrong|no|never|hakuna|si|siyo|sio|haiwezekani|hairuhusiwi|haipaswi)\b',
    re.IGNORECASE,
)
_NEG_BEFORE, _NEG_AFTER = 40, 60


def _has_nearby_negation(text, match):
    window = text[max(0, match.start() - _NEG_BEFORE): match.end() + _NEG_AFTER]
    return bool(_NEGATION_CUE.search(window))


def resolve_row_texts(key, index, index_slugs):
    """Same resolution order as check_facts_index_sync.py's check(), but returns the
    ACTUAL DEPLOYED TEXT of whatever row(s) the key resolves to, not just a verdict --
    that text is what this script's content checks run against."""
    slug = _key_slug(key)

    exact = [index[i] for i, s in enumerate(index_slugs) if s == slug]
    if exact:
        return exact

    sibling = [index[i] for i, s in enumerate(index_slugs) if _is_sibling(slug, s)]
    if sibling:
        return sibling

    if key in _GROUP_MEMBERS:
        spec = _FACT_GROUPS[_GROUP_MEMBERS[key]]
        stem = spec["text"][:40]
        rows = [r for r in index if r.startswith(stem)]
        if rows:
            return rows
        return []

    pin = PINNED.get(key)
    if pin and pin[0] == "present_elsewhere":
        needle = pin[1]
        status, matches = _match_needle(needle, index)
        if status == "unique":
            return [index[matches[0]]]

    return []


def check(facts_path=FACTS_PATH, index_path=INDEX_PATH):
    with open(facts_path, encoding="utf-8") as f:
        locked = json.load(f)
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)
    index_slugs = [f.split(":")[0].strip().lower() for f in index]

    report = {
        "stale_wrong_pattern": [],
        "negated_mention": [],
        "figure_not_found": [],
        "clean": [],
        "unresolved": [],
        "no_check_possible": [],
    }

    for key, v in locked.items():
        if key.startswith("_") or not isinstance(v, dict):
            continue
        if "correction_note" not in v:
            continue

        rows = resolve_row_texts(key, index, index_slugs)
        if not rows:
            report["unresolved"].append(key)
            continue
        combined = " || ".join(rows)

        wrong_patterns = v.get("wrong_patterns") or []
        stale, negated = [], []
        for wp in wrong_patterns:
            m = re.search(wp, combined, re.IGNORECASE)
            if not m:
                continue
            (negated if _has_nearby_negation(combined, m) else stale).append(wp)
        if stale:
            report["stale_wrong_pattern"].append({
                "key": key, "matched_patterns": stale, "rows": rows,
            })
            continue
        if negated:
            report["negated_mention"].append({
                "key": key, "matched_patterns": negated, "rows": rows,
            })
            continue

        fig = _figure_of(_fact_value(v))
        if not wrong_patterns and not fig:
            report["no_check_possible"].append(key)
            continue
        if fig and fig not in combined:
            report["figure_not_found"].append({
                "key": key, "expected_figure": fig, "rows": rows,
            })
            continue

        report["clean"].append(key)

    ok = not report["stale_wrong_pattern"]
    return ok, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=FACTS_PATH)
    ap.add_argument("--index", default=INDEX_PATH)
    ap.add_argument("--out", default=os.path.join(_REPO, "eval", "results",
                                                    "correction_sync_audit.json"))
    args = ap.parse_args()

    ok, report = check(args.facts, args.index)
    total = sum(len(v) for v in report.values())

    print(f"corrected facts checked: {total}")
    print(f"  clean                    {len(report['clean'])}")
    print(f"  no check possible        {len(report['no_check_possible'])}")
    print(f"  unresolved (not reachable, owned by check_facts_index_sync.py) "
          f"{len(report['unresolved'])}")
    print(f"  negated mention (wrong claim named only to reject it -- not a defect) "
          f"{len(report['negated_mention'])}")
    print(f"  WEAK: figure not found   {len(report['figure_not_found'])}")
    print(f"  STRONG: stale wrong_pattern MATCH {len(report['stale_wrong_pattern'])}")
    print()

    if report["negated_mention"]:
        print(f"INFO -- {len(report['negated_mention'])} fact(s) mention their own "
              f"wrong_patterns text, but with a negation cue nearby -- read to confirm, "
              f"not treated as a defect:")
        for r in report["negated_mention"]:
            print(f"    {r['key']}: {r['matched_patterns']}")
        print()

    if report["figure_not_found"]:
        print("ADVISORY -- expected figure not found in the resolved row(s) (noisy "
              "signal, verify by hand, does not fail the gate):")
        for r in report["figure_not_found"]:
            print(f"    {r['key']}: expected {r['expected_figure']!r}, "
                  f"row(s): {[t[:80] for t in r['rows']]}")
        print()

    if report["stale_wrong_pattern"]:
        print(f"FAIL -- {len(report['stale_wrong_pattern'])} corrected fact(s) still match "
              f"their OWN wrong_patterns in the deployed index:")
        for r in report["stale_wrong_pattern"]:
            print(f"    {r['key']}: matched {r['matched_patterns']}")
            for t in r["rows"]:
                print(f"        row: {t[:120]}")
        print("  These facts were corrected once and are silently serving the wrong "
              "content again (or still). Update the CONCISE rendering in "
              "precompute_rag_embeddings.py to match the corrected fact, then re-run.")
        print()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[saved] {args.out}")

    if ok:
        print("CLEAN -- no corrected fact's OWN wrong_patterns matches its deployed "
              "rendering.")
    else:
        print("FAIL -- see above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
