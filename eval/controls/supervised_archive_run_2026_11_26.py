# -*- coding: utf-8 -*-
"""SUPERVISED FIRST RUN of the archiver (2026-11-26), with an independent check of what it did. Run AFTER scripts/backup_dicts_local.py.

    python eval/controls/supervised_archive_run_2026_11_26.py <backup dir>

Steps, each written to eval/results/supervised_archive_run_2026_11_26.json as it completes (a dropped link costs one step, not the report):
  1. EXPECTATION computed offline from the backup (which items are archivable, how many are test by flag+hash, how many real).
  2. BEFORE: live Dict counts.   3. RUN: the deployed `run_archive` once (`.remote()`), so it uses the real image, secrets and Volume mount.
  4. AFTER: live Dict counts.    5. DOWNLOAD the archive Volume to a git-ignored scratch folder and check, FILE BY FILE and independently of the code under test:
     every moved item has its file; each file equals the locally recomputed record (reviewer handles aside); no phone address anywhere; aggregates agree with the
     expectation (test vs real); tombstones none; transcripts copied and still in the Dict; nothing pending moved.
Any mismatch is listed under `surprises`; the exit code is 1 if there is one. It never writes to a Dict or the Volume itself: only the deployed function does.
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
OUT = os.path.join(_ROOT, "eval", "results", "supervised_archive_run_2026_11_26.json")
COPY = os.path.join(_ROOT, "scratch", "archive_copy")
JID = re.compile(r"\d{6,}@[A-Za-z.]+")


def _save(rep):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)


def _strip_handles(rec):
    return {k: v for k, v in rec.items() if not k.endswith("_handle")}


def expectation(backup_dir, now):
    import handler_core as core
    items = json.load(open(os.path.join(backup_dir, "review_queue.json"), encoding="utf-8"))
    rows = json.load(open(os.path.join(backup_dir, "transcripts.json"), encoding="utf-8"))
    th = core.test_hashes_from(list(items.values()), list(rows.values()))
    elig = {k: i for k, i in items.items() if core.is_archivable_review(i, now, core.ARCHIVE_HOT_DAYS_DEFAULT)}
    test = {k for k, i in elig.items() if core._is_test_item(i, th)}
    old_rows = [k for k, r in rows.items() if isinstance(r, dict) and core._parse_ts(r.get("ts")) and (now - core._parse_ts(r["ts"])).days >= core.ARCHIVE_TRANSCRIPT_MIN_AGE_DAYS]
    return {"items_before": len(items), "transcripts_before": len(rows), "archivable_ids": sorted(elig), "expected_moved": len(elig), "expected_test": len(test),
            "expected_real": len(elig) - len(test), "expected_review_after": len(items) - len(elig), "expected_transcripts_archived": len(old_rows),
            "pending_in_backup": sum(1 for i in items.values() if i.get("status") == "pending")}, items, th


def live_counts():
    import modal
    out = {}
    for label, name in (("review_queue", "chike-review-queue-kv"), ("transcripts", "chike-transcripts-kv"), ("autosend_claims", "chike-autosend-kv"),
                        ("disclosures", "chike-disclosures-kv"), ("identity_aliases", "chike-identity-aliases-kv"), ("archive_state", "chike-archive-state-kv")):
        try:
            out[label] = len(list(modal.Dict.from_name(name).keys()))
        except modal.exception.NotFoundError:
            out[label] = None
    return out


def check_volume(exp, items, th, surprises):
    import handler_core as core
    base = os.path.join(COPY, "archive")
    got = {"review_files": 0, "transcript_files": 0, "aggregate_files": 0, "tombstones": 0, "leaks": 0, "mismatched": 0, "missing": 0}
    if not os.path.isdir(base):
        surprises.append("the archive folder was not downloaded / does not exist")
        return got
    for kind in ("review", "transcript"):
        for dp, _, fs in os.walk(os.path.join(base, kind)):
            for f in fs:
                got[f"{kind}_files"] += 1
    got["aggregate_files"] = len(glob.glob(os.path.join(base, "aggregates", "*.json")))
    got["tombstones"] = len(glob.glob(os.path.join(base, "tombstones", "*.json")))
    for dp, _, fs in os.walk(base):
        for f in fs:
            if JID.search(open(os.path.join(dp, f), "rb").read().decode("utf-8", "replace")):
                got["leaks"] += 1
    for rid in exp["archivable_ids"]:
        item = items[rid]
        rel = core.archive_relpath("review", item.get("sender_hash"), rid)
        path = os.path.join(COPY, rel.replace("/", os.sep))
        if not os.path.exists(path):
            got["missing"] += 1
            continue
        archived = json.load(open(path, encoding="utf-8"))
        want = json.loads(json.dumps(item, default=str))
        for k in ("sender", "sender_lid", "claimed_by", "released_from", "decided_by"):
            want.pop(k, None)
        want["_archive"] = {"schema": 1, "kind": "review"}
        if _strip_handles(archived) != _strip_handles(want):
            got["mismatched"] += 1
    # aggregates: totals by test vs real, from the files themselves
    tot_real, tot_test = 0, 0
    for p in glob.glob(os.path.join(base, "aggregates", "*.json")):
        ag = json.load(open(p, encoding="utf-8"))
        tot_test += int(ag.get("excluded_test") or 0)
        tot_real += sum(v for c in ag.get("routes", {}).values() for k, v in c.items() if k != "pending")
    got["aggregate_real_counted"], got["aggregate_test_counted"] = tot_real, tot_test
    if got["review_files"] != exp["expected_moved"]:
        surprises.append(f"review files {got['review_files']} != expected moved {exp['expected_moved']}")
    if got["transcript_files"] != exp["expected_transcripts_archived"]:
        surprises.append(f"transcript files {got['transcript_files']} != expected {exp['expected_transcripts_archived']}")
    for k in ("leaks", "mismatched", "missing", "tombstones"):
        if got[k]:
            surprises.append(f"{k}: {got[k]} (expected 0)")
    if (tot_real, tot_test) != (exp["expected_real"], exp["expected_test"]):
        surprises.append(f"aggregates count real/test {tot_real}/{tot_test} != expected {exp['expected_real']}/{exp['expected_test']}")
    return got


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    positional = [a for a in argv if not a.startswith("--")]
    backup = positional[0] if positional else sorted(glob.glob(os.path.join(_ROOT, "scratch", "backups", "*")))[-1]
    now = dt.datetime.now(dt.timezone.utc)
    rep = {"started_utc": now.isoformat(timespec="seconds"), "backup_dir_used": os.path.relpath(backup, _ROOT), "surprises": []}
    exp, items, th = expectation(backup, now)
    verify_only = "--verify-only" in argv                 # the archiver already ran: re-do ONLY the download + independent check, from the saved report
    if verify_only:
        rep = json.load(open(OUT, encoding="utf-8"))
        rep["surprises"] = []
        rep["verify_only_rerun_utc"] = now.isoformat(timespec="seconds")
    rep["expectation"] = {k: v for k, v in exp.items() if k != "archivable_ids"}
    _save(rep)
    if not verify_only:
        rep["before"] = live_counts()
        _save(rep)
    if not verify_only and (rep["before"]["review_queue"] != exp["items_before"] or rep["before"]["transcripts"] != exp["transcripts_before"]):
        rep["surprises"].append(f"live counts changed since the backup: {rep['before']} vs backup {exp['items_before']}/{exp['transcripts_before']}: NOT RUNNING")
        _save(rep)
        print(json.dumps(rep, indent=1, default=str))
        return 1
    import modal
    if not verify_only:
        try:
            rep["run_summary"] = modal.Function.from_name("chike-whatsapp", "run_archive").remote()
        except Exception as e:                                       # noqa: BLE001
            rep["run_error"] = f"{type(e).__name__}: {e}"
            rep["surprises"].append("the run raised: " + rep["run_error"])
        _save(rep)
        rep["after"] = live_counts()
        _save(rep)
    # the download target must exist (the CLI refuses a missing one), and a failed download must be LOUD, never an empty folder read as a result
    import shutil
    shutil.rmtree(COPY, ignore_errors=True)
    os.makedirs(COPY, exist_ok=True)
    dl = subprocess.run([sys.executable, "-m", "modal", "volume", "get", "--force", "chike-archive", "archive", COPY], cwd=_ROOT, capture_output=True, timeout=900,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    rep["download_returncode"] = dl.returncode
    if dl.returncode != 0:
        rep["surprises"].append("volume download failed: " + (dl.stdout + dl.stderr).decode("utf-8", "replace")[-200:])
    rep["volume"] = check_volume(exp, items, th, rep["surprises"])
    s = rep.get("run_summary") or {}
    if s.get("review_removed") != exp["expected_moved"] or s.get("review_archived") != exp["expected_moved"]:
        rep["surprises"].append(f"function summary moved/archived {s.get('review_removed')}/{s.get('review_archived')} != expected {exp['expected_moved']}")
    for k in ("review_kept_failed", "review_kept_leak", "review_changed_since_archive", "review_tombstoned_dropped"):
        if s.get(k):
            rep["surprises"].append(f"{k} = {s.get(k)} (expected 0)")
    if rep["after"]["review_queue"] != exp["expected_review_after"]:
        rep["surprises"].append(f"review queue after {rep['after']['review_queue']} != expected {exp['expected_review_after']}")
    if rep["after"]["transcripts"] != exp["transcripts_before"]:
        rep["surprises"].append("transcripts changed (they are copied, never removed)")
    rep["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    _save(rep)
    print(json.dumps({k: rep[k] for k in ("expectation", "before", "run_summary", "after", "volume", "surprises") if k in rep}, indent=1, default=str))
    return 1 if rep["surprises"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
