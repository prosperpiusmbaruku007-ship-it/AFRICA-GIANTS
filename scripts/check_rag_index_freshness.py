#!/usr/bin/env python3
"""
RAG INDEX FRESHNESS CHECK -- is the deployed retrieval index built from the CURRENT
locked_facts.json, or from a stale one?

Usage: python scripts/check_rag_index_freshness.py
Exit code: 0 = the deployed index's regen commit contains every later fact/build-logic
           edit, 1 = it does not (facts changed after the index was last built)

WHY THIS EXISTS (2026-09-03). check_facts_index_sync.py (2026-08-17) answers "is every
locked fact REACHABLE in the index content on disk" -- a structural/key-matching question.
It says nothing about TIME: it would report CLEAN even if every reachable row's VALUE is
six edits stale, because it only checks that a key's figure appears somewhere in the index
text, not when that text was last regenerated relative to the fact that produced it.

That exact gap went unnoticed for a week. The 2026-09-02/03 verification arc ran 24 commits
against scripts/locked_facts.json -- including reverting vat_deferment_minimum_value off a
fabricated-lineage 20,000,000 back to the correct 10,000,000, and a4246fd (2026-08-29)
correcting efd_threshold_tzs_11m off an invented threshold entirely, a fact this project's
own traffic notes describe as served ~111 times. Neither correction reached the deployed
index: the last regen (b017aac, 2026-08-26) predates both by three and seven days. Nothing
caught this until someone asked -- the same shape as the sft/ quarantine gap (a real
divergence between what the record says and what the artifact actually contains, closed
only by a person noticing rather than a standing check). This script is that standing check.

WHAT IT CHECKS. For each file in FRESHNESS_INPUTS (the fact data itself, plus the module
that turns facts into embedded text -- a logic change is exactly as capable of making the
deployed index wrong as a data change), find the most recent commit that touched it. For
each file in DEPLOYED_ARTIFACTS, find the commit that last updated it. The check passes only
if EVERY input's last-touch commit is an ancestor of (or equal to) EVERY artifact's last-
touch commit -- i.e. the artifact was built at or after every input change that could affect
it. It also requires all artifact files to share the same last-touch commit: kaggle/ and
chike-inference/ carry independent git history for the same logical index, and R15's own
atomic-upload rationale (both HF files land in one commit or neither does) is exactly the
property that matters here too -- if the two directories' copies were committed separately,
one could silently be staler than the other with nothing to say so.

This does NOT replace check_facts_index_sync.py. That check is content-shaped (is this KEY
retrievable at all); this one is time-shaped (is the retrievable content current). A repo
can pass one and fail the other, and both are real defects.
"""
import argparse
import subprocess
import sys

FRESHNESS_INPUTS = [
    "scripts/locked_facts.json",
    "scripts/precompute_rag_embeddings.py",
]
DEPLOYED_ARTIFACTS = [
    "kaggle/rag_embeddings.npy",
    "kaggle/rag_facts_text.json",
    "chike-inference/rag_embeddings.npy",
    "chike-inference/rag_facts_text.json",
]


# ─── CONTENT ADDRESSING, ADDED 2026-10-08 ────────────────────────────────────────
# ⛔ WHY THE SHA LIMB ALONE WAS THE WRONG INSTRUMENT, and it is the same lesson /health
# learned about counts. The SHA limb asks "which FILE was touched since the artifacts were
# built". On 2026-10-08 a `wrong_patterns` fix on `rent_wht_rate` -- a field authored for
# matching GENERATED output, which `build_fact_texts()` does not read at all -- turned this
# check red while `build_fact_texts()` produced 184 rows BYTE-IDENTICAL to the served
# index. The check was reporting staleness that did not exist.
#
# Leaving it red was the wrong call for a reason worth stating: a check that is red when
# nothing is wrong teaches the reflex of overriding it, and that reflex is spent the one
# time it is red because something IS wrong. The fix is not to silence it and not to
# special-case a field name -- a field allowlist would be a second, divergent copy of the
# builder's own field selection, which is how two implementations of one rule start
# disagreeing. The fix is to ask the question the check actually cares about: IS THE SERVED
# TEXT WHAT THIS TREE BUILDS?
#
# So the verdict is now content-addressed: rebuild the fact texts and compare. A
# `wrong_patterns` edit leaves it GREEN because nothing served changed; a fact edit, a
# builder change, or a row reordering turns it RED because something did. The SHA limb is
# KEPT, demoted to provenance -- it still answers "which commits are implicated", which is
# what a reader needs once the content check is red, and it still catches the two artifact
# directories being committed separately.
def built_fact_texts(repo_dir="."):
    """(texts, error). Imported from the real builder, never re-implemented.

    Returns (None, reason) rather than raising, and the caller treats that as NOT FRESH:
    cannot-evaluate is not passed -- the same rule that made run_eval.py's empty-corpus
    path exit 2 instead of 0.
    """
    import importlib.util
    import os
    path = os.path.join(repo_dir, "scripts", "precompute_rag_embeddings.py")
    if not os.path.exists(path):
        return None, f"builder not found at {path}"
    cwd = os.getcwd()
    try:
        os.chdir(repo_dir)
        spec = importlib.util.spec_from_file_location(
            "_freshness_precompute", os.path.join("scripts",
                                                  "precompute_rag_embeddings.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_freshness_precompute"] = mod
        spec.loader.exec_module(mod)
        texts, _keys, _dropped = mod.build_fact_texts()
        return list(texts), None
    except Exception as exc:                      # noqa: BLE001 - reported, never swallowed
        return None, f"{type(exc).__name__}: {str(exc)[:200]}"
    finally:
        os.chdir(cwd)


def _served_texts(repo_dir):
    import json
    import os
    out = {}
    for rel in [p for p in DEPLOYED_ARTIFACTS if p.endswith("rag_facts_text.json")]:
        full = os.path.join(repo_dir, *rel.split("/"))
        if not os.path.exists(full):
            out[rel] = None
            continue
        with open(full, encoding="utf-8") as fh:
            out[rel] = json.load(fh)
    return out


def _embedding_rows(repo_dir):
    import os
    out = {}
    for rel in [p for p in DEPLOYED_ARTIFACTS if p.endswith(".npy")]:
        full = os.path.join(repo_dir, *rel.split("/"))
        if not os.path.exists(full):
            out[rel] = None
            continue
        try:
            import numpy as np
            out[rel] = int(np.load(full, mmap_mode="r").shape[0])
        except Exception:
            out[rel] = None
    return out


def _run(args, repo_dir):
    out = subprocess.run(args, cwd=repo_dir, capture_output=True, text=True, timeout=30)
    return out.stdout.strip(), out.returncode


def _last_touch_sha(path, repo_dir):
    """Most recent commit SHA touching `path`, or None if the file has no history here
    (e.g. it has never been committed -- a distinct failure from 'stale')."""
    out, rc = _run(["git", "log", "-1", "--format=%H", "--", path], repo_dir)
    if rc != 0 or not out:
        return None
    return out


def _is_ancestor(older_sha, newer_sha, repo_dir):
    """True if older_sha is an ancestor of (or equal to) newer_sha -- i.e. newer_sha's
    tree already contains whatever older_sha changed."""
    if older_sha == newer_sha:
        return True
    _, rc = _run(["git", "merge-base", "--is-ancestor", older_sha, newer_sha], repo_dir)
    return rc == 0


def _commits_since(old_sha, new_sha, path, repo_dir):
    """One-line summaries of commits touching `path` in (old_sha, new_sha] -- the
    concrete list of what the stale index is missing, not just a count."""
    out, rc = _run(
        ["git", "log", "--format=%h %ci %s", f"{old_sha}..{new_sha}", "--", path],
        repo_dir)
    return out.splitlines() if rc == 0 and out else []


def check(repo_dir=".", is_ancestor_fn=None, last_touch_fn=None, commits_since_fn=None,
          content_fn=None):
    """Pure-ish core: every git call is routed through the three injectable functions so
    this can be exercised against a synthetic commit graph, not just live git state (R26 --
    a control is not demonstrated until it has been made to both fire and pass clean).

    Returns (ok, report) where report has:
      input_shas / artifact_shas : {path: sha or None}
      artifacts_diverged         : bool -- artifact files don't share one last-touch commit
      stale_inputs               : {input_path: {artifact_path: [commit summaries]}}
                                   -- PROVENANCE ONLY since 2026-10-08; see below
      content_matches            : bool | None -- DECIDES THE VERDICT. Does
                                   build_fact_texts() over this tree equal the served
                                   rag_facts_text.json, row for row, in BOTH deploy dirs?
      diverging                  : {artifact: {reason, rows:[{index,built,served}]}}
      embedding_rows_match       : bool -- npy row count == len(texts) in both dirs
      content_build_error        : str | None -- if set, `ok` is False, never True
    """
    is_ancestor_fn = is_ancestor_fn or (lambda a, b: _is_ancestor(a, b, repo_dir))
    last_touch_fn = last_touch_fn or (lambda p: _last_touch_sha(p, repo_dir))
    commits_since_fn = commits_since_fn or (lambda a, b, p: _commits_since(a, b, p, repo_dir))

    input_shas = {p: last_touch_fn(p) for p in FRESHNESS_INPUTS}
    artifact_shas = {p: last_touch_fn(p) for p in DEPLOYED_ARTIFACTS}

    missing_inputs = [p for p, s in input_shas.items() if s is None]
    missing_artifacts = [p for p, s in artifact_shas.items() if s is None]
    if missing_inputs or missing_artifacts:
        return False, {
            "input_shas": input_shas, "artifact_shas": artifact_shas,
            "missing_inputs": missing_inputs, "missing_artifacts": missing_artifacts,
            "artifacts_diverged": False, "stale_inputs": {},
            "content_checked": False, "content_build_error": None,
            "content_matches": None, "built_rows": None, "diverging": {},
            "embedding_rows": {}, "embedding_rows_match": False,
        }

    distinct_artifact_shas = set(artifact_shas.values())
    artifacts_diverged = len(distinct_artifact_shas) > 1

    stale_inputs = {}
    for in_path, in_sha in input_shas.items():
        for art_path, art_sha in artifact_shas.items():
            if not is_ancestor_fn(in_sha, art_sha):
                stale_inputs.setdefault(in_path, {})[art_path] = commits_since_fn(
                    art_sha, in_sha, in_path)

    # ── THE CONTENT LIMB, WHICH NOW DECIDES THE VERDICT ──────────────────────────
    # `content_fn` is injectable for the same reason the git calls are: a control must be
    # exercisable against a synthetic state, in BOTH directions, rather than only against
    # whatever the live tree happens to be (R26).
    content_fn = content_fn or (lambda: built_fact_texts(repo_dir))
    built, build_error = content_fn()
    served = _served_texts(repo_dir)
    emb_rows = _embedding_rows(repo_dir)

    diverging = {}
    content_matches = None
    if built is not None:
        content_matches = True
        for rel, rows in served.items():
            if rows is None:
                diverging[rel] = {"reason": "served text file missing"}
                content_matches = False
                continue
            if len(rows) != len(built):
                diverging[rel] = {"reason": "row count differs",
                                  "built_rows": len(built), "served_rows": len(rows)}
                content_matches = False
                continue
            bad = [{"index": i, "built": built[i][:160], "served": rows[i][:160]}
                   for i in range(len(rows)) if rows[i] != built[i]]
            if bad:
                diverging[rel] = {"reason": f"{len(bad)} row(s) differ", "rows": bad[:8]}
                content_matches = False

    # The embeddings cannot be rebuilt here (the e5 model is not run in this check), so this
    # limb verifies the one property that IS checkable locally and that a content change
    # would break: the embedding matrix has one row per fact text. A row-count mismatch
    # between the npy and the json is a half-shipped index, which is precisely the state the
    # fail-loud contract exists to refuse.
    embedding_rows_match = True
    if built is not None:
        for rel, n in emb_rows.items():
            if n is None or n != len(built):
                embedding_rows_match = False

    # ⛔ CANNOT-EVALUATE IS NOT PASSED. If the builder could not be imported or run, `ok` is
    # False with a distinct reason, never True by omission -- the same rule that made
    # run_eval.py's empty-corpus path exit 2 rather than 0.
    ok = (not artifacts_diverged
          and build_error is None
          and content_matches is True
          and embedding_rows_match)
    return ok, {
        "input_shas": input_shas, "artifact_shas": artifact_shas,
        "missing_inputs": [], "missing_artifacts": [],
        "artifacts_diverged": artifacts_diverged,
        # PROVENANCE, no longer decisive: which commits are implicated once content is red.
        "stale_inputs": stale_inputs,
        "_stale_inputs_is_provenance_only": (
            "which inputs moved since the artifacts were committed. INFORMATIONAL: it does "
            "not decide `ok`, because a field the builder never reads (e.g. wrong_patterns) "
            "can move an input without changing a single served row -- measured 2026-10-08."),
        "content_checked": built is not None,
        "content_build_error": build_error,
        "content_matches": content_matches,
        "built_rows": None if built is None else len(built),
        "diverging": diverging,
        "embedding_rows": emb_rows,
        "embedding_rows_match": embedding_rows_match,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-dir", default=".")
    args = ap.parse_args()

    ok, report = check(repo_dir=args.repo_dir)

    if report["missing_inputs"] or report["missing_artifacts"]:
        print("FAIL -- could not resolve git history for:")
        for p in report["missing_inputs"] + report["missing_artifacts"]:
            print(f"    {p}")
        return 1

    print("last commit touching each freshness input:")
    for p, s in report["input_shas"].items():
        print(f"    {s[:7]}  {p}")
    print("last commit touching each deployed artifact:")
    for p, s in report["artifact_shas"].items():
        print(f"    {s[:7]}  {p}")
    print()

    if report["artifacts_diverged"]:
        print("FAIL -- deployed artifact files do not share one last-touch commit "
              "(kaggle/ and chike-inference/ copies have drifted apart).")

    # ── THE CONTENT VERDICT LEADS, because it is the one that decides. The previous
    #    reporting printed the SHA limb as "FAIL" and then "FRESH" in the same breath --
    #    contradictory output with exit 0, which is worse than either verdict alone.
    if report["content_build_error"]:
        print("FAIL -- could not rebuild the fact texts, so freshness CANNOT BE EVALUATED. "
              "That is not a pass.")
        print(f"    {report['content_build_error']}")
    elif report["content_matches"] is False:
        print("FAIL -- the SERVED index text is not what this tree builds. "
              f"build_fact_texts() produced {report['built_rows']} rows:")
        for rel, info in report["diverging"].items():
            print(f"\n  {rel}: {info.get('reason')}")
            for row in info.get("rows", []):
                print(f"    row {row['index']}")
                print(f"      built : {row['built']}")
                print(f"      served: {row['served']}")
        print(
            "\n  Run kaggle/regenerate_rag_e5.py on Kaggle (per CLAUDE.md R15), fetch the "
            "resulting rag_embeddings.npy / rag_facts_text.json from the HF dataset repo, "
            "commit them to BOTH kaggle/ and chike-inference/, redeploy Modal, then re-run "
            "this check.")
    elif not report["embedding_rows_match"]:
        print("FAIL -- the embedding matrix does not have one row per fact text. A "
              "half-shipped index:")
        print(f"    texts: {report['built_rows']}   embeddings: {report['embedding_rows']}")

    # PROVENANCE, printed whether or not it is decisive, and LABELLED so it cannot be read
    # as a verdict. On 2026-10-08 this limb was red while the content was byte-identical:
    # a `wrong_patterns` edit moved locked_facts.json without changing a single served row.
    if report["stale_inputs"]:
        label = ("PROVENANCE (not a failure)" if ok else "PROVENANCE -- implicated commits")
        print(f"\n{label}: {len(report['stale_inputs'])} input file(s) changed after the "
              f"artifacts were committed:")
        for in_path, by_artifact in report["stale_inputs"].items():
            any_commits = next(iter(by_artifact.values()))
            print(f"  {in_path}: {len(any_commits)} commit(s)")
            for line in any_commits:
                print(f"    {line}")
        if ok:
            print("  -> and NONE of them changed a served row: build_fact_texts() over this "
                  "tree is byte-identical to the deployed text. A field the builder never "
                  "reads (e.g. wrong_patterns) can move an input without changing the index.")

    if ok:
        print(f"\nFRESH -- the deployed index text is BYTE-IDENTICAL to what this tree "
              f"builds ({report['built_rows']} rows), and the embedding matrix matches it "
              f"row for row.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
