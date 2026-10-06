# -*- coding: utf-8 -*-
"""WHAT WOULD D-FIDELITY-7 BLANK, IF IT WERE WIRED TODAY?

THE QUESTION HAS TO BE ASKED BEFORE WIRING, NOT AFTER, because this guard's failure mode is
REMOVING TEXT. The ⛔ block above R17 in CLAUDE.md governs: a mechanism that fails by letting
something through is cheap to iterate on; one that fails by BLANKING a real user's answer is not,
because that cost lands on them and is invisible to us. `tg_08` passing in isolation says nothing
about prose the rule has never seen -- that is exactly R33 (a variant set validated against
variants of its own design measures the generator, not the phenomenon).

THE POPULATIONS, each named with WHY IT IS THE POPULATION THE DECISION APPLIES TO (R22):

  STORED_REPLY   every recorded model reply in eval/results/ -- the 48, the 78, every R16 live
                 verification, every A/B arm. This is the only population that is actual MODEL
                 PROSE, which is what the guard will be handed in production. It is also where
                 a flag can be joined to a RECORDED VERDICT, so "would it blank something we had
                 already booked correct?" is answerable rather than guessed.
  GOLD           `correct_answer_sw` from every eval/accuracy_gate + eval/refusal_gate corpus. A
                 human asserted each of these is RIGHT. A flag here is the strongest available
                 false-positive signal: either the guard is over-broad, or a gold answer is wrong
                 and the gate has been scoring against it.
  PAIRED         `answer_sw` / `output` from every cleaned_pairs and sft_shaped_pairs batch -- the
                 corpus the model was TRAINED on, so its prose style is the closest offline proxy
                 for what the model emits. A flag here is a candidate training defect as well as
                 a guard signal, and the two have to be told apart by reading.

WHAT A FLAG MEANS, AND IT IS NOT ONE THING -- the blanking decision depends on the PATH:

  compute path (sub.computation is not None): blanking is safe. `_render` still emits the engine's
      authoritative working, so the user loses a wrong sentence and keeps the right figure. This is
      where D-FIDELITY-1/3/4/5/6 live.
  fact path (sub.computation is None): BLANKING IS SILENCE. `_render` returns the body alone, so a
      blanked fact answer is an empty reply, and GUARD A's note applies -- silence is worse than a
      wrong answer. eval_347 is a FACT-path question, so wiring this guard the way D-FIDELITY-6 is
      wired would not have fixed it; it needs replacement copy, like GUARD A's.

So this sweep reports flags SPLIT BY whether the row would have been blanked or replaced, because
a false positive on the fact path costs a whole answer and on the compute path costs a sentence.

WHAT THIS CANNOT SHOW (R21): all three populations share vocabulary with the facts by
construction, so the false-positive count here is a LOWER BOUND, not a safety verdict. It is the
strongest offline evidence available and it is not a substitute for the live check.

R18: committed before the write-up that cites it.
Artifact: eval/results/threshold_guard_prewiring_2026_10_06.json

Usage:  python eval/fidelity/price_threshold_guard_before_wiring.py
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

OUT = os.path.join(REPO, "eval", "results", "threshold_guard_prewiring_2026_10_06.json")
ADJ = os.path.join(REPO, "eval", "results", "extended_078_adjudication_2026_09_23.json")

from chike.fidelity import (body_states_wrong_threshold,            # noqa: E402
                            stated_wrong_thresholds)

# Inherited verbatim from eval/fidelity/sweep_rate_attribution_all_stored.py, including the
# reason `ok`/`pass`/`result` are ABSENT: on a probe fixture those booleans mean "the probe
# behaved as designed", and the design is TO BE FLAGGED. Reading them once reported four rows of
# a guard working perfectly as a softened baseline.
REPLY_KEYS = ("reply", "text", "raw_text", "body", "answer", "model_reply", "response")
VERDICT_KEYS = ("verdict", "judgement", "grade")
# Files whose rows are PROBES DESIGNED TO BE FLAGGED. A flag here is the instrument working, and
# `threshold_guard_probes` is this guard's OWN fixture -- counting it as a false positive would
# invert the meaning of every row in it.
PROBE_FIXTURES = ("rate_guard_sweep.json", "threshold_guard_probes.json",
                  "regen_guards_local_dryrun.json", "control_fire_audit.json")


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


def _jsonl(path):
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except Exception:
                continue


def collect():
    """[(population, id, locator, body, recorded_verdict, is_probe)] over all three populations."""
    rows, seen = [], set()

    # --- STORED_REPLY ----------------------------------------------------------------------
    adj = {}
    if os.path.exists(ADJ):
        adj = {r["id"]: r for r in json.load(open(ADJ, encoding="utf-8"))["rows"]}
    for path in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        if os.path.basename(path) == os.path.basename(OUT):
            continue
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        try:
            blob = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for item in walk(blob):
            body = next((item[k] for k in REPLY_KEYS
                         if isinstance(item.get(k), str) and item[k].strip()), "")
            rid = str(item.get("id") or item.get("qid") or item.get("probe") or "?")
            fp = (rid, body[:120])
            if fp in seen:
                continue
            seen.add(fp)
            recorded = None
            if rid in adj:
                recorded = adj[rid].get("verdict")
            elif any(isinstance(item.get(k), (str, bool)) for k in VERDICT_KEYS):
                recorded = str(next(item[k] for k in VERDICT_KEYS
                                    if isinstance(item.get(k), (str, bool))))
            rows.append(("STORED_REPLY", rid, rel, body, recorded,
                         os.path.basename(path) in PROBE_FIXTURES))

    # --- GOLD ------------------------------------------------------------------------------
    for sub in ("accuracy_gate", "refusal_gate"):
        for path in sorted(glob.glob(os.path.join(REPO, "eval", sub, "*.jsonl"))):
            rel = os.path.relpath(path, REPO).replace(os.sep, "/")
            for n, obj in _jsonl(path):
                body = next((obj[k] for k in ("correct_answer_sw", "expected_answer_sw",
                                              "answer_sw", "gold_sw", "expected_sw")
                             if isinstance(obj.get(k), str) and obj[k].strip()), "")
                if not body:
                    continue
                rid = str(obj.get("id") or f"{os.path.basename(path)}:{n}")
                rows.append(("GOLD", rid, f"{rel}:{n}", body, "HUMAN_ASSERTED_CORRECT", False))

    # --- PAIRED ----------------------------------------------------------------------------
    for sub in ("cleaned_pairs", "sft_shaped_pairs"):
        for path in sorted(glob.glob(os.path.join(
                REPO, "datasets", "tier1a", sub, "*.jsonl"))):
            rel = os.path.relpath(path, REPO).replace(os.sep, "/")
            for n, obj in _jsonl(path):
                body = next((obj[k] for k in ("answer_sw", "output")
                             if isinstance(obj.get(k), str) and obj[k].strip()), "")
                if not body:
                    continue
                rid = str(obj.get("id") or f"{os.path.basename(path)}:{n}")
                rows.append(("PAIRED", rid, f"{rel}:{n}", body, "IN_TRAINING_SET", False))

    return rows


def main():
    rows = collect()

    # R20: a collector that finds nothing reports zero flags, which is indistinguishable from a
    # clean result. Both halves asserted -- a population AND an exercised instrument.
    by_pop = collections.Counter(p for p, *_ in rows)
    assert by_pop["STORED_REPLY"] > 200, f"only {by_pop['STORED_REPLY']} stored replies"
    assert by_pop["GOLD"] > 300, f"only {by_pop['GOLD']} gold answers"
    assert by_pop["PAIRED"] > 1000, f"only {by_pop['PAIRED']} paired rows"

    flagged = []
    for pop, rid, loc, body, recorded, is_probe in rows:
        pairs = stated_wrong_thresholds(body)
        if not pairs:
            continue
        assert body_states_wrong_threshold(body)      # the two entry points must agree
        flagged.append({
            "population": pop, "id": rid, "locator": loc,
            "recorded_verdict": recorded, "is_probe_designed_to_flag": is_probe,
            "claims": [[s, a] for s, a in pairs],
            "body": body[:700],
        })

    # The instrument must be EXERCISED, not merely run: if nothing anywhere trips it, a zero-flag
    # result would be vacuous rather than clean. The guard's own probe fixture guarantees this.
    assert flagged, ("the guard flagged NOTHING across 3 populations -- including its own probe "
                     "fixture, which contains rows designed to be flagged. The instrument is not "
                     "wired to the corpora at all and a clean verdict here would be vacuous.")

    real = [f for f in flagged if not f["is_probe_designed_to_flag"]]
    gold_flags = [f for f in real if f["population"] == "GOLD"]
    booked_correct = [f for f in real if f["population"] == "STORED_REPLY"
                      and str(f["recorded_verdict"]).upper() in
                      ("PASS", "PASS_BY_OUTCOME", "CORRECT")]

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/fidelity/price_threshold_guard_before_wiring.py",
        "instrument": ("chike.fidelity.stated_wrong_thresholds -- D-FIDELITY-7, built 2026-08-23, "
                       "NOT WIRED. No new rule was written for this measurement (R33): writing "
                       "one would have measured the new rule, not the phenomenon."),
        "question": ("If D-FIDELITY-7 were wired today, what text would it remove? Split by "
                     "population and by whether the row was already booked correct."),
        "why_each_population": {
            "STORED_REPLY": ("the only population that is actual MODEL PROSE, which is what the "
                             "guard is handed in production -- and the only one where a flag can "
                             "be joined to a recorded verdict"),
            "GOLD": ("a human asserted each of these is RIGHT, so a flag is the strongest "
                     "available false-positive signal"),
            "PAIRED": ("the corpus the model was trained on -- closest offline proxy for the "
                       "prose it emits, and a flag is a candidate training defect too"),
        },
        "the_path_distinction": (
            "A flag does not mean one action. On the COMPUTE path blanking is safe -- _render "
            "still emits the engine's working, so the user loses a sentence and keeps the figure. "
            "On the FACT path blanking is SILENCE, because _render returns the body alone. "
            "eval_347 is a fact-path question, so wiring this the way D-FIDELITY-6 is wired would "
            "not fix it: it needs replacement copy, like GUARD A's headcount_contradiction."),
        "what_this_cannot_show": (
            "R21: all three populations share vocabulary with the facts by construction, so the "
            "false-positive count is a LOWER BOUND, not a safety verdict. A flag is a CANDIDATE, "
            "not a verdict (R26 second half) -- every one below is printed with its attributed "
            "claims so it can be read individually before anything is done with it."),
        "totals": {
            "rows_swept": len(rows),
            "by_population": dict(by_pop),
            "flagged_total": len(flagged),
            "flagged_excluding_own_probe_fixtures": len(real),
            "flagged_in_GOLD": len(gold_flags),
            "flagged_and_previously_booked_correct": len(booked_correct),
            "by_subject": dict(collections.Counter(
                c[0] for f in real for c in f["claims"])),
            "by_file": dict(collections.Counter(f["locator"].split(":")[0] for f in real)),
        },
        "flagged": flagged,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    t = artifact["totals"]
    print(f"rows swept: {t['rows_swept']}  {t['by_population']}")
    print(f"FLAGGED total:                        {t['flagged_total']}")
    print(f"  excluding the guard's own fixtures: {t['flagged_excluding_own_probe_fixtures']}")
    print(f"  in GOLD (human-asserted correct):   {t['flagged_in_GOLD']}")
    print(f"  stored replies booked CORRECT:      {t['flagged_and_previously_booked_correct']}")
    print(f"  by subject: {t['by_subject']}")
    print()
    for f in real:
        print(f"  [{f['population']:12}] {f['id']:22} {f['claims']}")
        print(f"      {f['locator']}   recorded={f['recorded_verdict']}")
        print(f"      {' '.join(f['body'].split())[:240]}")
        print()
    print(f"[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
