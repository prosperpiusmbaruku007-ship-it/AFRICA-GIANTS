# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the medicines-VAT and PAYE-base statement routes. Baseline = `chike/routing.py` AS COMMITTED at 33cdb88 (the landing commit, before either route), loaded from `git show` into a scratch module: code against code, nothing hand-subtracted.
Population = every question we hold (sweep_d18_routes.questions()). Every question whose route or fixed-statement topic changed is printed with its source and READ BY A PERSON (a rising or falling count is not a result).
Also: how many questions carry two topics at once (must be 0 = mutual exclusion), and per-topic membership.
    python eval/controls/sweep_two_statements_2026_11_25.py   ->  eval/results/sweep_two_statements_2026_11_25.json"""
import io, json, os, subprocess, sys, tempfile, types
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

NEW = ("vat_medicines", "paye_base")


def baseline_module(ref="33cdb88"):
    src = subprocess.run(["git", "show", f"{ref}:chike/routing.py"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8")
    assert "vat_medicines" not in src and "paye_base" not in src, "the baseline must predate both routes"
    mod = types.ModuleType("chike._routing_baseline")
    mod.__package__ = "chike"
    mod.__file__ = os.path.join(tempfile.gettempdir(), "_routing_baseline.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def main():
    base = baseline_module()
    qs = questions()
    assert len(qs) > 8000, len(qs)                       # a loader returning nothing must fail, not pass vacuously (R20)
    changed, per_topic = [], {t: 0 for t in NEW}
    for q, src in qs.items():
        b_int, a_int = base.detect_intent(q), routing.detect_intent(q)
        b_top, a_top = base.fixed_statement_topic(q), routing.fixed_statement_topic(q)
        if a_top in per_topic:
            per_topic[a_top] += 1
        if (b_int, b_top) != (a_int, a_top):
            changed.append({"q": q, "src": src, "before": [b_int, b_top], "after": [a_int, a_top]})
    both = [q for q in qs if len(routing.fixed_statement_topics(q)) > 1 and len(base.fixed_statement_topics(q)) <= 1]
    onto_new = [c for c in changed if c["after"][1] in NEW]
    other = [c for c in changed if c not in onto_new]
    print(f"{len(qs)} questions; {len(changed)} changed (route, topic); onto a NEW route {len(onto_new)}; other {len(other)}; newly carrying 2+ topics {len(both)}")
    print("topic membership now:", per_topic)
    for label, rows in (("ONTO NEW", onto_new), ("OTHER", other)):
        for c in sorted(rows, key=lambda c: (c["after"][1] or "", c["q"])):
            print(f"  [{label}] {c['before']} -> {c['after']} [{c['src']}] {c['q'][:230]}")
    for q in both:
        print(f"  BOTH: {q[:200]}")
    out = {"swept": len(qs), "changed": changed, "onto_new": len(onto_new), "other": len(other), "newly_both": both, "membership": per_topic, "baseline": "git show 33cdb88:chike/routing.py"}
    io.open(os.path.join(REPO, "eval", "results", "sweep_two_statements_2026_11_25.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))


main()
