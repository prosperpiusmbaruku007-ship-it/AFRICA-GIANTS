# -*- coding: utf-8 -*-
"""WRITE THE PRE-REGISTRATION FOR THE FIFTH FULL GATE (baseline c2143c0, 2026-11-16; the 2026-11-17 pre-registration was for a gate that was never launched and is superseded, left untouched) FROM THE COMMITTED ARTIFACTS -- the numbers are COMPUTED, never typed (R12c, R18).

Inputs (all committed): eval/results/gate_production_c2143c0.json (baseline), gate_blast_radius_2026_11_25.json (prompt-level enumeration, c2143c0 -> 02f514d), gate_postgen_replay_2026_11_25.json (the same questions
replayed through the real Orchestrator in both trees with the baseline's STORED pre-clean model text: the post-generation layer's blast radius), and the CURRENT gold files (so the regex scoring of each
deterministic text uses today's keys). Output: eval/results/gate_preregistration_2026_11_25.json. Re-running it must reproduce the committed file byte for byte except `written_utc`.

    python eval/controls/make_gate_preregistration_2026_11_25.py
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
    blast = {r["id"]: r for r in L("eval/results/gate_blast_radius_2026_11_25.json")["rows"]}
    rep = {r["id"]: r for r in L("eval/results/gate_postgen_replay_2026_11_25.json")["rows"]}
    bsum = L("eval/results/gate_blast_radius_2026_11_25.json")["summary"]
    rsum = L("eval/results/gate_postgen_replay_2026_11_25.json")["summary"]
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
                    "regex_on_the_deterministic_text": regex, "predicted_clarified": bool(clarified), "predicted_regex_verdict": pred, "key_changed_2026_11_25": i in keyed,
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
        "_what": "The expectation for the FIFTH full gate (baseline c2143c0; the unlaunched 2026-11-17 pre-registration is superseded and untouched), written and COMMITTED BEFORE it is launched so the result cannot be read backwards into it. Check with `git log --diff-filter=A -- eval/results/gate_preregistration_2026_11_25.json` against the results artifact's add-commit. Generated by eval/controls/make_gate_preregistration_2026_11_25.py from committed artifacts.",
        "run": {"harness": "kaggle/eval_gate_production_2026_10_09.py (GitHub main at launch)", "n_questions": 400, "judge": "MANDATORY; the bracket is the headline, the regex figure beside it (R12b)", "index_rows": 224,
                "configuration": "production single-arm retriever over the 224-row index; D-FIDELITY-7..32 wired; 38 model-free fixed-statement topics live (plus the engines) (incl. the SDL/NSSF/PAYE party and base routes, the three-levy rate/deadline routes, medical VAT, medicines VAT, PAYE base, GN487A premise opener, NHIF/excise out-of-scope phrases, future-year rate, sector minimum wage); the fragment-merge decomposer; R44 strips in served text; gold keys as of 2026-11-17 (ten rows changed since the baseline: see key_only) PLUS the eval_203 correction, which lives in a sha-pinned SIDECAR the harness does not read (so its key is the OLD one in the run)",
                "NO_PUSH_WHILE_IT_RUNS": "the harness aborts on STALE CLONE; nothing may be pushed from launch until the artifact is committed"},
        "baseline": {"commit": "c2143c0", "in_corpus_raw": f"{b_pass}/{len(inc)} = {b_pass / len(inc):.1%}", "confirmed_false_passes_removed": "308/384 = 80.2%", "judge_augmented": "310/379 = 81.8% (bracket 75.7-81.8%)",
                     "hand_adjudicated": "78.9% / 76.8% with partials", "no_answer_or_clarified": 23, "gate2_16_rows": "16/16"},
        "enumerated_blast_radius": {"instruments": ["eval/controls/gate_blast_radius_2026_11_25.py (prompt level, route, model-free text; c2143c0 -> 02f514d)", "eval/controls/gate_postgen_replay_2026_11_25.py (the post-generation layer: the same questions replayed through the real Orchestrator in both trees with the baseline's stored pre-clean model text)"],
                                    "prompt_level": {k: bsum[k] for k in ("changed", "unchanged", "changed_by_reason", "changed_baseline", "unchanged_baseline", "index_rows")},
                                    "with_post_generation_layer": {k: rsum[k] for k in ("changed", "unchanged", "changed_by_reason", "changed_baseline", "unchanged_baseline")},
                                    "reading": f"{len(changed)} of 400 rows can have moved: {len(route)} by ROUTE, {len(textonly)} by the POST-GENERATION layer alone (prompt unchanged, served text changed), {len(prompt_only)} by PROMPT only (the index grew 211->224 and rows were rewritten). {len(control)} rows ({sum(base_pass[i] for i in control)} PASS / {sum(not base_pass[i] for i in control)} FAIL at baseline) have a byte-identical prompt AND a byte-identical served text and cannot move."},
        "predictions": {
            "P0_identity": "The artifact's own serving verdict must read 'MEASURES THE SERVING CODE' (chike/ at the gate commit byte-identical to chike/ at the serving commit). If it reads anything else the run is read as a batch of unknowns about a system production is not running.",
            "P1_control_arm": f"The {len(control)} control rows (excluding rows whose gold key changed since the baseline): ZERO pass/fail flips and at most 3 rows whose reply text differs. A flip here FALSIFIES the enumeration (R12c step 2); the analyser exits non-zero.",
            "P2_deterministic_rows": {"n": len(table), "rule": "scored BEFORE the run with the package's own scorer (chike.scoring) on the stored deterministic text and TODAY'S keys; a clarification is predicted a MISS because the harness scores every clarified row a miss", "gains_regex_FAIL_to_PASS": sorted(gains), "losses_regex_PASS_to_FAIL": sorted(losses), "net_regex": net_det, "rows": table},
            "P3_prompt_only": {"n": len(prompt_only), "baseline_FAIL": len(po_fail), "baseline_PASS": len(po_pass), "gains_predicted": f"0-{po_gain_hi}", "losses_predicted": f"0-{po_loss_hi}",
                               "basis": "the last gate's observed rates on the same kind of row (8 gains of 31 FAIL = 26%, 5 losses of 138 PASS = 3.6%), widened; EVERY PASS->FAIL is read by hand, R37"},
            "P4_key_only": {"rows": sorted(keyed), "regex": "UNCHANGED on all ten under old and new key (measured 2026-11-17: the regex ignores the authority tail)", "judge": "the judge reads the tail: measured on the stored replies, eval_135 and eval_120 go WRONG->CORRECT under the new key and eval_116 CORRECT->WRONG on an UNREPAIRED reply (CORRECT on the repaired one). Key-only judge movement is reported on its own line and never counted as model movement."},
            "P5_headline": {"point_estimate_in_corpus_raw_REGEX": f"{b_pass}/{len(inc)} -> about {(b_pass + net_det) / len(inc):.1%}", "band_raw_REGEX": f"{lo / len(inc):.1%} - {hi / len(inc):.1%}",
                           "READ_THIS_BEFORE_THE_NUMBER": "THE REGEX FIGURE IS NOT THE HEADLINE (R12b) AND ITS TOP MAY EXCEED 85%. At the baseline the regex said 83.1% where hand adjudication said 78.9% (80.2% with confirmed false passes removed): the regex credits wrong-direction and added-fabrication replies and has run 2.4-4.2 points ABOVE the adjudicated figure. A regex figure at or above 85% is therefore NOT a Gate 1 pass and must never be reported as one.",
                           "predicted_headline": "the judge BRACKET (lower = every queued false pass upheld, upper = every one adjudicated away), then HAND ADJUDICATION of the queue. Predicted adjudicated in-corpus: 80%-84% (the baseline's 78.9-80.2% plus the deterministic gains, minus the model-path defects found by reading since: see known_open). Gate 1 (85%) is NOT predicted to clear on the adjudicated or bracketed figure; if it does, that is a surprise to be explained row by row, not celebrated.",
                           "gate_1_85pct": "NOT predicted to clear (R7: 85% on the adjudicated figure); R7 also needs Gate 2, which no instrument here measures"},
            "P6_A1_and_A2_not_netted": "A1 (confident wrong), A2 (answered right) and the no-answer count are reported separately (a guard converts a wrong answer into a no-answer and moves A1 only). The 2026-11-17 pre-registration predicted eval_333/eval_353 as real A2 losses (the VAT two-amount regression); that was FIXED and verified live (PROGRESS 4aw), so they are predicted PASS here.",
            "P7_gate_2": "the 16 OOC rows in the 400: predicted 16/16, BUT the OOC phrase list WAS widened on 2026-11-22 (excise duty, ushuru wa bidhaa, verb-qualified NHIF phrases): any in-scope row refused by a widened phrase is a COLLISION and is read by name. A floor on an instrument with a known ~37x corpus-vs-held-out gap, NOT a Gate 2 measurement.",
        },
        "known_open_before_the_run": [
            "FOUND LIVE 2026-11-25, BY READING (eval/results/two_routes_deploy_live_2026_11_25.json), NOT FIXED, each predicted to recur where the question is in the 400: (1) 'Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?' -> 'Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated)': D-FIDELITY-32 did NOT fire, because the clause also carries 'si' (a negation cue vetoes the whole clause) -- a polarity limitation, queued; (2) 'Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?' -> 'kiwango cha VAT ni 18%': medicines charged at 18%, wrong for an exempt supply and outside D-FIDELITY-32 (it checks 'zero-rated', not '18%'); (3) the merged 'Huduma za afya zinatozwa VAT? Na dawa je?' answers ONLY the medicines limb (D-FIDELITY-32 replaced a model body with the medicines statement), so the medical-services limb is unanswered; a combined two-limb statement is queued as the next code-only fix; (4) the WCF base reply says 'posho zinazolipwa kila mwezi' where the fact says FIXED monthly allowances; (5) 'Nimefanya kazi mwaka mmoja ... malipo gani ya kuachishwa?' -> a bare 'unapaswa kulipwa ... Thibitisha na Ofisi ya Kazi (Ministry of Labour)' with no figure.",
            "SEVERANCE row 188 (the founder's accepted record): fails the regen's self-retrieval probe in every regen since the 211-row index (a probe artefact: rank 1, cosine 1.0, locally); six real phrasings rank [5,1,4,1,1,2] on BOTH the 220- and 224-row indexes. The TWO outside the top 3 are the VAGUE phrasings 'Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.' (rank 5) and 'Mfanyakazi aliyefanya kazi miezi 8 tu akiachishwa, hastahili malipo ya kuachishwa kazi, sivyo?' (rank 4); the English key:value fragment rows 154/156/157 absorb them. No rewrite clears all six (3 measured). 'miezi 12' and 'mwaka mmoja' rank 1.",
            "Rows whose new deterministic text is CORRECT but does not open with the polarity word the regex wants (eval_039, eval_392, eval_348): predicted regex FAIL, judge expected CORRECT. A scorer artefact, not a model defect.",
            "The harness scores every CLARIFIED row a miss whatever the gold says (the 2026-11-16 finding): A2 is understated; NOT changed, a scoring-policy decision.",
            "The eval_203 gold correction is a sha-pinned SIDECAR the harness does not read: the run scores it against the OLD key; the analyser must read it with the sidecar (eval/fidelity/negated_premise_heldout/rescore_with_sidecars_2026_11_17.py pattern).",
            "Supervised pilot only: no Gate 1/Gate 2 pass is claimed or implied by this run (R7 reading, CLAUDE.md); the supervision condition, not the gates, is what the pilot rests on.",
            "No retrain is planned; the Hugging Face copy of the repaired training pairs is not updated; training-corpus repairs of 2026-11-24/25 do not reach the served model (RAG-first, R10)."],
    }
    io.open(os.path.join(REPO, "eval", "results", "gate_preregistration_2026_11_25.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(pre, ensure_ascii=False, indent=1))
    print("changed", len(changed), "route", len(route), "text-only", len(textonly), "prompt-only", len(prompt_only), "control", len(control))
    print("deterministic rows", len(table), "gains", sorted(gains), "losses", sorted(losses), "net", net_det)
    print("prompt-only baseline FAIL/PASS", len(po_fail), len(po_pass), "| band", f"{lo}-{hi}", "of", len(inc), f"-> {lo / len(inc):.1%}-{hi / len(inc):.1%}", "point", f"{(b_pass + net_det) / len(inc):.1%}")
    for i, t in table.items():
        print(f"  {i:9} {t['route']:34} base {t['baseline']} judge {t['baseline_judge']} regex {t['regex_on_the_deterministic_text']} -> {t['predicted_regex_verdict'][:34]}")


if __name__ == "__main__":
    main()
