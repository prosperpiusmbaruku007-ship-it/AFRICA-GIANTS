"""Tests for data cleaning and deduplication pipeline."""
import pytest
from src.common.schemas import ScrapedDocument, CleanedDocument
from src.process.clean import clean_documents
from src.process.deduplicate import deduplicate_documents


def _make_scraped(url: str, content: str, source: str = "TRA") -> ScrapedDocument:
    return ScrapedDocument(
        url=url,
        source_name=source,
        title="Test Doc",
        raw_content=content,
        scraped_at="2026-01-01T00:00:00",
    )


def test_clean_removes_html():
    doc = _make_scraped("https://tra.go.tz/", "<p>Tax <b>registration</b> in Tanzania.</p>")
    cleaned = clean_documents([doc])
    assert "<p>" not in cleaned[0].cleaned_content
    assert "Tax" in cleaned[0].cleaned_content


def test_clean_detects_swahili():
    content = "Usajili wa biashara nchini Tanzania ni muhimu kwa kodi na leseni."
    doc = _make_scraped("https://brela.go.tz/", content)
    cleaned = clean_documents([doc])
    assert cleaned[0].language == "sw"


def test_clean_detects_english():
    content = "Business registration in Tanzania requires a TIN number and a valid license."
    doc = _make_scraped("https://tra.go.tz/", content)
    cleaned = clean_documents([doc])
    assert cleaned[0].language == "en"


def test_clean_skips_empty_content():
    doc = _make_scraped("https://tra.go.tz/", "   ")
    cleaned = clean_documents([doc])
    assert len(cleaned) == 0


def test_clean_normalizes_whitespace():
    doc = _make_scraped("https://tra.go.tz/", "Hello   world.\n\nNext  line.")
    cleaned = clean_documents([doc])
    assert "  " not in cleaned[0].cleaned_content


def test_deduplicate_removes_exact_duplicates():
    base = "Business registration in Tanzania requires TIN and license documents."
    docs = [
        CleanedDocument(doc_id=f"doc_{i}", source_name="TRA", url="https://tra.go.tz/",
                        cleaned_content=base, language="en", cleaned_at="2026-01-01T00:00:00")
        for i in range(3)
    ]
    unique = deduplicate_documents(docs)
    assert len(unique) == 1


def test_deduplicate_keeps_different_docs():
    docs = [
        CleanedDocument(doc_id="doc_1", source_name="TRA", url="https://tra.go.tz/",
                        cleaned_content="Tax registration in Tanzania.", language="en",
                        cleaned_at="2026-01-01T00:00:00"),
        CleanedDocument(doc_id="doc_2", source_name="BRELA", url="https://brela.go.tz/",
                        cleaned_content="Company incorporation requirements at BRELA.", language="en",
                        cleaned_at="2026-01-01T00:00:00"),
    ]
    unique = deduplicate_documents(docs)
    assert len(unique) == 2


# ── the .go.ke rewrite, removed 2026-08-24 ───────────────────────────────────────

def test_a_kenyan_authority_domain_survives_cleaning():
    """REGRESSION PIN for a rewrite that manufactured a wrong citation.

    `.go.ke` -> `.go.tz` was live and fired on 21 corpus rows, every one of them CORRECT: an
    out-of-scope refusal naming Kenya's own regulator. It turned `kra.go.ke` into `kra.go.tz`, a
    domain that does not exist — the model declined a question outside its scope, named the right
    foreign authority, and the repair layer replaced its citation with a fabrication.

    If anyone reinstates it, this fails first.
    """
    from chike.generation_cleanup import clean_generated_reply
    body = ("Kwa maswali ya Kenya tafadhali wasiliana na Kenya Revenue Authority (KRA) "
            "kwa kra.go.ke.")
    assert clean_generated_reply(body) == body
    assert "kra.go.tz" not in clean_generated_reply(body)


def test_the_dead_nssf_domain_is_still_rewritten():
    """The OTHER content rewrite stays. Unlike .go.ke it contains a real authoring defect —
    1,374 corpus occurrences of a domain CLAUDE.md records as DNS-failing — and there is no
    context in which nssf.or.tz is the correct citation, so it can damage nothing."""
    from chike.generation_cleanup import clean_generated_reply
    assert clean_generated_reply("Thibitisha na nssf.or.tz.") == "Thibitisha na nssf.go.tz."


def test_exactly_two_content_rewrites_exist_and_both_are_justified_in_writing():
    """R25 pin. A content rewrite may only be added with its justification recorded AT THE SITE:
    what corpus defect it repairs, and what correct output it could damage. Neither of the two
    original rewrites had that, and one of them turned out to be corrupting correct answers.

    Counting the substitutions in the source is crude, and deliberately so — it fails when
    someone adds a third without touching this test, which is the moment to write the
    justification down."""
    import inspect
    from chike import generation_cleanup
    src = inspect.getsource(generation_cleanup.clean_generated_reply)
    domain_subs = [ln for ln in src.splitlines()
                   if "re.sub(" in ln and (".tz" in ln or ".ke" in ln)]
    assert len(domain_subs) == 1, (
        f"expected exactly 1 domain rewrite, found {len(domain_subs)}: {domain_subs}\n"
        f"If you added one, record at the site what corpus defect it repairs and what correct "
        f"output it could damage (R25), then update this count in the same commit.")
