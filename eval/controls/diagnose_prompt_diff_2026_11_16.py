# -*- coding: utf-8 -*-
"""WHAT DID THE 211-ROW REORDER DO TO ONE QUESTION'S PROMPTS? (2026-11-16, eval_318). Captures every prompt the orchestrator sends for a question in the baseline tree
(`gate_blast_radius_2026_11_16.BASELINE`, with ITS OWN committed index) and in HEAD, each in its own process (R24b), and prints the retrieved FACT lines per prompt side by side.

    python eval/controls/diagnose_prompt_diff_2026_11_16.py eval_318
"""
import io, json, os, subprocess, sys, tempfile, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASELINE = "0e11c3d"


def capture(tree, question):
    sys.path.insert(0, tree)
    os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator
    from chike import pipeline_v15
    cfg = json.load(io.open(os.path.join(tree, "kaggle", "chike_config.json"), encoding="utf-8"))
    npy = os.path.join(tree, "chike-inference", "rag_embeddings.npy"); txt = os.path.join(tree, "chike-inference", "rag_facts_text.json")
    n = len(json.load(io.open(txt, encoding="utf-8")))
    single = pipeline_v15.V15Retriever(emb_path=npy, texts_path=txt, expected_fact_count=n)
    seen = []

    class C(ModelBackend):
        def generate(self, prompt, params=None):
            seen.append(prompt); return ""
    Orchestrator(backend=C(), retriever=single.retrieve_facts, system_prompt=cfg["system_prompt"]).answer(question)
    return {"index_rows": n, "prompts": seen}


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--capture":
        print(json.dumps(capture(sys.argv[2], sys.argv[3]), ensure_ascii=False)); return
    qid = sys.argv[1]
    q = None
    for rel in ("eval_questions_001.jsonl", "eval_questions_002_additions.jsonl", "eval_questions_003.jsonl"):
        for l in io.open(os.path.join(REPO, "eval/accuracy_gate", rel), encoding="utf-8"):
            if l.strip() and json.loads(l)["id"] == qid:
                q = json.loads(l)["question_sw"]
    assert q, qid
    tmp = tempfile.mkdtemp(prefix="pd_"); res = {}
    try:
        for label, rev in (("before", BASELINE), ("after", "HEAD")):
            wt = os.path.join(tmp, label)
            assert subprocess.run(["git", "worktree", "add", "--detach", wt, rev], cwd=REPO, capture_output=True).returncode == 0
            me = os.path.join(wt, "_pd.py"); shutil.copy(os.path.abspath(__file__), me)
            p = subprocess.run([sys.executable, me, "--capture", wt, q], capture_output=True, text=True, cwd=wt, env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1"))
            subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=REPO, capture_output=True)
            assert p.returncode == 0, p.stderr[-600:]
            res[label] = json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = {"question": q, "baseline": BASELINE, "rows": {k: v["index_rows"] for k, v in res.items()}, "prompts": {k: v["prompts"] for k, v in res.items()}}
    json.dump(out, io.open(os.path.join(REPO, "eval", "results", f"prompt_diff_{qid}_2026_11_16.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for label in ("before", "after"):
        print(f"\n===== {label}  index rows {res[label]['index_rows']}  prompts {len(res[label]['prompts'])}")
        for i, pr in enumerate(res[label]["prompts"]):
            print(f"--- prompt {i}: {len(pr)} chars"); print(pr[-900:])


if __name__ == "__main__":
    main()
