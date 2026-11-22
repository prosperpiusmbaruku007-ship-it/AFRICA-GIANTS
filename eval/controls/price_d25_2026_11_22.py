# -*- coding: utf-8 -*-
"""R22/R25 pricing of D-FIDELITY-25 ("SDL not payable" told to an employer whose OWN stated headcount is 10 or more): the guard over every stored reply, gold answer and training answer we hold, every flag listed to be READ, plus the
POPULATION it could ever act on (questions that name SDL and state one headcount >= 10 with no exempt category), so the flag count is read against its denominator.
    python eval/controls/price_d25_2026_11_22.py  ->  eval/results/price_d25_2026_11_22.json"""
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
from chike.swahili_numbers import sole_headcount  # noqa: E402
from price_d23_2026_11_18 import pairs  # noqa: E402


def main():
    n, pop, denies_in_pop, flags = 0, 0, 0, []
    for src, q, a in pairs():
        n += 1
        in_pop = bool(fidelity._D25_Q_SDL.search(q)) and not fidelity._D25_EXEMPT.search(q) and (sole_headcount(q) or 0) >= 10
        if in_pop:
            pop += 1
            if fidelity._D25_DENY.search(a):
                denies_in_pop += 1
        for s in fidelity.sdl_denied_above_threshold(q, a):
            flags.append({"src": src, "q": q[:220], "sentence": s[:300]})
    print(f"{n} texts priced; population (SDL + one headcount >= 10 + no exempt category): {pop}; of those, answers containing a denial phrase at all: {denies_in_pop}; FLAGGED: {len(flags)}")
    for f in flags:
        print(f"  [{f['src']}] Q: {f['q'][:120]}\n       -> {f['sentence'][:220]}")
    json.dump({"priced": n, "population": pop, "denial_phrase_in_population": denies_in_pop, "flags": flags}, io.open(os.path.join(REPO, "eval", "results", "price_d25_2026_11_22.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
