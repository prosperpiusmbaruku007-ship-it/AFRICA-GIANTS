# -*- coding: utf-8 -*-
"""TARGETED VERIFICATION IN PLACE OF THE FOURTH FULL GATE (founder's decision 2026-11-17: "do NOT run the full gate ... per R12c a targeted verification is the right instrument").

WHY NOT THE FULL GATE (recorded here and in PROGRESS): the pre-registration (eval/results/gate_preregistration_2026_11_17.json + ADDENDUM_1) predicts a deterministic-row net of +2 (5 gains, 3 losses that are scorer artefacts) and a headline inside 82.8-84.1% -- i.e. the full gate could not
move the answer, and it cannot attribute. R12c: a single change's prediction is verified against its ENUMERATED BLAST RADIUS, and the premise (rows outside it cannot move) is tested with controls.

POPULATIONS, against the LIVE endpoint (chike-inference, build e9e429e):
  A. THE 56 BLAST-RADIUS ROWS (eval/results/gate_postgen_replay_2026_11_17.json `changed`): 10 route, 5 post-generation-only, 41 prompt-only. Scored under the CURRENT key with the harness's own rule (a clarified reply is a miss;
     chike.scoring.score_question otherwise) and, where a key changed on 2026-11-17, under the OLD key too; WITH THE JUDGE OVERLAY (chike.judge, pinned model, majority-of-5) on these 56 rows only.
  B. A SEEDED RANDOM SAMPLE OF 20 CONTROL-ARM ROWS (the 344 rows whose prompt, route and served text are byte-identical to c2143c0): the premise check. SEED RECORDED IN THE ARTIFACT. Any verdict flip is read by hand.

THE HOST CAVEAT (R24b), stated before the run so it cannot be argued afterwards: the c2143c0 replies were generated on the KAGGLE host; these are generated on PRODUCTION. Reply bytes are not comparable across the two (a measured one-space drift on an unchanged
row). A control-arm verdict flip therefore has two possible causes -- the enumeration is wrong (the prompt did change) or the host differs -- and the analyser separates them: a flip whose reply text is byte-identical modulo whitespace to the baseline's cannot be host drift.

Artifact is written after EVERY row; per-row errors are captured; a resume restores MEASUREMENTS (reply, path, calls, guards, judge votes) and RE-DERIVES every verdict (never carried).

    python eval/controls/verify_targeted_gate4_2026_11_17.py    ->  eval/results/targeted_gate4_2026_11_17.json
"""
import io
import json
import os
import random
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "targeted_gate4_2026_11_17.json")
SEED = 20261117
N_CONTROL = 20
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "e9e429e")
GOLD_FILES = ("eval_questions_001", "eval_questions_002_additions", "eval_questions_003")
KEY_DATE = "2026-11-17"


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def gold_rows():
    out = {}
    for f in GOLD_FILES:
        for l in io.open(os.path.join(REPO, "eval", "accuracy_gate", f + ".jsonl"), encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                out[r["id"]] = r
    return out


def old_key(row):
    """the key as it stood at c2143c0 for a row corrected on KEY_DATE: the DEEPEST correction entry dated KEY_DATE carries it in `old`"""
    corr, old = row.get("_scoring_key_correction"), None
    while isinstance(corr, dict):
        if corr.get("date") == KEY_DATE and isinstance(corr.get("old"), dict):
            old = corr["old"]
        corr = corr.get("earlier_correction")
    return old


def is_clarified(path):
    return any(seg == "clarification" or seg.endswith(":ask") for seg in (path or "").split("+"))


def verdicts(row, g, refusal, scoring):
    """re-derived EVERY run from the measured fields; the harness's own rule: a clarified reply is a miss"""
    clar = is_clarified(row.get("path"))
    gen = row.get("reply") or ""
    now = False if clar else bool(scoring.score_question(g, gen, refusal))
    ok_ = old_key(g)
    old = None if ok_ is None else (False if clar else bool(scoring.score_question({**g, **ok_}, gen, refusal)))
    return {"clarified": clar, "regex_pass_current_key": now, "regex_pass_old_key": old}


def main():
    import modal
    from chike import judge, scoring
    key = os.environ.get("OPENROUTER_API_KEY", "")
    assert key, "OPENROUTER_API_KEY not set (the judge overlay is mandatory on the 56 rows)"
    refusal = L("kaggle/chike_config.json").get("refusal_phrases", [])
    gold = gold_rows()
    rep = {r["id"]: r for r in L("eval/results/gate_postgen_replay_2026_11_17.json")["rows"]}
    blast_ids = sorted(i for i in rep if rep[i]["changed"])
    control_ids = sorted(i for i in rep if not rep[i]["changed"])
    assert len(blast_ids) == 56 and len(control_ids) == 344, (len(blast_ids), len(control_ids))
    sample = sorted(random.Random(SEED).sample(control_ids, N_CONTROL))
    plan = [(i, "blast") for i in blast_ids] + [(i, "control") for i in sample]
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    art.setdefault("seed", SEED)
    art.setdefault("control_sample", sample)
    art.setdefault("blast_ids", blast_ids)
    art.setdefault("rows", [])
    assert art["seed"] == SEED and art["control_sample"] == sample, "a resumed artifact must use the same seed and sample"
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["id"] for r in art["rows"]}
    save = lambda: io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))   # noqa: E731
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote()
        save()
    ident = art["identity"]
    print("served identity:", {k: ident.get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256")})
    assert ident.get("build") == EXPECT_BUILD, f"live build {ident.get('build')} != expected {EXPECT_BUILD}"
    t0 = time.time()
    for n, (i, arm) in enumerate(plan, 1):
        if i in done:
            continue
        g = gold[i]
        try:
            out = m.run.remote(g["question_sw"])
            row = {"id": i, "arm": arm, "reply": out.get("reply", ""), "path": out.get("path"), "model_calls": out.get("model_calls"), "guards": out.get("guards")}
        except Exception as e:                                           # noqa: BLE001
            row = {"id": i, "arm": arm, "error": repr(e)[:300]}
        if "reply" in row:
            if arm == "blast":
                try:
                    row["judge_current_key"] = judge.judge_majority(g["question_sw"], g["correct_answer_sw"], row["reply"], api_key=key)
                    ok_ = old_key(g)
                    if ok_:
                        row["judge_old_key"] = judge.judge_majority(g["question_sw"], ok_["correct_answer_sw"], row["reply"], api_key=key)
                except Exception as e:                                   # noqa: BLE001
                    row["judge_error"] = repr(e)[:200]
            row.update(verdicts(row, g, refusal, scoring))
        art["rows"].append(row)
        save()
        print(f"[{n}/{len(plan)}] {arm:7} {i} {row.get('path')} calls={row.get('model_calls')} {'ERR' if 'error' in row else ('PASS' if row.get('regex_pass_current_key') else 'miss')}  {time.time() - t0:.0f}s", flush=True)
    for r in art["rows"]:                                                # every verdict RE-DERIVED, never carried from a resumed row
        if "reply" in r:
            r.update(verdicts(r, gold[r["id"]], refusal, scoring))
    art["complete"] = len({r["id"] for r in art["rows"] if "reply" in r}) == len(plan)
    save()
    print(f"\n{len(art['rows'])} rows; complete={art['complete']}")
    sys.exit(0 if art["complete"] else 1)


if __name__ == "__main__":
    main()
