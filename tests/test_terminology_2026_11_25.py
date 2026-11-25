"""2026-11-25 (founder decision 1): "ukaazi wa kikodi" widened from the residency statement to the band-table and rate statements and the engine:paye non-resident working line. USER-FACING LABELS ONLY: the internal identifiers
(rates.PAYE_NONRESIDENT_RATE, the topic names, the guard topic names) are unchanged. A census of the bare uses that REMAIN in other topics' served text is pinned shrink-only, so they stay visible."""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike.rules_engine import fixed_statements as fs   # noqa: E402
from chike.rules_engine import paye as paye_engine      # noqa: E402
from decimal import Decimal                              # noqa: E402

_BARE = re.compile(r"(?i)(?<![a-z])(?:mkazi|wakazi|ukazi)(?![a-z])")


@pytest.mark.parametrize("topic", ["paye_band_table", "paye_rate", "levy_rates_three", "paye_residency"])
def test_band_rate_and_residency_statements_use_ukaazi_wa_kikodi(topic):
    t = fs.fixed_statement(topic).working
    assert "mkaazi wa kikodi" in t.lower() or "ukaazi wa kikodi" in t.lower(), topic
    assert not _BARE.search(t), (topic, _BARE.search(t).group(0), "a bare 'mkazi' reads as the immigration residence permit")


def test_the_generated_band_text_is_the_one_source_for_all_three_statements():
    bands = fs._paye_bands_text()
    assert "(mkaazi wa kikodi, 2025/26)" in bands and "Asiye mkaazi wa kikodi analipa 15% tambarare (kodi ya mwisho, si mabano)" in bands
    for topic in ("paye_band_table", "paye_rate", "levy_rates_three"):
        assert bands in fs.fixed_statement(topic).working, topic


def test_the_engine_nonresident_working_line_carries_the_label_and_the_figures_are_unchanged():
    r = paye_engine.compute_paye(Decimal("5000000"), resident=False)
    assert r.amount == Decimal("750000") and "PAYE (asiye mkaazi wa kikodi) = 15%" in r.working and "si mabano" in r.working
    assert not _BARE.search(r.working)


def test_internal_identifiers_are_unchanged():
    from chike.rules_engine import rates
    assert hasattr(rates, "PAYE_NONRESIDENT_RATE") and rates.PAYE_NONRESIDENT_RATE == Decimal("0.15")
    assert "paye_band_table" in fs.TOPICS and "paye_rate" in fs.TOPICS and "paye_residency" in fs.TOPICS


def test_census_of_the_bare_uses_that_remain_in_other_served_text_is_shrink_only():
    """Other topics' served strings that still say 'mkazi' / 'wakazi' (dividends, professional fees, severance, rent, the TIN statement, the residency CLARIFICATION). Out of this decision's scope (band / rate statements only); pinned so they stay visible and can only shrink."""
    n = 0
    for rel in ("chike/clarification.py", "chike/rules_engine/fixed_statements.py", "chike/rules_engine/rent_wht.py", "chike/rules_engine/paye.py"):
        for line in io.open(os.path.join(_ROOT, rel), encoding="utf-8"):
            code = line.split("#", 1)[0] if line.lstrip().startswith("#") else line
            if line.lstrip().startswith("#"):
                continue
            n += len(_BARE.findall(code))
    assert n <= 12, f"{n} bare uses (was 12 on 2026-11-25: clarification 6, fixed_statements 4 incl. two in the residency note that QUOTE the forbidden word, rent_wht 2); a NEW one means the terminology decision is being undone"
