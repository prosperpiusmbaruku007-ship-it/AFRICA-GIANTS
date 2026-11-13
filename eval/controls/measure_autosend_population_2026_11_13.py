import sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
from chike.orchestrator import Orchestrator
from chike import answer_trace
d = json.load(open("eval/results/gate_production_0e11c3d.json", encoding="utf-8"))
rows = d.get("rows") or d.get("results") or d
if isinstance(rows, dict): rows = list(rows.values())
qs = [r.get("question") or r.get("question_sw") for r in rows if isinstance(r, dict)]
qs = [q for q in qs if q]
class B:
    def generate(self, prompt, params=None): return "JIBU LA MFANO: ni sawa."
orch = Orchestrator(B(), retriever=lambda q: ["Ukweli wa mfano."], ooc_phrases=[], in_scope_phrases=[])
tally = collections.Counter(); ex = collections.defaultdict(list)
for q in qs:
    try:
        r = orch.answer(q); t = answer_trace.trace(r)
    except Exception as e:
        tally["error"] += 1; continue
    parts = t["path"].split("+")
    eng = all(p.startswith("engine:") and not p.endswith(":ask") for p in parts) and bool(t["working"])
    key = ("engine_literal_rule" if eng else "other")
    free = (t["model_calls"] == 0)
    tally[(key, "model_free" if free else "has_model_calls")] += 1
    if eng and not free and len(ex["lit"]) < 3: ex["lit"].append(q[:90])
print(len(qs), "questions")
for k, v in sorted(tally.items(), key=str): print(k, v)
print("engine-literal but model involved, examples:", ex["lit"])
out = {"harness": "eval/controls/measure_autosend_population_2026_11_13.py", "population": "the 400 gate questions (eval/results/gate_production_0e11c3d.json)",
       "backend": "stub (every generate() returns a fixed string; retrieval stubbed) -- measures WHICH ROUTES CALL THE MODEL, not answer quality",
       "n": len(qs), "counts": {"|".join(k) if isinstance(k, tuple) else k: v for k, v in tally.items()},
       "literal_rule": "path all engine:* (no :ask), working present",
       "examples_literal_rule_but_model_wrote_a_sentence": ex["lit"]}
json.dump(out, open("eval/results/autosend_population_2026_11_13.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
