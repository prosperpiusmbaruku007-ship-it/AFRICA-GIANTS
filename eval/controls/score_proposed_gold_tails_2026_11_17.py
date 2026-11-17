# -*- coding: utf-8 -*-
"""READ-ONLY: score the PROPOSED gold-key tail corrections (eval_116, 117, 120, 126; eval/results/tail_conflation_proposals_2026_11_17.json) beside the CURRENT keys, on the stored replies of the last two gates:
regex, and the project's pinned majority-of-5 judge. NOTHING in eval/accuracy_gate/ is edited. Writes eval/results/proposed_gold_tails_scored_2026_11_17.json after every row.

    python eval/controls/score_proposed_gold_tails_2026_11_17.py
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402  (2026-11-17: the artifact is written ATOMICALLY: temp file + os.replace)
from chike import fidelity, judge, scoring                                              # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "proposed_gold_tails_scored_2026_11_17.json")


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def main():
    key = os.environ.get("OPENROUTER_API_KEY", "")
    assert key, "OPENROUTER_API_KEY not set"
    props = L("eval/results/tail_conflation_proposals_2026_11_17.json")["gold"]
    refusal = L("kaggle/chike_config.json").get("refusal_phrases", [])
    gates = {"c2143c0": L("eval/results/gate_production_c2143c0.json"), "0e11c3d": L("eval/results/gate_production_0e11c3d.json")}
    out = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"rows": {}}
    for p in props:
        rid = p["id"]
        rec = out["rows"].setdefault(rid, {"question": p["question"], "old_sw": p["old_sw"], "new_sw": p["new_sw"], "scores": {}})
        for gname, g in gates.items():
            if gname in rec["scores"] and "judge_new_on_repaired" in rec["scores"][gname]:
                continue
            row = next((x for x in g["rows"] if x["id"] == rid), None)
            if not row:
                continue
            base = {"id": rid, "answer_type": p["answer_type"]}
            s = rec["scores"].get(gname) or {}
            s.update({"reply": row["generated"], "regex_old": bool(scoring.score_question({**base, "correct_answer_sw": p["old_sw"], "correct_answer_en": p["old_en"]}, row["generated"], refusal)),
                 "regex_new": bool(scoring.score_question({**base, "correct_answer_sw": p["new_sw"], "correct_answer_en": p["new_en"]}, row["generated"], refusal)), "stored_judge": row.get("judge")})
            if "judge_new" not in s:
                s["judge_old"] = judge.judge_majority(p["question"], p["old_sw"], row["generated"], api_key=key)
                s["judge_new"] = judge.judge_majority(p["question"], p["new_sw"], row["generated"], api_key=key)
            # THE FAIR ARM: the stored replies pre-date D-FIDELITY-14/18; production now repairs the authority tail before a reply is served, so the new key is also judged against the reply AS SERVED NOW
            repaired = fidelity.repair_firm_authority(p["question"], fidelity.repair_authority(p["question"], row["generated"]))
            s["reply_repaired_now"] = repaired
            s["judge_old_on_repaired"] = judge.judge_majority(p["question"], p["old_sw"], repaired, api_key=key)
            s["judge_new_on_repaired"] = judge.judge_majority(p["question"], p["new_sw"], repaired, api_key=key)
            rec["scores"][gname] = s
            atomic_artifact.write_json(OUT, out, ensure_ascii=False, indent=1)
    for rid, rec in out["rows"].items():
        for g, s in rec["scores"].items():
            print(rid, g, "regex old/new", s["regex_old"], s["regex_new"], "| judge old/new", s["judge_old"]["verdict"], s["judge_new"]["verdict"], s["judge_old"]["votes"], s["judge_new"]["votes"])


if __name__ == "__main__":
    main()
