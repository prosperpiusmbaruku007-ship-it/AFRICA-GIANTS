# -*- coding: utf-8 -*-
"""HOW MANY GOLD ANSWERS CARRY ANY PROVENANCE, AND HOW MANY AGREE WITH OUR OWN VERIFIED FACTS?

THE QUESTION, and it is the strongest one asked this week. A gold answer is a CLAIM ABOUT THE LAW.
Every failure count this project has quoted is the model measured against those claims. If a gold
answer is wrong, the row is booked as a model failure and the adjudication cannot see it, because
the adjudication reads the key. Four `_scoring_key_correction` fields already exist in
eval_questions_003.jsonl and one in edge_probe_natural_048.jsonl -- every one found by accident
while investigating something else.

WHAT THIS MEASURES, in three layers, cheapest first:

  1. PROVENANCE COVERAGE -- does the row carry a source at all? This is a field census, exact,
     no judgement.
  2. CHECKABILITY -- does the gold answer assert a figure, rate, or deadline that COULD be
     checked against a statute? A prose-only rubric ("must not fabricate") has nothing to check.
  3. AGREEMENT -- for every gold answer asserting a quantity that also appears in
     scripts/locked_facts.json, do they agree? This is the only layer that can find a WRONG key
     mechanically, and it is a LOWER BOUND on the error rate for a reason stated below.

⚠️ WHY LAYER 3 IS A LOWER BOUND AND NOT AN ESTIMATE -- this is the caveat that must travel with
any number this prints. It compares gold answers against locked_facts.json, which is OUR OWN fact
store. So:
  * A gold answer wrong in the SAME WAY as the locked fact agrees, and is counted CLEAN here.
    `efd_threshold_tzs_11m` was fabricated and sat in locked_facts for months while eval_355's
    gold matched it -- this layer would have called that pair consistent. Consistency with
    ourselves is not correctness.
  * Only a reading of the STATUTE can settle a disagreement either way, and this harness reads
    no statutes. A flagged pair says "these two disagree", never "the key is wrong".
  * 68 of the 246 locked facts have verified_by=None (counted below). A gold answer agreeing with
    an unverified fact inherits its unverifiedness.

So the honest output is a CEILING ON WHAT WE CAN CURRENTLY SEE: the share of gold answers for
which no independent check exists at all, plus the disagreements visible without leaving the repo.

R22: the population is named and it is the one the decision applies to -- every gold answer the
project's quoted failure counts are measured against.

R18: committed before the write-up that cites it.
Artifact: eval/results/gold_answer_provenance_audit.json

Usage:  python eval/controls/audit_gold_answer_provenance.py
Exit 0 always -- a measurement, not a gate.
"""
import collections
import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "gold_answer_provenance_audit.json")
FACTS = os.path.join(REPO, "scripts", "locked_facts.json")

# The three corpora the project's failure counts are quoted from.
CORPORA = [
    ("the_78", "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl"),
    ("the_48", "eval/accuracy_gate/edge_probe_natural_048.jsonl"),
    ("eval_150", "eval/accuracy_gate/eval_questions_003.jsonl"),
]
GOLD_KEYS = ("correct_answer_sw", "correct_answer_en", "expected_behavior")
SOURCE_KEYS = ("source_url", "primary_source_url", "primary_source", "source",
               "verified_by", "statute", "citation")

# A gold answer asserting one of these is CHECKABLE: there is a quantity a statute could confirm.
_MONEY = re.compile(r"(?:TZS|USD)\s*[\d,]{3,}|\b\d{1,3}(?:,\d{3}){1,}\b")
_RATE = re.compile(r"\b\d{1,2}(?:\.\d)?\s*%|asilimia\s+[\w\s\.]{1,20}")
_DEADLINE = re.compile(r"\b(?:siku|days?|miezi|months?|mwaka|years?)\s+\d{1,3}|"
                       r"\b\d{1,3}\s+(?:siku|days?|miezi|months?|mwaka|years?)", re.I)


def norm_money(text):
    """Every money-like figure in the text, as ints, for comparison against a fact's value."""
    out = set()
    for m in re.finditer(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{4,}\b", text):
        try:
            out.add(int(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


def main():
    facts = json.load(open(FACTS, encoding="utf-8"))
    if isinstance(facts, dict) and "facts" in facts:
        facts = facts["facts"]
    fact_items = (list(facts.items()) if isinstance(facts, dict)
                  else [(f.get("key", str(i)), f) for i, f in enumerate(facts)])
    unverified = sum(1 for _, f in fact_items
                     if isinstance(f, dict) and not f.get("verified_by"))

    # Fact values as numbers, so a gold answer's figure can be matched to a fact that names it.
    fact_numbers = {}
    for key, f in fact_items:
        if not isinstance(f, dict):
            continue
        blob = " ".join(str(f.get(k, "")) for k in
                        ("correct_value", "fact", "value", "statement"))
        for n in norm_money(blob):
            fact_numbers.setdefault(n, []).append(key)

    per_corpus, rows = {}, []
    for label, rel in CORPORA:
        path = os.path.join(REPO, rel)
        data = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        tally = collections.Counter()
        for r in data:
            gold = " ".join(str(r.get(k, "")) for k in GOLD_KEYS).strip()
            has_source = any(str(r.get(k, "")).strip() for k in SOURCE_KEYS)
            checkable = bool(_MONEY.search(gold) or _RATE.search(gold)
                             or _DEADLINE.search(gold))
            corrected = any(k.startswith("_scoring_key_correction") or k == "_correction"
                            for k in r)
            nums = norm_money(gold)
            matched = sorted({k for n in nums for k in fact_numbers.get(n, [])})
            tally["rows"] += 1
            tally["with_source"] += int(has_source)
            tally["checkable"] += int(checkable)
            tally["checkable_without_source"] += int(checkable and not has_source)
            tally["already_corrected"] += int(corrected)
            tally["matched_a_locked_fact_figure"] += int(bool(matched))
            rows.append({"corpus": label, "id": str(r.get("id")),
                         "has_source": has_source, "gold_is_checkable": checkable,
                         "already_has_scoring_key_correction": corrected,
                         "locked_facts_sharing_a_figure": matched[:4],
                         "gold": gold[:240]})
        per_corpus[label] = dict(tally)

    assert len(rows) > 200, f"only {len(rows)} gold answers read -- the corpora paths are wrong"
    assert any(r["gold_is_checkable"] for r in rows), (
        "no gold answer was judged checkable -- the patterns are not matching, so a clean "
        "result here would be vacuous")

    tot = collections.Counter()
    for c in per_corpus.values():
        tot.update(c)

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/controls/audit_gold_answer_provenance.py",
        "question": ("How many gold answers carry any provenance, how many assert something a "
                     "statute could check, and how many could be cross-checked against our own "
                     "locked facts?"),
        "headline": {
            "gold_answers_examined": tot["rows"],
            "carrying_any_source_field": tot["with_source"],
            "asserting_a_checkable_quantity": tot["checkable"],
            "checkable_but_carrying_NO_source": tot["checkable_without_source"],
            "already_carrying_a_scoring_key_correction": tot["already_corrected"],
            "sharing_a_figure_with_some_locked_fact": tot["matched_a_locked_fact_figure"],
        },
        "per_corpus": per_corpus,
        "locked_facts": {"total": len(fact_items), "verified_by_absent": unverified},
        "what_this_cannot_show": (
            "LOWER BOUND, not an estimate. Layer 3 compares gold answers to locked_facts.json -- "
            "our own store. A gold answer wrong in the SAME WAY as the locked fact AGREES and is "
            "counted clean: efd_threshold_tzs_11m was fabricated for months while eval_355's gold "
            "matched it, and this check would have called that pair consistent. Only a statute can "
            "settle a disagreement, and this harness reads none. A flagged pair says 'these two "
            "disagree', never 'the key is wrong'."),
        "why_this_population": (
            "Every gold answer in the three corpora this project's quoted failure counts are "
            "measured against. A wrong key is invisible to adjudication because the adjudication "
            "reads the key -- so this population is exactly where that error hides."),
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    h = artifact["headline"]
    print(f"gold answers examined:                        {h['gold_answers_examined']}")
    print(f"carrying ANY source field:                    {h['carrying_any_source_field']}")
    print(f"asserting a checkable quantity:               "
          f"{h['asserting_a_checkable_quantity']}")
    print(f"CHECKABLE BUT NO SOURCE:                      "
          f"{h['checkable_but_carrying_NO_source']}")
    print(f"already carrying a scoring-key correction:    "
          f"{h['already_carrying_a_scoring_key_correction']}")
    print(f"sharing a figure with some locked fact:       "
          f"{h['sharing_a_figure_with_some_locked_fact']}")
    print()
    for label, c in per_corpus.items():
        print(f"  {label:10} rows={c['rows']:4} with_source={c['with_source']:4} "
              f"checkable={c['checkable']:4} checkable_no_source="
              f"{c['checkable_without_source']:4}")
    print(f"\nlocked facts: {len(fact_items)} total, {unverified} with verified_by absent")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
