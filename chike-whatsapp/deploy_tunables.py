# -*- coding: utf-8 -*-
"""The chike-whatsapp deploy-time tunables: ONE committed, secret-free source, and the pure functions that compare it with /health.

WHY (2026-11-16). The tunables are baked into the image at DEPLOY time (modal_whatsapp._DEPLOY_TUNABLES) from the deploying shell's
environment. Twice that has shipped a pilot with the wrong settings: 2026-11-10 a bare deploy (cohort 0, links unissuable) and 2026-11-15 a
deploy whose shell had not kept the exports (links off, review timeout off, cohort 0, MAX_RENOTIFIES back to 3). Both failed safe, both were
caught by /health AFTER the deploy, and the pre-flight could not have caught the second at all: it certified the PRE-FLIGHT shell's env, not the
deploy command's. So the values now live in `deploy_tunables.json`, read by modal_whatsapp.py itself, and the pre-flight compares the image it
builds with (a) this file and (b) the LIVE app's /health.

PURE: no network, no modal import, so tests/test_deploy_tunables.py can plant a missing and a changed value and watch each refuse.
Credentials are refused here by name: a tunables file that could hold a secret would be committed to a public repo.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "deploy_tunables.json")

REQUIRED = ("COHORT_SIZE", "CLAIM_TTL_S", "RENOTIFY_AFTER_S", "MAX_RENOTIFIES", "AUTOSEND_ENGINE", "AUTOSEND_AFTER_S", "SUPERVISED",
            "MODEL_TIMEOUT_S", "SUPERVISED_MODEL_TIMEOUT_S", "SLOW_ACK_AFTER_S", "SECOND_ACK_AFTER_S",
            "REVIEW_D_URL", "REVIEW_CLAIM_URL", "REVIEW_ACT_URL")
_SECRET_LIKE = re.compile(r"token|secret|password|salt|signing|roster|api_?key", re.IGNORECASE)
_TRUE = ("1", "true", "yes", "on")


class TunablesError(Exception):
    """The committed tunables are missing, malformed or contain something that looks like a credential."""


def load(path=None):
    """The committed tunables as {name: str}. Raises TunablesError on a missing/empty required key, an unknown key, a non-string value,
    or a key whose NAME looks like a credential. Keys starting with '_' are notes and are dropped."""
    path = path or FILE
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except Exception as e:                                           # noqa: BLE001
        raise TunablesError(f"cannot read tunables file {path!r}: {type(e).__name__}: {e}") from e
    if not isinstance(raw, dict):
        raise TunablesError("tunables file must be a JSON object")
    vals = {k: v for k, v in raw.items() if not k.startswith("_")}
    missing = [k for k in REQUIRED if not isinstance(vals.get(k), str) or not vals[k].strip()]
    if missing:
        raise TunablesError(f"required tunables missing or empty: {missing}")
    unknown = [k for k in vals if k not in REQUIRED]
    if unknown:
        raise TunablesError(f"unknown tunables (add to REQUIRED deliberately): {unknown}")
    bad = [k for k in vals if _SECRET_LIKE.search(k)]
    if bad:
        raise TunablesError(f"credential-looking keys are not allowed in a committed file: {bad}")
    return vals


def env_conflicts(committed, environ):
    """{name: (shell value, committed value)} for every tunable the shell sets to something DIFFERENT from the committed file."""
    return {k: (environ[k], v) for k, v in committed.items() if environ.get(k) not in (None, "") and environ[k] != v}


def _num(s):
    return float(s)


def expected_view(committed):
    """The /health fields the committed tunables must produce."""
    return {
        "cohort_size": int(committed["COHORT_SIZE"]),
        "claim_ttl_s": _num(committed["CLAIM_TTL_S"]),
        "renotify_after_s": _num(committed["RENOTIFY_AFTER_S"]),
        "max_renotifies": int(committed["MAX_RENOTIFIES"]),
        "autosend_enabled": committed["AUTOSEND_ENGINE"].strip().lower() in _TRUE,
        "autosend_after_s": _num(committed["AUTOSEND_AFTER_S"]),
        "supervised": committed["SUPERVISED"].strip().lower() in _TRUE,
        "supervised_raw_env": committed["SUPERVISED"],
        "model_timeout_s": _num(committed["MODEL_TIMEOUT_S"]),
        "supervised_model_timeout_s": _num(committed["SUPERVISED_MODEL_TIMEOUT_S"]),
        "slow_ack_after_s": _num(committed["SLOW_ACK_AFTER_S"]),
        "second_ack_after_s": _num(committed["SECOND_ACK_AFTER_S"]),
        "disclosure_enabled": True,
        "review_urls_set": True,
        "can_issue_links": True,
    }


def health_view(h):
    """The same fields read out of a /health payload. A missing field is None, which never equals an expected value."""
    h = h or {}
    cohort, roster = h.get("cohort") or {}, h.get("roster") or {}
    rt, disc = h.get("review_timeout") or {}, h.get("disclosure") or {}
    return {
        "cohort_size": cohort.get("declared_size"),
        "claim_ttl_s": roster.get("claim_ttl_s"),
        "renotify_after_s": roster.get("renotify_after_s"),
        "max_renotifies": h.get("max_renotifies"),
        "autosend_enabled": rt.get("enabled"),
        "autosend_after_s": rt.get("after_s"),
        "supervised": h.get("supervised"),
        "supervised_raw_env": h.get("supervised_raw_env"),
        "model_timeout_s": h.get("model_timeout_s"),
        "supervised_model_timeout_s": h.get("supervised_model_timeout_s"),
        "slow_ack_after_s": h.get("slow_ack_after_s"),
        "second_ack_after_s": h.get("second_ack_after_s"),
        "disclosure_enabled": disc.get("enabled"),
        "review_urls_set": roster.get("review_urls_set"),
        "can_issue_links": roster.get("can_issue_links"),
    }


def _same(a, b):
    if a is None or b is None:
        return False                      # a field that did not arrive never equals anything
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return str(a) == str(b)


def diff_views(left, right, left_name, right_name):
    """['field: left=X right=Y', ...] for every field that differs; a missing field (None) on either side differs."""
    return [f"{k}: {left_name}={left.get(k)!r} {right_name}={right.get(k)!r}" for k in left if not _same(left.get(k), right.get(k))]
