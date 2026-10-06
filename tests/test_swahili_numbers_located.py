# -*- coding: utf-8 -*-
"""`parse_amounts` AND `parse_amounts_located` MUST SEE THE SAME AMOUNTS.

WHY THIS IS NOT A FORMALITY. D-FIDELITY-7's narrowing turns on POSITIONS — whether a threshold
frame word reaches an amount without crossing another amount. The bare value list cannot answer
that, so `parse_amounts_located` was extracted from `parse_amounts` on 2026-10-06.

If the two ever diverge, the guard reasons about an amount list that no other caller sees, and
every conclusion drawn from it is about a parse the pipeline does not perform. That is R24's
baseline-reproduction failure arriving in a parser: an arm agreeing with production for the wrong
reason. The cheap defence is to make one delegate to the other and assert it — which is what this
file does, over text drawn from the corpora rather than invented, because invented inputs test
the inventor's idea of Swahili money (R33).
"""
import json
import os
import random

import pytest

from chike.swahili_numbers import parse_amounts, parse_amounts_located

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _corpus_bodies(limit=400):
    """Real answer prose, not invented strings."""
    out = []
    for rel in ("datasets/tier1a/cleaned_pairs", "datasets/tier1a/sft_shaped_pairs"):
        d = os.path.join(REPO, *rel.split("/"))
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(d, name), encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    body = obj.get("answer_sw") or obj.get("output") or ""
                    if body:
                        out.append(body)
    random.Random(20261006).shuffle(out)
    return out[:limit]


BODIES = _corpus_bodies()


def test_the_corpus_sample_is_real_and_exercises_the_parser():
    """R20: an empty sample makes every assertion below vacuous, and a sample containing no money
    makes them vacuous in a way that still looks like a pass."""
    assert len(BODIES) >= 300, f"only {len(BODIES)} corpus bodies sampled"
    with_money = [b for b in BODIES if parse_amounts(b)]
    assert len(with_money) >= 100, (
        f"only {len(with_money)} of {len(BODIES)} sampled bodies contain any amount — a "
        f"positions test over text with no numbers in it proves nothing")


def test_the_two_entry_points_agree_on_every_corpus_body():
    for body in BODIES:
        assert parse_amounts(body) == [v for _, v in parse_amounts_located(body)], body[:160]


def test_offsets_are_ascending_and_point_inside_the_text():
    for body in BODIES:
        located = parse_amounts_located(body)
        positions = [p for p, _ in located]
        assert positions == sorted(positions), f"offsets not ascending: {body[:160]}"
        for p, _ in located:
            assert 0 <= p < len(body), f"offset {p} outside a {len(body)}-char body"


@pytest.mark.parametrize("text,expect", [
    ("Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000.", [11_000_000]),
    ("Kwa mauzo ya TZS 250,000,000 (zaidi ya TZS 200,000,000)",
     [250_000_000, 200_000_000]),
    ("chini ya milioni 10", [10_000_000]),
])
def test_the_offsets_land_on_the_figures_a_reader_would_point_at(text, expect):
    located = parse_amounts_located(text)
    assert [int(v) for _, v in located] == expect, located
    for pos, value in located:
        # the offset must sit at or just before the digits/word-number, not elsewhere
        assert text[pos:pos + 24].strip(), f"offset {pos} lands on whitespace in {text!r}"
