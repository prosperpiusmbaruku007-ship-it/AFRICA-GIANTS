# -*- coding: utf-8 -*-
"""scripts/backup_dicts_local.py: read-only local backup, git-ignored only, never the bridge auth store, verified by reading back.
Plants: a non-ignored destination is refused; the auth store is refused by name; a tampered file fails verification; the destination the real script uses
(scratch/backups/...) really is git-ignored; the script has no write path to Modal."""
import ast
import importlib.util
import json
import os
import subprocess

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("backup_dicts_local", os.path.join(_ROOT, "scripts", "backup_dicts_local.py"))
bk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bk)

ALWAYS = lambda p: True       # noqa: E731


def _stores():
    return {"review_queue": ("chike-review-queue-kv", [("r1", {"q": "swali", "sender": "x"}), ("r2", {"q": "q2"})]),
            "transcripts": ("chike-transcripts-kv", [("t1", {"ts": 1})]),
            "autosend_claims": ("chike-autosend-kv", []),
            "identity_aliases": ("chike-identity-aliases-kv", None)}


def test_it_writes_every_store_reads_it_back_and_reports_counts(tmp_path):
    m = bk.write_backup(_stores(), str(tmp_path / "b"), ignored_check=ALWAYS)
    assert {k: v["count"] for k, v in m["stores"].items()} == {"review_queue": 2, "transcripts": 1, "autosend_claims": 0, "identity_aliases": 0}
    assert m["stores"]["identity_aliases"]["exists"] is False and m["stores"]["autosend_claims"]["exists"] is True, "absent and empty are different"
    assert bk.verify_backup(str(tmp_path / "b")) is True
    assert json.load(open(tmp_path / "b" / "review_queue.json", encoding="utf-8"))["r1"]["q"] == "swali"


def test_PLANT_a_destination_that_is_not_git_ignored_is_refused_and_nothing_is_written(tmp_path):
    with pytest.raises(bk.BackupRefused, match="not git-ignored"):
        bk.write_backup(_stores(), str(tmp_path / "b"), ignored_check=lambda p: False)
    assert not (tmp_path / "b").exists()


def test_PLANT_the_bridge_auth_store_is_refused_by_name():
    for name in ("chike-bridge-auth-kv", "some-token-store", "x-secret-kv"):
        with pytest.raises(bk.BackupRefused):
            bk.refuse_sensitive(name)
    bk.refuse_sensitive("chike-review-queue-kv")                                  # positive control: a normal store passes
    st = _stores()
    st["auth"] = ("chike-bridge-auth-kv", [("creds", "secret")])
    with pytest.raises(bk.BackupRefused):
        bk.write_backup(st, "x", ignored_check=ALWAYS)


def test_PLANT_a_tampered_or_truncated_backup_fails_verification(tmp_path):
    bk.write_backup(_stores(), str(tmp_path / "b"), ignored_check=ALWAYS)
    f = tmp_path / "b" / "review_queue.json"
    f.write_bytes(f.read_bytes() + b" ")
    with pytest.raises(AssertionError, match="review_queue"):
        bk.verify_backup(str(tmp_path / "b"))


def test_the_destination_the_real_script_uses_is_git_ignored():
    stamp_dir = os.path.join(_ROOT, "scratch", "backups", "20990101T000000Z")
    r = subprocess.run(["git", "check-ignore", "-q", stamp_dir], cwd=_ROOT)
    assert r.returncode == 0, "scratch/backups must be ignored by git or the script will (rightly) refuse to run"
    assert bk.is_git_ignored(stamp_dir) is True and bk.is_git_ignored(os.path.join(_ROOT, "scripts", "x")) is False, "and the check can say no"


def test_the_script_only_reads():
    src = open(os.path.join(_ROOT, "scripts", "backup_dicts_local.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not (attrs & {"put", "pop", "clear", "update", "batch_upload", "remove_file", "delete"}), attrs & {"put", "pop", "clear", "update"}
    code = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith(("#", '"""')))
    assert "create_if_missing=True" not in code and "upload" not in code.lower().replace("never uploaded", "").replace("nothing was uploaded", "")
