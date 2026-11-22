"""2026-11-22: the FLAG-ONLY unsupported-figure check (handler_core.unsupported_figures). A flag on the review card, never a rewrite, never a block. R17 probes both ways -- nine of the fifteen are CLEAN, the arm that does the work --
the two tokenizer slips pinned, the subject-blindness limit pinned (so widening it is a visible change), and PLANTS (R26). The preliminary Gate 2 set is burned and appears nowhere here."""
import importlib.util
import io
import json
import os
import re

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_uf", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

_PROBES = os.path.join(_ROOT, "eval", "fidelity", "unsupported_figure_flag_probes_2026_11_22.jsonl")


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 15, len(rows)                         # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"]) >= 4 and sum(1 for r in rows if not r["expect"]) >= 9
    return rows


def _run(p):
    return hc.unsupported_figures(p["question"], p["draft"], p["facts"], p.get("engine_working"), p.get("model_calls", 1))


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_flags_exactly_what_was_authored(p):
    assert _run(p) == p["expect"], p["why"]


def test_tokenizer_slip_an_act_year_is_not_money():
    assert hc._uf_figures("Sheria ya Fedha 2025 na Cap.438 R.E. 2023") == []
    assert [f[0] for f in hc._uf_figures("TZS 2025 ilitozwa")] == ["2025"]          # a currency before it IS money: only the BARE year is exempt


def test_tokenizer_slip_a_decimal_comma_is_not_a_thousands_separator():
    assert [(f[0], f[1]) for f in hc._uf_figures("asilimia 3,5")] == [("3,5", 3.5)]
    assert [(f[0], f[1]) for f in hc._uf_figures("TZS 3,500 kwa mwezi")] == [("3,500", 3500.0)]


def test_the_flag_changes_nothing_but_the_item():
    row = {"ts": "2026-11-22T10:00:00+00:00", "sender_hash": "abcd1234ef", "question": "EFD inahitajika kwa biashara gani?"}
    item = hc.review_item(row, "255700000000", "Kizingiti cha EFD ni TZS 11,000,000 kwa mwaka.", None, ["EFD kwa kila mfanyabiashara."], model_calls=1)
    assert item["unsupported_figures"] == ["11,000,000"]
    assert item["draft"] == "Kizingiti cha EFD ni TZS 11,000,000 kwa mwaka." and item["status"] == "pending"      # the draft is untouched and still pending: FLAG-ONLY


def test_a_check_that_cannot_run_is_stored_as_none_and_says_so(monkeypatch):
    monkeypatch.setattr(hc, "unsupported_figures", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    row = {"ts": "2026-11-22T10:00:00+00:00", "sender_hash": "abcd1234ef", "question": "q"}
    item = hc.review_item(row, "255700000000", "d", None, [], model_calls=1)
    assert item["unsupported_figures"] is None                         # the hold still happens
    assert hc.unsupported_figure_lines(item) == [hc.UNSUPPORTED_FIGURE_NOT_RUN]


def test_an_item_stored_before_the_feature_says_nothing():
    assert hc.unsupported_figure_lines({"draft": "x"}) == []


def test_the_push_text_carries_the_flag_and_a_clean_item_does_not():
    row = {"ts": "2026-11-22T10:00:00+00:00", "sender_hash": "abcd1234ef", "question": "EFD inahitajika kwa biashara gani?"}
    bad = hc.review_item(row, "255700000000", "Kizingiti cha EFD ni TZS 11,000,000 kwa mwaka.", None, ["EFD kwa kila mfanyabiashara."], model_calls=1)
    ok = hc.review_item(row, "255700000000", "EFD inahitajika kwa kila mfanyabiashara.", None, ["EFD kwa kila mfanyabiashara."], model_calls=1)
    t_bad, t_ok = hc.notification_text(bad, "https://x/y"), hc.notification_text(ok, "https://x/y")
    assert "NAMBA ISIYO KWENYE VIGEZO: 11,000,000" in t_bad and "Figure not in served facts: 11,000,000" in t_bad
    assert "NAMBA ISIYO" not in t_ok and "Figure not in served facts" not in t_ok
    assert "Hakuna jibu linalotumwa mpaka mtu abonyeze" in t_bad                      # the hold copy is unchanged: this flag adds a line, it removes nothing


def test_plant_a_year_treated_as_money_flags_a_clean_probe(monkeypatch):
    monkeypatch.setattr(hc, "_uf_is_year", lambda raw: False)
    p = [x for x in _probes() if x["id"] == "uf_06"][0]
    assert _run(p) == ["2025"], "without the year exemption the Act-year probe must wrongly flag; if not, the exemption is decoration"


def test_plant_the_decimal_comma_reverted_flags_a_clean_probe(monkeypatch):
    monkeypatch.setattr(hc, "_uf_value", lambda raw: float(raw.replace(",", "")))
    p = [x for x in _probes() if x["id"] == "uf_07"][0]
    assert _run(p) != [], "reading 3,5 as 35 must make the clean probe flag; if not, the decimal-comma rule is decoration"


def test_plant_the_support_set_emptied_flags_every_clean_probe_that_has_a_figure(monkeypatch):
    monkeypatch.setattr(hc, "_uf_support", lambda q, f, w: (set(), set()))
    flagged_clean = [p["id"] for p in _probes() if not p["expect"] and p.get("model_calls", 1) >= 1 and not p.get("engine_working") and _run(p)]
    assert {"uf_06", "uf_07", "uf_08", "uf_09", "uf_14"} <= set(flagged_clean), flagged_clean


def test_new_patterns_contain_no_control_characters():
    for r in (hc._UF_NUM, hc._UF_UNIT_AFTER, hc._UF_UNIT_BEFORE):
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
    assert re.compile(hc._UF_NUM.pattern)


# ── the REAL review page (modal_whatsapp._d_page), rendered the way tests/test_link_failures.py renders it ─────────────────────────────────────────────────
def _page(monkeypatch, item_extra):
    import sys
    import types
    sys.path.insert(0, os.path.join(_ROOT, "tests"))
    from conftest import isolate_modal_stores
    for k, v in {"REVIEW_D_URL": "https://d.example", "REVIEW_CLAIM_URL": "https://c.example", "REVIEW_ACT_URL": "https://a.example"}.items():
        monkeypatch.setenv(k, v)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_uf", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "salt")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", "test-key")
    rid = "2026-11-12T00:41:28+00:00-b5908217"
    mw.REVIEW_QUEUE[rid] = dict({"review_id": rid, "ts_held": "2026-11-12T00:41:28+00:00", "question": "q", "draft": "Kizingiti ni TZS 11,000,000.", "status": "pending",
                                 "sender_tail": "5913", "sender_hash": "abc", "facts": ["F"], "engine_working": None, "answer_path": "fact"}, **item_extra)
    number = mw._settings().roster[0][0]
    resp = mw._d_page(rid, hc.reviewer_id("test-key", number), hc.review_token("test-key", rid, number))
    return resp.status_code, resp.body.decode("utf-8")


def test_the_real_page_shows_the_flag_above_the_evidence(monkeypatch):
    status, body = _page(monkeypatch, {"unsupported_figures": ["11,000,000"]})
    assert status == 200 and "NAMBA ISIYO KWENYE VIGEZO: 11,000,000" in body and "Figure not in served facts" in body
    assert body.index("NAMBA ISIYO") < body.index("Hakuna hesabu ya mfumo")          # above the evidence panel, where a reviewer meets it first


def test_the_real_page_is_quiet_for_a_clean_item_and_loud_when_the_check_did_not_run(monkeypatch):
    status, body = _page(monkeypatch, {"unsupported_figures": []})
    assert status == 200 and "NAMBA ISIYO" not in body and "haukufanya kazi" not in body
    status, body = _page(monkeypatch, {"unsupported_figures": None})
    assert status == 200 and "haukufanya kazi" in body
