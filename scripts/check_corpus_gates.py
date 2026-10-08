#!/usr/bin/env python3
"""THE CORPUS GATES, RUN BY ONE THING SO THE HOOK AND THE SUITE CANNOT DISAGREE (2026-10-08).

WHY THIS EXISTS. Measured 2026-10-08:

    validate_dataset.py   ENFORCED  — tests assert the real corpus passes; pre-push runs
                                      pytest. Corpus clean: 1714 pairs / 0 errors.
    check_locked_facts.py NOT       — imported by two tests, NEITHER of which runs it over
                                      the corpus. 48 flag lines were live at HEAD.
    check_sources.py      NOT       — ZERO test references.
    check_eval_split.py   NOT       — ZERO test references.

`.githooks/` held ONLY `pre-push`; there was NO pre-commit hook at all. "Do NOT save if exit
code 1" and "only commit if all 4 return 0" are instructions to a reader, enforced by
nothing. THE DIFFERENCE BETWEEN THE CLEAN GATE AND THE DIRTY ONES WAS WIRING, NOT DILIGENCE.

⛔ WHY A RATCHET AND NOT "MUST BE ZERO", which is the decision that makes this adoptable.
Eighteen pairs across the corpus still flag, and they are REAL (OSHA/WCF threshold
conflations, e.g. a row giving OSHA registration a 10-employee floor, which is SDL's
threshold). A hook that blocks every commit touching those files would be bypassed within a
day — and a bypassed hook is worse than none, because it also removes the appetite for the
next one. So the rule is SHRINK-ONLY per file: a commit may not make a file worse, and
fixing rows ratchets the ceiling down.

That is not a softening. It is the same reasoning that made the fact-guardian itself stop
being run: a gate that fails continuously stops carrying information. The ratchet makes
every one of those 18 visible, counted, and impossible to add to.

⛔ ONE IMPLEMENTATION, TWO CALLERS. The pre-commit hook and tests/test_corpus_gates_wired.py
both invoke THIS file. The 2026-10-06 dry run passed a package the real run refused because
it re-implemented the checks its author remembered; a hook that re-implemented these would
drift from the suite the same way, and the drift would be invisible because both would be
green.

Usage:
    python scripts/check_corpus_gates.py                 # whole corpus
    python scripts/check_corpus_gates.py --files a b c   # just these (the hook's mode)
    python scripts/check_corpus_gates.py --update-baseline
Exit: 0 = no file exceeds its baseline; 1 = at least one got worse; 2 = cannot evaluate.
"""
import argparse
import glob
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BASELINE = os.path.join(HERE, "corpus_gate_baseline.json")

CORPUS_GLOBS = [
    "datasets/tier1a/cleaned_pairs/*.jsonl",
    "datasets/tier1a/sft_shaped_pairs/*.jsonl",
]


def _rel(p):
    return os.path.relpath(p, REPO).replace("\\", "/")


def corpus_files():
    out = []
    for g in CORPUS_GLOBS:
        out.extend(glob.glob(os.path.join(REPO, *g.split("/"))))
    return sorted(_rel(p) for p in out)


def _load(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    cwd = os.getcwd()
    try:
        os.chdir(REPO)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def locked_fact_flags(rel_paths):
    """{path: flagged_pair_count}. Uses check_locked_facts.check_pair directly rather than
    shelling out, so the compile cache is shared across files -- a full-corpus pass went from
    ~40s per file to seconds once patterns stopped being recompiled per pair, and expense is
    how a check ends up not being run."""
    m = _load("_cg_locked", "check_locked_facts.py")
    facts = m.load_locked_facts(os.path.join(REPO, "scripts", "locked_facts.json"))
    out = {}
    for rel in rel_paths:
        full = os.path.join(REPO, *rel.split("/"))
        n = 0
        with open(full, encoding="utf-8") as fh:
            for line in fh:
                if line.strip() and m.check_pair(json.loads(line), facts):
                    n += 1
        out[rel] = n
    return out


def source_violations(rel_paths):
    """{path: violation_count}, via the real CLI so its own whitelist logic is the authority.
    Not re-implemented here for the reason stated at the top of this file."""
    out = {}
    for rel in rel_paths:
        p = subprocess.run(
            [sys.executable, os.path.join(HERE, "check_sources.py"), "--file", rel],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
        n = 0
        for line in (p.stdout or "").splitlines():
            if "source violations" in line:
                try:
                    n = int(line.split("pairs.")[1].split("source")[0].strip())
                except (IndexError, ValueError):
                    n = 0 if "0 source" in line else 1
        out[rel] = n
    return out


def eval_split_ok():
    """check_eval_split has no per-file notion -- it is a whole-corpus invariant (R6: eval
    pairs must not reach training). Pass/fail, no ratchet: unlike the other two it has no
    legacy backlog, so a ceiling would be inventing slack that does not exist."""
    p = subprocess.run([sys.executable, os.path.join(HERE, "check_eval_split.py")],
                       cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout or "")[-400:]


def load_baseline():
    if not os.path.exists(BASELINE):
        return None
    with open(BASELINE, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None,
                    help="repo-relative corpus files; default = the whole corpus")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    targets = [f for f in (args.files or corpus_files())
               if f in set(corpus_files())]
    if args.files is not None and not targets:
        if not args.quiet:
            print("[corpus-gates] no corpus files among the given paths — nothing to check")
        return 0

    lf = locked_fact_flags(targets)
    sv = source_violations(targets)

    if args.update_baseline:
        base = load_baseline() or {"_what": "", "locked_facts": {}, "sources": {}}
        base["_what"] = (
            "Per-file ceilings for the corpus gates. SHRINK-ONLY: a commit may not make a "
            "file worse. These are not targets -- every count above zero is a real defect "
            "awaiting adjudication. Lower a ceiling in the same commit that fixes rows.")
        base["_why_not_zero"] = (
            "18 pairs still flag against locked facts (OSHA/WCF threshold conflations) and 1 "
            "source violation remains (a dead nssf.or.tz domain). A hook demanding zero would "
            "block every commit touching those files and be bypassed within a day -- and a "
            "bypassed hook is worse than none, because it also removes the appetite for the "
            "next one.")
        base["locked_facts"].update(lf)
        base["sources"].update(sv)
        with open(BASELINE, "w", encoding="utf-8") as fh:
            json.dump(base, fh, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[corpus-gates] baseline updated for {len(targets)} file(s) -> {_rel(BASELINE)}")
        return 0

    base = load_baseline()
    if base is None:
        print("[corpus-gates] FAIL — no baseline file. Cannot evaluate, which is NOT a pass.")
        return 2

    worse = []
    for rel in targets:
        for gate, got, ceil in (
                ("locked_facts", lf[rel], base["locked_facts"].get(rel)),
                ("sources", sv[rel], base["sources"].get(rel))):
            if ceil is None:
                worse.append((rel, gate, got, "NO BASELINE — a new corpus file must be "
                                              "added to the baseline deliberately"))
            elif got > ceil:
                worse.append((rel, gate, got, f"ceiling {ceil}"))

    split_ok, split_tail = eval_split_ok()

    if not args.quiet or worse or not split_ok:
        for rel in targets:
            l, s = lf[rel], sv[rel]
            bl, bs = base["locked_facts"].get(rel), base["sources"].get(rel)
            flag = "  <-- WORSE" if (bl is not None and l > bl) or \
                                    (bs is not None and s > bs) else ""
            if not args.quiet or flag:
                print(f"  locked_facts {l:3d}/{bl}  sources {s}/{bs}  {rel}{flag}")
    if not split_ok:
        print("[corpus-gates] FAIL — check_eval_split:")
        print(split_tail)
    for rel, gate, got, why in worse:
        print(f"[corpus-gates] FAIL — {rel}: {gate} rose to {got} ({why})")

    if worse or not split_ok:
        print("\n[corpus-gates] BLOCKED. These gates were unenforced until 2026-10-08; the "
              "ratchet is shrink-only, so this means the change ADDED a violation. Fix it, or "
              "if a ceiling is genuinely being lowered run --update-baseline and say why in "
              "the commit.")
        return 1
    if not args.quiet:
        print(f"[corpus-gates] OK — {len(targets)} file(s), none worse than baseline; "
              f"eval split clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
