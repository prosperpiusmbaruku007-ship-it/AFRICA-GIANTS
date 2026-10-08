#!/usr/bin/env python3
"""PRE-FLIGHT FOR A MODAL DEPLOY — run BEFORE `modal app stop`, never after.

⛔ WHY THE ORDER IS THE WHOLE POINT. R16 step 1 says "force fresh containers": `modal app
stop chike-inference --yes`, then redeploy. The stop is INSTANT AND IRREVERSIBLE; the deploy
is neither. TWICE now the stop has succeeded and the replacing deploy has failed for an
unrelated reason, leaving production dead until it was fixed:

  2026-08-10  the CLI aborted on its own `✓` glyph, unprintable on a cp1252 console.
              ~2 minutes down.
  2026-10-08  `.env({'CHIKE_BUILD': BUILD})` was chained AFTER `add_local_file`, which Modal
              forbids without `copy=True`. ~3 minutes down.

Two unrelated causes, one window. Enumerating causes is therefore the wrong defence — the
defence is to REORDER: build and validate first, and only then open the window. After this,
the outage window can only be opened by a deploy that has ALREADY BUILT ONCE.

⚠️ AND THE OBVIOUS PRE-FLIGHT DOES NOT WORK, which is worth recording because it is the first
thing anyone would reach for. "Import modal_app.py and construct the image" DOES NOT CATCH
the 2026-10-08 bug: measured on modal 1.5.1, chaining `.env()` after `add_local_file()`
CONSTRUCTS FINE and raises only when the image is BUILT, at deploy time. An import-based
pre-flight would have passed and the outage would have happened anyway.

So this file does three things, in increasing cost:

  GATE 1  PROVENANCE — the tree is clean and HEAD is on origin. A deploy from a dirty tree
          makes /health lie: on 2026-10-08 it reported `build 5d1ed71` while the running
          image carried an uncommitted fix, so the label named a commit whose own
          modal_app.py CANNOT DEPLOY AT ALL. Accurate about what was passed, wrong about what
          was built — the stale-clone provenance problem one layer out.
  GATE 2  STATIC CHAIN LINT — AST-level, instant, offline. Encodes the one rule Modal
          enforces at build time: no `add_local_*` may be followed by another operation in an
          image chain unless it passed `copy=True`. This is the specific 2026-10-08 class, and
          it is the only gate here that costs nothing.
  GATE 3  REAL BUILD — `modal deploy --name <app>-preflight` on the SAME FILE. This performs
          the actual image build and app construction against Modal, under a throwaway app
          name, so the live app is untouched. It is the only gate that can catch a build
          failure nobody has thought of, which is exactly the category both outages came
          from. The preflight app is stopped afterwards.

Usage:
    python scripts/preflight_deploy.py chike-inference/modal_app.py
    python scripts/preflight_deploy.py chike-inference/modal_app.py --no-build   # gates 1-2
Exit: 0 = safe to stop and deploy; 1 = a gate failed; 2 = could not evaluate (NOT a pass).
"""
import argparse
import ast
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Methods that must be last in an image chain unless copy=True was passed.
_LOCAL_ADDS = {"add_local_file", "add_local_dir", "add_local_python_source"}


def _run(args, **kw):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


# ── GATE 1 ───────────────────────────────────────────────────────────────────────
def gate_provenance():
    fails = []
    st = _run(["git", "status", "--porcelain"])
    if st.returncode != 0:
        return ["git status failed — cannot evaluate provenance"], None
    if st.stdout.strip():
        fails.append(
            "WORKING TREE IS DIRTY. Deploying now makes /health report a commit that is not "
            "what is running:\n      "
            + "\n      ".join(st.stdout.strip().splitlines()[:8]))
    head = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    _run(["git", "fetch", "origin", "--quiet"])
    on_origin = _run(["git", "merge-base", "--is-ancestor", head,
                      "refs/remotes/origin/main"]).returncode == 0
    if not on_origin:
        fails.append(
            f"HEAD ({head[:7]}) IS NOT ON origin/main. The deployed SHA must be fetchable by "
            f"anyone reading /health, or the label points at a commit that exists only on "
            f"this machine. Push first.")
    return fails, head[:7]


# ── GATE 2 ───────────────────────────────────────────────────────────────────────
def gate_chain_lint(path):
    """Find `.add_local_*(...)` calls that are NOT the last operation in their chain.

    ⛔ THIS IS AN AST WALK, NOT A GREP. Three separate checks in the 2026-08-24 control audit
    matched the COMMENT explaining why a defect had been removed rather than any code — one
    of them introduced while fixing the previous two.
    """
    with open(os.path.join(REPO, path), encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    fails = []
    for node in ast.walk(tree):
        # A chain looks like Call(func=Attribute(value=Call(func=Attribute(...)))). For each
        # call, ask whether anything INSIDE its receiver was a local-add without copy=True.
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        outer = node.func.attr
        if outer in _LOCAL_ADDS:
            continue                      # a local-add wrapping a local-add is fine
        inner = node.func.value
        if not (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)):
            continue
        if inner.func.attr not in _LOCAL_ADDS:
            continue
        copied = any(k.arg == "copy" and getattr(k.value, "value", False) is True
                     for k in inner.keywords)
        if not copied:
            fails.append(
                f"{path}:{node.lineno}: `.{outer}()` is chained AFTER "
                f"`.{inner.func.attr}()` (line {inner.lineno}). Modal requires local-file "
                f"adds to be the LAST operations in an image chain unless copy=True. THIS IS "
                f"THE 2026-10-08 OUTAGE: it constructs fine and fails at BUILD time, so an "
                f"import-based pre-flight cannot see it. Move `.{outer}()` before the "
                f"local-adds.")
    return fails


# ── GATE 3 ───────────────────────────────────────────────────────────────────────
def gate_real_build(path, app_name):
    """Deploy the SAME FILE under a throwaway app name, then stop it.

    This is the only gate that catches a build failure nobody anticipated — the category both
    outages came from. `--name` overrides the deployment name, so `chike-inference` is never
    touched; the image layers are cached, so the subsequent real deploy is fast.
    """
    pre = f"{app_name}-preflight"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1",
               CHIKE_BUILD=os.environ.get("CHIKE_BUILD", "preflight"))
    p = subprocess.run([sys.executable, "-m", "modal", "deploy", "--name", pre, path],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    tail = ((p.stdout or "") + (p.stderr or ""))[-1200:]
    # Stop the preflight app whatever happened, so a failed run does not leave one behind.
    subprocess.run([sys.executable, "-m", "modal", "app", "stop", pre, "--yes"],
                   cwd=REPO, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        return [f"THE REAL BUILD FAILED under the preflight name {pre!r}, so the live deploy "
                f"would have failed too — and if the stop had already run, production would "
                f"be DOWN right now. Output tail:\n{tail}"], pre
    return [], pre


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_file", nargs="?",
                    default="chike-inference/modal_app.py")
    ap.add_argument("--app-name", default=None,
                    help="live app name; defaults to the modal.App(...) literal in the file")
    ap.add_argument("--no-build", action="store_true",
                    help="gates 1-2 only (offline). NOT a full pre-flight.")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(REPO, args.app_file)):
        print(f"[preflight] FAIL — {args.app_file} not found. Cannot evaluate, which is NOT "
              f"a pass.")
        return 2

    app_name = args.app_name
    if app_name is None:
        src = open(os.path.join(REPO, args.app_file), encoding="utf-8").read()
        import re
        m = re.search(r"modal\.App\(\s*['\"]([^'\"]+)['\"]", src)
        if not m:
            print("[preflight] FAIL — could not find the modal.App name. Cannot evaluate.")
            return 2
        app_name = m.group(1)

    print(f"[preflight] {args.app_file}  (live app: {app_name})")
    all_fails = []

    prov, head = gate_provenance()
    print(f"  GATE 1 provenance   : {'OK' if not prov else 'FAIL'}"
          + (f"  HEAD {head}" if head else ""))
    all_fails += prov

    lint = gate_chain_lint(args.app_file)
    print(f"  GATE 2 chain lint   : {'OK' if not lint else 'FAIL'}")
    all_fails += lint

    if args.no_build:
        print("  GATE 3 real build   : SKIPPED (--no-build). This is NOT a full pre-flight: "
              "the 2026-10-08 class is caught by gate 2, but a build failure nobody has "
              "thought of is only caught here.")
    elif all_fails:
        print("  GATE 3 real build   : SKIPPED — earlier gates already failed")
    else:
        build, pre = gate_real_build(args.app_file, app_name)
        print(f"  GATE 3 real build   : {'OK' if not build else 'FAIL'}  (as {pre}, stopped)")
        all_fails += build

    print()
    for f in all_fails:
        print(f"  ⛔ {f}")
    if all_fails:
        print("\n[preflight] DO NOT STOP THE LIVE APP. Fix the above first — the stop is the "
              "irreversible half, and twice now it has been taken before a deploy that then "
              "failed.")
        return 1
    print("[preflight] SAFE TO DEPLOY. Now, in this order:\n"
          f"  python -m modal app stop {app_name} --yes\n"
          f"  CHIKE_BUILD=$(git rev-parse --short HEAD) PYTHONIOENCODING=utf-8 PYTHONUTF8=1 \\\n"
          f"    python -m modal deploy {args.app_file}\n"
          "  then verify: GET /health (build == the SHA), and ?deep=1 for the served digest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
