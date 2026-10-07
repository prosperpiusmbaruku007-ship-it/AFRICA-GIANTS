# -*- coding: utf-8 -*-
"""EVERY LIVE ROW ASSERTING A FABRICATED EFD TURNOVER THRESHOLD, IN ANY NOTATION.

⛔ THE REASON THIS EXISTS IS THAT THE PREVIOUS SWEEP COUNTED THE NOTATION, NOT THE CLAIM.

A sweep run on 2026-10-06 for the spelled-out `milioni 11` found THREE rows. D-FIDELITY-7, run
over the same corpora the same day, found SEVEN — and the seven include rows the first sweep
could not see because they write the same fabricated figure as `TZS 11M` or `TZS 11,000,000`.

The cause is not carelessness. Every corpus sweep in this arc has been keyed on FIGURES, and the
fact's own `wrong_patterns` hold `(11|14),?000,?000` in DIGITS, so a sweep built from the fact's
own patterns is blind to the words by construction. Swahili writes money both ways and this
corpus uses both in the same file. **The number is the claim; the notation is an accident of who
typed the row.**

AND THE SECOND CAUSE IS WORSE, because it made a real remediation look complete. The 2026-08-29
quarantine recorded 58 rows. For 24 of them the fix was an EDIT IN PLACE, not a removal — the
OPENING sentence was repaired and the body prose was not:

    quarantined:  "EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11 au zaidi kwa mwaka."
    live today:   "EFD inahitajika kulingana na kizingiti cha mauzo kilichowekwa na TRA ..."
    SAME ROW, three sentences later: "... haujafika kizingiti cha TZS 11M ..."

The repair deleted the words a sweep keys on and left the digits standing. That is R25's
containment shape — a repair makes the symptom disappear without touching the cause, and a defect
with no symptom is never looked for — arriving in the corpus layer. See
eval/controls/audit_quarantine_reach.py for how it was found.

SO THIS SWEEP IS KEYED ON THE CLAIM. Three notation families, plus the guard itself as an
independent fourth reader:

  DIGITS   11,000,000 / 11000000 / 11.000.000 / TZS 11M / 11m
  WORDS    milioni 11 / milioni kumi na moja / milioni 11.5
  OTHER FABRICATED EFD FIGURES already on record (40M, 14M), which have the same status: TAA
           Cap.438 R.E.2023 s.44 sets NO turnover threshold for EFD at any level.
  GUARD    chike.fidelity.stated_wrong_thresholds — the production rule, as a second opinion that
           was written for a different purpose and therefore fails differently.

ADJUDICATION IS BY READING, NOT BY MATCHING, and the standard is the one set on 2026-10-05:
every candidate is printed in full and classified before anything is counted. A row that states
the figure IN ORDER TO REJECT IT is an ASSERTION of the correction, not of the fabrication —
polarity, not presence. The 2026-08-29 adversarial pairs are exactly that shape and quarantining
them would delete the corpus's own defence against the defect.

⚠️ A LOOSE MENTION RULE DOES NOT ADD NOISE -- IT DELETES FINDINGS. Every negation alternative
below is WORD-BOUNDED. In the NSSF-fine sweep a bare `si\s` matched inside the ordinary Swahili
word `kiasi ` and silently reclassified the one real false positive as a mention, shrinking the
adjudicated set. A shorter findings list is indistinguishable from progress.

R18: committed before the write-up that cites it.
Artifact: eval/results/efd_fabrication_all_notations_2026_10_06.json

Usage:  python eval/controls/sweep_efd_threshold_fabrication_all_notations.py
Exit 0 always -- this is a measurement, not a gate.
"""
import collections
import glob
import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "efd_fabrication_all_notations_2026_10_06.json")

from chike.fidelity import stated_wrong_thresholds                   # noqa: E402

# --- the three notation families ------------------------------------------------------------
#
# ⛔ THE BOUNDARY IS `(?![\d,]|\.\d)`, NOT `(?![\d,.])`, AND THE PLANTED SPECIMEN IS WHAT FOUND IT.
#
# The first draft used `(?![\d,.])`, intending to stop `11,000,000` matching inside
# `11,000,000,000`. It also stops it matching at the END OF A SENTENCE — "SI TZS 11,000,000." —
# because the next character is a full stop. The planted REJECTS specimen came back CLEAN, which
# is how it was caught; without that specimen the sweep would have silently under-counted every
# row whose figure closes a sentence, and under-counting looks exactly like a clean corpus.
#
# This is the same family as the money-boundary traps already on record (`100,000` inside
# `100,000,000`, `200,000` inside `200,000,000`, `asilimia 1` inside `asilimia 10`) — but in the
# opposite direction: those were too LOOSE and produced false positives; this one was too TIGHT
# and produced false negatives. A false negative in a boundary is the dangerous one, because it
# removes findings rather than adding noise.
DIGITS = re.compile(r"(?<![\d,])(?<!\d\.)(?:11|14|40)[,.\s]?000[,.\s]?000(?![\d,]|\.\d)"
                    r"|(?<![\d,])(?:11|14|40)\s?M\b", re.IGNORECASE)
WORDS = re.compile(r"milioni\s+(?:11|14|40)\b|milioni\s+kumi\s+na\s+moja|"
                   r"milioni\s+kumi\s+na\s+nne|milioni\s+arobaini", re.IGNORECASE)
# The subject must be EFD, or the figure is about something else entirely.
EFD = re.compile(r"\befd\b|mashine\s+ya\s+risiti|electronic\s+fiscal", re.IGNORECASE)

# Word-bounded, every alternative. See the module header for why this matters more than it looks.
NEGATION_BEFORE = re.compile(
    r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bsivyo\b|\bhakuna\b|\bhaina\b|\bhapana\b|\bhakina\b|"
    r"\bsiyo\b|\bnot\b|\bno\b|\bwala\b)[\s:,—–-]*(?:tzs\s*)?$", re.IGNORECASE)
# Phrases that mark the whole row as a CORRECTION of the fabrication rather than an assertion
# of it. These are the 2026-08-29 adversarial pairs and the corrected replacements.
CORRECTION_MARKERS = re.compile(
    r"hakuna\s+kizingiti|haina\s+kizingiti|bila\s+kujali\s+(?:kiasi\s+cha\s+)?mauzo|"
    r"kwa\s+default|si\s+kweli|sio\s+kweli|hiyo\s+si\s+sahihi|taarifa\s+rasmi|"
    r"commissioner[- ]general|kamishna\s+mkuu", re.IGNORECASE)

CORPORA = [
    ("cleaned_pairs", "datasets/tier1a/cleaned_pairs", ("answer_sw",), ("question_sw",)),
    ("sft_shaped_pairs", "datasets/tier1a/sft_shaped_pairs", ("output",), ("instruction",)),
    ("sft_EXPORTED_TRAINING", "datasets/tier1a/sft", ("output",), ("instruction",)),
    ("eval_set", "datasets/tier1a/eval_set", ("answer_sw", "output"),
     ("question_sw", "instruction")),
    ("adversarial", "datasets/tier1a/adversarial", ("answer_sw", "output"),
     ("question_sw", "instruction")),
    ("GOLD_accuracy", "eval/accuracy_gate", ("correct_answer_sw",), ("question_sw",)),
    ("GOLD_refusal", "eval/refusal_gate", ("correct_answer_sw", "answer_sw"), ("question_sw",)),
]


def classify(body):
    """ASSERTS_FABRICATION | REJECTS_FABRICATION | NO_EFD_SUBJECT | CLEAN, plus the hits."""
    hits = [(m.group(0), m.start()) for m in DIGITS.finditer(body)]
    hits += [(m.group(0), m.start()) for m in WORDS.finditer(body)]
    if not hits:
        return "CLEAN", []
    if not EFD.search(body):
        # The figure is present but the row is not about EFD -- e.g. a presumptive band edge,
        # which is LAWFUL at 11,000,000. Not this sweep's business.
        return "NO_EFD_SUBJECT", hits
    # polarity, per hit: a figure under a negation is named in order to be rejected
    asserted = [h for h, pos in hits
                if not NEGATION_BEFORE.search(body[max(0, pos - 24):pos])]
    if not asserted:
        return "REJECTS_FABRICATION", hits
    if CORRECTION_MARKERS.search(body):
        # The row carries the correct position somewhere. It may still assert the figure
        # elsewhere, so this is NOT an automatic clear -- it is a flag for reading.
        return "MIXED_READ_IT", hits
    return "ASSERTS_FABRICATION", hits


def main():
    rows = []
    for stage, rel, body_keys, q_keys in CORPORA:
        for path in sorted(glob.glob(os.path.join(REPO, *rel.split("/"), "*.jsonl"))):
            loc = os.path.relpath(path, REPO).replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    body = next((obj[k] for k in body_keys
                                 if isinstance(obj.get(k), str) and obj[k].strip()), "")
                    if not body:
                        continue
                    verdict, hits = classify(body)
                    if verdict == "CLEAN":
                        continue
                    question = next((obj[k] for k in q_keys
                                     if isinstance(obj.get(k), str)), "")
                    rows.append({
                        "stage": stage, "locator": f"{loc}:{n}",
                        "id": obj.get("id", ""),
                        "verdict": verdict,
                        "notation": sorted({h for h, _ in hits}),
                        "guard_also_flags": bool(stated_wrong_thresholds(body)),
                        "question": question[:180],
                        "body": body,
                    })

    # R20, both halves: a sweep that reads no corpus, and a sweep whose patterns match nothing,
    # both report zero and both look clean.
    assert rows, ("nothing matched anywhere, including the 2026-08-29 adversarial pairs that "
                  "quote the fabrication deliberately. The patterns or the paths are wrong.")
    # ⛔ THE POLARITY LIMB IS EXERCISED ON A PLANTED SPECIMEN, NOT ON A BELIEF ABOUT THE CORPUS.
    #
    # The first draft asserted `any(verdict == "REJECTS_FABRICATION")` over the corpus, "because
    # the corpus demonstrably contains such rows". It does not. The 2026-08-29 adversarial pairs
    # that quote the fabrication in order to refuse it are not in any jsonl corpus — the rows
    # that carry the correction under a negation live in scripts/precompute_rag_embeddings.py
    # (index rows 57, 63, 159), which this sweep does not read.
    #
    # That assertion would have aborted a working instrument on a false premise about data it had
    # just finished reading — R26's second half exactly: when a control does not fire, eliminate
    # the SPECIMEN before concluding anything, and the specimen here was my own assumption. The
    # right non-vacuity check plants the thing the limb must catch.
    _planted_reject = ("Kizingiti cha kuanza kutumia mashine ya EFD: EFD haina kizingiti cha "
                       "mauzo. SI TZS 11,000,000.")
    _planted_assert = "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 kwa mwaka."
    assert classify(_planted_reject)[0] == "REJECTS_FABRICATION", (
        f"the polarity limb does not fire: a figure named under an explicit negation was "
        f"classified {classify(_planted_reject)[0]}. Every 'ASSERTS' verdict below is therefore "
        f"unadjudicated.")
    assert classify(_planted_assert)[0] == "ASSERTS_FABRICATION", (
        f"the assertion limb does not fire on the plainest possible statement of the "
        f"fabrication: {classify(_planted_assert)[0]}. The sweep is inert.")
    assert classify("Kiasi cha TZS 11,000,000 ni kizingiti cha EFD.")[0] == (
        "ASSERTS_FABRICATION"), (
        "`kiasi ` was read as a negation. A loose mention rule does not add noise -- it DELETES "
        "findings, and this exact substring did so once already (NSSF-fine sweep, 2026-10-05).")

    asserts = [r for r in rows if r["verdict"] == "ASSERTS_FABRICATION"]
    mixed = [r for r in rows if r["verdict"] == "MIXED_READ_IT"]
    rejects = [r for r in rows if r["verdict"] == "REJECTS_FABRICATION"]
    nosubj = [r for r in rows if r["verdict"] == "NO_EFD_SUBJECT"]

    # THE NOTATION SPLIT -- the whole point of the sweep.
    def family(r):
        d = any(DIGITS.fullmatch(x) or DIGITS.match(x) for x in r["notation"])
        w = any(WORDS.match(x) for x in r["notation"])
        return "both" if d and w else "digits" if d else "words"

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/controls/sweep_efd_threshold_fabrication_all_notations.py",
        "question": ("Which live rows assert a fabricated EFD turnover threshold, in ANY "
                     "notation -- and how many would a digits-only or a words-only sweep miss?"),
        "why_this_population": (
            "every live corpus plus both gold sets. The gold sets are included deliberately: a "
            "gold answer that asserts the fabrication is a scoring key rewarding the defect, "
            "which is worse than a training row carrying it."),
        "the_notation_blindness": (
            "A sweep for the spelled-out 'milioni 11' found 3 rows; D-FIDELITY-7 found 7 on the "
            "same corpora the same day. Every corpus sweep in this arc has been keyed on "
            "FIGURES, and the fact's own wrong_patterns hold (11|14),?000,?000 in DIGITS -- so a "
            "sweep built from the fact's own patterns is blind to the words by construction."),
        "adjudication_rule": (
            "POLARITY, NOT PRESENCE, and word-bounded. A row stating the figure in order to "
            "REJECT it asserts the CORRECTION. Quarantining those would delete the corpus's own "
            "defence against the defect. MIXED_READ_IT rows carry a correction marker AND an "
            "un-negated figure -- they are flagged for reading, never auto-cleared."),
        "totals": {
            "rows_matching_any_notation": len(rows),
            "ASSERTS_FABRICATION": len(asserts),
            "MIXED_READ_IT": len(mixed),
            "REJECTS_FABRICATION": len(rejects),
            "NO_EFD_SUBJECT": len(nosubj),
            "asserts_by_stage": dict(collections.Counter(r["stage"] for r in asserts)),
            "asserts_by_notation_family": dict(collections.Counter(family(r) for r in asserts)),
            "asserts_the_guard_also_flags": len([r for r in asserts if r["guard_also_flags"]]),
        },
        "ASSERTS_FABRICATION": asserts,
        "MIXED_READ_IT": mixed,
        "REJECTS_FABRICATION_excluded_by_name": [
            {"locator": r["locator"], "id": r["id"], "notation": r["notation"],
             "question": r["question"]} for r in rejects],
        "NO_EFD_SUBJECT_excluded_by_name": [
            {"locator": r["locator"], "id": r["id"], "notation": r["notation"]} for r in nosubj],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    t = artifact["totals"]
    print(f"rows matching any notation:      {t['rows_matching_any_notation']}")
    print(f"  ASSERTS_FABRICATION            {t['ASSERTS_FABRICATION']}")
    print(f"  MIXED_READ_IT                  {t['MIXED_READ_IT']}")
    print(f"  REJECTS_FABRICATION (excluded) {t['REJECTS_FABRICATION']}")
    print(f"  NO_EFD_SUBJECT      (excluded) {t['NO_EFD_SUBJECT']}")
    print(f"  asserts by stage:     {t['asserts_by_stage']}")
    print(f"  asserts by notation:  {t['asserts_by_notation_family']}")
    print(f"  of which D-FIDELITY-7 also flags: {t['asserts_the_guard_also_flags']}")
    print()
    for r in asserts + mixed:
        print(f"  [{r['verdict']:20}] {r['locator']}  {r['notation']}  guard={r['guard_also_flags']}")
        print(f"      Q: {' '.join(r['question'].split())[:150]}")
        print(f"      A: {' '.join(r['body'].split())[:330]}")
        print()
    print(f"[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
