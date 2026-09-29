# -*- coding: utf-8 -*-
"""HOW MANY CURRENTLY-PASSING STORED REPLIES ATTACH A RATE TO THE WRONG LEVY?

THE QUESTION, and it is the right one to ask. If a reply can carry a CORRECT rate attached to the
WRONG levy, then every figure in it checks out individually and only the pairing is wrong -- so a
human adjudicating it, or any check that asks "is a wrong number present", passes it. If such rows
exist among replies already recorded as correct, the "currently correct" baseline on the 48 and the
78 is softer than it has been treated as.

THE INSTRUMENT IS THE RULE WE ALREADY HAVE, not a new one. chike.fidelity's D-FIDELITY-6
(`body_states_wrong_levy_rate`, shipped 2026-08-22) is exactly a per-levy rate-attribution check:
it holds the statutory rate set per levy, attributes each rate in the body to a levy
bidirectionally, and flags any pair the statute does not license. It was specified by nat_24 --
a body saying "10% ... kwa ajili ya WCF", where 10% is NSSF's CORRECT employer share attached to
the wrong levy. So correct-rate-wrong-levy is the case it was built for, and the measurement below
needs no new code. Writing a second rule to answer this would have measured the new rule, not the
phenomenon (R33).

WHAT IT WAS SWEPT OVER BEFORE, AND WHY THAT IS A DIFFERENT POPULATION (R22). The 2026-08-22 sweep
that priced this guard before it shipped covered 150 recorded replies and flagged 5, all true
positives. This sweeps EVERY stored reply artifact in eval/results/ -- a wider population -- and
crucially it JOINS each flag to that row's RECORDED VERDICT, which the original sweep did not do.
The original asked "does the guard false-positive?". This asks "does the guard flag rows we have
already booked as correct?" Those are different questions and only the second one can soften a
baseline.

WHAT THIS CANNOT SHOW.
  * It reads only the reply BODY. A reply that asserts no rate -- ext_55's bare "Ndiyo", ext_56's
    "Ndiyo, bado hujafika", ext_58's two clarification requests -- is invisible here, and those are
    inherited-claim failures that no body-reading rule can reach (recorded 2026-09-23: "a
    confirmation does not need to restate the thing it confirms").
  * It is silent on statutory constants stated without a levy nearby, and on a rate that is
    correct for the levy it names but wrong for the question asked.
  * A flag is a CANDIDATE, not a verdict. R26's second half governs: six of the first eight adverse
    verdicts in the 2026-08-24 control audit were bad specimens, and a false flag sends someone to
    "fix" a correct answer. Every flag below is printed with its attributed pairs so it can be read
    individually before anything is done with it.

R18: committed before the write-up that cites it.
Artifact: eval/results/rate_attribution_all_stored_2026_09_29.json

Usage:  python eval/fidelity/sweep_rate_attribution_all_stored.py
Exit 0 always -- this is a measurement, not a gate.
"""
import collections
import glob
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "rate_attribution_all_stored_2026_09_29.json")
ADJ = os.path.join(REPO, "eval", "results", "extended_078_adjudication_2026_09_23.json")

from chike.fidelity import (attributed_levy_rates,                  # noqa: E402
                            body_states_wrong_levy_rate)

REPLY_KEYS = ("reply", "text", "raw_text", "body", "answer", "model_reply", "response")
# `ok`/`pass`/`result` are DELIBERATELY ABSENT. The first run read them and reported 5 rows as
# "previously recorded correct"; four were rg_13-rg_16 from the guard's OWN probe fixture, where
# the boolean means "this probe behaved as designed" and the design is TO BE FLAGGED. R26's second
# half: a control that does not fire needs its specimen eliminated first, and here the specimen
# inverted the meaning of the field. Reported unchecked it would have claimed a 5-row baseline
# softening, of which 4 were the guard working perfectly.
VERDICT_KEYS = ("verdict", "judgement", "grade")
# Files whose rows are PROBES designed to be flagged. A flag here is the instrument working.
PROBE_FIXTURES = ("rate_guard_sweep.json", "threshold_guard_probes.json",
                  "regen_guards_local_dryrun.json")


def walk(node, depth=0):
    """Yield every dict that looks like a recorded reply, at any nesting depth."""
    if depth > 4:
        return
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and any(
                    isinstance(item.get(k), str) and item[k].strip() for k in REPLY_KEYS):
                yield item
            else:
                yield from walk(item, depth + 1)
    elif isinstance(node, dict):
        for value in node.values():
            yield from walk(value, depth + 1)


def main():
    # Recorded verdicts for the 78, so a flag can be joined to whether we booked the row correct.
    adj = {r["id"]: r for r in json.load(open(ADJ, encoding="utf-8"))["rows"]}

    seen, rows = set(), []
    for path in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        if os.path.basename(path) == os.path.basename(OUT):
            continue
        try:
            blob = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for item in walk(blob):
            body = next((item[k] for k in REPLY_KEYS
                         if isinstance(item.get(k), str) and item[k].strip()), "")
            rid = str(item.get("id") or item.get("qid") or item.get("probe") or "?")
            fingerprint = (rid, body[:120])
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            is_probe = os.path.basename(rel) in PROBE_FIXTURES
            pairs = [(lv, str(rt)) for lv, rt in attributed_levy_rates(body)]
            flagged = body_states_wrong_levy_rate(body)
            recorded = None
            if rid in adj:
                recorded = adj[rid].get("verdict")
            elif any(isinstance(item.get(k), (str, bool)) for k in VERDICT_KEYS):
                recorded = str(next(item[k] for k in VERDICT_KEYS
                                    if isinstance(item.get(k), (str, bool))))
            rows.append({"id": rid, "file": rel, "flagged": flagged,
                         "is_probe_designed_to_flag": is_probe,
                         "attributed_pairs": pairs, "recorded_verdict": recorded,
                         "body": body[:600]})

    # R20: a walker that finds nothing reports zero flags, indistinguishable from a clean result.
    assert len(rows) > 200, (
        f"only {len(rows)} stored replies found -- the walker or REPLY_KEYS are wrong, and a "
        f"sweep over a handful of replies cannot answer a baseline question")
    assert any(r["attributed_pairs"] for r in rows), (
        "no reply anywhere attributed a rate to a levy -- attributed_levy_rates is not being "
        "exercised at all, so a zero-flag result would be vacuous")

    flagged = [r for r in rows if r["flagged"]]
    # The load-bearing subset: flagged AND we had booked the row as correct.
    passing_flagged = [r for r in flagged
                       if not r["is_probe_designed_to_flag"]
                       and str(r["recorded_verdict"]).upper() in
                       ("PASS", "PASS_BY_OUTCOME", "CORRECT")]
    with_pairs = [r for r in rows if r["attributed_pairs"]]

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/fidelity/sweep_rate_attribution_all_stored.py",
        "instrument": ("chike.fidelity.body_states_wrong_levy_rate -- D-FIDELITY-6, shipped "
                       "2026-08-22, specified by nat_24 (NSSF's correct 10% attached to WCF). "
                       "No new rule was written for this measurement."),
        "question": ("How many stored replies attach a rate to a levy the statute does not give "
                     "it, and how many of those had already been recorded as correct?"),
        "why_this_population": (
            "Every stored reply artifact in eval/results/, joined to the extended-078 "
            "adjudication verdicts. The 2026-08-22 pricing sweep covered 150 replies and asked "
            "whether the guard false-positives; this asks whether it flags rows already booked "
            "correct, which is the only question that can soften a baseline (R22)."),
        "what_it_cannot_show": (
            "Replies that assert no rate at all are invisible -- ext_55's bare 'Ndiyo', ext_56's "
            "'Ndiyo, bado hujafika', ext_58's two clarification requests. Those are "
            "inherited-claim failures no body-reading rule can reach. A flag is a candidate, "
            "not a verdict (R26)."),
        "totals": {
            "stored_replies_swept": len(rows),
            "replies_attributing_any_rate_to_a_levy": len(with_pairs),
            "flagged_wrong_pairing": len(flagged),
            "flagged_and_previously_recorded_correct": len(passing_flagged),
            "by_file": dict(collections.Counter(r["file"] for r in flagged)),
        },
        "flagged": flagged,
        "flagged_and_previously_recorded_correct": passing_flagged,
        "the_staging_finding": {
            "row": "N2_ordinary_compute, eval/results/r16_deploy_verification_2026_09_24.json",
            "live_reply": ("Kwa wafanyakazi 10, unalipa asilimia 0.5 ya jumla ya mishahara. "
                           "Thibitisha na tra.go.tz. [newline] "
                           "SDL = 3.5% x TZS 5,000,000 = TZS 175,000"),
            "why_the_guard_missed_it": (
                "D-FIDELITY-6 IS wired in production (chike/orchestrator.py:818, pipeline=v16) "
                "and it FIRES on this text -- but it is handed `cleaned`, the MODEL BODY, and "
                "_render appends the engine's working AFTERWARDS. Measured: body alone -> 0 "
                "attributed pairs, flag False. Full rendered reply -> [('sdl','0.5'), "
                "('sdl','3.5')], flag True. The body states a bare rate with NO levy token, so "
                "it is unattributable in isolation; the levy name arrives from the engine's own "
                "working line, and nothing re-checks the concatenation."),
            "class": ("A FIFTH R26 shape, distinct from the four on record. Not INERT, not "
                      "NOT_WIRED, not OVERBROAD, not a bad fixture: the control is correct, "
                      "wired, and firing, and is CHECKED AT THE WRONG STAGE. The contradiction "
                      "does not exist in either half and is created by joining them."),
            "why_the_harness_recorded_PASS": (
                "r16_deploy_verification's must_contain was ['175,000'], which is present. A "
                "substring check cannot see a contradiction beside the substring it wants -- "
                "R23's shape: the control's expected value was satisfied by a reply carrying the "
                "defect."),
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    t = artifact["totals"]
    print(f"stored replies swept:                        {t['stored_replies_swept']}")
    print(f"replies attributing a rate to a levy:        "
          f"{t['replies_attributing_any_rate_to_a_levy']}")
    print(f"FLAGGED wrong rate/levy pairing:             {t['flagged_wrong_pairing']}")
    print(f"  of which previously recorded CORRECT:      "
          f"{t['flagged_and_previously_recorded_correct']}")
    print()
    for r in flagged:
        print(f"  [{str(r['recorded_verdict']):>10}] {r['id']:14} {r['attributed_pairs']}")
        print(f"      {os.path.basename(r['file'])}")
        print(f"      {r['body'][:190]}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
