# -*- coding: utf-8 -*-
"""READ-ONLY, the FACT-PATH restriction of price_unsupported_figure_hedge_2026_11_22.py (nothing is built or wired). The proposed hedge acts on the FACT path only; the compute path's figures are the ENGINE's arithmetic (multi-step results the
one-step support set cannot derive), so pricing it over compute replies counts the engine's correct numbers as "unsupported". This restricts the last full gate (c2143c0) to the 282 rows whose `compute` flag is false and reports, by the judge's verdict,
which replies the hedge WOULD touch -- and, the number that decides it, how many of the WRONG fact-path replies it would reach at all (recall).
    python eval/controls/price_unsupported_figure_hedge_fact_path_2026_11_22.py  ->  eval/results/price_unsupported_figure_hedge_fact_path_2026_11_22.json"""
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import price_unsupported_figure_hedge_2026_11_22 as p  # noqa: E402


def verdict(r):
    return r.get("judge") if r.get("judge") in ("wrong", "correct", "undetermined") else "none"


def main():
    idx, _ = p.load_index_numbers()
    g = json.load(io.open(os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json"), encoding="utf-8"))
    rows = [r for r in g["rows"] if isinstance(r.get("generated"), str)]
    fact = [r for r in rows if not r.get("compute")]
    stats, touched = p.judge([(r["question_sw"], r["generated"], r) for r in fact], idx)
    tot, hit = collections.Counter(verdict(r) for r in fact), collections.Counter(verdict(r) for _, _, r, _ in touched)
    ids = {r["id"] for _, _, r, _ in touched}
    art = {"gate": "c2143c0", "rows": len(rows), "fact_path_rows": len(fact), "stats": stats,
           "touched_by_judge_verdict": {k: {"touched": hit[k], "of": tot[k]} for k in tot},
           "recall_on_wrong_fact_path_replies": f"{hit['wrong']}/{tot['wrong']}", "wrong_fact_path_replies_not_touched": tot["wrong"] - hit["wrong"],
           "touched": [{"id": r["id"], "judge": r.get("judge"), "regex_pass": r.get("pass"), "unsupported": [f"{f[0]:g} ({f[1]})" for f in un], "reply": a[:240]} for _, a, r, un in touched],
           "note": "support set = question numbers + EVERY index row's numbers + one-step arithmetic: lenient, so unsupported counts are a LOWER bound; the preliminary Gate 2 set is burned and not used"}
    print(f"{len(fact)} fact-path rows of {len(rows)}; would touch {len(touched)}; by verdict: {art['touched_by_judge_verdict']}; recall on wrong: {art['recall_on_wrong_fact_path_replies']}")
    for t in art["touched"]:
        print(f"  {t['id']} judge={t['judge']} unsupported={t['unsupported']} | {t['reply'][:130]!r}")
    io.open(os.path.join(REPO, "eval", "results", "price_unsupported_figure_hedge_fact_path_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
