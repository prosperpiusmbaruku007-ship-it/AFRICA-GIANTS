# -*- coding: utf-8 -*-
r"""THREE QUESTIONS ABOUT THE QUARANTINES THAT NOBODY HAS ASKED, ONE OF THEM IN THE OPPOSITE
DIRECTION FROM EVERY AUDIT SO FAR.

Every quarantine audit in this repo asks the same thing: did the defective rows actually go? This
file asks three different ones, and the third is the one that matters most, because it is the only
one whose answer can be "we deleted correct data".

  ARM 1 — EDITED IN PLACE, RE-READ WHOLE. A quarantine that repairs a row instead of removing it
          leaves the quarantine record holding the PRE-EDIT text, so a body match reports the row
          as cleanly gone. 24 rows of the 2026-08-29 EFD quarantine were that, and EIGHT still
          asserted the fabrication three sentences after the repaired opening line. R25's
          containment shape: the symptom went, the defect stayed, so no later sweep was looking.
          So each edited row is re-read in FULL and re-classified on the claim.

  ARM 2 — THE INVISIBLE EDIT. `audit_quarantine_reach.py` detects an edit by finding the
          quarantined QUESTION live with a different body. A quarantine that edited the question
          TOO is therefore invisible to both of its outcomes — it is neither a survivor nor an
          edit, it is simply absent, which reads as success. Measured here by near-match instead
          of exact match, so the size of that blind spot is a number rather than an assumption.

  ⛔ ARM 3 — OVER-REMOVAL. THE AUDIT NOBODY HAS RUN, AND WE ALREADY KNOW IT HAS A HIT.
          The 2026-09-01 VAT-withholding sweep removed `train_sft:3196` because it contained
          `tarehe 20`. The row REJECTED the 20th — correct data, deleted by a presence check, a
          month before mention-vs-assertion was written down. That was found by accident while
          re-running a different quarantine. So: classify every quarantined body on the claim,
          polarity-aware, and count how many were MENTIONS rather than ASSERTIONS.

          **This is the direction an audit never looks, because its finding is an accusation
          against the remediation rather than the corpus.** A quarantine's record is the only
          evidence a row ever existed; if the removal was wrong, nothing downstream will ever say
          so — the row is gone, the count went down, and the write-up reads as progress.

The classifier is IMPORTED from the precondition re-derivation rather than re-written, because its
polarity rules, `lawful_attachment` escapes and 24 planted specimens are exactly what this arm
needs, and a second implementation would measure itself (R33).

Usage:  python eval/controls/audit_edit_in_place_and_overremoval_2026_10_07.py
Artifact: eval/results/edit_in_place_and_overremoval_audit_2026_10_07.json
"""
import collections
import difflib
import glob
import importlib.util
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARTIFACT = "eval/results/edit_in_place_and_overremoval_audit_2026_10_07.json"

LIVE_DIRS = [
    ("cleaned_pairs", "datasets/tier1a/cleaned_pairs"),
    ("sft_shaped_pairs", "datasets/tier1a/sft_shaped_pairs"),
    ("sft_EXPORTED_TRAINING", "datasets/tier1a/sft"),
    ("eval_set", "datasets/tier1a/eval_set"),
    ("adversarial", "datasets/tier1a/adversarial"),
]
QUARANTINE_GLOB = "datasets/tier1a/rejected/*.jsonl"
BODY_KEYS = ("output", "answer_sw", "response")
QKEYS = ("instruction", "question_sw", "question")


def _load_classifier():
    path = os.path.join(REPO, "eval", "controls",
                        "rederive_retrain_precondition_2026_10_07.py")
    assert os.path.exists(path), (
        "the claim classifier is missing. This audit must NOT fall back to a local "
        "re-implementation: a second copy of the polarity rules would be validated against "
        "itself (R33), and the whole point of arm 3 is that the rules are the ones with 24 "
        "planted specimens behind them.")
    spec = importlib.util.spec_from_file_location("precondition_classifier", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["precondition_classifier"] = mod
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def _norm(s):
    s = re.sub(r"[—–�’‘“”-]+", " ", s or "")
    return " ".join(s.split()).lower()


def _unwrap(o):
    return o["row"] if isinstance(o.get("row"), dict) else o


def _q(o):
    o = _unwrap(o)
    return next((o[k] for k in QKEYS if isinstance(o.get(k), str) and o[k].strip()), "")


def _b(o):
    o = _unwrap(o)
    return next((o[k] for k in BODY_KEYS if isinstance(o.get(k), str) and o[k].strip()), "")


def _rows(path):
    with io.open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except Exception:
                continue


def main():
    cls = _load_classifier()
    classify = cls.classify

    # Non-vacuity: the imported classifier must still pass its own specimens here, in THIS
    # process, before any verdict below is trusted. A borrowed instrument that silently fails
    # its own self-test would make every arm report clean.
    specimens = cls._self_test()
    print(f"imported classifier exercised: {len(specimens)} specimens\n")

    live_by_body, live_by_q, live_rows = {}, collections.defaultdict(list), 0
    for stage, rel in LIVE_DIRS:
        for path in sorted(glob.glob(os.path.join(REPO, *rel.split("/"), "*.jsonl"))):
            loc = os.path.relpath(path, REPO).replace(os.sep, "/")
            for n, o in _rows(path):
                body, q = _b(o), _q(o)
                if not body:
                    continue
                live_rows += 1
                live_by_body.setdefault(_norm(body), (stage, f"{loc}:{n}", q))
                live_by_q[_norm(q)].append((stage, f"{loc}:{n}", body))
    live_q_keys = list(live_by_q)
    print(f"live corpus rows indexed: {live_rows}")

    quarantined = []
    for path in sorted(glob.glob(os.path.join(REPO, *QUARANTINE_GLOB.split("/")))):
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for n, o in _rows(path):
            if _b(o):
                quarantined.append((rel, n, _q(o), _b(o)))
    assert quarantined, "zero quarantined rows with a body -- refusing to report clean"
    print(f"quarantined rows read:    {len(quarantined)}\n")

    arm1, arm2, arm3 = [], [], []
    for rel, n, q, body in quarantined:
        nb, nq = _norm(body), _norm(q)

        # ── ARM 3: was this row's REMOVAL justified? ─────────────────────────────────────
        verdicts = {c: v for c, v, _ in classify(q, body)}
        if verdicts and all(v == "MENTIONS_UNDER_NEGATION" for v in verdicts.values()):
            arm3.append({
                "quarantine_record": rel, "line": n, "question": q[:180], "body": body[:600],
                "classifier_verdict": verdicts,
                "reading": "every claim this body touches is NAMED UNDER NEGATION, i.e. the row "
                           "REJECTS the defect. On the claim-keyed, polarity-aware rules this "
                           "row was correct data and its removal was the defect.",
                "still_live_somewhere": nb in live_by_body,
            })

        if nb in live_by_body:
            continue                      # survivor -- audit_quarantine_reach.py's business

        # ── ARM 1: body gone, question live -> EDITED IN PLACE. Re-read whole. ──────────
        if nq in live_by_q:
            for stage, at, live_body in live_by_q[nq]:
                if _norm(live_body) == nb:
                    continue
                v = {c: ver for c, ver, _ in classify(q, live_body)}
                asserts = {c: ver for c, ver in v.items() if ver == "ASSERTS"}
                arm1.append({
                    "quarantine_record": rel, "line": n, "stage": stage, "at": at,
                    "question": q[:180],
                    "live_body_now": live_body,
                    "classifier_on_the_LIVE_body": v,
                    "verdict": "DEFECT_SURVIVED_THE_EDIT" if asserts else "REPAIRED",
                })
            continue

        # ── ARM 2: neither body nor question live. Did the question change too? ────────
        near = difflib.get_close_matches(nq, live_q_keys, n=1, cutoff=0.86)
        if near:
            stage, at, live_body = live_by_q[near[0]][0]
            ratio = difflib.SequenceMatcher(None, nq, near[0]).ratio()
            v = {c: ver for c, ver, _ in classify(q, live_body)}
            asserts = {c: ver for c, ver in v.items() if ver == "ASSERTS"}
            arm2.append({
                "quarantine_record": rel, "line": n, "stage": stage, "at": at,
                "quarantined_question": q[:180],
                "live_question_now": live_by_q[near[0]][0] and near[0][:180],
                "question_similarity": round(ratio, 3),
                "live_body_now": live_body[:600],
                "classifier_on_the_LIVE_body": v,
                "verdict": "DEFECT_SURVIVED_THE_EDIT" if asserts else "REPAIRED",
            })

    arm1_survived = [r for r in arm1 if r["verdict"] == "DEFECT_SURVIVED_THE_EDIT"]
    arm2_survived = [r for r in arm2 if r["verdict"] == "DEFECT_SURVIVED_THE_EDIT"]

    print("=" * 78)
    print(f"ARM 1  EDITED IN PLACE (question live, body changed): {len(arm1)} location(s), "
          f"{len({(r['quarantine_record'], r['at']) for r in arm1})} distinct")
    for r in arm1:
        mark = "⛔" if r["verdict"] == "DEFECT_SURVIVED_THE_EDIT" else "ok"
        print(f"  [{mark}] {r['at']}  <- {os.path.basename(r['quarantine_record'])}:{r['line']}")
        print(f"        {r['verdict']}  {r['classifier_on_the_LIVE_body'] or '(no class touched)'}")
    print(f"\n  defects surviving an edit: {len(arm1_survived)}")

    print(f"\nARM 2  INVISIBLE EDIT (question ALSO reworded, >=0.86 similarity): {len(arm2)}")
    for r in arm2:
        mark = "⛔" if r["verdict"] == "DEFECT_SURVIVED_THE_EDIT" else "ok"
        print(f"  [{mark}] sim={r['question_similarity']}  {r['at']}  "
              f"<- {os.path.basename(r['quarantine_record'])}:{r['line']}")
    print(f"\n  defects surviving an invisible edit: {len(arm2_survived)}")

    print(f"\nARM 3  OVER-REMOVAL — quarantined rows that REJECT the claim: {len(arm3)}")
    for r in arm3:
        print(f"  ⛔ {os.path.basename(r['quarantine_record'])}:{r['line']}  "
              f"{r['classifier_verdict']}  still_live={r['still_live_somewhere']}")
        print(f"       Q: {r['question'][:120]}")
        print(f"       A: {r['body'][:160]}")

    out = {
        "_what": "Three questions about the quarantines: did an edit-in-place keep the defect, "
                 "how big is the blind spot where the question was edited too, and were any "
                 "CORRECT rows removed.",
        "_why_this_population": (
            "Arms 1 and 2 cover every quarantined row whose body is no longer live -- the "
            "population audit_quarantine_reach.py scores as cleanly gone. Arm 3 covers every "
            "quarantined row, because the question it asks is about the REMOVAL and therefore "
            "applies to rows that left correctly as well."),
        "_what_this_cannot_show": (
            "Arm 2 is a similarity heuristic at 0.86 and will miss a question rewritten freely. "
            "Arm 3 inherits the classifier's 17 figure-testable classes: a quarantined row whose "
            "defect class is NOT figure-testable (stamp duty's flat-1% scope, the WCF 14+7 "
            "chain, P45/P9 terminology) produces no verdict and is counted in neither column -- "
            "it is unexamined, not cleared."),
        "classifier": "eval/controls/rederive_retrain_precondition_2026_10_07.py (imported, "
                      "self-test re-run in this process)",
        "live_rows_indexed": live_rows,
        "quarantined_rows_read": len(quarantined),
        "arm1_edited_in_place": arm1,
        "arm1_defects_surviving_an_edit": len(arm1_survived),
        "arm2_invisible_edit": arm2,
        "arm2_defects_surviving_an_edit": len(arm2_survived),
        "arm3_over_removal_correct_rows_deleted": arm3,
        "totals": {
            "edited_in_place_locations": len(arm1),
            "edited_in_place_defect_survived": len(arm1_survived),
            "invisible_edit_locations": len(arm2),
            "invisible_edit_defect_survived": len(arm2_survived),
            "over_removals": len(arm3),
        },
    }
    os.makedirs(os.path.join(REPO, "eval", "results"), exist_ok=True)
    with io.open(os.path.join(REPO, *ARTIFACT.split("/")), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nartifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
