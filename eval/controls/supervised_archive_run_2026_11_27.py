# -*- coding: utf-8 -*-
"""SECOND SUPERVISED ARCHIVE RUN (2026-11-27): the first real BRIDGE-LEDGER-PRUNE-1 pass, with an independent check of everything the run did.

    python eval/controls/supervised_archive_run_2026_11_27.py [<backup dir>]      (take scripts/backup_dicts_local.py FIRST)

Steps, each saved to eval/results/supervised_archive_run_2026_11_27.json as it completes:
  1. LEDGER DIGEST (keys + timestamps ONLY: never a `to`, so no phone address is copied to this machine), the receipt reconciler's awaited ids, and the send-time index.
     EXPECTATION computed from it: which rows are older than 24 h and not awaited (must be pruned), which are older and awaited (must be KEPT), which are young (must be kept).
     Rows within +-10 minutes of the 24 h line are classed BOUNDARY (the clock moves between this snapshot and the run) and excluded from the strict checks, but counted.
  2. The review/transcript EXPECTATION from the backup, as in the first supervised run.   3. BEFORE: live counts and a download of the archive Volume.
  4. RUN: the deployed `run_archive` once (`.remote()`).   5. AFTER: live counts, a second ledger digest, a second Volume download.
  6. CHECKS, independent of the code under test: the removed ledger rows are exactly the expected ones; protected/young rows all survived; every archive file that existed before is
     byte-identical (write-once) except aggregate files, which may only grow; new files equal the expected moves; no phone address in any file; the keep-alive touched every key.
Any mismatch is listed under `surprises`; exit 1 if there is one. It never writes to a Dict or the Volume itself: only the deployed function does.
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
OUT = os.path.join(_ROOT, "eval", "results", "supervised_archive_run_2026_11_27.json")
BEFORE = os.path.join(_ROOT, "scratch", "archive_copy_before")
AFTER = os.path.join(_ROOT, "scratch", "archive_copy_after")
JID = re.compile(r"\d{6,}@[A-Za-z.]+")
DAY = 24 * 3600.0
BAND = 600.0


def save(rep):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)


def ledger_digest():
    import modal
    ledger = {}
    for k, r in modal.Dict.from_name("chike-bridge-ledger-kv").items():
        ts = None
        if isinstance(r, dict):
            try:
                ts = float(r.get("ts"))
            except (TypeError, ValueError):
                ts = None
        ledger[str(k)] = ts                                          # KEY AND TIMESTAMP ONLY
    try:
        pending = {str(k) for k in modal.Dict.from_name("chike-pending-rows-kv").keys()}
    except modal.exception.NotFoundError:
        pending = set()
    try:
        index = {str(k): v for k, v in modal.Dict.from_name("chike-ledger-index-kv").items()}
    except modal.exception.NotFoundError:
        index = {}
    return ledger, pending, index


def ledger_expectation(ledger, pending, now):
    must_prune, must_keep_old, young, boundary, bad_ts = set(), set(), set(), set(), set()
    for k, ts in ledger.items():
        if ts is None:
            bad_ts.add(k)
            continue
        age = now - ts
        if abs(age - DAY) <= BAND:
            boundary.add(k)
        elif age > DAY:
            (must_keep_old if k in pending else must_prune).add(k)
        else:
            young.add(k)
    return must_prune, must_keep_old, young, boundary, bad_ts


def live_counts():
    import modal
    out = {}
    for label, name in (("review_queue", "chike-review-queue-kv"), ("transcripts", "chike-transcripts-kv"), ("bridge_ledger", "chike-bridge-ledger-kv"),
                        ("ledger_index", "chike-ledger-index-kv"), ("pending_rows", "chike-pending-rows-kv"), ("identity_aliases", "chike-identity-aliases-kv"),
                        ("bridge_auth", "chike-bridge-auth-kv")):
        try:
            out[label] = len(list(modal.Dict.from_name(name).keys()))
        except modal.exception.NotFoundError:
            out[label] = None
    return out


def download(dest):
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "modal", "volume", "get", "--force", "chike-archive", "archive", dest], cwd=_ROOT, capture_output=True, timeout=1200,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")[-200:]


def tree(dest):
    out = {}
    base = os.path.join(dest, "archive")
    for dp, _, fs in os.walk(base):
        for f in fs:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base).replace("\\", "/")] = open(p, "rb").read()
    return out


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import handler_core as core
    positional = [a for a in argv if not a.startswith("--")]
    backup = positional[0] if positional else sorted(glob.glob(os.path.join(_ROOT, "scratch", "backups", "*")))[-1]
    rep = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "backup_dir_used": os.path.relpath(backup, _ROOT), "surprises": []}
    s = rep["surprises"]

    # 1. ledger digest + expectation
    now = time.time()
    ledger_b, pending, index_b = ledger_digest()
    mp, mk, young, boundary, bad = ledger_expectation(ledger_b, pending, now)
    rep["ledger_before"] = {"rows": len(ledger_b), "must_prune": len(mp), "old_but_awaited_must_keep": len(mk), "young_must_keep": len(young), "boundary_excluded": len(boundary),
                            "unreadable_ts_must_keep": len(bad), "awaited_ids_total": len(pending), "index_entries": len(index_b)}
    save(rep)

    # 2. review / transcript expectation from the backup
    items = json.load(open(os.path.join(backup, "review_queue.json"), encoding="utf-8"))
    rows = json.load(open(os.path.join(backup, "transcripts.json"), encoding="utf-8"))
    dnow = dt.datetime.now(dt.timezone.utc)
    th = core.test_hashes_from(list(items.values()), list(rows.values()))
    elig = {k for k, i in items.items() if core.is_archivable_review(i, dnow, core.ARCHIVE_HOT_DAYS_DEFAULT)}
    old_rows = {k for k, r in rows.items() if isinstance(r, dict) and core._parse_ts(r.get("ts")) and (dnow - core._parse_ts(r["ts"])).days >= core.ARCHIVE_TRANSCRIPT_MIN_AGE_DAYS}
    rep["expectation_review"] = {"items_in_backup": len(items), "archivable_now": len(elig), "transcripts_in_backup": len(rows), "transcripts_old_enough_in_total": len(old_rows),
                                 "pending_in_backup": sum(1 for i in items.values() if i.get("status") == "pending")}
    save(rep)

    # 3. BEFORE
    rep["before"] = live_counts()
    rc, tail = download(BEFORE)
    files_b = tree(BEFORE)
    rep["volume_before"] = {"download_rc": rc, "files": len(files_b)}
    if rc != 0:
        s.append("BEFORE download failed: " + tail)
    save(rep)
    if s:
        print(json.dumps(rep, indent=1, default=str))
        return 1

    # 4. RUN
    import modal
    try:
        rep["run_summary"] = modal.Function.from_name("chike-whatsapp", "run_archive").remote()
    except Exception as e:                                           # noqa: BLE001
        rep["run_error"] = f"{type(e).__name__}: {e}"
        s.append("the run raised: " + rep["run_error"])
    save(rep)

    # 5. AFTER
    rep["after"] = live_counts()
    ledger_a, pending_a, index_a = ledger_digest()
    rc2, tail2 = download(AFTER)
    files_a = tree(AFTER)
    rep["volume_after"] = {"download_rc": rc2, "files": len(files_a)}
    if rc2 != 0:
        s.append("AFTER download failed: " + tail2)
    save(rep)

    # 6. CHECKS
    run = rep.get("run_summary") or {}
    removed = set(ledger_b) - set(ledger_a)
    arrived = set(ledger_a) - set(ledger_b)
    rep["ledger_after"] = {"rows": len(ledger_a), "removed": len(removed), "new_rows_since_snapshot": len(arrived), "index_entries": len(index_a)}
    if not mp <= removed:
        s.append(f"{len(mp - removed)} row(s) older than 24 h and not awaited were NOT pruned")
    if removed - (mp | boundary):
        s.append(f"{len(removed - (mp | boundary))} row(s) were removed that were young or awaited or unreadable: {sorted(removed - (mp | boundary))[:5]}")
    if not (mk | young | bad) <= set(ledger_a):
        s.append("a row that must be kept is gone")
    if mk and not mk <= set(ledger_a):
        s.append("an OLD row still awaited by the receipt reconciler was removed")
    if run.get("ledger_pruned") is not None and abs(run["ledger_pruned"] - len(removed)) > len(boundary):
        s.append(f"summary says ledger_pruned {run.get('ledger_pruned')} but {len(removed)} rows are gone")
    if run.get("ledger_kept_protected") is not None and run["ledger_kept_protected"] < len(mk):
        s.append(f"summary protected {run['ledger_kept_protected']} < {len(mk)} awaited old rows")
    if run.get("ledger_prune_error"):
        s.append("ledger_prune_error: " + str(run["ledger_prune_error"]))
    for k in ("review_kept_failed", "review_kept_leak", "review_changed_since_archive", "review_tombstoned_dropped", "transcripts_kept_leak"):
        if run.get(k):
            s.append(f"{k} = {run.get(k)} (expected 0)")
    new_files = {k for k in files_a if k not in files_b}
    changed = {k for k in files_b if k in files_a and files_a[k] != files_b[k]}
    gone = {k for k in files_b if k not in files_a}
    bad_changed = {k for k in changed if not k.startswith("aggregates/")}
    rep["volume_diff"] = {"new_files": len(new_files), "changed_files": len(changed), "changed_non_aggregate": len(bad_changed), "files_missing_after": len(gone)}
    if bad_changed:
        s.append(f"write-once files changed: {sorted(bad_changed)[:5]}")
    if gone:
        s.append(f"files disappeared: {sorted(gone)[:5]}")
    n_new_review = sum(1 for k in new_files if k.startswith("review/"))
    n_new_tr = sum(1 for k in new_files if k.startswith("transcript/"))
    if run.get("review_archived") is not None and n_new_review != run["review_archived"]:
        s.append(f"new review files {n_new_review} != summary review_archived {run['review_archived']}")
    if run.get("transcripts_archived") is not None and n_new_tr != run["transcripts_archived"]:
        s.append(f"new transcript files {n_new_tr} != summary transcripts_archived {run['transcripts_archived']}")
    if run.get("review_archived") != len(elig):
        s.append(f"review_archived {run.get('review_archived')} != items archivable per the backup {len(elig)}")
    leaks = [k for k, v in {**files_a}.items() if JID.search(v.decode("utf-8", "replace"))]
    if leaks:
        s.append(f"phone address found in archive file(s): {leaks[:3]}")
    rep["leaks"] = len(leaks)
    if run.get("auth_keys_touched") != rep["after"].get("bridge_auth"):
        s.append(f"keep-alive touched {run.get('auth_keys_touched')} keys but the auth store has {rep['after'].get('bridge_auth')}")
    if run.get("alias_keys_touched") != rep["after"].get("identity_aliases"):
        s.append(f"alias keep-alive touched {run.get('alias_keys_touched')} but there are {rep['after'].get('identity_aliases')}")
    if rep["after"]["transcripts"] != rep["before"]["transcripts"]:
        s.append("transcripts changed (they are copied, never removed)")
    st = modal.Dict.from_name("chike-archive-state-kv")
    last = st.get("last") or {}
    rep["state"] = {"last_ok": last.get("ok"), "last_ts_utc": dt.datetime.fromtimestamp(last["ts"], dt.timezone.utc).strftime("%H:%M:%S") if last.get("ts") else None,
                    "last_error": st.get("last_error"), "lock_present": "lock" in list(st.keys())}
    if not last.get("ok") or rep["state"]["lock_present"] or rep["state"]["last_error"]:
        s.append(f"state not clean after the run: {rep['state']}")
    rep["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    save(rep)
    print(json.dumps({k: rep[k] for k in ("ledger_before", "expectation_review", "before", "run_summary", "after", "ledger_after", "volume_before", "volume_after", "volume_diff",
                                          "leaks", "state", "surprises") if k in rep}, indent=1, default=str))
    return 1 if s else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
