# -*- coding: utf-8 -*-
"""DATED ADDENDUM 1 to the fourth-gate pre-registration (founder's instruction 2026-11-17: "add a DATED ADDENDUM ... don't rewrite the original"). eval/results/gate_preregistration_2026_11_17.json is NOT touched.

What changed AFTER the original was committed (cb66f9e): the VAT two-figure fix (e9e429e, `routing.turnover_pair_with_periods` + `registration_thresholds.vat_registration_both_limbs`) and a redeploy of chike-inference at e9e429e
(live /health build e9e429e, 215 rows, served digest == committed; eval/results/batch5_deploy_live_2026_11_17.json). eval_333 and eval_353 move from predicted LOSSES to predicted PASS. The post-fix text of each is the
ACTUAL text the real Orchestrator produces (not an inference), scored with the package's own scorer and today's keys. Everything else in the original stands. Output: eval/results/gate_preregistration_2026_11_17_ADDENDUM_1.json.

    python eval/controls/make_gate_preregistration_addendum_1_2026_11_17.py
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import scoring                                                    # noqa: E402
from chike.model_abstraction import ModelBackend                             # noqa: E402
from chike.orchestrator import Orchestrator                                  # noqa: E402


class _NoModel(ModelBackend):
    def generate(self, prompt, params=None):
        raise AssertionError("the two-figure VAT route must not call the model")


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def main():
    orig = L("eval/results/gate_preregistration_2026_11_17.json")
    gold = {}
    for f in ("eval_questions_001", "eval_questions_002_additions", "eval_questions_003"):
        for l in io.open(os.path.join(REPO, "eval", "accuracy_gate", f + ".jsonl"), encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                gold[r["id"]] = r
    refusal = L("kaggle/chike_config.json").get("refusal_phrases", [])
    base = {r["id"]: r for r in L("eval/results/gate_production_c2143c0.json")["rows"]}
    inc = [i for i in base if base[i].get("subdomain") != "out_of_corpus"]
    b_pass = sum(str(base[i].get("pass")) == "True" for i in inc)
    moved = {}
    for i in ("eval_333", "eval_353"):
        reply = Orchestrator(backend=_NoModel(), retriever=lambda *a, **k: [], system_prompt="x").answer(gold[i]["question_sw"])
        clar = bool(reply.needs_clarification)
        regex = bool(scoring.score_question(gold[i], reply.text, refusal))
        before = orig["predictions"]["P2_deterministic_rows"]["rows"][i]
        moved[i] = {"was_predicted": before["predicted_regex_verdict"], "now_predicted": "PASS" if (regex and not clar) else "FAIL", "clarified": clar, "regex_on_the_actual_text": regex, "model_calls": 0, "text": reply.text}
    p2 = orig["predictions"]["P2_deterministic_rows"]
    gains = sorted(p2["gains_regex_FAIL_to_PASS"])
    losses = sorted(set(p2["losses_regex_PASS_to_FAIL"]) - {i for i, m in moved.items() if m["now_predicted"] == "PASS"})
    net = len(gains) - len(losses)
    p3 = orig["predictions"]["P3_prompt_only"]
    hi_gain, hi_loss = int(p3["gains_predicted"].split("-")[1]), int(p3["losses_predicted"].split("-")[1])
    lo, hi = b_pass + net - hi_loss, b_pass + net + hi_gain
    add = {
        "_what": "DATED ADDENDUM 1 to gate_preregistration_2026_11_17.json (committed cb66f9e, NOT rewritten). Written and committed BEFORE the gate is launched. Check with `git log --diff-filter=A` for this file against the results artifact's add-commit.",
        "dated": "2026-11-17 (after cb66f9e, c027924)",
        "what_changed_since_the_original": [
            "e9e429e: the VAT engine tests an ANNUAL and a SIX-MONTH turnover figure given together, each against its OWN limb (eval_333 / eval_353 regressed at 8ff677a). Priced over 8,613 held questions (4 read as a pair, all genuine, every verdict correct); the bound+one-figure path, the stated-average path and the competing-cue ask are unchanged (tests/test_d20_vat_pair.py, 26).",
            "corporate_income_tax_return.wrong_patterns[0] narrowed off BRELA annual-return text (a sweep pattern; no runtime effect).",
            "chike-inference REDEPLOYED at e9e429e: pre-flight green, whatsapp pending 0, app stop + deploy, /health build e9e429e, 215 rows, served digest == committed (eval/results/batch5_deploy_live_2026_11_17.json, 14 rows, every reply read, 0 misses)."],
        "blast_radius_effect": "NONE on the enumerated set: eval_333 and eval_353 were already in the 10 route-changed rows (route none->vat_registration at 8ff677a); the fix changes their TEXT, not their membership. The control arm (344 rows) is unchanged. The pair reader fires on 4 of 8,613 held questions, 2 of them in the gate.",
        "identity": "P0 now expected to read 'MEASURES THE SERVING CODE': chike/ at the gate commit is byte-identical to chike/ at the serving commit e9e429e IF nothing under chike/ changes between e9e429e and launch (only eval/, tests/, kaggle/ runbook and PROGRESS commits follow).",
        "moved_rows": moved,
        "revised_P2_deterministic_rows": {"gains_regex_FAIL_to_PASS": gains, "losses_regex_PASS_to_FAIL": losses, "net_regex": net,
                                          "note": "the three remaining predicted losses are scorer artefacts or the known clarified-row policy, not model defects: eval_039 and eval_392 (the new statement is correct but lacks the polarity word the yes/no regex wants), eval_318 (SDL and NSSF answered, the VAT period asked)"},
        "revised_P5_headline": {"point_estimate_in_corpus_raw": f"{b_pass}/{len(inc)} -> about {(b_pass + net) / len(inc):.1%}", "band_raw": f"{lo / len(inc):.1%} - {hi / len(inc):.1%} ({lo}-{hi} of {len(inc)})",
                                "gate_1_85pct": "still NOT predicted to clear; the top of the band is below 85%",
                                "basis": "the original's prompt-only band (0-%d gains, 0-%d losses on %d rows) unchanged; only the deterministic-row net moved (original net %d -> %d)" % (hi_gain, hi_loss, p3["n"], p2["net_regex"], net)},
        "known_open_before_the_run_changes": ["REMOVED: the eval_333 / eval_353 VAT two-figure regression (fixed and verified live).",
                                              "ADDED, from the BRELA verification: a stored gate reply (eval_072: 'annual return ... hasa ndani ya miezi 12 kutoka tarehe ya usajili wake') states a deadline the Companies Act (Cap.212 R.E.2023) does not: the return is made up to the anniversary of incorporation and delivered within 28 days of that return date (s.131). The gold key is correct ('Mara moja kwa mwaka'); the reply is a possible A1 on that row. A constant guard is PROPOSED, not built."],
        "NO_PUSH_WHILE_IT_RUNS": "unchanged: nothing may be pushed from launch until the artifact is committed",
    }
    io.open(os.path.join(REPO, "eval", "results", "gate_preregistration_2026_11_17_ADDENDUM_1.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(add, ensure_ascii=False, indent=1))
    print(json.dumps({k: add[k] for k in ("revised_P2_deterministic_rows", "revised_P5_headline")}, ensure_ascii=False, indent=1))
    for i, m in moved.items():
        print(i, m["was_predicted"][:30], "->", m["now_predicted"], "| regex", m["regex_on_the_actual_text"], "| clarified", m["clarified"])


if __name__ == "__main__":
    main()
