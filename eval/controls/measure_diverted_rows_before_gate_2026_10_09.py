# -*- coding: utf-8 -*-
"""THE 8 GATE ROWS THE STATEMENT ROUTE MOVES, MEASURED LIVE AND SCORED, BEFORE THE GATE RUNS.

⛔ WHY THIS EXISTS, AND IT IS NOT A PREVIEW OF THE GATE. The pre-registration needs one number
it cannot guess: **how many of the 12 confirmed defects should flip.** Guessing it would make the
result unfalsifiable in either direction — a flat gate could be read as "the change did nothing"
or as "the change was never going to show here", and nothing written afterwards could settle
which. So the 8 rows the sweep measured as diverting are asked LIVE and scored with the
PRODUCTION scorer, and the prediction is derived from that rather than asserted.

⛔ AND THE FINDING THAT MAKES THE WHOLE EXERCISE NECESSARY: AT `0e11c3d` THE REGEX SCORER
ALREADY MARKED 7 OF THESE 8 ROWS AS PASSES. Three of them (`eval_086`, `eval_130`, `eval_394`)
were flagged by the judge and hand-adjudicated as FALSE_PASS — a party inversion, an inverted
operation, and a cross-levy threshold bleed, every one credited as correct. So:

    THE REGEX A2 CANNOT RISE ON THESE ROWS. IT WAS ALREADY COUNTING THEM.

The improvement therefore cannot appear in the regex headline at all. It appears as the judge's
DISAGREEMENT QUEUE SHRINKING, which raises the LOWER end of the bracket while leaving the upper
end roughly where it was. A reader who looks only at the regex figure will see a change that did
nothing, or slightly worse than nothing — and that is the measured reason the judge was promoted
to the headline this cycle, not a reinterpretation offered afterwards.

⚠️ WHAT THIS IS NOT. It is not the gate: one call per row, no judge, no OOC arm, no bucket
arithmetic, and greedy decoding means these are the replies production gives TODAY. It bounds
only the 8 rows named here. Everything else in the 400 is the unbounded term, and the sweep's
own bound applies: 2,473 questions swept, 24 diversions, 0 already-routed questions changed.

Usage:  python eval/controls/measure_diverted_rows_before_gate_2026_10_09.py
Artifact: eval/results/diverted_rows_live_2026_10_09.json  (written after EVERY row)
Exit 0 always — this MEASURES, it does not gate. A regression here is a finding for the
pre-registration, not a reason to stop the run.
"""
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "diverted_rows_live_2026_10_09.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
SWEEP = os.path.join(REPO, "eval", "results", "statement_route_sweep_2026_10_09.json")
BASELINE = os.path.join(REPO, "eval", "results", "gate_production_0e11c3d.json")

from chike import routing                                                    # noqa: E402
from chike.scoring import score_question, scorer_reliability                 # noqa: E402

GATE_FILES = (
    "eval/accuracy_gate/eval_questions_001.jsonl",
    "eval/accuracy_gate/eval_questions_002_additions.jsonl",
    "eval/accuracy_gate/eval_questions_003.jsonl",
)


def _gate_rows():
    out = {}
    for rel in GATE_FILES:
        for line in io.open(os.path.join(REPO, rel), encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                r["_file"] = rel
                out[r["id"]] = r
    assert len(out) == 400, f"expected the 400, got {len(out)}"
    return out


def _diverted_ids(gate):
    """⛔ READ FROM THE SWEEP'S ARTIFACT, NEVER RE-DERIVED HERE. A second implementation of
    'which rows divert' could disagree with the first without either being obviously wrong —
    the exact defect that let the 2026-10-07 dry run report SAFE while the real regen aborted.
    Cross-checked against the live router, which must agree on every id."""
    sw = json.load(io.open(SWEEP, encoding="utf-8"))
    ids = [r["id"] for r in sw["diversion_rows"] if r.get("id") in gate]
    assert ids, "the sweep artifact lists no diverted row inside the 400 — one of us is stale"
    for i in ids:
        got = routing.detect_intent(gate[i]["question_sw"])
        assert got != "none", (
            f"{i} is listed as diverted but detect_intent now returns 'none'. The sweep "
            f"artifact and the live router disagree; do not proceed on either.")
    return ids, sw


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (io.open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def ask(question, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                        # noqa: BLE001
        pass

    tok = token()
    if not tok:
        print("NO TOKEN — not exercisable. This is NOT a result.")
        return 2

    gate = _gate_rows()
    ids, sw = _diverted_ids(gate)
    base = {r["id"]: r for r in json.load(io.open(BASELINE, encoding="utf-8"))["rows"]}
    cfg = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"),
                            encoding="utf-8"))
    refusals = cfg.get("refusal_phrases") or cfg.get("REFUSAL_PHRASES") or []

    adj = json.load(io.open(os.path.join(REPO, "eval", "results",
                                         "false_pass_adjudication_0e11c3d.json"),
                            encoding="utf-8"))
    # ⛔ THE FIELD IS `verdict`, NOT `outcome`, AND READING THE WRONG ONE RETURNED A SILENT ZERO.
    # The first run of this harness printed `adjudicated=None` on all eight rows and tallied
    # "0 hand-adjudicated FALSE_PASS" — for eval_086, eval_130 and eval_394, which are three of
    # the seventeen. R39's deleting direction, in a harness written to support a prediction:
    # a lookup against a key that does not exist produces an EMPTY finding set, and an empty set
    # reads as "nothing to report" rather than as a broken join. Asserted below instead.
    adjudicated = {r["id"]: r.get("verdict") for r in adj.get("rows", [])}
    assert len(adjudicated) == 17, f"expected the 17 adjudicated rows, got {len(adjudicated)}"
    assert any(v for v in adjudicated.values()), "every adjudication verdict read as empty"
    _expect_adjudicated = {"eval_086", "eval_130", "eval_394"}
    assert _expect_adjudicated <= set(adjudicated), (
        f"the three rows this change targets are not in the adjudicated set, so the join is "
        f"wrong again: {sorted(set(adjudicated))}")

    rows = []
    for qid in ids:
        q = gate[qid]
        row = {
            "id": qid, "file": q["_file"], "answer_type": q.get("answer_type"),
            "intent_now": routing.detect_intent(q["question_sw"]),
            "question": q["question_sw"],
            "gold": q.get("correct_answer_sw"),
            "baseline_0e11c3d": {
                "pass": base[qid]["pass"], "reliable": base[qid]["reliable"],
                "clarified": base[qid]["clarified"],
            },
            "hand_adjudication_0e11c3d": adjudicated.get(qid),
        }
        try:
            reply = str(ask(q["question_sw"], tok).get("reply") or "")
            row["reply"] = reply
            row["scored_pass_now"] = bool(score_question(q, reply, refusals))
            ok, why = scorer_reliability(q, reply)
            row["scorer_reliable_now"] = bool(ok)
            row["scorer_unreliable_reason"] = why or None
            row["regex_delta"] = (
                "unchanged" if row["scored_pass_now"] == base[qid]["pass"]
                else ("REGEX_GAIN" if row["scored_pass_now"] else "REGEX_LOSS"))
        except Exception as exc:                                             # noqa: BLE001
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        _save(rows, sw)
        print(f"[{row.get('regex_delta', 'ERROR'):9s}] {qid:10s} intent={row['intent_now']:6s} "
              f"base_pass={row['baseline_0e11c3d']['pass']!s:5s} "
              f"now_pass={row.get('scored_pass_now')!s:5s} "
              f"adjudicated={row.get('hand_adjudication_0e11c3d')}")
        if row.get("reply"):
            print(f"            {' '.join(row['reply'].split())[:200]}")
        if row.get("error"):
            print(f"            ⛔ {row['error']}")

    payload = _save(rows, sw)
    print("\n" + json.dumps(payload["tally"], ensure_ascii=False, indent=1))
    print(payload["_the_prediction"])
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    return 0


def _save(rows, sw):
    gains = [r["id"] for r in rows if r.get("regex_delta") == "REGEX_GAIN"]
    losses = [r["id"] for r in rows if r.get("regex_delta") == "REGEX_LOSS"]
    flat = [r["id"] for r in rows if r.get("regex_delta") == "unchanged"]
    already = [r["id"] for r in rows if r["baseline_0e11c3d"]["pass"]]
    false_pass = [r["id"] for r in rows
                  if r.get("hand_adjudication_0e11c3d") in ("FALSE_PASS", "PARTIAL")]
    payload = {
        "_what": "the 8 gate-400 rows the statement route diverts, asked live on the deployed "
                 "system and scored with the production scorer, before the gate runs",
        "_population_and_why": (
            "R22: the population is the rows the CHANGE touches, read out of the sweep's own "
            "artifact rather than re-derived, and cross-checked against the live router. It is "
            "the population the prediction is about and nothing wider — every other row in the "
            "400 is the unbounded term."),
        "_endpoint": ENDPOINT,
        "sweep_bound": {k: sw[k] for k in ("questions_swept", "unchanged", "diversions",
                                           "already_routed_and_changed") if k in sw},
        "tally": {
            "rows": len(rows),
            "already_passing_under_regex_at_baseline": len(already),
            "of_those_hand_adjudicated_false_pass_or_partial": len(false_pass),
            "regex_gain": gains, "regex_loss": losses, "regex_unchanged": flat,
        },
        "_the_prediction": (
            "THE REGEX HEADLINE CANNOT RISE ON THESE ROWS BECAUSE IT WAS ALREADY COUNTING THEM: "
            f"{len(already)} of {len(rows)} scored pass=True at 0e11c3d, and {len(false_pass)} "
            "of those were hand-adjudicated FALSE_PASS or PARTIAL. The improvement shows up as "
            "the judge's disagreement queue shrinking — which raises the LOWER end of the Bar A "
            "bracket and leaves the upper end roughly flat. A flat or slightly lower regex A2 is "
            "the PREDICTED result here, not evidence the change failed."),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


if __name__ == "__main__":
    sys.exit(main())
