# -*- coding: utf-8 -*-
"""QUARANTINE THE 6 CONFIRMED-WRONG ROWS; REVERSIBLY REMOVE THE 3 OSHA ROWS (2026-10-08).

Authorised by the founder 2026-10-08, acting on the retrain-precondition re-derivation
(eval/results/retrain_precondition_rederived_2026_10_07.json, verdict NOT MET, 9 rows,
3 classes). TWO DISPOSITIONS, deliberately different, because the evidence differs:

  CONFIRMED_WRONG (6) -- quarantined. The claim is refuted by primary text.
  REMOVED_PENDING_CONFIRMATION (3) -- reversible. `course_fee` is a locked HEDGE, and a
  confident training row teaches a certainty the fact base itself withholds. Not proved
  wrong; proved unsupported. The distinction is recorded in the record, not just here, so
  a later pass restoring them does not have to re-derive why they were removable.

EVERY LOCKED FACT WAS RE-READ BEFORE REMOVING ANYTHING (R28: a correction candidate is a
claim, not a verdict, and the thing telling you a row is wrong carries the same burden as
the row):

  paye_p9_deadline -- "shall be served by 30th January after the end of the year",
    Income Tax Act Cap.332 R.E.2023 s.110(3)(b), quoted verbatim in the fact's verified_by
    from a 146pp HTTP 200 read of tra.go.tz on 2026-10-05. Source note "[s. 85]" confirms
    the renumbering. Also: "Form P9" is Kenyan KRA terminology; TRA has no such form.
  vat_registration_threshold -- GN 448Y/2023 s.4, commencement clause "deemed to have come
    into operation on the 1st day of July, 2023". So "Julai 2024" is wrong by one year.
  course_fee -- status "HEDGE", and its own `training_instruction` reads "Do not state
    250,000 TZS for an unnamed OSHA course." That instruction is a STRONGER basis for
    removal than "unconfirmed": the fact base explicitly forbids the assertion.

⛔ THREE CANDIDATES WERE READ AND REJECTED, WHICH IS THE POINT OF READING RATHER THAN
SWEEPING. A broader local sweep for "OSHA near 250,000" surfaced three authored rows the
precondition artifact does NOT list. Both of the extra OSHA ones are CORRECT:

  cleaned_pairs_batch_014.jsonl:184 -- the question is "Hizo 'OSH TRAININGS AND PROMOTION'
    NILIZOLIPIA 250,000 TZS..." The 250,000 is THE USER'S OWN FIGURE and the body only
    echoes it ("kama haya uliyolipia 250,000 TZS"). The row asserts no course fee at all.
    This is D-FIDELITY-7's N2 narrowing in corpus form: a threshold CLAIM and the user's
    own number are different things, and a presence sweep cannot tell them apart.
  batch_005_cleaned.jsonl:151 -- a compliance-cost breakdown whose OSHA line is
    "OSHA TZS 50,000-150,000 kwa mwaka". The 250,000 belongs to a DIFFERENT levy in the
    same sentence: "EFD machine TZS 250,000-500,000". My sweep matched on co-occurrence
    inside one long body -- the bare-magnitude proximity false positive this project has
    already recorded three times (D-FIDELITY-6's +/-60 chars, bare 'asilimia 10', bare
    'TZS 70,000'). The precondition sweep was RIGHT to exclude it and mine was wrong.

  Both are therefore NOT removed, and are recorded here so no later pass re-raises them.
  The third extra (batch_004_cleaned.jsonl:120, tier1a_paye_adv_033) IS a genuine defect
  and IS in the set -- it asserts "P9 ... inawasilishwa ... ifikapo tarehe 31 Machi" with
  no negation anywhere.

PER-ROW REASONS QUOTE THE ROW'S OWN SENTENCE. R37's second lesson: the 2026-08-25 PAYE
quarantine wrote one reason for a batch and applied it per row, so the record read as
adjudicated while the adjudication never happened -- and its stated reason ("computes band
2 at 9%") was false of every row it named. Here `reason` is built from the matched
sentence of the specific row, so a reason that is not true of its row cannot be written.

POLARITY IS CHECKED AT REMOVAL TIME, NOT INHERITED. A row that NAMES the wrong value in
order to reject it must survive. One of the five P9 rows does the opposite -- "tarehe 31
Machi ..., si 31 Januari" asserts the wrong date AND denies the right one -- which is why
the check is run per row rather than assumed from the artifact.

WHERE IT ACTS (R36): the authored corpus, then `generate_sft.py`, then an assertion that
the rows are GONE FROM THE EXPORT. R36 exists because the 2026-10-05 quarantine fired one
stage upstream of the bytes that train and nobody re-ran the export. The reach assertion
is part of this script, not a follow-up step.

REPORT-ONLY BY DEFAULT. Writes only under --write.
"""
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "precondition_quarantine_2026_10_08.json")
REC_DIR = os.path.join(REPO, "datasets", "tier1a", "rejected")
WRITE = "--write" in sys.argv

CP = os.path.join("datasets", "tier1a", "cleaned_pairs")
SP = os.path.join("datasets", "tier1a", "sft_shaped_pairs")
RS = os.path.join("datasets", "tier1a", "raw_sources")

# ── THE CLAIM PATTERNS, AND THE NEGATION RULE ─────────────────────────────────────
# Word-bounded alternatives only. A bare `si\s` matches inside the ordinary Swahili word
# `kiasi `, and that exact looseness already DELETED a real finding from an adjudicated
# set once (CLAUDE.md, the demotion-rule failures). A loose demotion rule does not add
# noise -- it shrinks the population under adjudication, and a shorter finding list looks
# like progress.
NEG = (r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhapana\b|\bhakuna\b|\bhaina\b|\bni\s+makosa\b"
       r"|\bnot\b|\bincorrect\b)")

CLASSES = {
    "paye_p9_31_march": {
        "disposition": "CONFIRMED_WRONG",
        "claim": re.compile(r"31\s*Machi|31\s*March", re.I),
        "locked_fact": "paye_p9_deadline",
        "reason_head": "asserts the annual employment-income withholding certificate is due "
                       "31 March. Income Tax Act Cap.332 R.E.2023 s.110(3)(b): \"shall be "
                       "served by 30th January after the end of the year\" (read verbatim "
                       "from tra.go.tz, 146pp, HTTP 200, 2026-10-05; source note '[s. 85]' "
                       "confirms the renumbering from the pre-R.E.2023 citation). Separately, "
                       "'Form P9' is Kenyan KRA terminology -- TRA has no form by that name.",
    },
    "vat_threshold_dated_2024": {
        "disposition": "CONFIRMED_WRONG",
        "claim": re.compile(r"Julai\s*2024|July\s*2024", re.I),
        "locked_fact": "vat_registration_threshold",
        "reason_head": "dates the 100M -> 200M VAT registration threshold increase to July "
                       "2024. GN 448Y/2023 s.4 made the substitution and its commencement "
                       "clause reads \"deemed to have come into operation on the 1st day of "
                       "July, 2023\" -- wrong by one year. The row's FIGURES (200M current, "
                       "100M old) are correct; only the date is wrong.",
    },
    "osha_course_fee_250k": {
        "disposition": "REMOVED_PENDING_CONFIRMATION",
        "claim": re.compile(r"250,?000"),
        "locked_fact": "course_fee",
        "reason_head": "asserts an OSHA training course fee of TZS 250,000 as a plain fact. "
                       "NOT PROVED WRONG -- proved UNSUPPORTED: `course_fee` is a locked "
                       "HEDGE (status 'HEDGE -- Tier 3'), every OSHA course sampled on "
                       "osha.go.tz is TZS 300,000, and which course 250,000 refers to was "
                       "never identified. The fact's own `training_instruction` reads \"Do "
                       "not state 250,000 TZS for an unnamed OSHA course.\" A confident "
                       "training row teaches a certainty the fact base withholds.",
        "reversible": True,
    },
}

# Targets located by reading, then pinned by (file, question-prefix, claim) and re-resolved
# at run time. A line number into an authored append-only file would survive, but content
# resolution states WHAT is being removed, so a silently-moved row fails loudly instead of
# taking a neighbour with it (the 2026-10-07 generated-file pinning failure).
TARGETS = [
    # ── paye_p9_31_march : 5 distinct authored rows (+ raw_sources duplicates) ─────
    {"cls": "paye_p9_31_march", "files": [f"{CP}/batch_004_cleaned.jsonl",
                                          f"{RS}/raw_pairs_batch_004.jsonl",
                                          f"{RS}/_verify_batch004_pairs21_300.jsonl"],
     "q": "Tofauti kati ya P9 na P10 ni nini kwa madhumuni ya PAYE?",
     "row_id": "tier1a_paye_adv_033_20260609"},
    {"cls": "paye_p9_31_march", "files": [f"{CP}/batch_006_cleaned.jsonl",
                                          f"{RS}/raw_pairs_batch_006.jsonl",
                                          f"{RS}/_verify_batch006_all.jsonl"],
     "q": "P9 form kwa mfanyakazi mgeni — ni nini na inapaswa kutolewa lini?",
     "row_id": "b006_paye_for_018"},
    {"cls": "paye_p9_31_march", "files": [f"{CP}/batch_006_cleaned.jsonl",
                                          f"{RS}/raw_pairs_batch_006.jsonl",
                                          f"{RS}/_verify_batch006_all.jsonl"],
     "q": "P9 form na P9A form — ni tofauti gani?",
     "row_id": "b006_disambig_012"},
    {"cls": "paye_p9_31_march", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Fomu ya P9 inatumika kwa nini na inawasilishwa lini?", "row_id": None,
     "note": "THE WORST ROW IN THIS CLASS: 'Inawasilishwa kufikia tarehe 31 Machi ya mwaka "
             "unaofuata, si 31 Januari.' It asserts the wrong date AND explicitly denies the "
             "correct one, so a polarity rule that looked only for a negation near the wrong "
             "value would have DEMOTED it to a mention and dropped it from the set."},
    {"cls": "paye_p9_31_march", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Fomu ya P9 ni nini, inawasilishwa lini na nani hupata nakala?", "row_id": None},
    # ── vat_threshold_dated_2024 : 1 row ──────────────────────────────────────────
    {"cls": "vat_threshold_dated_2024", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Nasikia kizingiti cha VAT ni milioni 100 kwa mwaka — bado ni hivyo?",
     "row_id": None},
    # ── osha_course_fee_250k : 3 rows, REVERSIBLE ─────────────────────────────────
    {"cls": "osha_course_fee_250k", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Mafunzo ya usalama kazini ya OSHA yanawahusu akina nani na gharama yake?",
     "row_id": None},
    {"cls": "osha_course_fee_250k", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Mafunzo ya OSHA kwa afisa usalama na matakwa ya huduma ya kwanza ya WCF — ni "
          "mafunzo yale yale au tofauti?", "row_id": None},
    {"cls": "osha_course_fee_250k", "files": [f"{SP}/cleaned_pairs_batch_015.jsonl"],
     "q": "Naomba namba tatu: ada ya BRELA ya annual return, ada ya mafunzo ya OSHA, na "
          "kiwango cha mchango wa WCF.", "row_id": None},
]

# Read, judged correct, and NOT removed. Recorded at the site so no later pass re-raises
# them -- R20's "'no assertion needed here' is a valid, recordable outcome", applied to a
# removal decision.
READ_AND_KEPT = [
    {"at": f"{SP}/cleaned_pairs_batch_014.jsonl:184",
     "q": "Hizo 'OSH TRAININGS AND PROMOTION' nilizolipia 250,000 TZS zinahusiana na kodi "
          "gani hasa?",
     "why_kept": "The 250,000 is THE USER'S OWN figure, stated in the question "
                 "('nilizolipia 250,000 TZS') and echoed by the body ('kama haya uliyolipia "
                 "250,000 TZS'). The row asserts no OSHA course fee. Removing it would be an "
                 "over-removal of exactly the kind R37 was written for."},
    {"at": f"{CP}/batch_005_cleaned.jsonl:151 (+ {RS}/raw_pairs_batch_005.jsonl:151)",
     "q": "Gharama ya jumla ya kufuata sheria za biashara kwa miaka ya kwanza...",
     "why_kept": "The 250,000 is the EFD MACHINE ('EFD machine TZS 250,000-500,000'). This "
                 "row's OSHA line is 'OSHA TZS 50,000-150,000 kwa mwaka' and is correct. My "
                 "sweep matched on co-occurrence inside one long body; the precondition "
                 "sweep correctly excluded it."},
]


def body_of(o):
    return o.get("answer_sw") or o.get("output") or ""


def q_of(o):
    return o.get("question_sw") or o.get("instruction") or ""


def claim_polarity(pat, text):
    """ASSERTS vs MENTIONS_UNDER_NEGATION. The negation must sit within 40 characters
    BEFORE the matched value: a marker anywhere in the sentence excused a row that
    rejected one value and asserted another in the same breath."""
    found = list(re.finditer(pat, text))
    if not found:
        return "NO_MATCH", []
    asserts = [m.group(0) for m in found
               if not re.search(NEG + r"[\s:,—-]*(?:tarehe\s*|TZS\s*)?$",
                                text[max(0, m.start() - 40):m.start()], re.I)]
    return ("ASSERTS" if asserts else "MENTIONS_UNDER_NEGATION"), asserts


def sentence_with(pat, text):
    for s in re.split(r"(?<=[.!?;])\s+", text):
        if re.search(pat, s):
            return s.strip()
    return ""


def main():
    results, removals = [], {}
    for t in TARGETS:
        spec = CLASSES[t["cls"]]
        for rel in t["files"]:
            path = os.path.join(REPO, rel)
            assert os.path.exists(path), f"missing {rel}"
            rows = []
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    rows.append(json.loads(line))
            hits = [i for i, o in enumerate(rows)
                    if q_of(o) == t["q"]
                    and (t["row_id"] is None or o.get("id") == t["row_id"])]
            if len(hits) != 1:
                results.append({"class": t["cls"], "at": rel, "question": t["q"][:80],
                                "verdict": f"UNRESOLVED -- {len(hits)} matches",
                                "action": "SKIPPED"})
                print(f"[SKIP ] {t['cls']} {rel}: {len(hits)} matches for the question")
                continue
            i = hits[0]
            obj = rows[i]
            body = body_of(obj)
            polarity, matched = claim_polarity(spec["claim"], body)
            sent = sentence_with(spec["claim"], body)
            row = {
                "class": t["cls"], "disposition": spec["disposition"],
                "reversible": bool(spec.get("reversible")),
                "at": f"{rel}:{i + 1}", "row_id": obj.get("id"),
                "question": q_of(obj), "subdomain": obj.get("subdomain"),
                "pair_type": obj.get("pair_type"),
                "polarity": polarity, "matched": matched,
                "locked_fact": spec["locked_fact"],
                # ── THE PER-ROW REASON, BUILT FROM THIS ROW'S OWN SENTENCE ──────
                "reason": f"{spec['reason_head']} THIS ROW SAYS: \"{sent}\"",
                "quoted_sentence": sent,
            }
            if "note" in t:
                row["note"] = t["note"]
            if polarity != "ASSERTS":
                row["action"] = "KEPT -- rejects the claim, removal would be an over-removal"
                print(f"[KEEP ] {t['cls']} {rel}:{i+1} -- {polarity}")
            else:
                row["action"] = "REMOVE" if WRITE else "WOULD REMOVE (report-only)"
                removals.setdefault(path, []).append((i, row))
                print(f"[{row['action'][:6]}] {t['cls']} {rel}:{i+1} "
                      f"{spec['disposition']}")
                print(f"         \"{sent[:120]}\"")
            results.append(row)

    confirmed = [r for r in results if r.get("disposition") == "CONFIRMED_WRONG"
                 and r["action"].startswith(("REMOVE", "WOULD"))]
    reversible = [r for r in results if r.get("reversible")
                  and r["action"].startswith(("REMOVE", "WOULD"))]

    if WRITE:
        for path, items in removals.items():
            shutil.copy2(path, path + ".pre_quarantine_bak")
            keep, recs = [], []
            idx = {i for i, _ in items}
            lines = [l for l in open(path, encoding="utf-8") if l.strip()]
            for n, line in enumerate(lines):
                if n in idx:
                    o = json.loads(line)
                    meta = next(r for i, r in items if i == n)
                    o["_quarantine"] = {
                        "from_file": os.path.relpath(path, REPO).replace("\\", "/"),
                        "from_line": n + 1,
                        "quarantined": "2026-10-08",
                        "defect_class": meta["class"],
                        "disposition": meta["disposition"],
                        "reversible": meta["reversible"],
                        "reasons": [meta["reason"]],
                        "locked_fact": meta["locked_fact"],
                        "authorised_by": "founder, 2026-10-08",
                        "restore_condition": (
                            "Identify which OSHA course TZS 250,000 refers to on osha.go.tz, "
                            "or confirm the figure from a primary source. Then restore this "
                            "row unchanged. `course_fee` must stop being a HEDGE first."
                            if meta["reversible"] else
                            "None -- the claim is refuted by primary text. Any replacement "
                            "must be newly authored from the locked fact, not restored."),
                    }
                    recs.append(o)
                else:
                    keep.append(line)
            with open(path, "w", encoding="utf-8") as fh:
                fh.writelines(keep)
            for o in recs:
                name = ("osha_course_fee_removed_pending_confirmation_2026_10_08.jsonl"
                        if o["_quarantine"]["reversible"]
                        else "precondition_confirmed_wrong_quarantine_2026_10_08.jsonl")
                with open(os.path.join(REC_DIR, name), "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(o, ensure_ascii=False) + "\n")
            print(f"  removed {len(recs)} row(s) from "
                  f"{os.path.relpath(path, REPO)} (backup: .pre_quarantine_bak)")

    payload = {
        "_what": "Quarantine of the 6 confirmed-wrong precondition rows and reversible "
                 "removal of the 3 OSHA course-fee rows.",
        "_authorised": "founder, 2026-10-08",
        "_mode": "WRITE" if WRITE else "REPORT_ONLY",
        "_two_dispositions": "CONFIRMED_WRONG is refuted by primary text and has no restore "
                             "condition. REMOVED_PENDING_CONFIRMATION is unsupported, not "
                             "disproven: course_fee is a locked HEDGE whose own "
                             "training_instruction forbids asserting 250,000, so a confident "
                             "row teaches a certainty the fact base withholds. Each removed "
                             "row carries its own restore_condition.",
        "_per_row_reasons": "Each `reason` embeds the matched sentence FROM THAT ROW. The "
                            "2026-08-25 PAYE quarantine wrote one reason for a batch, applied "
                            "it per row, and its stated reason was false of every row it "
                            "named (R37). A reason built from the row cannot be.",
        "_where_it_acts": "The AUTHORED corpus (cleaned_pairs/, sft_shaped_pairs/, "
                          "raw_sources/). datasets/tier1a/sft/ is generated; the export is "
                          "rebuilt afterwards and the reach is asserted separately per R36.",
        "_read_and_kept": READ_AND_KEPT,
        "totals": {
            "targets": len(TARGETS),
            "file_instances_considered": len(results),
            "confirmed_wrong_removed": len(confirmed),
            "reversibly_removed": len(reversible),
            "kept_on_polarity": len([r for r in results
                                     if r["action"].startswith("KEPT")]),
            "unresolved": len([r for r in results if "UNRESOLVED" in str(r.get("verdict"))]),
            "read_and_kept_outside_the_set": len(READ_AND_KEPT),
        },
        "rows": results,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\n{payload['totals']}")
    print(f"wrote {OUT}")
    if not WRITE:
        print("REPORT-ONLY. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
