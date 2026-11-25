"""2026-11-25 (founder, approved with amendments): the paye_residency statement route, the 'ukaazi wa kikodi' terminology (never 'ukazi'/'mkazi' alone: 'mkazi' reads as the immigration residence permit), the sourced 'final' on the 15%, the VAT exempt-sales-threshold statement, and the six repaired foreign-authority training pairs.
Probes both ways (R17, 37 in eval/refusal_gate/residency_probes_2026_11_25.jsonl, the founding specimen VERBATIM), statement pins to the QUOTED provisions, end to end with ZERO model calls, PLANTS (R26), pattern hygiene (R39), the sweep artifact and the corpus reach (R36)."""
import glob
import importlib.util
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import fidelity, routing   # noqa: E402
from chike.orchestrator import Orchestrator   # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "residency_probes_2026_11_25.jsonl")
R = "paye_residency"


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 37 and sum(r["expect"] == R for r in rows) >= 12 and sum(r["expect"] == "none" or r["expect"].startswith("not:") for r in rows) >= 18   # a loader returning nothing must fail (R20)
    return rows


def _verdict(q, expect):
    got = routing.fixed_statement_topic(q)
    if expect == "none":
        return got is None
    if expect.startswith("not:"):
        return got != expect[4:]
    return got == expect


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert _verdict(p["question"], p["expect"]), (routing.fixed_statement_topic(p["question"]), p["guards_against"])


_BARE = re.compile(r"(?i)(?<![a-z])ukazi(?![a-z])|(?<![a-z])mkazi(?![a-z])|(?<![a-z])wakazi(?![a-z])")


def test_terminology_is_ukaazi_wa_kikodi_everywhere_in_the_new_texts():
    from chike import clarification
    st = fs.fixed_statement(R).working
    hold = clarification.CONSTANT_RESTATEMENTS["foreign_15pct"]
    for name, t in (("statement", st), ("holding line", hold)):
        assert "UKAAZI WA KIKODI" in t, name
        assert not _BARE.search(t), (name, _BARE.search(t).group(0))                   # 'mkazi' alone reads as the immigration residence permit
    assert "mkaazi wa kikodi" in st and "kibali cha ukaazi cha uhamiaji" in st         # and the statement says a permit is a DIFFERENT matter


def test_statement_states_the_four_limbs_the_final_tax_and_no_section_number():
    st = fs.fixed_statement(R).working
    for token in ("makazi ya kudumu", "siku 183", "siku 122", "mtumishi au afisa wa Serikali", "asilimia 15 tambarare", "kodi ya mwisho (final)", "si 15%"):
        assert token in st, token
    assert "Kifungu" not in st and not re.search(r"(?i)s\.\s*\d|section\s+\d", st)      # R44


def test_the_note_carries_the_quoted_provisions_including_the_one_that_makes_the_15_percent_final():
    note = fs.fixed_statement(R).note
    assert "R.E.2023" in note and "assert_edition" in note
    assert "one hundred eighty three days or more" in note and "averaging more than one hundred twenty two days" in note
    assert "in the case of a non-resident withholdee - fifteen percent" in note
    assert "payments made to non-resident persons other than through a domestic permanent establishment of the person that are subject to withholding under Subdivision A" in note       # the 'final' provision (s.111(1)(e))
    assert "satisfies the withholdee's income tax liability" in note


def test_the_quoted_provisions_are_really_in_the_cached_act():
    """The note quotes the Act; this checks the quotes against the file itself (edition asserted first), so a mis-transcribed quote fails here."""
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import check_source_editions as cse
    import pypdf
    path = os.path.join(_ROOT, "data", "source_documents", "tra", "income_tax_act_cap332_re2023.pdf")
    cse.assert_edition(path, "2023")
    text = re.sub(r"\s+", " ", " ".join((pg.extract_text() or "") for pg in pypdf.PdfReader(path).pages))
    for q in ("amounting in aggregate to one hundred eighty three days or more", "averaging more than one hundred twenty two days in each such year of income",
              "in the case of a non-resident withholdee - fifteen percent",
              "payments made to non-resident persons other than through a domestic permanent establishment of the person that are subject to withholding under Subdivision A"):
        assert q in text, q


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "SHOULD NOT BE CALLED"


def _answer(q):
    _B.calls = 0
    return Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("q", ["Does a foreign employee pay PAYE at a different rate from a citizen?", "Is a resident foreigner taxed on the PAYE bands?", "PAYE ya mfanyakazi asiye mkazi ni asilimia ngapi?"])
def test_end_to_end_zero_model_calls_and_the_whole_statement(q):
    r = _answer(q)
    assert _B.calls == 0 and r.text == fs.fixed_statement(R).working, r.text


def test_the_route_is_never_auto_send_eligible():
    spec = importlib.util.spec_from_file_location("hc_res_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    assert "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES and "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


def test_plant_route_disabled_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != R))
    failed = [p for p in _probes() if p["expect"] == R and not _verdict(p["question"], p["expect"])]
    assert len(failed) >= 8, failed


def test_plant_veto_emptied_is_caught(monkeypatch):
    """R26, the other direction: with the veto emptied, the wrong-topic classes found by reading the sweep MUST reach the statement (they are what the veto exists for)."""
    patched = tuple((n, c, nd, (re.compile(r"(?!x)x") if n == R else v)) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", patched)
    failed = {p["id"] for p in _probes() if not _verdict(p["question"], p["expect"])}
    assert {"rs_11", "rs_14", "rs_21", "rs_25", "rs_30", "rs_31"} <= failed, failed      # only probes the VETO decides: rs_12 (director, no PAYE word) and rs_13 (Kenya, no foreign / residency word) never reach the cue and need no veto


def test_exclusivity_with_the_rate_and_band_routes_both_directions():
    assert routing.fixed_statement_topic("PAYE ni asilimia ngapi?") == "paye_rate"
    assert routing.fixed_statement_topic("Bendi za PAYE ni zipi?") == "paye_band_table"
    assert routing.fixed_statement_topic("Je, kuna tofauti kati ya kiwango cha kodi cha kwanza na cha pili kwa PAYE?") == "paye_rate"       # the regression found by the sweep
    for q in ("Does a foreign employee pay PAYE at a different rate from a citizen?", "Mgeni mwenye makazi ya kudumu Tanzania analipa PAYE kwa bendi au 15%?"):
        assert routing.fixed_statement_topics(q) == [R], q


def test_new_patterns_contain_no_control_characters():
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in (R, "paye_band_table", "paye_rate"):
            for p in (cue, need, veto):
                if p is not None:
                    assert not any(ord(c) < 32 for c in p.pattern), (n, repr(p.pattern))
    assert not any(ord(c) < 32 for c in routing._FS_TOPIC_ASK[R].pattern)


def test_the_sweep_artifact_is_committed_and_clean():
    d = json.load(io.open(os.path.join(_ROOT, "eval", "results", "sweep_residency_2026_11_25.json"), encoding="utf-8"))
    assert d["swept"] > 8000 and d["other"] == 0 and d["newly_both"] == [] and d["onto_new"] == len(d["changed"]) and d["membership"][R] >= 20


# ---------------- the six repaired training pairs (R37 handling, R36 reach) ----------------
def _texts(path):
    for line in io.open(path, encoding="utf-8"):
        if line.strip():
            o = json.loads(line)
            q = o.get("question_sw") or o.get("instruction") or ""
            for k in ("answer_sw", "answer_en", "output"):
                if isinstance(o.get(k), str):
                    yield path, q, o[k]


def test_no_live_stage_or_export_row_names_a_foreign_authority_or_url():
    n, bad = 0, []
    for g in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/raw_sources/*.jsonl", "datasets/tier1a/sft/*.jsonl"):
        for f in glob.glob(os.path.join(_ROOT, g)):
            for p, q, t in _texts(f):
                n += 1
                if fidelity.foreign_authority_sentences(q, t):
                    bad.append((os.path.relpath(p, _ROOT), q[:50], t[:80]))
    assert n > 10000 and not bad, bad[:5]            # a loader that read nothing must fail (R20)


def test_the_six_questions_are_kept_and_the_repair_is_logged():
    qs = ("Niambie kuhusu kodi ya VAT nchini Kenya.", "Kiwango cha PAYE Kenya ni asilimia ngapi?", "Uganda ina kizingiti gani cha usajili wa VAT?", "Niambie jinsi ya kulipa kodi nchini Uingereza", "Wafanyabiashara wa mpakani (cross-border traders) Tunduma", "Serikali ya Kenya inazuia nini kwa wafanyabiashara wa Ta")
    seen = {x: False for x in qs}
    for f in glob.glob(os.path.join(_ROOT, "datasets", "tier1a", "cleaned_pairs", "*.jsonl")):
        for _, q, t in _texts(f):
            for x in qs:
                if q.startswith(x):
                    seen[x] = True
                    assert "wasiliana na mamlaka ya kodi ya nchi husika" in t or "tax authority of the country concerned" in t or "TRA" in t, (x, t[:120])
    assert all(seen.values()), seen
    log = [json.loads(x) for x in io.open(os.path.join(_ROOT, "eval", "results", "foreign_authority_repairs_2026_11_25.jsonl"), encoding="utf-8") if x.strip()]
    assert len(log) == 12 and all(r["action"] == "authority_sentence_replaced_in_place" for r in log)
    assert not os.path.exists(os.path.join(_ROOT, "datasets", "tier1a", "rejected", "foreign_authority_repairs_2026_11_25.jsonl")), "a repair log in rejected/ is audited as a removal record"
