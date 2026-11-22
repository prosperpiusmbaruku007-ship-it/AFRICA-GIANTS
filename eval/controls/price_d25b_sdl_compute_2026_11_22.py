# -*- coding: utf-8 -*-
"""PRICING of D-FIDELITY-25b over every stored reply to an SDL-routed question: each stored `generated` body is replayed through the REAL orchestrator as the model's output, so the engine boolean is the engine's own. READ every flag.
Population named (R22): replies where body and engine verdict could disagree (SDL-routed), not the ones that agree by construction.
    python eval/controls/price_d25b_sdl_compute_2026_11_22.py  ->  eval/results/price_d25b_sdl_compute_2026_11_22.json"""
import glob, io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
from chike import fidelity, routing  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402

class B:
    def __init__(self, r): self.r = r
    def generate(self, p, params=None): return self.r

def main():
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "results", "gate_production_*.json"))):
        try:
            for r in json.load(io.open(f, encoding="utf-8")).get("rows", []):
                q, g = r.get("question_sw"), r.get("generated")
                if isinstance(q, str) and isinstance(g, str) and (q, g) not in seen and routing.detect_intent(q) == "sdl":
                    seen.add((q, g)); rows.append((os.path.basename(f) + ":" + str(r.get("id")), q, g))
        except Exception:                                                # noqa: BLE001
            continue
    flagged = []
    real = fidelity.sdl_body_contradicts_verdict
    for tag, q, g in rows:
        hits = []
        fidelity.sdl_body_contradicts_verdict = lambda qq, b, c, _h=hits: (_h.extend(real(qq, b, c)) or _h[:])
        try:
            Orchestrator(B(g), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q)
        except Exception as e:                                           # noqa: BLE001
            hits.append("ERR " + repr(e)[:80])
        finally:
            fidelity.sdl_body_contradicts_verdict = real
        if hits:
            flagged.append({"src": tag, "q": q, "body": g[:300], "flagged": hits})
    print(f"{len(rows)} SDL-routed stored replies replayed; {len(flagged)} flagged")
    for h in flagged:
        print(" ", h["src"], "|", h["q"][:90], "|", h["flagged"])
    io.open(os.path.join(REPO, "eval", "results", "price_d25b_sdl_compute_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps({"replayed": len(rows), "flagged": flagged}, ensure_ascii=False, indent=1))

main()
