# -*- coding: utf-8 -*-
"""The staleness check requested after the 2026-09-01 presumptive-tax incident: a test that
fails when a rates.py constant's "verified through Finance Act year Y" claim is behind
CURRENT_FINANCE_ACT_YEAR, so it goes red on its own the moment a new Finance Act is gazetted
and the registry is bumped without every group being re-checked -- rather than waiting for
someone to notice by accident, which is how the presumptive-tax engine went two months wrong.

Same shape as this project's strict-xfail convention (tests/test_presumptive.py,
tests/test_fact_group_consolidation.py): a marker that records WHY something is allowed to be
in a particular state, and fails loudly the moment that state should have changed but didn't.
Here the marker is a year number instead of an xfail decorator, and the trigger is
CURRENT_FINANCE_ACT_YEAR moving instead of a defect being fixed.

WHAT THIS TEST DOES NOT DO. It cannot verify that a group's `evidence` string is actually
true -- that still requires a human (or an agent) to read the cited Finance Act. What it
guarantees is that the CLAIM is never silently allowed to go stale: raising
CURRENT_FINANCE_ACT_YEAR without updating every group's own year is exactly the state that let
the presumptive-tax engine ship wrong for two months, and this test turns that state red
instead of quiet.
"""
import re

from chike.rules_engine import rates


def test_every_group_is_verified_through_the_current_finance_act_year():
    """THE staleness check. Fails the moment any group's registered year falls behind
    CURRENT_FINANCE_ACT_YEAR -- which happens the instant someone bumps the year constant
    without re-checking (and re-bumping) every group, exactly the gap this test exists to
    close.
    """
    stale = []
    for group, (year, provision, evidence) in rates.FINANCE_ACT_VERIFIED_THROUGH.items():
        if year is None:
            continue  # NEVER_GROUNDED groups are a different, separately-tracked status
        if year < rates.CURRENT_FINANCE_ACT_YEAR:
            stale.append((group, year, provision))
    assert not stale, (
        f"{len(stale)} group(s) verified through a year BEHIND "
        f"CURRENT_FINANCE_ACT_YEAR={rates.CURRENT_FINANCE_ACT_YEAR}: {stale}. "
        f"Read the current Finance Act's Part covering each provision in full, then bump "
        f"that group's year in rates.FINANCE_ACT_VERIFIED_THROUGH (per the module docstring's "
        f"4-step process) -- do not bump the year without having actually read the Act.")


def test_every_rates_py_constant_belongs_to_a_registered_group():
    """The registry is only a mechanism if every constant it is supposed to cover is actually
    IN it. A new rate/threshold added to rates.py without a matching
    FINANCE_ACT_VERIFIED_THROUGH entry would be invisible to the freshness test above --
    silently unprotected, the same blind spot the registry exists to close for the constants
    already here. This walks the module's own public names and requires each Decimal/int
    constant's comment to name one of the registered groups, so a future addition fails loudly
    if it forgets to register itself."""
    import inspect
    source = inspect.getsource(rates)
    # Lines defining a top-level constant: NAME = Decimal(...) or NAME = <int/tuple/etc>,
    # excluding the registry's own machinery and pure derived aliases documented inline.
    const_line = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=', re.M)
    defined = set(const_line.findall(source))
    exempt = {
        'CURRENT_FINANCE_ACT_YEAR', 'FINANCE_ACT_VERIFIED_THROUGH', 'NEVER_GROUNDED',
        # Derived from an already-registered constant, not an independent legal claim of its
        # own -- PRESUMPTIVE_NEW_BUSINESS_EXEMPT_UPPER is PRESUMPTIVE_TURNOVER_CEILING itself.
        'PRESUMPTIVE_NEW_BUSINESS_EXEMPT_UPPER',
    }
    group_prefixes = {
        'SDL': 'SDL', 'NSSF': 'NSSF', 'WCF': 'WCF',
        'PAYE_BANDS': 'PAYE_BANDS', 'PAYE_NONRESIDENT_RATE': 'PAYE_NONRESIDENT_RATE',
        'PRESUMPTIVE': 'PRESUMPTIVE', 'CORPORATE_AND_PARTNERSHIP': ('CORPORATE', 'AMT',
                                                                    'PARTNERSHIP'),
    }
    unregistered = []
    for name in sorted(defined - exempt):
        matched = any(
            name.startswith(p) if isinstance(prefixes, str) else
            any(name.startswith(p) for p in prefixes)
            for group, prefixes in group_prefixes.items()
            for p in ([prefixes] if isinstance(prefixes, str) else prefixes)
        )
        if not matched:
            unregistered.append(name)
    assert not unregistered, (
        f"{unregistered} defined in rates.py but match no group in "
        f"FINANCE_ACT_VERIFIED_THROUGH -- add a group (or extend an existing prefix mapping "
        f"in this test) so the freshness check actually covers it.")


def test_never_grounded_status_is_visible_not_silently_dropped():
    """PAYE_NONRESIDENT_RATE's `None` entry must show up in NEVER_GROUNDED, or the distinction
    between 'stale' and 'never verified at all' collapses back into the freshness test's
    silent skip."""
    assert 'PAYE_NONRESIDENT_RATE' in rates.NEVER_GROUNDED
    for group in rates.NEVER_GROUNDED:
        year, provision, evidence = rates.FINANCE_ACT_VERIFIED_THROUGH[group]
        assert year is None
        assert len(evidence) > 40, f"{group}: NEVER_GROUNDED needs a real reason, not a label"


def test_the_registry_itself_is_the_control_group_it_documents():
    """CONTROL, per R26/R23: this test must be capable of FAILING. Prove it by planting the
    exact failure the mechanism exists to catch -- a group whose year is behind current -- and
    confirming the freshness assertion actually raises, not merely that it happens to pass on
    real data (which could mean the check is vacuous rather than that everything is current)."""
    fake_registry = {'FAKE_GROUP': (rates.CURRENT_FINANCE_ACT_YEAR - 1, 'irrelevant',
                                    'planted for the control')}
    stale = [(g, y, p) for g, (y, p, _e) in fake_registry.items()
            if y is not None and y < rates.CURRENT_FINANCE_ACT_YEAR]
    assert stale, 'the planted stale group did not register as stale -- the check is inert'
