# -*- coding: utf-8 -*-
"""READ-ONLY local backup of the hot Dicts (and the archive aggregates) to a folder on THIS machine, taken before a supervised archiver run.

    python scripts/backup_dicts_local.py            # writes scratch/backups/<UTC timestamp>/

NEVER committed, NEVER uploaded: the destination must be git-ignored (checked with `git check-ignore`; otherwise the script refuses), nothing here makes a
network call except Modal reads, and it reads only: no put / pop / clear / create_if_missing. The files hold personal data (sender addresses, question text)
and credentials-adjacent records are refused by name: **the bridge auth store (the WhatsApp login) is NOT backed up**. The archiver only READS it (a keep-alive
touch), so there is nothing to restore, and a copy of a login's keys on a laptop is a risk with no benefit.

Writes one JSON file per store, a manifest (counts + sha256 + UTC time), then READS EVERY FILE BACK and checks the counts and hashes against what it wrote.
"""
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# every store the archiver reads or changes, plus the ones the founder asked for
DICTS = {
    "review_queue": "chike-review-queue-kv",
    "transcripts": "chike-transcripts-kv",
    "disclosures": "chike-disclosures-kv",
    "autosend_claims": "chike-autosend-kv",
    "archive_state": "chike-archive-state-kv",
    "identity_aliases": "chike-identity-aliases-kv",
}
REFUSED_NAME_PARTS = ("auth", "secret", "token", "signing", "credential")


class BackupRefused(Exception):
    pass


def refuse_sensitive(dict_name):
    low = str(dict_name).lower()
    if any(p in low for p in REFUSED_NAME_PARTS):
        raise BackupRefused(f"refusing to back up {dict_name!r}: credentials-adjacent, and not needed (the archiver only reads it)")


def is_git_ignored(path):
    """True when git says `path` is ignored. Anything else (including git being unavailable) is NOT a pass."""
    try:
        r = subprocess.run(["git", "check-ignore", "-q", path], cwd=_ROOT, capture_output=True, timeout=30)
        return r.returncode == 0
    except Exception:                                                # noqa: BLE001
        return False


def _json_bytes(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1, default=str).encode("utf-8")


def write_backup(stores, out_dir, ignored_check=is_git_ignored, now=None):
    """`stores` = {label: (dict_name, [(key, value), ...] or None if the store does not exist)}. Returns the manifest. Raises BackupRefused or AssertionError."""
    for label, (dict_name, _) in stores.items():
        refuse_sensitive(dict_name)
    if not ignored_check(out_dir):
        raise BackupRefused(f"{out_dir!r} is not git-ignored: a backup of personal data must never be committable")
    os.makedirs(out_dir, exist_ok=True)
    manifest = {"taken_at_utc": (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"), "stores": {}}
    for label, (dict_name, items) in stores.items():
        entry = {"dict": dict_name, "exists": items is not None, "count": 0 if items is None else len(items), "file": None, "sha256": None}
        if items is not None:
            data = _json_bytes({str(k): v for k, v in items})
            name = f"{label}.json"
            with open(os.path.join(out_dir, name), "wb") as f:
                f.write(data)
            entry["file"], entry["sha256"] = name, hashlib.sha256(data).hexdigest()
        manifest["stores"][label] = entry
    with open(os.path.join(out_dir, "manifest.json"), "wb") as f:
        f.write(_json_bytes(manifest))
    verify_backup(out_dir)
    return manifest


def verify_backup(out_dir):
    """Read every file back: hash and entry count must equal the manifest. Raises AssertionError naming the store that does not."""
    manifest = json.load(open(os.path.join(out_dir, "manifest.json"), encoding="utf-8"))
    for label, e in manifest["stores"].items():
        if not e["exists"]:
            continue
        raw = open(os.path.join(out_dir, e["file"]), "rb").read()
        assert hashlib.sha256(raw).hexdigest() == e["sha256"], f"{label}: file hash differs from the manifest"
        assert len(json.loads(raw.decode("utf-8"))) == e["count"], f"{label}: entry count differs from the manifest"
    return True


def _read_dict(dict_name):
    import modal
    try:
        d = modal.Dict.from_name(dict_name)                          # never create_if_missing
        return [(k, v) for k, v in d.items()]
    except modal.exception.NotFoundError:
        return None


def _read_aggregates():
    """[(file name, parsed json)] from the archive Volume, or None when the Volume path does not exist yet."""
    import modal
    try:
        vol = modal.Volume.from_name("chike-archive")
        entries = list(vol.listdir("archive/aggregates"))
    except Exception:                                                # noqa: BLE001
        return None
    return [(os.path.basename(e.path), json.loads(b"".join(vol.read_file(e.path)).decode("utf-8"))) for e in entries]


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # in main(), never at import (R40)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(_ROOT, "scratch", "backups", stamp)
    stores = {label: (name, _read_dict(name)) for label, name in DICTS.items()}
    stores["archive_aggregates"] = ("volume:chike-archive/archive/aggregates", _read_aggregates())
    manifest = write_backup(stores, out_dir)
    print(f"backup written and verified (read back): {os.path.relpath(out_dir, _ROOT)}")
    for label, e in manifest["stores"].items():
        print(f"  {label:<20}{e['count']:>6} entries" + ("" if e["exists"] else "   (store does not exist yet)"))
    print("NOT backed up by design: the bridge auth store (WhatsApp login). Nothing was uploaded or committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
