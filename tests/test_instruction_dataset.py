"""Tests for the clean instruction dataset builder."""
import os
import json
import tempfile
import pytest
from src.process.build_instruction_dataset import SEED_EXAMPLES, build_instruction_dataset


def test_seed_examples_have_required_fields():
    assert SEED_EXAMPLES, "SEED_EXAMPLES is empty -- this loop would assert nothing (dead-anchor census, 2026-08-22)"
    for ex in SEED_EXAMPLES:
        assert "instruction" in ex, f"Missing instruction: {ex}"
        assert "output" in ex, f"Missing output: {ex}"
        assert "category" in ex, f"Missing category: {ex}"
        assert "language" in ex, f"Missing language: {ex}"
        assert ex["language"] in ("sw", "en"), f"Invalid language: {ex['language']}"


def test_seed_examples_not_forum_continuations():
    """Ensure no example output starts with forum artefacts."""
    bad_patterns = ["JamiiForums", "Discussion in", "started by", "| The Home of"]
    assert SEED_EXAMPLES, "SEED_EXAMPLES is empty -- this loop would assert nothing (dead-anchor census, 2026-08-22)"
    for ex in SEED_EXAMPLES:
        # (no assertion on bad_patterns: it is a literal defined two lines above, so an
        # assertion on it could never fail — an inert check by construction.)
        for pattern in bad_patterns:
            assert pattern not in ex["output"], f"Forum artefact in seed example: {ex['instruction']}"


def test_seed_examples_cover_both_languages():
    langs = {ex["language"] for ex in SEED_EXAMPLES}
    assert "sw" in langs
    assert "en" in langs


def test_seed_examples_cover_multiple_categories():
    cats = {ex["category"] for ex in SEED_EXAMPLES}
    assert len(cats) >= 5


def test_build_instruction_dataset_writes_file(tmp_path):
    out = str(tmp_path / "test_instruction.jsonl")
    examples = build_instruction_dataset(include_forums=False, output_path=out)
    assert len(examples) == len(SEED_EXAMPLES)
    assert os.path.exists(out)

    rows = []
    with open(out, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    assert len(rows) == len(SEED_EXAMPLES)


def test_build_instruction_dataset_valid_jsonl(tmp_path):
    out = str(tmp_path / "valid.jsonl")
    build_instruction_dataset(include_forums=False, output_path=out)
    with open(out, "r", encoding="utf-8") as f:
        # NON-EMPTY ASSERTION on the CONTENT, not the handle. `assert f` would be always-true
        # — an inert check, which is the very thing the 2026-08-22 census was removing.
        written = f.readlines()
        assert written, f"{out} has no lines — this loop would assert nothing"
        for line in written:
            if not line.strip():
                continue
            row = json.loads(line)
            assert "instruction" in row
            assert "output" in row
