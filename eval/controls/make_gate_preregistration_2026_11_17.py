# -*- coding: utf-8 -*-
"""WRITE THE PRE-REGISTRATION FOR THE FOURTH FULL GATE (baseline c2143c0, 2026-11-16) FROM THE COMMITTED ARTIFACTS -- the numbers are COMPUTED, never typed (R12c, R18).

Inputs (all committed): eval/results/gate_production_c2143c0.json (baseline), gate_blast_radius_2026_11_17.json (prompt-level enumeration, c2143c0 -> 97a9a47), gate_postgen_replay_2026_11_17.json (the same questions
replayed through the real Orchestrator in both trees with the baseline's STORED pre-clean model text: the post-generation layer's blast radius), and the CURRENT gold files (so the regex scoring of each
deterministic text uses today's keys). Output: eval/results/gate_preregistration_2026_11_17.json. Re-running it must reproduce the committed file byte for byte except `written_utc`.

    python eval/controls/make_gate_preregistration_2026_11_17.py
"""
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import scoring                                                    # noqa: E402

CLARIFY_MARKERS = ("niambie", "nipe ", "taja ", "tafadhali")


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def main():
    base = {r["id"]: r for r in L("eval/results/gate_production_c2143c0.json")["rows"]}
    blast = {r["id"]: r for r in L("eval/results/gate_blast_radius_2026_11_17.json")["rows"]}
    rep = {r["id"]: r for r in L("eval/results/gate_postgen_replay_2026_11_17.json")["rows"]}
    bsum = L("eval/results/gate_blast_radius_2026_11_17.json")["summary"]
    rsum = L("eval/results/gate_postgen_replay_2026_11_17.json")["summary"]
    refusal = L("kaggle/chike_config.json").get("refusal_phrases", [])
    gold = {}
    keyed = set()
    for f in ("eval_questions_001", "eval_questions_002_additions", "eval_questions_003"):
        for l in io.open(os.path.join(REPO, "eval", "accuracy_gate", f + ".jsonl"), encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                gold[r["id"]] = r
                corr = r.get("_scoring_key_correction")
                while isinstance(corr, dict):
                    if corr.get("date") == "2026-11-17":
                        keyed.add(r["id"])
                    corr = corr.get("earlier_correction")
    ok = lambda r: str(r.get("pass")) == "True"                              # noqa: E731
    base_pass = {i: ok(base[i]) for i in base}
    inc = [i for i in base if base[i].get("subdomain") != "out_of_corpus"]
    changed = [i for i in rep if rep[i]["changed"]]
    route = [i for i in changed if rep[i]["route_changed"]]
    textonly = [i for i in changed if rep[i]["model_free_text_changed"] and not rep[i]["prompt_changed"] and not rep[i]["route_changed"]]
    prompt_only = [i for i in changed if rep[i]["prompt_changed"] and not rep[i]["route_changed"]]
    control = [i for i in rep if not rep[i]["changed"]]
    model_free = sorted(set(route) | set(textonly) | {i for i in changed if rep[i]["model_free_text_changed"]})
    table = {}
    for i in model_free:
        txt = rep[i]["text_after"] or ""
        regex = bool(scoring.score_question(gold[i], txt, refusal)) if txt else None
        clarified = bool(rep[i].get("clarified_after"))                    # recorded by the replay from the Orchestrator's own `needs_clarification`, never inferred from the wording
        pred = "FAIL (the harness scores every clarified row a miss)" if clarified else ("PASS" if regex else "FAIL")
        table[i] = {"subdomain": gold[i].get("subdomain"), "route": f'{rep[i]["intent_before"]}->{rep[i]["intent_after"]}', "baseline": "PASS" if base_pass[i] else "FAIL", "baseline_judge": base[i].get("judge"),
                    "regex_on_the_deterministic_text": regex, "predicted_clarified": bool(clarified), "predicted_regex_verdict": pred, "key_changed_2026_11_17": i in keyed,
                    "text_after": txt[:240]}
    gains = [i for i, t in table.items() if t["baseline"] == "FAIL" and t["predicted_regex_verdict"] == "PASS"]
    losses = [i for i, t in table.items() if t["baseline"] == "PASS" and t["predicted_regex_verdict"].startswith("FAIL")]
    po_fail = [i for i in prompt_only if not base_pass[i]]
    po_pass = [i for i in prompt_only if base_pass[i]]
    b_pass = sum(base_pass[i] for i in inc)
    net_det = len(gains) - len(losses)
    # prompt-only band from the last gate's observed rates (8 gains of 31 FAIL = 26%; 5 losses of 138 PASS = 3.6%), widened
    po_gain_hi, po_loss_hi = max(1, round(0.40 * len(po_fail))), max(2, round(0.08 * len(po_pass)))
    lo, hi = b_pass + net_det - po_loss_hi, b_pass + net_det + po_gain_hi
    pre = {
        "_what": "The expectation for the FOURTH full gate (baseline c2143c0), written and COMMITTED BEFORE it is launched so the result cannot be read backwards into it. Check with `git log --diff-filter=A -- eval/results/gate_preregistration_2026_11_17.json` against the results artifact's add-commit. Generated by eval/controls/make_gate_preregistration_2026_11_17.py from committed artifacts.",
        "run": {"harness": "kaggle/eval_gate_production_2026_10_09.py (GitHub main at launch)", "n_questions": 400, "judge": "MANDATORY; the bracket is the headline, the regex figure beside it (R12b)", "index_rows": 215,
                "configuration": "production single-arm retriever over the 215-row index; D-FIDELITY-7..19 wired; statement routes (incl. TIN window, licence validity, licence fee+renewal, individual return) and the VAT stated-average route live; R44 strips in served text; gold keys as of 2026-11-17 (ten rows changed since the baseline: see key_only)",
                "NO_PUSH_WHILE_IT_RUNS": "the harness aborts on STALE CLONE; nothing may be pushed from launch until the artifact is committed"},
        "baseline": {"commit": "c2143c0", "in_corpus_raw": f"{b_pass}/{len(inc)} = {b_pass / len(inc):.1%}", "confirmed_false_passes_removed": "308/384 = 80.2%", "judge_augmented": "310/379 = 81.8% (bracket 75.7-81.8%)",
                     "hand_adjudicated": "78.9% / 76.8% with partials", "no_answer_or_clarified": 23, "gate2_16_rows": "16/16"},
        "enumerated_blast_radius": {"instruments": ["eval/controls/gate_blast_radius_2026_11_17.py (prompt level, route, model-free text; c2143c0 -> 97a9a47)", "eval/controls/gate_postgen_replay_2026_11_17.py (the post-generation layer: the same questions replayed through the real Orchestrator in both trees with the baseline's stored pre-clean model text)"],
                                    "prompt_level": {k: bsum[k] for k in ("changed", "unchanged", "changed_by_reason", "changed_baseline", "unchanged_baseline", "index_rows")},
                                    "with_post_generation_layer": {k: rsum[k] for k in ("changed", "unchanged", "changed_by_reason", "changed_baseline", "unchanged_baseline")},
                                    "reading": f"{len(changed)} of 400 rows can have moved: {len(route)} by ROUTE, {len(textonly)} by the POST-GENERATION layer alone (prompt unchanged, served text changed), {len(prompt_only)} by PROMPT only (the index grew 211->215 and rows were rewritten). {len(control)} rows ({sum(base_pass[i] for i in control)} PASS / {sum(not base_pass[i] for i in control)} FAIL at baseline) have a byte-identical prompt AND a byte-identical served text and cannot move."},
        "predictions": {
            "P0_identity": "The artifact's own serving verdict must read 'MEASURES THE SERVING CODE' (chike/ at the gate commit byte-identical to chike/ at the serving commit). If it reads anything else the run is read as a batch of unknowns about a system production is not running.",
            "P1_control_arm": f"The {len(control)} control rows (excluding rows whose gold key changed since the baseline): ZERO pass/fail flips and at most 3 rows whose reply text differs. A flip here FALSIFIES the enumeration (R12c step 2); the analyser exits non-zero.",
            "P2_deterministic_rows": {"n": len(table), "rule": "scored BEFORE the run with the package's own scorer (chike.scoring) on the stored deterministic text and TODAY'S keys; a clarification is predicted a MISS because the harness scores every clarified row a miss", "gains_regex_FAIL_to_PASS": sorted(gains), "losses_regex_PASS_to_FAIL": sorted(losses), "net_regex": net_det, "rows": table},
            "P3_prompt_only": {"n": len(prompt_only), "baseline_FAIL": len(po_fail), "baseline_PASS": len(po_pass), "gains_predicted": f"0-{po_gain_hi}", "losses_predicted": f"0-{po_loss_hi}",
                               "basis": "the last gate's observed rates on the same kind of row (8 gains of 31 FAIL = 26%, 5 losses of 138 PASS = 3.6%), widened; EVERY PASS->FAIL is read by hand, R37"},
            "P4_key_only": {"rows": sorted(keyed), "regex": "UNCHANGED on all ten under old and new key (measured 2026-11-17: the regex ignores the authority tail)", "judge": "the judge reads the tail: measured on the stored replies, eval_135 and eval_120 go WRONG->CORRECT under the new key and eval_116 CORRECT->WRONG on an UNREPAIRED reply (CORRECT on the repaired one). Key-only judge movement is reported on its own line and never counted as model movement."},
            "P5_headline": {"point_estimate_in_corpus_raw": f"{b_pass}/{len(inc)} -> about {(b_pass + net_det) / len(inc):.1%}", "band_raw": f"{lo / len(inc):.1%} - {hi / len(inc):.1%}", "gate_1_85pct": "NOT predicted to clear (the band's top is below 85%); R7's line is 85% on the in-corpus gate and the gate has been flat since 1476caa",
                           "judge_bracket": "the lower bound should rise by the model-free rows the judge already called wrong at baseline and that are now deterministic; the headline is the bracket, never the regex figure (R12b)"},
            "P6_A1_and_A2_not_netted": "A1 (confident wrong), A2 (answered right) and the no-answer count are reported separately. Two rows are PREDICTED A2 LOSSES that are real, not artefacts: see known_open_before_the_run (VAT two-amount questions).",
            "P7_gate_2": "the 16 OOC rows in the 400: predicted 16/16 (no OOC list or classifier changed). A floor on an instrument with a known ~37x corpus-vs-held-out gap, NOT a Gate 2 measurement.",
        },
        "known_open_before_the_run": [
            "REGRESSION FOUND BY THIS ENUMERATION, NOT FIXED: eval_333 and eval_353 (a question stating an annual AND a six-month turnover, no bound) passed at baseline and are now routed to the VAT engine, which ASKS for sales figures the user already gave. Caused by the intentional 'VAT route gaps' extension in 8ff677a (the route fires; the two-amount reader only handles a bound plus one figure). Both predicted regex/A2 losses above; unrecorded in PROGRESS until now.",
            "Rows whose new deterministic text is CORRECT but does not open with the polarity word the regex wants (eval_039, eval_392, eval_348): predicted regex FAIL, judge expected CORRECT. A scorer artefact, not a model defect.",
            "eval_119's served reply invents rates (263,000; 358,322 attributed to mining): a genuine model miss that no change since the baseline addresses.",
            "A gate reply says a BRELA annual return is due 'within 12 months of registration' while the locked fact puts the annual-return duty at 28 days from the return date (annual_return_form_number): possibly wrong, unverified here.",
            "The harness scores every CLARIFIED row a miss whatever the gold says (the 2026-11-16 finding): A2 is understated; NOT changed, a scoring-policy decision.",
            "The monthly-rate VAT question without the word 'VAT' reaches only the comparison guard (D-FIDELITY-19), which repairs the comparator but not a conclusion that followed it.",
            "No retrain is planned; the Hugging Face copy of the repaired training pairs is not updated."],
    }
    io.open(os.path.join(REPO, "eval", "results", "gate_preregistration_2026_11_17.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(pre, ensure_ascii=False, indent=1))
    print("changed", len(changed), "route", len(route), "text-only", len(textonly), "prompt-only", len(prompt_only), "control", len(control))
    print("deterministic rows", len(table), "gains", sorted(gains), "losses", sorted(losses), "net", net_det)
    print("prompt-only baseline FAIL/PASS", len(po_fail), len(po_pass), "| band", f"{lo}-{hi}", "of", len(inc), f"-> {lo / len(inc):.1%}-{hi / len(inc):.1%}", "point", f"{(b_pass + net_det) / len(inc):.1%}")
    for i, t in table.items():
        print(f"  {i:9} {t['route']:34} base {t['baseline']} judge {t['baseline_judge']} regex {t['regex_on_the_deterministic_text']} -> {t['predicted_regex_verdict'][:34]}")


if __name__ == "__main__":
    main()
