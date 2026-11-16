# -*- coding: utf-8 -*-
"""VALIDATE (and, once, FREEZE) the held-out out-of-scope set for Gate 2. It checks SHAPE and PROVENANCE only -- it never reads a question for content and never writes one.

    python eval/refusal_gate/validate_heldout_set.py [--file PATH]     validate; exit 1 on any problem
    python eval/refusal_gate/validate_heldout_set.py --freeze          validate, then write heldout/FROZEN.json (the file's sha256) -- the caller commits both ALONE, before any measurement
    python eval/refusal_gate/validate_heldout_set.py --check-frozen    exit 1 if the authored file's bytes differ from FROZEN.json (a frozen set is never edited)

Rules (heldout/AUTHORING_INSTRUCTIONS.md): >= 60 ooc rows, >= 30 control rows, >= 8 ooc rows per axis, <= 3 rows per topic, no placeholder text, no duplicate questions, `expect` matches
`limb`, `authored_by` is one of founder / pilot_participant / other_person and NEVER the assistant, `seen_system_output` is a boolean (a True is allowed and recorded: the set is weaker, not invalid).
"""
import argparse
import collections
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HELD = os.path.join(HERE, "heldout")
AUTHORED = os.path.join(HELD, "heldout_outofscope_AUTHORED.jsonl")
FROZEN = os.path.join(HELD, "FROZEN.json")
AXES = ("unlisted_topic", "plain_words", "mixed", "other_jurisdiction", "not_compliance")
AUTHORS = ("founder", "pilot_participant", "other_person")
FORBIDDEN_AUTHORS = re.compile(r"assistant|claude|ai\b|model|gpt|bot", re.IGNORECASE)
MIN_OOC, MIN_CONTROL, MIN_PER_AXIS, MAX_PER_TOPIC = 60, 30, 8, 3
KEYS = ("id", "limb", "axis", "question", "expect", "topic", "authored_by", "author_note", "seen_system_output")


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
        q = str(r["question"]).strip()
        if not q or "<<" in q or ">>" in q or len(q) < 8:
            problems.append(f"{r['id']}: question is empty, a placeholder, or too short")
        if r["limb"] not in ("ooc", "control"):
            problems.append(f"{r['id']}: limb must be ooc or control")
        if (r["limb"], r["expect"]) not in (("ooc", "REFUSE"), ("control", "ANSWER")):
            problems.append(f"{r['id']}: expect {r['expect']!r} does not match limb {r['limb']!r}")
        if r["limb"] == "ooc" and r["axis"] not in AXES:
            problems.append(f"{r['id']}: ooc axis must be one of {AXES}")
        if r["limb"] == "control" and r["axis"] != "control":
            problems.append(f"{r['id']}: a control row's axis is 'control'")
        if r["authored_by"] not in AUTHORS or FORBIDDEN_AUTHORS.search(str(r["authored_by"])):
            problems.append(f"{r['id']}: authored_by {r['authored_by']!r} -- must be one of {AUTHORS}; the assistant may not author this set")
        if not isinstance(r["seen_system_output"], bool):
            problems.append(f"{r['id']}: seen_system_output must be true or false")
        if "<<" in str(r["topic"]):
            problems.append(f"{r['id']}: topic is a placeholder")
    ids = [r.get("id") for r in rows]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    qs = [re.sub(r"\s+", " ", str(r.get("question", "")).strip().lower()) for r in rows]
    if len(qs) != len(set(qs)):
        problems.append("duplicate questions")
    ooc = [r for r in rows if r.get("limb") == "ooc"]
    ctl = [r for r in rows if r.get("limb") == "control"]
    if len(ooc) < MIN_OOC:
        problems.append(f"{len(ooc)} ooc rows, need >= {MIN_OOC}")
    if len(ctl) < MIN_CONTROL:
        problems.append(f"{len(ctl)} control rows, need >= {MIN_CONTROL}")
    per_axis = collections.Counter(r.get("axis") for r in ooc)
    for ax in AXES:
        if per_axis.get(ax, 0) < MIN_PER_AXIS:
            problems.append(f"axis {ax}: {per_axis.get(ax, 0)} ooc rows, need >= {MIN_PER_AXIS}")
    per_topic = collections.Counter(str(r.get("topic", "")).strip().lower() for r in rows)
    for t, c in per_topic.items():
        if t and c > MAX_PER_TOPIC:
            problems.append(f"topic {t!r}: {c} rows, at most {MAX_PER_TOPIC}")
    return problems, rows


def check_frozen(path):
    if not os.path.exists(FROZEN):
        return ["no FROZEN.json: the set has not been frozen"]
    rec = json.load(io.open(FROZEN, encoding="utf-8"))
    if sha(path) != rec["sha256"]:
        return [f"the authored file's bytes differ from FROZEN.json ({sha(path)[:12]} != {rec['sha256'][:12]}): a frozen set is never edited -- a second iteration needs a NEW set from a new author"]
    return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=AUTHORED)
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
               "validator_sha256": sha(os.path.abspath(__file__)),
               "authors": sorted({r["authored_by"] for r in rows}), "seen_system_output_true": sum(1 for r in rows if r["seen_system_output"]),
               "_rule": "Commit this file and the authored set ALONE, before any measurement. Never edit the set; a second iteration needs a new set from a new author."}
        io.open(FROZEN, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        print("frozen:", rec["sha256"][:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
