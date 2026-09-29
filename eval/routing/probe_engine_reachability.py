# -*- coding: utf-8 -*-
"""EVERY ENGINE probed THROUGH THE FULL PIPELINE: raw question string -> reply text.

WHY THIS EXISTS, AND WHY IT IS NOT eval/routing/probe_rent_wht_pipeline.py GENERALISED. That
harness reproduces ONE deterministic route by hand. This one drives the real
`Orchestrator.answer()` -- classify -> decompose -> route -> answer -> merge -- so a row can
fail for every reason a live message can fail for, including the two a route-level check cannot
see:

  * THE OOC GATE FIRES FIRST. `classify()` runs before routing and returns before anything can
    intervene. `soko la hisa` refused ext_01 in PRODUCTION (2026-09-23) and nothing offline was
    looking; bare `mrabaha` refused our own training pair for months. A reachability harness
    that starts at `detect_intent` cannot see either, because by then the question has already
    survived the gate. Here an OOC intercept is a verdict: OOC_REFUSED.
  * ROUTING CORRECTLY AND THEN DELIVERING NOTHING. A question can reach the right route and
    still end in a clarification because the field extraction found no usable value. From the
    user's side that is indistinguishable from an unreachable engine, and it is a DIFFERENT
    defect with a different fix -- so the verdict distinguishes them (CLARIFIED vs FACT_PATH).

WHAT EACH VERDICT MEANS, and there are six because "the engine did not answer" has six causes
and only some are defects:
    REACHED      the expected engine ran and its ComputationResult is in the reply
    WRONG_ENGINE an engine ran, but not the expected one -- a misroute, the dangerous case
    CLARIFIED    routed correctly, no engine result: a never-guess exit fired
    FACT_PATH    routed to `none`; the model answers from RAG. The R31 shape exactly
    OOC_REFUSED  the refusal gate intercepted an in-scope question. A substring collision
    ERROR        the harness itself failed on this row (recorded, never fatal to the run)

THE BACKEND IS A FakeBackend AND THAT BOUNDS WHAT THIS MEASURES -- stated rather than implied,
because the wrong reading of a clean result here is the R26 "bad specimen" failure:
  * Routes whose answer is `_deterministic_answer` (minimum_wage, vat_registration,
    efd_requirement, presumptive, corporate_tax, partnership_tax, rent_wht, base rejections,
    the rate statements) call NO model at all. For those rows this harness IS the production
    path, offline, byte-for-byte.
  * The four levy computations (sdl/nssf/paye/wcf) DO call the model -- once for slot extraction
    and once to render. The extraction layer is deterministic-primary (regex originates values;
    the model is a fallback only where regex found nothing), so a probe stating its figures in
    parseable form exercises exactly what production exercises. A probe that would need the
    MODEL fallback to find its figure is NOT measured here, and cannot be measured offline.
    Those rows are reported, never silently counted as clean.

R21/R33 BOUND. Every probe was authored by someone who had read the cue lists, so a REACHED
verdict is a COVERAGE result -- these named natural forms reach the engine -- and never a
REALISM one. Whether real users produce these forms is a traffic claim that needs transcripts.
The `technical_control` arm exists for the opposite reason (R26 step 2): if the row containing
the acronym or statutory term ALSO misses, the route is broken rather than merely narrow, and
the natural-arm failures mean something different.

Artifact is written after EVERY row and per-row errors are captured rather than raised (R16
structural rule), so a fault costs one row and never the run.

Usage:  python eval/routing/probe_engine_reachability.py
Exit 0 = every row reached what it was expected to; 1 = at least one did not.
"""

import json
import os
import sys
import traceback
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

PROBES = os.path.join(REPO, "eval", "routing", "engine_reachability_probes.jsonl")
OUT = os.path.join(REPO, "eval", "results", "engine_reachability_probes.json")

from chike import classification                                    # noqa: E402
from chike.model_abstraction.test_double import FakeBackend         # noqa: E402
from chike.orchestrator import Orchestrator                         # noqa: E402

# The route name a probe declares, mapped to the `computation` string its engine stamps on the
# ComputationResult. They differ for the levies (the rate-statement and applicability paths
# reuse the levy name) and agree elsewhere; declared explicitly so a mismatch is a failure
# rather than a silent miss.
ROUTE_TO_COMPUTATION = {
    "sdl": {"sdl"},
    "nssf": {"nssf"},
    "paye": {"paye"},
    "wcf": {"wcf"},
    "minimum_wage": {"minimum_wage"},
    "vat_registration": {"vat_registration"},
    "efd_requirement": {"efd_requirement", "efd"},
    "presumptive": {"presumptive"},
    "corporate_tax": {"corporate_tax"},
    "partnership_tax": {"partnership_tax", "corporate_tax"},
    "rent_wht": {"rent_wht"},
}


def ooc_verdict(question, ooc_phrases):
    """Which OOC phrase (if any) intercepts this question, for diagnosis not just a boolean.

    Mirrors chike.classification.classify's precedence: the conjunctive rules share the flat
    list's slot and both run before anything else. Reported so a collision names the phrase
    that has to be narrowed -- the 2026-09-23 ext_01 incident cost a production cycle partly
    because the offending phrase had to be hunted for after the fact.
    """
    msg = question.lower()
    if classification._matches_conjunction(msg):
        return "OOC_CONJUNCTION"
    for phrase in ooc_phrases:
        if phrase in msg:
            return phrase
    return None


def probe(orch, row):
    q = row["question"]
    expect = row["expect"]

    matched = ooc_verdict(q, orch.ooc_phrases)
    parts = orch.decompose(q)
    routed = [orch.route(p) for p in parts]
    routes = [sq.computation_type or "none" for sq in routed]

    reply = orch.answer(q)
    computations = [
        {"computation": sa.computation.computation,
         "applicable": sa.computation.applicable,
         "amount": None if sa.computation.amount is None else str(sa.computation.amount),
         "inputs": {k: (None if v is None else str(v))
                    for k, v in (sa.computation.inputs or {}).items()},
         "note": sa.computation.note}
        for sa in reply.sub_answers if getattr(sa, "computation", None) is not None
    ]
    got = {c["computation"] for c in computations}
    wanted = ROUTE_TO_COMPUTATION[expect]

    if reply.refused or not reply.in_scope:
        verdict = "OOC_REFUSED"
    elif got & wanted:
        verdict = "REACHED"
    elif got:
        verdict = "WRONG_ENGINE"
    elif reply.needs_clarification:
        verdict = "CLARIFIED"
    else:
        verdict = "FACT_PATH"

    # `accept` IS PER ROW AND DEFAULTS TO REACHED-ONLY, which is the strict reading. Two other
    # outcomes are legitimately correct for specific rows and both had to be discovered by
    # running verbatim committed probes through this harness rather than by reasoning:
    #   * CLARIFIED -- a documented never-guess exit fired. wp_02 states no occupation, so
    #     min_wage_no_sector IS the right answer; scoring it a miss would have reported the
    #     minimum-wage route broken when only the Schedule resolver had nothing to resolve.
    #   * FACT_PATH -- the question is not a compute question at all (it asks what a threshold
    #     IS, with no figure to test). Three rows in this fixture are mine and wrong, kept
    #     visible with the pass condition inverted so a future widening that captures them FAILS.
    # A row that accepts anything other than REACHED must carry its reason in the fixture; the
    # assertion in main() enforces that, so `accept` cannot become a way to make a row pass.
    accept = row.get("accept") or ["REACHED"]

    return {
        "id": row["id"], "arm": row["arm"], "expect": expect, "verdict": verdict,
        "accept": accept, "ok": verdict in accept,
        "ooc_phrase_matched": matched,
        "parts": parts, "routes": routes,
        "engine_results": computations,
        # The parameter-level evidence: which of the engine's parameters this NATURAL phrasing
        # actually populated. A REACHED row whose target parameter is still None is a
        # reachability pass and a parameter-extraction miss -- two different findings, and
        # collapsing them is how corporate `sector` stayed unreachable while its route worked.
        "engine_inputs": {k: v for c in computations for k, v in c["inputs"].items()},
        "needs_clarification": reply.needs_clarification,
        "question": q,
        "supplies": row.get("supplies", ""),
        "guards_against": row.get("guards_against", ""),
        "reply": reply.text,
    }


def main():
    rows = [json.loads(l) for l in open(PROBES, encoding="utf-8") if l.strip()]

    # R20: not decorative. An empty probe file sweeps zero rows and reports zero failures,
    # which is indistinguishable from a clean pass to any caller and to any `&&` chain.
    assert rows, "probe file is empty"
    unknown = sorted({r["expect"] for r in rows} - set(ROUTE_TO_COMPUTATION))
    assert not unknown, f"probe rows expect routes with no computation mapping: {unknown}"

    # R20: `accept` must not become a way to make a row pass. Any row that accepts an outcome
    # other than REACHED has to say why, in the fixture, where the next reader will see it.
    unreasoned = [r["id"] for r in rows
                  if set(r.get("accept") or ["REACHED"]) - {"REACHED"}
                  and not (r.get("accept_clarify_reason") or r.get("specimen_verdict"))]
    assert not unreasoned, (
        f"rows accept a non-REACHED verdict with no recorded reason: {unreasoned}. A relaxed "
        f"expectation with no justification is the vacuous-check shape -- state the never-guess "
        f"exit that makes it correct, or fix the probe.")

    # ooc_phrases/in_scope_phrases left to DEFAULT so the real config-resolved production lists
    # are exercised. Passing [] here would disable the very gate whose collisions this harness
    # exists to find -- the shape of a control that cannot fire.
    orch = Orchestrator(backend=FakeBackend(scripted_reply="{}"), retriever=lambda q: [])
    assert len(orch.ooc_phrases) > 100, (
        f"only {len(orch.ooc_phrases)} OOC phrases loaded -- the config-only phrases are "
        f"missing and an OOC collision could not be detected (CONTAINER-PATH-1)")

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/routing/probe_engine_reachability.py",
        "probes": "eval/routing/engine_reachability_probes.jsonl",
        "ooc_phrases_loaded": len(orch.ooc_phrases),
        "what_this_measures": (
            "Whether each rules engine is reachable from a question phrased the way a real "
            "asker phrases it -- measured from the raw string through the OOC gate, "
            "decomposition, routing and field extraction to the reply, which is the span no "
            "unit test touches."),
        "what_it_cannot_show": (
            "Whether these are the phrasings real users produce (R33: the probes were authored "
            "by someone who had read the cue lists, so REACHED is a coverage result, never a "
            "realism one), and anything that depends on the MODEL fallback in slot extraction, "
            "which a FakeBackend cannot supply."),
        "why_this_population": (
            "Every engine the system can answer with, two arms each: a natural phrasing that "
            "names no acronym or statutory term, and a technical control that does. R31's five "
            "instances were all engines whose branches were correct and whose natural phrasings "
            "reached nothing, so the population a reachability defect lives in IS the engine "
            "list -- not the gate corpora, which are authored in the register that already "
            "works (R22)."),
        "verdict_meanings": {
            "REACHED": "expected engine ran; its result is in the reply",
            "WRONG_ENGINE": "an engine ran, but not the expected one -- a misroute",
            "CLARIFIED": "routed correctly, never-guess exit fired, no engine result",
            "FACT_PATH": "routed to `none`; the model answers from RAG. The R31 shape",
            "OOC_REFUSED": "the refusal gate intercepted an in-scope question",
            "ERROR": "the harness failed on this row",
        },
        "rows": [],
    }

    def flush():
        by_verdict = {}
        for r in artifact["rows"]:
            by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
        artifact["summary"] = {
            "n": len(artifact["rows"]),
            "by_verdict": by_verdict,
            "reached": sum(1 for r in artifact["rows"] if r["ok"]),
            "natural_reached": sum(1 for r in artifact["rows"]
                                   if r["arm"] == "natural" and r["ok"]),
            "natural_total": sum(1 for r in artifact["rows"] if r["arm"] == "natural"),
            "control_reached": sum(1 for r in artifact["rows"]
                                   if r["arm"] == "technical_control" and r["ok"]),
            "control_total": sum(1 for r in artifact["rows"]
                                 if r["arm"] == "technical_control"),
            "by_arm": {arm: {"ok": sum(1 for r in artifact["rows"]
                                       if r["arm"] == arm and r["ok"]),
                             "n": sum(1 for r in artifact["rows"] if r["arm"] == arm)}
                       for arm in sorted({r["arm"] for r in artifact["rows"]})},
            "failures": [r["id"] for r in artifact["rows"] if not r["ok"]],
        }
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(artifact, fh, ensure_ascii=False, indent=2)

    for row in rows:
        try:
            res = probe(orch, row)
        except Exception:                      # per-row capture, never fatal (R16)
            res = {"id": row["id"], "arm": row["arm"], "expect": row["expect"],
                   "verdict": "ERROR", "ok": False, "question": row["question"],
                   "error": traceback.format_exc(limit=4)}
        artifact["rows"].append(res)
        flush()                                # after EVERY row, not once at the end
        print(f"{'ok  ' if res['ok'] else 'MISS'} {res['id']:12} {res['arm']:18}"
              f" expect={res['expect']:18} {res['verdict']:13}"
              f" routes={res.get('routes')}"
              + (f"  ooc={res['ooc_phrase_matched']!r}"
                 if res.get("ooc_phrase_matched") else ""))

    s = artifact["summary"]
    print()
    print(f"natural arm:          {s['natural_reached']}/{s['natural_total']} reached")
    print(f"technical control:    {s['control_reached']}/{s['control_total']} reached")
    print(f"verdicts: {s['by_verdict']}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    if s["failures"]:
        print("DID NOT REACH: " + ", ".join(s["failures"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
