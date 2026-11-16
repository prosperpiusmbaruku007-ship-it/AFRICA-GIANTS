# -*- coding: utf-8 -*-
"""READ A NEW FULL-GATE ARTIFACT AGAINST THE COMMITTED PRE-REGISTRATION AND THE ENUMERATED BLAST RADIUS (2026-11-16).

    python eval/controls/analyse_gate_vs_preregistration_2026_11_16.py eval/results/gate_production_<sha>.json

Prints, in this order (the order is the discipline): P1 the CONTROL arm (unchanged-route/prompt rows -- any verdict flip falsifies the enumeration), P2 the model-free rows,
P3 flips inside the prompt-only rows (every PASS->FAIL listed for hand reading), then A1 / A2 / no-answer SEPARATELY (never netted) against the baseline, and the list of every
confirmed miss with its route, for the ROUTE / CORPUS / MODEL / GOLD classification by hand. Writes eval/results/gate_vs_preregistration_2026_11_16.json.
Exit 1 if the control arm is falsified.
"""
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def L(p):
    return json.load(io.open(os.path.join(REPO, p) if not os.path.isabs(p) else p, encoding="utf-8"))


def ok(r):
    return str(r.get("pass")) == "True"


def main(path):
    new = {r["id"]: r for r in L(path)["rows"]}
    base = {r["id"]: r for r in L("eval/results/gate_production_0e11c3d.json")["rows"]}
    blast = {r["id"]: r for r in L("eval/results/gate_blast_radius_2026_11_16.json")["rows"]}
    ids = [i for i in blast if i in new]
    assert len(ids) == 400, f"{len(ids)} rows joined"
    out = {}
    un = [i for i in ids if not blast[i]["changed"]]
    flips = [i for i in un if ok(new[i]) != ok(base[i])]
    textdiff = [i for i in un if (new[i].get("generated") or "") != (base[i].get("generated") or "")]
    out["P1_control"] = {"rows": len(un), "verdict_flips": flips, "reply_text_differs": len(textdiff), "falsified": bool(flips)}
    print(f"P1 CONTROL ARM  unchanged rows {len(un)}  verdict flips {len(flips)} {flips}  reply text differs in {len(textdiff)} (tolerance 3, none with a verdict change)")
    mf = [i for i in ids if blast[i]["route_changed"] or blast[i]["model_free_text_changed"]]
    out["P2_model_free"] = {i: {"baseline": ok(base[i]), "now": ok(new[i]), "judge_now": new[i].get("judge")} for i in mf}
    print("P2 MODEL-FREE ROWS", {i: (ok(base[i]), ok(new[i]), new[i].get("judge")) for i in mf})
    po = [i for i in ids if blast[i]["prompt_changed"] and not blast[i]["route_changed"] and not blast[i]["model_free_text_changed"]]
    gain = [i for i in po if not ok(base[i]) and ok(new[i])]
    loss = [i for i in po if ok(base[i]) and not ok(new[i])]
    out["P3_prompt_only"] = {"rows": len(po), "gains": gain, "losses": loss}
    print(f"P3 PROMPT-ONLY {len(po)}  gains {len(gain)} (predicted 6-12 of 31)  losses {len(loss)} (predicted 3-8 of 138)")
    for i in loss:
        print("   LOSS (READ BY HAND):", i, "|", (new[i].get("generated") or "")[:200].replace("\n", " "))
    inc = [i for i in ids if new[i].get("subdomain") != "out_of_corpus"]

    def tally(rows):
        n = len(rows)
        right = sum(ok(r) for r in rows)
        gi = [r for r in rows if r.get("guard_interventions") not in (None, "[]", [])]
        na = sum(1 for r in rows if str(r.get("clarified")) == "True" or str(r.get("refused")) == "True")
        return {"n": n, "A2_right": right, "A2": round(right / n, 4), "no_answer_or_clarified": na, "guard_rows": len(gi)}
    out["baseline_all"] = tally([base[i] for i in inc])
    out["now_all"] = tally([new[i] for i in inc])
    print("IN-CORPUS  baseline", out["baseline_all"], "\n           now     ", out["now_all"])
    ooc = [i for i in ids if new[i].get("subdomain") == "out_of_corpus"]
    out["gate2_16_rows"] = {"n": len(ooc), "pass": sum(ok(new[i]) for i in ooc)}
    print("GATE 2 (the 16 OOC rows in the 400 -- a floor, not a held-out measure):", out["gate2_16_rows"])
    miss = [i for i in inc if not ok(new[i])]
    out["misses"] = [{"id": i, "subdomain": new[i].get("subdomain"), "changed_by_enumeration": blast[i]["changed"], "baseline_pass": ok(base[i]),
                      "judge": new[i].get("judge"), "guards": new[i].get("guard_interventions")} for i in miss]
    print(f"CONFIRMED-MISS CANDIDATES {len(miss)} -- classify by hand (ROUTE / CORPUS / MODEL / GOLD); read the served index row BEFORE calling one MODEL (R12b)")
    print(collections.Counter(new[i].get("subdomain") for i in miss).most_common(10))
    io.open(os.path.join(REPO, "eval", "results", "gate_vs_preregistration_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if flips else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
