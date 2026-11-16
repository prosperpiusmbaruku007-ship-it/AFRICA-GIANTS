# -*- coding: utf-8 -*-
"""VALIDATE (and, once, FREEZE) the negated-premise probe set. SHAPE AND PROVENANCE ONLY: it never reads a question for meaning, never writes one, and never checks that a polarity is right (that is the `source` field's job
and a human's).

    python eval/fidelity/negated_premise_heldout/validate_negated_premise_set.py [--file PATH]    validate; exit 1 on any problem
    python eval/fidelity/negated_premise_heldout/validate_negated_premise_set.py --freeze         validate, then write FROZEN.json (the file's sha256) -- commit it with the authored set ALONE, before any measurement
    python eval/fidelity/negated_premise_heldout/validate_negated_premise_set.py --check-frozen   exit 1 if the authored file's bytes differ from FROZEN.json

AUTHORSHIP (founder's decision, 2026-11-16 -- supersedes the original "founder / pilot_participant / other_person only"):
  * `authored_by` is one of founder / pilot_participant / other_person / external_model.
  * `external_model` rows MUST also record `author_model` (the model's name), `author_session` (where it was written; "not recorded" is an honest value), `author_source` (free text), `reviewed_by`, and
    `independence: "weaker"` -- they are reported SEPARATELY and labelled weaker independence, never pooled silently with human-authored rows.
  * THE HARD RULE, unchanged in force: NO row may be authored by Claude Code (the assistant that builds and measures Chike). Any `authored_by` or `author_model` matching /claude code/ is refused. Claude as a model in a
    DIFFERENT session (e.g. the claude.ai advisor) is an external_model; Claude Code is not.
  * every row records `author_source`, whatever its class.
Other rules (AUTHORING_INSTRUCTIONS.md): >= 20 rows; >= 14 negated and >= 6 plain (`none`); among negated >= 6 true_premise and >= 6 false_premise and >= 3 negation forms; per-topic caps (default 4, VAT 5, labour 6 --
see TOPIC_CAPS); no placeholders; no duplicates; every row has a `source`. `correct_polarity` is YES / NO, or OPEN for a question that is not yes/no (then premise_label is `not_applicable`, negation_form `none` and
answer_kind `open`; the measure for such a row is whether the reply opens with Ndiyo/Hapana anyway).
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
AUTHORED = os.path.join(HERE, "negated_premise_AUTHORED.jsonl")
FROZEN = os.path.join(HERE, "FROZEN.json")
FORMS = ("si_kweli", "negative_verb", "tag_question", "double_negative", "belief_check", "none")
TOPICS = ("vat", "paye", "sdl", "nssf", "wcf", "efd", "brela", "osha", "gn487a", "gn605a", "labour", "licence", "tin", "records", "income_tax", "other")
AUTHORS = ("founder", "pilot_participant", "other_person", "external_model")
CLAUDE_CODE = re.compile(r"claude[\s_\-]*code", re.IGNORECASE)
MIN_ROWS, MIN_NEG, MIN_PLAIN, MIN_PER_LABEL, MIN_FORMS = 20, 14, 6, 6, 3
DEFAULT_TOPIC_CAP = 4
TOPIC_CAPS = {"vat": 5, "labour": 6}          # founder 2026-11-16: VAT 5. LABOUR 6 is the arithmetic consequence of re-filing ten `other` rows under real topics (six are labour-law rows, three of them a deliberate notice pair) -- flagged
KEYS = ("id", "question", "negation_form", "premise_label", "correct_polarity", "topic", "correct_answer_sw", "source", "authored_by", "author_note", "seen_system_output", "author_source")
EXTERNAL_KEYS = ("author_model", "author_session", "reviewed_by", "independence")


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
        rid = r["id"]
        for k in ("question", "correct_answer_sw", "source", "topic", "negation_form", "premise_label", "correct_polarity", "author_source"):
            if "<<" in str(r[k]) or ">>" in str(r[k]):
                problems.append(f"{rid}: {k} is a placeholder")
        if len(str(r["question"]).strip()) < 8:
            problems.append(f"{rid}: question is empty or too short")
        if len(str(r["source"]).strip()) < 6:
            problems.append(f"{rid}: no source -- a key without a primary source is not usable (R12b)")
        if len(str(r["author_source"]).strip()) < 6:
            problems.append(f"{rid}: no author_source -- every row must record where its question came from")
        if r["negation_form"] not in FORMS:
            problems.append(f"{rid}: negation_form must be one of {FORMS}")
        if r["topic"] not in TOPICS:
            problems.append(f"{rid}: topic must be one of {TOPICS}")
        if r["correct_polarity"] not in ("YES", "NO", "OPEN"):
            problems.append(f"{rid}: correct_polarity must be YES, NO or OPEN")
        if r["correct_polarity"] == "OPEN":
            if r["premise_label"] != "not_applicable" or r["negation_form"] != "none" or r.get("answer_kind") != "open":
                problems.append(f"{rid}: an OPEN row needs premise_label not_applicable, negation_form none and answer_kind open")
        else:
            if r["premise_label"] not in ("true_premise", "false_premise"):
                problems.append(f"{rid}: premise_label must be true_premise or false_premise (not_applicable is only for OPEN rows)")
        a = r["authored_by"]
        if a not in AUTHORS:
            problems.append(f"{rid}: authored_by {a!r} must be one of {AUTHORS}")
        if CLAUDE_CODE.search(str(a)) or CLAUDE_CODE.search(str(r.get("author_model", ""))) or CLAUDE_CODE.search(str(r.get("author_session", ""))):
            problems.append(f"{rid}: HARD RULE -- no row may be authored by Claude Code (the assistant that builds and measures Chike)")
        if a == "external_model":
            for k in EXTERNAL_KEYS:
                if not str(r.get(k, "")).strip():
                    problems.append(f"{rid}: an external_model row must record {k}")
            if r.get("independence") != "weaker":
                problems.append(f"{rid}: an external_model row must be labelled independence: weaker")
        if not isinstance(r["seen_system_output"], bool):
            problems.append(f"{rid}: seen_system_output must be true or false")
    ids = [r.get("id") for r in rows]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    qs = [re.sub(r"\s+", " ", str(r.get("question", "")).strip().lower()) for r in rows]
    if len(qs) != len(set(qs)):
        problems.append("duplicate questions")
    neg = [r for r in rows if r.get("negation_form") not in (None, "none")]
    plain = [r for r in rows if r.get("negation_form") == "none"]
    if len(rows) < MIN_ROWS:
        problems.append(f"{len(rows)} rows, need >= {MIN_ROWS}")
    if len(neg) < MIN_NEG:
        problems.append(f"{len(neg)} negated rows, need >= {MIN_NEG}")
    if len(plain) < MIN_PLAIN:
        problems.append(f"{len(plain)} plain control rows, need >= {MIN_PLAIN}")
    lab = collections.Counter(r.get("premise_label") for r in neg)
    for k in ("true_premise", "false_premise"):
        if lab.get(k, 0) < MIN_PER_LABEL:
            problems.append(f"{lab.get(k, 0)} negated {k} rows, need >= {MIN_PER_LABEL}")
    if len({r.get("negation_form") for r in neg}) < MIN_FORMS:
        problems.append(f"fewer than {MIN_FORMS} different negation forms among the negated rows")
    for t, c in collections.Counter(r.get("topic") for r in rows).items():
        cap = TOPIC_CAPS.get(t, DEFAULT_TOPIC_CAP)
        if t and c > cap:
            problems.append(f"topic {t!r}: {c} rows, at most {cap}")
    return problems, rows


def check_frozen(path):
    if not os.path.exists(FROZEN):
        return ["no FROZEN.json: the set has not been frozen"]
    rec = json.load(io.open(FROZEN, encoding="utf-8"))
    if sha(path) != rec["sha256"]:
        return [f"the authored file's bytes differ from FROZEN.json ({sha(path)[:12]} != {rec['sha256'][:12]}): a frozen set is never edited -- a second iteration needs a NEW set"]
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
               "validator_sha256": sha(os.path.abspath(__file__)), "authors": sorted({r["authored_by"] for r in rows}),
               "author_models": sorted({str(r.get("author_model", "")) for r in rows if r["authored_by"] == "external_model"}),
               "external_model_rows": sum(1 for r in rows if r["authored_by"] == "external_model"), "seen_system_output_true": sum(1 for r in rows if r["seen_system_output"]),
               "_rule": "Commit this file and the authored set ALONE, before any measurement. Never edit the set; a second iteration needs a new set."}
        io.open(FROZEN, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        print("frozen:", rec["sha256"][:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
