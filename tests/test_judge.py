"""Tests for chike.judge — the frontier LLM-as-judge scoring overlay (follow-up #3, item 5).

Covers the PURE core only (no network): the item-4 majority vote + tie handling, the reply
parser, and the item-5 confirmation-overlay aggregation (three side-by-side numbers +
disagreement queue). judge_once/judge_majority are exercised with an injected fake
`requests` so no OpenRouter call is made.

The invariants locked here are the ones that make the overlay SAFE:
  * a tie in the vote resolves to `undetermined`, never a silent pass/fail;
  * the judge FILLS the reliable=False gap but NEVER flips a reliable=True regex verdict
    (disagreements only queue);
  * `undetermined` never moves a regex-scored question into/out of the denominator;
  * clarifications (deliberate never-guess) are excluded from grading.
"""
import json
import pytest

from chike.judge import (majority_vote, parse_verdict, judge_gradeable,
                         build_confirmation_report, judge_once, judge_majority)


# ── item-4: majority vote + tie ───────────────────────────────────────────────────
def test_majority_5_1_split_resolves_to_the_five():
    # The exact shape every unstable item-4 case took — the minority (1) cannot win.
    v, tie, votes = majority_vote(['wrong'] * 5 + ['correct'])
    assert v == 'wrong' and tie is False
    assert votes == {'wrong': 5, 'correct': 1}


def test_majority_unanimous():
    v, tie, _ = majority_vote(['correct'] * 5)
    assert v == 'correct' and tie is False


def test_majority_three_way_2_2_1_is_a_tie_undetermined():
    # A 2-2-1 plurality tie must NOT silently pick a side.
    v, tie, _ = majority_vote(['correct', 'correct', 'wrong', 'wrong', 'undetermined'])
    assert v == 'undetermined' and tie is True


def test_majority_clear_plurality_wins_over_tie_check():
    v, tie, _ = majority_vote(['correct', 'correct', 'correct', 'wrong', 'undetermined'])
    assert v == 'correct' and tie is False


def test_majority_empty_is_undetermined():
    v, tie, _ = majority_vote([])
    assert v == 'undetermined' and tie is True


# ── parser fallback ladder ────────────────────────────────────────────────────────
def test_parse_strict_json():
    v, j = parse_verdict('{"verdict": "wrong", "justification": "figure contradicts reference"}')
    assert v == 'wrong' and 'contradicts' in j


def test_parse_substring_fallback_on_junk_verdict_value():
    # Fallback ladder fires when JSON IS present but the verdict value is not one of the
    # three enums — then substring-detect from the raw message. (Parity with the census /
    # scale39 parser the item-4 numbers were measured on.)
    assert parse_verdict('{"verdict": "definitely wrong"}')[0] == 'wrong'


def test_parse_no_json_stays_undetermined():
    # No JSON object at all -> undetermined, matching census/scale39 behaviour exactly (the
    # judge is instructed to return ONLY JSON and reliably does, with reasoning disabled).
    assert parse_verdict('The answer is clearly wrong because...')[0] == 'undetermined'
    assert parse_verdict('...')[0] == 'undetermined'


# ── judge_once / judge_majority with an injected fake requests ────────────────────
class _FakeResp:
    def __init__(self, payload):
        self._p = payload

    def json(self):
        return self._p


class _FakeRequests:
    """Serves a scripted sequence of verdicts, one per POST, as OpenRouter-shaped JSON."""
    def __init__(self, verdicts, provider='DeepInfra'):
        self._verdicts = list(verdicts)
        self.provider = provider
        self.calls = 0

    def post(self, url, headers=None, json=None, timeout=None):
        v = self._verdicts[self.calls]
        self.calls += 1
        return _FakeResp({
            'provider': self.provider,
            'usage': {'prompt_tokens': 100, 'completion_tokens': 20},
            'choices': [{'message': {'content':
                json_dumps_verdict(v)}}]})


def json_dumps_verdict(v):
    return json.dumps({'verdict': v, 'justification': f'because {v}'})


def test_judge_once_pins_provider_and_parses():
    fake = _FakeRequests(['correct'])
    r = judge_once('q', 'ref', 'gen', api_key='x', _requests=fake)
    assert r['verdict'] == 'correct' and r['provider'] == 'DeepInfra' and r['err'] == ''
    assert fake.calls == 1


def test_judge_majority_five_calls_and_pin_check():
    fake = _FakeRequests(['correct', 'correct', 'wrong', 'correct', 'correct'])
    r = judge_majority('q', 'ref', 'gen', api_key='x', n=5, _requests=fake)
    assert r['verdict'] == 'correct' and r['n'] == 5 and fake.calls == 5
    assert r['votes'] == {'correct': 4, 'wrong': 1}
    assert r['providers'] == ['DeepInfra']       # pin held across all 5
    assert r['tie'] is False


# ── item-5: gradeable filtering ───────────────────────────────────────────────────
def test_judge_gradeable_excludes_refusals_and_clarifications():
    rows = [
        {'id': 'a', 'subdomain': 'vat', 'clarified': False},
        {'id': 'b', 'subdomain': 'out_of_corpus', 'clarified': False},   # refusal -> out
        {'id': 'c', 'subdomain': 'paye', 'clarified': True},             # clarification -> out
    ]
    assert [r['id'] for r in judge_gradeable(rows)] == ['a']


# ── item-5: the confirmation-overlay aggregation (the safety-critical math) ───────
def _row(id, subdomain='vat', passed=False, reliable=True, clarified=False, judge=None):
    return {'id': id, 'subdomain': subdomain, 'pass': passed,
            'reliable': reliable, 'clarified': clarified, 'judge': judge}


def test_augmented_fills_gap_and_never_flips_reliable():
    rows = [
        # reliable=True regex verdicts — trusted base, judge must NOT change these numbers
        _row('r1', passed=True,  reliable=True, judge='wrong'),    # disagreement -> QUEUE only
        _row('r2', passed=False, reliable=True, judge='correct'),  # disagreement -> QUEUE only
        _row('r3', passed=True,  reliable=True, judge='correct'),  # agree
        # reliable=False gap — judge FILLS
        _row('g1', reliable=False, judge='correct'),               # -> counts as pass
        _row('g2', reliable=False, judge='wrong'),                 # -> counts as fail
        _row('g3', reliable=False, judge='undetermined'),          # -> excluded
        # a refusal + a clarification that must not enter any in-corpus number
        _row('x1', subdomain='out_of_corpus', reliable=True, passed=True),
    ]
    rep = build_confirmation_report(rows)

    # raw = all in-corpus (6): passes r1,r3 = 2 / 6
    assert rep['raw'] == {'pass': 2, 'total': 6, 'acc': 2 / 6}
    # reliable-denom = the 3 reliable in-corpus: passes r1,r3 = 2 / 3  (UNCHANGED by judge)
    assert rep['reliable_denom'] == {'pass': 2, 'total': 3, 'acc': 2 / 3}
    # judge-augmented = reliable base (2/3) + gap g1(correct)->pass, g2(wrong)->fail, g3 excluded
    #   pass = 2 + 1 = 3 ; total = 3 + 1 + 1 = 5
    assert rep['judge_augmented']['pass'] == 3
    assert rep['judge_augmented']['total'] == 5
    assert rep['judge_augmented']['acc'] == 3 / 5
    # conservative floor: undetermined counts as fail -> total = 3 + 3 gap = 6
    assert rep['judge_augmented']['floor_undet_fail'] == {'pass': 3, 'total': 6, 'acc': 3 / 6}


def test_the_promoted_headline_is_a_BRACKET_and_the_upper_bound_is_the_old_figure():
    """⛔ THE JUDGE BECAME THE BAR A HEADLINE ON 2026-10-09, AND A POINT ESTIMATE WOULD HAVE
    CARRIED THE SAME DEFECT THAT PROMPTED THE PROMOTION.

    `judge_augmented` fills the unreliable gap and deliberately does NOT demote the queued false
    passes. While the judge was report-alongside that was correct. As a HEADLINE it means every
    queued false pass is still inside the numerator — on gate 0e11c3d it read 81.9% with 17
    rows the judge had itself flagged as wrong counted as passes, and hand adjudication put 10
    of them beyond doubt.

    So the headline is a bracket: upper = judge_augmented unchanged (every candidate survives),
    lower = every candidate upheld. Only hand adjudication moves the true figure, which must sit
    inside. Asserted here on the real shape, so a future 'simplification' to a single number
    fails rather than quietly restoring the overstatement.
    """
    rows = [
        _row('p1', passed=True,  reliable=True, judge='correct'),
        _row('p2', passed=True,  reliable=True, judge='correct'),
        _row('fp', passed=True,  reliable=True, judge='wrong'),      # queued false pass
        _row('g1', reliable=False, judge='correct'),
    ]
    rep = build_confirmation_report(rows)
    b = rep['bar_a_headline_bracket']
    # upper is EXACTLY the pre-promotion figure — the bracket adds a bound, it does not
    # redefine the old number
    assert b['upper']['acc'] == rep['judge_augmented']['acc']
    assert b['upper']['pass'] == rep['judge_augmented']['pass']
    # lower demotes the queued false passes, and only those
    assert b['queued_false_pass'] == 1
    assert b['lower']['pass'] == b['upper']['pass'] - 1
    assert b['lower']['total'] == b['upper']['total'], (
        "the lower bound changed the DENOMINATOR — a demoted pass becomes a fail, it does not "
        "leave the population")
    assert b['lower']['acc'] < b['upper']['acc']
    assert b['width_pts'] > 0

    # ⛔ AND THE FALSE-FAIL DIRECTION MUST NOT BE APPLIED. Promoting a regex fail on the
    # judge's word alone is the same error in the flattering direction, and that queue has
    # never been adjudicated.
    rows2 = rows + [_row('ff', passed=False, reliable=True, judge='correct')]
    rep2 = build_confirmation_report(rows2)
    assert rep2['disagreement_queue']['false_fail_candidates'] == ['ff']
    b2 = rep2['bar_a_headline_bracket']
    assert b2['upper']['pass'] == rep2['judge_augmented']['pass'], (
        "a false-FAIL candidate was promoted into the headline — the bracket may only demote")


def test_the_bracket_contains_the_adjudicated_figure_for_the_real_gate_run():
    """⛔ R24's baseline reproduction, applied to the promotion itself: the bracket is only
    useful if the hand-adjudicated answer actually falls inside it. On gate 0e11c3d the upper
    bound is 81.89% (and must equal the shipped overlay's own figure), the lower is 77.30%, and
    adjudication landed at 293/370 = 79.19% — inside, as it must be. If a future change to the
    bracket puts the adjudicated figure outside it, the bracket is wrong, not the adjudication.
    """
    import io
    import json
    import os
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gate = os.path.join(repo, 'eval', 'results', 'gate_production_0e11c3d.json')
    adj = os.path.join(repo, 'eval', 'results', 'false_pass_adjudication_0e11c3d.json')
    if not (os.path.isfile(gate) and os.path.isfile(adj)):
        import pytest
        pytest.skip('the 0e11c3d artifacts are not present')
    d = json.load(io.open(gate, encoding='utf-8'))
    a = json.load(io.open(adj, encoding='utf-8'))
    rep = build_confirmation_report(d['rows'])
    b = rep['bar_a_headline_bracket']
    # the upper bound must still be the figure the run itself published
    assert abs(b['upper']['acc'] - d['judge_overlay']['report']['judge_augmented']['acc']) < 1e-9
    confirmed = a['tally']['FALSE_PASS']
    adjudicated = (b['upper']['pass'] - confirmed) / b['upper']['total']
    assert b['lower']['acc'] <= adjudicated <= b['upper']['acc'], (
        f"the adjudicated figure {adjudicated:.4f} is OUTSIDE the bracket "
        f"[{b['lower']['acc']:.4f}, {b['upper']['acc']:.4f}] — the bracket is wrong")
    assert adjudicated < 0.85, (
        'the adjudicated in-corpus figure now clears R7 Gate 1 — if that is real it is the '
        'headline of the project, so re-derive it before believing this test')


def test_disagreement_queue_is_flags_not_corrections():
    rows = [
        _row('fp', passed=True,  reliable=True, judge='wrong'),
        _row('ff', passed=False, reliable=True, judge='correct'),
        _row('ok', passed=True,  reliable=True, judge='correct'),
    ]
    rep = build_confirmation_report(rows)
    assert rep['disagreement_queue']['false_pass_candidates'] == ['fp']
    assert rep['disagreement_queue']['false_fail_candidates'] == ['ff']
    # the reliable number is exactly the regex number — no flip applied
    assert rep['reliable_denom']['pass'] == 2 and rep['reliable_denom']['total'] == 3


def test_undetermined_gap_never_changes_reliable_denominator():
    # A gap full of undetermined must leave the trusted denominator untouched and only
    # widen the conservative floor.
    rows = [_row('r1', passed=True, reliable=True, judge='correct'),
            _row('g1', reliable=False, judge='undetermined'),
            _row('g2', reliable=False, judge='undetermined')]
    rep = build_confirmation_report(rows)
    assert rep['reliable_denom'] == {'pass': 1, 'total': 1, 'acc': 1.0}
    assert rep['judge_augmented']['pass'] == 1 and rep['judge_augmented']['total'] == 1
    assert rep['judge_augmented']['floor_undet_fail']['total'] == 3


def test_gap_fill_counts_reported():
    rows = [_row('g1', reliable=False, judge='correct'),
            _row('g2', reliable=False, judge='wrong'),
            _row('g3', reliable=False, judge='undetermined')]
    gf = build_confirmation_report(rows)['gap_fill']
    assert gf == {'gap_n': 3, 'judge_correct': 1, 'judge_wrong': 1, 'judge_undetermined': 1,
                  'correct_ids': ['g1'], 'wrong_ids': ['g2'], 'undetermined_ids': ['g3']}
