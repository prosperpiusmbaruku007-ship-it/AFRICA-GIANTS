# -*- coding: utf-8 -*-
"""Print the answer-path split of real inbound messages (2026-11-25, founder). Reads the transcript store (modal.Dict chike-transcripts-kv)
or a JSON file of rows (--file). Text-free: it prints counts only.   python scripts/answer_path_summary.py [--file rows.json] [--include-test]

ALSO PRINTS (item D, 2026-11-26) the PER-ROUTE REVIEW REPORT: for each route, how many drafts a reviewer approved unchanged / edited / withheld, plus
auto-sent and pending, from the hot review items AND the archived per-day aggregates (decided items older than 3 days live only in the archive).
Offline: --reviews items.json [--archive-dir <local copy of archive/aggregates>]. Measurement only: nothing here changes what auto-sends."""
import importlib.util
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _core():
    spec = importlib.util.spec_from_file_location("hc_summary", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def render(s):
    lines = [f"answer paths: {s['n']} messages ({s['excluded_test']} test excluded, {s['untraced']} untraced)"]
    for k, v in sorted(s["by_class"].items(), key=lambda kv: -kv[1]):
        lines.append(f"  {k:<16}{v:>5}  {100 * v / max(1, s['n'] - s['untraced']):5.1f}%")
    lines.append("routes: " + (", ".join(f"{k}={v}" for k, v in sorted(s["by_route"].items(), key=lambda kv: -kv[1])) or "-"))
    lines.append(f"model-free {s['model_free']} | model called {s['model_called']} | calls unknown {s['model_calls_unknown']} | guard fired {s['guard_fired']}")
    return "\n".join(lines)


def render_routes(rep):
    lines = [f"review outcomes per route: {rep['hot_items']} hot items + {rep['archived_days']} archived day(s), {rep['excluded_test']} test excluded"]
    lines.append(f"  {'route':<26}{'reviewed':>9}{'unchanged':>10}{'edited':>8}{'withheld':>9}{'auto':>6}{'pending':>8}  unchanged-rate")
    for ro, c in sorted(rep["routes"].items(), key=lambda kv: -kv[1]["reviewed"]):
        rate = "n/a (nothing reviewed)" if c["unchanged_rate"] is None else f"{100 * c['unchanged_rate']:.1f}%"
        lines.append(f"  {ro:<26}{c['reviewed']:>9}{c['approved_unchanged']:>10}{c['edited']:>8}{c['withheld']:>9}{c['auto_sent']:>6}{c['pending']:>8}  {rate}")
    if not rep["routes"]:
        lines.append("  (no review items)")
    return "\n".join(lines)


def _volume_aggregates():
    """([aggregates], note). A volume that cannot be read is REPORTED, never silently read as 'no history'."""
    import modal
    vol = modal.Volume.from_name("chike-archive")
    try:
        entries = list(vol.listdir("archive/aggregates"))
    except Exception as e:                                           # noqa: BLE001
        return [], f"archive aggregates not read ({type(e).__name__}): history before the hot window is NOT included"
    out = []
    for e in entries:
        try:
            out.append(json.loads(b"".join(vol.read_file(e.path)).decode("utf-8")))
        except Exception:                                            # noqa: BLE001
            return out, f"archive aggregate {os.path.basename(e.path)} unreadable: history may be incomplete"
    return out, None


def _dir_aggregates(path):
    out = []
    for name in sorted(os.listdir(path)):
        if name.endswith(".json"):
            out.append(json.load(open(os.path.join(path, name), encoding="utf-8")))
    return out


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # in main(), never at import (R40)
    core = _core()
    if "--file" in argv:
        rows = json.load(open(argv[argv.index("--file") + 1], encoding="utf-8"))
    else:
        import modal
        d = modal.Dict.from_name("chike-transcripts-kv")
        rows = [v for _, v in d.items() if isinstance(v, dict) and v.get("kind") == "question"]
    print(render(core.summarize_answer_paths(rows, include_test="--include-test" in argv)))
    reviews, aggs, note = None, [], None
    if "--file" not in argv:
        q = modal.Dict.from_name("chike-review-queue-kv")
        reviews = [v for _, v in q.items() if isinstance(v, dict)]
        h = core.count_holding_sent(reviews, include_test="--include-test" in argv)
        print(f"holding messages sent (a separate event, not an answer path): {h['holding_sent']} ({h['holding_failed']} failed, {h['excluded_test']} test excluded)")
        aggs, note = _volume_aggregates()
    elif "--reviews" in argv:
        reviews = json.load(open(argv[argv.index("--reviews") + 1], encoding="utf-8"))
        if "--archive-dir" in argv:
            aggs = _dir_aggregates(argv[argv.index("--archive-dir") + 1])
    if reviews is None:
        print("per-route review report skipped: give --reviews items.json (offline) or run without --file (live)")
        return 0
    th = core.test_hashes_from(reviews, rows)          # a hash seen on ANY flagged record classifies all of that sender's older, unflagged ones
    print(render_routes(core.route_report(reviews, aggs, include_test="--include-test" in argv, test_hashes=th)))
    if note:
        print("  NOTE: " + note)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
