# -*- coding: utf-8 -*-
"""R22/R25 pricing of D-FIDELITY-24 (another sector's minimum wage stated as a MINING rate): run the guard over every stored reply, gold answer and training answer we hold and list every flag, so each can be read.
    python eval/controls/price_d24_2026_11_22.py  ->  eval/results/price_d24_2026_11_22.json"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from chike import fidelity  # noqa: E402
from price_d23_2026_11_18 import pairs  # noqa: E402


def main():
    n, flags, mining_figs = 0, [], 0
    for src, q, a in pairs():
        n += 1
        if fidelity._D24_SUBJECT.search(a) and any(int(m.group(1).replace(",", "")) in (333500, 397600, 595000, 695000) for m in fidelity._D24_FIGURE.finditer(a)):
            mining_figs += 1
        for s in fidelity.mining_wage_misattributed(q, a):
            flags.append({"src": src, "q": q[:200], "sentence": s[:300]})
    print(f"{n} texts priced; {mining_figs} state one of the four mining rates near a mining word (must NOT flag); {len(flags)} flagged")
    for f in flags:
        print(f"  [{f['src']}] Q: {f['q'][:110]}\n       -> {f['sentence'][:220]}")
    json.dump({"priced": n, "state_a_mining_rate": mining_figs, "flags": flags}, io.open(os.path.join(REPO, "eval", "results", "price_d24_2026_11_22.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
