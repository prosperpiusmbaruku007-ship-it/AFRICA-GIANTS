# -*- coding: utf-8 -*-
"""Rate-conflation guard: sweep the FALSE-POSITIVE surface before designing anything.

Specified by one live row. nat_24's WCF body says "unatakiwa kulipa 10% ya jumla ya mishahara
kwa ajili ya WCF" — 10% is NSSF's employer share. All three mechanism gaps sit in that single
row, so the guard has to close all three:

  1. DIRECTION.  _cross_levy_guard's body_contradicts_siblings looks for OTHER levies' windows.
                 Here the body volunteers a SIBLING'S rate for its OWN levy.
  2. VACUITY.    WCF's sub-answer is an APPLICABILITY verdict, so ComputationResult.amount is
                 None and every figure-comparing rule is satisfied trivially. D-FIDELITY-5's
                 shape: there is nothing to compare against.
  3. WINDOW.     _levy_windows runs FORWARD from a levy token, so "kulipa 10% ... kwa ajili ya
                 WCF" puts the figure BEFORE the token, in no window at all.

(3) is what makes (1) and (2) fixable: a BACKWARD window is what attaches the rate to its levy
subject, and attaching it is the whole binding constraint — because a correct multi-levy answer
legitimately states several rates, and only adjacency distinguishes "WCF is 0.5%" from
"WCF is 10%".

THE SAFETY ARGUMENT, and why this is not the impossible Guard B: a levy rate is a CONSTANT, not
a quantity derived from the user's figures. "3.5% is not 0.5% under any transformation" has
exactly GUARD A's property. Guard B failed because a fabricated amount and a legitimate
transformation are indistinguishable; that does not apply to a fixed statutory rate.

THIS SCRIPT DESIGNS NOTHING. It runs a candidate detector over every real model reply this
project has recorded and reports what it would flag, so the false-positive surface is measured
BEFORE any guard is written into chike/fidelity.py.

R18: committed before its result is written up.
Artifact: eval/results/rate_guard_sweep.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(REPO, 'eval', 'results')
OUT = os.path.join(RESULTS, 'rate_guard_sweep.json')

# Statutory rates per levy. A body may legitimately state ANY of these for that levy.
# NSSF carries all three lawful split arrangements (10+10, 15+5, 20+0) per locked fact 77,
# so 5, 10, 15 and 20 are all lawful NSSF percentages.
LEVY_RATES = {
    'sdl':  {3.5},
    'nssf': {20, 10, 15, 5},
    'wcf':  {0.5},
    'paye': {0, 8, 20, 25, 30, 15},          # bands + non-resident flat 15
    'vat':  {18, 0, 3, 6, 16, 15, 12},       # standard, zero, withholding, B2C, supplier shares
}
# ZERO IS LAWFUL FOR EVERY LEVY. Found by the first sweep as its only false positive: nat_24's
# live reply says "unatakiwa kulipa asilimia 0% ya SDL kwa kuwa una chini ya wafanyakazi 10",
# which is a correct NON-LIABILITY statement, not a wrong rate. A body asserting 0% is denying
# the obligation, and that claim is already checked where it belongs — D-FIDELITY-5
# (body_denies_a_positive_obligation) fires when the engine computed a POSITIVE amount. Adding
# 0 here keeps this guard to the one thing it can settle: a rate that is wrong under any
# transformation.
for _rates in LEVY_RATES.values():
    _rates.add(0)
LEVY_TOKEN = re.compile(r'\b(sdl|nssf|wcf|paye|vat)\b', re.IGNORECASE)
# Swahili nicknames, so a body that says "kwa ajili ya mafunzo" is attributable too.
NICKNAME = {
    'mafunzo': 'sdl', 'ufundi': 'sdl', 'ujuzi': 'sdl',
    'uzeeni': 'nssf', 'pensheni': 'nssf', 'hifadhi ya jamii': 'nssf',
    'fidia': 'wcf',
}
NICK_TOKEN = re.compile('|'.join(re.escape(k) for k in sorted(NICKNAME, key=len,
                                                              reverse=True)), re.IGNORECASE)
RATE = re.compile(r'(?:asilimia\s*([0-9]+(?:[.,][0-9]+)?)|([0-9]+(?:[.,][0-9]+)?)\s*%)',
                  re.IGNORECASE)
# A negated/contrast clause: "si asilimia 4", "NOT 14%", "si 200,000,000". The 18%-contrast
# false-PASS proved these are real and must not be flagged as the body's own claim.
NEGATION = re.compile(r'\b(si|sio|siyo|not|never|badala ya|tofauti na)\b\s*$', re.IGNORECASE)

BACKWARD_CHARS = 60      # how far before a levy token a rate may sit and still be attributed
FORWARD_CHARS = 60


def levy_marks(text):
    """(position, levy) for every explicit token AND nickname, in order."""
    marks = [(m.start(), m.group(1).lower(), m.group(0)) for m in LEVY_TOKEN.finditer(text)]
    for m in NICK_TOKEN.finditer(text):
        marks.append((m.start(), NICKNAME[m.group(0).lower()], m.group(0)))
    return sorted(marks)


def attributed_rates(body):
    """[(levy, rate, evidence, direction)] for rates adjacent to a levy subject.

    BIDIRECTIONAL by design (gap 3), but NOT nearest-wins — A PRECEDING LEVY ALWAYS WINS.

    Nearest-wins was the first rule and R17 probe rg_01 broke it immediately, on a perfectly
    correct sentence: "SDL ni asilimia 3.5 ..., NSSF ni asilimia 20, na WCF ni asilimia 0.5."
    The 20 has NSSF ~9 chars behind it and WCF ~4 chars ahead, so nearest-wins attributed
    NSSF's rate to WCF and flagged a right answer.

    The asymmetry is grammatical, not a fudge: in "X ni asilimia N" the subject PRECEDES its
    rate, so a preceding levy is the subject whenever one is in range. Forward attribution
    exists only as the fallback for the shape that has no preceding levy at all — which is
    exactly the defect ordering, "kulipa 10% ... kwa ajili ya WCF". So the fallback still
    catches every real case while the preference protects every correct breakdown.
    """
    marks = levy_marks(body)
    if not marks:
        return []
    out = []
    for m in RATE.finditer(body):
        raw = (m.group(1) or m.group(2)).replace(',', '.')
        try:
            rate = float(raw)
        except ValueError:
            continue
        pre = body[max(0, m.start() - 12):m.start()]
        if NEGATION.search(pre.strip()):
            continue                                  # a contrast clause, not a claim
        back, fwd = None, None
        for pos, levy, tok in marks:
            if pos >= m.end():
                dist = pos - m.end()
                if dist <= FORWARD_CHARS and (fwd is None or dist < fwd[0]):
                    fwd = (dist, levy, tok, 'forward')
            else:
                dist = m.start() - pos
                if dist <= BACKWARD_CHARS and (back is None or dist < back[0]):
                    back = (dist, levy, tok, 'backward')
        # AN EXPLICIT ATTACHMENT BEATS PROXIMITY. "asilimia 10% kwa ajili ya NSSF" states its
        # own subject, and that must win over a levy word left over from the previous clause.
        # Found in real output: "...kwa ajili ya mafunzo ya FIDIA, pamoja na asilimia 10% kwa
        # ajili ya NSSF" — preceding-wins alone attributed NSSF's correct 10% to WCF via the
        # stray 'fidia'. The connector has to be the WHOLE gap, so the defect's longer
        # "10% ya jumla ya mishahara kwa ajili ya WCF" does not qualify as an attachment and
        # still falls through to the ordinary rules.
        attached = False
        if fwd is not None:
            gap = body[m.end():m.end() + fwd[0]]
            # The leading '%' is part of the gap, not the rate: "asilimia 10%" is matched by
            # the `asilimia N` alternative, which stops before the sign.
            attached = bool(re.fullmatch(
                r'[\s,]*%?[\s,]*(?:kwa\s+ajili\s+ya|kwa|ya|ni\s+ya)?\s*', gap, re.IGNORECASE))
        best = fwd if attached else (back or fwd)
        if best:
            _, levy, tok, direction = best
            out.append((levy, rate, tok, direction))
    return out


def check(body):
    """Rates attributed to a levy that are NOT among that levy's statutory rates."""
    bad = []
    for levy, rate, tok, direction in attributed_rates(body):
        allowed = LEVY_RATES.get(levy)
        if allowed is None:
            continue
        if rate not in allowed:
            bad.append({'levy': levy, 'rate': rate, 'via': tok, 'direction': direction,
                        'allowed': sorted(allowed)})
    return bad


def corpus():
    """Every recorded model reply in eval/results/, tagged by file."""
    rows = []
    for name in sorted(os.listdir(RESULTS)):
        if not name.endswith('.json') or name == os.path.basename(OUT):
            continue
        try:
            with open(os.path.join(RESULTS, name), encoding='utf-8') as f:
                blob = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        def walk(node, path):
            if isinstance(node, dict):
                reply = node.get('reply')
                if isinstance(reply, str) and reply.strip():
                    rows.append({'file': name, 'id': node.get('id', path),
                                 'reply': reply})
                for k, v in node.items():
                    walk(v, f'{path}.{k}')
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f'{path}[{i}]')
        walk(blob, name)
    # de-duplicate identical (id, reply) pairs across re-runs
    seen, uniq = set(), []
    for r in rows:
        key = (r['id'], r['reply'])
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    return uniq


def probes():
    """R17 step 2: bodies AUTHORED to contain the risky pattern, most of them CORRECTLY.

    A clean sweep over the recorded corpus is weak evidence — the corpus only contains what the
    model happened to say. These are written to break an over-broad guard: correct multi-levy
    breakdowns, contrast clauses naming a sibling's rate, the NSSF split arrangements, and the
    exact rate-before-nickname ordering the defect uses but stated RIGHT.
    """
    path = os.path.join(HERE, 'rate_guard_probes.jsonl')
    with open(path, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    assert rows, 'probe file empty — this check would pass vacuously'
    return rows


def main():
    rows = corpus()
    flagged = []
    for r in rows:
        bad = check(r['reply'])
        if bad:
            flagged.append({**r, 'violations': bad})

    # --- R17 probe arm: measured separately, because a corpus sweep cannot find over-breadth
    probe_results, probe_failures = [], []
    for p in probes():
        bad = check(p['body'])
        got = 'flag' if bad else 'clean'
        rec = {**p, 'got': got, 'violations': bad, 'ok': got == p['expect']}
        probe_results.append(rec)
        if not rec['ok']:
            probe_failures.append(rec)

    by_file = {}
    for r in flagged:
        by_file[r['file']] = by_file.get(r['file'], 0) + 1

    out = {
        'measured': '2026-08-22',
        'harness': 'eval/fidelity/sweep_rate_guard.py',
        'purpose': 'measure the FALSE-POSITIVE surface of a rate-conflation guard before '
                   'writing one into chike/fidelity.py',
        'specified_by': 'nat_24 live WCF 10% (canary, 2026-08-22)',
        'window': {'backward_chars': BACKWARD_CHARS, 'forward_chars': FORWARD_CHARS},
        'levy_rates': {k: sorted(v) for k, v in LEVY_RATES.items()},
        'replies_swept': len(rows),
        'flagged_count': len(flagged),
        'flagged_by_file': by_file,
        'flagged': flagged,
        'probes_total': len(probe_results),
        'probes_failed': len(probe_failures),
        'probe_failures': probe_failures,
        'probes': probe_results,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'replies swept: {len(rows)}')
    print(f'FLAGGED: {len(flagged)}')
    print(json.dumps(by_file, indent=2))
    for r in flagged:
        v = '; '.join(f"{b['levy']}={b['rate']} (via {b['via']}, {b['direction']})"
                      for b in r['violations'])
        print(f"\n  [{r['file']}] {r['id']}: {v}")
        print(f"    {r['reply'][:200]}")
    print(f"\n--- R17 authored probes: {len(probe_results) - len(probe_failures)}"
          f"/{len(probe_results)} as expected ---")
    for p in probe_results:
        mark = 'ok ' if p['ok'] else 'FAIL'
        v = '; '.join(f"{b['levy']}={b['rate']}" for b in p['violations']) or '-'
        print(f"  [{mark}] {p['id']} expect={p['expect']:5} got={p['got']:5} {v}")
        if not p['ok']:
            print(f"        {p['body']}")
            print(f"        guards_against: {p['guards_against']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
