# -*- coding: utf-8 -*-
"""WHICH QUESTIONS DOES AN UNCOMMITTED CHANGE MOVE? (2026-11-16, R12c step 1/2: enumerate the blast radius from an instrument, and read every moved row.)

Every distinct question in the gate corpora and the committed probe sets (~1,070) is run through the REAL orchestrator with a capturing backend (returns "", so only model-free text -- engine
answers, fixed statements, clarifications, refusals, guard replacements -- is compared) in two trees, each in its OWN process (R24b): `--before` (default HEAD, in a throwaway `git worktree`)
and the WORKING TREE. Per question: intent, route, model-free text, and the sha256 of every prompt the model WOULD have received (so a change that only perturbs a model-path prompt is visible
too). Prints every question whose intent, text or prompt changed.

    python eval/controls/sweep_tree_diff_2026_11_16.py [--before HEAD] [--out eval/results/sweep_tree_diff_<tag>.json] [--tag NAME]
"""
import argparse, glob, hashlib, io, json, os, shutil, subprocess, sys, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QK = ("question_sw", "question", "q", "instruction", "prompt")


def questions():
    seen = {}
    for g in ("eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl", "eval/**/*probes*.jsonl", "eval/fidelity/*.jsonl", "eval/routing/*.jsonl"):
        for f in sorted(glob.glob(os.path.join(REPO, g), recursive=True)):
            for l in io.open(f, encoding="utf-8", errors="replace"):
                if not l.strip():
                    continue
                try:
                    r = json.loads(l)
                except Exception:                                        # noqa: BLE001
                    continue
                q = next((r[k] for k in QK if isinstance(r.get(k), str) and 6 < len(r[k]) < 600), None)
                if q:
                    seen.setdefault(q, os.path.relpath(f, REPO).replace("\\", "/"))
    return seen


def capture(tree, qs):
    sys.path.insert(0, tree)
    os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator
    from chike import pipeline_v15, routing
    cfg = json.load(io.open(os.path.join(tree, "kaggle", "chike_config.json"), encoding="utf-8"))
    npy = os.path.join(tree, "chike-inference", "rag_embeddings.npy"); txt = os.path.join(tree, "chike-inference", "rag_facts_text.json")
    single = pipeline_v15.V15Retriever(emb_path=npy, texts_path=txt, expected_fact_count=len(json.load(io.open(txt, encoding="utf-8"))))
    seen = []

    class C(ModelBackend):
        def generate(self, prompt, params=None):
            seen.append(prompt); return ""
    out = {}
    for q in qs:
        seen.clear()
        try:
            r = Orchestrator(backend=C(), retriever=single.retrieve_facts, system_prompt=cfg["system_prompt"]).answer(q)
            text, err = r.text or "", None
        except Exception as e:                                           # noqa: BLE001
            text, err = "", repr(e)[:160]
        out[q] = {"intent": routing.detect_intent(q), "text": text, "err": err, "prompts": [hashlib.sha256(p.encode("utf-8")).hexdigest()[:12] for p in seen]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture"); ap.add_argument("--qfile"); ap.add_argument("--before", default="HEAD"); ap.add_argument("--tag", default="work"); ap.add_argument("--show", type=int, default=400)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass
    if a.capture:
        print(json.dumps(capture(a.capture, json.load(io.open(a.qfile, encoding="utf-8"))), ensure_ascii=False)); return
    qs = questions(); tmp = tempfile.mkdtemp(prefix="sw_"); res = {}
    try:
        qf = os.path.join(tmp, "q.json"); io.open(qf, "w", encoding="utf-8").write(json.dumps(list(qs), ensure_ascii=False))
        for label, rev in (("before", a.before), ("after", None)):
            tree = REPO
            if rev:
                tree = os.path.join(tmp, label)
                assert subprocess.run(["git", "worktree", "add", "--detach", tree, rev], cwd=REPO, capture_output=True).returncode == 0
            me = os.path.join(tmp, f"_c_{label}.py"); shutil.copy(os.path.abspath(__file__), me)
            p = subprocess.run([sys.executable, me, "--capture", tree, "--qfile", qf], capture_output=True, text=True, encoding="utf-8", cwd=tree, env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONPATH=tree))
            if rev:
                subprocess.run(["git", "worktree", "remove", "--force", tree], cwd=REPO, capture_output=True)
            assert p.returncode == 0, p.stderr[-800:]
            res[label] = json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    moved = []
    for q in qs:
        b, n = res["before"][q], res["after"][q]
        what = [k for k in ("intent", "text", "prompts", "err") if b[k] != n[k]]
        if what:
            moved.append({"q": q, "src": qs[q], "changed": what, "before": {k: b[k] for k in ("intent", "text")}, "after": {k: n[k] for k in ("intent", "text")}})
    out = {"tag": a.tag, "before_rev": a.before, "n_questions": len(qs), "n_moved": len(moved), "moved": moved}
    io.open(os.path.join(REPO, "eval", "results", f"sweep_tree_diff_{a.tag}.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(qs)} questions, {len(moved)} moved vs {a.before}")
    for m in moved[: a.show]:
        print(f"\n[{'/'.join(m['changed'])}] {m['q'][:150]}\n   {m['src']}\n   BEFORE ({m['before']['intent']}): {m['before']['text'][:170]!r}\n   AFTER  ({m['after']['intent']}): {m['after']['text'][:170]!r}")


if __name__ == "__main__":
    main()
