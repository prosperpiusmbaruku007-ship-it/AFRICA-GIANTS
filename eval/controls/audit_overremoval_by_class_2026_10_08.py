# -*- coding: utf-8 -*-
"""OVER-REMOVAL AUDIT ACROSS EVERY QUARANTINE CLASS (R37), 2026-10-08.

THE QUESTION: of the rows our own quarantines removed, how many were CORRECT?

WHY THIS IS NOT THE 2026-10-07 AUDIT AGAIN. That audit's arm 3 read all 486 quarantined
rows and found 3 correct rows deleted, and it was right. But it inherits the
precondition classifier's 17 figure-testable classes, and its own caveat says so: "a
quarantined row whose defect class is NOT figure-testable produces no verdict and is
counted in neither column -- it is UNEXAMINED, NOT CLEARED." Nobody had measured how big
that population is. THAT NUMBER IS THE POINT OF THIS FILE.

So this harness reports, per quarantine record:
  * rows removed
  * rows the classifier can reach at all (VERDICT-BEARING)
  * of those, how many ASSERT the defect (removal correct) vs REJECT it (over-removal)
  * rows with NO VERDICT -- the unexamined population, sampled for reading by hand

⛔ THE ASYMMETRY THAT DECIDES HOW THIS IS REPORTED (R26's second half, inverted). For a
DEFECT hunt, a false positive is the expensive error because only false positives generate
edits. For an OVER-REMOVAL hunt the asymmetry FLIPS: a false "this removal was fine"
leaves correct data deleted forever, and an over-removal destroys its own evidence -- the
row is gone, the count went down, and the write-up reads as progress. So a NO_VERDICT row
is reported as UNEXAMINED and never folded into a "removals were correct" total. A clean
number here would be the least trustworthy possible result.

AND THE SAMPLING IS NOT RANDOM, DELIBERATELY. R37 names the highest-risk population:
`pair_type: adversarial` / `subdomain: *_adversarial`, because containing the wrong value
is their entire purpose -- that is how the two PAYE rows were lost. Those are enumerated
in FULL rather than sampled. Random sampling of a population whose risk is concentrated in
a known, labelled subset would be measuring the cheap part.

REPORT-ONLY. This harness reads; it never edits a corpus.
"""
import collections
import importlib.util
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "overremoval_by_class_2026_10_08.json")
REJ = os.path.join(REPO, "datasets", "tier1a", "rejected")
SAMPLE_PER_CLASS = int(os.environ.get("SAMPLE_PER_CLASS", "4"))


def _load_classifier():
    """IMPORTED, never re-implemented. The 2026-10-06 dry run passed a package the real run
    refused because it re-wrote the checks its author remembered. A second copy of a
    polarity rule is the same mistake: four of this project's demotion-rule failures were
    found only by re-running the one real instrument."""
    p = os.path.join(REPO, "eval", "controls",
                     "rederive_retrain_precondition_2026_10_07.py")
    spec = importlib.util.spec_from_file_location("precond", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["precond"] = mod
    cwd = os.getcwd()
    try:
        os.chdir(REPO)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    assert hasattr(mod, "classify"), "classifier API moved"
    assert len(mod.CLASSES) >= 16, f"class list shrank to {len(mod.CLASSES)}"
    assert len(mod.NOT_FIGURE_TESTABLE) >= 4, "the not-figure-testable list shrank"
    return mod


PRE = _load_classifier()

BODY_KEYS = ("output", "answer_sw", "response")
QKEYS = ("instruction", "question_sw", "question")


def body_of(o):
    for k in BODY_KEYS:
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return body_of(o["row"])
    return ""


def q_of(o):
    for k in QKEYS:
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return q_of(o["row"])
    return ""


def meta_of(o):
    """subdomain/pair_type/id can sit on the row or on a nested `row` key -- four quarantine
    records use the nested shape, and the first draft of the reach audit reported `0/0` for
    exactly those, which reads identically to clean."""
    src = o["row"] if isinstance(o.get("row"), dict) else o
    return {"id": src.get("id"), "subdomain": src.get("subdomain"),
            "pair_type": src.get("pair_type")}


IS_ADVERSARIAL = re.compile(r"adversarial", re.I)

# The three bodies restored on 2026-10-08, matched on their own distinctive text. Keyed by
# CONTENT, not by record line: the same body occupies several record lines (7 for the two
# PAYE rows, 2 for the VAT row), which is why 3 restorations clear 9 over-removal lines.
RESTORED = re.compile(
    r"Bendi tano za PAYE Tanzania 2025/2026: \(1\) TZS 0 hadi 270,000"
    r"|Bendi TANO za PAYE Tanzania 2025/2026 — sahihi kamili"
    r"|kudai kiasi kilichozuiliwa kama input credit")

# ── HAND ADJUDICATIONS OF THE UNEXAMINED SAMPLES, 2026-10-08 ─────────────────────
# Read by hand because no instrument in this repo can judge them. Each verdict names the
# primary-sourced fact it rests on, so a later reader can check the adjudication rather
# than inherit it -- which is the whole complaint R18 makes about uncommitted results.
#
# ⛔ A THIRD CATEGORY HAD TO BE ADDED, AND IT IS A FINDING ABOUT THE QUESTION ITSELF.
# "How many removed rows were correct?" presumes correctness was the removal criterion.
# For `eval_contaminated.jsonl` it was not: those rows were removed under R6 to keep the
# train/eval split, and they are CORRECT. Counting them as over-removals would be wrong;
# counting them as correctly-removed-because-wrong would also be wrong. They are
# CORRECT_AND_CORRECTLY_REMOVED, and 9 of the 501 are in that state.
ADJUDICATIONS = [
    {"record": "eval_contaminated.jsonl", "rows_covered": 9,
     "verdict": "CORRECT_AND_CORRECTLY_REMOVED",
     "basis": "Removed under R6 (training/eval contamination), NOT for being wrong, and the "
              "record carries no `reasons` field at all. Spot-read 4: two correct "
              "out-of-corpus refusals; one PAYE computation on TZS 800,000 that is exactly "
              "right against the locked bands (0 + 20,000 + 48,000 + 10,000 = 78,000); one "
              "GN 605A row stating 33.4%, which CLAUDE.md s.11 confirms. Correctness was "
              "never the criterion here, so this record cannot answer the over-removal "
              "question in either direction."},
    {"record": "sdl_tourism_levy_mislabeled.jsonl", "rows_covered": 3,
     "verdict": "REMOVAL_CORRECT",
     "basis": "All three assert a 'tourism development levy' of 1% under subdomain "
              "`sdl_compliance`. No such levy is a locked fact and the rate is not SDL's "
              "3.5%; row 2 goes further and computes 1% x TZS 50,000,000 = 500,000 "
              "confidently. A fabricated levy with a confident worked example. BUT the "
              "record's `reasons` is None -- the only statement of why these went is the "
              "FILENAME, which is not checkable against any row."},
    {"record": "vat_deferment_stale_cutoff_framing_quarantine_2026_09_02.jsonl",
     "rows_covered": 11, "verdict": "REMOVAL_CORRECT",
     "basis": "R32's shape: the DATE is right and the TENSE is wrong. Rows frame 30 June "
              "2026 as an upcoming deadline ('inaruhusiwa HADI', 'unaisha lini') and that "
              "date has now passed. The locked fact's own text reads 'This is now a PAST "
              "cutoff, not an upcoming deadline' (FA2023 s.65(b)). `reasons` is None here "
              "too."},
    {"record": "presumptive_stale_ceiling_rate_quarantine_2026_09_01.jsonl",
     "rows_covered": 5, "verdict": "REMOVAL_CORRECT",
     "basis": "Sampled rows state the ceiling as TZS 100,000,000 and the top-band rate as "
              "3.5%. FA2026 s.27(a)(ii) substituted the band: 11,000,001-200,000,000 at "
              "4.0% of turnover. One row is stale on both limbs at once ('milioni 11 hadi "
              "milioni 100 ... asilimia 3.5')."},
    {"record": "rent_wht_nonresident_15pct_quarantine_2026_09_26.jsonl",
     "rows_covered": 8, "verdict": "REMOVAL_CORRECT -- but the record is misnamed",
     "basis": "`rent_wht_rate` is 10% for residents AND non-residents, a SINGLE rate with no "
              "residency split (Cap.332 R.E.2023 First Schedule para 4(b)(ii), verbatim, "
              "cross-checked against tra.go.tz's '10% | 10%' table). The sampled rows assert "
              "'kodi ya pango 10%/20%' and 'wasio wakazi ... kodi ya pango 20%' -- both wrong, "
              "both asserting the split the fact denies. NOTE: the record is named for a 15% "
              "defect and these rows say 20%, so the quarantine caught MORE than its name "
              "claims. Good for the corpus, bad for the record: with `reasons` None, nothing "
              "states what was actually wrong with these particular rows."},
    {"record": "dse_stale_float_quarantine_2026_09_01.jsonl", "rows_covered": 3,
     "verdict": "REMOVAL_CORRECT",
     "basis": "tier1a_income_tax_adv_051 asserts the DSE-listed 25% rate requires 'angalau "
              "asilimia 30 ya hisa zao kwa umma'. FA2025 s.60(d)(i) lowered that public-float "
              "condition to 25% WEF 1 July 2025 (quoted verbatim in the record, and CLAUDE.md "
              "records the 30%->25% change independently). The row's other limbs (30% "
              "standard, 25% for listed) are correct, but the float condition is the "
              "operative qualifier, so removal rather than repair was defensible."},
    # ⛔ THE ONE GENUINELY MIXED CLASS, AND THE PATTERN IS WORTH MORE THAN THE COUNT.
    {"record": "tier2_confirmed_wrong_quarantine_2026_08_31.jsonl (stamp-duty limb)",
     "rows_covered": 4, "verdict": "MIXED -- 2 correct removals, 2 WEAK",
     "basis": "One reason -- 'asserts a flat 1% stamp duty ... Cap.189 Art.22(b) sets a TIERED "
              "rate' -- was applied to two DIFFERENT kinds of row. It is true of "
              "stamp_duty_101 and stamp_duty_108, which explicitly DENY tiering ('hakuna "
              "mfumo wa ngazi (tiered) wa 0.5% na 1%'). It is NOT really true of "
              "stamp_duty_122, whose job is refuting a 2% claim and which is RIGHT that the "
              "rate is not 2% -- 'BAPA' is an incidental adjective in an otherwise correct "
              "answer; nor of stamp_duty_138, whose subject is first-time-buyer relief (there "
              "is none in Tanzania -- correct) and which mentions 1% only in passing. Those "
              "two were removable by repair (strike one word) rather than deletion. Not "
              "scored as over-removals, because the word IS wrong; recorded as the same "
              "batch-reason-applied-per-row shape R37 was written for, one degree milder.",
     "consequence": "Stamp duty is in NOT_FIGURE_TESTABLE precisely because 1% is lawful and "
                    "the defect is SCOPE (R19's Guard B line). That is exactly why no "
                    "instrument caught the difference between these two kinds of row, and why "
                    "148 unexamined rows in this one record is the largest blind spot found."},
    {"record": "tier2_confirmed_wrong_quarantine_2026_08_31.jsonl (GN487A limb)",
     "rows_covered": 2, "verdict": "REMOVAL_CORRECT",
     "basis": "Reason: GN487A s.3(3)(a) makes visa/permit revocation MANDATORY on conviction "
              "('shall be liable to ... AND revocation'), not discretionary. The sampled row "
              "says 'kufutwa kwa visa ... KUNAWEZA kutokea' -- the discretionary framing the "
              "reason names. Checkable against the row, unlike the stamp-duty limb."},
]


def main():
    records = sorted(f for f in os.listdir(REJ) if f.endswith(".jsonl"))
    assert records, "no quarantine records found -- a census that reads nothing reports clean"
    per_record, all_rows = [], []

    for name in records:
        path = os.path.join(REJ, name)
        rows = []
        for ln, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                rows.append((ln, json.loads(line)))
            except Exception:
                continue

        asserts, rejects, noverdict, adversarial = [], [], [], []
        for ln, o in rows:
            b, q = body_of(o), q_of(o)
            m = meta_of(o)
            qn = o.get("_quarantine") or {}
            entry = {
                "record": name, "line": ln, "id": m["id"],
                "subdomain": m["subdomain"], "pair_type": m["pair_type"],
                "question": q[:150], "body": b[:400],
                "stated_reason": (qn.get("reasons") or [None])[0],
                "declared_class": qn.get("defect_class"),
                "disposition": qn.get("disposition"),
            }
            if not b:
                entry["verdict"] = "NO_BODY"
                noverdict.append(entry)
                all_rows.append(entry)
                continue
            verdicts = PRE.classify(q, b)
            entry["classifier"] = {c: v for c, v, _ in verdicts}
            if not verdicts:
                entry["verdict"] = "NO_VERDICT"
                noverdict.append(entry)
            elif any(v == "ASSERTS" for _, v, _ in verdicts):
                entry["verdict"] = "ASSERTS -- removal correct"
                asserts.append(entry)
            else:
                entry["verdict"] = "REJECTS -- OVER-REMOVAL"
                # A quarantine record is an append-only audit trail: restoring the row does
                # NOT delete the record line, and it should not -- the record of a wrong
                # removal is the only evidence the removal happened. So the over-removal
                # count stays at 9 permanently, and without this marker a later reader would
                # read 9 rows as still missing when they are live again.
                entry["restored_on"] = ("2026-10-08 -- "
                                        "eval/controls/restore_overremoved_rows_2026_10_08.py"
                                        if RESTORED.search(b) else None)
                rejects.append(entry)
            if (IS_ADVERSARIAL.search(m["subdomain"] or "")
                    or IS_ADVERSARIAL.search(m["pair_type"] or "")):
                adversarial.append(entry)
            all_rows.append(entry)

        per_record.append({
            "record": name,
            "rows": len(rows),
            "verdict_bearing": len(asserts) + len(rejects),
            "asserts_removal_correct": len(asserts),
            "rejects_OVER_REMOVAL": len(rejects),
            "no_verdict_UNEXAMINED": len(noverdict),
            "coverage_pct": (round(100.0 * (len(asserts) + len(rejects)) / len(rows), 1)
                             if rows else None),
            "adversarial_population": len(adversarial),
            "over_removals": rejects,
            # Non-random: the highest-risk labelled subset in full, then a head sample of
            # the rest. A head sample is deterministic and therefore re-derivable, which
            # random sampling without a committed seed is not (R18).
            "unexamined_sample": ([e for e in noverdict
                                   if IS_ADVERSARIAL.search(e["subdomain"] or "")
                                   or IS_ADVERSARIAL.search(e["pair_type"] or "")]
                                  + [e for e in noverdict
                                     if not (IS_ADVERSARIAL.search(e["subdomain"] or "")
                                             or IS_ADVERSARIAL.search(
                                                 e["pair_type"] or ""))][:SAMPLE_PER_CLASS]),
        })

    tot = collections.Counter()
    for r in per_record:
        for k in ("rows", "verdict_bearing", "asserts_removal_correct",
                  "rejects_OVER_REMOVAL", "no_verdict_UNEXAMINED",
                  "adversarial_population"):
            tot[k] += r[k]

    adv_all = [e for e in all_rows
               if IS_ADVERSARIAL.search(e.get("subdomain") or "")
               or IS_ADVERSARIAL.search(e.get("pair_type") or "")]
    adv_over = [e for e in adv_all if "OVER-REMOVAL" in e["verdict"]]
    adv_unex = [e for e in adv_all if e["verdict"] in ("NO_VERDICT", "NO_BODY")]

    payload = {
        "_what": "Over-removal audit across every quarantine class: of the rows our "
                 "quarantines removed, how many were correct?",
        "_why_not_the_same_as_2026_10_07": "That audit's arm 3 read all 486 rows and found 3 "
                                           "over-removals, correctly. It inherits the "
                                           "precondition classifier's figure-testable classes, "
                                           "and its own caveat calls the remainder UNEXAMINED, "
                                           "NOT CLEARED. Nobody had measured how large that "
                                           "remainder is. This file measures it per record.",
        "_the_asymmetry_flips": "For a DEFECT hunt a false positive is the expensive error, "
                                "because only false positives generate edits. For an "
                                "OVER-REMOVAL hunt a false 'that removal was fine' leaves "
                                "correct data deleted forever, and the removal destroyed its "
                                "own evidence. So NO_VERDICT is reported as UNEXAMINED and is "
                                "NEVER folded into a 'removals were correct' total.",
        "_sampling_is_not_random": "R37 names the highest-risk population: adversarial pairs, "
                                   "where containing the wrong value IS the design. Those are "
                                   "enumerated in FULL, not sampled. The rest get a "
                                   "deterministic head sample (re-derivable; random without a "
                                   "committed seed is not, per R18).",
        "_what_this_cannot_show": "A NO_VERDICT row is not a cleared row and not a defect -- it "
                                  "is a row no instrument in this repo can judge. Reading the "
                                  "samples is the only way to convert it, and reading is not "
                                  "automatable here: the four NOT_FIGURE_TESTABLE classes are "
                                  "scope (stamp duty's flat-1%), structure (the WCF 14+7 "
                                  "chain), terminology (P45/P9), and a defect fixed by rewrite "
                                  "(nssf.or.tz) -- none has a figure to key on.",
        "_classifier": "eval/controls/rederive_retrain_precondition_2026_10_07.py, IMPORTED "
                       f"({len(PRE.CLASSES)} figure-testable classes, "
                       f"{len(PRE.NOT_FIGURE_TESTABLE)} explicitly not figure-testable)",
        "hand_adjudications_of_unexamined_samples": ADJUDICATIONS,
        "records_with_no_stated_reason_at_all": [
            "eval_contaminated.jsonl", "sdl_tourism_levy_mislabeled.jsonl",
            "vat_deferment_stale_cutoff_framing_quarantine_2026_09_02.jsonl",
            "rent_wht_nonresident_15pct_quarantine_2026_09_26.jsonl",
        ],
        "_records_with_no_stated_reason_why_it_matters":
            "R37's second lesson is that a quarantine's stated reason must be checkable "
            "against the row it names. FOUR records state no reason at all -- their only "
            "account of why rows went is the FILENAME, which cannot be checked against any "
            "row. That is strictly worse than the 2026-08-25 PAYE record, which at least "
            "wrote a reason that could be found false. Every removal here happened to be "
            "correct on reading; that is a fact about those rows, not about the practice.",
        "totals": dict(tot),
        "coverage_pct_overall": round(100.0 * tot["verdict_bearing"] / tot["rows"], 1),
        "adversarial_population_total": len(adv_all),
        "adversarial_over_removals": adv_over,
        "adversarial_unexamined": adv_unex,
        "per_quarantine_record": per_record,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"{'record':62s} {'rows':>5s} {'verd':>5s} {'OK':>4s} {'OVER':>5s} "
          f"{'UNEX':>5s} {'cov%':>6s}")
    for r in per_record:
        flag = " <-- OVER-REMOVAL" if r["rejects_OVER_REMOVAL"] else ""
        print(f"{r['record'][:62]:62s} {r['rows']:5d} {r['verdict_bearing']:5d} "
              f"{r['asserts_removal_correct']:4d} {r['rejects_OVER_REMOVAL']:5d} "
              f"{r['no_verdict_UNEXAMINED']:5d} {str(r['coverage_pct']):>6s}{flag}")
    print(f"\n{dict(tot)}")
    print(f"classifier coverage of the removed population: "
          f"{payload['coverage_pct_overall']}%")
    print(f"adversarial rows removed: {len(adv_all)} "
          f"(over-removals {len(adv_over)}, unexamined {len(adv_unex)})")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
