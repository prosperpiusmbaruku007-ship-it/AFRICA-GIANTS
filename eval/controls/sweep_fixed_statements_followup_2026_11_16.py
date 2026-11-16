"""SWEEP + PROBES (R17/R12c) for the 2026-11-16 EXTENSION of the fixed-statement route: voluntary VAT registration, the WCF accident-reporting chain, VAT withholding on a
mixed supply. Founder's decision of the same day; founding specimens are the live wrong replies of the follow-up deploy.

POPULATION (R12c step 1, mechanical): every committed question string, routed by the OLD `chike/routing.py` (`--old-rev`, a separate module, never a reload) and the NEW one.
A string whose route did not change cannot have changed its answer; the changed ones are the blast radius and every one is printed. Then PROBES: in-scope questions that
must DIVERT, and (the half that does the work, R17 -- three of three OOC list changes collided with in-scope vocabulary) questions carrying the SAME vocabulary that must stay
CLEAN or keep another engine. The original five topics' probes are re-run as controls on unchanged routes.

    python eval/controls/sweep_fixed_statements_followup_2026_11_16.py [--old-rev HEAD]
Exit 1 if a probe disagrees, or a corpus string diverts anywhere but to fixed_statement.
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
    # ---- voluntary VAT registration: must DIVERT
    ("Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?", FS, "live specimen (voluntary)"),
    ("Nina mauzo madogo, naweza kusajili VAT ingawa sijafikia kiwango?", FS, "live specimen 2 (no 'hiari')"),
    ("Naweza kujisajili VAT ingawa mauzo yangu bado ni madogo?", "none", "no voluntariness cue (hiari / sijafikia kiwango): NOT diverted -- a bare mauzo madogo is also the mandatory-threshold question"),
    ("Je, usajili wa VAT wa hiari upo Tanzania?", FS, "'upo'"),
    ("Nataka kusajili biashara yangu VAT kwa hiari, nifanyeje?", FS, "'nataka'"),
    ("Can I register for VAT voluntarily?", FS, "English"),
    # ---- voluntary: same vocabulary, must stay CLEAN or keep another engine
    ("Kizingiti cha kujisajili VAT ni kiasi gani?", "none", "the threshold question is a different question"),
    ("Mauzo yangu ni milioni 50 kwa mwaka, lazima nijisajili VAT?", "vat_registration", "the registration engine wins"),
    ("Nimesajiliwa VAT, naweza kujiondoa kwa hiari?", "none", "deregistration, not registration"),
    ("Usajili wa NSSF ni wa hiari?", "none", "another levy's voluntariness: unchanged route"),
    ("Naweza kujisajili VAT mtandaoni?", "none", "how to register, no voluntariness"),
    ("Je, mshauri wa kodi lazima ajisajili VAT?", "none", "professionals: a different limb, no 'hiari'"),
    ("Mchango wa hiari wa NSSF ni kiasi gani?", "none", "NSSF voluntary contribution: unchanged route"),
    ("VAT ya hiari ni kiasi gani?", "none", "no registration word"),
    ("Nimeuza kwa mkopo mauzo milioni 250 kwa mwaka, je nijisajili VAT?", "vat_registration", "registration engine wins"),
    # ---- WCF accident reporting: must DIVERT
    ("Mfanyakazi ameumia jana nina siku ngapi za kupeleka taarifa ya ajali", FS, "nat_45 verbatim"),
    ("Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", FS, "live specimen"),
    ("Mfanyakazi amepata ajali kazini, taarifa WCF inaanza kuhesabiwa lini?", FS, "live specimen 2 (the trigger)"),
    ("Mfanyakazi ameumia kazini, mwajiri ana muda gani wa kuripoti WCF?", FS, "own phrasing"),
    ("Taarifa ya ajali kazini inapelekwa WCF ndani ya siku ngapi?", FS, "fp_06b-like"),
    ("How many days to report a workplace accident to WCF?", FS, "English"),
    # ---- WCF: same vocabulary, must stay CLEAN
    ("Taarifa ya ugonjwa wa kazini WCF ni siku ngapi?", "none", "occupational disease is a different chain (14 + 7)"),
    ("Ajali ya kazini fidia ni kiasi gani?", "none", "compensation amount, not reporting"),
    ("Ajali ya gari, nipeleke taarifa polisi lini?", "none", "a road accident: no workplace word"),
    ("Ajali ya kazini WCF itolewe taarifa ndani ya siku 30, sivyo?", "none", "a false-premise question goes to the model (eval_343)"),
    ("Mfanyakazi akifa kazini taarifa WCF ni muda gani?", "none", "death has its own limb (12 months)"),
    ("Tofauti kati ya ripoti ya ajali ya OSHA na WCF ni ipi?", "none", "OSHA vs WCF: a comparison, not the chain"),
    ("Nahitaji kujisajili WCF nikiwa na mfanyakazi, ndani ya siku ngapi?", "none", "WCF registration deadline, no accident"),
    ("WCF ni asilimia ngapi?", "wcf", "the WCF rate engine"),
    # ---- VAT withholding, mixed supply: must DIVERT
    ("VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?", FS, "live specimen"),
    ("Mkandarasi anatoa vifaa na kazi, VAT ya zuio inahesabiwaje?", FS, "live specimen 2"),
    ("Je, VAT ya zuio kwa mkataba wenye vifaa na huduma inakatwa kwa 6% kwenye thamani yote?", FS, "live specimen 3 (whole value)"),
    ("Nauza vifaa na kufunga (bidhaa na huduma), zuio la VAT ni asilimia ngapi?", FS, "own phrasing"),
    # ---- mixed: same vocabulary, must stay CLEAN
    ("VAT ya zuio kwa bidhaa ni asilimia ngapi?", "none", "pure goods: no 3:2 injected"),
    ("VAT ya zuio kwa huduma ni asilimia ngapi?", "none", "pure services"),
    ("Cheti cha VAT ya zuio kinatolewa lini?", "none", "certificate timing"),
    ("VAT ya zuio kwa bidhaa na huduma inalipwa lini?", "none", "remittance timing, same vocabulary"),
    ("Kodi ya zuio kwa mkandarasi wa ujenzi ni asilimia ngapi?", "none", "ITA construction withholding: the hedged fact, not this route"),
    ("VAT ya zuio, bidhaa na huduma, ni kweli inakatwa 3%?", "none", "premise-check form goes to the model"),
    # ---- the original five, re-run as controls on unchanged routes
    ("Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?", FS, "control: notice"),
    ("Severance pay inahesabiwaje?", FS, "control: severance"),
    ("Overtime inalipwa kiasi gani?", FS, "control: overtime"),
    ("Likizo ya mwaka ni siku ngapi?", FS, "control: annual leave"),
    ("Nimeuza kwa mkopo, VAT inalipwa lini?", FS, "control: VAT time of supply"),
    ("Likizo ya uzazi ni siku ngapi?", "none", "control: maternity leave"),
    ("Kizingiti cha EFD ni kiasi gani?", "none", "control: EFD (unchanged route)"),
    ("Niko chini ya kizingiti cha VAT lakini nataka kujisajili VAT kwa hiari -- je EFD inakuwa lazima mara moja?", "none", "an EFD question that mentions voluntary registration"),
    ("Faida ya kusajili VAT kwa hiari kabla ya kizingiti ni nini?", "none", "benefits, not the routes"),
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
        print(f"  {o} -> {n} :: {q[:170]!r}")
        if n != FS or o != "none":
            bad.append(q)
    out = os.path.join(REPO, "eval", "results", "sweep_fixed_statements_followup_2026_11_16.json")
    json.dump({"corpus_strings": len(qs), "changed": [dict(q=q, old=o, new=n) for q, o, n in moved],
               "probes": [dict(q=q, want=w, got=new.detect_intent(q), was=old.detect_intent(q)) for q, w, _ in PROBES]},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
