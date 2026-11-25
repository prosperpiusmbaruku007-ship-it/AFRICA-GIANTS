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
#
# ⭐ BUMPED 2026-10-09 for the row-9 regen (`nssf_employer_rate` reworded so the BASE is not
# readable as the SOURCE). Previous value, kept so a rollback is one lookup away rather than one
# git-log excavation: 19bcfabb887c49643268b9a5659ae31d90d31a982fb42930a250b23d6f5ae405 — the
# 2026-10-07 BRELA index. The pin FIRED on this change, with its own instruction attached, which
# is the only reason the constant and the index are in the same commit.
#
# ⭐ BUMPED 2026-11-13 for the three-profile coverage regen (184 -> 208 rows: 24 new facts appended + 5 rewritten rows). Previous value, kept
# for rollback: 5f76d40cf46d8be515f356c05bfb072529482c5bdf3dab966264965a9d98381f -- the row-9 index of 2026-10-09 (184 rows). Computed from
# the fetched HF file, which was verified identical (rows and order) to the local build of adb03a2 BEFORE it was committed.
# ⭐ BUMPED 2026-11-16 for the follow-up regen (208 -> 211 rows: 3 new rows, 29 R44 section-number strips, the presumptive row, the 2 WCF rows). Previous
# value, kept for rollback: 78b2b4d2e36dd88eb9c297a087fbf8f68a010e800d7c36b980eab0b1d7917577 -- the 208-row index of 2026-11-13. Computed from the fetched HF
# file (dataset commit 3565846), verified IDENTICAL (rows and order) to the local build of a0a4ce4 BEFORE it was committed.
# ⭐ BUMPED 2026-11-17 for the licence/dividend/company-return regen (211 -> 215 rows: rows 168 and 199 rewritten, 4 appended). Previous value, kept for rollback:
# cfaaa6f16d63bfd46256b18e1172e39d6a484f0c52a7e3946f057204db4d582b -- the 211-row index of 2026-11-16. Computed from the fetched HF file (dataset commit f0696366, built
# from 8452139), verified IDENTICAL (rows and order) to the local build of 896a6c9 BEFORE it was committed.
# ⭐ BUMPED 2026-11-17 (batch 2): row 213 (gn605a_issuer) rewritten to state the issuer BY OFFICE; the index stays 215 rows. Previous value, kept for rollback:
# 97696157be5acb0d98ac1654bae924301b55ea1ca9d962888f05e3253de680c7 -- the 215-row index of a2e6611. Computed from the fetched HF file (dataset commit 9882b1b7, built from 8c9ecfd),
# verified IDENTICAL (rows and order) to the local build of 8c9ecfd, and verified to differ from the served index at row 213 ONLY (text and embedding), BEFORE it was committed.
# ⭐ BUMPED 2026-11-17 (batch 3): ONE row appended (company_annual_return_deadline, index 215); 215 -> 216 rows. Previous value, kept for rollback:
# 456838235c40f757c4b833571763c9cfa5754ffc170d5c11af336cf5653a0e13 -- the 215-row index of e9e429e. Computed from the fetched HF file (dataset commit 8dfb5d56, built from edd7357),
# verified IDENTICAL (rows and order) to the local build, and verified to equal the served index on the first 215 rows (text and embedding) with row 215 the only addition, BEFORE it was committed.
# BUMPED 2026-11-23: TWO rows appended (sdl_domestic_workers_scope 216, nssf_contributions_age_60 217) and row 174 (sdl_exemption_categories) revised in place; 216 -> 218 rows. Previous value, kept for rollback:
# 4dc60c37d8c28cd0beb4e020fab8f6d61b4407c0b64e9e4c13a8600658a7c84a -- the 216-row index of 8dfb5d56. Computed from the fetched HF file (Kaggle run of b3d43af, baseline bd4bf61), verified IDENTICAL (rows and order) to build_fact_texts(),
# and verified to differ from the served index at row 174 ONLY (215 embeddings identical to the served ones within 1e-5), BEFORE it was committed.
# BUMPED 2026-11-24: TWO rows appended (sdl_base_includes_allowances 218, medical_services_vat_exempt 219) and SIX rows revised in place (4, 20, 21, 66, 89, 108); 218 -> 220 rows. Previous value, kept for rollback:
# f1e6e51396e10d9be7fa1b07e0fa7124e451427384c26f71c2d320cd64c16e50 -- the 218-row index of Kaggle run b3d43af. Computed from the fetched HF file (dataset commit ea67e42b, Kaggle run of 3b8cf2f, baseline ae0f09b), verified IDENTICAL (rows and order) to build_fact_texts(),
# verified to differ from the served index at rows 4, 20, 21, 66, 89, 108 ONLY (212 unchanged embeddings identical within 1.5e-7), BEFORE it was committed (eval/results/regen_landing_verification_2026_11_24.json).
# BUMPED 2026-11-24b: FOUR rows appended (medicines_vat_exempt 220, paye_base_employment_income 221, sdl_deemed_month_of_payment 222, wcf_contribution_base 223) and row 66 revised in place; 220 -> 224 rows. Previous value, kept for rollback:
# bd4a15a16662003703a3839287ca8d3abddfe34d072855829530b1524d96e8b8 -- the 220-row index of Kaggle run 3b8cf2f. Computed from the fetched HF file (Kaggle run of fd451db, 224 facts, 95 guards PASS), verified IDENTICAL (rows and order) to build_fact_texts(), differing from the served index at row 66 ONLY
# (219 unchanged embeddings identical within 2e-7), BEFORE it was committed (eval/results/regen_landing_verification_2026_11_24b.json).
EXPECTED_SERVED_SHA256 = (
    "e97ed6019e2a90d96800204acc141f4e44408a46c5fa82ffe996db0b37928f6b")
EXPECTED_ROWS = 224


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
