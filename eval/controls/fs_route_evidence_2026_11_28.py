# -*- coding: utf-8 -*-
"""FIXED-STATEMENT ROUTES: what each one routes, over every question string in the repo corpora (founder, 2026-11-28). Read-only. Run from the repo root.

"own" = the row's source FILE NAME carries a word of the topic (a probe authored for that route); "foreign" = every other row it routes. FOREIGN IS A CEILING ON MISROUTES, NOT A COUNT OF THEM:
most foreign rows are training paraphrases of the same topic that sit in a file not named after it. The only population with an authoritative key is the 400-question gate, so those rows are listed
for HAND reading (see PROGRESS). `topics with ZERO routed rows` is printed so a route no corpus exercises is visible (R20/R39)."""
import glob
import json
import os
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.getcwd())
from chike import routing

QKEYS = ("question", "question_sw", "q", "instruction", "prompt")
rows = []          # (topic, src, question)
seen = set()
files = [p for p in glob.glob("eval/**/*.jsonl", recursive=True)] + glob.glob("datasets/tier1a/**/*.jsonl", recursive=True)
n_q = 0
for p in files:
    try:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            q = next((d[k] for k in QKEYS if isinstance(d.get(k), str) and d[k].strip()), None)
            if not q:
                continue
            n_q += 1
            key = (q, p)
            if key in seen:
                continue
            seen.add(key)
            t = routing.fixed_statement_topic(q)
            if t:
                rows.append((t, p.replace("\\", "/"), q))
    except Exception as e:
        print("skip", p, type(e).__name__)
print("question strings scanned:", n_q, "| distinct (question,file):", len(seen), "| routed to a fixed statement:", len(rows))

GATE = re.compile(r"eval/accuracy_gate/(eval_questions|gate_)|accuracy_gate/eval_questions")
by = collections.defaultdict(list)
for t, p, q in rows:
    by[t].append((p, q))


def topic_words(t):
    return [w for w in re.split(r"[_]", t) if len(w) > 2]


out = {}
for t, lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    # a row is "own" when its source file name carries a word of the topic name; the rest are FOREIGN
    own = [x for x in lst if any(w in os.path.basename(x[0]).lower() for w in topic_words(t))]
    foreign = [x for x in lst if x not in own]
    gate = [x for x in foreign if GATE.search(x[0])]
    out[t] = {"routed_total": len(lst), "own_probe_rows": len(own), "foreign_rows": len(foreign), "foreign_in_gate_400": len(gate),
              "foreign_examples": [{"src": os.path.basename(p), "q": q[:150]} for p, q in foreign[:6]]}
json.dump(out, open("eval/results/fs_route_evidence_2026_11_28.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{'topic':36s} total own foreign gate400")
for t, v in out.items():
    print(f"{t:36s} {v['routed_total']:5d} {v['own_probe_rows']:4d} {v['foreign_rows']:6d} {v['foreign_in_gate_400']:6d}")
print("topics in table:", len(routing._FS_TOPICS) + 1, "| topics with ZERO routed rows anywhere:", [n for n, *_ in routing._FS_TOPICS if n not in out])
