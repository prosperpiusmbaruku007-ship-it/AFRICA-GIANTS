# -*- coding: utf-8 -*-
"""READ A NEW FULL-GATE ARTIFACT AGAINST THE COMMITTED PRE-REGISTRATION AND THE ENUMERATED BLAST RADIUS (2026-11-17; baseline c2143c0).

    python eval/controls/analyse_gate_vs_preregistration_2026_11_17.py eval/results/gate_production_<sha>.json

Prints, in this order (the order is the discipline):
  P0  IDENTITY: the serving-code verdict the run stamped on itself ("MEASURES THE SERVING CODE" or not), the index identity, the judge's state.
  P1  the CONTROL arm: rows whose prompt, route and model-free text are byte-identical to c2143c0. A verdict flip here FALSIFIES the enumeration (R12c step 2) -- EXCEPT a row whose GOLD KEY changed since
      c2143c0, which is listed on its own line (a key can move a verdict with no model change; the regex ignores the authority tail, the judge does not).
  P2  the model-free rows (route changed or model-free text changed).
  P3  the prompt-only rows: gains, and EVERY PASS->FAIL listed for hand reading.
  P4  KEY-ONLY movement: every row whose gold key changed after c2143c0, scored by the regex under the NEW key and under the OLD key (read out of the row's own `_scoring_key_correction` chain), so a
      key correction is never counted as model movement.
  then A1 / A2 / no-answer SEPARATELY (never netted), Gate 2's 16 OOC rows (a floor, not a held-out measure), and every confirmed-miss candidate with its route for the ROUTE / CORPUS / MODEL / GOLD
  classification BY HAND (read the served index row BEFORE calling one MODEL, R12b).
Writes eval/results/gate_vs_preregistration_2026_11_17.json. Exit 1 if the control arm is falsified.
"""
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
KEY_DATE = "2026-11-17"
GOLD_FILES = ("eval/accuracy_gate/eval_questions_001.jsonl", "eval/accuracy_gate/eval_questions_002_additions.jsonl", "eval/accuracy_gate/eval_questions_003.jsonl")


def L(p):
    return json.load(io.open(os.path.join(REPO, p) if not os.path.isabs(p) else p, encoding="utf-8"))


def ok(r):
    return str(r.get("pass")) == "True"


def key_changes():
    """{id: (current row, OLD key fields as of c2143c0)} for every gold row corrected on KEY_DATE; the old key is the DEEPEST entry of the correction chain dated KEY_DATE."""
    out = {}
    for rel in GOLD_FILES:
        for l in io.open(os.path.join(REPO, rel), encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            corr, old = r.get("_scoring_key_correction"), None
            while isinstance(corr, dict):
                if corr.get("date") == KEY_DATE and isinstance(corr.get("old"), dict):
                    old = corr["old"]
                corr = corr.get("earlier_correction")
            if old:
                out[r["id"]] = (r, old)
    return out


def main(path):
    from chike import scoring
    art = L(path)
    new = {r["id"]: r for r in art["rows"]}
    base = {r["id"]: r for r in L("eval/results/gate_production_c2143c0.json")["rows"]}
    blast = {r["id"]: r for r in L("eval/results/gate_blast_radius_2026_11_17.json")["rows"]}
    ids = [i for i in blast if i in new]
    assert len(ids) == 400, f"{len(ids)} rows joined"
    refusal = L("kaggle/chike_config.json").get("refusal_phrases", [])
    kc = key_changes()
    out = {"key_changed_rows": sorted(kc)}
    print("P0 IDENTITY")
    print("   serving verdict :", (art.get("serving_identity") or {}).get("verdict"))
    print("   gate commit     :", art.get("gate_commit"), "| github head:", art.get("github_head"), "| index facts:", art.get("index_facts"))
    out["P0"] = {"serving_verdict": (art.get("serving_identity") or {}).get("verdict"), "gate_commit": art.get("gate_commit"), "index_facts": art.get("index_facts")}

    un = [i for i in ids if not blast[i]["changed"]]
    un_nokey = [i for i in un if i not in kc]
    flips = [i for i in un_nokey if ok(new[i]) != ok(base[i])]
    key_flips = [i for i in un if i in kc and ok(new[i]) != ok(base[i])]
    textdiff = [i for i in un_nokey if (new[i].get("generated") or "") != (base[i].get("generated") or "")]
    out["P1_control"] = {"rows": len(un), "rows_without_key_change": len(un_nokey), "verdict_flips": flips, "reply_text_differs": len(textdiff), "falsified": bool(flips), "unchanged_rows_with_a_key_change_that_flipped": key_flips}
    print(f"\nP1 CONTROL ARM  unchanged rows {len(un)} ({len(un_nokey)} with an unchanged key)  verdict flips {len(flips)} {flips}  reply text differs in {len(textdiff)} (tolerance 3, none with a verdict change)")
    print(f"   unchanged-prompt rows whose KEY changed and whose verdict flipped (judge reads the key; NOT a falsification): {key_flips}")
    mf = [i for i in ids if blast[i]["route_changed"] or blast[i]["model_free_text_changed"]]
    out["P2_model_free"] = {i: {"baseline": ok(base[i]), "now": ok(new[i]), "judge_now": new[i].get("judge")} for i in mf}
    print("\nP2 MODEL-FREE ROWS", {i: (ok(base[i]), ok(new[i]), new[i].get("judge")) for i in mf})
    po = [i for i in ids if blast[i]["prompt_changed"] and not blast[i]["route_changed"] and not blast[i]["model_free_text_changed"]]
    gain = [i for i in po if not ok(base[i]) and ok(new[i])]
    loss = [i for i in po if ok(base[i]) and not ok(new[i])]
    out["P3_prompt_only"] = {"rows": len(po), "gains": gain, "losses": loss}
    print(f"\nP3 PROMPT-ONLY {len(po)}  gains {len(gain)}  losses {len(loss)}")
    for i in loss:
        print("   LOSS (READ BY HAND):", i, "| key changed" if i in kc else "", "|", (new[i].get("generated") or "")[:220].replace("\n", " "))

    print("\nP4 KEY-ONLY MOVEMENT (regex, the row's NEW reply under the NEW key and under the OLD key)")
    out["P4_key_only"] = {}
    for i in sorted(kc):
        if i not in new:
            continue
        row, old = kc[i]
        base_q = {"id": i, "answer_type": row.get("answer_type")}
        gen = new[i].get("generated") or ""
        now_new = bool(scoring.score_question({**base_q, "correct_answer_sw": row["correct_answer_sw"], "correct_answer_en": row["correct_answer_en"]}, gen, refusal))
        now_old = bool(scoring.score_question({**base_q, **old}, gen, refusal))
        out["P4_key_only"][i] = {"regex_new_key": now_new, "regex_old_key": now_old, "judge_now": new[i].get("judge"), "harness_pass": ok(new[i]), "baseline_pass": ok(base[i])}
        print(f"   {i}: regex new key {now_new} | old key {now_old} | gate judge (new key) {new[i].get('judge')} | harness pass {ok(new[i])} | baseline pass {ok(base[i])}")

    inc = [i for i in ids if new[i].get("subdomain") != "out_of_corpus"]

    def tally(rows):
        n = len(rows)
        right = sum(ok(r) for r in rows)
        gi = [r for r in rows if r.get("guard_interventions") not in (None, "[]", [])]
        na = sum(1 for r in rows if str(r.get("clarified")) == "True" or str(r.get("refused")) == "True")
        return {"n": n, "A2_right": right, "A2": round(right / n, 4), "no_answer_or_clarified": na, "guard_rows": len(gi)}
    out["baseline_all"] = tally([base[i] for i in inc])
    out["now_all"] = tally([new[i] for i in inc])
    print("\nIN-CORPUS  baseline c2143c0", out["baseline_all"], "\n           now            ", out["now_all"])
    ooc = [i for i in ids if new[i].get("subdomain") == "out_of_corpus"]
    out["gate2_16_rows"] = {"n": len(ooc), "pass": sum(ok(new[i]) for i in ooc)}
    print("GATE 2 (the OOC rows in the 400 -- a floor, not a held-out measure):", out["gate2_16_rows"])
    miss = [i for i in inc if not ok(new[i])]
    out["misses"] = [{"id": i, "subdomain": new[i].get("subdomain"), "changed_by_enumeration": blast[i]["changed"], "key_changed": i in kc, "baseline_pass": ok(base[i]),
                      "judge": new[i].get("judge"), "guards": new[i].get("guard_interventions")} for i in miss]
    print(f"\nCONFIRMED-MISS CANDIDATES {len(miss)} -- classify by hand (ROUTE / CORPUS / MODEL / GOLD); read the served index row BEFORE calling one MODEL (R12b)")
    print(collections.Counter(new[i].get("subdomain") for i in miss).most_common(10))
    io.open(os.path.join(REPO, "eval", "results", "gate_vs_preregistration_2026_11_17.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if flips else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
