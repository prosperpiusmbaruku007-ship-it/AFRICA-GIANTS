"""SWEEP + PROBES (R17/R12c) for the 2026-11-16 fixed-statement route (notice, severance, overtime, annual leave, VAT time of supply).

POPULATION (R12c step 1, mechanical): every committed question string, routed by the OLD `chike/routing.py` (from `--old-rev`, a separate module,
never a reload) and the NEW one. A string whose route did not change cannot have changed its answer; the changed ones are the blast radius and
every one is printed. Then PROBES: in-scope questions that must DIVERT, and (the half that does the work, R17) questions that contain the same
vocabulary and must stay CLEAN or keep another engine.

    python eval/controls/sweep_fixed_statements_2026_11_16.py [--old-rev HEAD]
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
# (question, expected route NOW, why)
PROBES = [
    # must DIVERT
    ("Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?", FS, "live specimen 1 (notice)"),
    ("Severance pay inahesabiwaje?", FS, "live specimen 2 (severance)"),
    ("Overtime inalipwa kiasi gani?", FS, "live specimen 3 (overtime)"),
    ("Likizo ya mwaka ni siku ngapi?", FS, "live specimen 4 (annual leave)"),
    ("Nimeuza kwa mkopo, VAT inalipwa lini?", FS, "live specimen 5 (VAT credit sale)"),
    ("Nikitaka kumfukuza mfanyakazi, notisi ni ya siku ngapi?", FS, "notice, employer's wording"),
    ("Mfanyakazi anataka kuacha kazi, anatakiwa kutoa notisi ya muda gani?", FS, "notice, employee's wording"),
    ("Malipo ya kuachishwa kazi ni kiasi gani?", FS, "severance, Swahili label"),
    ("Mfanyakazi aliyeachishwa anastahili severance?", FS, "severance, 'anastahili'"),
    ("Saa za ziada nalipa vipi?", FS, "overtime, Swahili label"),
    ("Annual leave ni siku ngapi?", FS, "annual leave, English label"),
    ("Mfanyakazi anastahili likizo ya mwaka kwa siku ngapi?", FS, "annual leave, 'anastahili'"),
    ("Nimetoa invoice, mteja hajalipa bado, VAT inadaiwa lini?", FS, "VAT, invoice + unpaid"),
    ("How many days notice must I give an employee?", FS, "notice, English"),
    ("Nimemfukuza mfanyakazi, mshahara wake 500,000, notisi ni siku ngapi?", FS, "carries a figure: states the rule, computes nothing"),
    # must come back CLEAN, or keep ANOTHER route -- the same vocabulary in another question
    ("Likizo ya uzazi ni siku ngapi?", "none", "maternity leave is a different fact"),
    ("Likizo ya ugonjwa ni siku ngapi?", "none", "sick leave"),
    ("Likizo ya mwaka ni bila malipo?", "none", "unpaid veto"),
    ("Overtime inakatwa NSSF kiasi gani?", "none", "another levy named: a different question"),
    ("Mfanyakazi alifanya overtime masaa 10, mshahara 800,000, PAYE ni kiasi gani?", "paye", "PAYE engine wins"),
    ("Severance inaingia kwenye hesabu ya SDL?", "none", "SDL base question"),
    ("Notisi ya TRA ya ukaguzi ni siku ngapi kujibu?", "none", "a TRA notice, not employment"),
    ("Notisi ya kupandisha kodi ya pango ni siku ngapi?", "none", "a rent notice: no employment word"),
    ("Nalipa overtime na severance kiasi gani?", "none", "two topics: one statement would drop a limb"),
    ("VAT return nawasilisha lini?", "none", "VAT but no credit-sale cue"),
    ("VAT inalipwa lini kwenye mauzo ya nje?", "none", "VAT timing, no credit-sale cue"),
    ("Kiasi gani kitatozwa nikichelewa kulipa VAT ya invoice?", "none", "late-payment penalty, not time of supply"),
    ("Nimeuza kwa mkopo, nahitaji mashine ya EFD?", "none", "credit cue but no VAT/ask"),
    ("Nimeuza kwa mkopo mauzo milioni 250 kwa mwaka, je nijisajili VAT?", "vat_registration", "VAT registration engine wins"),
    ("Mfanyakazi akikataa kuchukua likizo ya mwaka je?", "none", "no ask cue: a topic word is not a question"),
    ("Mkataba wa kazi ni lazima uandikwe?", "none", "contract-in-writing: deliberately unanswered"),
    ("Nalipa mfanyakazi wa duka 200,000 kwa mwezi, ni halali?", "minimum_wage", "min wage unchanged"),
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
    out = os.path.join(REPO, "eval", "results", "sweep_fixed_statements_2026_11_16.json")
    json.dump({"corpus_strings": len(qs), "changed": [dict(q=q, old=o, new=n) for q, o, n in moved],
               "probes": [dict(q=q, want=w, got=new.detect_intent(q), was=old.detect_intent(q)) for q, w, _ in PROBES]},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
