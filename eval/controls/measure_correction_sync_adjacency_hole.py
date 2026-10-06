# -*- coding: utf-8 -*-
"""HOW BIG IS THE HOLE THAT LET ROW 63 THROUGH? MEASURED, NOT ESTIMATED.

THE DIAGNOSIS THIS FOLLOWS FROM (eval/controls/diagnose_correction_sync_miss_row63.py,
artifact eval/results/correction_sync_miss_row63.json). Reconstructing all four inputs at
eb12e70/7d46df1 and running the REAL gate:

    (a) row came from a different key ............. REFUTED. The PINNED needle
        'ifikapo tarehe 10' resolved the key straight to row 63.
    (b) wrong_patterns never named the served value  SUPPORTED. Both patterns require the
        literal 'au' plus 'mwishoni/mwisho wa mwezi' -- the AMBIGUOUS "10th OR end of month"
        conflation. The row said a BARE 'ifikapo tarehe 10 ya mwezi unaofuata'.
    (c) soft gate, flag read past ................. REFUTED. Never flagged; a BLOCKING posture
        would have passed it identically.

So the gate's strong signal is not "does the row contradict the fact?" but "does the row
contain A FORMULATION THE CORRECTION'S AUTHOR ANTICIPATED?" -- and the gate's own docstring
says what those patterns were written for: "to catch a WRONG CLAIM APPEARING IN GENERATED TEXT
(a model reply or training pair asserting it)". Index rows are a different population, authored
by a different hand for a different purpose. Nothing requires the two wordings to overlap.

⛔ AND IT IS STILL OPEN, LIVE, ON ANOTHER FACT. `efd_threshold_tzs_11m` was corrected on
2026-08-29 (the TZS 11M "EFD threshold" is a fabrication; s.44(1) makes EFD the default for
everyone and the only exemption is a CG public notice). Its wrong_patterns include
`kizingiti cha efd[^.?!]{0,30}(11|14),?000,?000`. Index row 57 reads:

    "Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 ... kwa mwaka."

25 characters of ordinary Swahili -- "kuanza kutumia mashine ya" -- sit between `kizingiti cha`
and `efd`, so the pattern cannot match. The row asserts the exact fabrication its own fact
rejects, and has done since the correction. It is the SAME failure the checker's own docstring
already records as a KNOWN LIMITATION on the SIBLING fact ("the 40-char window was too narrow
for the actual sentence structure") -- recorded, widened for that one fact, and never asked of
any other.

THIS SCRIPT MEASURES THE CLASS. For every corrected fact, it pulls the DIGIT GROUPS its own
wrong_patterns single out as wrong, and asks whether the fact's resolved row ASSERTS one of
them (polarity-aware: a figure named in order to reject it is not an assertion). That test is
independent of regex adjacency, which is the thing that failed.

⚠️ WHAT THIS IS AND IS NOT. It is a LOWER BOUND on one axis -- figures. A correction that is
qualitative (EFD "no figure excuses a business", OSHA "representative not officer") carries no
figure to test, so this cannot see it; `figure_not_found` measured 1-of-5 precision on exactly
those. Every flag below is ADJUDICATED BY READING, not reported raw, because R26's second half
applies with force here: a false INERT verdict sends someone to rewrite a working control.
"""
import importlib.util
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "correction_sync_adjacency_hole.json")

NEG = re.compile(r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bwrong\b|\bhakuna\b|\bnever\b"
                 r"|kimepitwa|\bsi:\b)[\s:,—-]*(?:tzs\s*)?$", re.I)


def load(name):
    p = os.path.join(REPO, "scripts", f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def wrong_figures(patterns):
    """Digit groups a wrong_patterns regex singles out. `(11|14),?000,?000` yields
    11,000,000 and 14,000,000; a bare `\\d` class or a section number is skipped."""
    out = set()
    for p in patterns:
        for alt in re.findall(r"\(([\d|]+)\)[,.?]*0{3}[,.?]*0{3}", p):
            for n in alt.split("|"):
                if n.isdigit():
                    out.add(f"{int(n) * 1_000_000:,}")
        for lit in re.findall(r"(?<!\d)(\d{1,3}(?:,\d{3})+)(?!\d)", p):
            out.add(lit)
        for lit in re.findall(r"(?<!\d)(\d{1,3}),?(\d{3}),?(\d{3})(?!\d)", p):
            out.add(f"{int(''.join(lit)):,}")
    return {f for f in out if len(f) >= 7}        # millions and up; skip section numbers


# Adjudications, written after READING each flagged row. Asserted against what the measurement
# finds, so a changed flag set fails the run rather than inheriting a stale verdict.
ADJUDICATED = {
    "efd_threshold_tzs_11m": {
        "verdict": "GENUINE -- LIVE STALE ROW, SAME CLASS AS ROW 63",
        "why": "Row 57 opens 'Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS "
               "11,000,000 ... kwa mwaka', asserting as a threshold the exact figure its own "
               "fact calls a fabrication ('TZS 11M and TZS 14M are NOT EFD thresholds'). The "
               "wrong_pattern `kizingiti cha efd[^.?!]{0,30}(11|14),?000,?000` cannot match "
               "because 25 chars of ordinary Swahili sit between 'kizingiti cha' and 'efd'. "
               "Corrected 2026-08-29; still live 2026-10-06. NOT FIXED HERE -- reported.",
        "also_note": "It contradicts a SIBLING LIVE ROW: efd_not_every_business's row says "
                     "EFD is required by default regardless of turnover. Two live rows, "
                     "opposite answers to the same question.",
    },
    "vat_threshold_200m_july2024_increase": {
        "verdict": "FALSE POSITIVE -- the figure is CORRECT in this row's context",
        "why": "The flagged figure is TZS 100,000,000, and row 71 states it correctly: it is "
               "the 6-MONTH threshold ('TZS 100M per any 6-month rolling period'). The "
               "wrong_pattern it came from is `vat.*kizingiti.*100,000,000 kwa mwaka` -- "
               "100,000,000 PER YEAR, which is the superseded 12-month figure. Same number, "
               "two periods, one right and one wrong.",
        "what_it_demonstrates": "A FIGURE-ONLY test is context-blind by construction, and that "
                                "is not fixable by widening it: the wrong_pattern already "
                                "encodes the context ('kwa mwaka') and is RIGHT to. So this "
                                "measurement must stay ADJUDICATED and must never be promoted "
                                "to a blocking gate as it stands -- it would block a regen on "
                                "a correct row, which is the expensive direction (R21).",
    },
}


def main():
    precompute = load("precompute_rag_embeddings")
    load("check_facts_index_sync")
    chk = load("check_correction_sync")

    locked = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"),
                            encoding="utf-8"))
    index = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                           encoding="utf-8"))
    slugs = [f.split(":")[0].strip().lower() for f in index]

    corrected = [k for k, v in locked.items()
                 if isinstance(v, dict) and "correction_note" in v and not k.startswith("_")]

    flags, no_figure, unresolved, clean = [], [], [], []
    for key in corrected:
        v = locked[key]
        rows = chk.resolve_row_texts(key, index, slugs)
        if not rows:
            unresolved.append(key)
            continue
        figs = wrong_figures(v.get("wrong_patterns") or [])
        if not figs:
            no_figure.append(key)
            continue
        combined = " || ".join(rows)
        asserted = []
        for f in figs:
            for m in re.finditer(re.escape(f), combined):
                if not NEG.search(combined[max(0, m.start() - 16):m.start()]):
                    asserted.append(f)
                    break
        if asserted:
            flags.append({"key": key, "asserted_wrong_figures": sorted(set(asserted)),
                          "rows": [r[:300] for r in rows]})
        else:
            clean.append(key)

    found = {f["key"] for f in flags}
    assert found == set(ADJUDICATED), (
        "the flag set no longer matches the adjudicated set -- READ each flagged row before "
        f"trusting any verdict.\n  new, unadjudicated: {sorted(found - set(ADJUDICATED))}\n"
        f"  adjudicated but gone: {sorted(set(ADJUDICATED) - found)}")
    for f in flags:
        f.update(ADJUDICATED[f["key"]])

    payload = {
        "_question": "How many corrected facts have a row ASSERTING a figure their own "
                     "wrong_patterns call wrong, despite the gate reporting CLEAN?",
        "_why_this_test": "The gate's strong signal depends on a wrong_patterns regex matching "
                          "the index row's exact wording. Row 63 and row 57 both escaped by "
                          "WORD ORDER / ADJACENCY, not by content. This test extracts the "
                          "FIGURES the patterns single out and checks assertion directly, so "
                          "adjacency cannot hide a defect.",
        "_bound": "LOWER BOUND, one axis. Facts whose correction is QUALITATIVE carry no "
                  "figure to test and are invisible here -- which is most of the no_figure "
                  "bucket. R21: this is a lower bound on cost and an upper bound on nothing.",
        "population": {
            "locked_facts_total": len([k for k, v in locked.items()
                                       if isinstance(v, dict) and not k.startswith("_")]),
            "with_correction_note": len(corrected),
            "resolved_and_figure_testable": len(flags) + len(clean),
            "no_wrong_figure_to_test": len(no_figure),
            "unresolved_by_the_gate": len(unresolved),
        },
        "totals": {"asserting_a_wrong_figure": len(flags), "clean": len(clean)},
        "flags": flags,
        "no_figure_to_test": sorted(no_figure),
        "unresolved": sorted(unresolved),
        "_gate_said": "correction_sync=CLEAN on every regen through 2026-10-06, including the "
                      "one that shipped today.",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(json.dumps(payload["population"], indent=2))
    print(json.dumps(payload["totals"], indent=2))
    for f in flags:
        print(f"\n  [{f['verdict'][:28]}] {f['key']}  figures={f['asserted_wrong_figures']}")
        print(f"      {f['rows'][0][:190]}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
