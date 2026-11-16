"""Auto-send FAIL-CLOSED regression (founder, 2026-11-17): engine:corporate_tax answered two dividend-withholding questions with the corporate income tax rate (set #2 s2_15/s2_18) and was auto-send eligible.
It is REMOVED from the allowlist and named in the EXCLUDED set, so deleting the exclusion alone cannot quietly re-admit it. It returns only on the founder's explicit word after the wrong-topic audit clears it."""
import importlib.util
import os

spec = importlib.util.spec_from_file_location("hc", os.path.join("chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)

BASE = {"status": "pending", "draft": "x", "engine_working": "w", "facts": [{"t": "f"}], "model_calls": 0, "guards": [], "fallback": False}


def test_corporate_tax_is_out_of_auto_send_and_named_excluded():
    assert "engine:corporate_tax" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES
    assert "engine:corporate_tax" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES


def test_a_model_free_corporate_tax_reply_is_refused_and_a_still_eligible_route_is_not():
    ok, why = hc.engine_only_verdict(dict(BASE, answer_path="engine:corporate_tax"))
    assert ok is False and "excluded" in why
    # positive control (R26): the same item on an eligible route is accepted, so the refusal above is the ROUTE and nothing else
    assert hc.engine_only_verdict(dict(BASE, answer_path="engine:sdl"))[0] is True


# ---- the wrong-topic audit of every eligible route (2026-11-17): the committed probes must all pass, and the corporate_tax veto must be WATCHED to matter (R26) ----
def _audit_module():
    sp = importlib.util.spec_from_file_location("audit_wt", os.path.join("eval", "controls", "audit_autosend_wrong_topic_2026_11_17.py"))
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def test_every_wrong_topic_probe_routes_acceptably():
    from chike import routing
    mod = _audit_module()
    assert len(mod.PROBES) >= 60
    bad = [(q, routing.detect_intent(q)) for _r, q, ok, _w in mod.PROBES if routing.detect_intent(q) not in ok]
    assert not bad, bad


def test_planted_corporate_veto_disabled_lets_the_dividend_question_back_in(monkeypatch):
    import re

    from chike import routing
    q = "Nina kampuni ambayo imeorodheshwa DSE. Tukigawa gawio kwa wanahisa, withholding tax yake ni 5%, ndiyo?"
    assert routing.detect_intent(q) != "corporate_tax"
    monkeypatch.setattr(routing, "_CORP_NEIGHBOUR_VETO", re.compile(r"(?!x)x"))
    assert routing.detect_intent(q) == "corporate_tax", "with the veto removed the s2_18 question must be captured again, or the veto proves nothing"
