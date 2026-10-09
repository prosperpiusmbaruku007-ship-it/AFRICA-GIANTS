# -*- coding: utf-8 -*-
"""DERIVE THE OLD GOLD KEYS FROM GIT, so the next gate can separate key correction from movement.

⛔ WHY THIS EXISTS AND WHY IT IS A HARNESS RATHER THAN A LIST. The last full gate ran at
`1476caa` (2026-08-08). Since then the gate corpora have been edited: some rows had their
GOLD ANSWER corrected, and a corrected gold MOVES THE SCORE WITHOUT THE MODEL CHANGING AT ALL.
Run the next gate and compare its headline to 82.5% and you are comparing two different
denominators dressed as one number — the exact confound R22 is about, arriving in the scoring
key instead of in the population.

So the next gate scores every changed row TWICE: once against the key it had at `1476caa`, once
against the key it has now. The delta attributable to key correction is then a measured
quantity, reported separately, instead of an unstated term inside a single figure.

⛔ AND THE OLD KEYS ARE READ OUT OF GIT, NEVER RECONSTRUCTED FROM MEMORY OR FROM THE
`_scoring_key_correction` PROSE. That block is a note written by whoever made the change; it
says what they believed they changed. git says what changed. Three standing reasons:

  * the founder's own standing instruction (memory: re-derive supplied figures from the record;
    nine of nine failed verification in one session)
  * R34: a defect inferred from metadata is not a defect. `_scoring_key_correction.what_changed`
    IS metadata about an artifact, and the artifact is one `git show` away.
  * it was already wrong once, TODAY. eval_383's block said "TZS 300,000 -> TZS 500,000" while
    `correct_answer_en` still read 300,000 — and `score_question` unions the SW and EN numeric
    keys, so the "corrected" key accepted BOTH figures and could never have shown a delta. The
    prose described a correction the bytes had only half received.

WHAT IT EMITS — `eval/results/gold_key_corrections_2026_10_09.json`:
  * every row of the 400 whose SCORED fields changed between `1476caa` and HEAD, with the old
    and new values verbatim
  * for each, whether the change can move a score at all (a citation-only edit to a `number`
    row cannot; a changed figure can) — decided by running the REAL scorer, not by eye
  * the probe-set rows that changed, listed separately, because they are not in the 400 and are
    adjudicated by hand

SCORED FIELDS ONLY. `score_question` reads `answer_type`, `correct_answer_sw` and
`correct_answer_en`; `scorer_reliability` reads the same three. A `_why_hard` or `_target` edit
cannot move a verdict, so it is reported as `scored_fields_changed: false` rather than inflating
the count — and the discrimination is made by comparing the fields the scorer names, not by
guessing which edits looked cosmetic.
"""
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

import chike.scoring as S  # noqa: E402
from chike.scoring import extract_numbers, score_question, scorer_reliability  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "gold_key_corrections_2026_10_09.json")

# The commit the last full gate ran at. Taken from the artifact's own `clone_head`, not from a
# write-up — eval/results/gate_phase_d_paired_1476caa.json.
BASELINE = "1476caa"

# The 400. eval_questions_002_additions is listed even though it is unchanged, so a future edit
# to it cannot slip past this harness by not being looked at.
GATE_400 = [
    ("eval/accuracy_gate/eval_questions_001.jsonl", 200),
    ("eval/accuracy_gate/eval_questions_002_additions.jsonl", 50),
    ("eval/accuracy_gate/eval_questions_003.jsonl", 150),
]

# Probe sets: not in the 400, hand-adjudicated, reported separately rather than dropped.
PROBE_SETS = [
    "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl",
    "eval/accuracy_gate/edge_probe_natural_048.jsonl",
    "eval/accuracy_gate/threshold_comparison_probes_024.jsonl",
    "eval/accuracy_gate/vat_efd_probes_019.jsonl",
    "eval/accuracy_gate/quantity_instruction_heldout_024.jsonl",
]

SCORED_FIELDS = ("answer_type", "correct_answer_sw", "correct_answer_en")


def _git_show(rev, path):
    """Read a file as of `rev`. Returns None when it did not exist there (a NEW probe set)."""
    p = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO,
                       capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8")


def _rows(text):
    if text is None:
        return None
    out = {}
    for line in text.splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out


def _read_now(path):
    return _rows(io.open(os.path.join(REPO, path), encoding="utf-8").read())


def _key_signature(row):
    """What the scorer can actually see of this row's gold. Two rows with the same signature
    cannot score differently, whatever else was edited."""
    return {f: row.get(f) for f in SCORED_FIELDS}


def _numeric_key(row):
    sw = (row.get("correct_answer_sw") or "").lower()
    en = (row.get("correct_answer_en") or "").lower()
    return sorted(extract_numbers(sw) | extract_numbers(en))


def _discriminates(old_row, new_row, refusal_phrases):
    """⛔ DOES THE CORRECTION ACTUALLY NARROW THE KEY? Feed the OLD GOLD TEXT to the REAL scorer
    as though the model had produced it, and compare the verdict under both keys.

    THE SPECIMEN IS THE OLD GOLD ANSWER ITSELF, which is the only specimen that works for every
    `answer_type` at once. A model that answered exactly what the old key said is the best
    possible case of "scored right under the old key"; if the new key rejects that same text,
    the correction narrows, and a pass->fail flip on this row is attributable to the KEY rather
    than to the model.

    ⛔ THE FIRST VERSION OF THIS FUNCTION COMPARED NUMERIC KEYS AND IT WAS WRONG IN THE DELETING
    DIRECTION — R39, in my own instrument, within an hour of writing R39 down. It built a probe
    out of a dropped FIGURE, which is meaningless for `yes_no` rows: `score_question` compares
    POLARITY there and never looks at a number. So it reported eval_354 and eval_355 as
    unscoreable no-ops when eval_355's own correction note says "VERDICT FLIPPED from No to
    Yes" — the single most scoring-relevant change in the set — and it reported eval_331 and
    eval_347 as NARROWS on a numeric basis their scorer ignores. Three of its four verdicts on
    the yes_no rows were wrong, and the net effect was a SHORTER dual-score list, which read as
    a tidy result rather than as a broken discriminator.

    The lesson is the one R39 states and I had just written: a filter that fails loose in a
    cleanup DELETES findings, and a shrinking list is indistinguishable from progress. The fix
    is not a better numeric rule; it is to stop re-implementing the scorer's notion of
    equivalence and ASK THE SCORER.
    """
    old_gold = (old_row.get("correct_answer_sw") or "").strip()
    if not old_gold:
        return {"narrows": None,
                "why": "no old Swahili gold text to use as a specimen — cannot decide"}
    under_old = bool(score_question(old_row, old_gold, refusal_phrases))
    under_new = bool(score_question(new_row, old_gold, refusal_phrases))
    rec = {
        "specimen": "the OLD gold answer text, scored as if the model had produced it",
        "specimen_text": old_gold[:300],
        "old_gold_passes_old_key": under_old,
        "old_gold_passes_new_key": under_new,
        "old_numeric_key_dropped": [n for n in _numeric_key(old_row)
                                    if n not in _numeric_key(new_row)],
    }
    if not under_old:
        # The old gold does not even satisfy its own key. That is a finding about the scorer or
        # the old row, not about the correction, and it must not be silently read as "narrows".
        rec["narrows"] = None
        rec["why"] = ("THE OLD GOLD DID NOT PASS ITS OWN OLD KEY — the specimen is bad, so this "
                      "row cannot be adjudicated by this method (R26: eliminate the specimen "
                      "before recording an adverse verdict).")
        return rec
    rec["narrows"] = not under_new
    rec["why"] = ("the old gold answer is REJECTED by the new key, so a pass->fail flip here is "
                  "attributable to the key, not the model"
                  if not under_new else
                  "the new key still accepts the old gold answer, so a model giving the old "
                  "answer still passes and no key-correction delta is observable on this row")
    return rec


def _yn_divergence(old_row, new_row):
    """⛔ FOR yes_no ROWS: does the SCORER read the same verdict a human reads?

    `score_question` scores a yes_no row by comparing the model's polarity to
    `_yn_polarity(correct_answer_sw)` — so if the scorer MISREADS the gold's own verdict, the
    row is scored against a key nobody wrote, and a correction that flips the verdict produces
    no delta at all.

    THIS IS NOT HYPOTHETICAL AND IT IS WHY THIS FUNCTION EXISTS. eval_331's correction note says
    "VERDICT FLIPPED from No to Yes". Its OLD gold stated the No without a leading "Hapana" —
    *"...hivyo hulazimiki kutumia EFD bado"* — and `_YN_NEG` carries `halazimiki` (3rd person)
    but not `hulazimiki` (2nd person). One vowel. `_yn_polarity` therefore fell through to its
    AFFIRMATIVE DEFAULT and read the old gold as "yes", which is the new verdict. So any model
    answer leading "Ndiyo" passed eval_331 BOTH BEFORE AND AFTER a verdict flip, and the regex
    delta for the correction is exactly zero.

    Reported, not repaired. Widening `_YN_NEG` is a scorer change that would move historical
    numbers, and it needs R17's treatment (sweep every corpus, author probes that must stay
    clean) rather than a one-word patch dropped in alongside a gate package. All four affected
    rows are already `reliable=False`, so the reliable denominator never counted them — the raw
    denominator did.
    """
    if new_row.get("answer_type") != "yes_no":
        return None
    read_old = S._yn_polarity(old_row.get("correct_answer_sw") or "")
    read_new = S._yn_polarity(new_row.get("correct_answer_sw") or "")
    # `_scoring_key_correction` is a dict on the 400 rows and a bare STRING on some probe rows
    # (nat_36). Read it defensively rather than assuming the shape — the first version of this
    # crashed on exactly that, and because the run was piped to /dev/null the artifact simply
    # stayed at its previous contents and looked like a successful run with nothing to report.
    # The console-operation-between-a-measurement-and-its-file family, in one line.
    note = new_row.get("_scoring_key_correction")
    declared = str((note.get("what_changed") if isinstance(note, dict) else note) or "")
    declared_flip = "FLIP" in declared.upper()
    return {
        "scorer_reads_old_gold_as": read_old,
        "scorer_reads_new_gold_as": read_new,
        "scorer_sees_a_flip": read_old != read_new,
        "the_note_declares_a_flip": declared_flip,
        "DIVERGENT": declared_flip and read_old == read_new,
        "why_it_matters": ("the correction note declares a verdict flip that the scorer cannot "
                           "see, so this row was being scored against a verdict nobody wrote "
                           "and the key-correction delta on it is zero by construction"
                           if declared_flip and read_old == read_new else ""),
    }


def _refusal_phrases():
    """From chike_config.json (R14), because score_question needs them for refusal rows and a
    hand-written list here would be a second source of truth for the same thing."""
    cfg = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"), encoding="utf-8"))
    ph = cfg.get("refusal_phrases") or []
    assert ph, "chike_config.json carries no refusal_phrases — refusal rows cannot be scored"
    return ph


def main():
    findings, probe_findings = [], []
    refusal_phrases = _refusal_phrases()

    for path, n in GATE_400:
        new = _read_now(path)
        assert len(new) == n, f"{path}: expected {n} rows, got {len(new)}"
        old = _rows(_git_show(BASELINE, path))
        if old is None:
            print(f"[!] {path} did not exist at {BASELINE} — the whole file is new")
            continue
        for qid, nrow in new.items():
            orow = old.get(qid)
            if orow is None:
                findings.append({"id": qid, "file": path, "change": "ROW IS NEW since baseline"})
                continue
            if orow == nrow:
                continue
            scored = _key_signature(orow) != _key_signature(nrow)
            rec = {
                "id": qid, "file": path,
                "scored_fields_changed": scored,
                "answer_type": nrow.get("answer_type"),
                "fields_differing": sorted(k for k in set(orow) | set(nrow)
                                           if orow.get(k) != nrow.get(k)),
            }
            if scored:
                rec["old"] = _key_signature(orow)
                rec["new"] = _key_signature(nrow)
                rec["old_numeric_key"] = _numeric_key(orow)
                rec["new_numeric_key"] = _numeric_key(nrow)
                rec["discrimination"] = _discriminates(orow, nrow, refusal_phrases)
                rec["reliable_old"] = scorer_reliability(orow, "")[0]
                rec["reliable_new"] = scorer_reliability(nrow, "")[0]
                yn = _yn_divergence(orow, nrow)
                if yn is not None:
                    rec["yes_no_verdict_read_by_scorer"] = yn
            c = nrow.get("_scoring_key_correction")
            if isinstance(c, dict):
                rec["self_declared"] = c.get("what_changed")
            findings.append(rec)

    for path in PROBE_SETS:
        new = _read_now(path)
        old = _rows(_git_show(BASELINE, path))
        if old is None:
            probe_findings.append({"file": path, "n": len(new),
                                   "change": "ENTIRE SET IS NEW since the baseline — it was "
                                             "never scored at 1476caa, so it contributes no "
                                             "key-correction delta and no comparison"})
            continue
        for qid, nrow in new.items():
            orow = old.get(qid)
            if orow is None or orow == nrow:
                continue
            probe_findings.append({
                "id": qid, "file": path,
                "fields_differing": sorted(k for k in set(orow) | set(nrow)
                                           if orow.get(k) != nrow.get(k)),
                "old_expected": orow.get("expected_behavior") or orow.get("truth")
                                or orow.get("expect_value"),
                "new_expected": nrow.get("expected_behavior") or nrow.get("truth")
                                or nrow.get("expect_value"),
            })

    scored = [f for f in findings if f.get("scored_fields_changed")]
    narrowing = [f for f in scored if f.get("discrimination", {}).get("narrows") is True]
    inert = [f for f in scored if f.get("discrimination", {}).get("narrows") is False]
    undecided = [f for f in scored if f.get("discrimination", {}).get("narrows") is None]
    divergent = [f for f in scored
                 if (f.get("yes_no_verdict_read_by_scorer") or {}).get("DIVERGENT")]

    payload = {
        "_what": "Every gate-corpus row whose gold changed between the last full gate's commit "
                 "and HEAD, read out of git rather than from any write-up.",
        "_why": "A corrected gold moves the score with no model change. Scoring the changed "
                "rows under BOTH keys makes that term measurable instead of leaving it inside "
                "the headline.",
        "_old_keys_are_from_git_not_from_the_correction_notes": (
            "_scoring_key_correction.what_changed is a note by the person who made the change. "
            "It was wrong once already: eval_383's said '300,000 -> 500,000' while "
            "correct_answer_en still read 300,000, and score_question unions the SW and EN "
            "numeric keys, so the corrected key accepted both."),
        "baseline_commit": BASELINE,
        "head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                               capture_output=True, text=True).stdout.strip(),
        "counts": {
            "rows_in_400_changed_at_all": len(findings),
            "rows_whose_SCORED_fields_changed": len(scored),
            "of_those_that_NARROW_the_key": len(narrowing),
            "of_those_that_CANNOT_move_a_score": len(inert),
            "of_those_UNDECIDABLE_by_this_method": len(undecided),
            "yes_no_rows_whose_DECLARED_FLIP_THE_SCORER_CANNOT_SEE": len(divergent),
        },
        "dual_score_these": sorted(f["id"] for f in narrowing),
        "undecidable_ids": sorted(f["id"] for f in undecided),
        "scorer_blind_verdict_flips": {
            "_what": "yes_no rows whose _scoring_key_correction declares a verdict flip that "
                     "chike.scoring._yn_polarity does not read, so the row was scored against a "
                     "verdict nobody wrote and the correction produces ZERO regex delta.",
            "_cause": "_YN_NEG lists `halazimiki` (3rd person) and not `hulazimiki` (2nd "
                      "person). One vowel. _yn_polarity falls through to its AFFIRMATIVE "
                      "DEFAULT, so a model leading with 'Ndiyo' passed eval_331 both before and "
                      "after the verdict flipped from No to Yes.",
            "_not_repaired_here": "widening _YN_NEG is a scorer change that moves historical "
                                  "numbers and needs R17's treatment (sweep every corpus, "
                                  "author probes that must stay clean), not a one-word patch "
                                  "shipped alongside a gate package. All affected rows are "
                                  "already reliable=False, so the reliable denominator never "
                                  "counted them; the raw denominator did.",
            "ids": sorted(f["id"] for f in divergent),
        },
        "findings_400": findings,
        "probe_set_changes": probe_findings,
    }
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("=" * 78)
    print(f"GOLD KEY CORRECTIONS since {BASELINE} (last full gate, 2026-08-08)")
    print("=" * 78)
    print(f"  rows of the 400 edited at all          : {len(findings)}")
    print(f"  of those, SCORED fields changed        : {len(scored)}")
    print(f"  of those, the key actually NARROWS     : {len(narrowing)}  <- dual-score these")
    print(f"  of those, cannot move a score          : {len(inert)}")
    print(f"  of those, UNDECIDABLE by this method   : {len(undecided)}")
    print(f"  yes_no DECLARED flips the scorer CANNOT see: {len(divergent)} "
          f"{sorted(f['id'] for f in divergent)}")
    for f in scored:
        d = f.get("discrimination", {})
        mark = {True: "NARROWS", False: "no-op  ", None: "UNDECID"}[d.get("narrows")]
        print(f"\n  [{mark}] {f['id']} ({f['answer_type']})  fields={f['fields_differing']}")
        print(f"      old key nums: {f['old_numeric_key']}   new key nums: {f['new_numeric_key']}")
        print(f"      old gold under old key={d.get('old_gold_passes_old_key')}  "
              f"under new key={d.get('old_gold_passes_new_key')}")
        print(f"      {d.get('why')}")
    print(f"\n  probe-set rows changed (hand-adjudicated, NOT in the 400): "
          f"{len([p for p in probe_findings if 'id' in p])}")
    for p in probe_findings:
        if "id" in p:
            print(f"      {p['id']}  fields={p['fields_differing']}")
        else:
            print(f"      {os.path.basename(p['file'])}: {p['change']}")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
