# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the three 2026-11-23 SDL statement routes (sdl_employee_premise, sdl_how_to_file_pay, sdl_nssf_party) and of the file/pay veto added to the older sdl_payer and sdl_exemptions routes.
Baseline = `chike/routing.py` AS COMMITTED at HEAD (a67462c-era), loaded from `git show` into a scratch module, so the comparison is code against code and nothing is hand-subtracted. Population = every question we hold (sweep_d18_routes.questions()).
Every question whose route or fixed-statement topic changed is printed with its source and is READ BY A PERSON (R17/R21: a falling or rising count is not a result). Also: how many questions carry two of the SDL topics at once (must be 0 = mutual exclusion).
    python eval/controls/sweep_sdl_three_routes_2026_11_23.py   ->  eval/results/sweep_sdl_three_routes_2026_11_23.json"""
import importlib.util, io, json, os, subprocess, sys, tempfile, types
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

NEW = ("sdl_employee_premise", "sdl_how_to_file_pay", "sdl_nssf_party")
SDL_TOPICS = ("sdl_payer", "sdl_exemptions") + NEW


def baseline_module(ref="HEAD"):
    src = subprocess.run(["git", "show", f"{ref}:chike/routing.py"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8")
    assert "sdl_employee_premise" not in src, "the baseline must predate the three routes"
    pkg = sys.modules["chike"]
    mod = types.ModuleType("chike._routing_baseline")
    mod.__package__ = "chike"
    mod.__file__ = os.path.join(tempfile.gettempdir(), "_routing_baseline.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def main():
    base = baseline_module()
    qs = questions()
    changed, per_topic = [], {t: 0 for t in SDL_TOPICS}
    for q, src in qs.items():
        b_int, a_int = base.detect_intent(q), routing.detect_intent(q)
        b_top, a_top = base.fixed_statement_topic(q), routing.fixed_statement_topic(q)
        if a_top in per_topic:
            per_topic[a_top] += 1
        if (b_int, b_top) != (a_int, a_top):
            changed.append({"q": q, "src": src, "before": [b_int, b_top], "after": [a_int, a_top]})
    both = [q for q in qs if len([t for t in routing.fixed_statement_topics(q) if t in SDL_TOPICS]) > 1]
    onto_new = [c for c in changed if c["after"][1] in NEW]
    off_old = [c for c in changed if c["before"][1] in ("sdl_payer", "sdl_exemptions") and c["after"][1] not in ("sdl_payer", "sdl_exemptions")]
    other = [c for c in changed if c not in onto_new and c not in off_old]
    print(f"{len(qs)} questions; {len(changed)} changed (route, topic); onto a NEW route {len(onto_new)}; OFF sdl_payer/sdl_exemptions {len(off_old)}; other {len(other)}; carrying 2+ SDL topics {len(both)}")
    print("topic membership now:", per_topic)
    for label, rows in (("ONTO NEW", onto_new), ("OFF OLD", off_old), ("OTHER", other)):
        for c in rows:
            print(f"  [{label}] {c['before']} -> {c['after']} [{c['src']}] {c['q'][:220]}")
    for q in both:
        print(f"  BOTH: {q[:200]}")
    out = {"swept": len(qs), "changed": changed, "onto_new": len(onto_new), "off_old": len(off_old), "other": len(other), "both": both, "membership": per_topic,
           "baseline": "git show HEAD:chike/routing.py"}
    io.open(os.path.join(REPO, "eval", "results", "sweep_sdl_three_routes_2026_11_23.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))


main()
