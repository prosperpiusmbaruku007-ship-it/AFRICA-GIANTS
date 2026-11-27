# -*- coding: utf-8 -*-
"""QUESTION-TO-ANSWER LEGS, from stored rows (founder, 2026-11-28, Step 1). Read-only; AGGREGATES ONLY are written (no sender, no text).

    python eval/controls/measure_latency_legs_2026_11_28.py <archive copy dir> <backup dir>

`<archive copy dir>` is a local download of the archive Volume (`.../archive`), `<backup dir>` a scripts/backup_dicts_local.py backup. Both stay on this machine (scratch/, gitignored).
Test senders are INCLUDED on purpose (include_test=True): every participant so far is a test or founder number and TEST-CLASSIFY-CONFIGURED-1 is still queued, so excluding them would report nothing.
Two things are reported separately because they answer different questions: the legs of ANSWERED questions (handler_core.latency_report) and the hold+notify gap of ALL held questions BY DATE AND BUILD,
because a pooled figure mixes eras (the 2026-11-25 bridge send pacing moved that gap from ~2 s to 10-34 s, and a pooled p50 of 18.7 s described neither era)."""
import collections
import glob
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
OUT = os.path.join(_ROOT, "eval", "results", "latency_legs_2026_11_28.json")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import handler_core as core
    arch, bk = argv[0], argv[1]
    items, rows = {}, {}
    for p in glob.glob(os.path.join(arch, "review", "*", "*.json")):
        d = json.load(open(p, encoding="utf-8")); items[d["review_id"]] = d
    for k, d in json.load(open(os.path.join(bk, "review_queue.json"), encoding="utf-8")).items():
        items.setdefault(d.get("review_id", k), d)
    for p in glob.glob(os.path.join(arch, "transcript", "*", "*.json")):
        d = json.load(open(p, encoding="utf-8")); rows[(d["sender_hash"], d["ts"], d["kind"])] = d
    for k, d in json.load(open(os.path.join(bk, "transcripts.json"), encoding="utf-8")).items():
        rows.setdefault((d["sender_hash"], d["ts"], d["kind"]), d)
    rep = core.latency_report(list(items.values()), list(rows.values()), include_test=True)
    by = collections.defaultdict(list)
    for (h, t, k), d in rows.items():
        if k == "question" and d.get("supervision") == "held" and d.get("total_latency_ms") is not None and d.get("model_latency_ms") is not None:
            by[f"{t[:10]} build {str(d.get('build', '?'))[:7]}"].append(round((d["total_latency_ms"] - d["model_latency_ms"]) / 1000, 1))
    gap = {k: {"n": len(v), "p50": core._percentile(v, 0.5), "min": min(v), "max": max(v)} for k, v in sorted(by.items())}
    allq = [d for (h, t, k), d in rows.items() if k == "question"]
    out = {"items_read": len(items), "transcript_rows_read": len(rows), "population": "all stored senders incl. test (see docstring)", "latency_report": rep,
           "hold_notify_gap_by_date_and_build": gap,
           "question_rows": {"n": len(allq), "cold_flagged": sum(1 for d in allq if d.get("cold_start_suspected")),
                             "model_s": {"p50": core._percentile([d["model_latency_ms"] / 1000 for d in allq if d.get("model_latency_ms") is not None], .5),
                                         "p90": core._percentile([d["model_latency_ms"] / 1000 for d in allq if d.get("model_latency_ms") is not None], .9)}}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:3500])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
