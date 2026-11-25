# -*- coding: utf-8 -*-
"""Print the answer-path split of real inbound messages (2026-11-25, founder). Reads the transcript store (modal.Dict chike-transcripts-kv)
or a JSON file of rows (--file). Text-free: it prints counts only.   python scripts/answer_path_summary.py [--file rows.json] [--include-test]"""
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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
