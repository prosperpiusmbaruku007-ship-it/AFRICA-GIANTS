# -*- coding: utf-8 -*-
"""DOES ANY MODULE A KAGGLE SCRIPT IMPORTS CONFIGURE GLOBAL I/O AT IMPORT TIME?

⛔ THE DEFECT THIS EXISTS FOR, TWICE NOW, IN TWO DIFFERENT FILES, FOURTEEN DAYS APART.

`sys.stdout.reconfigure(...)` exists on a real `TextIOWrapper` and NOT on Jupyter's
`ipykernel.iostream.OutStream`. At module level in a library, it therefore raises
`AttributeError` the moment a notebook imports the module — before a single line of the
caller's work has run.

  2026-09-24  scripts/check_correction_sync.py  killed a Kaggle RAG regen AFTER every
              blocking check had passed (183 facts, 0 self-retrieval failures, 34 unique
              anchors, rank gate clean) and BEFORE anything was uploaded. The whole run.
  2026-10-09  eval/index_quality/sweep_superseded_values_in_built_index.py  killed the full
              production gate at SECOND 13, in a module-level loader added the previous day.

⛔⛔ AND THE REASON THIS IS A TEST RATHER THAN A FIX IS THE SHAPE OF THE FIRST REMEDY.
The 2026-09-24 fix was correct and thorough: guard the line, move it into `main()`, and then
"AST-sweep the other two modules the regen imports in-process for module-level I/O
configuration of any kind". That sweep was a ONE-TIME ACT over a TWO-MODULE population. It
could not protect a file that did not exist yet, and the file that broke the gate was written
fifteen days later. Prose in a long file is exactly as durable as an unenforced convention —
which this project has already ruled, repeatedly, is not durable at all (R30, R35). So the
population has to be re-derived on every run, and that is all this script does.

⛔⛔⛔ WHY LOCAL GREEN SAYS NOTHING ABOUT THIS CLASS — the part worth remembering.
The gate package ships 23 offline tests specifically so it cannot waste GPU time, and they
all passed, including tests that LOAD this very module and run its self-test. They could not
have caught it. Under pytest `sys.stdout` is a real `TextIOWrapper` (or pytest's own
`CaptureIO`, which subclasses it) and therefore HAS `reconfigure`. So every local test of a
Kaggle-imported module runs in an environment where this failure mode cannot occur, and a
green suite is not evidence of anything here. The only reachable check is STATIC — read the
source, do not run it — which is why this is an AST scan and not an import probe.

THE POPULATION IS THE TRANSITIVE CLOSURE, AND THE DYNAMIC EDGE IS THE WHOLE POINT. An import
graph built from `import` / `from ... import` statements alone WOULD HAVE MISSED THE 2026-10-09
INSTANCE: the gate package reaches that module through
`importlib.util.spec_from_file_location(name, os.path.join(_CLONE, 'eval', 'index_quality',
'sweep_...py'))`, which is a string, not an import. So `spec_from_file_location` path
expressions are resolved too, and the planted specimens in tests/test_kaggle_import_safety.py
include a dynamically-loaded offender for exactly that reason.

Usage:  python scripts/check_kaggle_import_safety.py [--json]
Exit 0 clean · 1 findings · 2 the instrument could not be exercised (NOT a pass).
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The entry points. Everything under kaggle/ runs inside a notebook kernel by definition —
# that is what the directory IS — so the seed set is the directory, re-read every run rather
# than a list someone has to remember to extend.
SEED_DIR = "kaggle"

# Directories a repo-local import can resolve into. A name that resolves nowhere here is a
# third-party package and is not ours to audit.
LOCAL_ROOTS = ("chike", "scripts", "eval", "kaggle", "chike-inference", "chike-whatsapp")

# ── THE RULES ────────────────────────────────────────────────────────────────────────────
# Each rule is a module-level global-state mutation that a LIBRARY must not perform, because
# the caller owns that state and may be a notebook, a piped subprocess, or a test harness
# capturing output — none of which asked for it.
#
# `reconfigure` is BLOCKING: it has twice crashed a run outright.
#
# `chdir` is BLOCKING TOO, and not by analogy — it is the second rule the 2026-09-24 sweep
# itself named, and the 2026-10-09 file carries a live instance (`os.chdir(REPO)` at line 61,
# where REPO resolves to the Kaggle clone). It did not break the gate only because every path
# in that package is absolute or `_CLONE`-joined, i.e. by luck of an unrelated choice. A
# latent defect that depends on a caller's path style for its harmlessness is still a defect.
RULES = {
    "stdout_reconfigure": {
        "what": "sys.stdout/sys.stderr .reconfigure() at module level, unguarded",
        "why": "AttributeError on ipykernel.iostream.OutStream — the import fails and the "
               "caller's run dies before it starts. Crashed a regen 2026-09-24 and the full "
               "gate 2026-10-09.",
        "fix": "wrap in try/except Exception, or move it into main() — both are accepted; "
               "see scripts/check_anchor_provenance.py and scripts/check_correction_sync.py",
    },
    "chdir": {
        "what": "os.chdir() at module level",
        "why": "silently relocates the CALLER's working directory at import. Any relative "
               "path the caller uses afterwards resolves somewhere else, and nothing reports "
               "it. Named by the 2026-09-24 sweep's own rule list.",
        "fix": "move it into main(), or build absolute paths from REPO instead",
    },
    # ── THE REST OF THE 2026-09-24 RULE LIST, IMPLEMENTED RATHER THAN SWEPT ──────────────
    # That incident's write-up says it "AST-swept the other two modules ... for module-level
    # I/O configuration of any kind -- reconfigure, setlocale, logging.basicConfig,
    # filterwarnings, chdir, os.environ assignment. Both clean; this was the only one."
    #
    # ⛔ ALL FOUR BELOW ARE CURRENTLY CLEAN ACROSS ALL 43 LIBRARIES IN THE CLOSURE, AND THAT
    # IS EXACTLY WHY THEY ARE CODED HERE INSTEAD OF RECORDED AS A CLEAN SWEEP. A one-time
    # sweep that found nothing is the same artifact as the one that found something and then
    # could not protect a file written fifteen days later. The marginal cost of enforcing a
    # rule with zero current violations is zero; the cost of re-deriving it by hand next time
    # is a lost run. Each is planted in tests/test_kaggle_import_safety.py so none is inert.
    "setlocale": {
        "what": "locale.setlocale() at module level",
        "why": "process-global. Changes number and date formatting for the caller and every "
               "other module in the kernel, and can make float parsing locale-dependent.",
        "fix": "move it into main()",
    },
    "logging_basicConfig": {
        "what": "logging.basicConfig() at module level",
        "why": "configures the ROOT logger once, process-wide, first-caller-wins. An import "
               "silently decides the caller's log format and level, and a later legitimate "
               "basicConfig is then a no-op with no warning.",
        "fix": "move it into main(), or use logging.getLogger(__name__) and configure nothing",
    },
    "filterwarnings": {
        "what": "warnings.filterwarnings() at module level",
        "why": "process-global warning state. An import can silence a DeprecationWarning the "
               "caller needed to see — the quiet direction, which is the one nobody notices.",
        "fix": "move it into main(), or use warnings.catch_warnings() as a context manager",
    },
    "environ_assign": {
        "what": "os.environ[...] = ... at module level",
        "why": "mutates the caller's process environment at import. On Kaggle this can flip "
               "a token, a cache directory or a device-visibility variable for code that "
               "imported this module for an unrelated reason.",
        "fix": "move it into main(), or pass the value as an argument",
    },
}


#   rule -> (module, attribute) for the plain `module.attr()` forms
_DOTTED_RULES = {
    "chdir": ("os", "chdir"),
    "setlocale": ("locale", "setlocale"),
    "logging_basicConfig": ("logging", "basicConfig"),
    "filterwarnings": ("warnings", "filterwarnings"),
}
# Rules a SEED script is exempt from: it runs as __main__ in the kernel and owns its own
# process state. `stdout_reconfigure` is deliberately NOT here — the kernel's stdout has no
# `reconfigure` whoever calls it, so a seed's own unguarded call crashes just the same.
SEED_EXEMPT = frozenset({"chdir", "setlocale", "logging_basicConfig", "filterwarnings",
                         "environ_assign"})


def _parse(rel: str):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=rel)


def _resolve_module(name: str):
    """A dotted module name -> a repo-relative .py path, or None if it is third-party.

    ⛔ THE SECOND BRANCH IS THE ONE THAT MATTERS, AND IT WAS MISSING FROM THE FIRST DRAFT OF
    THIS FILE — WHICH THEREFORE DID NOT CONTAIN THE 2026-09-24 OFFENDER AT ALL. The regen
    reaches its checker as `sys.path.insert(0, 'scripts')` then
    `from check_correction_sync import check_facts_and_index`: a BARE module name that
    resolves only because a directory was pushed onto sys.path. Resolving the dotted name
    against the repo root alone returns None, so `scripts/check_correction_sync.py` — the file
    whose module-level reconfigure killed a whole regen — sat outside the audited population
    while the scan reported two findings and looked like it was working.

    That is the fixture-composition defect (R20's fourth arrival point) in the instrument
    built to close this class: a population that silently omits the historical specimen
    reports a cleaner result than it earned. The test asserts specific expected members for
    exactly this reason — a population is checked by its POSITIVE limb, not by its findings.
    """
    if not name:
        return None
    parts = name.split(".")
    cands = [os.path.join(*parts) + ".py", os.path.join(*parts, "__init__.py")]
    # a bare/dotted name made importable by `sys.path.insert(0, '<root>')`
    if parts[0] not in LOCAL_ROOTS and name not in getattr(sys, "stdlib_module_names", ()):
        for root in LOCAL_ROOTS:
            cands.append(os.path.join(root, *parts) + ".py")
            cands.append(os.path.join(root, *parts, "__init__.py"))
    for cand in cands:
        if os.path.isfile(os.path.join(REPO, cand)):
            rel = cand.replace("\\", "/")
            if rel.split("/")[0] in LOCAL_ROOTS:
                return rel
    return None


def _consts(tree):
    """Module-level `NAME = '<literal path>'` bindings, so a path held in a variable resolves.

    `kaggle/regenerate_rag_e5.py` does `_gates_path = 'scripts/rag_payload_gates.py'` and then
    `spec_from_file_location('rag_payload_gates', _gates_path)`. Reading only literal call
    arguments misses it — and that module is the one holding every payload gate for the regen,
    i.e. the last thing that should sit outside an audit.
    """
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0],
                                                                           ast.Name):
            v = _literal_join(n.value, {})
            if v:
                out[n.targets[0].id] = v
    return out


def _candidate_paths(node, consts):
    """Every repo-relative path a path expression could denote, longest first.

    ⛔ WHY SUFFIXES AND NOT ONE JOINED STRING — AND THIS IS THE SECOND INSTRUMENT DEFECT THIS
    FILE RECORDS AGAINST ITSELF, IN THE SAME DIRECTION AS THE FIRST.

    The gate package reaches the sweep as
    `os.path.join(_CLONE, 'eval', 'index_quality', 'sweep_...py')`. The first draft ignored
    non-literal arguments and got `eval/index_quality/sweep_...py`, which resolved and gave two
    findings. Then `_consts` was added so `_gates_path` would resolve — and `_CLONE` is ALSO a
    module-level literal (`'/kaggle/working/AFRICA-GIANTS'`), so the join became
    `/kaggle/working/AFRICA-GIANTS/eval/index_quality/sweep_...py`, which is not a repo file.
    THE MODULE FELL OUT OF THE POPULATION AND THE SCAN WENT FROM 2 FINDINGS TO 'CLEAN' WHILE
    THE CLOSURE GREW FROM 58 TO 60 — a strictly more capable resolver that deleted the only
    finding it existed to report.

    That is R39 exactly: in a cleanup the dangerous failure is the one that SHORTENS the
    output, because a falling count is indistinguishable from progress. It was caught only by
    asking why the number moved, and it is why the test asserts specific expected MEMBERS of
    the population rather than only asserting the findings list.

    So every suffix is tried and the first that is a real repo file wins: a clone root is just
    a prefix, whether it is a literal, a variable, or absent.
    """
    parts = None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        parts = [node.value]
    elif isinstance(node, ast.Name):
        v = consts.get(node.id)
        parts = [v] if v else None
    elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "join"):
        parts = []
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                parts.append(a.value)
            elif isinstance(a, ast.Name) and a.id in consts:
                parts.append(consts[a.id])
    if not parts:
        return []
    flat = []
    for p in parts:
        flat.extend([x for x in p.replace("\\", "/").split("/") if x])
    return ["/".join(flat[i:]) for i in range(len(flat))]


def _literal_join(node, consts):
    """The first candidate that is an actual repo file, or the plain literal if none is."""
    cands = _candidate_paths(node, consts)
    for c in cands:
        if os.path.isfile(os.path.join(REPO, c)):
            return c
    return cands[0] if cands else None


def _deps(tree, rel: str):
    """Every repo-local module `rel` can pull in — statically or by file path.

    Imports anywhere are followed, not only module-level ones: the gate package imports
    `chike.*` at module level and `torch`/`huggingface_hub` inside functions, and a repo-local
    import inside a function is just as able to carry this defect.
    """
    pkg = rel.replace("\\", "/").rsplit("/", 1)[0]
    consts = _consts(tree)
    out = set()

    # A DECLARED DEPENDENCY MANIFEST is an edge too. regenerate_rag_e5.py lists every file it
    # fetches in `SOURCE_FILES = [...]`, which is how its two checkers arrive on the
    # no-local-checkout path. Scoped to list/tuple literals assigned at module level — NOT to
    # every string in the file, because a docstring that NAMES a script is not an import, and
    # several named-but-not-imported scripts do carry a module-level reconfigure (correctly,
    # since they run as __main__).
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.List, ast.Tuple)):
            for el in n.value.elts:
                if isinstance(el, ast.Constant) and isinstance(el.value, str) \
                        and el.value.endswith(".py"):
                    p = el.value.replace("\\", "/")
                    if (os.path.isfile(os.path.join(REPO, p))
                            and p.split("/")[0] in LOCAL_ROOTS):
                        out.add(p)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                r = _resolve_module(a.name)
                if r:
                    out.add(r)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:                       # relative import: ../ per level
                up = pkg.split("/")
                up = up[:len(up) - (node.level - 1)] if node.level > 1 else up
                base = ".".join([p for p in up if p] + ([base] if base else []))
            r = _resolve_module(base)
            if r:
                out.add(r)
            for a in node.names:                 # `from chike import fidelity`
                r2 = _resolve_module(f"{base}.{a.name}" if base else a.name)
                if r2:
                    out.add(r2)
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            # ⛔ THE DYNAMIC EDGE. This is the edge the 2026-10-09 crash came in on, and a
            # statement-only import graph does not have it.
            if name == "spec_from_file_location":
                for arg in node.args[1:2] or node.args[:1]:
                    p = _literal_join(arg, consts)
                    if p and os.path.isfile(os.path.join(REPO, p)):
                        out.add(p)
                for kw in node.keywords:
                    if kw.arg in ("location", "origin"):
                        p = _literal_join(kw.value, consts)
                        if p and os.path.isfile(os.path.join(REPO, p)):
                            out.add(p)
            elif name == "import_module":
                for arg in node.args[:1]:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        r = _resolve_module(arg.value)
                        if r:
                            out.add(r)
    return out


def closure(seeds):
    """Transitive closure of repo-local modules reachable from `seeds`."""
    seen, queue, edges = set(), list(seeds), {}
    while queue:
        rel = queue.pop()
        if rel in seen:
            continue
        seen.add(rel)
        try:
            tree = _parse(rel)
        except (SyntaxError, OSError):
            continue
        deps = _deps(tree, rel)
        edges[rel] = sorted(deps)
        queue.extend(deps)
    return seen, edges


def _module_level_offences(tree):
    """Module-level global-I/O mutations that are NOT inside a try/except.

    Scope is deliberately narrow in two ways, and both are the point:
      * inside a FunctionDef/ClassDef is FINE — it only runs when called, so the caller
        decides. That is the shape check_correction_sync.py was fixed into.
      * inside a `try` is FINE — the AttributeError is caught, which is the shape
        check_anchor_provenance.py already uses.
    """
    found = []

    def walk(nodes, in_try):
        for n in nodes:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue                                     # not import-time
            if isinstance(n, ast.Try):
                # the handlers themselves still run at import time, so they are scanned too
                walk(n.body, True)
                walk(n.orelse, True)
                walk(n.finalbody, in_try)
                for h in n.handlers:
                    walk(h.body, in_try)
                continue
            for call in [c for c in ast.walk(n) if isinstance(c, ast.Call)]:
                f = call.func
                if isinstance(f, ast.Attribute) and f.attr == "reconfigure":
                    tgt = f.value
                    if (isinstance(tgt, ast.Attribute) and tgt.attr in ("stdout", "stderr")
                            and isinstance(tgt.value, ast.Name) and tgt.value.id == "sys"):
                        if not in_try:
                            found.append(("stdout_reconfigure", call.lineno,
                                          f"sys.{tgt.attr}.reconfigure(...)"))
                # module.attr() forms: os.chdir, locale.setlocale, logging.basicConfig,
                # warnings.filterwarnings
                for rule, (mod_, attr) in _DOTTED_RULES.items():
                    if (isinstance(f, ast.Attribute) and f.attr == attr
                            and isinstance(f.value, ast.Name) and f.value.id == mod_
                            and not in_try):
                        found.append((rule, call.lineno, f"{mod_}.{attr}(...)"))
            # os.environ['X'] = ... / os.environ.setdefault(...) / .update(...)
            for asg in [a for a in ast.walk(n) if isinstance(a, ast.Assign)]:
                for tgt in asg.targets:
                    if (isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Attribute)
                            and tgt.value.attr == "environ" and not in_try):
                        found.append(("environ_assign", asg.lineno, "os.environ[...] = ..."))
            for call in [c for c in ast.walk(n) if isinstance(c, ast.Call)]:
                f = call.func
                if (isinstance(f, ast.Attribute) and f.attr in ("setdefault", "update")
                        and isinstance(f.value, ast.Attribute) and f.value.attr == "environ"
                        and not in_try):
                    found.append(("environ_assign", call.lineno,
                                  f"os.environ.{f.attr}(...)"))
            if isinstance(n, (ast.If, ast.With, ast.For, ast.While)):
                walk(getattr(n, "body", []), in_try)
                walk(getattr(n, "orelse", []), in_try)
    walk(tree.body, False)
    return found


def scan(seeds=None):
    """Returns (findings, population, edges). A finding is a blocking defect."""
    if seeds is None:
        d = os.path.join(REPO, SEED_DIR)
        seeds = sorted(f"{SEED_DIR}/{f}" for f in os.listdir(d) if f.endswith(".py"))
    if not seeds:
        raise RuntimeError(f"no seeds under {SEED_DIR}/ — the instrument has no population "
                           f"and a clean result would mean nothing (exit 2, not a pass)")
    population, edges = closure(seeds)
    findings = []
    for rel in sorted(population):
        # A seed is a SCRIPT, not a library: it runs as `__main__` in the notebook and owns
        # its own stdout. Only modules something else IMPORTS are judged.
        is_seed = rel in set(seeds)
        try:
            tree = _parse(rel)
        except (SyntaxError, OSError) as e:
            findings.append({"module": rel, "rule": "unparseable", "line": 0,
                             "detail": str(e)[:200],
                             "why": "a module in the closure cannot be parsed, so it cannot "
                                    "be cleared either"})
            continue
        for rule, lineno, detail in _module_level_offences(tree):
            if is_seed and rule in SEED_EXEMPT:
                continue
            findings.append({"module": rel, "rule": rule, "line": lineno, "detail": detail,
                             "imported_by": sorted(k for k, v in edges.items() if rel in v),
                             **RULES[rule]})
    return findings, sorted(population), edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # noqa: this is main()
    except Exception:                                                # noqa: BLE001
        pass
    findings, population, edges = scan()
    out = {
        "_what": "module-level global-I/O mutations in modules the kaggle/ scripts import, "
                 "directly or transitively (including via spec_from_file_location)",
        "_why_static": "under pytest sys.stdout is a TextIOWrapper and HAS reconfigure, so "
                       "no local run of these modules can reach this failure mode. Local "
                       "green says nothing about Jupyter's OutStream.",
        "seeds": SEED_DIR, "modules_in_closure": len(population),
        "population": population, "findings": findings,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(f"closure: {len(population)} repo-local modules reachable from {SEED_DIR}/")
        for f in findings:
            print(f"  [{f['rule']}] {f['module']}:{f['line']}  {f['detail']}")
            print(f"      imported by: {', '.join(f.get('imported_by') or ['-'])}")
            print(f"      {f['why']}")
            print(f"      FIX: {f['fix']}")
        print(f"\n{'CLEAN' if not findings else f'{len(findings)} FINDING(S)'}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
