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
