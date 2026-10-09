# -*- coding: utf-8 -*-
r"""DOES ANY BUILT INDEX ROW STILL ASSERT A VALUE ITS OWN FACT DECLARES SUPERSEDED?

⛔ WHY THIS EXISTS, AND IT IS NOT "BRELA NEEDED CHECKING".

On 2026-10-06 twelve BRELA facts were amended and a payload gate demanding `TZS 70,000` in
`brela_foreign_late_filing_penalty`'s index row was written IN THE SAME COMMIT. The row itself was
not touched. The local dry run reported SAFE TO RUN; the Kaggle regen aborted on that gate before
uploading anything.

The gate did its job. The question this file answers is the one the founder asked next: what
checked the OTHER eleven? Nothing did. The dry run hand-wrote payload assertions for the two rows
whoever wrote it remembered changing (`brela_filing_fees`, `company_registration_ladder`) — which
is R33 exactly: a validator authored by the author of the change, scoped to the change the author
had in mind. Twelve facts moved; two rows were checked.

So this sweep's POPULATION IS DEFINED BY THE DATA, NOT BY RECOLLECTION: every fact in
locked_facts.json carrying a `superseded_value` field, whatever domain it is in. Adding a thirteenth
amendment enrols it automatically. Nobody has to remember.

⚠️ AND THE FIGURE TEST ALONE IS CONTEXT-BLIND — measured, not feared. `TZS 22,000` is the
SUPERSEDED special-company-information-report fee AND the CURRENT annual-return filing fee. A
whole-index sweep for superseded figures flags `annual_return_filing_fee`, which is correct. That
is the same false positive the correction-sync figure test produced on `vat_threshold_200m` (TZS
100,000,000 right as the 6-month threshold, wrong "kwa mwaka"), and it is why this file has two arms
with different authority:

  ARM 1 — OWN-ROW, BLOCKING. A fact's superseded figure in the row that RENDERS THAT FACT is a
          defect with no second reading. Scope is resolved structurally: the fact's own key row, or
          the FACT_GROUPS passage that absorbed it (precompute._GROUP_MEMBERS).
  ARM 2 — WHOLE-INDEX, REPORTING ONLY. Every other row carrying the figure, listed for a human.
          Collisions are expected here and are NOT failures.

⚠️ POLARITY, NOT PRESENCE — the lesson that has now arrived in a guard, a quarantine, an anchor
extractor and a payload gate. Three live rows deliberately name their superseded value in order to
CONTRADICT it ("SI TZS 100,000", "si tarehe 10", "SI USD 220 na SI USD 25"), because training rows
assert the old figure and an explicit contradiction is what overrides that prior. A presence check
would fail the very rows it protects. The negation device is lifted verbatim from the regen's own
payload gate so the two cannot drift.

⚠️ AND THE MONEY BOUNDARY FAILS IN THE DANGEROUS DIRECTION IF IT IS TOO TIGHT. A too-loose
boundary adds noise, which is visible and annoying. A too-tight one DELETES FINDINGS: `(?![\d,.])`
also blocks a sentence-final period, so "SI TZS 11,000,000." came back CLEAN from the EFD sweep
until a planted specimen caught it. The boundary here is the corrected form, and the planted
specimens below include a sentence-final case for exactly that reason.

Usage:  python eval/index_quality/sweep_superseded_values_in_built_index.py
Artifact: eval/results/superseded_values_in_built_index.json
Exit 1 if any ARM 1 finding. Exit 2 if the instrument could not be exercised (NOT a pass).
"""
import importlib.util
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ARTIFACT = "eval/results/superseded_values_in_built_index.json"


def _safe_stdout_utf8():
    """Make stdout UTF-8-tolerant WHERE THAT IS POSSIBLE, and never raise where it is not.

    ⛔ CALLED ONLY FROM main(). IT USED TO RUN AT MODULE LEVEL, AND THAT KILLED THE FULL
    PRODUCTION GATE AT SECOND 13 ON 2026-10-09 — before the GPU, before the HF download,
    before a single pre-flight check. `sys.stdout.reconfigure` exists on a real
    `TextIOWrapper` but NOT on Jupyter's `ipykernel.iostream.OutStream`, so importing this
    module inside a notebook kernel raised AttributeError at import time.

    THIS IS THE SECOND INSTANCE OF THE IDENTICAL DEFECT. The first was
    scripts/check_correction_sync.py on 2026-09-24, which cost a whole RAG regen after every
    blocking check had passed. That fix was correct and it included a sweep of "the other two
    modules the regen imports in-process" — a ONE-TIME act over a TWO-MODULE population,
    which could not protect this file because this file did not exist yet. The remembered-rule
    failure, again.

    So the durable half is NOT this function. It is
    scripts/check_kaggle_import_safety.py + tests/test_kaggle_import_safety.py, which re-derive
    the transitive closure of every module the kaggle/ scripts import — including through
    `spec_from_file_location`, which is the edge this one arrived on — and fail on any
    unguarded module-level reconfigure. The population is computed every run, so a module
    written next month is audited without anyone remembering to add it.

    ⚠️ AND NO LOCAL TEST COULD HAVE CAUGHT THIS. Under pytest `sys.stdout` is a TextIOWrapper
    (or pytest's CaptureIO, which subclasses it) and therefore HAS `reconfigure`. The gate
    package's 23 offline tests included two that LOAD this module and run its self-test, and
    they passed. Local green says nothing whatever about Jupyter's stream objects; the only
    reachable check for this class is static.

    The second defect was in the same two lines and is the general one: A LIBRARY MUST NOT
    MUTATE ITS CALLER'S GLOBAL STATE AT IMPORT. `os.chdir(REPO)` sat on the next line, and
    importing this module silently relocated the notebook's working directory. It is now in
    `main()` alongside this call — moved, NOT removed, and the attempt to remove it is worth
    recording: it is LOAD-BEARING. `scripts/precompute_rag_embeddings.py` holds
    `FACTS_PATH = 'scripts/locked_facts.json'` as a RELATIVE path, so `build_fact_texts()`
    raises FileNotFoundError from any other cwd. The first fix made this file's own artifact
    path absolute and declared the chdir unnecessary; running the sweep from `C:\\` disproved
    that in one line. The distinction that matters is not chdir-vs-no-chdir, it is IMPORT TIME
    vs CALL TIME: a script's main() may set up its own world, a library's import may not.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

# Lifted VERBATIM from kaggle/regenerate_rag_e5.py's payload gate. If these two ever disagree,
# this sweep and the gate that aborts the regen are measuring different things.
_NEGATED = r"(?:\bsi\b|\bnot\b|\bsio\b|\bhapana\b)[\s:,]*(?:TZS\s*|USD\s*)?$"
_NEGATION_CHARS = 14

# ⚠️ AND `SUPERSEDES` IS A STRONGER SUPERSESSION MARKER THAN ANY OF THOSE, which the borrowed
# device does not know about — it was written for Swahili reply text, and this is English
# provenance prose that R27/R29 discipline puts into every amended fact's `fact` field. A row
# rendered via the `key: value` fallback therefore serves that prose verbatim:
#
#   "...ni TZS 2,000,000 (BRELA fee schedule item 15(i), as at 2026-10-06...).
#    SUPERSEDES USD 750 (published as at 2026-06-30)."
#
# That row states the CURRENT value first and labels the old one as superseded. It is not a wrong
# value, and reporting it as one would have sent someone to edit a correct row. R20's sixth
# arrival point, exactly: whose words is the detector matching, and were they written for the
# population it is now pointed at?
#
# ⚠️ THERE IS A REAL FINDING UNDERNEATH, AND IT IS A DIFFERENT ONE — recorded, not conflated:
# the row is the LABEL-LED `key: value` fallback ("certified copy agreement law constitution
# fee: ..."), it carries a statutory citation in the EMBEDDED text (forbidden by the standing
# rule in precompute_rag_embeddings.py — folding citations in cost nat_05 ranks 24 -> 59), and it
# serves English provenance a user never needs. That is a reachability/dilution defect, not an
# accuracy one, and fixing it changes served content, so it needs the displacement harness rather
# than an edit here. Counted in `provenance_leaking_rows` below.
_SUPERSESSION_MARKER = re.compile(r"\bSUPERSEDES\b|\bSUPERSEDED\b|\bwas\s+(?:TZS|USD)\b",
                                  re.IGNORECASE)
_SUPERSESSION_CHARS = 60

# Money tokens as they appear in a `superseded_value` field: currency-led ("USD 25"), or
# comma-grouped ("440,000"). Nothing else.
#
# ⚠️ A BARE RUN OF DIGITS IS NOT A MONEY TOKEN, and the first draft of this pattern had
# `\d{4,}` as a third alternative "so 70000 lands too". No fee in this corpus is written without
# separators, and that alternative turned the DATE in "(published as at 2026-06-30)" into a
# needle — which then matched ten unrelated rows (gn605a_effective_date, the presumptive bands,
# the GN487A disambiguation) and reported them as carrying a superseded BRELA fee. R34: a defect
# inferred from a pattern is not a defect. Dropped rather than special-cased, because "exclude
# years" is a list and "require money notation" is a rule.
_MONEY = re.compile(
    r"(?:USD|TZS|Dola\s+za\s+Kimarekani)\s*\d[\d,]*(?:\.\d+)?"
    r"|(?<![\d,.])\d{1,3}(?:,\d{3})+(?![\d,])",
    re.IGNORECASE)


_SUPERSEDES_CLAUSE = re.compile(
    r"\bSUPERSEDES\b|\bSUPERSEDED\b|\bwas\s+(?:TZS|USD)\b|\(was\b|\bya\s+zamani\b", re.IGNORECASE)


def _current_prose(fact_text: str) -> str:
    """The part of a fact's prose that asserts its CURRENT value, with the provenance tail cut.

    ⛔⛔ THIS SWEEP SHIPPED WITH THE EXACT DEFECT IT EXISTS TO FIND, AND IT REPORTED `CLEAN`.

    The current-value filter read tokens out of the whole `fact` field to cancel a superseded
    token that had not actually moved (the TZS 50,000,000 band edge). But R27/R29 discipline means
    a corrected fact RECORDS WHAT IT SUPERSEDES in its own prose:

        "Ada ya kutafuta jalada ... ni TZS 5,000 (item 9, as at 2026-10-06).
         SUPERSEDES TZS 3,000 (published as at 2026-06-30, June item 12)."

    So `3,000` was read as a CURRENT value, cancelled itself, and the fact's superseded-token list
    came out EMPTY. Three of eleven facts were never examined at all — `file_search_fee`,
    `file_search_report_fee`, `certified_copy_certificate_of_registration_fee` — and all three
    printed as `CLEAN`, which is what an unexamined row looks like from the outside.

    **It is the same polarity failure as every other one found today, one level up: a value named
    in order to be REJECTED was read as a value ASSERTED.** The difference is where it landed —
    not in a demotion rule but in a CANCELLATION rule, where its effect is not to excuse a finding
    but to delete the question. And the signature was the same: a shorter list, read as clean.

    Found only because row 182 of the built index was read by eye and still carried `TZS 3,000`.
    """
    m = _SUPERSEDES_CLAUSE.search(fact_text)
    return fact_text[:m.start()] if m else fact_text


def _numeric(token: str) -> str:
    """The digits of a money token, currency and separators stripped.

    ⛔ WHY COMPARISON IS BY NUMBER AND NOT BY STRING. `company_registration_fee_bands` declares
    its supersession as "5 bands ending in an OPEN-ENDED 'above TZS 50,000,000 = 440,000'", and
    its CURRENT nine-band text reads "hadi 50,000,000 = 290,000" — the same figure, written
    without the currency because it is a band EDGE rather than a fee. String comparison made
    `TZS 50,000,000` and `50,000,000` different tokens, so the current-value filter missed it and
    the sweep reported a BLOCKING finding on a figure that never moved: only the band's SCOPE
    changed (it closed at 100,000,000 with four bands above it). The actual superseded figure for
    that fact is 440,000, and the row correctly no longer carries it.
    """
    return re.sub(r"[^\d]", "", token)


def _needle_pattern(token: str) -> str:
    """A regex matching `token` in row text, tolerant of currency spacing, strict at the edges.

    The trailing boundary deliberately does NOT exclude a following '.' or ',' — a figure at the
    end of a sentence, or in a list, is still that figure. It excludes only a continuation of the
    NUMBER itself (another digit, or a comma followed by digits), which is what distinguishes
    `70,000` from `70,000,000`.
    """
    m = re.match(r"(?i)^(USD|TZS|Dola\s+za\s+Kimarekani)\s*(.+)$", token)
    if m:
        cur, num = m.group(1), m.group(2)
        cur_pat = r"Dola\s+za\s+Kimarekani" if cur.lower().startswith("dola") else re.escape(cur)
        return rf"(?<![\d,.]){cur_pat}\s*{re.escape(num)}(?![\d]|,\d)"
    return rf"(?<![\d,.]){re.escape(token)}(?![\d]|,\d)"


def _tokens(text: str) -> list:
    seen, out = set(), []
    for m in _MONEY.finditer(text or ""):
        t = re.sub(r"\s+", " ", m.group(0)).strip()
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def _asserted_spans(row: str, token: str) -> list:
    pat = _needle_pattern(token)
    out = []
    for m in re.finditer(pat, row, re.IGNORECASE):
        before = row[max(0, m.start() - _NEGATION_CHARS):m.start()]
        if re.search(_NEGATED, before, re.IGNORECASE):
            continue
        if _SUPERSESSION_MARKER.search(row[max(0, m.start() - _SUPERSESSION_CHARS):m.start()]):
            continue
        out.append(m.group(0))
    return out


def _mentioned(row: str, token: str) -> bool:
    return bool(re.search(_needle_pattern(token), row, re.IGNORECASE))


def _load_precompute():
    spec = importlib.util.spec_from_file_location(
        "precompute", os.path.join(REPO, "scripts", "precompute_rag_embeddings.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _self_test():
    """NON-VACUITY BY PLANTED SPECIMEN, both directions (R26).

    A sweep that reports CLEAN is indistinguishable from a sweep that cannot report anything, and
    this project has shipped both. So the instrument is exercised against rows written to be
    caught and rows written to pass, BEFORE it is pointed at the index.
    """
    cases = [
        # (row, token, must_be_asserted, why)
        ("faini ni USD 25 kwa kila mwezi", "USD 25", True,
         "the exact defect this sweep exists for -- a plain assertion of the superseded figure"),
        ("SI USD 220 na SI USD 25 — hizo ni ada za zamani.", "USD 25", False,
         "brela_filing_fees' real contradiction clause. A presence check fails the row that "
         "protects the figure; this is why polarity is checked"),
        ("Faini ya juu ni TZS 10,000,000, SI TZS 100,000.", "TZS 100,000", False,
         "fine_limit's real override clause, mid-sentence negation"),
        ("Kizingiti sahihi: hakuna. SI TZS 11,000,000.", "TZS 11,000,000", False,
         "SENTENCE-FINAL negated figure. The EFD sweep's first boundary blocked a trailing '.' "
         "and reported this CLEAN -- a too-tight boundary DELETES findings, which is the "
         "dangerous direction"),
        ("Ada ni TZS 440,000 kwa mtaji wa juu.", "TZS 440,000", True,
         "the superseded open-ended ladder band, asserted"),
        ("Ada ... ni TZS 2,000,000 (item 15(i), as at 2026-10-06). SUPERSEDES USD 750 "
         "(published as at 2026-06-30).", "USD 750", False,
         "the `key: value` FALLBACK rendering of an amended fact serves its provenance prose "
         "verbatim. `SUPERSEDES` is a stronger supersession marker than any Swahili negation and "
         "the borrowed device knew none of them -- it was written for reply text. Reporting this "
         "as a wrong value would have sent someone to edit a CORRECT row"),
        ("Ada ya kuwasilisha ni USD 750 kwa Msajili.", "USD 750", True,
         "and the same figure WITHOUT the marker must still flag -- otherwise the escape above "
         "would be a blanket release for every USD figure in the index"),
        ("Ada ni TZS 400,000 kwa mtaji wa juu.", "TZS 440,000", False,
         "the CURRENT band must not match the superseded needle -- 400,000 vs 440,000"),
        ("Ada ni TZS 70,000,000 kwa kitu kingine.", "TZS 70,000", False,
         "a LONGER number must not match a shorter needle: 70,000,000 is not 70,000"),
        ("Ada tatu: TZS 600,000, TZS 70,000, na TZS 2,500.", "TZS 70,000", True,
         "a figure inside a comma-separated list is still that figure"),
    ]
    failures = []
    for row, token, want, why in cases:
        got = bool(_asserted_spans(row, token))
        if got != want:
            failures.append({"row": row, "token": token, "expected_asserted": want,
                             "got_asserted": got, "why_this_case_exists": why})
    # TOKEN EXTRACTION, pinned separately because both of this instrument's own real defects were
    # here rather than in the polarity logic -- and both were found by RUNNING it, not by reading
    # it. Kept as specimens so neither can return.
    tok_cases = [
        ("5 bands ending in an OPEN-ENDED 'above TZS 50,000,000 = 440,000' (published as at "
         "2026-06-30)", ["TZS 50,000,000", "440,000"],
         "the DATE must not become a money needle. With `\\d{4,}` in the pattern, '2026' was a "
         "token and matched ten unrelated rows -- gn605a_effective_date, the presumptive bands, "
         "the GN487A disambiguation -- reporting each as carrying a superseded BRELA fee"),
        ("USD 25 per month (published as at 2026-06-30, June capture item 14)", ["USD 25"],
         "'item 14' and the date are not money; the currency-led figure is"),
    ]
    for text, want, why in tok_cases:
        got = _tokens(text)
        if got != want:
            failures.append({"superseded_value_text": text, "expected_tokens": want,
                             "got_tokens": got, "why_this_case_exists": why})
    # THE CANCELLATION RULE, pinned both ways. It emptied three facts' token lists and printed
    # CLEAN; a specimen is the only thing that would have shown it.
    cancel_cases = [
        ("Ada ya kutafuta jalada la kampuni yoyote BRELA ni TZS 5,000 (item 9, as at "
         "2026-10-06). SUPERSEDES TZS 3,000 (published as at 2026-06-30, June item 12).",
         ["TZS 5,000"],
         "the SUPERSEDES tail must NOT contribute current tokens. Reading 3,000 from it "
         "cancelled the fact's own superseded value and the check was never performed"),
        ("Ada ya kusajili kampuni ... hadi 50,000,000 = 290,000; hadi 100,000,000 = 400,000.",
         ["50,000,000", "290,000", "100,000,000", "400,000"],
         "a fact with NO supersession clause keeps its whole prose -- this is the case the "
         "cancellation rule exists for (a band edge that never moved)"),
    ]
    for text, want, why in cancel_cases:
        got = _tokens(_current_prose(text))
        if got != want:
            failures.append({"fact_prose": text, "expected_current_tokens": want,
                             "got": got, "why_this_case_exists": why})
    if _numeric("TZS 50,000,000") != _numeric("50,000,000"):
        failures.append({"why_this_case_exists":
                         "a band EDGE written without its currency in the fact's current text "
                         "must cancel the same figure written WITH it in the superseded field. "
                         "String comparison did not, and the sweep reported a BLOCKING finding "
                         "on a figure that never moved"})
    assert not failures, (
        "THE INSTRUMENT IS BROKEN, NOT THE INDEX. Planted specimens disagree with the "
        "polarity/boundary/extraction logic:\n" + json.dumps(failures, ensure_ascii=False,
                                                             indent=2) +
        "\nRefusing to sweep -- a broken sweep reports CLEAN and that reads as progress.")
    return ([{"row": r, "token": t, "expected_asserted": w, "why_this_case_exists": y}
             for r, t, w, y in cases] +
            [{"superseded_value_text": t, "expected_tokens": w, "why_this_case_exists": y}
             for t, w, y in tok_cases])


def main():
    _safe_stdout_utf8()
    # At CALL time, not import time. Needed because precompute_rag_embeddings.FACTS_PATH is
    # relative ('scripts/locked_facts.json'), so build_fact_texts() below only works from the
    # repo root. See _safe_stdout_utf8's docstring: removing this looked right and broke the
    # standalone run.
    os.chdir(REPO)
    specimens = _self_test()
    precompute = _load_precompute()
    texts, keys, _dropped = precompute.build_fact_texts()
    by_key = dict(zip(keys, texts))
    group_of = dict(precompute._GROUP_MEMBERS)

    facts = json.load(io.open(os.path.join(REPO, "scripts", "locked_facts.json"),
                              encoding="utf-8"))

    population = {k: v for k, v in facts.items()
                  if isinstance(v, dict) and v.get("superseded_value")}
    assert population, (
        "ZERO facts carry a `superseded_value` field. That is either a renamed field or a "
        "corpus with no recorded supersessions -- both make this sweep vacuous, so it refuses "
        "to report CLEAN. Check the field name before believing this.")

    arm1, arm2, clean = [], [], []
    for key, fact in sorted(population.items()):
        row_key = group_of.get(key, key)
        row = by_key.get(row_key)
        superseded = _tokens(str(fact.get("superseded_value", "")))
        current = _tokens(str(fact.get("correct_value", "")) + " " +
                          _current_prose(str(fact.get("fact", ""))))
        # A token that is ALSO the current value is not superseded for this fact -- the amount
        # did not move, something else did (a currency, a band's scope, a citation). Compared by
        # NUMBER, not by string: see _numeric's note on the TZS 50,000,000 false positive.
        current_nums = {_numeric(c) for c in current}
        superseded = [t for t in superseded if _numeric(t) not in current_nums]

        if row is None:
            arm1.append({"fact": key, "row_key": row_key, "verdict": "ROW_ABSENT",
                         "detail": "the fact declares a supersession and has no built row at "
                                   "all -- it cannot be serving the right value either"})
            continue

        # ⛔ A GROUP PASSAGE HOLDS MANY FEES, SO "THE ROW THAT RENDERS THIS FACT" IS SHARED —
        # AND TWO OF THE FIRST THREE BLOCKING FINDINGS WERE SIBLINGS' CURRENT FEES.
        #
        # `file_search_fee` moved TZS 3,000 -> 5,000, and `brela_filing_fees` contains BOTH
        # "kutafuta jalada TZS 5,000" (this fact, correct) and "kuthibitisha nyaraka kwa ukurasa
        # TZS 3,000" — which is item 8 of BRELA's October schedule, *"Malipo ya kuthibitisha
        # waraka wowote (kwa kila ukurasa) 3,000/="*, CURRENT and unchanged. Same for
        # `file_search_report_fee` (22,000 -> 30,000): item 5 *"Upokeaji/usajili wa hati ya
        # kisheria 22,000/="* is also current, as is item 7's annual return. Both read from the
        # sha256-pinned capture, not inferred (R34).
        #
        # So for a GROUP row the test needs its positive limb: a fact is correctly rendered when
        # ITS CURRENT VALUE IS PRESENT — which is exactly what the regen's own payload gates
        # assert. If the current value is there, a stray match of the old one elsewhere in the
        # passage belongs to a sibling. A STANDALONE row has no siblings, so it stays strict.
        #
        # ⚠️ RESIDUAL, stated rather than engineered around: a group passage stating BOTH the old
        # and the new value for the SAME item would be cancelled here. That is a smaller hole than
        # two false positives in three findings, because only a false positive generates an edit —
        # and an edit lands in correct data.
        in_group = key in group_of
        current_present = any(_mentioned(row, c) for c in current) if current else False
        hits = []
        for t in superseded:
            if in_group and current_present:
                continue
            spans = _asserted_spans(row, t)
            if spans:
                hits.append({"token": t, "asserted_as": spans})
        if hits:
            arm1.append({"fact": key, "row_key": row_key, "verdict": "ASSERTS_SUPERSEDED",
                         "hits": hits, "row": row,
                         "superseded_value": fact.get("superseded_value"),
                         "correct_value": fact.get("correct_value")})
        else:
            negated = [t for t in superseded if _mentioned(row, t)]
            clean.append({"fact": key, "row_key": row_key,
                          "verdict": "MENTIONS_UNDER_NEGATION" if negated else "CLEAN",
                          "superseded_tokens_checked": superseded,
                          "mentioned_under_negation": negated})

        # ARM 2 — reporting only.
        for t in superseded:
            elsewhere = [k for k, txt in by_key.items()
                         if k != row_key and _asserted_spans(txt, t)]
            if elsewhere:
                arm2.append({"fact": key, "token": t, "also_asserted_by_rows": elsewhere})

    # ── THE SEPARATE, REAL FINDING: provenance prose reaching served text ───────────────────
    # Not an accuracy defect (the current value leads), so it is REPORTED, not blocking. But it is
    # a dilution + reachability one: a `key: value` fallback row is label-led, carries a statutory
    # citation in the embedded text (forbidden by the standing rule in
    # precompute_rag_embeddings.py), and serves English provenance a user never needs. Fixing it
    # changes served content and therefore needs the displacement harness, not an edit here.
    provenance_leaking = []
    for key in sorted(population):
        row_key = group_of.get(key, key)
        row = by_key.get(row_key) or ""
        if not _SUPERSESSION_MARKER.search(row):
            continue
        provenance_leaking.append({
            "fact": key, "row_key": row_key,
            "label_led_fallback": row.lower().startswith(key.replace("_", " ").lower() + ":"),
            "carries_citation_in_embedded_text": bool(
                re.search(r"cap\.?\s*\d|item\s+\d|s\.\d|schedule", row, re.IGNORECASE)),
            "chars": len(row),
            "row": row,
        })

    out = {
        "_what": "Every locked fact declaring a `superseded_value`, checked against the index row "
                 "that renders it. Built locally from scripts/precompute_rag_embeddings.py, the "
                 "same module the regen imports.",
        "_why_this_population": (
            "Defined by the DATA (the presence of a `superseded_value` field), not by which rows "
            "whoever ran it remembered changing. The 2026-10-06 dry run hand-picked two of twelve "
            "amended facts and reported SAFE TO RUN; the Kaggle gate then aborted on a third."),
        "_arm_authority": {
            "arm1_own_row": "BLOCKING. A fact's superseded figure in the row that renders that "
                            "fact has no innocent reading.",
            "arm2_whole_index": "REPORTING ONLY. Figure collisions across subjects are expected: "
                                "TZS 22,000 is the superseded special-report fee AND the current "
                                "annual-return fee. A figure test is context-blind by "
                                "construction, not by being too narrow.",
        },
        "rows_in_built_index": len(keys),
        "facts_declaring_a_supersession": len(population),
        "arm1_blocking": arm1,
        "arm1_clean": clean,
        "arm2_reporting": arm2,
        "provenance_leaking_rows": provenance_leaking,
        "_provenance_leak_is_not_an_accuracy_defect": (
            "These rows state the CURRENT value first and label the old one SUPERSEDED, so none "
            "serves a wrong figure. The defect is dilution and reachability: a label-led "
            "`key: value` fallback, a statutory citation inside the EMBEDDED text (forbidden by "
            "precompute_rag_embeddings.py's standing rule -- folding citations in cost nat_05 "
            "ranks 24 -> 59), and English provenance a user never needs. Fixing it changes "
            "SERVED CONTENT, so it needs the displacement harness, not an edit."),
        "planted_specimens": specimens,
    }
    # Absolute, because the module-level `os.chdir(REPO)` that used to make this work is gone:
    # a library may not relocate its caller's working directory at import. This was the only
    # cwd-dependent path in the file; every other one already joined REPO.
    os.makedirs(os.path.join(REPO, os.path.dirname(ARTIFACT)), exist_ok=True)
    with io.open(os.path.join(REPO, ARTIFACT), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"built index: {len(keys)} rows")
    print(f"facts declaring a supersession: {len(population)}")
    print(f"planted specimens: {len(specimens)} passed (instrument exercised both directions)\n")
    for r in arm1:
        print(f"  [BLOCKING] {r['fact']} (row '{r['row_key']}'): {r['verdict']}")
        for h in r.get("hits", []):
            print(f"             asserts {h['asserted_as']}")
    for r in clean:
        tag = "note" if r["verdict"] == "MENTIONS_UNDER_NEGATION" else "ok"
        print(f"  [{tag}] {r['fact']} -> row '{r['row_key']}': {r['verdict']}")
    if arm2:
        print("\n  ARM 2 (reporting only, collisions expected):")
        for r in arm2:
            print(f"    {r['token']} (from {r['fact']}) also asserted by: "
                  f"{r['also_asserted_by_rows']}")

    if provenance_leaking:
        print(f"\n  PROVENANCE LEAK (reported, NOT blocking): {len(provenance_leaking)} row(s) "
              f"serve `SUPERSEDES ...` prose to users")
        for r in provenance_leaking:
            print(f"    {r['fact']} -> row '{r['row_key']}'  {r['chars']} chars  "
                  f"label_led={r['label_led_fallback']}  "
                  f"cited={r['carries_citation_in_embedded_text']}")

    print(f"\nartifact: {ARTIFACT}")
    print(f"VERDICT: {'BLOCKING FINDINGS' if arm1 else 'no own-row supersession survives'}")
    return 1 if arm1 else 0


if __name__ == "__main__":
    raise SystemExit(main())
