"""2026-11-16: the chike-whatsapp deploy gate, completed.

Two deploys shipped the wrong pilot settings because the tunables lived in the deploying shell (2026-11-10 bare deploy; 2026-11-15 exports that
did not persist between shell calls). Now: (1) ONE committed, secret-free source (`chike-whatsapp/deploy_tunables.json`) that modal_whatsapp.py
reads itself, so the deploy command cannot go out without them; (2) a shell value that DIFFERS from it aborts the deploy; (3) the pre-flight
compares the image it builds with the file AND with the live /health, refusing on any difference without a written override; (4) auto-send
off REFUSES. Every refusal is PLANTED here -- a missing value, a changed value, a drifted live value, a dead live app, auto-send off -- and
every one has a clean case that must pass (R26)."""
import copy
import importlib.util
import json
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import preflight_deploy as pf   # noqa: E402

_spec = importlib.util.spec_from_file_location("dt_under_test", os.path.join(_ROOT, "chike-whatsapp", "deploy_tunables.py"))
dt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dt)

# The live /health of chike-whatsapp read on 2026-11-15 after the corrective deploy (build 00516ec), reduced to the tunable-bearing fields --
# EXCEPT max_renotifies, which is 1 here (2026-11-26): the fixture is "the app as deployed from the committed file", and the committed file moved
# 0 -> 1 after the reminder storm. The REAL live app reads 0 until the approved deploy; the pre-flight's live-vs-file gate refuses until then.
LIVE = {"supervised": True, "supervised_raw_env": "1", "max_renotifies": 1, "model_timeout_s": 240.0,
        "supervised_model_timeout_s": 1800.0, "slow_ack_after_s": 12.0, "send_ceiling": {"per_recipient_per_hour": 20, "global_per_hour": 150, "reviewer_per_recipient_per_hour": 40, "digest_only_above": 8}, "daily_question_limit": 20, "digest_min_wait_s": 3600.0, "second_ack_after_s": 45.0,
        "review_timeout": {"enabled": True, "after_s": 900.0, "raw_flag": "1", "raw_after_s": "900"},
        "cohort": {"declared_size": 15}, "disclosure": {"enabled": True},
        "roster": {"reviewers": 1, "signing_key_set": True, "claim_ttl_s": 900.0, "renotify_after_s": 420.0,
                   "review_urls_set": True, "can_issue_links": True},
        "bridge": {"session_status": "connected", "session_detail": "open", "transport": "bridge", "lease_holders": 1,
                   "alerting": {"configured": True, "missing": []}}}
COMMITTED = dt.load()


# ── the committed file ────────────────────────────────────────────────────────────────────────────
def test_the_committed_file_loads_and_equals_the_live_app_it_was_copied_from():
    assert dt.diff_views(dt.expected_view(COMMITTED), dt.health_view(LIVE), "committed", "live") == []


def test_the_file_is_secret_free_and_complete():
    raw = json.load(open(dt.FILE, encoding="utf-8"))
    assert set(k for k in raw if not k.startswith("_")) == set(dt.REQUIRED)
    for k, v in raw.items():
        assert not dt._SECRET_LIKE.search(k), k
        assert "REVIEWER_ROSTER" not in k and "SIGNING" not in k


def _write(tmp_path, mutate):
    raw = json.load(open(dt.FILE, encoding="utf-8"))
    mutate(raw)
    p = tmp_path / "t.json"
    p.write_text(json.dumps(raw), encoding="utf-8")
    return str(p)


@pytest.mark.parametrize("name,mutate", [
    ("a MISSING value", lambda r: r.pop("MAX_RENOTIFIES")),
    ("an EMPTY value", lambda r: r.update(COHORT_SIZE="")),
    ("a non-string value", lambda r: r.update(COHORT_SIZE=15)),
    ("an UNKNOWN key", lambda r: r.update(SOMETHING_NEW="1")),
    ("a credential-looking key", lambda r: r.update(REVIEW_SIGNING_KEY="x")),
    ("a token key", lambda r: r.update(ADMIN_TOKEN="x")),
])
def test_a_bad_tunables_file_is_refused_at_load(tmp_path, name, mutate):
    with pytest.raises(dt.TunablesError):
        dt.load(_write(tmp_path, mutate))


def test_a_clean_file_loads(tmp_path):
    assert dt.load(_write(tmp_path, lambda r: None)) == COMMITTED


# ── shell vs file ─────────────────────────────────────────────────────────────────────────────────
def test_a_shell_value_that_differs_from_the_file_is_a_conflict():
    assert dt.env_conflicts(COMMITTED, {"COHORT_SIZE": "3"}) == {"COHORT_SIZE": ("3", "15")}


@pytest.mark.parametrize("env", [{}, {"COHORT_SIZE": "15"}, {"COHORT_SIZE": ""}, {"UNRELATED": "x"}])
def test_an_equal_or_unset_shell_is_no_conflict(env):
    assert dt.env_conflicts(COMMITTED, env) == {}


def _import_modal_whatsapp(env_extra, code_after=""):
    code = ("import importlib.util,sys,os\n"
            f"sys.path.insert(0, {os.path.join(_ROOT, 'chike-whatsapp')!r})\n"
            f"spec=importlib.util.spec_from_file_location('mw', {os.path.join(_ROOT, 'chike-whatsapp', 'modal_whatsapp.py')!r})\n"
            "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n" + code_after)
    env = {k: v for k, v in os.environ.items() if k not in dt.REQUIRED and k not in ("CHIKE_TUNABLES_OVERRIDE", "CHIKE_TUNABLES_FILE",
                                                                                      "CHIKE_PREFLIGHT_NO_SCHEDULE")}
    env.update(env_extra)
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                          cwd=_ROOT)


def test_the_deploy_reads_the_committed_file_even_when_the_shell_holds_nothing():
    """POSITIVE CONTROL: a bare shell (the 2026-11-15 mistake) still yields every tunable."""
    r = _import_modal_whatsapp({}, "print('TUN=' + repr(m._TUNABLES))")
    assert r.returncode == 0, r.stderr[-800:]
    assert repr(COMMITTED) in r.stdout


def test_a_changed_shell_value_aborts_the_deploy_before_anything_is_built():
    r = _import_modal_whatsapp({"COHORT_SIZE": "3"})
    assert r.returncode != 0 and "DEPLOY REFUSED" in r.stderr and "COHORT_SIZE" in r.stderr, r.stderr[-800:]


def test_an_explicit_override_lets_the_shell_value_win():
    r = _import_modal_whatsapp({"COHORT_SIZE": "3", "CHIKE_TUNABLES_OVERRIDE": "shrinking the cohort on purpose"},
                               "print('COHORT=' + m._TUNABLES['COHORT_SIZE'])")
    assert r.returncode == 0 and "COHORT=3" in r.stdout, r.stderr[-800:]


def test_the_tunables_file_seam_is_honoured_only_in_the_preflight_throwaway_build(tmp_path):
    bad = _write(tmp_path, lambda r: r.pop("MAX_RENOTIFIES"))
    real = _import_modal_whatsapp({"CHIKE_TUNABLES_FILE": bad})            # a REAL deploy: the seam must be ignored
    assert real.returncode == 0, real.stderr[-800:]
    pre = _import_modal_whatsapp({"CHIKE_TUNABLES_FILE": bad, "CHIKE_PREFLIGHT_NO_SCHEDULE": "1"})   # the throwaway build: planted file used
    assert pre.returncode != 0 and "MAX_RENOTIFIES" in pre.stderr, pre.stderr[-800:]


def test_the_image_env_is_built_from_the_tunables_and_stays_before_the_local_adds():
    """The chain rule (2026-10-08): .env() must precede add_local_*. The tunables ride the existing .env() call."""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    assert "**_TUNABLES" in src and src.index("**_TUNABLES") < src.index(".add_local_dir(_HERE")
    assert pf.gate_chain_lint("chike-whatsapp/modal_whatsapp.py") == []


# ── the pre-flight comparison: image vs file, image vs LIVE ──────────────────────────────────────
def _fails(image, live=LIVE, committed=COMMITTED, live_err=None, override=None):
    return pf.check_tunables(image, live, committed, live_err, override)


def test_an_image_identical_to_file_and_live_passes_clean():
    assert _fails(copy.deepcopy(LIVE)) == ([], [])


@pytest.mark.parametrize("name,mutate,needle", [
    ("MAX_RENOTIFIES back to the default 3", lambda h: h.update(max_renotifies=3), "max_renotifies"),
    ("RENOTIFY_AFTER_S changed", lambda h: h["roster"].update(renotify_after_s=1800.0), "renotify_after_s"),
    ("CLAIM_TTL_S changed", lambda h: h["roster"].update(claim_ttl_s=60.0), "claim_ttl_s"),
    ("AUTOSEND seconds changed", lambda h: h["review_timeout"].update(after_s=300.0), "autosend_after_s"),
    ("AUTOSEND off", lambda h: h["review_timeout"].update(enabled=False), "autosend_enabled"),
    ("COHORT_SIZE 0 (the 2026-11-15 mistake)", lambda h: h["cohort"].update(declared_size=0), "cohort_size"),
    ("SUPERVISED off", lambda h: h.update(supervised=False), "supervised"),
    ("SUPERVISED could not be read", lambda h: h.update(supervised=None), "supervised"),
    ("disclosure off", lambda h: h["disclosure"].update(enabled=False), "disclosure_enabled"),
    ("review URLs unset (the 2026-11-15 mistake)", lambda h: h["roster"].update(review_urls_set=False, can_issue_links=False),
     "review_urls_set"),
    ("a model timeout changed", lambda h: h.update(model_timeout_s=60.0), "model_timeout_s"),
    ("a field missing from /health", lambda h: h["roster"].pop("renotify_after_s"), "renotify_after_s"),
])
def test_a_changed_or_missing_tunable_in_the_image_REFUSES(name, mutate, needle):
    h = copy.deepcopy(LIVE)
    mutate(h)
    fails, warns = _fails(h)
    assert any(needle in f for f in fails), (name, fails)
    assert any("deploy_tunables.json" in f for f in fails), "the image must also be refused against the FILE"


def test_a_live_app_that_drifted_from_the_file_refuses_without_an_override_and_only_warns_with_one():
    """The case: the file was edited (intended change) so live differs. Image == file, image != live."""
    new = dict(COMMITTED, RENOTIFY_AFTER_S="600")
    image = copy.deepcopy(LIVE)
    image["roster"]["renotify_after_s"] = 600.0
    fails, warns = _fails(image, committed=new)
    assert fails and "LIVE" in fails[0] and "renotify_after_s" in fails[0] and warns == []
    fails, warns = _fails(image, committed=new, override="moving re-notify to 10 minutes, founder 2026-11-16")
    assert fails == [] and warns and "OVERRIDDEN" in warns[0] and "founder 2026-11-16" in warns[0]


def test_the_override_never_excuses_an_image_that_ignores_the_file():
    image = copy.deepcopy(LIVE)
    image["max_renotifies"] = 3
    fails, _ = _fails(image, override="whatever")
    assert any("deploy_tunables.json" in f for f in fails)


def test_an_unreadable_live_app_refuses_unless_overridden():
    fails, warns = _fails(copy.deepcopy(LIVE), live=None, live_err="URLError")
    assert fails and "NOT a pass" in fails[0]
    fails, warns = _fails(copy.deepcopy(LIVE), live=None, live_err="URLError", override="first-ever deploy")
    assert fails == [] and "OVERRIDDEN" in warns[0]


def test_the_live_url_is_derived_from_the_preview_url():
    assert pf._live_health_url("https://ws--chike-whatsapp-preflight-health.us-east.modal.run") == \
        "https://ws--chike-whatsapp-health.us-east.modal.run"
    assert pf._live_health_url("https://ws--chike-whatsapp-health.us-east.modal.run") is None     # never compare an app with itself
    assert pf._live_health_url(None) is None


# ── auto-send off now REFUSES (it used to warn) ─────────────────────────────────────────────────
def _good_for_3b():
    h = copy.deepcopy(LIVE)
    h["bridge"]["alerting"] = {"configured": True, "missing": []}
    return h


def test_auto_send_off_REFUSES_not_warns():
    """History: until 2026-11-16 this test asserted the opposite -- off only WARNED, 'the safe direction'. It is safe for R7 and silent for
    a participant: with the timeout off no holding message is ever sent. The 2026-11-15 deploy shipped exactly that with every gate green."""
    del pf.WARNINGS[:]
    assert pf.check_whatsapp_health(_good_for_3b(), today="2026-11-16") == []                 # POSITIVE CONTROL: on passes
    for rt in ({"enabled": False, "raw_flag": None, "raw_after_s": None}, {}, None, {"enabled": None}):
        h = _good_for_3b()
        h["review_timeout"] = rt
        fails = pf.check_whatsapp_health(h, today="2026-11-16")
        assert any("review_timeout.enabled" in f and "silence" in f for f in fails), (rt, fails)
    h = _good_for_3b()
    h.pop("review_timeout")                                                                    # a field that did not arrive
    assert pf.check_whatsapp_health(h, today="2026-11-16")


def test_the_preflight_no_longer_tells_the_operator_to_export_env_vars():
    src = open(os.path.join(_ROOT, "scripts", "preflight_deploy.py"), encoding="utf-8").read()
    assert "export them once" not in src and "deploy_tunables.json" in src
    assert "--tunables-file" in src
