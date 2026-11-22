# -*- coding: utf-8 -*-
"""RUN the PRELIMINARY Gate 2 set (26 rows) LIVE against production chike-inference and store the RAW output. It SCORES NOTHING: every verdict is assigned by hand afterwards, in
eval/results/gate2_prelim_scoring_2026_11_22.json (CORRECT_REFUSAL / LEAK / PARTIAL for the 19 out-of-scope rows, #20 separately, ANSWERED_CORRECTLY / WRONGLY_REFUSED / WRONG for the 6 controls), with a model judge only as a
second reader. REFUSES TO RUN unless the set validates AND its bytes equal FROZEN_PRELIM.json (frozen in git BEFORE any live run, R18).

Production path = the Modal SDK `ChikeModel.run`, i.e. classifier + retrieval + model + guards exactly as a WhatsApp question reaches them (the WhatsApp handler adds only review and delivery).
Artifact written ATOMICALLY after EVERY row, per-row errors captured, a resume re-asks only rows with an error and re-derives nothing (this harness derives no verdict).

    python eval/refusal_gate/preliminary/run_prelim_live_2026_11_22.py   ->  eval/results/gate2_prelim_live_2026_11_22.json
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "eval", "controls"))
import atomic_artifact  # noqa: E402
import validate_prelim_set as vps  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "gate2_prelim_live_2026_11_22.json")


def main():
    problems, rows = vps.validate(vps.SET)
    frozen = vps.check_frozen(vps.SET)
    if problems or frozen:
        print("REFUSING TO RUN:", problems + frozen)
        return 2
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["id"] for r in art["rows"]}
    save = lambda: atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote()
        art["set_sha256"] = vps.sha(vps.SET)
        art["note"] = "PRELIMINARY Gate 2 (n=26, external-model author, weaker independence). RAW output only; scored by hand in gate2_prelim_scoring_2026_11_22.json."
        save()
    print("served identity:", {k: art["identity"].get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256")})
    for r in rows:
        if r["id"] in done:
            continue
        try:
            out = m.run.remote(r["question"])
            row = dict(id=r["id"], n=r["n"], limb=r["limb"], category=r["category"], axis=r["axis"], question=r["question"], reply=out.get("reply", ""),
                       path=out.get("answer_path") or out.get("path"), model_calls=out.get("model_calls"), guards=out.get("guards"),
                       raw={k: v for k, v in out.items() if k != "reply" and isinstance(v, (str, int, float, bool, list, dict, type(None)))})
        except Exception as e:                                           # noqa: BLE001
            row = dict(id=r["id"], n=r["n"], limb=r["limb"], question=r["question"], error=repr(e)[:300])
        art["rows"].append(row)
        save()
        print(f"[{'ERR' if 'error' in row else 'ok '}] gp_{r['n']:02d} {r['limb']:<7} path={row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')}")
    errs = [r for r in art["rows"] if "error" in r]
    print(f"\n{len(art['rows'])} rows stored; {len(errs)} with an error (re-run to retry only those). NOTHING SCORED: read every reply.")
    return 1 if errs or len(art["rows"]) < len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
