# -*- coding: utf-8 -*-
"""READ-ONLY residue check for a FUTA end-to-end test with a throwaway number. Prints COUNTS only: no number, no hash, no text.

    python scripts/futa_check.py --baseline            # BEFORE the test: whole-system totals, NO digits needed (the throwaway number has no records yet)
    python scripts/futa_check.py --last4 1234          # the last four digits of the throwaway number (you supply them; they are not stored anywhere)

It finds a person's records WITHOUT the salt, by the 4-digit tail every transcript row, review item and archive record carries, so it is a second opinion
independent of the hash-based scan the live deletion runs inside Modal. Run it BEFORE (to see what the test created) and AFTER (to see it gone), and compare
the other-people totals, which must not change. The bridge delivery ledger is deliberately not read (about 3,500 rows, one read each) and is a documented
accepted limit (runbook 6a). Nothing here writes, creates or deletes.
"""
import json
import os
import sys


def summarize(last4, transcripts, review_items, archive_tails, tombstones, futa_logs):
    """Pure. `archive_tails` is {'review': [tail, ...], 'transcript': [tail, ...]} (one entry per archived record); `futa_logs` the logged deletion records."""
    mine = lambda r: isinstance(r, dict) and str(r.get("sender_tail") or "") == str(last4)         # noqa: E731
    out = {
        "transcripts_total": len(transcripts), "transcripts_mine": sum(1 for r in transcripts if mine(r)),
        "review_total": len(review_items), "review_mine": sum(1 for r in review_items if mine(r)),
        "archive_review_mine": sum(1 for t in archive_tails.get("review", ()) if str(t) == str(last4)),
        "archive_transcript_mine": sum(1 for t in archive_tails.get("transcript", ()) if str(t) == str(last4)),
        "archive_review_total": len(archive_tails.get("review", ())), "archive_transcript_total": len(archive_tails.get("transcript", ())),
        "tombstones": tombstones,
    }
    out["others_total"] = (out["transcripts_total"] - out["transcripts_mine"]) + (out["review_total"] - out["review_mine"]) + \
                          (out["archive_review_total"] - out["archive_review_mine"]) + (out["archive_transcript_total"] - out["archive_transcript_mine"])
    out["residue_total"] = out["transcripts_mine"] + out["review_mine"] + out["archive_review_mine"] + out["archive_transcript_mine"]
    last = sorted(futa_logs, key=lambda r: r.get("ts") or 0)[-1] if futa_logs else None
    out["last_deletion"] = None if not last else {"verified": last.get("verified"), "residue_stores": last.get("residue_stores"),
                                                   "archive_removed_dirs": last.get("archive_removed_dirs"), "counts": last.get("counts")}
    return out


def render(s):
    lines = [
        f"records of the number (by last-4 tail): transcripts {s['transcripts_mine']}/{s['transcripts_total']}, review items {s['review_mine']}/{s['review_total']}, "
        f"archive review {s['archive_review_mine']}/{s['archive_review_total']}, archive transcripts {s['archive_transcript_mine']}/{s['archive_transcript_total']}",
        f"RESIDUE TOTAL: {s['residue_total']}   |   everyone else's records (must not change across the test): {s['others_total']}   |   tombstones: {s['tombstones']}",
    ]
    ld = s["last_deletion"]
    lines.append("last logged deletion: " + ("none" if not ld else f"verified={ld['verified']} residue_stores={ld['residue_stores']} archive_dirs_removed={ld['archive_removed_dirs']} counts={ld['counts']}"))
    lines.append("not read: the bridge delivery ledger (accepted limit, rows age out within 24 h)")
    return "\n".join(lines)


def render_baseline(s):
    """The totals the later checks are compared against. No number, no tail: nothing here can identify anyone."""
    everyone = s["transcripts_total"] + s["review_total"] + s["archive_review_total"] + s["archive_transcript_total"]
    ld = s["last_deletion"]
    return "\n".join([
        f"BASELINE (whole system, no number): transcripts {s['transcripts_total']}, review items {s['review_total']}, archive review {s['archive_review_total']}, "
        f"archive transcripts {s['archive_transcript_total']}, tombstones {s['tombstones']}",
        f"TOTAL RECORDS (everyone): {everyone}   <- after the test, 'everyone else's records' must equal this number exactly",
        "last logged deletion: " + ("none" if not ld else f"verified={ld['verified']}"),
        "not read: the bridge delivery ledger (accepted limit, rows age out within 24 h)"])


def _volume_read():
    """({'review': [tails], 'transcript': [tails]}, tombstone_count). A Volume or path that does not exist yet reads as empty, and says so."""
    import modal
    vol = modal.Volume.from_name("chike-archive")
    tails, tomb = {"review": [], "transcript": []}, 0
    try:
        tomb = len(list(vol.listdir("archive/tombstones")))
    except Exception:                                                # noqa: BLE001
        print("archive/tombstones: not present yet (treated as 0)", file=sys.stderr)
    for kind in ("review", "transcript"):
        try:
            owners = list(vol.listdir(f"archive/{kind}"))
        except Exception:                                            # noqa: BLE001
            print(f"archive/{kind}: not present yet (treated as empty)", file=sys.stderr)
            continue
        for o in owners:
            for f in vol.listdir(o.path):
                try:
                    rec = json.loads(b"".join(vol.read_file(f.path)).decode("utf-8"))
                    tails[kind].append(str(rec.get("sender_tail") or ""))
                except Exception:                                    # noqa: BLE001
                    tails[kind].append("")
    return tails, tomb


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # in main(), never at import (R40)
    baseline = "--baseline" in argv
    if not baseline and ("--last4" not in argv or not argv[argv.index("--last4") + 1].isdigit() or len(argv[argv.index("--last4") + 1]) != 4):
        print("give --last4 NNNN (the last four digits of the throwaway number), or --baseline for the totals before the test")
        return 2
    last4 = None if baseline else argv[argv.index("--last4") + 1]
    import modal
    rows = [v for _, v in modal.Dict.from_name("chike-transcripts-kv").items() if isinstance(v, dict)]
    items = [v for _, v in modal.Dict.from_name("chike-review-queue-kv").items() if isinstance(v, dict)]
    try:
        logs = [v for k, v in modal.Dict.from_name("chike-archive-state-kv").items() if str(k).startswith("futa:") and isinstance(v, dict)]
    except Exception:                                                # noqa: BLE001
        logs = []
    tails, tomb = _volume_read()
    summary = summarize(last4, rows, items, tails, tomb, logs)
    print(render_baseline(summary) if baseline else render(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
