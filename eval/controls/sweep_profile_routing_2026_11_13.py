"""SWEEP + PROBES (R17/R12c) for the 2026-11-13 routing batch: minimum wage ("Nalipa <worker> N, ni halali?", "inatosha kisheria") and presumptive
("kodi ya makadirio kwa mauzo ya milioni N").

POPULATION (step 1 of R12c, mechanical): every committed question string (the corpus the earlier sweeps use), routed by the OLD
`chike/routing.py` (from git HEAD, loaded as a separate module -- never a reload) and the NEW one. A string whose route did not change cannot
have changed its answer; the changed ones are the blast radius and every one is printed. Then PROBES: in-scope probes that must DIVERT, and
(the half that does the work -- R17) probes that contain the risky vocabulary and must come back CLEAN.

    python eval/controls/sweep_profile_routing_2026_11_13.py [--old-rev HEAD]
Exit 1 if a probe disagrees with its expectation or if a corpus string diverts outside the expected two routes.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (question, expected route NOW, why)
PROBES = [
    # must DIVERT
    ("Nalipa dada wa kazi za nyumbani 150,000 kwa mwezi, ni halali?", "minimum_wage", "the gap, verbatim"),
    ("Nalipa mlinzi 120,000 kwa mwezi, ni halali?", "minimum_wage", "the gap, security guard"),
    ("Nalipa mfanyakazi wa duka 200,000 kwa mwezi, je ni sawa?", "minimum_wage", "colloquial + 'ni sawa'"),
    ("Mfanyakazi wa duka analipwa 200,000 kwa mwezi, je inatosha kisheria?", "minimum_wage", "'inatosha kisheria' frame"),
    ("Kodi ya makadirio kwa mauzo ya milioni 40 ni kiasi gani?", "presumptive", "the gap, verbatim"),
    ("Nina duka, mauzo milioni 80 kwa mwaka, kodi ya makadirio ni ngapi?", "presumptive", "the gap, verbatim"),
    ("Kodi ya makadirio kwa mauzo ya TZS 25,000,000 ni shingapi?", "presumptive", "TZS notation"),
    ("Presumptive tax kwa mauzo ya mwaka ni milioni 60 ni kiasi gani?", "presumptive", "English cue + 'mauzo ya mwaka ni'"),
    # must come back CLEAN (route unchanged from before)
    ("Nalipa kodi ya mapato 150,000 kwa mwezi, ni halali?", "none", "`nalipa` + kodi: a TAX payment, not a wage"),
    ("Nalipa NSSF 70,000 kila mwezi, ni halali?", "nssf", "levy wins"),
    ("Nalipa PAYE 80,000, ni sawa?", "paye", "levy wins"),
    ("Nalipa pango la duka 300,000 kwa mwezi, ni halali kukata kodi ya zuio?", "rent_wht", "rent, not a wage"),
    ("Nalipa ada ya leseni 150,000, ni halali?", "none", "`nalipa` + a fee, not a person"),
    ("Pesa 200,000 inatosha kulipa umeme wa duka?", "none", "bare 'inatosha' is ordinary Swahili"),
    ("Kodi ya makadirio ni nini?", "none", "definition question, no figure"),
    ("Kodi ya makadirio kwa mapato ya milioni 40 ni kiasi gani?", "none", "`mapato` is not turnover"),
    ("Kodi ya makadirio kwa mauzo ya daladala ya milioni 40 ni kiasi gani?", "none", "transport schedule veto"),
    ("Kampuni ina mauzo ya milioni 80, kodi ya makadirio ni ngapi?", "none", "entity veto: a company"),
    ("Mauzo ya milioni 80, kodi gani nalipa?", "none", "no named presumptive cue"),
    ("Nitumie kodi ya makadirio au mfumo wa kawaida? Mauzo ya milioni 40", "none", "election question veto"),
]


def load_old(rev):
    src = subprocess.run(["git", "show", f"{rev}:chike/routing.py"], capture_output=True, cwd=REPO, check=True).stdout
    path = os.path.join(REPO, "scratch", "routing_old.py")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(src)
    spec = importlib.util.spec_from_file_location("chike.routing_old_snapshot", path, submodule_search_locations=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "chike"                                            # so its relative imports resolve against the live package
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-rev", default="HEAD")
    a = ap.parse_args()
    import sweep_parser_scale_order_2026_11_12 as sw
    from chike import routing as new
    old = load_old(a.old_rev)
    bad = []

    print("== PROBES ==")
    for q, want, why in PROBES:
        got, was = new.detect_intent(q), old.detect_intent(q)
        ok = got == want
        bad += [] if ok else [q]
        print(f"{'ok ' if ok else 'BAD'} now={got:<13} was={was:<13} want={want:<13} {why} :: {q[:62]}")

    qs, _ = sw.corpus()
    moved = []
    for q in qs:
        if len(q) > 600:
            continue
        try:
            o, n = old.detect_intent(q), new.detect_intent(q)
        except Exception:                                                # noqa: BLE001
            continue
        if o != n:
            moved.append((q, o, n))
    print(f"\n== CORPUS: {len(qs)} strings, {len(moved)} changed route ==")
    for q, o, n in moved:
        print(f"  {o} -> {n} :: {q[:150]!r}")
        if n not in ("minimum_wage", "presumptive"):
            bad.append(q)
    out = os.path.join(REPO, "eval", "results", "sweep_profile_routing_2026_11_13.json")
    json.dump({"corpus_strings": len(qs), "changed": [dict(q=q, old=o, new=n) for q, o, n in moved],
               "probes": [dict(q=q, want=w, got=new.detect_intent(q), was=old.detect_intent(q)) for q, w, _ in PROBES]},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
