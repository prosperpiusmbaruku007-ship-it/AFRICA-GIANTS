# -*- coding: utf-8 -*-
"""VALIDATE (and, once, FREEZE) the PRELIMINARY Gate 2 set. SEPARATE PROFILE from eval/refusal_gate/validate_heldout_set.py: that one demands 60 ooc + 30 controls from a HUMAN author and refuses any model author; this set is 26 rows
written by an EXTERNAL MODEL (ChatGPT) from the founder's prompt, reviewed by the claude.ai advisor session and approved by the founder -- weaker independence, recorded on every row. It is NOT the formal held-out set and must never be
passed off as one. The assistant (Claude Code) may not be the author of any question; it fills the six controls' correct answers from the locked facts (filled_by: claude_code) and nothing else.

    python eval/refusal_gate/preliminary/validate_prelim_set.py [--file PATH]   validate; exit 1 on any problem
    python eval/refusal_gate/preliminary/validate_prelim_set.py --freeze        validate, then write FROZEN_PRELIM.json (the file's sha256); the caller commits both BEFORE any live run
    python eval/refusal_gate/preliminary/validate_prelim_set.py --check-frozen  exit 1 if the file's bytes differ from FROZEN_PRELIM.json
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.join(HERE, "gate2_prelim_2026_11_22.jsonl")
FROZEN = os.path.join(HERE, "FROZEN_PRELIM.json")
AXES = ("unlisted_topic", "plain_words", "mixed", "other_jurisdiction", "not_compliance")
CATEGORY_AXES = {"OFF_TOPIC": {"not_compliance"}, "ADJACENT_NOT_COVERED": {"unlisted_topic"}, "TRICKY_LOOKALIKE": {"other_jurisdiction", "mixed", "plain_words"}, "IN_SCOPE_CONTROL": {"control"}}
LIMB_EXPECT = {"ooc": "REFUSE_OR_REFER", "hedge": "ANSWER_CURRENT_AND_HEDGE", "control": "ANSWER"}
KEYS = ("id", "n", "limb", "category", "axis", "axis_note", "question", "expect", "topic", "authored_by", "independence", "reviewed_by", "approved_by", "seen_system_output", "formal_set")
FORBIDDEN_AUTHOR = re.compile(r"claude_code|claude code|assistant|^claude$", re.IGNORECASE)
EXPECTED_COUNTS = {"ooc": 19, "hedge": 1, "control": 6}


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def validate(path):
    problems, rows = [], []
    if not os.path.exists(path):
        return [f"{path} does not exist"], rows
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception as e:                                           # noqa: BLE001
            problems.append(f"line {n}: not JSON ({e})")
            continue
        rows.append(r)
        miss = [k for k in KEYS if k not in r]
        if miss:
            problems.append(f"{r.get('id', n)}: missing {miss}")
            continue
        i = r["id"]
        q = str(r["question"]).strip()
        if not q or "<<" in q or ">>" in q or len(q) < 8:
            problems.append(f"{i}: question is empty, a placeholder, or too short")
        if r["limb"] not in LIMB_EXPECT or r["expect"] != LIMB_EXPECT[r["limb"]]:
            problems.append(f"{i}: expect {r['expect']!r} does not match limb {r['limb']!r}")
        if r["category"] not in CATEGORY_AXES or r["axis"] not in CATEGORY_AXES[r["category"]]:
            problems.append(f"{i}: axis {r['axis']!r} is not an allowed mapping for category {r['category']!r}")
        if not str(r["authored_by"]).startswith("external_model:") or FORBIDDEN_AUTHOR.search(str(r["authored_by"])):
            problems.append(f"{i}: authored_by {r['authored_by']!r} must be 'external_model:<name>'; the assistant may not author a question")
        if "weaker independence" not in str(r["independence"]):
            problems.append(f"{i}: the weaker-independence note is missing")
        if r["formal_set"] is not False:
            problems.append(f"{i}: formal_set must be false -- this is NOT the formal held-out set")
        if r["seen_system_output"] is not False:
            problems.append(f"{i}: seen_system_output is not false (a set whose author saw Chike's replies is not preliminary-grade either)")
        if r["limb"] == "control":
            for k in ("correct_answer", "source", "filled_by", "flag"):
                if k not in r:
                    problems.append(f"{i}: control row missing {k}")
            if r.get("filled_by") != "claude_code":
                problems.append(f"{i}: filled_by must be claude_code")
            if not str(r.get("correct_answer", "")).strip() or not str(r.get("source", "")).strip():
                problems.append(f"{i}: control row needs a correct_answer and a source")
        elif any(k in r for k in ("correct_answer", "filled_by")):
            problems.append(f"{i}: only control rows carry a correct_answer")
    if len(rows) != 26:
        problems.append(f"{len(rows)} rows, need exactly 26")
    ids = [r.get("id") for r in rows]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    qs = [re.sub(r"\s+", " ", str(r.get("question", "")).strip().lower()) for r in rows]
    if len(qs) != len(set(qs)):
        problems.append("duplicate questions")
    for limb, want in EXPECTED_COUNTS.items():
        got = sum(1 for r in rows if r.get("limb") == limb)
        if got != want:
            problems.append(f"{got} {limb} rows, need {want}")
    return problems, rows


def check_frozen(path):
    if not os.path.exists(FROZEN):
        return ["no FROZEN_PRELIM.json: the set has not been frozen"]
    rec = json.load(io.open(FROZEN, encoding="utf-8"))
    if sha(path) != rec["sha256"]:
        return [f"the set's bytes differ from FROZEN_PRELIM.json ({sha(path)[:12]} != {rec['sha256'][:12]}): a frozen set is never edited"]
    return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=SET)
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--check-frozen", action="store_true")
    a = ap.parse_args(argv)
    if a.check_frozen:
        p = check_frozen(a.file)
        print("\n".join(p) or "frozen set unchanged")
        return 1 if p else 0
    problems, rows = validate(a.file)
    print(f"{len(rows)} rows; {len(problems)} problem(s)")
    for p in problems:
        print("  -", p)
    if problems:
        return 1
    if a.freeze:
        if os.path.exists(FROZEN):
            print("already frozen:", FROZEN)
            return 1
        rec = {"file": os.path.basename(a.file), "sha256": sha(a.file), "rows": len(rows), "frozen_utc": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
               "validator_sha256": sha(os.path.abspath(__file__)), "authored_by": sorted({r["authored_by"] for r in rows}),
               "counts": {k: sum(1 for r in rows if r["limb"] == k) for k in EXPECTED_COUNTS}, "formal_set": False,
               "_rule": "PRELIMINARY, n=26, external-model author (weaker independence). Frozen BEFORE any live run; never edited. NOT the formal held-out set."}
        io.open(FROZEN, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        print("frozen:", rec["sha256"][:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
