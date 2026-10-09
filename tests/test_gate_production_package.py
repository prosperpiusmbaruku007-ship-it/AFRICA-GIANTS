# -*- coding: utf-8 -*-
"""THE 2026-10-09 GATE PACKAGE, EXERCISED OFFLINE BEFORE IT CONSUMES AN HOUR OF GPU.

⛔ WHY EVERY ONE OF THESE IS PLANTED IN BOTH DIRECTIONS (R26). The package's whole claim is
that it measures the serving build with the guards wired, scores both directions, and separates
key correction from movement. Each of those is a mechanism, and a mechanism that cannot fail is
worth less than no mechanism — it reports clean and nobody looks again.

Three things here cannot be unit-tested and are named rather than skipped quietly: the GPU run
itself, the HF index download, and production's live /health. Everything else — the index
content probes, the guard plants, the outcome partition, the dual-key arithmetic, the guard
classifier — is exercised here, on the real repo data, against the real `chike` modules.
"""
import importlib.util
import io
import json
import os
import sys
import types

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

PKG = os.path.join(REPO, "kaggle", "eval_gate_production_2026_10_09.py")

from chike import clarification, fidelity  # noqa: E402
from chike.scoring import score_question   # noqa: E402


# ── THE GUARD PLANTS — lifted verbatim out of the package, so they cannot drift ─────────
def _package_source():
    return io.open(PKG, encoding="utf-8").read()


def test_the_package_exists_and_names_the_production_index():
    src = _package_source()
    assert "EXPECTED_FACT_COUNT = 184" in src, (
        "the package no longer asserts the 184-fact production index — a gate measured against "
        "a different index is not a gate against production")
    assert "BASELINE_COMMIT = '1476caa'" in src


def test_D_FIDELITY_7_blocks_the_fabricated_threshold_and_passes_a_correct_body():
    """⛔ THE PLANT. The dirty specimen is the live 2026-10-06 reply for eval_347, verbatim.
    The clean one is the correct no-threshold answer, which must NOT flag — a guard that flags
    the right answer is worse than one that misses the wrong one, because it blanks gold."""
    dirty = "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 kwa mwaka."
    clean = ("EFD inahitajika kwa default kwa kila mfanyabiashara; hakuna kizingiti cha "
             "mauzo. Usajili wa VAT ni TZS 200,000,000 kwa mwaka.")
    assert fidelity.body_states_wrong_threshold(dirty) is True, (
        "D-FIDELITY-7 no longer fires on its own founding specimen — it is INERT, which is "
        "byte-identical from the outside to a clean sweep from a sound rule")
    assert fidelity.body_states_wrong_threshold(clean) is False, (
        "D-FIDELITY-7 flags the CORRECT no-threshold answer — it would blank gold")


def test_D_FIDELITY_8_blocks_the_wrong_band_fee_and_passes_the_right_one():
    q = ("Nina kampuni na mtaji wa hisa wa TZS 2,000,000,000. Ada ya kusajili BRELA ni ngapi?")
    dirty = "Ada ya kusajili kampuni yako ni TZS 290,000."
    clean = "Ada ya kusajili kampuni yenye mtaji huo ni TZS 600,000."
    assert fidelity.body_states_wrong_fee_band(q, dirty) is True, (
        "D-FIDELITY-8 no longer fires on the measured 290,000 defect — its first prototype "
        "shipped INERT with 0 flags over 13,632 rows and a verdict of SAFE, so this plant is "
        "the only thing standing between that state and a green run")
    assert fidelity.body_states_wrong_fee_band(q, clean) is False, (
        "D-FIDELITY-8 flags the CORRECT band fee")


def test_the_replacement_copy_is_substantive_on_both_guards():
    """A fact-path guard that replaces a body with nothing ships SILENCE, which is the one
    outcome worse than the wrong answer it removed. Both copies must be real sentences."""
    c8 = clarification.wrong_fee_band_withheld()
    assert len(c8) > 200 and "mtaji wa hisa" in c8
    assert "samahani" not in c8.lower() and "jibu langu la awali" not in c8.lower(), (
        "the apology came back. On the fact path the user never sees the original answer, so "
        "an apology reads as though something went wrong that they should worry about")
    c7 = clarification.wrong_threshold_withheld("efd")
    assert len(c7) > 80


# ── THE INDEX CONTENT PROBES — run against the real committed index ─────────────────────
def _index():
    return json.load(io.open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                             encoding="utf-8"))


def test_the_committed_index_is_184_rows_and_matches_the_config_count():
    facts = _index()
    assert len(facts) == 184
    cfg = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"),
                            encoding="utf-8"))
    assert cfg.get("rag_fact_count") == 184, (
        f"chike_config.json says rag_fact_count={cfg.get('rag_fact_count')} while the baked "
        f"index has 184 rows — R14's own control, and the gate asserts the pair")


def test_row_172_serves_the_current_brela_figure_not_the_superseded_one():
    """The content probe that carried the whole of the 2026-10-07 deploy evidence. A digest
    proves two files match each other; only this proves they are the NEW build."""
    row = _index()[172]
    assert "70,000" in row, "row 172 does not carry TZS 70,000 — the index is not the new build"
    assert "USD 25" not in row, "row 172 still carries the superseded USD 25"


def _sweep():
    """The committed mention-vs-assertion rule, loaded from the repo — not re-implemented.

    A second copy of a cue list is the defect R39 names: `sahihi ni` sat in two rules and
    removing it from one left the row demoted, which only a re-run found. One rule, one place.
    """
    spec = importlib.util.spec_from_file_location(
        "superseded_sweep", os.path.join(REPO, "eval", "index_quality",
                                         "sweep_superseded_values_in_built_index.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_EFD_TOKENS = ("TZS 11,000,000", "11,000,000", "milioni 11")


def test_row_57_does_not_assert_the_fabricated_efd_threshold():
    """⛔ THIS TEST SHIPPED AS A BARE `not in` AND ITS FIRST RUN FAILED ON THE CORRECT ROW.

    Row 57 reads "EFD haina kizingiti cha mauzo kwa mwaka. SI TZS 200,000,000 — hiyo ni
    kizingiti cha kusajili VAT, si EFD. Na SI TZS 11,000,000." It DENIES the fabrication, which
    is the whole point of the correction — and containment is True of exactly that row.
    CLAUDE.md already records that rows 57, 63 and 159 deliberately carry their superseded value
    under a negation and that "a presence check would fail the very rows it protects"; this test
    was written anyway, and the package carried the same check at two more sites.

    The failure was LOUD, which is the only reason it cost nothing (R39): a too-tight rule
    produces a finding you dismiss by hand, a too-loose one produces silence.
    """
    sw = _sweep()
    row = _index()[57]
    for tok in _EFD_TOKENS:
        spans = sw._asserted_spans(row, tok)
        assert not spans, (
            f"row 57 ASSERTS {tok!r} (as {spans!r}) — not under a negation. That is the defect "
            f"it carried live for five and a half weeks")
    # POSITIVE LIMB — without it the check above passes trivially on a row that has lost the
    # content altogether, which is a check that cannot fail.
    #
    # ⚠️ MY FIRST DRAFT ASSERTED `hakuna kizingiti` AND THE LIVE ROW SAYS `haina kizingiti`.
    # The forms are LISTED, not assembled from optional morphemes (R37: a constructed
    # `u(?:li)?(?:ya)?lipi?a` generated `uliyalipia` where the row says `uliyolipia`, matched
    # nothing, and the escape it implemented was decoration). Both forms state the same claim,
    # so accepting either is the claim-keyed check, not a loosening to get green.
    _NO_THRESHOLD = ("haina kizingiti", "hakuna kizingiti", "hakina kizingiti")
    assert any(f in row.lower() for f in _NO_THRESHOLD), (
        f"row 57 no longer states that EFD has no turnover threshold (looked for any of "
        f"{_NO_THRESHOLD}). s.44(1) makes EFD the default for everyone; a row that merely "
        f"omits the fabrication does not answer eval_347")


def test_the_polarity_rule_still_FIRES_on_an_asserting_row():
    """⛔ THE PLANT FOR THE TEST ABOVE (R26). An inert rule returns "nothing asserted" for every
    row on earth, and that is byte-identical to a clean index. Both notations are planted
    because the index writes money in digits and in words, and a digit-keyed sweep found 3 rows
    where a claim-keyed one found 14 (R36)."""
    sw = _sweep()
    sw._self_test()          # the instrument's own nine specimens, both directions
    dirty_digits = ("Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 "
                    "kwa mwaka.")
    dirty_words = "Kizingiti cha EFD ni mauzo ya milioni 11 kwa mwaka."
    assert sw._asserted_spans(dirty_digits, "TZS 11,000,000"), (
        "the polarity rule does not fire on the verbatim pre-correction row 57 — it is INERT, "
        "and every row 57 probe built on it is decoration")
    assert sw._asserted_spans(dirty_words, "milioni 11"), (
        "the spelled-out notation is invisible to the rule, so a re-worded fabrication would "
        "pass every probe in this file")
    # and the live row must NOT flag on either notation — the negative half of the plant
    row = _index()[57]
    assert not any(sw._asserted_spans(row, t) for t in _EFD_TOKENS)


def _package_probes():
    """Extract the package's module-level content-probe machinery and run it for real.

    ⛔ WHY EXTRACTION AND NOT A GREP. The first version of this test asserted that the source
    CONTAINS `must_not_assert` and does NOT contain `must_not_contain` — and it failed on the
    COMMENT explaining why containment was wrong. That is R26's recorded defect ("three separate
    checks matched the COMMENT explaining why a defect was removed, including one introduced
    while fixing the previous two"), arriving while fixing a presence check with a presence
    check. A string check also cannot tell a correctly-wired probe from a mis-keyed one. So the
    probe list and its loop were lifted to module level in the package specifically so this test
    can CALL them against the real committed index.
    """
    src = _package_source()
    start = src.index("INDEX_CONTENT_PROBES = [")
    end = src.index("# ── PRE-FLIGHT GATES")
    ns = {"json": json}
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    assert "INDEX_CONTENT_PROBES" in ns and "index_content_probes" in ns, (
        "the package's probe machinery is no longer module-level — this test is stale and, "
        "worse, the probes are back to being unrunnable offline")
    return ns["INDEX_CONTENT_PROBES"], ns["index_content_probes"]


def test_the_packages_own_probes_PASS_on_the_real_committed_index():
    """The probe that would have aborted the GPU run, run here on the same bytes."""
    probes, run = _package_probes()
    assert len(probes) >= 2
    assert {p["row"] for p in probes} == {57, 172}
    # Every probe must carry BOTH limbs, or it is half a check.
    for p in probes:
        assert p.get("must_not_assert"), f"probe row {p['row']} has no negative limb"
        assert p.get("must_contain") or p.get("must_contain_any"), (
            f"probe row {p['row']} has no POSITIVE limb — a negated-mention check passes "
            f"trivially on a row that has lost its content altogether")
    fails, detail = run(_index(), _sweep()._asserted_spans)
    assert fails == [], (
        f"the package's FATAL pre-flight probes fail on the committed index. On Kaggle this "
        f"aborts AFTER the HF download: {fails}")
    assert detail and set(detail) == {"row_57", "row_172"}


def test_the_packages_probes_FIRE_on_a_planted_dirty_index():
    """⛔ THE PLANT (R26). The test above proves the probes pass; on its own that is
    indistinguishable from probes that can never fail. Three separate plants, because three
    different things can go inert: the negative limb, the positive limb, and the notation."""
    probes, run = _package_probes()
    sw = _sweep()
    good = _index()

    dirty = list(good)
    dirty[57] = "Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 kwa mwaka."
    fails, _ = run(dirty, sw._asserted_spans)
    assert any("ASSERTS" in f and "57" in f for f in fails), (
        "the negative limb is INERT — the verbatim pre-correction row 57 passes")

    worded = list(good)
    worded[57] = "Kizingiti cha EFD ni mauzo ya milioni 11 kwa mwaka."
    fails, _ = run(worded, sw._asserted_spans)
    assert any("milioni 11" in f for f in fails), (
        "the spelled-out notation is invisible, so a re-worded fabrication passes every probe")

    hollow = list(good)
    hollow[57] = "Mashine ya EFD inahitajika kwa wafanyabiashara."   # no fabrication, no claim
    fails, _ = run(hollow, sw._asserted_spans)
    assert any("NONE of" in f for f in fails), (
        "the POSITIVE limb is inert: a row that merely omits the fabrication without stating "
        "the no-threshold claim passes, and that row does not answer eval_347")

    stale = list(good)
    stale[172] = "Kampuni ya kigeni ikichelewa: faini ni USD 25 kwa kila mwezi."
    fails, _ = run(stale, sw._asserted_spans)
    assert any("172" in f for f in fails), "row 172's probe is inert on the superseded build"


def test_the_eval_347_verdict_is_polarity_aware():
    """Not extractable — it is inline reporting code — so this is a source pin, and it is
    labelled as the weaker check it is. It guards the single line of output most likely to be
    quoted: a bare `in` would report a reply that DENIES the fabrication as THE FINDING OF THE
    RUN, and a false accusation is the expensive direction because only it generates an edit."""
    src = _package_source()
    code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    assert "asserts_value(_e347['generated']" in code, (
        "the eval_347 verdict is back to a bare containment check on the model's reply")
    assert "_SWEEP._self_test()" in code, (
        "the package no longer exercises the polarity rule before judging rows with it")


# ── THE OUTCOME PARTITION AND THE GUARD CLASSIFIER ──────────────────────────────────────
def _load_scoring_helpers(scope_out=None):
    """Load just the pure helpers out of the package without executing its Kaggle preamble.

    The package is a flat Kaggle script — importing it would authenticate, clone and load an
    8B model. So the two functions under test are extracted by source and exec'd in a tiny
    namespace. That is a real limitation and it is stated rather than hidden: these tests
    exercise the LOGIC the package ships, and the extraction is asserted to have found it.

    `scope_out` injects the out-of-current-scope registry `bars` reads. It defaults to EMPTY so
    every pre-existing test keeps measuring what it measured — and the scope arms below pass one
    in explicitly, which is the only way to watch the column both fire and stay quiet.
    """
    src = _package_source()
    ns = {"Counter": __import__("collections").Counter, "SCOPE_OUT": dict(scope_out or {})}
    for marker in ("def outcome(r):", "def bars(rows_):"):
        assert marker in src, f"{marker} is gone from the package — this test is stale"
    start = src.index("def outcome(r):")
    end = src.index("def reliable_only(rows_):")
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    assert "outcome" in ns and "bars" in ns
    assert "SCOPE_OUT" in src.split("def bars(rows_):")[1][:2000], (
        "bars() no longer reads SCOPE_OUT, so the scope column has been removed or renamed and "
        "the arms below are measuring nothing")
    return ns["outcome"], ns["bars"]


def _row(**kw):
    base = {"id": "x", "subdomain": "vat", "error": None, "clarified": False, "pass": False,
            "guard_interventions": [], "reliable": True, "source": "gate_001",
            "compute": False, "pass_under_baseline_key": None}
    base.update(kw)
    return base


def test_the_outcome_partition_is_exhaustive_and_exclusive():
    outcome, bars = _load_scoring_helpers()
    assert outcome(_row(**{"pass": True})) == "RIGHT"
    assert outcome(_row(**{"pass": False})) == "WRONG"
    assert outcome(_row(clarified=True)) == "NO_ANSWER"
    assert outcome(_row(error="boom")) == "ERROR"
    # A guard-replaced fact row is a NO_ANSWER, never a WRONG. That is the whole point of
    # reporting A1 and A2 separately: a contained fabrication must not be counted as a
    # confident wrong answer, and must not be counted as a right one either.
    g = _row(clarified=True, guard_interventions=[{"guard": "D-FIDELITY-7", "mode": "replaced",
                                                   "pre_guard_body": "", "post_guard_text": ""}])
    assert outcome(g) == "NO_ANSWER"


def test_bars_RAISES_when_the_partition_does_not_sum():
    """⛔ PLANT THE BROKEN PARTITION. `bars` asserts its four buckets sum to the denominator;
    if that assert cannot fire, a mis-classification would be reported as a result. Forced by
    handing it a row whose `outcome` is a value the partition does not count."""
    outcome, bars = _load_scoring_helpers()
    src = _package_source()
    start = src.index("def outcome(r):")
    end = src.index("def reliable_only(rows_):")
    ns = {"Counter": __import__("collections").Counter}
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    ns["outcome"] = lambda r: "SOMETHING_ELSE"          # a fifth bucket nothing counts
    with pytest.raises(AssertionError, match="partition does not sum"):
        ns["bars"]([_row()])


def test_bars_counts_A1_and_A2_separately_and_never_nets_them():
    outcome, bars = _load_scoring_helpers()
    rows = ([_row(id=f"r{i}", **{"pass": True}) for i in range(7)]
            + [_row(id=f"w{i}", **{"pass": False}) for i in range(2)]
            + [_row(id=f"g{i}", clarified=True,
                    guard_interventions=[{"guard": "D-FIDELITY-7", "mode": "replaced",
                                          "pre_guard_body": "", "post_guard_text": ""}])
               for i in range(1)])
    b = bars(rows)
    assert b["n_in_corpus"] == 10
    assert b["A2_right"] == 7 and b["A1_wrong"] == 2 and b["no_answer"] == 1
    assert b["guard_rows"] == 1 and b["guard_by_name"] == {"D-FIDELITY-7": 1}
    assert b["guard_x_outcome"] == {"NO_ANSWER": 1}, (
        "the guard x outcome cross-tab is what shows a fact-path guard producing a non-answer "
        "while a compute-path blanking can still be RIGHT; losing it loses the distinction")


def test_out_of_corpus_rows_are_excluded_from_both_bars():
    outcome, bars = _load_scoring_helpers()
    rows = [_row(id="a", **{"pass": True}),
            _row(id="b", subdomain="out_of_corpus", **{"pass": True})]
    assert bars(rows)["n_in_corpus"] == 1, (
        "OOC rows are back in the in-corpus denominator. That is exactly how 330/400 = 82.5% "
        "came to be quoted against R7's IN-CORPUS bar")


# ── THE SCOPE COLUMN (added 2026-10-09 for eval_223) ────────────────────────────────────
def test_a_scope_tagged_row_stays_IN_the_denominator_and_is_reported_beside_it():
    """⛔ THE WHOLE POINT IS THAT IT IS *NOT* REMOVED. `eval_223` asks an EAC STR question — Tier
    1B, no corpus — so scoring it WRONG measures the roadmap. The tempting fix is to drop it, and
    dropping it would move the denominator of every historical comparison (1476caa, 0e11c3d) by
    one row, so a scope decision would surface as product movement. The column reports both.
    """
    outcome, bars = _load_scoring_helpers({"eval_223": {"tier": "tier1b"}})
    rows = ([_row(id=f"r{i}", **{"pass": True}) for i in range(8)]
            + [_row(id="eval_223", **{"pass": False})]
            + [_row(id="w0", **{"pass": False})])
    b = bars(rows)
    assert b["n_in_corpus"] == 10, (
        "a scope-tagged row was netted out of the denominator — that is the deletion this column "
        "exists to avoid, and it silently re-bases every historical comparison")
    assert b["A1_wrong"] == 2 and b["A2_right"] == 8
    assert b["scope_out_rows"] == ["eval_223"]
    assert b["scope_out_outcomes"] == {"eval_223": "WRONG"}
    # 8/9 vs 8/10 — the counterfactual is published, not asserted as the result.
    assert b["A2_rate_excluding_scope_out"] == pytest.approx(8 / 9)
    assert b["A1_rate_excluding_scope_out"] == pytest.approx(1 / 9)
    assert b["A2_rate"] == pytest.approx(0.8), "the headline rate moved; it must not"


def test_the_scope_column_is_QUIET_when_nothing_is_tagged():
    """R26's clean case. A column that reports members on an untagged population would make every
    historical bucket look scope-adjusted, and the two directions are indistinguishable from the
    artifact alone."""
    outcome, bars = _load_scoring_helpers()          # empty registry
    b = bars([_row(id="eval_223", **{"pass": False}), _row(id="a", **{"pass": True})])
    assert b["scope_out_rows"] == [] and b["scope_out_outcomes"] == {}
    assert b["A2_rate_excluding_scope_out"] == pytest.approx(b["A2_rate"]), (
        "with nothing tagged the two rates must be identical; if they diverge the exclusion "
        "arithmetic is reading a different population than the headline")


def test_eval_223_really_IS_tagged_in_the_corpus_and_its_gold_was_NOT_touched():
    """⛔ THE TAG IS THE CLAIM, SO READ THE CORPUS, NOT THE PACKAGE (R34). And assert the
    scored fields are untouched: the instruction was annotate, do not re-score, and a quiet edit
    to `correct_answer_sw` would move the key under the comparison it exists to preserve."""
    p = os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_002_additions.jsonl")
    rows = [json.loads(l) for l in io.open(p, encoding="utf-8") if l.strip()]
    assert len(rows) == 50, len(rows)
    r = next(x for x in rows if x["id"] == "eval_223")
    assert r["scope"]["status"] == "out_of_current_scope"
    assert r["scope"]["tier"] == "tier1b"
    assert r["scope"]["do_not_rescore"] is True
    assert "STR ina zana kuu nne" in r["correct_answer_sw"], (
        "eval_223's gold answer changed. The scope tag is metadata; re-scoring it is a different "
        "decision and was explicitly not taken")
    assert r["answer_type"] == "definition"
    # And exactly one row carries the tag — a second one appearing without a note means someone
    # used the column to quietly shrink the in-scope population.
    tagged = [x["id"] for x in rows if isinstance(x.get("scope"), dict)]
    assert tagged == ["eval_223"], tagged


# ── THE DUAL-KEY ARM ────────────────────────────────────────────────────────────────────
def test_the_committed_key_table_exists_and_lists_rows_that_really_narrow():
    """⛔ THE ARM MUST NOT BE VACUOUS. An empty dual-score list is a check that cannot fail, so
    the package asserts the list is non-empty; this asserts the list is CORRECT, by re-running
    the real scorer on each named row."""
    p = os.path.join(REPO, "eval", "results", "gold_key_corrections_2026_10_09.json")
    kc = json.load(io.open(p, encoding="utf-8"))
    ids = kc["dual_score_these"]
    assert ids, "the key-correction table lists no rows to dual-score"
    by_id = {f["id"]: f for f in kc["findings_400"]}
    rows = {}
    for line in io.open(os.path.join(REPO, "eval", "accuracy_gate",
                                     "eval_questions_003.jsonl"), encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            rows[r["id"]] = r
    for qid in ids:
        old = by_id[qid]["old"]
        new = rows[qid]
        old_row = dict(new)
        old_row.update(old)
        specimen = old_row["correct_answer_sw"]
        assert score_question(old_row, specimen, []) is True, (
            f"{qid}: the old gold does not satisfy its own old key — bad specimen")
        assert score_question(new, specimen, []) is False, (
            f"{qid} is listed as narrowing but the CURRENT key still accepts the OLD gold "
            f"answer. Then the row can never show a key-correction delta and listing it "
            f"overstates what the arm measures.")


def test_eval_383s_corrected_key_reaches_BOTH_fields_the_scorer_reads():
    """⛔ THE REGRESSION THIS WHOLE PASS STARTED FROM. score_question unions the SW and EN
    numeric keys, so a correction applied to correct_answer_sw alone leaves the superseded
    figure INSIDE the key — the corrected gold then accepts both the right and the wrong
    answer, which is the opposite of a correction."""
    row = None
    for line in io.open(os.path.join(REPO, "eval", "accuracy_gate",
                                     "eval_questions_003.jsonl"), encoding="utf-8"):
        if '"eval_383"' in line:
            row = json.loads(line)
    assert row is not None
    assert score_question(row, "Ada ni TZS 500,000.", []) is True
    assert score_question(row, "Ada ni TZS 300,000.", []) is False, (
        "eval_383 accepts the superseded TZS 300,000 again — correct_answer_en has drifted "
        "back, and the scorer reads it")


def test_no_other_corrected_row_has_an_EN_field_still_holding_the_old_figure():
    """The sweep that found eval_383, kept as a standing check over every corrected row."""
    from chike.scoring import extract_numbers
    import glob
    offenders = []
    for f in glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "*.jsonl")):
        for line in io.open(f, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if "_scoring_key_correction" not in r:
                continue
            if r.get("answer_type") not in ("number", "penalty"):
                continue
            sw = extract_numbers((r.get("correct_answer_sw") or "").lower())
            en = extract_numbers((r.get("correct_answer_en") or "").lower())
            if en - sw:
                offenders.append((r["id"], sorted(en - sw)))
    assert not offenders, (
        f"a corrected row's EN gold accepts figures its SW gold rejects, and score_question "
        f"UNIONS them: {offenders}")


# ── THE COVERAGE LEDGER AND THE PRE-REGISTRATION ────────────────────────────────────────
def _ledger():
    src = _package_source()
    start = src.index("KEY_CORRECTION_COVERAGE = [")
    end = src.index("print('\\n  ' + '-' * 86)")
    ns = {}
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    return ns["KEY_CORRECTION_COVERAGE"]


def test_the_coverage_ledger_names_every_item_the_arm_was_ASKED_to_cover():
    """⛔ THE ARM REACHES 2 OF 6 AND THAT IS THE POINT OF THE LEDGER.

    The dual-key arm was asked to cover eval_383, ext_15, ext_56 and the 41 sourced of 73. Only
    eval_383 is inside it. The other three are each zero or unmeasurable FOR A DIFFERENT REASON
    — ext_15 is in a 78-row probe set that is not in these 400 and whose gold is prose, ext_56's
    gold never changed at all, and the 41 were a REPORT_ONLY provenance backfill that changed no
    gold answer. An arm that silently covered two of four would report a cleaner result than it
    earned, which is the census-that-omits defect; this test is what stops the ledger being
    dropped later to tidy the output.
    """
    led = _ledger()
    items = {c["item"] for c in led}
    for needed in ("eval_383", "ext_15", "ext_56"):
        assert needed in items, f"the ledger no longer accounts for {needed}"
    assert any("41 sourced of 73" in i for i in items), (
        "the ledger no longer accounts for the 41 sourced gold answers")
    assert {c["item"] for c in led if c["dual_scored"]} == {"eval_383", "eval_355"}, (
        "the set of dual-scored rows changed. Only eval_355 and eval_383 narrow a key among "
        "the 400; anything else here is either unmeasurable or a fabricated term")
    # every NOT-REACHED item must carry a reason, and a long one — "out of scope" is not a reason
    for c in led:
        if not c["dual_scored"]:
            assert len(c["why"]) > 150, f"{c['item']}: not-reached with no stated reason"


def test_ext_56_really_has_no_key_correction_and_ext_15_really_is_not_in_the_400():
    """⛔ R34 / the standing instruction: an escalated specific is a correction candidate, not a
    verdict. Both of these were handed to me as corrected rows to dual-score. The ledger says
    otherwise, so the ledger's claims are checked against the corpora here rather than trusted.
    """
    ext = {}
    p = os.path.join(REPO, "eval", "accuracy_gate", "edge_probe_extended_078_DRAFT.jsonl")
    for line in io.open(p, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            ext[r["id"]] = r
    assert "ext_15" in ext and "ext_56" in ext, "the ext rows moved out of the 078 probe set"
    # ext_15: its key DID change (twice), and its own note demands a re-run
    assert "_scoring_key_correction" in ext["ext_15"]
    assert ext["ext_15"]["_scoring_key_correction_2"]["verdict"] == "RE_RUN_REQUIRED"
    # ext_56: no key correction of any kind — it is a model defect, not a gold one
    assert not any(k.startswith("_scoring_key_correction") for k in ext["ext_56"]), (
        "ext_56 now carries a key correction, so the ledger's reason for excluding it is stale")
    # and its gold is PROSE, which is why score_question cannot dual-score this set at all
    for qid in ("ext_15", "ext_56"):
        assert "expected_behavior" in ext[qid]
        assert "correct_answer_sw" not in ext[qid] and "answer_type" not in ext[qid], (
            f"{qid} has grown a regex-scorable key — the ledger's reason is now wrong and the "
            f"row could be dual-scored after all")
    # neither is in the 400 the gate runs
    in400 = set()
    for rel, n in (("eval_questions_001.jsonl", 200),
                   ("eval_questions_002_additions.jsonl", 50),
                   ("eval_questions_003.jsonl", 150)):
        lines = [l for l in io.open(os.path.join(REPO, "eval", "accuracy_gate", rel),
                                    encoding="utf-8") if l.strip()]
        assert len(lines) == n, f"{rel}: {len(lines)} rows, the package asserts {n}"
        in400 |= {json.loads(l)["id"] for l in lines}
    assert len(in400) == 400
    assert "ext_15" not in in400 and "ext_56" not in in400
    assert {"eval_355", "eval_383", "eval_347", "eval_331"} <= in400


def test_the_41_of_73_really_changed_no_gold_answer():
    """The ledger claims the provenance backfill moves no score. Re-derived from its artifact,
    because 'two sources agreeing' is not evidence and neither is a remembered figure."""
    p = os.path.join(REPO, "eval", "results", "gold_provenance_backfill_pass1.json")
    d = json.load(io.open(p, encoding="utf-8"))
    assert d["mode"] == "REPORT_ONLY"
    assert "Changes no gold answer" in d["what_this_does"]
    assert len(d["sourced"]) == 41 and len(d["still_pending"]) == 32, (
        f"the 41/73 split moved: {len(d['sourced'])} sourced + {len(d['still_pending'])} "
        f"pending. The ledger quotes 41 of 73 and must be re-derived, not edited to match")
    assert len(d["sourced"]) + len(d["still_pending"]) == 73
    # the live part: disagreements deliberately NOT changed are candidate wrong keys still
    # scoring rows today, and the ledger must keep pointing at them
    assert len(d["disagreements_reported_not_changed"]) == 4
    assert any("disagreements_reported_not_changed" in c["why"]
               for c in _ledger()), (
        "the ledger stopped naming the 4 reported disagreements — those are the only part of "
        "the 73 that can still be scoring a row against a wrong key")


def test_the_prereg_artifact_EXISTS_and_agrees_with_the_package():
    """⛔ THE SUMMARY NAMED THIS FILE BEFORE IT EXISTED. A claim whose evidence is 'one lookup
    away' has to actually be one lookup away — the five-week stale-doc lesson. And the numbers
    are asserted equal in both places, because two copies of a pre-registration that disagree
    let the run pick whichever it beat."""
    p = os.path.join(REPO, "eval", "results", "gate_preregistration_2026_10_09.json")
    assert os.path.isfile(p), (
        "the package's summary claims the pre-registration is committed at this path. It is not, "
        "so the artifact would ship a false provenance claim")
    pre = json.load(io.open(p, encoding="utf-8"))
    assert pre["run"]["n_questions"] == 400
    assert pre["baseline"]["commit"] == "1476caa"
    assert pre["baseline"]["in_corpus_raw"]["rate"] == 0.818
    assert pre["expected"]["point_estimate_in_corpus_raw"] == 0.825
    terms = {t["term"][:4]: t for t in pre["expected"]["terms"]}
    assert terms["a) K"]["pts"] == -0.52 and terms["b) C"]["pts"] == 1.25
    assert terms["d) T"]["pts"] is None, (
        "the index term has been given a number. It is UNSIGNED and UNBOUNDED and is the "
        "largest term; putting a figure on it is the thing the pre-registration exists to stop")
    assert pre["row_to_watch"]["id"] == "eval_347"
    src = _package_source()
    assert "'key_correction_pts': -0.52, 'corrected_facts_pts': +1.25" in src, (
        "the package's pre-registration terms no longer match the committed artifact's")
    assert "gate_preregistration_2026_10_09.json" in src


# ── WHAT THIS FILE CANNOT EXERCISE, NAMED RATHER THAN OMITTED ───────────────────────────
def test_the_unexercisable_parts_are_declared_in_the_package():
    """A census that quietly omits what it could not test reports a cleaner result than it
    earned. The package must say, in its own text, which of its gates need the live world."""
    src = _package_source()
    for needle in ("COULD NOT ASK", "gate_measures_what_is_serving", "REPORTING, NOT A BLOCK"):
        assert needle in src, (
            f"{needle!r} is gone — the package no longer distinguishes 'asked production and "
            f"it matched' from 'could not ask', and those are different claims")
    # ⛔ AND THE FOURTH THING, ADDED AFTER IT COST A RUN: this file being green says nothing
    # about whether the script will START. It died at second 13 on a module-level
    # sys.stdout.reconfigure in a module it loads, while two tests here were loading that
    # same module happily — under pytest sys.stdout HAS reconfigure, so the failure mode is
    # unreachable locally. The package must keep pointing at the static check that can see it.
    assert "check_kaggle_import_safety" in src, (
        "the package no longer names the static import-safety check. That check is the only "
        "thing in the repo that can see the class which killed this script at import, and no "
        "test in this file can substitute for it")
    assert os.path.isfile(os.path.join(REPO, "scripts", "check_kaggle_import_safety.py"))
