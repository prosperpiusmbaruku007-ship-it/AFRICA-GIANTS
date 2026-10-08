# -*- coding: utf-8 -*-
"""THE chike-inference BUILD ENDPOINT, ASSERTED (2026-10-08).

WHY IT WAS ADDED. R16b says "GET /health returns `build` -- confirm it matches the commit
you just pushed", and it was implemented on `chike-whatsapp` ONLY. `chike-inference` had no
/health, no CHIKE_BUILD and nothing else that reports what it serves, so on 2026-10-07 the
entire evidence that the corrected BRELA index had reached production was a CONTENT PROBE --
a question whose answer happens to differ before and after. That works only while someone
can think of such a question, and the gap was worse here than on the WhatsApp app: that
app's failure mode is a dead webhook, which is obvious, while this app's is a fluent,
confident, superseded regulatory figure, which is not.

WHAT THIS TEST CAN AND CANNOT DO. It cannot call the live endpoint -- that needs Modal and
the deploy. It CAN pin the three things a future edit could quietly remove, which is the
R26 question applied to a brand-new control: not "does it work" but "is it still wired, and
to the thing it claims".

⚠️ A PASSING TEST HERE IS NOT A DEPLOY VERIFICATION, and saying so is the point: the
endpoint has not yet been exercised live. It is listed as NOT_EXERCISABLE_OFFLINE in the
control-fire audit rather than as FIRES, because a census that quietly books an unexercised
control as working reports a cleaner result than it earned.
"""
import ast
import hashlib
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO, "chike-inference", "modal_app.py")

# The digest `served_index_identity` will report for the currently committed index, computed
# the same way the method computes it (json.dumps(..., ensure_ascii=False) over the loaded
# list). This is the post-deploy equality check: if deep /health reports this value, the
# corrected index is live, and no content probe is needed to establish it.
#
# ⛔ WHY A DIGEST AND NOT A ROW COUNT: `rag_fact_count` was UNCHANGED at 184 across the
# 2026-10-07 BRELA regen, so the count could not distinguish the corrected index from the
# superseded one and the fail-loud contract had nothing to catch. The count is the thing
# that failed; the digest is the fix.
EXPECTED_SERVED_SHA256 = (
    "19bcfabb887c49643268b9a5659ae31d90d31a982fb42930a250b23d6f5ae405")
EXPECTED_ROWS = 184


def _src():
    with open(APP, encoding="utf-8") as fh:
        return fh.read()


def _tree():
    return ast.parse(_src())


def test_the_health_endpoint_exists_and_is_a_GET():
    """Parsed from the AST, not grepped. Three separate checks in the 2026-08-24 control
    audit matched the COMMENT explaining why a defect was removed rather than any code, one
    of them introduced while fixing the previous two."""
    fns = {n.name: n for n in _tree().body if isinstance(n, ast.FunctionDef)}
    assert "health" in fns, "the /health endpoint is gone from chike-inference"
    decos = ast.unparse(ast.Module(body=fns["health"].decorator_list, type_ignores=[]))
    assert "fastapi_endpoint" in decos, "health is no longer an HTTP endpoint"
    assert "'GET'" in decos or '"GET"' in decos, "health must be a GET"


def test_build_is_read_from_the_environment_and_baked_into_both_images():
    """A build SHA that is not baked into the image cannot be reported by a container.
    BOTH images must carry it: the web tier and the GPU class are separate containers with
    separate lifecycles, and a warm GPU container behind a fresh web tier is the exact R16
    hazard the `build_matches` comparison exists to expose."""
    src = _src()
    assert "BUILD = os.environ.get('CHIKE_BUILD', '') or 'dev'" in src, \
        "CHIKE_BUILD is no longer read from the deploy environment"
    assert src.count(".env({'CHIKE_BUILD': BUILD})") == 2, (
        "CHIKE_BUILD must be baked into BOTH the GPU image and the web image; found "
        f"{src.count(chr(46) + 'env(' + chr(123) + chr(39) + 'CHIKE_BUILD' + chr(39))} site(s)")


def test_the_deep_check_reports_what_the_container_LOADED_not_what_the_repo_contains():
    """`served_index_identity` must read the retriever's arrays. Re-reading the file off
    disk would certify the IMAGE, which is a different claim from what is being served --
    R26's "ask what the deployed path actually calls, with what arguments"."""
    tree = _tree()
    cls = next(n for n in ast.walk(tree)
               if isinstance(n, ast.ClassDef) and n.name == "ChikeModel")
    meth = next((n for n in cls.body
                 if isinstance(n, ast.FunctionDef) and n.name == "served_index_identity"),
                None)
    assert meth is not None, "served_index_identity was removed from ChikeModel"
    body = ast.unparse(meth)
    assert "self.fact_texts" in body, (
        "the digest must be taken over self.fact_texts (what the retriever serves), not a "
        "fresh read of the file")
    assert "open(" not in body, (
        "served_index_identity re-reads a file; that certifies the image, not the served "
        "index")
    assert "sha256" in body and "rag_rows_loaded" in body


def test_a_shallow_pass_is_documented_as_NOT_a_deploy_verification():
    """The failure mode of a build endpoint is being trusted too far. R16's whole lesson is
    that '✓ App deployed' is not verification; a 200 from /health must not become the new
    version of that."""
    src = _src()
    assert "A SHALLOW PASS IS NOT A DEPLOY VERIFICATION" in src
    assert "build_matches" in src, "the two-tier comparison is gone"


def test_the_committed_index_still_matches_the_expected_served_digest():
    """⛔ THE ASSERTION THAT MAKES THE DIGEST USEFUL RATHER THAN DECORATIVE. If the index is
    regenerated and this constant is not updated, the post-deploy equality check would be
    run against a stale expectation and would 'fail' on a correct deploy -- the stale-pin
    shape. Failing here, loudly, at the moment the index changes is the fix: update the
    constant IN THE SAME COMMIT as the index, exactly as EXPECTED_HEAD is bumped."""
    for d in ("chike-inference", "kaggle"):
        p = os.path.join(REPO, d, "rag_facts_text.json")
        with open(p, encoding="utf-8") as fh:
            rows = json.load(fh)
        blob = json.dumps(rows, ensure_ascii=False).encode("utf-8")
        got = hashlib.sha256(blob).hexdigest()
        assert len(rows) == EXPECTED_ROWS, f"{d}: {len(rows)} rows, expected {EXPECTED_ROWS}"
        assert got == EXPECTED_SERVED_SHA256, (
            f"{d}/rag_facts_text.json no longer hashes to EXPECTED_SERVED_SHA256.\n"
            f"  expected {EXPECTED_SERVED_SHA256}\n  got      {got}\n"
            "If the index was regenerated on purpose, update EXPECTED_SERVED_SHA256 in this "
            "file IN THE SAME COMMIT, so deep /health keeps being checkable against a "
            "current expectation.")


@pytest.mark.parametrize("needle", [
    "rag_facts_text_sha256",
    "rag_rows_loaded",
    "build_mismatch_warning",
    "index_contract_violation",
])
def test_the_deep_payload_carries_the_fields_the_post_deploy_check_reads(needle):
    """Each is read by eval/controls/ during an R16 verification. A field that silently
    disappears turns the check into one that cannot fail (R20)."""
    assert needle in _src(), f"{needle} is no longer reported by /health"
