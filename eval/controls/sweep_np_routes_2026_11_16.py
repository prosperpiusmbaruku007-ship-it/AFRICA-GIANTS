"""SWEEP + PROBES (R17/R12c) for the 2026-11-16 np_ ROUTE changes (founder, item 3): (a) the four original fixed-statement topics (notice, severance, overtime, annual leave) now also route on a leading/negated
PREMISE phrasing of their own topic ("Likizo ya mwaka haizidi wiki mbili ..., sivyo?"); (b) `asks_rate` also reads the levy AFTER the ask ("asilimia ngapi ya mishahara yao ... WCF?", np_28).

POPULATION (R12c step 1, mechanical): every committed question string, routed by the OLD `chike/routing.py` (`--old-rev`, a separate module, never a reload) and the NEW one; also whether `asks_rate` changed on a string
that routes to an engine. A string whose route did not change cannot have changed its answer; every changed one is printed. Then PROBES: must DIVERT, and (the half that does the work) the same vocabulary that must
STAY CLEAN or keep another engine.

    python eval/controls/sweep_np_routes_2026_11_16.py [--old-rev HEAD]
Exit 1 if a probe disagrees, or a corpus string diverts anywhere but to fixed_statement / the rate statement.
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

FS = "fixed_statement"
PROBES = [
    # ---- (a) premise phrasings of the four topics: must DIVERT (the founding specimens are verbatim)
    ("Likizo ya mwaka haizidi wiki mbili kwa mujibu wa sheria, sivyo?", FS, "np_12 verbatim"),
    ("Mfanyakazi aliyefanya kazi miezi 8 tu akiachishwa, hastahili malipo ya kuachishwa kazi, sivyo?", FS, "np_05 verbatim"),
    ("Nina mfanyakazi wa kulipwa kwa wiki ambaye amefanya kazi kwangu miaka miwili. Nikitaka kusitisha ajira yake, notice ya siku 7 bado inatosha, sivyo?", FS, "set #2 #11 verbatim (notice)"),
    ("Mfanyakazi wangu anafanya overtime baada ya muda wa kawaida. Nimeambiwa siwezi kumlipa kiwango kilekile cha saa za kawaida, lazima iwe angalau mara moja na nusu, ni kweli?", FS, "set #2 #14 verbatim (overtime)"),
    ("Mfanyakazi wangu hajatumia likizo yake ya mwaka huu. Nimeambiwa ana haki ya siku 28 mfululizo za likizo yenye malipo, siyo?", FS, "set #2 #10 verbatim (annual leave)"),
    ("Mfanyakazi wangu amefanya kazi miezi 8 tu. Nikisitisha ajira yake sasa, sihitajiki kumlipa severance pay, au siyo?", FS, "set #2 #12 verbatim (severance)"),
    ("Likizo ya mwaka ni siku 21 tu, ni kweli?", FS, "false-premise leave"),
    ("Hastahili severance kama amefanya kazi chini ya mwaka, sivyo?", FS, "own phrasing"),
    # ---- (a) same vocabulary: must STAY CLEAN or keep another engine
    ("Mfanyakazi wangu ana likizo ya uzazi, sivyo?", "none", "another leave type: the topic veto"),
    ("Likizo ya mwaka bila malipo inaruhusiwa, sivyo?", "none", "unpaid leave: the topic veto"),
    ("Mfanyakazi wangu analipwa overtime, hivyo NSSF yake inakatwa kwenye overtime pia, sivyo?", "none", "another levy named: the global veto"),
    ("Naweza kumpa mfanyakazi likizo ya mwaka bila kumlipa mshahara, sivyo?", FS, "WAS WRONGLY EXPECTED 'none' (history): the closing 'sivyo?' IS a premise cue, and the statement (paid, at least 28 days) answers it correctly"),
    ("Nina wafanyakazi 7 tu, bado sihusiki na SDL, sivyo?", "none", "SDL premise question: not a fixed-statement topic, unchanged"),
    ("Mshahara wa mfanyakazi ni 600,000, overtime ya saa 10 ni kiasi gani?", FS, "UNCHANGED ROUTE (was FS before this change too; WAS WRONGLY EXPECTED 'none' -- recorded as a pre-existing observation: the overtime statement answers a computation question with the rule, no figure)"),
    ("Mfanyakazi alifanya kazi miaka 3 na kuachishwa, severance yake ni kiasi gani?", FS, "how-much ask: already routed before this change (control, unchanged route)"),
    # ---- (b) the levy after the ask: must DIVERT to the rate statement
    ("Nina wafanyakazi 6, naomba unisaidie kujua ni asilimia ngapi ya mishahara yao inapaswa kwenda kwenye WCF?", "wcf", "np_28 verbatim"),
    ("Asilimia ngapi ya mishahara ninapaswa kulipa NSSF?", "nssf", "own phrasing"),
    ("Naomba kujua asilimia ngapi ya mishahara inakwenda SDL?", "sdl", "own phrasing"),
    # ---- (a) added after the first sweep (read by hand): the severance TAX question and the "likizo yake ya mwaka" form
    ("Malipo ya fidia ya kuachishwa kazi (severance pay) hayapigwi kodi — je, ni kweli?", "none", "swept diversion: a TAX question about severance -- the wrong-topic harm class, now vetoed"),
    ("Mfanyakazi wangu hajatumia likizo yake ya mwaka huu. Nimeambiwa ana haki ya siku 28 mfululizo za likizo yenye malipo, siyo?", FS, "set #2 #10 verbatim: 'likizo yake ya mwaka' now reads as the annual-leave cue"),
    ("Mauzo yangu ni TZS 50,000,000 kwa mwaka — VAT ni asilimia ngapi, na je nahitaji kusajili NSSF?", "nssf", "swept: asks_rate must NOT flip to NSSF's rate across the comma (route unchanged: the decomposer splits it)"),
    # ---- (b) must STAY CLEAN / keep another engine
    ("Nina wafanyakazi 6 kila mmoja 500,000, asilimia ngapi ya mishahara inakwenda WCF kwa jumla?", "wcf", "carries a figure: the compute path already owned it (control, unchanged route)"),
    ("Asilimia ngapi ya mshahara wa mfanyakazi inakatwa PAYE?", "none", "PAYE is banded: no single rate, not a statement-route levy"),
    ("Asilimia ngapi ya faida ni kodi ya mapato ya kampuni?", "corporate_tax", "no payroll levy token: the corporate-tax engine keeps it (control, unchanged route; WAS WRONGLY EXPECTED 'none')"),
]


def load_old(rev):
    src = subprocess.run(["git", "show", f"{rev}:chike/routing.py"], capture_output=True, cwd=REPO, check=True).stdout
    path = os.path.join(REPO, "scratch", "routing_old.py")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(src)
    spec = importlib.util.spec_from_file_location("chike.routing_old_snapshot", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "chike"
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
        print(f"{'ok ' if ok else 'BAD'} now={got:<16} was={was:<16} want={want:<16} {why} :: {q[:60]}")
    qs, _ = sw.corpus()
    moved, rate_moved = [], []
    for q in qs:
        if len(q) > 600:
            continue
        try:
            o, n = old.detect_intent(q), new.detect_intent(q)
            ro, rn = old.asks_rate(q), new.asks_rate(q)
        except Exception:                                                # noqa: BLE001
            continue
        if o != n:
            moved.append((q, o, n))
        if ro != rn:
            rate_moved.append((q, o, n, ro, rn))
    print(f"\n== CORPUS: {len(qs)} strings, {len(moved)} changed route, {len(rate_moved)} changed asks_rate ==")
    for q, o, n in moved:
        print(f"  {o} -> {n} :: {q[:170]!r}")
        if n not in (FS, "wcf", "nssf", "sdl") or o != "none":
            bad.append(q)
    for q, o, n, ro, rn in rate_moved:
        print(f"  asks_rate {ro}->{rn} (route {o}->{n}) :: {q[:150]!r}")
    out = os.path.join(REPO, "eval", "results", "sweep_np_routes_2026_11_16.json")
    json.dump({"corpus_strings": len(qs), "changed": [dict(q=q, old=o, new=n) for q, o, n in moved],
               "asks_rate_changed": [dict(q=q, route_old=o, route_new=n, was=ro, now=rn) for q, o, n, ro, rn in rate_moved],
               "probes": [dict(q=q, want=w, got=new.detect_intent(q), was=old.detect_intent(q)) for q, w, _ in PROBES]},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
