#!/usr/bin/env python3
"""
FACT-GUARDIAN validation script.
Usage: python scripts/check_locked_facts.py --file path/to/batch.jsonl
Exit code: 0 = clean, 1 = violations found

Assertions are defined in scripts/locked_facts.json (wrong_patterns per fact key).
Last updated: 2026-06-16 — added from primary source verification:
  paye_all_bands_sequence    — 0%/8%/20%/25%/30% bands (PWC Jan 2026)
  paye_nonresident_flat_rate — 15% flat for non-residents (PWC Jan 2026)
  paye_personal_relief       — CORRECTED: no personal relief exists in Tanzania
  brela_annual_return_fee    — TZS 22,000 filing; TZS 2,500/month late penalty
  wcf_new_employer_registration — 30 days from first hire
  wcf_disease_reporting_deadline — disease 7 days; death/claim 12 months
  gn605a_increment_range     — TZS 20,000–195,000 increment range (PKF Oct 2025)
"""
import json, sys, re, argparse, os
from datetime import datetime

def load_locked_facts(facts_path="scripts/locked_facts.json"):
    if not os.path.exists(facts_path):
        print(f"ERROR: locked_facts.json not found at {facts_path}")
        sys.exit(1)
    with open(facts_path, encoding="utf-8") as f:
        data = json.load(f)
    # Return only fact entries (not _meta or _unresolved_items)
    return {k: v for k, v in data.items()
            if not k.startswith("_") and "wrong_patterns" in v}

# ─── TWO NARROWINGS, ADDED 2026-10-08 ────────────────────────────────────────────
# THE DEFECT. This gate flagged `b008_paye_adv_002`, `_005`, `_007`, `_015` and
# `b008_paye_adv_001` -- rows whose whole purpose is to DENY the wrong value
# ("kiwango 8% (si 9%)", "HAKUNA punguzo la kibinafsi tofauti la TZS 26,000"). Four of
# them had already been QUARANTINED on this basis; `_001` is live at HEAD carrying the
# same false positive. Measured on the real matcher: `paye.*band.*9%(?! is wrong| ni
# kosa)` matched a span of 604-812 characters, so the unbounded `.*` ran across the whole
# of answer_sw and into answer_en, and the `9%` it finally landed on was the one inside
# the English "(not 9%)". The lookahead sits AFTER the value and excuses two literal
# trailing phrases, so a negation BEFORE the value is invisible to it.
#
# ⚠️ BOTH NARROWINGS CAN DELETE FINDINGS, WHICH IS THE DANGEROUS DIRECTION. A loose
# demotion rule does not add noise -- it silently shrinks the population under
# adjudication, and a shorter finding list reads as progress. That failure happened four
# times in one session on 2026-10-07 and twice more on 2026-10-08. So: every alternative
# in NEGATION is word-bounded (a bare `si\s` matches inside the ordinary Swahili word
# `kiasi `), the window is bounded at 40 characters, demoted matches are RECORDED rather
# than dropped, and tests/test_locked_facts_polarity.py pins that every known TRUE
# positive still flags.
NEGATION = (
    r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhapana\b|\bhakuna\b|\bhaina\b|\bhakutakuwa\b"
    r"|\bni\s+makosa\b|\bsi\s+kweli\b|\buwongo\b|\bmuhimu\b"
    r"|\bnot\b|\bno\b|\bincorrect\b|\bis\s+wrong\b|\bwrong\b|\bfalse\b)")
# 60, not 40, and the number is measured rather than chosen. Swahili puts a full noun
# phrase between the negator and the figure: in b008_paye_adv_005's "HAKUNA punguzo la
# kibinafsi tofauti la TZS 26,000" the gap is 42 characters, so a 40-char window flagged a
# row that denies the phantom relief in as many words. 60 covers that construction and the
# true-positive probes (lfp_01/05/07/08) are pinned to confirm it does not reach them --
# widening a demotion window is the DELETING direction, so it is justified by a measured
# construction and bounded by a test, never nudged until the red goes away.
NEGATION_WINDOW = 60

# A pattern whose `.*` has spanned more than this is not evidence about anything: the
# tokens it joined are in unrelated sentences, and in the measured cases in different
# ANSWERS. Same reasoning as D-FIDELITY-6's +/-60-character proximity window and as the
# rejection of bare-magnitude anchors ('asilimia 10', 'TZS 70,000') that matched two rows.
MAX_MATCH_SPAN = 160

_VALUE = re.compile(r"\d[\d,.]*\s*%|\d[\d,.]*|asilimia\s*\d+")

# ── COMPILE CACHE ────────────────────────────────────────────────────────────────
# Not a micro-optimisation: locked_facts.json holds ~255 facts with ~2,000 patterns
# between them, which overflows Python's 512-entry internal regex cache, so every pair
# recompiled most of them. That made a corpus-wide run ~40s per file -- expensive enough
# that wiring this gate into the suite (which pre-push runs) would have been a real cost,
# and expense is how a check ends up not being run. Caching the compiled objects takes a
# full-corpus pass from minutes to seconds and changes no behaviour: `_COMPILED[p]` is the
# same object `re.search(p, ...)` would have built.
_COMPILED = {}
_UNCOMPILABLE = set()


def _compiled(pattern):
    """The compiled pattern, or None if it is not valid regex (caller falls back to a
    literal match, as this gate always has)."""
    low = pattern.lower()
    if low in _UNCOMPILABLE:
        return None
    got = _COMPILED.get(low)
    if got is None:
        try:
            got = _COMPILED[low] = re.compile(low)
        except re.error:
            _UNCOMPILABLE.add(low)
            return None
    return got


def _demotion(text, match):
    """Return a demotion reason, or None if the match stands as an assertion.

    Checked in this order on purpose: SPAN first, because a 600-character match has no
    single 'the value' to test polarity against -- asking about polarity first would be
    answering a question about a match that does not mean anything yet.
    """
    span = match.end() - match.start()
    if span > MAX_MATCH_SPAN:
        return (f"span_too_wide:{span}ch — the pattern's `.*` joined tokens "
                f"{span} characters apart, across unrelated sentences")
    # The value this pattern is about is the LAST figure inside the match; patterns in
    # locked_facts.json are written value-last.
    vals = list(_VALUE.finditer(match.group(0)))
    if not vals:
        return None
    v = vals[-1]
    abs_start = match.start() + v.start()
    before = text[max(0, abs_start - NEGATION_WINDOW):abs_start]
    # ⛔ A NEGATION ANYWHERE IN THE WINDOW, NOT IMMEDIATELY BEFORE THE VALUE. The first
    # version anchored the negator to the value (`NEGATION + separators + $`) and that is
    # wrong about how negation works: it SCOPES OVER A PHRASE. Measured on lfp_04
    # (b008_paye_adv_005, a row found wrongly removed): "there is NO SEPARATE personal
    # relief of TZS 26,000" puts six words between the negator and the figure, and the
    # Swahili limb puts a five-word noun phrase there ("HAKUNA punguzo la kibinafsi tofauti
    # la TZS 26,000"). An adjacency rule cannot reach either.
    #
    # ⚠️ THIS IS A LOOSENING OF A DEMOTION RULE, WHICH IS THE DELETING DIRECTION -- the
    # failure that struck four times on 2026-10-07 and twice more on 2026-10-08, every time
    # by making the finding list shorter, which reads as progress. Two things bound it, and
    # neither is optional: the window is 60 characters (not a sentence, not a row), and the
    # TRUE POSITIVES ARE PINNED -- lfp_01/05/07/08 in
    # eval/fidelity/locked_facts_polarity_probes.jsonl must still flag, including lfp_05,
    # which is the SAME FIGURE as lfp_04 with the opposite polarity. If a future widening
    # deletes one of those, the suite goes red rather than quiet.
    neg = re.search(NEGATION, before, re.I)
    if neg:
        return (f"mention_under_negation — {v.group(0)!r} has {neg.group(0)!r} within "
                f"{NEGATION_WINDOW} characters before it: {before[-48:]!r}")
    return None


def check_pair(pair, facts, include_demoted=False):
    flags = []
    demoted = []
    text = (
        pair.get("answer_sw", "") + " " +
        pair.get("answer_en", "")
    ).lower()
    pid = pair.get("id", "unknown")

    for fact_key, fact in facts.items():
        for pattern in fact.get("wrong_patterns", []):
            rec = {
                "pair_id": pid,
                "fact_key": fact_key,
                "wrong_pattern": pattern,
                "correct": fact.get("fact", ""),
                "source": fact.get("primary_source", "")
            }
            rx = _compiled(pattern)
            if rx is not None:
                match = rx.search(text)
            else:
                # Invalid regex: fall back to a literal match, as this gate always has.
                # Demotions still apply -- a literal match is still a match whose polarity
                # matters.
                idx = text.find(pattern.lower())
                match = None
                if idx >= 0:
                    class _M:  # minimal shim with the three attributes _demotion uses
                        def __init__(self, s, e, g):
                            self._s, self._e, self._g = s, e, g

                        def start(self):
                            return self._s

                        def end(self):
                            return self._e

                        def group(self, _=0):
                            return self._g
                    match = _M(idx, idx + len(pattern), pattern.lower())
            if match is None:
                continue
            why = _demotion(text, match)
            if why:
                rec["demoted"] = why
                demoted.append(rec)
            else:
                flags.append(rec)
    return (flags, demoted) if include_demoted else flags

def main():
    parser = argparse.ArgumentParser(
        description="Validate training pairs against locked regulatory facts"
    )
    parser.add_argument("--file", required=True,
                        help="Path to JSONL file to validate")
    parser.add_argument("--facts", default="scripts/locked_facts.json",
                        help="Path to locked_facts.json")
    parser.add_argument("--log", default="scripts/fact_check_log.txt",
                        help="Path to log file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    facts = load_locked_facts(args.facts)
    total = 0
    flagged_pairs = 0
    all_flags = []

    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                pair = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON ERROR on line {total+1}: {e}")
                continue
            total += 1
            flags = check_pair(pair, facts)
            if flags:
                flagged_pairs += 1
                all_flags.extend(flags)
                for flag in flags:
                    print(f"FLAG [{flag['pair_id']}] {flag['fact_key']}")
                    print(f"  Wrong pattern: '{flag['wrong_pattern']}'")
                    print(f"  Correct fact: {flag['correct'][:100]}")
                    print(f"  Source: {flag['source']}")
                    print()

    # Write log
    timestamp = datetime.now().isoformat()
    with open(args.log, "a", encoding="utf-8") as log:
        log.write(f"\n[{timestamp}] Checked {args.file}\n")
        log.write(f"Total: {total} | Flagged: {flagged_pairs}\n")
        for flag in all_flags:
            log.write(f"  FLAG [{flag['pair_id']}] {flag['fact_key']}: "
                      f"{flag['wrong_pattern']}\n")

    print(f"Checked {total} pairs. {flagged_pairs} pairs flagged.")

    if flagged_pairs > 0:
        print(f"\nFix all flagged pairs before committing.")
        print(f"Log written to: {args.log}")
        sys.exit(1)
    else:
        print("CLEAN — no locked fact violations found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
