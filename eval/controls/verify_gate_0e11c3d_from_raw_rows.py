# -*- coding: utf-8 -*-
"""RE-DERIVE EVERY HEADLINE OF THE 2026-10-09 GATE FROM ITS 400 RAW ROWS.

⛔ WHY THIS EXISTS RATHER THAN READING `summary`. The artifact ships its own summary block,
computed by the same process that produced the rows. Reading it back is not verification — it
is quotation. Three separate figures this project has published were wrong while their summary
block was internally consistent (the 50/400 staleness count, the 330/400 blend, the first Bar B
extraction), so the headline is recomputed here from `rows` and then COMPARED to `summary`, with
any disagreement reported as a finding rather than smoothed.

⛔ THE DEFINITIONS ARE LIFTED OUT OF THE PACKAGE, NOT RE-IMPLEMENTED. `outcome`, `bars`,
`reliable_only` and `BUCKETS` are extracted from kaggle/eval_gate_production_2026_10_09.py by
source. A harness that re-implements the real run's scoring is not a harness of that run — the
2026-10-07 dry run reported SAFE TO RUN against a regen that aborted, because it hand-wrote the
assertions it was supposed to be checking. So the only thing this file supplies independently is
the POPULATION (the artifact's rows) and the ARITHMETIC.

Usage:  python eval/controls/verify_gate_0e11c3d_from_raw_rows.py
Artifact: eval/results/gate_0e11c3d_verification.json
Exit 0 all figures reproduce · 1 a disagreement · 2 could not be exercised (NOT a pass).
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GATE = os.path.join(REPO, "eval", "results", "gate_production_0e11c3d.json")
PKG = os.path.join(REPO, "kaggle", "eval_gate_production_2026_10_09.py")
BASELINE = os.path.join(REPO, "eval", "results", "gate_phase_d_paired_1476caa.json")
OUT = os.path.join(REPO, "eval", "results", "gate_0e11c3d_verification.json")

EXPECTED_SHA256_PREFIX = "914aef328bd315aa"

# The figures as reported to me, quoted here so the comparison is explicit and a mismatch is
# visible rather than absorbed. Re-derived, never assumed (standing instruction 2026-10-04).
CLAIMED = {
    "all_400_A2_rate": 0.823,
    "fact_path_A2_raw": 0.852,
    "fact_path_A2_reliable": 0.858,
    "attributable_pts": 0.3,
    "total_A2_delta_pts": 0.5,
    "key_pts_eval_355": 0.26,
    "judge_augmented_rate": 0.819,
    "false_pass_candidates": 17,
}


def _scoring_helpers():
    """outcome / bars / reliable_only, exec'd verbatim out of the package."""
    src = io.open(PKG, encoding="utf-8").read()
    start = src.index("def outcome(r):")
    end = src.index("BUCKETS = {")
    ns = {"Counter": __import__("collections").Counter}
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    for need in ("outcome", "bars", "reliable_only"):
        assert need in ns, f"{need} not found in the package — this harness is stale"
    return ns["outcome"], ns["bars"], ns["reliable_only"]


def _buckets(rows):
    """BUCKETS, also lifted by source so a bucket definition cannot drift silently."""
    src = io.open(PKG, encoding="utf-8").read()
    start = src.index("BUCKETS = {")
    end = src.index("# The baseline, read back out of the committed artifact")
    ns = {"rows": rows}
    exec(compile(src[start:end], PKG, "exec"), ns)      # noqa: S102
    return ns["BUCKETS"]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # R40: inside main()
    except Exception:                                                # noqa: BLE001
        pass

    if not os.path.isfile(GATE):
        print(f"[FATAL] {GATE} not present — nothing to verify. Exit 2 is NOT a pass.")
        return 2

    import hashlib
    sha = hashlib.sha256(open(GATE, "rb").read()).hexdigest()
    d = json.load(io.open(GATE, encoding="utf-8"))
    rows = d["rows"]
    outcome, bars, reliable_only = _scoring_helpers()
    buckets = _buckets(rows)

    findings, checks = [], []

    def check(name, got, want, tol=0.0, note=""):
        ok = (abs(got - want) <= tol) if isinstance(got, float) else (got == want)
        checks.append({"check": name, "got": got, "expected": want, "ok": ok, "note": note})
        if not ok:
            findings.append(f"{name}: re-derived {got!r}, reported/expected {want!r}. {note}")
        return ok

    # ── PROVENANCE ──────────────────────────────────────────────────────────────────────
    check("sha256 prefix", sha[:16], EXPECTED_SHA256_PREFIX)
    check("complete flag", d["complete"], True)
    check("rows present", len(rows), 400)
    check("rows_measured == len(rows)", d["rows_measured"], len(rows))
    check("index_facts", d["index_facts"], 184)
    check("clone_head", d["clone_head"], "0e11c3d")
    check("unique ids", len({r["id"] for r in rows}), 400)
    check("rows with an error", sum(1 for r in rows if r["error"]), 0,
          note="a row that errored is not a measured row")

    # ── THE PARTITION MUST BE EXHAUSTIVE BEFORE ANY RATE MEANS ANYTHING ─────────────────
    from collections import Counter
    oc = Counter(outcome(r) for r in rows)
    check("partition sums to 400", sum(oc.values()), 400)
    check("no unexpected outcome", sorted(oc) and set(oc) <= {"RIGHT", "WRONG", "NO_ANSWER",
                                                              "ERROR"}, True)

    # ── BAR A, RECOMPUTED ───────────────────────────────────────────────────────────────
    derived = {}
    for name, bucket in buckets.items():
        derived[name] = {"n": len(bucket), "raw": bars(bucket),
                         "reliable": bars(reliable_only(bucket))}

    a = derived["ALL_400"]["raw"]
    fp_raw = derived["fact_path_190"]["raw"]
    fp_rel = derived["fact_path_190"]["reliable"]

    check("ALL_400 A2 rate", round(a["A2_rate"], 4), CLAIMED["all_400_A2_rate"], tol=0.0005,
          note="the in-corpus right-answer rate, OOC excluded")
    # tol 0.001: the reported figures are quoted to one decimal place as PERCENTAGES
    # (85.2%), so 0.85246 and 0.852 are the same claim. My first draft compared round(x, 4)
    # against a 3dp constant and reported a MISMATCH on agreement — a harness that cries wolf
    # on rounding trains its reader to skim its output, which is how a real mismatch gets
    # missed.
    check("fact_path A2 raw", round(fp_raw["A2_rate"], 4), CLAIMED["fact_path_A2_raw"],
          tol=0.001)
    check("fact_path A2 reliable", round(fp_rel["A2_rate"], 4),
          CLAIMED["fact_path_A2_reliable"], tol=0.001)
    check("ALL_400 clears R7 Gate 1 (>85%)", a["A2_rate"] > 0.85, False,
          note="recorded as a FACT about this run, not as a target")
    check("fact_path clears R7 Gate 1 (>85%)", fp_raw["A2_rate"] > 0.85, True,
          note="ON the line: this is why the 17 false-pass candidates decide it")

    # OOC must be excluded from the denominator, asserted rather than trusted
    n_ooc = sum(1 for r in rows if r["subdomain"] == "out_of_corpus")
    check("OOC rows excluded from in-corpus n", a["n_in_corpus"], 400 - n_ooc,
          note=f"{n_ooc} out_of_corpus rows in the corpus")

    # ── THE BASELINE, RECOMPUTED THE SAME WAY ───────────────────────────────────────────
    bl = json.load(io.open(BASELINE, encoding="utf-8"))
    bl_inc = [r for r in bl["v16_results"] if r["subdomain"] != "out_of_corpus"]
    bl_pass = sum(r["pass"] for r in bl_inc)
    bl_rate = bl_pass / len(bl_inc)
    check("baseline in-corpus n", len(bl_inc), 384)
    check("baseline in-corpus pass", bl_pass, 314)
    check("baseline in-corpus rate", round(bl_rate, 4), 0.8177, tol=0.0005,
          note="81.8% is the like-for-like figure; 330/400=82.5% blends the 16 OOC rows")
    bl_blend = (sum(r["pass"] for r in bl["v16_results"]) / len(bl["v16_results"]))
    check("the 82.5% stocktake figure reproduces as a BLEND", round(bl_blend, 4), 0.825,
          tol=0.0005, note="reproduced only to show it is a different quantity, not a baseline")

    a2_delta = (a["A2_rate"] - bl_rate) * 100
    check("A2 delta vs baseline (pts)", round(a2_delta, 2), CLAIMED["total_A2_delta_pts"],
          tol=0.06)

    # ── THE KEY-CORRECTION ARM ──────────────────────────────────────────────────────────
    dual = [r for r in rows if r["pass_under_baseline_key"] is not None]
    moved = [r for r in dual if r["pass_under_baseline_key"] != r["pass"]]
    kc_delta = sum((1 if r["pass"] else 0) - (1 if r["pass_under_baseline_key"] else 0)
                   for r in dual)
    kc_pts = kc_delta / a["n_in_corpus"] * 100
    # ⛔ 24 ROWS CARRY `pass_under_baseline_key`, NOT 2 — AND THAT IS THE PACKAGE BEING MORE
    # THOROUGH THAN ITS SPEC, NOT A DEFECT. `OLD_KEYS` is built from every finding whose
    # SCORED fields changed (24), while `dual_score_these` names only the 2 that NARROW the
    # key. So all 24 were scored both ways and the other 22 were measured not to move, rather
    # than assumed not to. My first draft asserted the set was exactly the 2 and reported a
    # mismatch on a superset — the check was wrong, not the run.
    declared = set(d["key_corrections"]["dual_scored"])
    check("dual-scored set covers the declared narrowing rows",
          declared <= {r["id"] for r in dual}, True)
    check("rows actually scored under both keys", len(dual), 24,
          note="every row whose scored gold changed, not only the 2 that narrow")
    check("exactly one row's verdict moved on the key alone", [r["id"] for r in moved],
          ["eval_355"], note="so the entire key-correction term is one row of 384")
    check("key-correction pts", round(abs(kc_pts), 2), CLAIMED["key_pts_eval_355"], tol=0.01,
          note="one row of 384 = 0.26 pts")
    attributable = a2_delta - kc_pts
    check("attributable movement (pts)", round(attributable, 1), CLAIMED["attributable_pts"],
          tol=0.06, note="A2 delta minus the key-correction term")

    # ── eval_347, THE PRE-REGISTERED ROW ────────────────────────────────────────────────
    e347 = next(r for r in rows if r["id"] == "eval_347")
    g347 = [g["guard"] for g in e347["guard_interventions"]]
    check("eval_347 outcome", outcome(e347), "NO_ANSWER",
          note="pre-registered: a FAIL THAT IS A WIN")
    check("eval_347 guard", g347, ["D-FIDELITY-7"])
    check("eval_347 does not assert the fabrication", "11,000,000" in e347["generated"], False)

    # ── THE JUDGE OVERLAY ───────────────────────────────────────────────────────────────
    # ⛔ `judge` IS A STRING ('correct' | 'wrong' | 'undetermined' | None), NOT A DICT. My first
    # draft assumed a dict and crashed — recorded because the SILENT version of that mistake is
    # the dangerous one: `.get('verdict','')` on a dict-shaped guess would have matched nothing
    # and reported ZERO false passes, which is the deleting direction (R39) and would have
    # cleared the very question this harness exists to answer.
    jo = d.get("judge_overlay") or {}
    judged = [r for r in rows if r.get("judge")]
    check("judge verdicts are strings", sorted({type(r["judge"]).__name__ for r in judged}),
          ["str"], note="if this ever becomes a dict, the comparisons below go silently empty")
    # ⛔ A REAL ARTIFACT FINDING, KEPT AS A CHECK RATHER THAN SMOOTHED. The top-level
    # `judge_overlay_status` says 'pending' in this artifact while `summary` says 'ran' and the
    # overlay holds 361 graded rows and a $0.21 bill: `_flush` hardcoded 'pending' and runs
    # LAST. Fixed in the package for the next run; asserted here against the TRUTHFUL field so
    # this harness reports the judge's real state either way.
    check("judge ran (summary field, the truthful one)",
          (d.get("summary") or {}).get("judge_overlay_status"), "ran")
    check("top-level status field is the known-stale one", d.get("judge_overlay_status"),
          "pending", note="package fixed after this run; a status that cannot report the "
                          "true state is worse than a missing one")

    # ⛔ TWO POPULATIONS, AND NAMING THEM IS THE WHOLE POINT (R22). A bare "false-pass count"
    # is ambiguous by a factor of two here, and the two answers support different decisions.
    inc = [r for r in rows if r["subdomain"] != "out_of_corpus"]
    fp_all = [r for r in inc if r["pass"] and r["judge"] == "wrong"]
    fp_rel = [r for r in fp_all if r["reliable"]]            # the regex scorer was CONFIDENT
    fp_unrel = [r for r in fp_all if not r["reliable"]]
    check("false-pass candidates (reliable=True)", len(fp_rel),
          CLAIMED["false_pass_candidates"],
          note="THE population that matters: regex PASS on a row it was confident about, "
               "judge says wrong. This is the 17.")
    check("false-pass candidates (all in-corpus)", len(fp_all), 36,
          note="the wider set; the extra 19 sit on reliable=False rows where the regex "
               "verdict was already known weak, so they are a different claim")
    check("the two populations partition", len(fp_rel) + len(fp_unrel), len(fp_all))

    # judge-augmented A2 as the overlay itself computed it, re-derived
    aug = (jo.get("report") or {}).get("judge_augmented") or {}
    check("judge-augmented A2 (overlay)", round(aug.get("acc", 0.0), 4),
          CLAIMED["judge_augmented_rate"], tol=0.0015,
          note="LOWER than raw, which is the direction that matters")
    check("judge-augmented floor (undetermined=fail)", round(
        ((aug.get("floor_undet_fail") or {}).get("acc", 0.0)), 4), 0.8016, tol=0.0015,
        note="the pessimistic bound the overlay also publishes")

    # ── THE GATE 1 QUESTION: the same correction applied to the FACT-PATH bucket ─────────
    fp_bucket = buckets["fact_path_190"]
    fp_inc = [r for r in fp_bucket if r["subdomain"] != "out_of_corpus"]
    ids_rel, ids_all = {r["id"] for r in fp_rel}, {r["id"] for r in fp_all}
    fp_hits_rel = [r["id"] for r in fp_inc if r["id"] in ids_rel]
    fp_hits_all = [r["id"] for r in fp_inc if r["id"] in ids_all]
    base_right = sum(1 for r in fp_inc if outcome(r) == "RIGHT")
    fp_aug_rate = (base_right - len(fp_hits_rel)) / len(fp_inc)
    fp_aug_rate_all = (base_right - len(fp_hits_all)) / len(fp_inc)
    check("fact_path falls BELOW 85% if the reliable-only judge calls hold",
          fp_aug_rate > 0.85, False,
          note=f"85.2% -> {fp_aug_rate:.1%} on {len(fp_hits_rel)} rows. This is why 85.2% "
               f"must not be quoted before the 17 are adjudicated")
    fp_fp = fp_hits_rel

    # ── SUMMARY-vs-ROWS ─────────────────────────────────────────────────────────────────
    s = d.get("summary") or {}
    s_bars = (s.get("bars") or {}).get("ALL_400", {}).get("raw", {})
    if s_bars:
        for k in ("A2_right", "A1_wrong", "no_answer", "n_in_corpus"):
            check(f"summary vs rows: ALL_400.{k}", s_bars.get(k), a[k],
                  note="the shipped summary must equal the re-derivation")

    out = {
        "_what": "every published headline of gate_production_0e11c3d re-derived from its 400 "
                 "raw rows, with the scoring definitions lifted out of the package by source",
        "artifact": os.path.relpath(GATE, REPO), "sha256": sha,
        "gate_commit": d["clone_head"], "index_facts": d["index_facts"],
        "outcome_partition": dict(oc),
        "bar_a": {k: {"n": v["n"],
                      "raw": {kk: v["raw"][kk] for kk in ("n_in_corpus", "A2_right", "A1_wrong",
                                                          "no_answer", "A2_rate", "A1_rate")},
                      "reliable": {kk: v["reliable"][kk] for kk in ("n_in_corpus", "A2_right",
                                                                     "A2_rate")}}
                  for k, v in derived.items()},
        "baseline": {"commit": "1476caa", "in_corpus": f"{bl_pass}/{len(bl_inc)}",
                     "rate": bl_rate, "blend_for_contrast": bl_blend},
        "deltas": {"A2_pts": a2_delta, "key_correction_pts": kc_pts,
                   "attributable_pts": attributable,
                   "moved_by_key_alone": [r["id"] for r in moved]},
        "eval_347": {"outcome": outcome(e347), "guards": g347,
                     "generated": e347["generated"][:400]},
        "judge": {"status": d.get("judge_overlay_status"), "judged": len(judged),
                  "cost_usd": jo.get("usd"), "api_errors": jo.get("api_errors"),
                  "false_pass_reliable_17": sorted(r["id"] for r in fp_rel),
                  "false_pass_all_36": sorted(r["id"] for r in fp_all),
                  "_why_two_populations": (
                      "regex PASS + judge 'wrong'. On reliable=True rows the regex scorer was "
                      "CONFIDENT, so a judge disagreement is a candidate wrong gold or a "
                      "candidate real miss; on reliable=False rows the regex verdict was "
                      "already known weak, so those 19 are a different claim and must not be "
                      "added to the 17 without saying so."),
                  "judge_augmented_A2_all400": aug.get("acc"),
                  "judge_augmented_floor": (aug.get("floor_undet_fail") or {}).get("acc"),
                  "fact_path_A2_raw": fp_raw["A2_rate"],
                  "fact_path_false_passes_reliable": fp_hits_rel,
                  "fact_path_false_passes_all": fp_hits_all,
                  "fact_path_A2_if_reliable_calls_hold": fp_aug_rate,
                  "fact_path_A2_if_all_calls_hold": fp_aug_rate_all,
                  "_the_gate_1_question": (
                      f"fact_path raw is {fp_raw['A2_rate']:.1%} — ON R7's line. If the "
                      f"{len(fp_hits_rel)} reliable-only judge calls in this bucket hold, it "
                      f"becomes {fp_aug_rate:.1%}; if all {len(fp_hits_all)} hold, "
                      f"{fp_aug_rate_all:.1%}. Both are BELOW 85%, so 85.2% must not be quoted "
                      f"as a Gate 1 result before the 17 are adjudicated."),
                  "overlay_caveat": jo.get("caveat"),
                  "overlay_keys": sorted(jo)},
        "serving_identity": d.get("serving_identity"),
        "checks": checks, "findings": findings,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print(f"artifact sha256 {sha[:16]}  complete={d['complete']}  rows={len(rows)}")
    print(f"outcome partition: {dict(oc)}")
    print(f"\n{'check':52s} {'re-derived':>14s} {'reported':>14s}  ok")
    for c in checks:
        print(f"  {c['check']:50s} {str(c['got']):>14s} {str(c['expected']):>14s}  "
              f"{'OK' if c['ok'] else 'MISMATCH'}")
    print(f"\nfact_path raw {fp_raw['A2_rate']:.1%} -> judge-augmented {fp_aug_rate:.1%} "
          f"({len(fp_fp)} false-pass candidates in the bucket: {fp_fp})")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if findings:
        print(f"\n{len(findings)} DISAGREEMENT(S):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("\nALL FIGURES REPRODUCE FROM RAW ROWS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
