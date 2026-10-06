#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AN ANCHOR OR PIN FOR A CORRECTED FACT MAY NOT CONTAIN THAT FACT'S OWN SUPERSEDED VALUE.

Usage:
    python scripts/check_anchor_provenance.py      # exit 1 if any anchor/pin is stale-valued

WHY THIS IS A CHECK AND NOT A CONVENTION. Three separate controls in two days were each
authored pointing at the value their own fact had already rejected:

  2026-10-05  act_section_12.wrong_patterns      rejected the CORRECT "Part XII" citation
  2026-10-05  check_facts_index_sync.PINNED      required "ifikapo tarehe 10", which s.14(1)
                                                 contradicts and the fact's verified_by
                                                 explicitly says appears in no source
  2026-10-06  regenerate_rag_e5 critical_queries required "milioni kumi na moja" -- the
                                                 fabricated 11M EFD threshold -- so the regen
                                                 gate DEMANDED the fabrication be retrievable,
                                                 and any regen correcting row 57 would have
                                                 tripped it and read as the regression

⛔ THE COMMON CAUSE: every one was chosen by searching the INDEX for text that is PRESENT AND
UNIQUE -- and a stale row is present and unique. Nothing in anchor selection asked whether the
text being anchored was TRUE. The index is where the stale text lives, so it is the one place an
anchor must not be drawn from.

THE RULE, structural rather than remembered: for any fact carrying a `correction_note`, its
anchors and pins come from the CORRECTED value in locked_facts.json, and this check fails if one
contains a value the fact itself records as superseded.

HOW THE SUPERSEDED VALUE IS OBTAINED -- three sources, because no single one covers the three
historical instances, and that is a measured statement not a hedge:

  1. `wrong_patterns` literals (digit groups, alternation groups like `(11|14),?000,?000`)
     catches the PINNED 'tarehe 10' case and the Part XIII case.
  2. quoted strings inside `correction_note` ("corrected from 'one hundred thousand TZS'")
     catches value corrections whose wrong_patterns are regex-only.
  3. ⚠️ SWAHILI WORD FORMS of those digit groups. This limb is what catches the THIRD instance
     and nothing else does: the stale anchor was 'milioni kumi na moja', the WORD form of
     11,000,000, while the wrong_pattern holds `(11|14),?000,?000` in DIGITS. The same
     digits-vs-words mismatch is why that fact's wrong_pattern also missed three training rows
     saying "milioni 11". A digits-only check would pass all three and report clean.

R20: this check must be able to fail. tests/test_anchor_provenance.py plants each of the three
historical stale anchors (must block) and the current corrected ones (must pass).
"""
import argparse
import importlib.util
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
FACTS = os.path.join(REPO, "scripts", "locked_facts.json")
REGEN = os.path.join(REPO, "kaggle", "regenerate_rag_e5.py")

# Swahili number words for the magnitudes that actually appear as fees/thresholds in this
# corpus. Bounded on purpose: a general numeral generator would be more code and more ways to
# be wrong, and the only job here is to recognise a magnitude written in words.
_ONES = {1: "moja", 2: "mbili", 3: "tatu", 4: "nne", 5: "tano", 6: "sita", 7: "saba",
         8: "nane", 9: "tisa", 10: "kumi", 11: "kumi na moja", 12: "kumi na mbili",
         13: "kumi na tatu", 14: "kumi na nne", 15: "kumi na tano", 20: "ishirini",
         25: "ishirini na tano", 30: "thelathini", 50: "hamsini", 100: "mia moja",
         200: "mia mbili", 500: "mia tano"}


def _swahili_forms(n):
    """Word forms of a magnitude, e.g. 11,000,000 -> {'milioni kumi na moja', 'milioni 11'}."""
    out = set()
    for unit, div in (("milioni", 1_000_000), ("elfu", 1_000)):
        if n % div == 0:
            q = n // div
            out.add(f"{unit} {q}")
            if q in _ONES:
                out.add(f"{unit} {_ONES[q]}")
                out.add(f"{_ONES[q]} {unit}")          # 'laki moja'-style inversions
    if n == 100_000:
        out.update({"laki moja", "elfu mia moja"})
    return out


def superseded_values(fact, strict=False):
    """Every string this fact itself identifies as a value it no longer asserts.

    ⛔ `strict=True` IS REQUIRED FOR ANCHORS AND MUST NOT BE USED FOR PINS, and the asymmetry is
    the whole design. A PIN is keyed to a fact, so attribution is exact and every extracted
    fragment is usable. An ANCHOR is NOT keyed to any fact, so the only available attribution is
    "this anchor contains some corrected fact's stale value" -- and with short fragments that is
    mostly noise: 'asilimia 10' is one fact's superseded value and another's correct claim.

    Measured, not predicted: the non-strict extraction produced EIGHT false positives on the
    live repo, every one cross-fact (a VAT fact's 'miezi 6' matched the VAT six-month anchor; a
    WCF fact's 'miaka mitatu' matched the AMT anchor). That made the check able to BLOCK CORRECT
    ANCHORS, which R21 names as the expensive direction -- a false block here delays a
    correction regen.

    So strict keeps only DISTINCTIVE values: a phrase of >=3 words, or a numeric magnitude of
    >=7 characters. That still catches the specimen it exists for -- 'milioni kumi na moja' is
    four words -- while dropping the two-word n-grams that caused every false positive.
    """
    vals = set()

    # 1. literals and alternation groups inside wrong_patterns
    for p in fact.get("wrong_patterns") or []:
        for alt, _ in re.findall(r"\(([\d|]+)\)([,.?]*0{3}[,.?]*0{3})", p):
            for q in alt.split("|"):
                if q.isdigit():
                    n = int(q) * 1_000_000
                    vals.add(f"{n:,}")
                    vals |= _swahili_forms(n)
        for lit in re.findall(r"(?<!\d)(\d{1,3}(?:,\d{3})+)(?!\d)", p):
            vals.add(lit)
            vals |= _swahili_forms(int(lit.replace(",", "")))
        # ⚠️ LITERAL FRAGMENTS, AND THE FIRST VERSION OF THIS MISSED TWO OF THE THREE HISTORICAL
        # SPECIMENS -- i.e. the check was PARTLY VACUOUS and its own test caught it.
        #
        #   'part\s*xiii'                      -> stripping `\\` left "part s xiii", so the
        #                                         planted 'Part XIII' never matched.
        #   'nssf.*tarehe 10 au mwishoni...'   -> the fragment pattern allowed only letters and
        #                                         spaces, so the run broke at the DIGIT in
        #                                         "tarehe 10" and the decisive phrase was never
        #                                         extracted.
        #
        # Both are the same mistake: treating a regex as a string to be scrubbed rather than as
        # a structure with literal runs between its operators. So: normalise whitespace classes
        # to a real space FIRST, then split on the operators, then keep the literal runs --
        # digits included, because the figures are the point.
        # `\s*` becomes a SPACE, not a split boundary -- it means "optional whitespace", so
        # splitting on it tore `320\s*[-]\s*328` into three runs too short to keep, and the
        # ss.320-328 range vanished. Only true discontinuities (`.*`, `|`, `[^..]{0,60}`) split.
        sk = re.sub(r"\\s[*+?]?", " ", p)
        sk = re.sub(r"\[\^[^\]]*\][{(][^})]*[})]|\.\*|\.\{[^}]*\}|\\d[*+?]?", " | ", sk)
        sk = re.sub(r"\(\?[:=!<][^)]*\)|\\[bwWSD]|[\\^$+?*(){}\[\]]", " ", sk)
        for frag in sk.split("|"):
            f = " ".join(frag.split())
            if len(f) < 6 or not re.search(r"[a-zA-Z0-9]", f):
                continue
            if len(f.split()) >= 2:
                vals.add(f.lower())
            # ⚠️ ALSO EMIT WORD N-GRAMS CONTAINING A DIGIT. The decisive phrase is often a
            # FRAGMENT of the run: the pin said 'ifikapo tarehe 10' while the run is
            # 'nssf tarehe 10 au mwisho wa mwezi', and `run in anchor` is the wrong direction
            # for that. Restricted to n-grams carrying a digit so this does not emit every
            # ordinary word pair ('au mwisho') and turn into a blocker for correct anchors.
            w = f.split()
            for n in (2, 3):
                for i in range(len(w) - n + 1):
                    g = " ".join(w[i:i + n])
                    if re.search(r"\d", g) and len(g) >= 6:
                        vals.add(g.lower())
                        vals.add(g.replace(" ", "").lower())   # '320 - 328' -> '320-328'

    # 2. quoted strings inside correction_note / status prose
    prose = " ".join(str(fact.get(k) or "") for k in
                     ("correction_note", "status", "_renumbering_note", "_sibling_note",
                      "_legacy_source_note"))
    for q in re.findall(r"['\"]([^'\"]{4,60})['\"]", prose):
        vals.add(q.strip().lower())
    for lit in re.findall(r"(?<!\d)(\d{1,3}(?:,\d{3})+)(?!\d)", prose):
        vals |= _swahili_forms(int(lit.replace(",", "")))

    # Never treat a value the fact CURRENTLY asserts as superseded -- the same figure can be
    # right in one period and wrong in another (vat_threshold_200m states TZS 100,000,000
    # correctly as the 6-month threshold while its wrong_pattern targets it "kwa mwaka").
    current = " ".join(str(fact.get(k) or "") for k in ("fact", "correct_value")).lower()
    keep = set()
    for v in vals:
        if len(v) < 5:
            continue
        if v.lower() in current:
            continue
        if strict:
            numericish = bool(_NUMERIC.match(v)) and len(v) >= 7
            if len(v.split()) < 3 and not numericish:
                continue
        keep.add(v)
    return keep


_NUMERIC = re.compile(r"^[\d,.\s]+$")


def _contains(haystack, needle):
    """⚠️ A NUMERIC VALUE MUST MATCH ON A NUMERIC BOUNDARY, and the first version of this check
    did plain `in` and immediately produced a FALSE POSITIVE: `200,000` (a superseded
    minimum-wage figure) matched inside `200,000,000 kwa miezi 12`, the VAT-threshold anchor,
    and attributed a wage fact's stale value to a VAT guard.

    That is the same substring trap as `100,000` inside `100,000,000`, which CLAUDE.md records
    three times in the OOC lists and which bit the NSSF-fine propagation sweep earlier today.
    It recurs because money in this corpus is comma-grouped, so every magnitude is a prefix of
    a larger one. Plain substring matching on figures is never right here.

    Phrases keep plain substring matching -- 'tarehe 10' inside 'ifikapo tarehe 10' is a TRUE
    positive and the whole point of the check.
    """
    if _NUMERIC.match(needle):
        return re.search(rf"(?<![\d,.]){re.escape(needle)}(?![\d,.])", haystack) is not None
    # ⚠️ A MIXED TOKEN ENDING IN A DIGIT NEEDS THE SAME BOUNDARY, and omitting it was the THIRD
    # substring collision of the day: the n-gram 'asilimia 1' matched inside 'asilimia 10',
    # attributing a 1%-fact's stale value to the NSSF-employer 10% anchor. Any needle whose
    # last character is a digit must not be allowed to match a longer number.
    if needle and needle[-1].isdigit():
        return re.search(rf"{re.escape(needle.lower())}(?![\d,.])",
                         haystack.lower()) is not None
    return needle.lower() in haystack.lower()


def _parse_anchors():
    """(guard_name, anchor) pairs from the regen's committed critical_queries."""
    src = io.open(REGEN, encoding="utf-8").read()
    out = []
    for name, _q, anchors in re.findall(
            r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", src):
        for a in re.findall(r"'([^']*)'", anchors):
            if a.strip():
                out.append((name, a))
    return out


def _parse_pins():
    spec = importlib.util.spec_from_file_location(
        "check_facts_index_sync", os.path.join(REPO, "scripts", "check_facts_index_sync.py"))
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_facts_index_sync"] = mod
    spec.loader.exec_module(mod)
    return [(k, v[1]) for k, v in mod.PINNED.items()
            if isinstance(v, tuple) and len(v) > 1 and isinstance(v[1], str)]


def check(facts=None, anchors=None, pins=None):
    facts = facts if facts is not None else json.load(io.open(FACTS, encoding="utf-8"))
    anchors = anchors if anchors is not None else _parse_anchors()
    pins = pins if pins is not None else _parse_pins()

    corrected = {k: v for k, v in facts.items()
                 if isinstance(v, dict) and "correction_note" in v and not k.startswith("_")}
    stale_by_pin = {k: superseded_values(v) for k, v in corrected.items()}
    stale_by_anchor = {k: superseded_values(v, strict=True) for k, v in corrected.items()}

    faults = []

    # PINS are keyed by fact, so the attribution is exact.
    for key, needle in pins:
        for bad in sorted(stale_by_pin.get(key, ())):
            if _contains(needle, bad):
                faults.append({"kind": "PIN", "fact": key, "text": needle,
                               "superseded_value_found": bad})

    # ANCHORS are not keyed by fact, so an anchor is attributed to a corrected fact only when
    # it contains that fact's superseded value -- which is the fault condition itself. That
    # keeps attribution from being guesswork: a match IS the evidence.
    for name, anchor in anchors:
        for key, bads in stale_by_anchor.items():
            for bad in sorted(bads):
                if _contains(anchor, bad):
                    faults.append({"kind": "ANCHOR", "guard": name, "fact": key,
                                   "text": anchor, "superseded_value_found": bad})
    return faults


def main():
    argparse.ArgumentParser().parse_args()
    facts = json.load(io.open(FACTS, encoding="utf-8"))
    corrected = [k for k, v in facts.items()
                 if isinstance(v, dict) and "correction_note" in v and not k.startswith("_")]
    anchors, pins = _parse_anchors(), _parse_pins()
    faults = check(facts, anchors, pins)

    print(f"corrected facts (with correction_note) : {len(corrected)}")
    print(f"committed guard anchors checked         : {len(anchors)}")
    print(f"committed pins checked                  : {len(pins)}")
    print(f"stale-valued anchors/pins               : {len(faults)}")
    for f in faults:
        who = f.get("guard") or f["fact"]
        print(f"\n  [{f['kind']}] {who}")
        print(f"      text          : {f['text']!r}")
        print(f"      contains      : {f['superseded_value_found']!r}")
        print(f"      corrected fact: {f['fact']}")
    if faults:
        print("\nFAIL -- an anchor or pin points at a value its own fact has rejected. Draw it "
              "from the CORRECTED value in locked_facts.json, never from the index: the index "
              "is where the stale text lives.")
        return 1
    print("\nOK -- no anchor or pin contains its own fact's superseded value.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
