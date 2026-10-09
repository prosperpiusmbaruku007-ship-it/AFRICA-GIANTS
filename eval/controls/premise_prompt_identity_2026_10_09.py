# -*- coding: utf-8 -*-
"""DOES THE STATEMENT ROUTE CHANGE ANYTHING FOR A ROW WHOSE ROUTE DID NOT CHANGE?

Answered at the PROMPT level, locally, exactly, with no GPU and no network.

⛔ WHY THIS EXISTS: THE REPLY-COMPARISON TEST I BUILT CANNOT ANSWER IT, AND I SHOULD HAVE SEEN
THAT BEFORE RUNNING IT. `targeted_route_verification_2026_10_09.py` compares production replies
now against the `0e11c3d` gate artifact's `generated` field, and that field was **not produced by
production**: the gate builds its own `_Backend` and `Orchestrator` on the Kaggle GPU — its own
source calls it "the Kaggle twin of modal_app.ChikeModel._generate" — while production at the
time served build `3659a06`. So `reply_changed` conflates **three** differences:

    (a) the route change — the thing under test
    (b) every other code change between the gate's tree and HEAD, including index row 9
    (c) a different HOST and a different model-loading path entirely

**And the noise floor is demonstrably above zero.** `eval_162` is a GN487A citizenship question
with no connection to routing, to NSSF, or to anything shipped today, and it "moved" — by a
SINGLE SPACE (`ni'mgeni'` → `ni 'mgeni'`). A comparison whose smallest observed movement is one
space on an untouched subject cannot attribute a reworded sentence to a routing change. That is
R24's lesson arriving in a baseline rather than in an arm: **matching the output is not enough;
the INPUT has to match too, and here the input was a different machine running different code.**

⛔ SO THE PREMISE IS TESTED AS WHAT IT ACTUALLY IS — A CLAIM ABOUT CODE, NOT ABOUT REPLIES.

    If `detect_intent` returns the same thing before and after, the question takes the same
    path, so the orchestrator hands the model the SAME PROMPT. Under greedy decoding the same
    weights on the same prompt give the same reply. Therefore: compare the PROMPTS.

Two trees, one question list, **retrieval held fixed by construction** — the same constant fact
list on both sides, so the comparison isolates the CODE change and cannot be perturbed by the
index. A prompt-level difference is decisive; a prompt-level identity means the route change
cannot have altered that row's reply, whatever a cross-host reply diff says.

⚠️ WHAT THIS DELIBERATELY DOES NOT TEST, named rather than folded in: **the index term.** Row 9
was reworded in the same deploy, so for NSSF-adjacent rows the RETRIEVED CONTEXT can differ even
when the code path is identical. Measuring that needs the e5 model (`integration`-marked, and a
native segfault risk this file will not take on). It is a separate question with a separate
answer, and conflating the two is what produced the misleading verdict in the first place.

Usage:
    python eval/controls/premise_prompt_identity_2026_10_09.py            # both arms
    python eval/controls/premise_prompt_identity_2026_10_09.py --capture  # one arm, internal
Artifact: eval/results/premise_prompt_identity_2026_10_09.json
Exit 0 if every unchanged-route row's prompt is identical across the two trees · 1 if any differs
· 2 if the comparison could not be set up (NOT a pass).
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
OUT = os.path.join(REPO, "eval", "results", "premise_prompt_identity_2026_10_09.json")

# The commit immediately BEFORE the statement route landed, and the commit the route landed in.
# Read as names, asserted as ancestors, never assumed.
PRE_ROUTE = "e45b28f"
ROUTE_COMMIT = "7b15756"

# ⛔ A FIXED RETRIEVAL CONTEXT, IDENTICAL ON BOTH SIDES. Not an attempt to reproduce what
# production retrieves — that would need e5 and would reintroduce the index as a variable. The
# claim under test is "the ROUTE change does not alter an unchanged-route row's prompt", so
# retrieval is held constant and the only thing allowed to vary is the code.
FIXED_FACTS = (
    "NSSF sehemu ya mwajiri: mwajiri analipa asilimia 10, ikihesabiwa kwa mshahara ghafi wa "
    "mfanyakazi.",
    "SDL: asilimia 3.5 ya jumla ya mishahara, kwa mwajiri mwenye wafanyakazi 10 au zaidi.",
    "WCF: asilimia 0.5 ya jumla ya mishahara ghafi, inalipwa kwa Mamlaka ya WCF.",
)


def _questions():
    """The unchanged-route rows of the targeted population, read from ITS artifact.

    Read rather than re-derived: a second implementation of "which rows had an unchanged route"
    could disagree with the first without either being obviously wrong, which is the defect that
    let the 2026-10-07 dry run report SAFE while the real regen aborted.
    """
    p = os.path.join(REPO, "eval", "results", "targeted_route_verification_2026_10_09.json")
    rows = json.load(io.open(p, encoding="utf-8"))["rows"]
    out = [{"id": r.get("id"), "question": r["question"],
            "arms": r["arms"], "moved_in_the_reply_diff": r.get("reply_changed")}
           for r in rows if r["intent_now"] == "none"]
    assert out, "no unchanged-route rows found — the artifact is stale or the join broke"
    # The four the reply diff flagged must be in here, or this test is not pointed at them.
    for i in ("eval_104", "eval_162", "eval_099", "eval_089"):
        assert any(r["id"] == i for r in out), f"{i} is missing from the unchanged-route set"
    return out


def capture(tree, questions):
    """Run INSIDE one tree: build each prompt and return its sha256 plus the text."""
    sys.path.insert(0, tree)
    for mod in [m for m in list(sys.modules) if m == "chike" or m.startswith("chike.")]:
        del sys.modules[mod]
    from chike.model_abstraction import ModelBackend                     # noqa: PLC0415
    from chike.orchestrator import Orchestrator                          # noqa: PLC0415
    from chike import routing                                            # noqa: PLC0415

    seen = []

    class _Capture(ModelBackend):
        def generate(self, prompt, params=None):
            seen.append(prompt)
            return ""

    out = []
    for q in questions:
        seen.clear()
        orch = Orchestrator(_Capture(), retriever=lambda _q: list(FIXED_FACTS),
                            ooc_phrases=[], in_scope_phrases=[])
        reply = orch.answer(q["question"])
        blob = "\n<<<PROMPT>>>\n".join(seen)
        out.append({
            "id": q["id"], "question": q["question"],
            "intent": routing.detect_intent(q["question"]),
            "n_prompts": len(seen),
            "prompt_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
            "prompt_len": len(blob),
            "deterministic_text_sha256": hashlib.sha256(
                (reply.text or "").encode("utf-8")).hexdigest(),
            "deterministic_text": reply.text or "",
        })
    return out


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

    # ── Arm A: HEAD, in process ─────────────────────────────────────────────────────────
    qs = _questions()
    head_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                              capture_output=True, text=True).stdout.strip()
    assert subprocess.run(["git", "merge-base", "--is-ancestor", ROUTE_COMMIT, "HEAD"],
                          cwd=REPO, capture_output=True).returncode == 0, (
        f"{ROUTE_COMMIT} is not an ancestor of HEAD, so HEAD is not a post-route tree")
    after = capture(REPO, qs)

    # ── Arm B: the pre-route tree, in a throwaway worktree and a SEPARATE PROCESS ───────
    # A separate process, not a module reload: `chike` has import-time state and reloading it
    # in-process is exactly the kind of half-swapped import that makes an arm agree with the
    # wrong thing (R24, four instances).
    tmp = tempfile.mkdtemp(prefix="premise_pre_route_")
    wt = os.path.join(tmp, "tree")
    before, err = None, None
    try:
        r = subprocess.run(["git", "worktree", "add", "--detach", wt, PRE_ROUTE],
                           cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            err = f"worktree add failed: {r.stderr[:300]}"
        else:
            qf = os.path.join(tmp, "q.json")
            io.open(qf, "w", encoding="utf-8").write(json.dumps(qs, ensure_ascii=False))
            me = os.path.join(wt, "_premise_capture.py")
            shutil.copy(os.path.abspath(__file__), me)
            p = subprocess.run([sys.executable, me, "--capture", "--tree", wt,
                                "--questions", qf],
                               capture_output=True, text=True, cwd=wt)
            if p.returncode != 0:
                err = f"pre-route capture failed: {p.stderr[-700:]}"
            else:
                before = json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=REPO,
                       capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)

    if before is None:
        print(f"[FATAL] {err}\nThe comparison could not be set up, which is NOT a pass.")
        payload = {"verdict": "NOT EXERCISABLE", "error": err}
        io.open(OUT, "w", encoding="utf-8", newline="\n").write(
            json.dumps(payload, ensure_ascii=False, indent=1))
        return 2

    b_by = {r["id"]: r for r in before}
    rows, diffs = [], []
    for a in after:
        b = b_by[a["id"]]
        same_prompt = a["prompt_sha256"] == b["prompt_sha256"]
        same_text = a["deterministic_text_sha256"] == b["deterministic_text_sha256"]
        row = {
            "id": a["id"], "question": a["question"],
            "intent_before": b["intent"], "intent_after": a["intent"],
            "prompt_identical": same_prompt,
            "deterministic_text_identical": same_text,
            "n_prompts_before": b["n_prompts"], "n_prompts_after": a["n_prompts"],
            "moved_in_the_cross_host_reply_diff": next(
                (q["moved_in_the_reply_diff"] for q in rows_q if q["id"] == a["id"]), None),
        }
        if not same_prompt:
            row["prompt_before"] = b.get("prompt_len")
            row["prompt_after"] = a.get("prompt_len")
            diffs.append(a["id"])
        if not same_text:
            row["text_before"] = b["deterministic_text"][:400]
            row["text_after"] = a["deterministic_text"][:400]
            if a["id"] not in diffs:
                diffs.append(a["id"])
        rows.append(row)

    payload = {
        "_what": "does the statement route alter anything for a row whose route did not change? "
                 "Answered at the prompt level, across two trees, with retrieval held fixed.",
        "_why_not_the_reply_diff": (
            "the targeted harness compares production replies now against the 0e11c3d GATE "
            "artifact, whose `generated` field was produced by the gate's OWN Kaggle backend "
            "(its source calls it 'the Kaggle twin of modal_app.ChikeModel._generate') while "
            "production then served build 3659a06. That diff therefore conflates the route, "
            "every other code change, and a different host — and its noise floor is "
            "demonstrably non-zero: eval_162, a GN487A row untouched by anything shipped today, "
            "'moved' by a single space."),
        "_what_is_held_fixed": (
            "retrieval. The same constant fact list is supplied on both sides, so the index "
            "cannot perturb the comparison. The index term is a SEPARATE question that needs e5 "
            "and is not answered here."),
        "trees": {"after": head_sha, "before": PRE_ROUTE, "route_landed_in": ROUTE_COMMIT},
        "n_rows": len(rows),
        "prompt_identical_for_all": not diffs,
        "rows_that_differ": diffs,
        "verdict": ("PREMISE HOLDS AT THE CODE LEVEL — every unchanged-route row gets a "
                    "byte-identical prompt before and after the route change, so the route "
                    "cannot have altered its reply. The reply differences seen against the "
                    "0e11c3d gate artifact are cross-host/cross-tree, not route effects."
                    if not diffs else
                    "PREMISE FALSIFIED AT THE CODE LEVEL — an unchanged-route row's prompt "
                    "changed. The blast radius is NOT bounded by the sweep and the full gate is "
                    "justified immediately."),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1))

    for r in rows:
        mark = "same" if r["prompt_identical"] and r["deterministic_text_identical"] else "DIFF"
        print(f"  [{mark}] {str(r['id']):14s} intent {r['intent_before']} -> {r['intent_after']}"
              f"  prompts {r['n_prompts_before']}/{r['n_prompts_after']}")
    print(f"\n{len(rows)} unchanged-route rows compared across {PRE_ROUTE} -> {head_sha}")
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    print(f"VERDICT: {payload['verdict']}")
    return 1 if diffs else 0


rows_q = []

if __name__ == "__main__":
    if "--capture" not in sys.argv:
        rows_q = _questions()
    sys.exit(main())
