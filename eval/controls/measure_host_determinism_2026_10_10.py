# -*- coding: utf-8 -*-
"""HAS CROSS-HOST DETERMINISM DRIFTED? EVERY LIVE CANARY THIS PROJECT HAS RUN DEPENDS ON IT.

⛔ WHY THIS IS BEING ASKED NOW. On 2026-08-10 the v16 cutover was verified by comparing each
live reply **byte-for-byte** against `scratch/canary_expected_v16.json`, written BEFORE the
cutover from a harness run — and canaries 1 and 2 came back *"byte-identical to v15"*. That
procedure only works if the harness host and production produce the same bytes from the same
prompt.

On 2026-10-09 they did not. `eval_162` — a GN487A citizenship question untouched by anything
shipped that day, on an unchanged route, with a prompt proven byte-identical across the two
trees — differed between the `0e11c3d` gate reply and production by **one space**
(`ni'mgeni'` → `ni 'mgeni'`). One space is not a behavioural difference; it is evidence that
**the equality the canary procedure rests on no longer holds.**

⚠️ AND THAT MATTERS MORE THAN THE SPACE. A byte-for-byte cross-host canary that silently stops
being valid does not fail loudly — it produces a FALSE FAIL on a correct deploy, which is the
stale-pin shape, and the 2026-08-10 run already shows what that costs: eval_318's canary
"failed" against a malformed expectation and the deviation had to be chased down before the
deploy could be trusted. If the hosts now differ systematically, every future canary inherits
that cost on every row.

⛔ WHAT THIS MEASURES, AND WHAT IT CANNOT. It can only ask PRODUCTION, so it answers the half
that is answerable without a GPU here:

  * **SELF-DETERMINISM** — the same question asked N times on the same deployed build. If the
    replies are identical, production is deterministic and the Kaggle/Modal difference is
    SYSTEMATIC (image, library versions, GPU model, quantisation kernels), not sampling noise.
    A systematic difference is the worse finding for canary design, because it will not average
    out and it will appear on every row that happens to be sensitive.
  * **NOT the cause.** Naming the cause needs the two images side by side. This refuses to
    guess, per R30: a reachability/behaviour claim about one host is a claim about one request
    until it is re-tested on the other.

The questions are drawn from the rows that actually mattered: the one that exposed the drift
(`eval_162`), one the engine answers deterministically (so a difference there would implicate
the deterministic path, not the model), and one plain fact-path row.

Usage:  python eval/controls/measure_host_determinism_2026_10_10.py [--n 3]
Artifact: eval/results/host_determinism_2026_10_10.json  (written after every call)
Exit 0 if production is self-deterministic · 1 if it is not · 2 if not exercisable.
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "host_determinism_2026_10_10.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"

# ⛔ READ FROM THE COMMITTED CORPORA BY ID, never retyped (R26).
PROBES = {
    "eval_162": ("eval/accuracy_gate/eval_questions_001.jsonl",
                 "THE ROW THAT EXPOSED THE DRIFT. Unchanged route, prompt proven byte-identical "
                 "across both trees, subject (GN487A citizenship) untouched by anything shipped "
                 "— and it still differed from the gate reply by one space."),
    "eval_111": ("eval/accuracy_gate/eval_questions_001.jsonl",
                 "A ROW THE ENGINE ANSWERS DETERMINISTICALLY. Its reply is levy_rate_statement's "
                 "own string, so a difference HERE would implicate the deterministic path rather "
                 "than the model — a much larger finding, and the reason this probe is in."),
    "eval_089": ("eval/accuracy_gate/eval_questions_001.jsonl",
                 "A PLAIN FACT-PATH ROW, long enough for a small difference to have somewhere to "
                 "appear. One of the four whose text differed cross-host."),
}


def _question(qid, rel):
    for line in io.open(os.path.join(REPO, rel), encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r.get("id") == qid:
                return r["question_sw"]
    raise AssertionError(f"{qid} not found in {rel} — this harness is stale")


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (io.open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def ask(question, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                        # noqa: BLE001
        pass

    tok = token()
    if not tok:
        print("NO TOKEN — not exercisable. This is NOT a result.")
        return 2

    build = ""
    try:
        with urllib.request.urlopen(f"{HEALTH}", timeout=300) as r:
            build = json.loads(r.read().decode("utf-8")).get("build", "")
    except Exception as exc:                                                 # noqa: BLE001
        build = f"unreadable: {type(exc).__name__}"

    # The cross-host specimen, read from the gate artifact rather than described.
    gate = {r["id"]: r for r in json.load(
        io.open(os.path.join(REPO, "eval", "results", "gate_production_0e11c3d.json"),
                encoding="utf-8"))["rows"]}

    rows = []
    for qid, (rel, why) in PROBES.items():
        q = _question(qid, rel)
        rec = {"id": qid, "question": q, "why_this_probe": why,
               "gate_0e11c3d_reply": gate[qid]["generated"],
               "gate_reply_sha16": _sha(gate[qid]["generated"]),
               "calls": []}
        rows.append(rec)
        for i in range(args.n):
            try:
                reply = str(ask(q, tok).get("reply") or "")
                rec["calls"].append({"i": i, "sha16": _sha(reply), "len": len(reply),
                                     "reply": reply})
            except Exception as exc:                                         # noqa: BLE001
                rec["calls"].append({"i": i, "error": f"{type(exc).__name__}: "
                                                      f"{str(exc)[:160]}"})
            _save(rows, build, args.n)
        shas = {c.get("sha16") for c in rec["calls"] if "sha16" in c}
        rec["self_deterministic"] = (len(shas) == 1)
        rec["matches_gate_reply"] = (rec["gate_reply_sha16"] in shas) if shas else None
        _save(rows, build, args.n)
        print(f"  {qid:10s} self-deterministic={rec['self_deterministic']!s:5s} "
              f"matches_gate_reply={rec['matches_gate_reply']!s:5s} "
              f"distinct={len(shas)}/{len([c for c in rec['calls'] if 'sha16' in c])}")

    payload = _save(rows, build, args.n)
    print("\n" + payload["verdict"])
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    return 0 if payload["production_self_deterministic"] else 1


def _save(rows, build, n):
    done = [r for r in rows if "self_deterministic" in r]
    self_det = all(r["self_deterministic"] for r in done) if done else None
    cross = {r["id"]: r.get("matches_gate_reply") for r in done}
    drifted = [k for k, v in cross.items() if v is False]
    payload = {
        "_what": "is production self-deterministic, and does it still reproduce the gate "
                 "harness's replies byte-for-byte as it did on 2026-08-10?",
        "_why": ("the 2026-08-10 v16 cutover was verified by byte-for-byte comparison against "
                 "a harness-derived expectation, and two canaries came back 'byte-identical'. "
                 "That procedure is only valid while the harness host and production produce "
                 "the same bytes. On 2026-10-09 eval_162 differed by ONE SPACE on an unchanged "
                 "route with a prompt proven byte-identical across both trees."),
        "_what_this_cannot_say": ("the CAUSE. Naming it needs the Kaggle and Modal images side "
                                  "by side — library versions, GPU model, quantisation kernels. "
                                  "R30: do not write down a diagnosis that has not been tested."),
        "deployed_build": build, "calls_per_question": n,
        "production_self_deterministic": self_det,
        "reproduces_gate_reply": cross,
        "drifted_from_the_gate_harness": drifted,
        "verdict": (
            "NOT YET DETERMINED" if self_det is None else
            ("PRODUCTION IS SELF-DETERMINISTIC" + (
                " — and it NO LONGER reproduces the gate harness's bytes on "
                f"{drifted}. The difference is therefore SYSTEMATIC (image, library versions, "
                "GPU, quantisation), not sampling noise. ⛔ CONSEQUENCE: a byte-for-byte "
                "CROSS-HOST canary is no longer a valid check and will produce false FAILs on "
                "correct deploys. Within-host comparisons remain valid, which is what the "
                "prompt-identity method uses."
                if drifted else
                " — and it still reproduces the gate harness's bytes on every probe here, so "
                "the eval_162 difference is narrower than this probe set and needs its own "
                "specimen before anything is concluded."))
            if self_det else
            "⛔ PRODUCTION IS NOT SELF-DETERMINISTIC — the same question on the same build gave "
            "different bytes. That is a larger finding than cross-host drift: it means NO "
            "byte-for-byte canary is valid, including within-host, and every recorded 'live "
            "reply' in this project is one sample rather than the system's answer."),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    sys.exit(main())
