# -*- coding: utf-8 -*-
"""WHICH STAGE SHOULD D-FIDELITY-6 RUN AT? Measured, not argued.

THE GAP. `Orchestrator._validate_and_clean` calls
`fidelity.body_states_wrong_levy_rate(cleaned)` -- the MODEL BODY. What the user receives is
`_render`'s output, which for a compute answer is `body + "\\n" + working`. So the guard is
correct, wired and firing (eval/results/control_fire_audit.json) and still never sees the text
that ships. That is a FIFTH R26 shape: not inert, not unwired, not overbroad -- CHECKED AT THE
WRONG STAGE.

TWO SEPARATE LIMBS, and conflating them is how this gets fixed wrongly:

  LIMB 1 -- THE WORKING IS NEVER CHECKED. It is engine output, so checking it means checking
            `rates.py`'s constants against `fidelity.py`'s `_LEVY_RATES`. That is a real check
            (two independent tables that must agree) but it is NOT the defect D-FIDELITY-6 was
            built for, and blanking is the wrong response to an engine defect anyway.

  LIMB 2 -- THE SEAM. The rule is a +/-60-character proximity window. Concatenating body and
            working puts the END of one within 60 characters of the START of the other, so the
            CONCATENATION can produce an attribution that NEITHER SEGMENT CONTAINS. That cuts
            both ways: pre-render misses a body rate whose only nearby levy name is in the
            working (false negative), and post-render can flag a correct body+working pair on
            a seam artefact (FALSE POSITIVE -- the expensive direction, because this guard
            BLANKS).

WHY THIS IS MEASURED RATHER THAN REASONED. R17's clearest case in this repo is this very guard:
two candidate attribution rules were written, both wrong, and the corpus swept CLEAN for both --
only authored probes found either. A stage change is an attribution change. It gets the same
treatment.

POPULATION (R22). The committed rate-guard probe bodies, paired with REAL engine workings
produced by the production compute functions -- not hand-written strings. Both arms matter and
the one that matters MORE is the probes designed to come back CLEAN: 12 of the 16 rate_guard
probes are deliberately CORRECT bodies, and on the founding R17 case it was that half which
exposed both bad rules. A stage change that flags a correct body is the failure mode here.

NO MODEL IS INVOLVED. The engine is deterministic, so this measurement reproduces exactly.
"""
import json
import os
import sys
from decimal import Decimal

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from chike import fidelity                                    # noqa: E402
from chike.rules_engine.sdl import compute_sdl                 # noqa: E402
from chike.rules_engine.wcf import compute_wcf                 # noqa: E402
from chike.rules_engine.nssf import compute_nssf               # noqa: E402
from chike.rules_engine.paye import compute_paye               # noqa: E402

PROBES = os.path.join(REPO, "eval", "fidelity", "rate_guard_probes.jsonl")
OUT = os.path.join(REPO, "eval", "results", "rate_guard_stage_measurement.json")

# Real engine results, from the production compute functions. A levy's working is paired with a
# body about that levy so the rendered string is the one production would actually emit.
PAYROLL = Decimal("15000000")
WORKINGS = {
    "sdl": compute_sdl(PAYROLL, 25),
    "wcf": compute_wcf(PAYROLL),
    "nssf": compute_nssf(PAYROLL),
    "paye": compute_paye(Decimal("900000")),
}


def render(body: str, working: str) -> str:
    """EXACTLY Orchestrator._render's compute branch. Copied rather than imported because
    _render takes a SubAnswer; if that branch changes, this assertion-bearing copy must be
    updated with it, and test_rate_guard_stage pins the shape so it cannot drift silently."""
    body = body.strip()
    return f"{body}\n{working}" if body else working


def levy_of(probe) -> str:
    """Which engine working would accompany this body. Uses the probe's own declared levy where
    it has one, else the first levy the guard's OWN mark extractor finds -- never a guess."""
    declared = (probe.get("levy") or probe.get("computation") or "").lower()
    if declared in WORKINGS:
        return declared
    marks = fidelity._rate_levy_marks(probe.get("body", ""))
    for _, lv in marks:
        if lv in WORKINGS:
            return lv
    return "sdl"


def main():
    with open(PROBES, encoding="utf-8") as fh:
        probes = [json.loads(l) for l in fh if l.strip()]
    assert probes, "no rate-guard probes loaded -- the fixture moved or is empty"

    rows, changed = [], []
    for p in probes:
        body = p.get("body", "")
        levy = levy_of(p)
        working = WORKINGS[levy].working
        rendered = render(body, working)

        pre = fidelity.body_states_wrong_levy_rate(body)
        post = fidelity.body_states_wrong_levy_rate(rendered)
        work_only = fidelity.body_states_wrong_levy_rate(working)

        # Attribution diff tells us WHY a verdict moved -- a seam artefact shows up as an
        # attribution present in `rendered` but in neither segment alone.
        attr_body = set(map(tuple, fidelity.attributed_levy_rates(body)))
        attr_work = set(map(tuple, fidelity.attributed_levy_rates(working)))
        attr_rend = set(map(tuple, fidelity.attributed_levy_rates(rendered)))
        seam_only = sorted(str(x) for x in (attr_rend - attr_body - attr_work))
        lost = sorted(str(x) for x in ((attr_body | attr_work) - attr_rend))

        # FIELD NAME: the fixture uses `expect`, not `verdict`/`judgement`. The first run of this
        # harness read the latter, got None on every row, and therefore reported
        # "new_false_positives_on_correct_bodies: 0" -- while the two rows that moved were BOTH
        # false positives on correct bodies. The reassuring number came from a wrong key, in the
        # safe-looking direction. R26's second half, in my own instrument: when a control reports
        # clean, suspect the specimen first. Asserted below so it cannot recur silently.
        row = {"id": p.get("id"), "expected": p.get("expect"),
               "levy_paired": levy, "pre_render_flag": pre, "post_render_flag": post,
               "working_alone_flag": work_only,
               "verdict_moved": pre != post,
               "attributions_created_by_the_seam": seam_only,
               "attributions_destroyed_by_the_seam": lost,
               "body": body[:160]}
        rows.append(row)
        if pre != post:
            changed.append(row)

    # R20: this measurement must be able to say something other than "no change". If the guard
    # attributes nothing anywhere, every verdict is False==False and the run is vacuously clean.
    attributing = [r for r in rows if r["pre_render_flag"] or r["post_render_flag"]
                   or r["working_alone_flag"]]
    assert attributing, (
        "no probe produced a flag at ANY stage -- the guard attributed nothing, so this "
        "comparison is vacuous rather than clean (R20). Check the fixture's field names.")

    # R20/R26: the `expected` field must actually be populated, or every judgement below is made
    # against None and reports clean by construction. This is the assertion the first run lacked.
    unknown = [r["id"] for r in rows if r["expected"] in (None, "")]
    assert not unknown, (
        f"these probes have no `expect` field, so no verdict can be judged against them: "
        f"{unknown}. A harness that cannot read its fixture's expectation reports 0 false "
        f"positives whatever happens -- which is what the first run of this file did.")

    seam_rows = [r for r in rows if r["attributions_created_by_the_seam"]]
    CLEAN_EXPECT = ("clean", "pass", "ok", "correct", "no_flag", "not_flagged")
    false_pos = [r for r in changed if r["post_render_flag"] and not r["pre_render_flag"]
                 and str(r["expected"]).lower() in CLEAN_EXPECT]

    out = {
        "_what": "Does moving D-FIDELITY-6 from the model body to the rendered reply change any "
                 "verdict, and if so why?",
        "_population": {
            "rows": PROBES,
            "why_this_population": "the committed rate-guard probes are the only fixture whose "
                                   "rows were authored with a KNOWN correct/incorrect verdict "
                                   "per body, so a verdict move can be judged rather than "
                                   "merely counted. 12 of 16 are deliberately CORRECT bodies, "
                                   "which is the half that exposed both bad attribution rules "
                                   "on the founding R17 case.",
            "workings": "REAL ComputationResults from the production compute functions "
                        "(compute_sdl/wcf/nssf/paye), not hand-written strings",
        },
        "totals": {
            "probes": len(rows),
            "flagged_pre_render": sum(1 for r in rows if r["pre_render_flag"]),
            "flagged_post_render": sum(1 for r in rows if r["post_render_flag"]),
            "verdicts_moved": len(changed),
            "working_alone_flags": sum(1 for r in rows if r["working_alone_flag"]),
            "rows_with_seam_created_attributions": len(seam_rows),
            "new_false_positives_on_correct_bodies": len(false_pos),
        },
        "verdicts_moved": changed,
        "seam_rows": seam_rows,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(json.dumps(out["totals"], indent=2))
    if changed:
        print("\nVERDICTS THAT MOVED:")
        for r in changed:
            print(f"  {r['id']}: pre={r['pre_render_flag']} post={r['post_render_flag']} "
                  f"expected={r['expected']}")
            print(f"     seam created: {r['attributions_created_by_the_seam']}")
            print(f"     body: {r['body'][:120]}")
    else:
        print("\nno verdict moved at any probe")
    if seam_rows:
        print(f"\n⚠️ SEAM-CREATED ATTRIBUTIONS on {len(seam_rows)} row(s) -- attributions present "
              f"in the rendered text but in NEITHER segment alone")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
