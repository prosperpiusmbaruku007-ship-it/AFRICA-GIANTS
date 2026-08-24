"""Proof that chike/pipeline_v15.py + chike/decomposition_v15.py preserve production's
behaviour, and that the v15 arm cannot silently acquire v16 capabilities.

The bar the founder set for Phase D is "behaviour-preserving by proof, not assertion". So
every deterministic, model-free stage is diffed against tests/fixtures/
v15_inline_baseline_30aa79b.py — the inline code captured straight out of
`git show 30aa79b:chike-inference/modal_app.py` (and `:kaggle/eval.py`), i.e. the last commit
before the extraction. Not a restatement of production; production.

Coverage of the pipeline, and what is verifiable where:

  stage                       verified here (local, offline)        needs e5/GPU
  --------------------------- ------------------------------------- ------------------
  classify (OOC)              yes — shared module, existing tests    no
  never-guess guard           yes — shared predicate + call order    no
  decompose                   yes — all 400 + 40 probe questions     no
  retrieve (per sub-query)    NO — single-arm CONTRACT tested with   yes (Kaggle/live)
                              a stub; the e5 encode itself is not
  pool (dedup/order/cap 9)    yes — fake retriever, all 400          no
  prompt build (messages)     yes — all 400, stub tokenizer          no (template call
                                                                     covered by the live
                                                                     20-question compare)
  generate                    n/a — injected, environment-specific   yes
  stop-split + clean          yes — 400 PERSISTED raw generations    no

The two stages that cannot be closed locally (the real e5 encode and the real
apply_chat_template on the adapter tokenizer) are closed by the 20-question live byte-compare
against the production web_endpoint, run over HTTP before the arm is declared faithful.
"""
import json
import os
import re
import sys

import pytest

from chike import decomposition           # v16 decomposer (has the ordinal split)
from chike import decomposition_v15       # v15 decomposer (must NOT have it)
from chike import generation_cleanup
from chike import pipeline_v15
from chike import prompting

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixtures import v15_inline_baseline_30aa79b as baseline   # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GATE_FILES = [
    "eval/accuracy_gate/eval_questions_001.jsonl",
    "eval/accuracy_gate/eval_questions_002_additions.jsonl",
    "eval/accuracy_gate/eval_questions_003.jsonl",
]
_PROBE_FILES = [
    "eval/accuracy_gate/edge_probe_plain_sw_015.jsonl",
    "eval/accuracy_gate/edge_probe_plain_sw_005b.jsonl",
]
_GENERATIONS = "eval/results/gate_orchestrator_combined_5a62c00.json"


def _jsonl(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _all_questions():
    """The 400 gate questions plus the 20 plain-Swahili probe questions."""
    qs = [r["question_sw"] for f in _GATE_FILES for r in _jsonl(f)]
    qs += [r["question"] for f in _PROBE_FILES for r in _jsonl(f)]
    return qs


ALL_QUESTIONS = _all_questions()


def test_the_corpus_under_test_is_the_full_400_plus_probes():
    # Guards the proof itself: if a corpus file moved, the byte-identity tests below would
    # silently pass on a smaller set.
    assert len(ALL_QUESTIONS) == 420, len(ALL_QUESTIONS)


# ── decompose: extracted == production's inline copy, on every question ──────────

def test_decompose_is_byte_identical_to_modal_app_inline_across_the_corpus():
    diffs = [q for q in ALL_QUESTIONS
             if decomposition_v15.decompose_query(q) != baseline.decompose_query(q)]
    assert diffs == [], f"{len(diffs)} questions decompose differently, e.g. {diffs[:3]}"


def test_decompose_is_byte_identical_to_the_eval_py_inline_copy_too():
    # All three copies collapse onto one module only if all three agreed to begin with.
    eval_decompose = baseline._eval_py_namespace()["decompose_query"]
    diffs = [q for q in ALL_QUESTIONS
             if decomposition_v15.decompose_query(q) != eval_decompose(q)]
    assert diffs == [], f"{len(diffs)} differ from eval.py's copy, e.g. {diffs[:3]}"


# ── the v15 arm must NOT inherit v16 capabilities ────────────────────────────────

def test_v15_decomposer_lacks_the_v16_only_splits_on_exactly_two_questions():
    """chike.decomposition (v16) has two capabilities chike.decomposition_v15 must never gain:
    the 'mambo matatu: kwanza/pili/tatu' ordinal split (eval_322, shipped 2026-07-24) and the
    `na je` connector split (eval_332, shipped 2026-08-11). If the v15 arm imported the v16
    module it would gain capabilities production's v15 path does not have and flatter itself in
    the paired comparison.

    The divergence set is enumerated, not counted loosely: an UNINTENDED divergence still fails
    here. When a third v16-only capability ships, add its question to this list in the same
    commit — do not relax the assertion to a bare inequality."""
    differing = [q for q in ALL_QUESTIONS
                 if decomposition.decompose_query(q) != decomposition_v15.decompose_query(q)]
    assert len(differing) == 2, f"expected exactly eval_322 + eval_332, got {len(differing)}"

    ordinal = [q for q in differing if "kwanza" in q.lower() and "pili" in q.lower()]
    na_je = [q for q in differing if re.search(r"\bna\s+je\b", q, re.IGNORECASE)]
    assert len(ordinal) == 1 and len(na_je) == 1

    assert len(decomposition.decompose_query(ordinal[0])) == 3      # v16 splits 3 ways
    assert len(decomposition_v15.decompose_query(ordinal[0])) == 1  # v15 keeps it whole
    assert len(decomposition.decompose_query(na_je[0])) == 3        # two `na je` -> 3 asks
    assert len(decomposition_v15.decompose_query(na_je[0])) == 1


def test_v15_decomposer_has_no_ordinal_split_symbols_at_all():
    assert not hasattr(decomposition_v15, "_split_ordinal_enumeration")
    assert not hasattr(decomposition_v15, "_ORDINAL_ANNOUNCE")


class _StubRetriever:
    """Two-arm on `retrieve` (like chike.retrieval.Retriever), single-arm on the ranking
    path — the shape V15Retriever must respect."""

    fact_texts = [f"fact-{i}" for i in range(6)]

    def __init__(self):
        self.calls = []

    def retrieve(self, question, top_k=3):
        self.calls.append(("two_arm", question))
        return self.fact_texts[:top_k + 1]        # the appended 4th fact

    def _ensure_index(self):
        pass

    def _ensure_embed_model(self):
        pass

    def _encode_and_rank(self, question, top_k):
        self.calls.append(("single_arm", question))
        return list(range(top_k))

    fact_embeddings = object()


def test_v15_retriever_is_single_arm_and_never_calls_the_two_arm_hybrid():
    v15r = pipeline_v15.V15Retriever.__new__(pipeline_v15.V15Retriever)
    stub = _StubRetriever()
    v15r._inner = stub

    facts = v15r.retrieve_facts("Nina wafanyakazi 12 na mshahara TZS 600,000, SDL ni ngapi?")

    assert facts == ["fact-0", "fact-1", "fact-2"]           # 3, not 4
    assert [c[0] for c in stub.calls] == ["single_arm"]      # the hybrid was never invoked
    assert facts == stub.retrieve("x", top_k=3)[:3]          # == the two-arm's first 3


# ── pool: dedup, order-preserving, cap 9 ─────────────────────────────────────────

def test_pool_facts_matches_the_inline_pooling_loop_across_the_corpus():
    def fake_retrieve(sub_query):
        # Deterministic, overlapping across sub-queries so dedup and the cap both bite.
        base = abs(hash(sub_query)) % 7
        return [f"f{(base + i) % 11}" for i in range(4)]

    assert ALL_QUESTIONS, "ALL_QUESTIONS is empty -- this loop would assert nothing (dead-anchor census, 2026-08-22)"
    for q in ALL_QUESTIONS:
        subs = decomposition_v15.decompose_query(q)
        assert (pipeline_v15.pool_facts(fake_retrieve, subs)
                == baseline.baseline_pool_facts(fake_retrieve, subs)), q


def test_pool_facts_caps_at_nine_and_preserves_first_seen_order():
    facts = pipeline_v15.pool_facts(lambda q: [f"{q}-{i}" for i in range(5)],
                                    ["a", "b", "c"])
    assert len(facts) == 9
    assert facts[:5] == [f"a-{i}" for i in range(5)]


# ── prompt build: the two messages, and the raising-tokenizer fallback ───────────

class _StubTokenizer:
    def __init__(self, raises=False):
        self.raises = raises
        self.seen = None

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        if self.raises:
            raise RuntimeError("no chat template")
        self.seen = messages
        return "PROMPT::" + json.dumps(messages, ensure_ascii=False)


def test_build_messages_is_byte_identical_to_the_inline_build_across_the_corpus():
    system_prompt = prompting.load_system_prompt()
    facts = ["ukweli mmoja", "ukweli mbili"]
    assert ALL_QUESTIONS, "ALL_QUESTIONS is empty -- this loop would assert nothing (dead-anchor census, 2026-08-22)"
    for q in ALL_QUESTIONS:
        assert (pipeline_v15.build_messages(q, facts, system_prompt)
                == baseline.baseline_build_messages(
                    q, facts, system_prompt,
                    prompting.build_enriched_system, prompting.ensure_terminal_punct)), q


def test_build_prompt_preserves_productions_header_fallback_not_naive_concat():
    """chike.prompting.build_chat_prompt falls back to naive-concat; PRODUCTION falls back to
    the Llama-3 header format when apply_chat_template RAISES. Different strings on a path
    that only fires when the tokenizer misbehaves — exactly the silent divergence the
    extraction exists to prevent."""
    out = pipeline_v15.build_prompt("Swali?", ["ukweli"], "SYS", _StubTokenizer(raises=True))
    assert out.startswith("<|begin_of_text|><|start_header_id|>system<|end_header_id|>")
    assert out.endswith("<|start_header_id|>assistant<|end_header_id|>\n\n")
    assert "SYS" in out and "Swali?" in out


def test_build_prompt_uses_the_tokenizer_template_when_it_works():
    tok = _StubTokenizer()
    out = pipeline_v15.build_prompt("Swali?", ["ukweli"], "SYS", tok)
    assert out.startswith("PROMPT::")
    assert tok.seen == pipeline_v15.build_messages("Swali?", ["ukweli"], "SYS")


# ── postprocess: proved against 400 REAL persisted generations ───────────────────

def _persisted_raw_generations():
    path = os.path.join(_ROOT, _GENERATIONS)
    if not os.path.exists(path):
        pytest.skip(f"{_GENERATIONS} not present")
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)["results"]
    return [r.get("raw_generated") or "" for r in rows]


def test_postprocess_is_byte_identical_on_400_persisted_generations():
    raws = _persisted_raw_generations()
    assert len(raws) == 400, len(raws)
    stops = generation_cleanup.STOP_STRINGS
    diffs = [i for i, raw in enumerate(raws)
             if pipeline_v15.postprocess(raw, stops)
             != baseline.baseline_postprocess(raw, stops, generation_cleanup.clean_reply)]
    assert diffs == [], f"{len(diffs)} generations clean differently, e.g. rows {diffs[:5]}"


def test_postprocess_actually_does_something_on_this_corpus():
    # Guards the test above from passing vacuously (e.g. if raw_generated were all empty).
    raws = _persisted_raw_generations()
    stops = generation_cleanup.STOP_STRINGS
    changed = sum(1 for raw in raws if pipeline_v15.postprocess(raw, stops) != raw.strip())
    assert changed > 20, f"only {changed} generations were altered by postprocess"


# ── answer(): stage order and the no-model-call guarantees ───────────────────────

def _answer(message, **over):
    calls = {"generate": 0, "retrieve": 0}

    def generate(prompt):
        calls["generate"] += 1
        return "Jibu la mfano."

    def retrieve_facts(q):
        calls["retrieve"] += 1
        return ["ukweli"]

    kwargs = dict(generate=generate, retrieve_facts=retrieve_facts,
                  system_prompt="SYS", tokenizer=_StubTokenizer(),
                  stop_strings=generation_cleanup.STOP_STRINGS)
    kwargs.update(over)
    return pipeline_v15.answer(message, **kwargs), calls


def test_ooc_question_refuses_with_the_shared_text_and_never_calls_the_model():
    out, calls = _answer("Niliuza nyumba yangu, kodi ya faida ya mtaji ni ngapi?")
    from chike import classification

    assert out["reply"] == classification.REFUSAL_TEXT
    assert calls == {"generate": 0, "retrieve": 0}


def test_payroll_amount_with_no_figure_clarifies_and_never_calls_the_model():
    out, calls = _answer("Nina wafanyakazi, PAYE yangu ni shilingi ngapi kwa mwezi?")
    assert out["reply"] == pipeline_v15.PAYROLL_CLARIFICATION
    assert calls == {"generate": 0, "retrieve": 0}


def test_payroll_clarification_is_the_shared_constant_not_a_fourth_copy():
    from chike import clarification

    assert pipeline_v15.PAYROLL_CLARIFICATION is clarification.PAYROLL_AMOUNT


def test_empty_message_returns_productions_error_contract():
    out, calls = _answer("   ")
    assert out == {"error": "No message provided"}
    assert calls == {"generate": 0, "retrieve": 0}


def test_fact_question_generates_once_and_retrieves_per_sub_query():
    q = "Kiwango cha SDL ni asilimia ngapi?"
    out, calls = _answer(q)
    assert out["reply"] == "Jibu la mfano."
    assert calls["generate"] == 1
    assert calls["retrieve"] == len(decomposition_v15.decompose_query(q))


# ── drift guards on the files that were collapsed ────────────────────────────────

def _src(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _defined_names(rel):
    """Top-level function/assignment names actually DEFINED in a file. Parsed, not
    text-matched — a grep-style assertion here false-positives on the comments that explain
    why the thing was removed."""
    import ast

    tree = ast.parse(_src(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def _imported_modules(rel):
    import ast

    mods = set()
    for node in ast.walk(ast.parse(_src(rel))):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add(("." * node.level) + (node.module or ""))
    return mods


def test_modal_app_no_longer_defines_its_own_pipeline_or_decomposer():
    names = _defined_names("chike-inference/modal_app.py")
    assert "decompose_query" not in names
    assert "MULTI_PART_SIGNALS" not in names
    assert "_split_enumeration" not in names
    assert "from chike import pipeline_v15" in _src("chike-inference/modal_app.py")
    assert "pipeline_v15.answer(" in _src("chike-inference/modal_app.py")


def test_modal_app_passes_its_own_single_arm_retriever_not_the_two_arm_hybrid():
    """NARROWED 2026-08-24, and the reason is the R17 corollary about proxies.

    This used to assert that `chike.retrieval` is not IMPORTED at all, as a proxy for 'does not
    use the two-arm hybrid'. The proxy was wrong: the module contains TWO separable things — the
    two-arm `Retriever.retrieve()` (which production must not use) and the FAIL-LOUD INDEX
    LOADER (which production must use, and did not).

    Production's own loader kept the exact silent fallback the contract was written to remove —
    a missing index printed a warning and every answer was generated with no facts at all. The
    import ban is part of why that was never fixed: it made the correct fix look like a
    violation. So the assertion now pins the thing it actually cares about — WHICH RETRIEVER IS
    INJECTED — and says nothing about imports.
    """
    src = _src("chike-inference/modal_app.py")
    code = "\n".join(ln for ln in src.splitlines()
                     if ln.strip() and not ln.strip().startswith("#"))
    # the v15 path and the v16 orchestrator must BOTH be handed production's own method
    assert "retrieve_facts=self.retrieve_facts" in code
    assert "retriever=self.retrieve_facts" in code
    # and the two-arm hybrid must never be CALLED, however the module is imported
    assert ".retrieve(" not in code, (
        "modal_app calls a Retriever.retrieve() — that is the TWO-ARM hybrid. The 2026-08-24 "
        "full A/B kept single-arm (eval/results/ab_retriever_full_adjudication.json)."
    )
    assert "chike.retrieval import retrieve" not in code


def test_eval_py_uses_the_shared_leaf_decomposer():
    names = _defined_names("kaggle/eval.py")
    assert "decompose_query" in names          # bound from the fetched module...
    assert "MULTI_PART_SIGNALS" not in names   # ...not re-declared inline
    assert "_split_enumeration" not in names
    assert "_fetch_chike_module('decomposition_v15')" in _src("kaggle/eval.py")


def test_decomposition_v15_stays_a_leaf_module_so_eval_py_can_exec_it():
    # eval.py fetches and exec()s it standalone; any chike-internal import would break that.
    mods = _imported_modules("chike/decomposition_v15.py")
    assert mods <= {"re", "typing"}, mods            # stdlib only
    assert not [m for m in mods if m.startswith(".") or m.startswith("chike")]
