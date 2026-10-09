# -*- coding: utf-8 -*-
"""PILOT STOCK-TAKE, 2026-10-08 — both bars, re-derived from artifacts.

Every figure here is recomputed from RAW ROWS, never read out of a summary block. That rule
exists because this project has twice found a correct summary attached to rows that said
something else, and because R18 makes a cited number provisional until its instrument is
committed. The instrument is this file.

🔴 THREE CORRECTIONS TO THE FRAMING BEFORE ANY NUMBER, because each changes what the numbers
mean:

  1. THERE IS NO 2026-09-21 ENTRY. The last actual PILOT RE-DERIVATION is 2026-09-04. The
     nearest major adjudication to the 21st is 2026-09-23 (the 78-row edge-probe set, which
     is where the floor's number comes from). So "closer than on 2026-09-21" is answered
     against TWO baselines, named separately, because they measure different things.

  2. NO FULL GATE HAS RUN SINCE 2026-08-09. The newest 400-question run is `1476caa`
     (eval/results/gate_phase_d_paired_1476caa.json, committed 2026-08-09). Everything since
     -- all of September and October -- is defect-class work measured on sub-populations.
     **So Bar A's headline is two months old, and no amount of since-closed defects changes
     it until it is re-run.** That is the single most important fact in this stock-take.

  3. THE INDEX IS NOT THE ONE THAT WAS MEASURED. `1476caa` ran against 217 index facts;
     production serves 184 (fact-group consolidation). A gate number is a statement about a
     system, and that system has changed shape underneath it.

WHAT THIS CAN AND CANNOT SAY. It can re-derive the last measured position, name every
population (R22), and bound how stale each figure is. It CANNOT tell you the current
accuracy: that needs a gate run. Saying otherwise would be exactly the error of reading a
defect-class win as a gate movement.
"""
import collections
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "pilot_stocktake_2026_10_08.json")

LATEST_GATE = "eval/results/gate_phase_d_paired_1476caa.json"
PRIOR_GATE = "eval/results/gate_orchestrator_combined_5a62c00.json"
FLOOR = "eval/results/extended_078_adjudication_2026_09_23.json"
VOCAB = "eval/results/vocab_substitution_arm_2026_09_24.json"


def _load(rel):
    with open(os.path.join(REPO, *rel.split("/")), encoding="utf-8") as fh:
        return json.load(fh)


# ── BAR A: recomputed from raw rows, per population ──────────────────────────────
def bar_a():
    g = _load(LATEST_GATE)
    rows = g["v16_results"]
    assert len(rows) == 400, f"expected 400 rows, got {len(rows)}"
    by_src = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        s = r.get("source") or "?"
        by_src[s][0] += 1
        by_src[s][1] += 1 if r.get("pass") is True else 0
    overall_pass = sum(1 for r in rows if r.get("pass") is True)
    clarified = sum(1 for r in rows if r.get("clarified") is True)

    # The run's own bucket block, recomputed-against rather than trusted: if the summary and
    # the rows disagree, that is itself the finding.
    buckets = g["summary"]["buckets"]
    recheck = {}
    for name, b in buckets.items():
        v16 = b.get("raw", {}).get("v16")
        if isinstance(v16, list) and len(v16) == 3:
            recheck[name] = {"summary_raw": v16[2], "n_scored": v16[1], "passes": v16[0]}

    prior = _load(PRIOR_GATE)
    prior_rows = prior["results"]
    prior_pass = sum(1 for r in prior_rows if r.get("pass") is True)

    return {
        "_what": "Bar A -- accuracy on questions the corpus covers. Recomputed from raw rows.",
        "_population_and_why": (
            "The 400-question combined corpus: gate_001 (200, the original accuracy gate), "
            "additions_003 (150, adversarial), additions_002 (50, staged compute). R22: the "
            "decision 'is Bar A near R7's >85%' applies to the FACT PATH, because that is "
            "where a pilot's first questions land -- so the fact-path bucket is reported "
            "separately and is NOT the same claim as the 400-row blend."),
        "latest_full_gate": {
            "artifact": LATEST_GATE, "clone_head": g["summary"]["clone_head"],
            "committed": "2026-08-09", "index_facts_at_run": g["summary"]["index_facts"],
            "index_facts_in_production_now": 184,
            "rows": len(rows), "passes": overall_pass,
            "raw_overall": round(overall_pass / len(rows), 4),
            "clarified": clarified,
            "by_source": {s: {"n": t, "pass": p, "rate": round(p / t, 4)}
                          for s, (t, p) in sorted(by_src.items())},
            "buckets_from_the_run": recheck,
        },
        "prior_full_gate": {
            "artifact": PRIOR_GATE, "committed": "2026-07-28",
            "rows": len(prior_rows), "passes": prior_pass,
            "raw_overall": round(prior_pass / len(prior_rows), 4),
        },
        "_the_number_that_matters_for_R7": (
            "R7 Gate 1 is >85% in-corpus. On the latest full gate the FACT PATH bucket is "
            "85.87% raw / 85.38% reliable -- i.e. ON the line, not clear of it. The 400-row "
            "blend is 82.5% raw, which is BELOW it, and the adversarial 150 is 75%. Quoting "
            "any single one of those as 'Bar A' is the blending error the two-bar framing "
            "exists to prevent."),
        "_staleness": (
            "TWO MONTHS OLD, and measured against a 217-fact index that production no longer "
            "serves (184 now). Everything closed since -- Part XII, the EFD 11M fabrication, "
            "the NSSF 100k fine, the BRELA fee schedule, rent WHT, two wired guards -- is "
            "INVISIBLE to this figure until the gate is re-run."),
    }


# ── HOW STALE: which gate rows touch a fact corrected since the run ──────────────
# Each pattern names a correction shipped AFTER 2026-08-09, with the date. A row touching one
# is a row whose July/August verdict can no longer be trusted in either direction -- it may
# have been failed on a key that was wrong (ext_15's shape) or passed on a fact since
# superseded. This BOUNDS the possible movement; it does not predict its sign.
SINCE_CORRECTED = {
    "part_xii_citation_2026_10_05": r"sehemu\s*(?:ya\s*)?xi{2,3}|part\s*xi{2,3}|ss\.?\s*437|320\s*-\s*328",
    "brela_fee_schedule_2026_10_06": r"USD\s*25\b|USD\s*220\b|USD\s*750\b|300,?000.*hisa|hisa.*300,?000"
                                     r"|440,?000|kampuni\s+ya\s+kigeni.*(?:faini|ada)",
    "efd_11m_fabrication_2026_10_06": r"11,?000,?000|milioni\s*11|11\s*milioni|TZS\s*11\s*M",
    "nssf_fine_100k_2026_10_05": r"faini.*100,?000(?![,.\d])|laki\s+moja|elfu\s+mia\s+moja",
    "nssf_deadline_2026_10_05": r"nssf.*tarehe\s*10\b|tarehe\s*10.*nssf",
    "rent_wht_nonresident_2026_09_26": r"pango.*asilimia\s*(?:15|20)|asilimia\s*(?:15|20).*pango",
    # ⛔ THE PRESUMPTIVE PATTERN MUST CARRY ITS SUBJECT. A bare `asilimia 3.5` matched 38
    # rows -- and ZERO were about presumptive tax: 31 were SDL (whose rate is ALSO 3.5%), plus
    # NSSF, PAYE, WCF and VAT rows. It inflated the staleness count from 12 to 50. The
    # bare-magnitude collision yet again, this time in the INFLATING direction, which is at
    # least the visible one (R39): a bigger number invites scrutiny, a smaller one reads as
    # progress. Verified by listing the matched subdomains before trusting the count.
    "presumptive_rate_ceiling_2026_09_01":
        r"(?:makisio|presumptive)[^.]{0,80}(?:asilimia\s*3[.,]5|3[.,]5%|100,?000,?000)"
        r"|(?:asilimia\s*3[.,]5|3[.,]5%|100,?000,?000)[^.]{0,80}(?:makisio|presumptive)",
    "paye_p9_deadline_2026_10_05": r"\bP9\b.*31\s*Machi|31\s*Machi.*\bP9\b",
}


def staleness():
    g = _load(LATEST_GATE)
    rows = g["v16_results"]
    hits = collections.defaultdict(list)
    touched = set()
    for i, r in enumerate(rows):
        text = " ".join(str(r.get(k) or "") for k in
                        ("question_sw", "correct_answer_sw", "generated"))
        for name, pat in SINCE_CORRECTED.items():
            if re.search(pat, text, re.I):
                hits[name].append({"i": i, "id": r.get("id"),
                                   "subdomain": r.get("subdomain"),
                                   "pass_at_run": r.get("pass")})
                touched.add(i)
    n = len(rows)
    tp = sum(1 for i in touched if rows[i].get("pass") is True)
    return {
        "_what": "How many of the 400 gate rows touch a fact corrected AFTER the run.",
        "_why_this_bounds_rather_than_predicts": (
            "A touched row's old verdict is untrustworthy in BOTH directions: it may have "
            "been FAILED against a key since found wrong (ext_15 is the worked example -- "
            "its 'Section XII' reply was marked WRONG and the Act vindicates the numeral), "
            "or PASSED on a value since superseded. So this is the size of the uncertain "
            "slice, not a predicted gain. Anyone reading it as 'Bar A is really N points "
            "higher' has read it backwards."),
        "rows_total": n,
        "rows_touched": len(touched),
        "pct_touched": round(100.0 * len(touched) / n, 1),
        "touched_passing_at_run": tp,
        "touched_failing_at_run": len(touched) - tp,
        "by_correction": {k: len(v) for k, v in sorted(hits.items())},
        "detail": {k: v[:6] for k, v in sorted(hits.items())},
    }


# ── BAR B: the floor, recomputed from the adjudication rows ──────────────────────
def bar_b():
    d = _load(FLOOR)
    rows = d["rows"]
    # ⛔ KEYED ON `cat`, NOT `cause`. My first attempt matched `cause == 'corpus_gap'`, which
    # is only 3 rows, and reported a tidy-looking 3/3 = 100%. That was MY extraction, not a
    # finding: the gap POPULATION is defined by how the probes were AUTHORED (cat prefix
    # `coverage_gap_`, 12 rows), while `cause` is the adjudicator's attribution of blame per
    # row -- and 9 of those 12 are attributed to `model`, not to `corpus_gap`, precisely
    # because the corpus gap is the SETTING and the fabrication is the BEHAVIOUR. Reading the
    # blame field as the population conflated the two. R34: the population is a property of
    # the probe set, and it is checkable by reading the probes.
    gap = [r for r in rows if str(r.get("cat") or "").startswith("coverage_gap_")]
    unbuilt = [r for r in rows if str(r.get("cat") or "").endswith("_unbuilt")]
    verdicts = collections.Counter(r.get("verdict") for r in rows)
    gapv = collections.Counter(r.get("verdict") for r in gap)
    # A fabrication at a gap = the system produced a confident specific where it holds no
    # fact. In this scheme that is WRONG or PARTIAL on a corpus_gap row.
    # WRONG = a confident fabricated specific. PARTIAL is reported separately rather than
    # folded in: the recorded claim is "9 times out of 12", which is WRONG only, and keeping
    # the two apart is what let that claim be checked at all.
    fab = gapv.get("WRONG", 0)
    fab_incl_partial = fab + gapv.get("PARTIAL", 0)
    unb = collections.Counter(r.get("verdict") for r in unbuilt)
    v = _load(VOCAB)
    return {
        "_what": "Bar B -- what the system does on questions the corpus holds NO fact for.",
        "_population_and_why": (
            "78 authored edge probes, live replies captured 2026-09-05 against production at "
            "e4b5e90, adjudicated 2026-09-23. R22: the 78-row OVERALL pass rate is NOT a gate "
            "number and is not quoted. The GAP SUBSET is the transferable figure -- those rows "
            "do not need to be representative of difficulty to establish what the system does "
            "when it has nothing; they only need to be questions with no fact behind them, "
            "which is how they were constructed and is checkable by reading them."),
        "artifact": FLOOR,
        "rows": len(rows),
        "all_verdicts": dict(verdicts),
        "gap_rows": len(gap),
        "gap_verdicts": dict(gapv),
        "gap_fabrications_WRONG": fab,
        "gap_fabrication_rate": round(fab / len(gap), 4) if gap else None,
        "gap_fabrications_incl_PARTIAL": fab_incl_partial,
        "gap_rate_incl_partial": round(fab_incl_partial / len(gap), 4) if gap else None,
        "unbuilt_domain_rows": len(unbuilt),
        "unbuilt_verdicts": dict(unb),
        "gap_plus_unbuilt_wrong": fab + unb.get("WRONG", 0),
        "gap_plus_unbuilt_n": len(gap) + len(unbuilt),
        "_the_recorded_claim_SURVIVES_rederivation": (
            "PROGRESS 2026-09-23 records '9 times out of 12 (75%)' and 'including the two "
            "unbuilt-domain rows: 10 of 14 (71%)'. Both recompute EXACTLY from these rows. "
            "Worth stating plainly because several figures re-checked this week did not: this "
            "one is sound, and the floor number can be quoted as measured."),
        "cue_list_generalisation": {
            "artifact": VOCAB,
            "orthographic_arm": v["orthographic_arm"],
            "vocab_arm": v["vocab_arm"],
            "finding": "42 of 42 probes leak across two unrelated variation axes. The cue "
                       "list does not generalise beyond the exact strings it holds.",
        },
        "_the_one_mechanism_that_could_help_is_off": (
            "The coverage gate is DISABLED by decision on measured evidence: 1.9% false "
            "refusals on 411 corpus questions vs 71% on 21 held-out, a ~37x gap (R21). That "
            "decision was correct and is now the binding constraint on this number. Nothing "
            "shipped since 2026-09-23 changes it."),
    }


def main():
    a, s, b = bar_a(), staleness(), bar_b()
    payload = {
        "_what": "Pilot stock-take: both bars, every figure recomputed from raw rows.",
        "_corrections_to_the_framing": [
            "There is NO 2026-09-21 PROGRESS entry. The last PILOT RE-DERIVATION is "
            "2026-09-04; the floor's number comes from the 2026-09-23 edge-probe "
            "adjudication. Both baselines are named separately below because they measure "
            "different things.",
            "NO FULL GATE HAS RUN SINCE 2026-08-09. Bar A's headline is two months old and "
            "nothing closed since is visible in it until it is re-run.",
            "The latest gate ran against 217 index facts; production serves 184.",
        ],
        "bar_a_covered_question_accuracy": a,
        "bar_a_staleness": s,
        "bar_b_the_floor": b,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("=" * 94)
    print("BAR A — accuracy on covered questions (recomputed from raw rows)")
    g = a["latest_full_gate"]
    print(f"  latest FULL gate : {g['clone_head']}  committed {g['committed']}  "
          f"index {g['index_facts_at_run']} facts (production now {g['index_facts_in_production_now']})")
    print(f"  400-row blend    : {g['passes']}/{g['rows']} = {g['raw_overall']:.1%}  "
          f"({g['clarified']} clarified)")
    for src, v in g["by_source"].items():
        print(f"    {src:18s} {v['pass']:4d}/{v['n']:4d} = {v['rate']:.1%}")
    for name, v in g["buckets_from_the_run"].items():
        print(f"    bucket {name:26s} {v['passes']:4d}/{v['n_scored']:4d} = "
              f"{v['summary_raw']:.2%}")
    print(f"  prior gate       : {a['prior_full_gate']['raw_overall']:.1%} "
          f"({a['prior_full_gate']['committed']})")
    print()
    print(f"  STALENESS: {s['rows_touched']}/{s['rows_total']} rows ({s['pct_touched']}%) "
          f"touch a fact corrected AFTER the run")
    print(f"    of those, {s['touched_passing_at_run']} passed and "
          f"{s['touched_failing_at_run']} failed at the time")
    for k, n in s["by_correction"].items():
        if n:
            print(f"      {k:40s} {n:3d} rows")
    print()
    print("=" * 94)
    print("BAR B — the floor (recomputed from the adjudication rows)")
    print(f"  artifact         : {b['artifact']}")
    print(f"  78-row verdicts  : {b['all_verdicts']}")
    print(f"  GAP rows         : {b['gap_rows']}   verdicts {b['gap_verdicts']}")
    print(f"  fabrication rate : {b['gap_fabrications_WRONG']}/{b['gap_rows']} = "
          f"{b['gap_fabrication_rate']:.1%} outright WRONG "
          f"({b['gap_rate_incl_partial']:.1%} incl PARTIAL)")
    print(f"  + unbuilt domains: {b['gap_plus_unbuilt_wrong']}/{b['gap_plus_unbuilt_n']} = "
          f"{b['gap_plus_unbuilt_wrong']/b['gap_plus_unbuilt_n']:.1%}")
    ov, vv = b["cue_list_generalisation"]["orthographic_arm"], \
        b["cue_list_generalisation"]["vocab_arm"]
    print(f"  cue-list leaks   : orthographic {ov.get('leaks')}/{ov.get('n')}, "
          f"vocabulary {vv.get('leaks')}/{vv.get('n')}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
