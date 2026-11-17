# -*- coding: utf-8 -*-
"""READ THE TARGETED-VERIFICATION ARTIFACT against the committed pre-registration + ADDENDUM 1 (2026-11-17).

    python eval/controls/analyse_targeted_gate4_2026_11_17.py     (reads eval/results/targeted_gate4_2026_11_17.json; writes eval/results/targeted_gate4_analysis_2026_11_17.json)

Order (the order is the discipline): P0 identity; P1 the CONTROL premise check (any verdict flip is listed, then SEPARATED into 'reply text identical modulo whitespace to the baseline' -- which CANNOT be host drift and so falsifies the
enumeration -- and 'reply text differs' -- which may be the Kaggle-vs-production host difference, R24b); P2 the predicted gains; P3 the predicted losses; P4 eval_333 / eval_353; P5 EVERY unpredicted movement among the 56, each with its reply
for reading by hand; P6 key-only movement; then A1 / A2 / no-answer for the 56, baseline beside now, never netted. A1 here is a CANDIDATE count (judge says wrong on a reply that is neither clarified nor refused): a hand reading decides.
"""
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def ws(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def verdict_of(j):
    return (j or {}).get("verdict") if isinstance(j, dict) else None


def main():
    art = L("eval/results/targeted_gate4_2026_11_17.json")
    live = {r["id"]: r for r in art["rows"] if "reply" in r}
    base = {r["id"]: r for r in L("eval/results/gate_production_c2143c0.json")["rows"]}
    pre = L("eval/results/gate_preregistration_2026_11_17.json")
    add = L("eval/results/gate_preregistration_2026_11_17_ADDENDUM_1.json")
    p2 = pre["predictions"]["P2_deterministic_rows"]
    gains = add["revised_P2_deterministic_rows"]["gains_regex_FAIL_to_PASS"]
    losses = add["revised_P2_deterministic_rows"]["losses_regex_PASS_to_FAIL"]
    blast = art["blast_ids"]
    ctl = art["control_sample"]
    bpass = lambda i: str(base[i].get("pass")) == "True"                  # noqa: E731
    out = {"seed": art["seed"], "control_sample": ctl}
    print("P0 IDENTITY:", {k: (art.get("identity") or {}).get(k) for k in ("build", "rag_rows_loaded")}, "| rows measured", len(live), "of", len(blast) + len(ctl), "| errors", sum(1 for r in art["rows"] if "error" in r))

    flips = [i for i in ctl if i in live and bool(live[i]["regex_pass_current_key"]) != bpass(i)]
    ident = [i for i in flips if ws(live[i]["reply"]) == ws(base[i].get("generated"))]
    out["P1_control"] = {"n": len([i for i in ctl if i in live]), "seed": art["seed"], "verdict_flips": flips, "flips_with_identical_text_modulo_whitespace": ident,
                         "text_differs_from_baseline": [i for i in ctl if i in live and ws(live[i]["reply"]) != ws(base[i].get("generated"))],
                         "enumeration_falsified": bool(ident)}
    print(f"\nP1 CONTROL PREMISE CHECK  n={out['P1_control']['n']}  seed={art['seed']}  verdict flips: {flips}")
    print(f"   flips with a reply IDENTICAL (modulo whitespace) to the baseline's -- cannot be host drift, FALSIFIES the enumeration: {ident}")
    print(f"   rows whose reply text differs at all from the Kaggle baseline (host drift is a candidate cause): {len(out['P1_control']['text_differs_from_baseline'])} of {out['P1_control']['n']}")
    for i in flips:
        print(f"   FLIP {i}: baseline {bpass(i)} -> live {live[i]['regex_pass_current_key']} | path {live[i].get('path')} | READ: {live[i]['reply'][:220]!r}\n        BASELINE: {(base[i].get('generated') or '')[:220]!r}")

    def line(i):
        r = live[i]
        return f"{i}: baseline {'PASS' if bpass(i) else 'FAIL'} -> live regex {'PASS' if r['regex_pass_current_key'] else 'FAIL'} (clarified {r['clarified']}) judge {verdict_of(r.get('judge_current_key'))} | {r.get('path')} calls={r.get('model_calls')} guards={r.get('guards')}"

    print("\nP2 PREDICTED GAINS (regex FAIL -> PASS)")
    out["P2_gains"] = {}
    for i in gains:
        hit = i in live and live[i]["regex_pass_current_key"] and not bpass(i)
        out["P2_gains"][i] = bool(hit)
        print(("  HIT  " if hit else "  MISS ") + (line(i) if i in live else i + " not measured"))
    print("\nP3 PREDICTED LOSSES (regex PASS -> FAIL; scorer artefacts / clarified policy)")
    out["P3_losses"] = {}
    for i in losses:
        hit = i in live and not live[i]["regex_pass_current_key"] and bpass(i)
        out["P3_losses"][i] = bool(hit)
        print(("  as predicted   " if hit else "  NOT as predicted ") + (line(i) if i in live else i + " not measured"))
    print("\nP4 eval_333 / eval_353 (addendum: predicted PASS)")
    out["P4_vat_pair"] = {i: bool(i in live and live[i]["regex_pass_current_key"]) for i in ("eval_333", "eval_353")}
    for i in ("eval_333", "eval_353"):
        print("  " + (line(i) if i in live else i + " not measured"))
    predicted = set(gains) | set(losses) | {"eval_333", "eval_353"}
    print("\nP5 EVERY UNPREDICTED MOVEMENT AMONG THE 56 (baseline verdict != live verdict) -- READ BY HAND")
    unpred = [i for i in blast if i in live and i not in predicted and bool(live[i]["regex_pass_current_key"]) != bpass(i)]
    out["P5_unpredicted"] = unpred
    for i in unpred:
        print("  " + line(i) + f"\n      LIVE    : {live[i]['reply'][:320]!r}\n      BASELINE: {(base[i].get('generated') or '')[:320]!r}")
    print(f"  ({len(unpred)} unpredicted)")
    print("\nP6 KEY-ONLY MOVEMENT (rows whose key changed on 2026-11-17): regex current key / old key, judge current / old")
    out["P6_key_only"] = {}
    for i in blast:
        r = live.get(i)
        if r and r.get("regex_pass_old_key") is not None:
            out["P6_key_only"][i] = {"regex_current": r["regex_pass_current_key"], "regex_old": r["regex_pass_old_key"], "judge_current": verdict_of(r.get("judge_current_key")), "judge_old": verdict_of(r.get("judge_old_key"))}
            print(f"  {i}: regex {r['regex_pass_current_key']}/{r['regex_pass_old_key']} | judge {verdict_of(r.get('judge_current_key'))}/{verdict_of(r.get('judge_old_key'))}")

    def tally(rows_live, rows_base):
        n = len(rows_live)
        a2 = sum(1 for r in rows_live if r["pass"])
        na = sum(1 for r in rows_live if r["no_answer"])
        a1c = sum(1 for r in rows_live if r["judge"] == "wrong" and not r["no_answer"])
        return {"n": n, "A2_pass": a2, "no_answer_clarified_or_refused": na, "A1_candidates_judge_wrong_and_answered": a1c, "judge_correct": sum(1 for r in rows_live if r["judge"] == "correct"),
                "judge_undetermined": sum(1 for r in rows_live if r["judge"] == "undetermined"), "judge_missing": sum(1 for r in rows_live if r["judge"] is None)}
    nowrows = [{"pass": bool(live[i]["regex_pass_current_key"]), "no_answer": bool(live[i]["clarified"]) or live[i].get("path") in ("refusal", "coverage_refusal"), "judge": verdict_of(live[i].get("judge_current_key"))} for i in blast if i in live]
    baserows = [{"pass": bpass(i), "no_answer": str(base[i].get("clarified")) == "True" or str(base[i].get("refused")) == "True", "judge": base[i].get("judge")} for i in blast if i in live]
    out["tally_56"] = {"baseline_c2143c0": tally(baserows, None), "live_e9e429e": tally(nowrows, None)}
    print("\nA1 / A2 / NO-ANSWER FOR THE 56 (separately, never netted; A1 is a candidate count, a hand reading decides)")
    print("  baseline c2143c0:", out["tally_56"]["baseline_c2143c0"])
    print("  live e9e429e   :", out["tally_56"]["live_e9e429e"])
    print("  paths of the 56 live:", collections.Counter((live[i].get("path") or "").split("+")[0] for i in blast if i in live).most_common(8))
    io.open(os.path.join(REPO, "eval", "results", "targeted_gate4_analysis_2026_11_17.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if out["P1_control"]["enumeration_falsified"] else 0


if __name__ == "__main__":
    sys.exit(main())
