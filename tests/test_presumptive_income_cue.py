"""R17 regression file for the bare `kodi ya mapato` presumptive cue (2026-08-23).

WHAT THIS FILE IS FOR. `_BUSINESS_INCOME_TAX_CUES` required the QUALIFIED forms — "kodi ya
mapato YA BIASHARA / YA DUKA" — so the commonest phrasing of the commonest duka tax question
fell to the fact path while the technical term `makadirio` reached the engine:

    "Nina duka dogo, mauzo yangu ni milioni 30 kwa mwaka. Nalipa kodi ya mapato kiasi gani?"
        -> `none`          (before)
    "Biashara yangu inauza milioni 4 kwa mwaka, kodi ya makadirio ni ngapi?"
        -> `presumptive`   (before and after)

AN ENGINE REACHABLE ONLY BY THE TECHNICAL TERM SERVES THE USERS WHO LEAST NEED IT.

THE CLEAN SWEEP PROVED NOTHING, AND THIS FILE IS THE PART THAT DID THE WORK. The corpus sweep
over 475 rows (400 gate + 48 natural + 27 in-scope adversarial) moved **ZERO** rows on BOTH
candidate arms — with and without the entity veto. It was an authored probe, `pic_04`, that
found the defect: `_PRESUMPTIVE_TURNOVER_CUES` contains "nauza", a SUBSTRING of "i-nauza", so
"Kampuni yangu INAUZA bidhaa za milioni 50" already satisfied the turnover gate, and the bare
cue alone routed a COMPANY to the resident-individual turnover table — a wrong figure carrying
the rules engine's authority. No corpus row has that shape.

TEN OF THE SIXTEEN PROBES ARE DELIBERATELY CORRECT BODIES that must keep their existing route
(PAYE, VAT registration, SDL, the fact path). That is the half R17 says does the work, and it is
the half that caught this.

ONE ROW IS KNOWN-FAILING AND STAYS THAT WAY ON PURPOSE. `pic_05` routes a partnership turnover
question to `paye` — on the BEFORE arm too, so this change did not cause it. Its expectation is
pinned to the CORRECT route with the defect recorded in `known_failing`, so the row fails loudly
if anyone ever "fixes" it by relaxing the expectation. See the probe's own note for the
mechanism and why the fix is boarded rather than bundled.
"""
import json
import os
import re

import pytest

from chike import decomposition, routing

PROBE_FILE = os.path.join('eval', 'routing', 'presumptive_income_cue_probes.jsonl')


def _probes():
    with open(PROBE_FILE, encoding='utf-8') as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert rows, 'probe file is empty — an R17 regression file with no probes checks nothing'
    return rows


PROBES = _probes()
IDS = [p['id'] for p in PROBES]


def route_of(text):
    """Orchestrator.route's own logic: decompose, then the first non-`none` intent."""
    parts = decomposition.decompose_query(text)
    intents = [routing.detect_intent(p) for p in parts]
    return next((i for i in intents if i != 'none'), 'none')


# ── the probe file itself ────────────────────────────────────────────────────────

def test_probe_file_is_intact():
    assert len(PROBES) == 16, f'probe file has {len(PROBES)} rows, expected 16'
    assert len(set(IDS)) == 16, 'duplicate probe ids'
    for p in PROBES:
        assert p['guards_against'].strip(), f"{p['id']} has no guards_against note"
        assert p['expect_route'] in {
            'presumptive', 'paye', 'sdl', 'vat_registration', 'none'}, p['expect_route']


def test_the_majority_of_probes_are_correct_bodies_that_must_not_move():
    """R17's clearest case in one assertion.

    Probes designed to FLAG pass on a broken rule too; the ones designed to come back CLEAN are
    what find an over-broad change. If a future edit rebalances this file toward positives it
    loses the property that caught pic_04, so the ratio is pinned.
    """
    positives = [p for p in PROBES if p['expect_route'] == 'presumptive']
    controls = [p for p in PROBES if p['expect_route'] != 'presumptive']
    assert len(controls) >= len(positives), (
        f'{len(controls)} controls vs {len(positives)} positives — the control arm must not '
        f'become the minority')
    assert len(positives) == 6 and len(controls) == 10, (len(positives), len(controls))


# ── the contract, probe by probe ─────────────────────────────────────────────────

@pytest.mark.parametrize('probe', PROBES, ids=IDS)
def test_probe_routes_as_specified(probe):
    got = route_of(probe['question'])
    expected = probe.get('known_failing') or probe['expect_route']
    assert got == expected, (
        f"{probe['id']}: expected {expected}, got {got}\n"
        f"question: {probe['question']}\nguards_against: {probe['guards_against']}")


@pytest.mark.parametrize('probe', [p for p in PROBES if p.get('known_failing')],
                         ids=[p['id'] for p in PROBES if p.get('known_failing')])
def test_known_failing_rows_still_name_a_live_defect(probe):
    """FAILS when a known-failing row starts passing — which is the good outcome, and must be
    an explicit edit rather than a silent one.

    The bucket exists so a defect cannot be parked and forgotten: the reason is mandatory, and
    it must say what would fix it.
    """
    assert probe['known_failing'] != probe['expect_route'], (
        f"{probe['id']}: known_failing equals expect_route, which makes the pin meaningless")
    assert len(probe.get('known_failing_reason', '')) > 120, (
        f"{probe['id']}: a known-failing row needs its mechanism written down, not a label")
    assert route_of(probe['question']) == probe['known_failing'], (
        f"{probe['id']} no longer reproduces its known defect — if it is genuinely fixed, "
        f"remove the known_failing keys in the same commit as the fix")


# ── pins that fail when the mechanism is widened without probes ──────────────────

def test_the_bare_cue_is_only_safe_inside_its_conjunction():
    """`kodi ya mapato` alone must never route. The guard is turnover cue AND magnitude AND no
    veto; each of the three is removed here in turn and the route must collapse to `none`."""
    assert route_of('Kodi ya mapato ni nini?') == 'none'                    # no figure
    assert route_of('Faida yangu ni milioni 10, kodi ya mapato ni ngapi?') == 'none'  # no turnover
    assert route_of('Mauzo yangu ni milioni 30, kodi ya mapato ni ngapi?') == 'presumptive'


def test_the_entity_veto_is_composed_and_subtractable():
    """The entity arm is a SEPARATE named pattern so a sweep can reconstruct the before-state.

    Inlining it would repeat the fault that made the routing A/B sweep report a false blast
    radius of 4: an arm it could not switch off independently.
    """
    assert routing._PRESUMPTIVE_ENTITY_VETO_PATTERN
    assert routing._PRESUMPTIVE_SCHEDULE_VETO_PATTERN
    combined = (routing._PRESUMPTIVE_SCHEDULE_VETO_PATTERN + '|'
                + routing._PRESUMPTIVE_ENTITY_VETO_PATTERN)
    assert routing._PRESUMPTIVE_VETO.pattern == combined
    schedule_only = re.compile(routing._PRESUMPTIVE_SCHEDULE_VETO_PATTERN)
    # The pre-change router did NOT veto a company; that is the whole point of the new arm.
    assert not schedule_only.search('kampuni yangu inauza bidhaa')
    assert routing._PRESUMPTIVE_VETO.search('kampuni yangu inauza bidhaa')


def test_the_transport_schedule_veto_survived_the_addition():
    """para 2(5)'s per-vehicle table is a different computation this engine does not implement.
    The entity arm was appended to the same regex, so this is the check that the append did not
    disturb what was already there."""
    for q in ('Nauza tiketi za daladala, mauzo yangu ni milioni 20, kodi ya mapato ni ngapi?',
              'Mauzo yangu ni milioni 20, nitajua vipi ikiwa nalipa kodi ya mapato kwa '
              'makadirio au mfumo wa kawaida?'):
        assert route_of(q) == 'none', q
