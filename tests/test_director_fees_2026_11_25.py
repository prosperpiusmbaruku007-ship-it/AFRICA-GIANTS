"""2026-11-25 (founder, approved with amendments): the director_fees_wht statement route. The 15% on director's fees for residents AND non-residents; FINAL for a non-resident, a credit against the year's tax for a resident ("kiasi kilichokatwa kinahesabiwa kupunguza kodi yake ya mwaka anapowasilisha ritani", never "mkopo", which reads as a loan);
the full-time service director is sent to TRA with NO inference about his pay. Probes both ways (R17, 21 in eval/refusal_gate/director_probes_2026_11_25.jsonl), the QUOTED provisions checked against the cached Act (edition asserted), end to end with ZERO model calls, PLANTS (R26), hygiene (R39), the sweep artifact."""
import importlib.util
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import routing   # noqa: E402
from chike.orchestrator import Orchestrator   # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "director_probes_2026_11_25.jsonl")
D = "director_fees_wht"


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 21 and sum(r["expect"] == D for r in rows) >= 9 and sum(r["expect"] == "none" or r["expect"].startswith("not:") for r in rows) >= 9   # a loader returning nothing must fail (R20)
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


def test_statement_text_carries_the_founders_amendments_and_nothing_he_removed():
    t = fs.fixed_statement(D).working
    assert "kiasi kilichokatwa kinahesabiwa kupunguza kodi yake ya mwaka anapowasilisha ritani (tax credit)" in t
    assert "mkopo" not in t.lower()                                                    # "mkopo" reads as a loan
    assert "Kiwango hiki hakimhusu mkurugenzi wa muda wote kama alivyofafanuliwa na Sheria; kwa mkurugenzi wa muda wote, thibitisha utaratibu na TRA." in t
    assert "mshahara wake" not in t and "mapato ya kawaida ya ajira" not in t and "nafasi ya usimamizi" not in t      # the paraphrase of the definition and the inference about his pay are DROPPED
    assert "asilimia 15" in t and "kodi ya mwisho (final)" in t and "iwe mpokeaji ni mkaazi wa kikodi au asiye mkaazi wa kikodi" in t
    assert not re.search(r"(?i)(?<![a-z])(?:mkazi|wakazi|ukazi)(?![a-z])", t) and "Kifungu" not in t and not re.search(r"(?i)s\.\s*\d|section\s+\d", t)   # terminology and R44


def test_the_note_quotes_the_full_time_definition_verbatim_and_the_final_and_credit_provisions():
    note = fs.fixed_statement(D).note
    assert "R.E.2023" in note and "assert_edition" in note
    assert "means a person at a managerial position and is in full time service in a corporation" in note
    assert "in the case of director's fees referred to in section 7(2)(h) - fifteen percent" in note
    assert "satisfies the withholdee's income tax liability" in note and "is entitled to a tax credit in an amount equal to the tax treated as paid" in note


def test_every_quoted_provision_is_really_in_the_cached_act():
    """The note quotes the Act; this checks the quotes against the file (edition asserted first), so a mis-transcribed quote fails here."""
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import check_source_editions as cse
    import pypdf
    path = os.path.join(_ROOT, "data", "source_documents", "tra", "income_tax_act_cap332_re2023.pdf")
    cse.assert_edition(path, "2023")
    text = re.sub(r"\s+", " ", " ".join((pg.extract_text() or "") for pg in pypdf.PdfReader(path).pages)).replace("’", "'")
    for q in ("means a person at a managerial position and is in full time service in a corporation", "annual director's fees payable to a director other than a full time service director",
              "in the case of director's fees referred to in section 7(2) (h) - fifteen percent".replace("7(2) (h)", "7(2) (h)"),
              "payments made to non-resident persons other than through a domestic permanent establishment of the person that are subject to withholding under Subdivision A",
              "The withholdee of a payment that is not a final withholding payment shall be treated as having paid any income tax",
              "is entitled to a tax credit in an amount equal to the tax treated as paid for the year of income in which the payment is derived"):
        assert q in text, q


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "SHOULD NOT BE CALLED"


@pytest.mark.parametrize("q", ["WHT kwa ada ya mkurugenzi ni asilimia ngapi?", "Mkurugenzi mgeni anapokea ada ya mkurugenzi, WHT ni asilimia ngapi?", "Ada ya mkurugenzi wa muda wote inakatwa vipi?"])
def test_end_to_end_zero_model_calls_and_the_whole_statement(q):
    _B.calls = 0
    r = Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q)
    assert _B.calls == 0 and r.text == fs.fixed_statement(D).working, r.text


def test_the_route_is_never_auto_send_eligible():
    spec = importlib.util.spec_from_file_location("hc_dir_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    assert "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES and "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


def test_plant_route_disabled_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != D))
    failed = [p for p in _probes() if p["expect"] == D and not _verdict(p["question"], p["expect"])]
    assert len(failed) >= 7, failed


def test_plant_veto_emptied_is_caught(monkeypatch):
    patched = tuple((n, c, nd, (re.compile(r"(?!x)x") if n == D else v)) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", patched)
    failed = {p["id"] for p in _probes() if not _verdict(p["question"], p["expect"])}
    assert {"df_10", "df_13", "df_14", "df_15", "df_16", "df_18"} <= failed, failed


def test_exclusivity_with_the_residency_route_both_directions():
    assert routing.fixed_statement_topics("Mkurugenzi mgeni analipa PAYE kwa bendi au 15%?") == ["paye_residency"]
    assert routing.fixed_statement_topics("Mkurugenzi mgeni anapokea ada ya mkurugenzi, WHT ni asilimia ngapi?") == [D]
    assert routing.fixed_statement_topics("Does a foreign employee pay PAYE at a different rate from a citizen?") == ["paye_residency"]


def test_new_patterns_contain_no_control_characters():
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in (D, "paye_residency"):
            for p in (cue, need, veto):
                if p is not None:
                    assert not any(ord(c) < 32 for c in p.pattern), (n, repr(p.pattern))
    assert not any(ord(c) < 32 for c in routing._FS_TOPIC_ASK[D].pattern)


def test_the_sweep_artifact_is_committed_and_clean():
    d = json.load(io.open(os.path.join(_ROOT, "eval", "results", "sweep_director_2026_11_25.json"), encoding="utf-8"))
    assert d["swept"] > 8000 and d["newly_both"] == [] and d["membership"][D] >= 20 and d["onto_new"] == d["membership"][D]
    assert all(c["after"][1] in (D, "paye_residency") for c in d["changed"]), "the only 'other' changes are the two probes the residency route now owns (exclusivity)"
