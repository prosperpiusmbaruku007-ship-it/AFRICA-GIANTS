# -*- coding: utf-8 -*-
"""TARGETED LIVE VERIFICATION OF THE STATEMENT ROUTE — instead of a full gate, and why.

⛔ THE FULL GATE IS NOT THE RIGHT INSTRUMENT FOR THIS CHANGE, by its own pre-registration.
`eval/results/gate_preregistration_statement_route_2026_10_09.json` predicts the regex headline
cannot move at all (7 of the 8 diverted rows were already scored as passes at `0e11c3d`) and the
judge's lower bound can move by at most three rows. **100 minutes of GPU to confirm a prediction
is not a measurement, it is a receipt.** The full gate is held until several changes have landed
together, so the expensive run attributes to something.

⛔ THE PREMISE UNDER TEST, STATED AS A FALSIFIABLE CLAIM:

    A ROW WHOSE ROUTE DID NOT CHANGE CANNOT HAVE CHANGED ITS ANSWER.

If that holds, the sweep has already enumerated the entire blast radius — 24 diversions over
2,473 questions — and checking those rows plus controls is not a sample, it is the population.
If it fails, the full gate is justified immediately and this harness says so in its own verdict.

⚠️ AND THE PREMISE HAS A SECOND TERM I CANNOT WISH AWAY: **this deploy also changed index row 9**
(`nssf_employer_rate`). So a moved answer on an unchanged route has TWO candidate causes, and
"the route" is excluded by construction, leaving the index. Rather than leave that as a confound
inside the control arm, the index gets its OWN arm — six unchanged-route NSSF rows, chosen
because their subject IS row 9's (does the employer's 10% come out of the wage, what the 10/10
split means). R22: the population a mechanism is measured on has to be the one it acts on.

THE FOUR ARMS, each with why-this-population recorded in the artifact:

  1. DIVERTED            — every row the sweep showed changing route. The only rows whose answer
                           CAN have changed, by the premise. Read by hand, judged against gold.
  2. THE_TWELVE          — the 12 confirmed defects of `0e11c3d`. Nine are not diverted; they are
                           here because they are the rows a reader will ask about.
  3. PREMISE_CONTROL_MODEL — the 6 MODEL rows. Route unchanged, nothing shipped reaches them, so
                           their replies must be UNCHANGED. A change here falsifies the premise.
  4. PREMISE_CONTROL_INDEX — six unchanged-route NSSF rows on row 9's own subject. A change here
                           is attributable to the index, not the route — and is a finding either
                           way, because nobody has measured row 9's second-order effects.

⛔ EVERY REFERENCE IS READ FROM ITS OWN FILE AND THE FIELD NAME IS RECORDED (R38). The corpora
disagree about what a gold is — `correct_answer_sw`, `output`, `expected_behavior`, `expect`,
`correct`, `truth` — and inventing one would make the judge grade against my expectation rather
than the corpus's. Where a row has no reference, it is read by hand and labelled as such.

⚠️ TWO PROBES IN ARM 1 CARRY AN EXPECTATION THIS CHANGE DELIBERATELY REVERSED, AND THE WAY THAT
RESOLVED IS THE USEFUL PART. `rq_03`/`rq_04` were authored with `expect: untouched` and
`guards_against: "eval_111 MUST-NOT-BREAK — same question with NO figure … answers correctly on
the fact path and carries detail this branch does not reproduce"`. The engine now carries exactly
that detail (`rate_statement._INCIDENCE`), which is what made routing them safe — so the probe's
expectation is stale, not the behaviour, and a probe that instructs a maintainer not to fix a real
defect is worse than no probe (R17's corollary).

**Keying on the question revealed that `rq_03` IS `eval_111` VERBATIM, and `rq_04` IS `eval_112`.**
So the merged row carries a real authored gold, and the right handling is not to skip it but to
GRADE it against that gold and record the stale routing expectation separately for a
history-preserving update of the probe file. My first draft returned a `STALE_EXPECTATION` verdict
early and skipped the judge — which would have discarded the grade on two of the rows most worth
grading. Hence the precedence rule below: an authored answer outranks a behavioural expectation.

Usage:  python eval/controls/targeted_route_verification_2026_10_09.py
        (OPENROUTER_API_KEY in the environment; majority-of-5 per row)
Artifact: eval/results/targeted_route_verification_2026_10_09.json — written after EVERY row and
          resumed from, so a dropped Tanzanian link costs one row, never the run.
Exit 0 if nothing regressed and the premise held · 1 on a regression · 2 if not exercisable.
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "targeted_route_verification_2026_10_09.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"
SWEEP = os.path.join(REPO, "eval", "results", "statement_route_sweep_2026_10_09.json")
BASELINE = os.path.join(REPO, "eval", "results", "gate_production_0e11c3d.json")
CLOSABILITY = os.path.join(REPO, "eval", "results", "bar_a_closability_2026_10_09.json")

from chike import routing                                                    # noqa: E402
from chike import judge as chike_judge                                       # noqa: E402

# ── REFERENCE FIELDS, PER CORPUS SHAPE. Ordered: the first present wins, and the NAME of the
# field that won is recorded on the row so a later reader can see what the judge graded against.
# ⛔ THE ORDER IS A PRECEDENCE RULE, NOT A CONVENIENCE. An AUTHORED ANSWER (`correct_answer_sw`,
# `output`) outranks a BEHAVIOURAL EXPECTATION (`expected_behavior`, `expect`, `correct`,
# `truth`), because the second kind describes what the SYSTEM should do and the first is the
# answer a user is owed. `rq_03` is `eval_111` verbatim and its `expect` field says `untouched`,
# i.e. "do not route this" — grading the reply against THAT would score the deliberate fix as a
# failure. Every candidate reference found across the merged files is still recorded on the row,
# so nothing is hidden by the precedence.
REF_FIELDS = ("correct_answer_sw", "output", "expected_behavior", "expect", "correct", "truth",
              "expected")
_AUTHORED_ANSWER_FIELDS = ("correct_answer_sw", "output")
QUESTION_FIELDS = ("question_sw", "question", "instruction")

# The five duplicate questions among the sweep's 24 diverted rows, asserted BY NAME. 24 rows and
# 19 unique questions is a claim about the corpora, and a future edit that merges or splits them
# differently must be loud rather than silently changing the denominator (R39).
EXPECTED_DUPLICATES = {
    "Jumla ya mchango wa NSSF ni asilimia ngapi?": 2,          # two training files
    "Kiwango cha SDL ni asilimia ngapi ya jumla ya mishahara ya jumla ya wafanyakazi wote?": 2,
    "Kiwango cha WCF ni asilimia ngapi ya jumla ya mishahara ya jumla?": 2,
    "Tuna wafanyakazi wachache sana, WCF inatuhusu?": 2,       # stress test + its reviewed copy
    "Nina wafanyakazi wachache tu, SDL itanihusu?": 2,
}

# ── ARM 4: the index-control rows, each with the reason it is here ───────────────────────
INDEX_CONTROLS = {
    "eval_099": "asks whether the employer's 10% is DEDUCTED from the wage — row 9's ambiguity "
                "verbatim, and the single best test of whether the rewording moved anything",
    "eval_348": "asks about the 10/10 split itself",
    "eval_337": "a cross-levy confusion on the NSSF rate (3.5 or 0.5), so it competes with the "
                "rows the rewording touched",
    "eval_365": "one first employee, is NSSF mandatory — eval_394's subject on an UNCHANGED route",
    "eval_234": "the NSSF remittance window, row 63's neighbourhood rather than row 9's",
    "eval_089": "the NSSF deadline, a plain NSSF row with no connection to the rewording — the "
                "quiet control inside the control arm",
}

# ── PROBES WHOSE COMMITTED EXPECTATION THIS CHANGE DELIBERATELY REVERSED ────────────────
STALE_EXPECTATION = {
    "rq_03": "expect:'untouched' + guards_against 'eval_111 MUST-NOT-BREAK … answers correctly "
             "on the fact path and carries detail this branch does not reproduce'. The engine "
             "now carries that detail (rate_statement._INCIDENCE), which is what made routing "
             "these safe. The probe's expectation is stale, not the behaviour.",
    "rq_04": "same, for WCF — 'Hulipwa kwa Mamlaka ya WCF (wcf.go.tz), si TRA' is now in the "
             "engine's own text.",
}


def _sh(*a):
    return subprocess.run(a, cwd=REPO, capture_output=True, text=True).stdout.strip()


HEAD = _sh("git", "rev-parse", "--short", "HEAD")
DEPLOY_PATHS = ["chike", "chike-inference", "kaggle/rag_facts_text.json",
                "kaggle/rag_embeddings.npy", "kaggle/chike_config.json"]


def _load(rel):
    rows = []
    for n, line in enumerate(io.open(os.path.join(REPO, rel), encoding="utf-8"), 1):
        if line.strip():
            r = json.loads(line)
            r["_file"], r["_line"] = rel, n
            rows.append(r)
    return rows


def _pick(row, fields):
    for f in fields:
        v = row.get(f)
        if isinstance(v, str) and v.strip():
            return f, v.strip()
    return None, None


def build_population():
    """Three sources, joined into one row list. Each row carries `arms` (a list, because the
    arms OVERLAP by design — the 6 MODEL rows are a subset of the twelve) and `why_population`.
    """
    sweep = json.load(io.open(SWEEP, encoding="utf-8"))
    base = {r["id"]: r for r in json.load(io.open(BASELINE, encoding="utf-8"))["rows"]}
    clos = {r["id"]: r for r in json.load(io.open(CLOSABILITY, encoding="utf-8"))["rows"]}

    out = {}

    def add(key, row, arm, why, extra=None):
        qf, q = _pick(row, QUESTION_FIELDS)
        assert q, f"{key}: no question field among {QUESTION_FIELDS}: {sorted(row)}"
        rf, ref = _pick(row, REF_FIELDS)
        rec = out.setdefault(key, {
            "key": key, "id": row.get("id"), "file": row["_file"], "line": row["_line"],
            "question": q, "question_field": qf,
            "reference": ref, "reference_field": rf,
            "all_references_found": [],
            "arms": [], "why_population": [],
            "intent_now": routing.detect_intent(q),
            "baseline_0e11c3d": None,
        })
        # Record EVERY reference the merged files offer, then apply the precedence. A merge that
        # silently picked whichever file the sweep happened to list first would make the judge's
        # grading depend on iteration order.
        if ref and not any(c["field"] == rf and c["file"] == row["_file"]
                           for c in rec["all_references_found"]):
            rec["all_references_found"].append(
                {"file": row["_file"], "field": rf, "text": ref})
        if ref and rf in _AUTHORED_ANSWER_FIELDS and \
                rec["reference_field"] not in _AUTHORED_ANSWER_FIELDS:
            rec["reference"], rec["reference_field"] = ref, rf
            rec["_reference_upgraded"] = (
                f"an authored answer ({rf}, from {row['_file']}) replaced a behavioural "
                f"expectation as the judge's reference")
        if arm not in rec["arms"]:
            rec["arms"].append(arm)
            rec["why_population"].append(f"{arm}: {why}")
        if extra:
            rec.update(extra)
        b = base.get(row.get("id"))
        if b is not None and rec["baseline_0e11c3d"] is None:
            rec["baseline_0e11c3d"] = {
                "pass": b["pass"], "reliable": b["reliable"], "clarified": b["clarified"],
                "reply": b.get("generated") or "",
                "judge": b.get("judge"),
            }
        return rec

    # ARM 1 — every diverted row, located by FILE AND LINE out of the sweep's own artifact.
    files = {}
    for d in sweep["diversion_rows"]:
        files.setdefault(d["file"], _load(d["file"]))
        row = next(r for r in files[d["file"]] if r["_line"] == d["line"])
        # Five of the 24 diverted rows are the SAME question in two files, so the key is the
        # question and each is asked once with both files recorded. ⛔ THE FULL QUESTION, NOT A
        # PREFIX: a truncated key can MERGE two different questions that share an opening, which
        # shrinks the population and reads as nothing (R39). Asserted against
        # EXPECTED_DUPLICATES below so a change in either direction is loud.
        key = f"q::{_pick(row, QUESTION_FIELDS)[1]}"
        rec = add(key, row, "DIVERTED",
                  "the sweep measured this row's route CHANGING. By the premise under test, "
                  "these are the only rows whose answer can have moved.",
                  extra={"route_before": d["before"], "route_after": d["after"]})
        rec.setdefault("also_in_files", [])
        if row["_file"] not in rec["also_in_files"]:
            rec["also_in_files"].append(row["_file"])
        if row.get("id") in STALE_EXPECTATION:
            rec["stale_expectation"] = STALE_EXPECTATION[row["id"]]
        # ⛔ A REFERENCE-LESS ROW GETS ITS COMMITTED FIELDS RECORDED RATHER THAN A GOLD INVENTED
        # FOR IT (R38). `hc_08` carries `expect_count` + `guards_against`; `ov_07` carries
        # `expected_refusal: false`. Both are real expectations about BEHAVIOUR and neither is an
        # answer, so the hand reading gets the raw fields and the judge is told there is no
        # reference — rather than me authoring one and grading the system against myself.
        if not rec["reference"]:
            rec["committed_fields"] = {k: v for k, v in row.items()
                                       if not k.startswith("_") and k != "system"}

    # ARMS 2 and 3 — the twelve, with the MODEL six additionally tagged as premise controls.
    gate_rows = {}
    for rel in ("eval/accuracy_gate/eval_questions_001.jsonl",
                "eval/accuracy_gate/eval_questions_002_additions.jsonl",
                "eval/accuracy_gate/eval_questions_003.jsonl"):
        for r in _load(rel):
            gate_rows[r["id"]] = r
    for qid, c in clos.items():
        row = gate_rows[qid]
        key = f"q::{_pick(row, QUESTION_FIELDS)[1]}"
        rec = add(key, row, "THE_TWELVE",
                  f"one of the 12 confirmed defects of 0e11c3d; closability={c['closability']}",
                  extra={"closability": c["closability"],
                         "adjudication_0e11c3d": c.get("adjudication")})
        if c["closability"] == "MODEL":
            rec["arms"].append("PREMISE_CONTROL_MODEL")
            rec["why_population"].append(
                "PREMISE_CONTROL_MODEL: route unchanged and nothing shipped this cycle reaches "
                "it, so the reply must be UNCHANGED. A change falsifies 'unchanged route means "
                "unchanged answer' and justifies the full gate immediately.")

    # ARM 4 — the index controls.
    for qid, why in INDEX_CONTROLS.items():
        row = gate_rows[qid]
        key = f"q::{_pick(row, QUESTION_FIELDS)[1]}"
        rec = add(key, row, "PREMISE_CONTROL_INDEX",
                  f"{why}. Route UNCHANGED, so a moved reply is attributable to index row 9's "
                  f"rewording rather than to the route — the second term the premise cannot "
                  f"exclude by construction.")

    rows = list(out.values())
    # Assertions on the POPULATION, not on the findings (R39): a population built by a join can
    # silently shrink, and a shorter finding list reads as success.
    n_div = len([r for r in rows if "DIVERTED" in r["arms"]])
    n_12 = len([r for r in rows if "THE_TWELVE" in r["arms"]])
    n_mod = len([r for r in rows if "PREMISE_CONTROL_MODEL" in r["arms"]])
    n_idx = len([r for r in rows if "PREMISE_CONTROL_INDEX" in r["arms"]])
    assert n_div == 19, (
        f"expected 19 unique diverted questions out of the sweep's 24 rows, got {n_div}. The "
        f"corpora changed; re-read EXPECTED_DUPLICATES before adjusting this number.")
    for q, k in EXPECTED_DUPLICATES.items():
        rec = out.get(f"q::{q}")
        assert rec is not None, f"a declared duplicate question is no longer in the population: {q!r}"
        assert len(rec.get("also_in_files", [])) == k, (
            f"{q!r} was declared as appearing in {k} files and now appears in "
            f"{len(rec.get('also_in_files', []))}: {rec.get('also_in_files')}")
    assert n_12 == 12, f"expected the twelve, got {n_12}"
    assert n_mod == 6, f"expected 6 MODEL premise controls, got {n_mod}"
    assert n_idx == len(INDEX_CONTROLS), f"index controls lost: {n_idx}"
    assert all(r["intent_now"] != "none" for r in rows if "DIVERTED" in r["arms"]), (
        "a diverted row routes to 'none' now — the sweep artifact and the live router disagree")
    assert all(r["intent_now"] == "none" for r in rows
               if "PREMISE_CONTROL_MODEL" in r["arms"] or "PREMISE_CONTROL_INDEX" in r["arms"]), (
        "a premise CONTROL has a changed route, so it is not a control at all — re-pick it")
    return rows


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


def health(tok):
    try:
        with urllib.request.urlopen(f"{HEALTH}?deep=1&token={tok}", timeout=600) as r:
            h = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                                                 # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    build = h.get("build") or ""
    anc = bool(build) and subprocess.run(
        ["git", "merge-base", "--is-ancestor", build, "HEAD"],
        cwd=REPO, capture_output=True).returncode == 0
    moved = [p for p in _sh("git", "diff", "--name-only", f"{build}..HEAD", "--",
                            *DEPLOY_PATHS).splitlines() if p.strip()] if anc else []
    h["_checks"] = {"build_is_an_ancestor_of_head": anc,
                    "no_serving_path_moved_since_the_build": not moved,
                    "web_and_gpu_tiers_agree": h.get("build_matches") is True}
    h["_provenance"] = {"deployed_build": build, "head": HEAD, "serving_paths_moved": moved}
    return h


def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def _resume():
    if not os.path.exists(OUT):
        return {}
    try:
        prev = json.load(io.open(OUT, encoding="utf-8"))
    except Exception:                                                        # noqa: BLE001
        return {}
    return {r["key"]: r for r in prev.get("rows", []) if r.get("reply")}


def classify(rec):
    """Per-row verdict. Deliberately distinguishes a REGRESSION from a row that was already
    wrong, and never treats a stale committed expectation as either."""
    b = rec.get("baseline_0e11c3d")
    jv = (rec.get("judge") or {}).get("verdict")
    if rec.get("error"):
        return "ERROR"
    # ⛔ A STALE COMMITTED EXPECTATION IS AN ANNOTATION, NOT A VERDICT. rq_03/rq_04 turned out to
    # be eval_111/eval_112 VERBATIM, so the merged row carries a real authored gold and can be
    # graded properly; the stale `expect: untouched` is recorded for a history-preserving update
    # of the probe file. Returning early here would have thrown away the grade on two of the
    # rows most worth grading.
    # Premise controls: the question is MOVEMENT, not correctness.
    if ("PREMISE_CONTROL_MODEL" in rec["arms"] or "PREMISE_CONTROL_INDEX" in rec["arms"]):
        if b is None:
            return "NO_BASELINE"
        return "CONTROL_MOVED" if rec["reply_changed"] else "CONTROL_HELD"
    if b is None:
        return "NO_BASELINE_JUDGE_" + str(jv).upper()
    if b["pass"] and jv == "wrong":
        return "REGRESSION_CANDIDATE"
    if not b["pass"] and jv == "correct":
        return "IMPROVED"
    return "HELD_" + str(jv).upper()


def save(rows, h, population):
    moved_controls = [r["id"] for r in rows if r.get("verdict") == "CONTROL_MOVED"]
    regressions = [r["id"] for r in rows if r.get("verdict") == "REGRESSION_CANDIDATE"]
    done = [r for r in rows if r.get("reply")]
    payload = {
        "_what": "targeted live verification of the statement route, in place of a full gate",
        "_why_not_the_full_gate": (
            "the change's own pre-registration predicts the regex headline cannot move (7 of the "
            "8 diverted rows were already scored as passes at 0e11c3d) and the judge's lower "
            "bound can move by at most three rows. 100 minutes of GPU to confirm a prediction is "
            "a receipt, not a measurement. The full gate is held for a batch of changes, so the "
            "expensive run attributes to something."),
        "_the_premise_under_test": (
            "A ROW WHOSE ROUTE DID NOT CHANGE CANNOT HAVE CHANGED ITS ANSWER. If it holds, the "
            "sweep's 24 diversions over 2,473 questions ARE the blast radius and this is a "
            "population, not a sample. If a premise control moved, the premise is false and the "
            "full gate is justified immediately."),
        "_the_second_term": (
            "this deploy also reworded index row 9, so a moved answer on an unchanged route has "
            "the index as its remaining candidate cause. That is why arm 4 exists: six "
            "unchanged-route NSSF rows on row 9's own subject, so the index term is MEASURED "
            "rather than left as a confound inside the control arm."),
        "endpoint": ENDPOINT, "health": h,
        "judge": {"model": chike_judge.DEFAULT_MODEL, "provider": chike_judge.DEFAULT_PROVIDER,
                  "n": chike_judge.DEFAULT_N,
                  "_never_auto_applies": "the judge is not ground truth. Diverted rows are read "
                                         "by hand; the verdict column records what it said."},
        "population": population,
        "totals": {
            "rows": len(rows), "measured": len(done),
            "by_verdict": {v: len([r for r in rows if r.get("verdict") == v])
                           for v in sorted({r.get("verdict") for r in rows if r.get("verdict")})},
        },
        "premise": {
            "controls_total": len([r for r in rows if "PREMISE_CONTROL_MODEL" in r["arms"]
                                   or "PREMISE_CONTROL_INDEX" in r["arms"]]),
            "controls_moved": moved_controls,
            "verdict": ("HELD — no unchanged-route row moved" if not moved_controls
                        else "FALSIFIED — an unchanged-route row moved; the full gate is now "
                             "justified and the blast radius is NOT bounded by the sweep"),
        },
        "regression_candidates": regressions,
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                        # noqa: BLE001
        pass

    tok = token()
    or_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not tok:
        print("NO MODAL TOKEN — not exercisable. This is NOT a pass.")
        return 2
    if not or_key:
        print("NO OPENROUTER_API_KEY — the judge cannot run, so there is no verdict. NOT a pass.")
        return 2

    rows = build_population()
    h = health(tok)
    print(f"[health] {json.dumps(h.get('_checks', h.get('error')), ensure_ascii=False)}")
    print(f"[health] deployed={h.get('_provenance', {}).get('deployed_build')} head={HEAD}")
    pop = {
        "_why_each_population": {r["key"]: r["why_population"] for r in rows},
        "counts": {
            "DIVERTED": len([r for r in rows if "DIVERTED" in r["arms"]]),
            "THE_TWELVE": len([r for r in rows if "THE_TWELVE" in r["arms"]]),
            "PREMISE_CONTROL_MODEL": len([r for r in rows
                                          if "PREMISE_CONTROL_MODEL" in r["arms"]]),
            "PREMISE_CONTROL_INDEX": len([r for r in rows
                                          if "PREMISE_CONTROL_INDEX" in r["arms"]]),
            "unique_questions": len(rows),
        },
    }
    print(f"[population] {json.dumps(pop['counts'], ensure_ascii=False)}")

    done = _resume()
    if done:
        print(f"[resume] {len(done)} row(s) already measured")

    out = []
    for rec in rows:
        if rec["key"] in done:
            prev = done[rec["key"]]
            rec.update({k: prev[k] for k in ("reply", "judge", "reply_changed", "verdict",
                                             "error") if k in prev})
            out.append(rec)
            save(out, h, pop)
            continue
        try:
            reply = str(ask(rec["question"], tok).get("reply") or "")
            rec["reply"] = reply
            b = rec.get("baseline_0e11c3d")
            rec["reply_changed"] = (None if b is None
                                    else _norm(reply) != _norm(b["reply"]))
            if rec.get("reference"):
                rec["judge"] = chike_judge.judge_majority(
                    rec["question"], rec["reference"], reply, api_key=or_key)
            else:
                rec["judge"] = {"verdict": "no_reference",
                                "_why": "this corpus row carries no reference field; the reply "
                                        "is recorded for hand reading rather than graded against "
                                        "an expectation I would have had to invent (R38)"}
        except Exception as exc:                                             # noqa: BLE001
            rec["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rec["verdict"] = classify(rec)
        out.append(rec)
        save(out, h, pop)
        jv = (rec.get("judge") or {}).get("verdict")
        ch = rec.get("reply_changed")
        print(f"[{rec['verdict']:22s}] {str(rec['id']):14s} {'/'.join(rec['arms'])[:34]:34s} "
              f"intent={rec['intent_now']:5s} judge={str(jv):13s} changed={ch}")
        if rec.get("error"):
            print(f"      ⛔ {rec['error']}")

    payload = save(out, h, pop)
    print("\n" + json.dumps(payload["totals"], ensure_ascii=False, indent=1))
    print(f"\nPREMISE: {payload['premise']['verdict']}")
    if payload["regression_candidates"]:
        print(f"⛔ REGRESSION CANDIDATES (hand-read before recording): "
              f"{payload['regression_candidates']}")
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    bad = payload["regression_candidates"] or payload["premise"]["controls_moved"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
