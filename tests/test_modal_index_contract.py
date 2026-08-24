"""The fail-loud index contract, now wired into PRODUCTION — pinned here.

WHY THESE EXIST. `chike/retrieval.py` has carried a "FAIL-LOUD INDEX CONTRACT (2026-08-06,
pre-launch blocker)" since before `chike-inference/modal_app.py` was written. It fires. **Production
never called it** — `ChikeModel.__enter__` loaded the index itself and kept the exact behaviour the
contract was written to remove: a missing index printed a WARNING, set `fact_texts = []`, and every
subsequent answer was generated with **no facts at all**.

So a pre-launch blocker protected local harnesses and never protected a single request. Found
2026-08-24 by `eval/controls/audit_control_fires.py`. **The lesson is R26's: where a control lives
matters more than whether it works, and no unit test of `chike/retrieval.py` could ever have shown
this** — the module was perfect; nothing imported it.

TWO THINGS ARE PINNED, and the second matters as much as the first:

  1. **The contract is wired.** A missing, inconsistent or wrong-sized index must raise.
  2. **RETRIEVAL BEHAVIOUR IS UNCHANGED, BYTE FOR BYTE.** A control fix must not smuggle in a
     behaviour change. The canonical loader is used ONLY to load and validate; the single-arm
     top-3 scoring in `retrieve_facts` is untouched, and `chike.retrieval.Retriever.retrieve()`
     — the TWO-ARM hybrid — is deliberately not called, because the full A/B on 2026-08-24 kept
     single-arm (eval/results/ab_retriever_full_adjudication.json).
"""
import json
import os

import numpy as np
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODAL_APP = os.path.join(REPO, 'chike-inference', 'modal_app.py')
EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
TXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
CONFIG = os.path.join(REPO, 'kaggle', 'chike_config.json')


def _src():
    with open(MODAL_APP, encoding='utf-8') as f:
        return f.read()


def _code_lines():
    """Non-comment, non-blank lines — so a comment quoting the old defect never satisfies a
    test. (The control audit's own first production-usage check matched `chike.retrieval` in
    two COMMENT LINES saying production does not use it.)"""
    return [ln for ln in _src().splitlines()
            if ln.strip() and not ln.strip().startswith('#')]


# --- 1. the contract is actually wired into the deployed file ---------------------------------

def test_production_loads_the_index_through_the_canonical_validating_loader():
    code = '\n'.join(_code_lines())
    assert 'from chike.retrieval import Retriever' in code, (
        'modal_app no longer imports the canonical loader — the fail-loud contract is back to '
        'living in a module production does not call.')
    assert '.preflight()' in code, 'modal_app does not run preflight(), so nothing validates'
    assert 'expected_fact_count=' in code, (
        'modal_app does not pass expected_fact_count, so a stale or half-regenerated R15 index '
        'loads silently')


def test_no_silent_empty_index_fallback_survives_in_production():
    """THE EXACT DEFECT. Two sites returned [] instead of failing: the startup else-branch and
    retrieve_facts' bare except. Either one alone reopens the hole."""
    code = _code_lines()
    disabled = [ln for ln in code if 'RAG disabled' in ln]
    assert not disabled, f'the silent RAG-disabled fallback is back: {disabled}'
    # `return []` must not appear anywhere in the retrieval path
    offenders = [ln for ln in code if ln.strip() == 'return []']
    assert not offenders, (
        f'a bare `return []` survives in modal_app: {offenders}. A retrieval failure must raise '
        f'— a failed request is visible to the user, a factless answer is not.')


def test_a_missing_rag_fact_count_is_fatal_rather_than_skipped():
    """An absent config key must not silently disable the count check — that is how a control
    gets weakened without anyone deciding to weaken it."""
    code = '\n'.join(_code_lines())
    assert 'rag_fact_count' in code
    assert 'raise RuntimeError' in code, (
        'a missing rag_fact_count no longer raises, so the count check can be skipped by '
        'omission')


def test_config_rag_fact_count_matches_the_baked_index():
    """The R14 config and the baked index ship together in the same image. If this drifts, the
    container will refuse to start — which is the point, but it should be caught here first."""
    with open(CONFIG, encoding='utf-8') as f:
        cfg = json.load(f)
    with open(TXT, encoding='utf-8') as f:
        texts = json.load(f)
    assert cfg.get('rag_fact_count') == len(texts), (
        f"chike_config.json rag_fact_count={cfg.get('rag_fact_count')} but the baked index has "
        f'{len(texts)} rows. Update the config in the same commit as an R15 regen.')


# --- 2. the loader raises on each planted defect (R26: watch the control fire) -----------------

def test_the_loader_raises_on_a_missing_index(tmp_path):
    from chike.retrieval import Retriever, RetrievalIndexError
    with pytest.raises(RetrievalIndexError):
        Retriever(emb_path=str(tmp_path / 'nope.npy'),
                  texts_path=str(tmp_path / 'nope.json')).preflight()


def test_the_loader_raises_on_a_shape_mismatch(tmp_path):
    """A half-written R15 regen: embeddings and texts disagree."""
    from chike.retrieval import Retriever, RetrievalIndexError
    emb = tmp_path / 'e.npy'
    txt = tmp_path / 't.json'
    np.save(str(emb), np.zeros((5, 768), dtype=np.float32))
    txt.write_text(json.dumps(['a', 'b', 'c']), encoding='utf-8')
    with pytest.raises(RetrievalIndexError):
        Retriever(emb_path=str(emb), texts_path=str(txt)).preflight()


def test_the_loader_raises_on_a_stale_but_internally_consistent_index(tmp_path):
    """The nastiest case, and the only one expected_fact_count can see: the index is perfectly
    well-formed and simply is not the one this deploy expects."""
    from chike.retrieval import Retriever, RetrievalIndexError
    emb = tmp_path / 'e.npy'
    txt = tmp_path / 't.json'
    np.save(str(emb), np.zeros((5, 768), dtype=np.float32))
    txt.write_text(json.dumps(['a', 'b', 'c', 'd', 'e']), encoding='utf-8')
    Retriever(emb_path=str(emb), texts_path=str(txt)).preflight()          # consistent: fine
    with pytest.raises(RetrievalIndexError):
        Retriever(emb_path=str(emb), texts_path=str(txt),
                  expected_fact_count=221).preflight()                      # stale: fatal


def test_the_real_index_passes_all_three_limbs():
    """R17's negative case. A loader that raises on everything is as useless as one that raises
    on nothing."""
    from chike.retrieval import Retriever
    with open(TXT, encoding='utf-8') as f:
        n = len(json.load(f))
    assert Retriever(emb_path=EMB, texts_path=TXT, expected_fact_count=n).preflight() == n


# --- 3. retrieval behaviour is UNCHANGED ------------------------------------------------------

def test_the_canonical_loader_yields_the_identical_arrays():
    """What production scores over must be the same object content as before the change."""
    from chike.retrieval import Retriever
    r = Retriever(emb_path=EMB, texts_path=TXT)
    r.preflight()
    raw_emb = np.load(EMB)
    with open(TXT, encoding='utf-8') as f:
        raw_txt = json.load(f)
    assert np.array_equal(r.fact_embeddings, raw_emb)
    assert r.fact_texts == raw_txt


def test_single_arm_top3_is_identical_through_either_loader():
    """The scoring math, exercised without the e5 model.

    `retrieve_facts` is deterministic given a query vector, so random query vectors test the
    ranking path end-to-end with no network and no GPU. If the loader change had altered dtype,
    ordering or normalisation, these top-3 lists would diverge.
    """
    from chike.retrieval import Retriever, _rank_indices
    r = Retriever(emb_path=EMB, texts_path=TXT)
    r.preflight()
    raw = np.load(EMB)
    rng = np.random.default_rng(20260824)
    for _ in range(25):
        q = rng.standard_normal(raw.shape[1]).astype(raw.dtype)
        assert _rank_indices(q, r.fact_embeddings, 3) == _rank_indices(q, raw, 3)


def test_production_still_uses_single_arm_not_the_two_arm_hybrid():
    """The A/B kept single-arm. A control fix must not quietly switch the retriever."""
    code = '\n'.join(_code_lines())
    assert 'retriever=self.retrieve_facts' in code, (
        'production is no longer injecting its own single-arm retriever')
    assert 'Retriever.retrieve(' not in code and '_retriever.retrieve(' not in code, (
        'modal_app is calling the two-arm hybrid; the 2026-08-24 A/B kept single-arm')
