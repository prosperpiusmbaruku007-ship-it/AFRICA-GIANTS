"""th_16 regression — GN 605A's minimum wage is a FLOOR, not a ceiling.

Production told an employer that paying TZS 200,000 to a farm worker was unlawful because it
"exceeded the maximum minimum wage" (kiwango cha juu cha chini — a construct that does not
exist in Tanzanian law), and repeated it in two independent runs. Verified against the gazette
itself: GN 605A paragraph 4(3) says "an employer may pay such employee an amount above the
minimum wage prescribed in respective sector or area" (kazi.go.tz official PDF, Special
Supplement No. 9 of 13 Oct 2025).

The cause was an ABSENT fact, not a wrong one: before the fix, 0 of 7 realistic Swahili
minimum-wage queries retrieved any GN 605A fact (best rank #22-#52), while 7 of 8 other domains
hit rank 1 — GN 605A existed in the index only as long English `key: value` text keyed on the
notice number, reachable by asking for "GN 605A" and by nothing a user actually says.

Two tiers, deliberately:
  * The structural tests are model-free and always run. Their real job is to catch an R15
    violation — a locked_facts edit that never reached the RAG index — which is invisible to
    any test that only reads locked_facts.json.
  * The integration test needs e5 and the real index, and skips cleanly without them.

Probe corpus: eval/accuracy_gate/minimum_wage_floor_probes_030.jsonl.
"""
import json
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCKED = os.path.join(REPO, "scripts", "locked_facts.json")
PROBES = os.path.join(REPO, "eval", "accuracy_gate",
                      "minimum_wage_floor_probes_030.jsonl")
KEY = "GN605A_minimum_is_a_floor_not_a_ceiling"

# The retrieval text's opening words. Matching on the fact's own lead rather than on the
# locked-facts key is deliberate: the RAG index stores the CONCISE text, not the key, so this
# is what actually has to be present in the shipped index.
LEAD = "Nampa mfanyakazi wangu mshahara kwa mwezi"


def _load(name):
    with open(os.path.join(REPO, name), encoding="utf-8") as f:
        return json.load(f)


def _probes():
    with open(PROBES, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_locked_fact_present_and_sourced():
    fact = _load("scripts/locked_facts.json")[KEY]
    assert "may pay such employee an amount above the minimum wage" in fact["fact"], \
        "the operative gazette words must be quoted, not paraphrased"
    assert "kazi.go.tz" in fact["primary_source"], "primary source must be the Tier 1A gazette"
    assert fact["status"] == "LOCKED"


@pytest.mark.parametrize("index_dir", ["kaggle", "chike-inference"])
def test_floor_fact_is_in_the_shipped_rag_index(index_dir):
    """R15: editing locked_facts.json without regenerating leaves the index serving stale
    facts while the source data reads correct. This is the check that notices."""
    texts = _load(f"{index_dir}/rag_facts_text.json")
    hits = [t for t in texts if t.startswith(LEAD)]
    assert len(hits) == 1, f"{index_dir}: expected exactly one floor fact, found {len(hits)}"
    body = hits[0]
    assert "si kiwango cha juu" in body, "must deny the ceiling reading explicitly"
    assert "175,000" in body, "must carry the agricultural/default floor"


def test_both_index_copies_agree():
    """chike-inference/ and kaggle/ are two copies of one index; a partial R15 update that
    refreshes only one is the failure this catches."""
    a = _load("kaggle/rag_facts_text.json")
    b = _load("chike-inference/rag_facts_text.json")
    assert a == b, "kaggle/ and chike-inference/ fact texts have diverged"


@pytest.mark.parametrize("index_dir", ["kaggle", "chike-inference"])
def test_index_embeddings_match_text_count(index_dir):
    np = pytest.importorskip("numpy")
    emb = np.load(os.path.join(REPO, index_dir, "rag_embeddings.npy"))
    texts = _load(f"{index_dir}/rag_facts_text.json")
    assert emb.shape[0] == len(texts), \
        f"{index_dir}: {emb.shape[0]} embeddings vs {len(texts)} texts — half-regenerated"


def test_wrong_patterns_catch_the_live_defect():
    """The exact strings production emitted, in both runs, must be flagged."""
    patterns = _load("scripts/locked_facts.json")[KEY]["wrong_patterns"]
    observed = [
        "Hapana, malipo hayo yanazidi kiwango cha juu cha chini cha mshahara "
        "kinachoruhusiwa kisheria.",
        "Hapana — malipo hayo yanazidi kiwango cha juu cha chini cha lazima cha kisheria. "
        "Kwa mujibu wa Sheria ya Ajira na Mahusiano ya Kazini, mfanyakazi wa shamba anaweza "
        "kulipwa kiwango cha chini cha TZS 175,000 tu. Malipo ya ziada juu ya hapo ni "
        "kinyume cha sheria.",
    ]
    for text in observed:
        assert any(re.search(p, text.lower()) for p in patterns), \
            f"no wrong_pattern matches the observed defect: {text[:60]}"


def test_wrong_patterns_do_not_flag_lawful_phrasings():
    """R17: the patterns were swept clean over 149,983 stored strings, which proves only that
    the corpus does not contain the risky forms. These are authored to contain them — the
    legitimate ways to talk about the HIGHEST minimum rate, which must not be flagged."""
    patterns = _load("scripts/locked_facts.json")[KEY]["wrong_patterns"]
    lawful = [
        "Kiwango cha juu zaidi cha mshahara wa chini chini ya GN 605A ni TZS 765,900.",
        "Kima cha juu kabisa cha mshahara wa GN 605A ni TZS 765,900 kwa sekta ya nishati.",
        "Mwajiri anaruhusiwa kulipa zaidi ya kima cha chini; ni halali kabisa.",
        "Kulipa chini ya kima cha chini ni kinyume cha sheria.",
        "Mfanyakazi wa shamba anaweza kulipwa TZS 175,000 au zaidi kwa mwezi.",
        "The maximum rate among the minimum wages is TZS 765,900 for the energy sector.",
        "Paying above the minimum wage is lawful under paragraph 4(3).",
    ]
    for text in lawful:
        hit = [p for p in patterns if re.search(p, text.lower())]
        assert not hit, f"pattern {hit} false-positives on a lawful phrasing: {text}"


def test_probe_file_shape():
    rows = _probes()
    assert len(rows) == 30
    assert sum(r["kind"] == "target" for r in rows) == 8
    assert sum(r["kind"] == "r17_displacement" for r in rows) == 22
    for r in rows:
        assert r["guards_against"], f"{r['id']} has no guards_against note"
    known = [r["id"] for r in rows if r.get("known_miss")]
    assert known == ["t_hotel"], (
        "t_hotel is the one accepted miss (it needs the hotel sector floor). A new known_miss "
        "means a target was quietly downgraded instead of fixed."
    )
    gaps = sorted(r["id"] for r in rows
                  if r["kind"] == "r17_displacement"
                  and not r["baseline_had_required_fact"])
    assert gaps == ["p_05", "p_09", "p_11", "p_16"], (
        "the recorded pre-existing retrieval gaps changed. These four probes retrieved no "
        "relevant fact before the floor entry existed; if the set moves, the baseline was "
        "re-derived against a different index and the non-regression claim below is no "
        "longer anchored."
    )


@pytest.mark.integration
def test_real_index_serves_the_floor_probes():
    """The end-to-end claim: on the real index, with production's own Retriever (including the
    numeric second arm), the floor fact reaches the injected set for every target except the
    documented t_hotel — and no R17 displacement probe loses the fact it needs."""
    pytest.importorskip("sentence_transformers")
    import sys
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from chike.retrieval import Retriever

    try:
        r = Retriever(emb_path=os.path.join(REPO, "kaggle", "rag_embeddings.npy"),
                      texts_path=os.path.join(REPO, "kaggle", "rag_facts_text.json"))
        r._ensure_index()
        r._ensure_embed_model()
    except Exception as e:                                        # offline / no model
        pytest.skip(f"e5 model or index unavailable: {e}")

    texts = _load("kaggle/rag_facts_text.json")
    floor = next(t for t in texts if t.startswith(LEAD))

    for row in _probes():
        got = r.retrieve(row["question_sw"])
        if row["kind"] == "target":
            if row.get("known_miss"):
                continue
            assert floor in got, (
                f'{row["id"]}: floor fact not injected — {row["guards_against"]}')
        elif row["baseline_had_required_fact"]:
            # Non-regression, not absolute correctness: four probes (p_05/p_09/p_11/p_16)
            # retrieved no relevant fact BEFORE this change either. Asserting they pass would
            # make this test fail for a defect it did not cause and cannot fix; asserting
            # nothing would let a real eviction hide. So the baseline is recorded per row in
            # the probe file and the claim is exactly "nothing that worked stopped working".
            assert any(row["must_retrieve"].lower() in g.lower() for g in got), (
                f'{row["id"]}: lost its required "{row["must_retrieve"]}" fact — the floor '
                f'entry has become a generic wage magnet')
