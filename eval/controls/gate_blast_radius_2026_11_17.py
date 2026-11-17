# -*- coding: utf-8 -*-
"""THE ENUMERATED BLAST RADIUS OF EVERYTHING THAT HAS LANDED SINCE THE LAST FULL GATE (`0e11c3d`, 2026-10-09) -- computed, not recalled (R12c step 1).

WHY. The next full gate is justified as a BATCH instrument: the statement route, the 2026-11-13 coverage batch (24 new facts, 5 rewritten rows), the five fixed
statements, D-FIDELITY-9/10, the R44 section-number strips, three new rows and the WCF rewrite have all landed since. The gate cannot attribute; the pre-registration
therefore has to say WHICH ROWS CAN HAVE MOVED and in which directions. That set is a property of CODE and INDEX, so it is measured at the PROMPT level (R24b):

    same question, same route, same retrieved facts, same system prompt  ->  byte-identical prompt  ->  the same weights give the same reply.

Two trees (the gate's own `0e11c3d`, in a throwaway `git worktree`, and HEAD), each in its OWN process (never a module reload), each with ITS OWN committed index and
production's single-arm retriever (`pipeline_v15.V15Retriever`, top_k 3 -- exactly what the gate package builds). A capturing backend records every prompt the
orchestrator would send and returns "" so nothing generates. Per row: the route, the number of prompts, the prompt sha256, and the model-free text (a fixed statement,
an engine answer, a refusal) with its sha256.

A row is CHANGED if its prompt set or its model-free text differs. Joined with the baseline artifact (`eval/results/gate_production_c2143c0.json`: pass / judge / guard):
  * UNCHANGED rows cannot move (same prompt, same weights, same host family) -- predicted movement ZERO; any movement there falsifies the enumeration, and the harness for
    the gate says so (that is the control arm, R12c step 2).
  * CHANGED rows that FAILED at the baseline are the only rows that can GAIN: an upper bound on the A2 rise.
  * CHANGED rows that PASSED at the baseline are the only rows that can LOSE: the exposure.

    python eval/controls/gate_blast_radius_2026_11_17.py            # both arms
    python eval/controls/gate_blast_radius_2026_11_17.py --capture  # one arm, internal
Artifact: eval/results/gate_blast_radius_2026_11_17.json  (the model-free text and a prompt hash per row, both trees)
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "gate_blast_radius_2026_11_17.json")
BASELINE = "c2143c0"
BASELINE_ARTIFACT = os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json")


def _questions():
    out = []
    for rel, n in (("eval/accuracy_gate/eval_questions_001.jsonl", 200), ("eval/accuracy_gate/eval_questions_002_additions.jsonl", 50),
                   ("eval/accuracy_gate/eval_questions_003.jsonl", 150)):
        rows = [json.loads(l) for l in io.open(os.path.join(REPO, rel), encoding="utf-8") if l.strip()]
        assert len(rows) == n, (rel, len(rows))
        out += [{"id": r["id"], "question": r["question_sw"]} for r in rows]
    assert len(out) == 400
    return out


def capture(tree, questions):
    """Run INSIDE one tree."""
    sys.path.insert(0, tree)
    for mod in [m for m in list(sys.modules) if m == "chike" or m.startswith("chike.")]:
        del sys.modules[mod]
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from chike.model_abstraction import ModelBackend                     # noqa: PLC0415
    from chike.orchestrator import Orchestrator                          # noqa: PLC0415
    from chike import pipeline_v15, routing                              # noqa: PLC0415

    cfg = json.load(io.open(os.path.join(tree, "kaggle", "chike_config.json"), encoding="utf-8"))
    npy = os.path.join(tree, "chike-inference", "rag_embeddings.npy")
    txt = os.path.join(tree, "chike-inference", "rag_facts_text.json")
    n_facts = len(json.load(io.open(txt, encoding="utf-8")))
    single = pipeline_v15.V15Retriever(emb_path=npy, texts_path=txt, expected_fact_count=n_facts)
    seen = []

    class _Capture(ModelBackend):
        def generate(self, prompt, params=None):
            seen.append(prompt)
            return ""

    out = []
    for q in questions:
        seen.clear()
        orch = Orchestrator(backend=_Capture(), retriever=single.retrieve_facts, system_prompt=cfg["system_prompt"])
        try:
            reply = orch.answer(q["question"])
            text, err = (reply.text or ""), None
        except Exception as e:                                           # noqa: BLE001
            text, err = "", repr(e)[:200]
        blob = "\n<<<PROMPT>>>\n".join(seen)
        out.append({"id": q["id"], "intent": routing.detect_intent(q["question"]), "n_prompts": len(seen),
                    "prompt_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "text": text, "error": err})
    return {"tree": tree, "rows": out, "index_rows": n_facts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--tree", default=REPO)
    ap.add_argument("--questions")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass
    if args.capture:
        qs = json.load(io.open(args.questions, encoding="utf-8"))
        print(json.dumps(capture(args.tree, qs), ensure_ascii=False))
        return 0

    qs = _questions()
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    tmp = tempfile.mkdtemp(prefix="blast_")
    results = {}
    try:
        qf = os.path.join(tmp, "q.json")
        io.open(qf, "w", encoding="utf-8").write(json.dumps(qs, ensure_ascii=False))
        for label, rev in (("before", BASELINE), ("after", "HEAD")):
            wt = os.path.join(tmp, label)
            r = subprocess.run(["git", "worktree", "add", "--detach", wt, rev], cwd=REPO, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"[FATAL] worktree {rev}: {r.stderr[:300]}")
                return 2
            me = os.path.join(wt, "_blast_capture.py")
            shutil.copy(os.path.abspath(__file__), me)
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
            p = subprocess.run([sys.executable, me, "--capture", "--tree", wt, "--questions", qf], capture_output=True, text=True, cwd=wt, env=env)
            subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=REPO, capture_output=True)
            if p.returncode != 0:
                print(f"[FATAL] capture {label}: {p.stderr[-800:]}")
                return 2
            results[label] = json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    base = {r["id"]: r for r in json.load(io.open(BASELINE_ARTIFACT, encoding="utf-8"))["rows"]}
    b_by = {r["id"]: r for r in results["before"]["rows"]}
    rows = []
    for a in results["after"]["rows"]:
        b = b_by[a["id"]]
        route_changed = a["intent"] != b["intent"]
        prompt_changed = a["prompt_sha256"] != b["prompt_sha256"]
        text_changed = a["text_sha256"] != b["text_sha256"]
        changed = route_changed or prompt_changed or text_changed
        br = base[a["id"]]
        status = ("PASS" if str(br.get("pass")) == "True" else "FAIL")
        rows.append({"id": a["id"], "intent_before": b["intent"], "intent_after": a["intent"], "route_changed": route_changed,
                     "prompt_changed": prompt_changed, "model_free_text_changed": text_changed, "changed": changed,
                     "n_prompts_before": b["n_prompts"], "n_prompts_after": a["n_prompts"],
                     "baseline_status": status, "baseline_judge": br.get("judge"), "baseline_guards": br.get("guard_interventions"),
                     "baseline_answer_type": br.get("answer_type"), "subdomain": br.get("subdomain"),
                     "text_after": a["text"] if text_changed else None})  # FULL text: a first run stored text[:300] and the scorer then failed eval_209 on a truncated reply
    ch = [r for r in rows if r["changed"]]
    un = [r for r in rows if not r["changed"]]
    summary = {
        "head": head, "baseline": BASELINE, "n": len(rows), "index_rows": {"before": results["before"]["index_rows"], "after": results["after"]["index_rows"]},
        "changed": len(ch), "unchanged": len(un),
        "changed_by_reason": {"route": sum(r["route_changed"] for r in ch), "prompt_only": sum(r["prompt_changed"] and not r["route_changed"] for r in ch),
                              "model_free_text_only": sum(r["model_free_text_changed"] and not r["prompt_changed"] and not r["route_changed"] for r in ch)},
        "changed_baseline": {"PASS": sum(r["baseline_status"] == "PASS" for r in ch), "FAIL": sum(r["baseline_status"] == "FAIL" for r in ch)},
        "unchanged_baseline": {"PASS": sum(r["baseline_status"] == "PASS" for r in un), "FAIL": sum(r["baseline_status"] == "FAIL" for r in un)},
        "errors": sum(1 for r in results["after"]["rows"] if r["error"]) + sum(1 for r in results["before"]["rows"] if r["error"]),
    }
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
