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


def check(repo_dir=".", is_ancestor_fn=None, last_touch_fn=None, commits_since_fn=None):
    """Pure-ish core: every git call is routed through the three injectable functions so
    this can be exercised against a synthetic commit graph, not just live git state (R26 --
    a control is not demonstrated until it has been made to both fire and pass clean).

    Returns (ok, report) where report has:
      input_shas / artifact_shas : {path: sha or None}
      artifacts_diverged         : bool -- artifact files don't share one last-touch commit
      stale_inputs                : {input_path: {artifact_path: [commit summaries]}}
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
        }

    distinct_artifact_shas = set(artifact_shas.values())
    artifacts_diverged = len(distinct_artifact_shas) > 1

    stale_inputs = {}
    for in_path, in_sha in input_shas.items():
        for art_path, art_sha in artifact_shas.items():
            if not is_ancestor_fn(in_sha, art_sha):
                stale_inputs.setdefault(in_path, {})[art_path] = commits_since_fn(
                    art_sha, in_sha, in_path)

    ok = not artifacts_diverged and not stale_inputs
    return ok, {
        "input_shas": input_shas, "artifact_shas": artifact_shas,
        "missing_inputs": [], "missing_artifacts": [],
        "artifacts_diverged": artifacts_diverged, "stale_inputs": stale_inputs,
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

    if report["stale_inputs"]:
        print(f"FAIL -- {len(report['stale_inputs'])} input file(s) changed AFTER the "
              f"deployed index was last built. The deployed RAG index does not reflect:")
        for in_path, by_artifact in report["stale_inputs"].items():
            any_commits = next(iter(by_artifact.values()))
            print(f"\n  {in_path}: {len(any_commits)} commit(s) not in the deployed index:")
            for line in any_commits:
                print(f"    {line}")
        print(
            "\n  Run kaggle/regenerate_rag_e5.py on Kaggle (per CLAUDE.md R15), fetch the "
            "resulting rag_embeddings.npy / rag_facts_text.json from the HF dataset repo, "
            "commit them to BOTH kaggle/ and chike-inference/, redeploy Modal, then re-run "
            "this check.")

    if ok:
        print("FRESH -- the deployed RAG index's build commit contains every later "
              "change to the facts it is built from.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
