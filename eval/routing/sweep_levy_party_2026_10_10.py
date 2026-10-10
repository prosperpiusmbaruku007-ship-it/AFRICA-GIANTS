# -*- coding: utf-8 -*-
"""THE PARTY RENDERER'S BLAST RADIUS, ENUMERATED MECHANICALLY BEFORE IT SHIPS.

WHAT THE CHANGE IS. `levy_party_share_statement` answers "what is the EMPLOYER's share" with
the employer's own figure first, instead of the total. It is reached through
`routing.levy_party`, which delegates to the existing `nssf_party` cue list and maps its
'total' default to None. The orchestrator consults it between the METHOD and RATE branches.

⛔ THIS IS A TARGETED VERIFICATION'S POPULATION, NOT A SAMPLE (R12c). The question the sweep
answers is "which corpus rows can this change possibly have touched", and it answers it by
running THE REAL ORCHESTRATOR twice over every corpus question — once with
`routing.levy_party` forced to None, once unpatched — and diffing the deterministic text. No
branch chain is re-implemented here: re-deriving the orchestrator's own ordering is how an arm
agrees with the wrong thing (R24), and the ordering is the thing under test.

⛔⛔ THE COLLISION THAT MATTERS IS THE ONE THAT WOULD LOOK LIKE SUCCESS. `nssf_party`'s
employee cues are 'ya mfanyakazi' / 'wa mfanyakazi', SINGULAR. Four corpus rows — eval_111,
eval_112, fp_01b, fp_02b — ask for a rate on "jumla ya mishahara ya WAFANYAKAZI wote", the
aggregate BASE. A bare 'mfanyakazi' cue would divert all four onto the party renderer and
answer a base question with a share, and the diversion count would have gone UP, which reads
as the change working. They are pinned below as MUST-NOT-MOVE and the sweep fails if any of
them moves.

Usage:  python eval/routing/sweep_levy_party_2026_10_10.py
Artifact: eval/results/levy_party_sweep_2026_10_10.json
Exit 0 clean · 1 a finding · 2 could not be exercised (NOT a pass).
"""
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "levy_party_sweep_2026_10_10.json")

# Rows the change EXISTS for. Each must divert, and each is pinned to the party it must reach
# — not merely to "it moved", because moving to the WRONG party is the defect being fixed.
MUST_MOVE = {
    "eval_086": ("nssf", "employer"),
    "eval_087": ("nssf", "employee"),
    "data/reviewed/hand_coded_batch_015_b05.jsonl:1": ("nssf", "employer"),
}

# ⛔ THE CONTROL ARM. These reach a levy route and contain party-adjacent vocabulary, and must
# keep the renderer they have. If any moves, the extractor is too wide and the enumeration
# above is not a population — the full gate is justified immediately.
MUST_NOT_MOVE = {
    "eval_111": "asks SDL's rate on 'jumla ya mishahara ya jumla ya WAFANYAKAZI wote' — the "
                "aggregate BASE, not a party. Plural, so the singular cues miss it by design.",
    "eval_112": "same shape for WCF, and this is the row whose BASE was wrong a day ago — "
                "answering it with a share would reintroduce that defect from the other side.",
    "fp_01b": "plain SDL rate question.",
    "fp_02b": "plain WCF rate question.",
    "eval_233": "a headcount question — the THRESHOLD renderer owns it and is ordered first.",
    "eval_130": "a method question — the METHOD renderer owns it and is ordered first.",
    "eval_364": "WCF applicability from the first employee; no party is named.",
    "ext_50": "asks which QUANTITY is right (10 vs 20), naming no party — the total is the "
              "answer, and this is the strongest row the rate renderer has.",
}

# Authored probes, because a clean corpus sweep is a lower bound (R21) and the corpus does not
# contain these shapes. The party signal arrives ONLY through natural phrasing — no technical
# term, no keyword argument — which is the test a unit test calling the engine directly
# cannot provide (R31 step 3).
PARTY_PROBES = [
    ("Kiwango cha NSSF kwa upande wa mfanyakazi ni asilimia ngapi?", "nssf", "employee",
     "eval_087's own construction"),
    ("Kiwango cha WCF kwa upande wa mwajiri ni asilimia ngapi?", "wcf", "employer",
     "WCF is employer-only, so the party answer and the rate answer agree in substance; what "
     "changes is that it leads with the party the question named."),
    ("Kiwango cha SDL kwa upande wa mfanyakazi ni asilimia ngapi?", "sdl", "employee",
     "AN EMPLOYER-ONLY LEVY ASKED ABOUT THE EMPLOYEE. The honest answer is that there is no "
     "employee share, and the contract requires that denial to precede any rate — otherwise "
     "the reply reads as the employee's own figure."),
]

# ⛔ MEASURED, AND RECORDED AS A GAP RATHER THAN CLOSED HERE. The party extractor resolves
# these correctly and `detect_intent` returns 'none', so the branch is unreachable for them —
# R31's bottleneck one layer up, which the 2026-10-09 closability pass already measured as a
# property of the ROUTER rather than of any engine (all 12 confirmed defects routed to 'none').
#
# Widening `detect_intent` is yesterday's change and needs yesterday's full sweep; bundling it
# into a renderer fix would put an unmeasured route widening inside a measured renderer split.
# Asserted in BOTH directions so the day the router widens, this list goes red and someone
# re-reads it rather than finding out from a live reply (R17's corollary: invert the test and
# keep the history).
PARTY_PROBES_BLOCKED_UPSTREAM = [
    ("Sehemu ya mwajiri katika NSSF ni kiasi gani cha asilimia?", "employer",
     "the plainest third-person employer framing. `asks_rate` wants 'kiwango'/'asilimia ngapi' "
     "and this says 'kiasi gani cha asilimia', so the statement route declines it."),
    ("Je, SDL ina sehemu ya mfanyakazi ya asilimia ngapi?", "employee",
     "'ina sehemu ya' is a HAVING frame rather than a rate ask, so the route declines it."),
]

# ⚠️ AND ONE PROBE WHERE THE EXTRACTOR ITSELF MISSES, WHICH IS A DIFFERENT GAP AND A WIDER
# BLAST RADIUS. `_NSSF_EMPLOYER_CUES` holds the first-person 'kama mwajiri nachangia' (added
# for nat_07) and not 'kama mwajiri NALIPA'. Adding it is a one-line change to a list that
# `compute_nssf` also consults to pick WHICH FIGURE TO COMPUTE, so it moves the amount path as
# well as this one and needs its own sweep over that population — not a free ride on this one.
PARTY_PROBES_EXTRACTOR_GAP = [
    ("Mimi kama mwajiri nalipa asilimia ngapi ya NSSF?",
     "first-person employer with 'nalipa' where the cue list has 'nachangia'. Resolves to "
     "None, so the rate renderer answers it with the total — not wrong, just not led by the "
     "party that was named."),
]

# Probes that must NOT reach the party renderer. Each contains party vocabulary in a context
# where the party is not the ask — R17 step 2, and these are the ones that find an over-broad
# cue the corpus never exercises.
MUST_STAY_OFF_PARTY = [
    ("Kiwango cha SDL ni asilimia ngapi ya mishahara ya wafanyakazi wote?",
     "PLURAL wafanyakazi — the aggregate base. This is the collision the whole narrowing "
     "exists for, authored rather than harvested."),
    ("SDL inalipwa na mwajiri au mfanyakazi?",
     "an INCIDENCE question. It names both parties and asks which one pays; answering it with "
     "one party's percentage answers a different question. The incidence renderer holds this "
     "and is deliberately not routed yet."),
    ("Jumla ya mchango wa NSSF kwa mwajiri na mfanyakazi ni asilimia ngapi?",
     "names BOTH parties and asks for the total — `nssf_party`'s TOTAL cues must win, which "
     "is the precedence this reuses rather than reimplements."),
    ("Nyaraka gani zinahitajika kusajili mfanyakazi NSSF?",
     "contains 'mfanyakazi' and asks for DOCUMENTS. No engine holds the document list."),
    ("Mfanyakazi wangu ana mshahara mdogo, NSSF inamhusu?",
     "an applicability question naming an employee. The applicability branch owns it."),
]

FIXED_FACTS = [
    "nssf_employer_rate: mwajiri analipa asilimia 10 ya mshahara ghafi wa mfanyakazi.",
    "sdl_rate: SDL ni asilimia 3.5 ya jumla ya mishahara.",
]


def _load_corpora():
    """Every question in every corpus, named file-by-file so the population is inspectable.

    Lifted from eval/routing/sweep_statement_route_2026_10_09.py deliberately: the two sweeps
    must agree on what "every corpus question" means, and two copies of a loader is how they
    stop agreeing.
    """
    pats = [
        "eval/accuracy_gate/*.jsonl",
        "eval/refusal_gate/*.jsonl",
        "eval/fidelity/*.jsonl",
        "eval/grounding/*.jsonl",
        "data/reviewed/*.jsonl",
    ]
    out = []
    for pat in pats:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            rel = os.path.relpath(path, REPO).replace("\\", "/")
            for i, line in enumerate(io.open(path, encoding="utf-8")):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                q = (r.get("question_sw") or r.get("question") or r.get("instruction")
                     or r.get("q") or "")
                if isinstance(q, str) and q.strip():
                    out.append({"file": rel, "line": i + 1,
                                "id": r.get("id") or f"{rel}:{i + 1}", "q": q})
    return out


def _run_all(questions, orch_factory):
    """⚠️ KEYED BY (file, line), NEVER BY `id`. My first version keyed by id and two corpus
    files both carry `hc_09` — so one row's BEFORE was silently overwritten by the other's,
    and the sweep reported a currency clarification as the baseline for an SDL question. A
    collision in a baseline map does not error; it produces a confident wrong diff."""
    out = {}
    for r in questions:
        key = (r["file"], r["line"])
        try:
            reply = orch_factory().answer(r["q"])
            out[key] = (reply.text or "")
        except Exception as exc:                                         # noqa: BLE001
            out[key] = f"<<ERROR {type(exc).__name__}: {str(exc)[:120]}>>"
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

    from chike import routing
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator

    class _Silent(ModelBackend):
        """Returns nothing. A row that reaches the model is identified by its empty text, so
        the fact path is distinguishable from a deterministic answer without a GPU."""

        def generate(self, prompt, params=None):
            return ""

    def factory():
        return Orchestrator(_Silent(), retriever=lambda _q: list(FIXED_FACTS),
                            ooc_phrases=[], in_scope_phrases=[])

    rows = _load_corpora()
    if len(rows) < 500:
        print(f"[FATAL] only {len(rows)} questions loaded — a clean result would mean nothing. "
              f"Exit 2 is NOT a pass.")
        return 2

    # BEFORE, by disabling the extractor rather than by asserting what the baseline was.
    orig = routing.levy_party
    routing.levy_party = lambda text, computation_type: None
    try:
        before = _run_all(rows, factory)
    finally:
        routing.levy_party = orig
    after = _run_all(rows, factory)

    def _key(r):
        return (r["file"], r["line"])

    moved = [{**r, "before": before[_key(r)], "after": after[_key(r)],
              "party": routing.levy_party(r["q"], routing.detect_intent(r["q"]))}
             for r in rows if before[_key(r)] != after[_key(r)]]
    moved_ids = {m["id"] for m in moved}

    findings = []
    for rid, (ct, party) in MUST_MOVE.items():
        hit = next((m for m in moved if m["id"] == rid), None)
        if hit is None:
            findings.append(f"MUST_MOVE row {rid} did not move")
        elif hit["party"] != party:
            findings.append(f"MUST_MOVE row {rid} reached party {hit['party']!r}, "
                            f"expected {party!r}")
    stayed_bad = sorted(moved_ids & set(MUST_NOT_MOVE))
    if stayed_bad:
        findings.append(f"CONTROL ARM BROKEN — {len(stayed_bad)} row(s) that must keep their "
                        f"renderer moved: {stayed_bad}. The extractor is too wide, the "
                        f"enumeration is not a population, and the full gate is justified.")
    unexpected = sorted(moved_ids - set(MUST_MOVE))
    if unexpected:
        findings.append(f"{len(unexpected)} UNADJUDICATED diversion(s) — read each, then pin "
                        f"it with the reason it is safe, or narrow the cue: {unexpected}")

    probes = []
    for q, ct, want, why in PARTY_PROBES:
        intent = routing.detect_intent(q)
        got = routing.levy_party(q, intent)
        ok = (intent == ct and got == want)
        probes.append({"question": q, "expect_levy": ct, "expect_party": want,
                       "intent": intent, "party": got, "ok": ok, "why": why})
    probe_bad = [p for p in probes if not p["ok"]]
    if probe_bad:
        findings.append(f"{len(probe_bad)} natural-phrasing probe(s) did not reach the party "
                        f"branch: {[p['question'] for p in probe_bad]}")

    # Both limbs asserted: the extractor resolves it AND the router declines it. Either limb
    # flipping is a finding — the first means the extractor regressed, the second means the
    # router widened and these rows are now reachable and unmeasured.
    blocked = []
    for q, want, why in PARTY_PROBES_BLOCKED_UPSTREAM:
        intent = routing.detect_intent(q)
        got = routing.levy_party(q, "nssf" if "nssf" in q.lower() else "sdl")
        blocked.append({"question": q, "expect_party": want, "party": got, "intent": intent,
                        "extractor_resolves": got == want, "router_declines": intent == "none",
                        "ok": got == want and intent == "none", "why": why})
    blocked_bad = [b for b in blocked if not b["ok"]]
    if blocked_bad:
        for b in blocked_bad:
            if not b["extractor_resolves"]:
                findings.append(f"blocked-upstream probe regressed in the EXTRACTOR: "
                                f"{b['question']!r} resolved {b['party']!r}, "
                                f"expected {b['expect_party']!r}")
            else:
                findings.append(f"blocked-upstream probe is NOW REACHABLE — the router widened "
                                f"to {b['intent']!r} on {b['question']!r}. This row's answer "
                                f"has never been measured; re-run this sweep's control arm.")

    gaps = []
    for q, why in PARTY_PROBES_EXTRACTOR_GAP:
        got = routing.levy_party(q, "nssf")
        gaps.append({"question": q, "party": got, "still_a_gap": got is None, "why": why})
    gap_closed = [g for g in gaps if not g["still_a_gap"]]
    if gap_closed:
        findings.append(f"a recorded extractor gap has been closed without this sweep being "
                        f"updated — the shared `nssf_party` list moved, which also moves the "
                        f"AMOUNT path: {[g['question'] for g in gap_closed]}")

    negatives = []
    for q, why in MUST_STAY_OFF_PARTY:
        intent = routing.detect_intent(q)
        got = routing.levy_party(q, intent)
        negatives.append({"question": q, "intent": intent, "party": got,
                          "ok": got is None, "why": why})
    neg_bad = [n for n in negatives if not n["ok"]]
    if neg_bad:
        findings.append(f"{len(neg_bad)} probe(s) that must stay off the party branch reached "
                        f"it: {[(n['question'], n['party']) for n in neg_bad]}")

    payload = {
        "_what": "every corpus question's deterministic answer with and without the party "
                 "renderer, run through the REAL orchestrator",
        "_why_this_is_a_population": "the party branch can only fire where routing.levy_party "
                                     "returns a party, so a row where it returns None cannot "
                                     "have changed. The control arm is what tests that premise "
                                     "rather than assuming it.",
        "_the_extractor_is_reused_not_rewritten": "routing.levy_party delegates to nssf_party, "
                                                  "which has resolved this signal since "
                                                  "2026-08-15 including the first-person and "
                                                  "object-concord work. A second cue list "
                                                  "would be R39's two-rules defect.",
        "questions_swept": len(rows),
        "files": sorted({r["file"] for r in rows}),
        "moved": len(moved),
        "must_move": {k: list(v) for k, v in MUST_MOVE.items()},
        "must_not_move": MUST_NOT_MOVE,
        "moved_rows": sorted(moved, key=lambda m: m["id"]),
        "natural_phrasing_probes": probes,
        "blocked_upstream_by_detect_intent": blocked,
        "extractor_gaps_recorded_not_closed": gaps,
        "must_stay_off_party": negatives,
        "findings": findings,
        "_bound": ("R21: a lower bound on cost. These corpora share vocabulary with the facts "
                   "by construction, and both probe arms were authored by whoever wrote the "
                   "rule — so a clean result says the change does not break what we have, not "
                   "that it is safe on a stranger's phrasing."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"swept {len(rows)} questions across {len(payload['files'])} files")
    print(f"  moved                  {len(moved)}")
    print(f"  natural-phrasing probes {len(probes) - len(probe_bad)}/{len(probes)} reached")
    print(f"  blocked upstream        {len(blocked) - len(blocked_bad)}/{len(blocked)} still "
          f"blocked by detect_intent, extractor resolving")
    print(f"  extractor gaps          {len(gaps) - len(gap_closed)}/{len(gaps)} still open")
    print(f"  must-stay-off probes    {len(negatives) - len(neg_bad)}/{len(negatives)} held")
    for m in sorted(moved, key=lambda m: m["id"]):
        tag = "MUST_MOVE" if m["id"] in MUST_MOVE else "unadjudicated"
        print(f"  [{tag:14s}] {m['id']:24s} party={m['party']}")
    if findings:
        print("\nFINDINGS:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("\nVERDICT: the party branch's population is the rows pinned above, and the control "
          "arm held.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
