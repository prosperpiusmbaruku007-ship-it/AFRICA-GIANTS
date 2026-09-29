# -*- coding: utf-8 -*-
"""Rent-WHT reachability probed THROUGH THE FULL PIPELINE: raw question -> reply.

WHY THIS HARNESS EXISTS, AND WHY THE UNIT TESTS COULD NOT REPLACE IT. tests/test_rent_wht.py
is 15/15 green and was green throughout the defect this harness was built to find. It calls
`rent_wht_statement(...)` with keyword arguments, so it proves the engine's BRANCHES are
correct. Reachability lives entirely in the code between a raw message and those keyword
arguments -- `decompose_query` -> `detect_intent` -> the orchestrator's dispatch -- and a unit
test never touches it. That is R31's lesson at the route level: an engine reachable only by
the technical term serves the users who least need it.

So every row here starts from a RAW QUESTION STRING and ends at the TEXT A USER WOULD
RECEIVE. Nothing is passed in by hand.

THE PATH IS DETERMINISTIC AND THAT IS NOT AN APPROXIMATION. Orchestrator._answer_rent_wht
calls _deterministic_answer, whose docstring is explicit: "A compute answer whose text is the
engine's `working` ALONE -- no model call." The engine's working IS the reply. So this harness
reproduces production's rent-WHT reply exactly, offline, with no adapter and no sampling --
it is not a stand-in for the live path, it is that path.

WHAT IS ASSERTED, and the 15% check is the load-bearing one (R23 -- a control must look for a
value the system would not produce by default):
  * must-route rows reach `rent_wht` AND the reply states asilimia 10 AND cites para 4(b)(ii)
  * NO reply anywhere contains `asilimia 15`. That is the corpus's error -- 16 rows quarantined
    2026-09-26 -- and it is exactly what would reappear if a future reader "fixed" the missing
    `is_resident` parameter. A reply containing it is the failure this suite exists to catch.
  * must-not-route rows do NOT reach `rent_wht`. This is the half that does the work (R17
    step 2): rwp_09 is a real held-out PAYE probe that already contains `nimkate`, and rwp_10
    supplies the `mkate` (BREAD) collision that the naive form of this fix creates.

R21 BOUND, stated rather than implied. The must-route rows are authored by whoever wrote the
cues, so they are not independent evidence about paraphrase space (R33). They establish that
named natural forms REACH the engine; they cannot establish that the forms real users type are
among them. That needs transcripts.

Artifact is written after EVERY row (R16 structural rule), so a fault costs one row, never the
run.

Usage:  python eval/routing/probe_rent_wht_pipeline.py
Exit 0 = all rows as expected; 1 = at least one mismatch.
"""

import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

PROBES = os.path.join(REPO, "eval", "routing", "rent_wht_pipeline_probes.jsonl")
OUT = os.path.join(REPO, "eval", "results", "rent_wht_pipeline_probes.json")

from chike import rules_engine                                          # noqa: E402
from chike.decomposition import decompose_query                         # noqa: E402
from chike.routing import detect_intent, rent_letting_is_commercial     # noqa: E402

# The exact figure the quarantined corpus rows asserted. Never legitimate in a rent-WHT reply.
FORBIDDEN = "asilimia 15"
REQUIRED_RATE = "asilimia 10"
REQUIRED_CITATION = "4(b)(ii)"


def pipeline(question: str):
    """Raw question -> (routes, reply). Mirrors Orchestrator._answer_rent_wht exactly.

    The engine call reproduces the orchestrator's line for line: `letting_is_commercial` comes
    from the production extractor applied to the sub-question text, and
    `payer_is_withholding_agent` is NOT passed -- it has no extractor by design, and supplying
    one here would be the R24 failure of probing a path we do not ship.
    """
    parts = decompose_query(question)
    routes = [detect_intent(p) for p in parts]
    replies = []
    for part, route in zip(parts, routes):
        if route == "rent_wht":
            result = rules_engine.rent_wht_statement(
                letting_is_commercial=rent_letting_is_commercial(part))
            replies.append(result.working)
    return routes, "\n".join(replies)


def check(row):
    routes, reply = pipeline(row["question"])
    expect = row["expect"]
    routed = "rent_wht" in routes

    if expect == "rent_wht":
        ok = (routed
              and REQUIRED_RATE in reply
              and REQUIRED_CITATION in reply
              and FORBIDDEN not in reply)
    elif expect == "not_rent_wht":
        # Deliberately NOT asserting which route it takes: pinning another engine's verdict
        # here would make this suite fail for reasons that have nothing to do with rent.
        ok = not routed
    else:                                   # "none"
        ok = not routed and routes == ["none"] * len(routes)

    # Applies to EVERY row regardless of expectation, including the must-not-route half.
    if FORBIDDEN in reply:
        ok = False

    return {
        "id": row["id"],
        "arm": row["arm"],
        "expect": expect,
        "routes": routes,
        "routed_rent_wht": routed,
        "reply_states_10pct": REQUIRED_RATE in reply,
        "reply_cites_para": REQUIRED_CITATION in reply,
        "reply_contains_forbidden_15pct": FORBIDDEN in reply,
        "ok": ok,
        "question": row["question"],
        "guards_against": row["guards_against"],
        "reply": reply,
    }


def main():
    rows = [json.loads(l) for l in open(PROBES, encoding="utf-8") if l.strip()]
    artifact = {
        "measured": str(date.today()),
        "harness": "eval/routing/probe_rent_wht_pipeline.py",
        "probes": "eval/routing/rent_wht_pipeline_probes.jsonl",
        "what_this_measures": (
            "Whether a rent-WHT question phrased WITHOUT the formal withholding vocabulary "
            "reaches the engine, measured from the raw string through decomposition and "
            "routing to the reply text -- the path a unit test does not touch."),
        "what_it_cannot_show": (
            "Whether these are the phrasings real users produce. The must-route rows are "
            "authored by whoever wrote the cues (R33), so they are a COVERAGE result, never a "
            "REALISM one. That claim needs transcripts."),
        "rows": [],
    }

    failures = []
    for row in rows:
        res = check(row)
        artifact["rows"].append(res)
        if not res["ok"]:
            failures.append(res["id"])
        # Written after every row, not once at the end (R16).
        artifact["summary"] = {"n": len(artifact["rows"]), "failures": list(failures)}
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(artifact, fh, ensure_ascii=False, indent=2)
        flag = "ok  " if res["ok"] else "FAIL"
        print(f"{flag} {res['id']:8} {res['arm']:24} expect={res['expect']:14} "
              f"routes={res['routes']}")

    print()
    print(f"{len(rows) - len(failures)}/{len(rows)} as expected -> {OUT}")
    if failures:
        print("FAILURES: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
