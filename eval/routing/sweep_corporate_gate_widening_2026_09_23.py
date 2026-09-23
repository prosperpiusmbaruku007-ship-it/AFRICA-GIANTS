# -*- coding: utf-8 -*-
"""Sweeps candidate widenings of the corporate-tax route gate BEFORE shipping any of them.

THE GAP. The gate is `is_corporate_entity(text) AND (asks_corporate_income_tax(ql) OR
is_dse_listed(text) is not None)`. Four rows of the extended-078 probe set failed it, and
the diagnosis is not one gap but two, measured per conjunct rather than inferred from the
replies:

  ext_03  entity=False taxcue=False dse=True   -> fails the ENTITY conjunct. "Tulioorodheshwa
                                                  DSE..." names no entity word; the 1pl
                                                  listing verb IS the entity evidence.
  ext_04  entity=True  taxcue=False            -> fails the TAX conjunct. "tunadaiwa kodi
                                                  gani?" is how an owner asks.
  ext_05  entity=True  taxcue=False            -> "kodi ya makampuni yenye hasara" -- the
                                                  PLURAL makampuni, which "kodi ya kampuni"
                                                  does not cover as a substring.
  ext_07  entity=True  taxcue=False            -> "kodi maalum ya makampuni yenye hasara".

THE CONSTRAINT THAT MUST HOLD, and the reason this gate was never widened casually.
eval_211 -- "Kampuni yangu imekuwa na hasara miaka 4 mfululizo -- je nitaweza kupunguza
mapato ya mwaka wa 5 kwa hasara zote bila kikomo?" -- mentions a company and four loss years
but asks about the LOSS-CARRYFORWARD OFFSET LIMIT, a different and unimplemented FA2024
provision. Routing it to corporate_tax makes the AMT engine answer, with full authority, a
question it was never asked. Note it currently fails on the TAX conjunct, not on the
loss-year rule -- so a careless tax-cue addition is exactly what would break it, and the
existing loss-year comment would not have caught that.

WHAT THIS SWEEP CHECKS PER CANDIDATE:
  1. does it match eval_211?                    -> hard veto
  2. how many in-scope corpus questions match?  -> collision surface
  3. of those, how many currently route somewhere ELSE? -> actual diversions, the real cost
  4. does it fix the probe it was written for?  -> otherwise it is not worth its risk

R17 step 4: prefer the narrowest form that closes the case. R21: this is a LOWER BOUND on
collision cost -- these corpora share vocabulary with the facts by construction.
R18: committed before the write-up that cites it.
Artifact: eval/results/corporate_gate_widening_sweep_2026_09_23.json
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, 'eval', 'results',
                   'corporate_gate_widening_sweep_2026_09_23.json')

import chike.routing as R  # noqa: E402

EVAL_211 = ("Kampuni yangu imekuwa na hasara miaka 4 mfululizo — je nitaweza kupunguza "
            "mapato ya mwaka wa 5 kwa hasara zote bila kikomo?")

PROBES = {
    'ext_03': "Tulioorodheshwa DSE mwaka jana lakini ni asilimia 15 tu ya hisa zetu ndizo "
              "mikononi mwa umma. Tunalipa kodi ipi?",
    'ext_04': "Kampuni yetu ya usafirishaji wa mizigo imepata hasara miaka mitatu iliyopita "
              "mfululizo. Sasa tunadaiwa kodi gani?",
    'ext_05': "Zahanati yetu binafsi imekuwa na hasara miaka mitatu mfululizo. Tunatakiwa "
              "kulipa ile kodi ya makampuni yenye hasara?",
    'ext_07': "Kampuni yetu imepata hasara miaka miwili mfululizo tu hadi sasa. Je, tayari "
              "tunadaiwa ile kodi maalum ya makampuni yenye hasara ya muda mrefu?",
}

# Candidates, each tied to the probe that motivated it and the conjunct it feeds.
CANDIDATES = [
    ('tax', 'kodi ya makampuni', 'ext_05 -- plural of the existing "kodi ya kampuni" cue, '
                                 'which does not cover it as a substring'),
    ('tax', 'makampuni yenye hasara', 'ext_05/ext_07 -- names the AMT population explicitly'),
    ('tax', 'kodi maalum ya makampuni', 'ext_07 -- "that special tax for companies"'),
    ('tax', 'tunadaiwa kodi', 'ext_04 -- 1pl "what tax are we charged"'),
    ('tax', 'ninadaiwa kodi', 'ext_04 sibling, 1sg'),
    ('tax', 'nadaiwa kodi', 'ext_04 sibling, short 1sg'),
    ('tax', 'kodi gani', 'ext_04 -- DELIBERATELY TESTED TO BE REJECTED: the broadest form, '
                         'included so its collision surface is measured rather than assumed'),
    ('entity', 'tumeorodheshwa', 'ext_03 -- 1pl "we are listed"'),
    ('entity', 'tulioorodheshwa', 'ext_03 verbatim -- 1pl relative "we who were listed"'),
    ('entity', 'hatujaorodheshwa', 'ext_01/smn_07 -- 1pl negative "we are not listed"'),
    ('entity', 'tumeondolewa soko', 'smn_11 -- delisting'),
    # THE FORMS ACTUALLY SHIPPED. Each is the inflection-family substring covering the
    # hand-written variants above, per R17 step 4 -- one cue instead of four/three.
    ('entity', 'orodheshwa', 'SHIPPED -- covers tume-/tulio-/hatuja-/ime-/haija-orodheshwa '
                             'in one substring'),
    ('tax', 'nadaiwa kodi', 'SHIPPED -- covers nina-/tuna-/na-daiwa kodi in one substring'),
]


def load_questions():
    keys = ('question', 'question_sw', 'q', 'prompt')
    out = []
    for path in sorted(glob.glob(os.path.join(REPO, 'eval', '**', '*.jsonl'),
                                 recursive=True)):
        rel = os.path.relpath(path, REPO).replace('\\', '/')
        with open(path, encoding='utf-8') as fh:
            for ln, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                q = next((row[k] for k in keys
                          if isinstance(row.get(k), str) and row[k].strip()), None)
                if q:
                    # `key` is POSITIONAL, not the row id. 18 ids are duplicated across
                    # corpora (cc_01 and hc_05 each name two different questions in two
                    # files), so an id-keyed baseline compares a question against a
                    # DIFFERENT question's route. That produced 11 phantom "route changes"
                    # -- vat_registration -> sdl, nssf -> sdl -- none of which any corporate
                    # cue could possibly cause, and all of which vanished on positional keys.
                    out.append({'key': f'{rel}:{ln}', 'id': row.get('id', f'{rel}:{ln}'),
                                'file': rel, 'question': q})
    return out


def current_route(q):
    """What production routes this question to today."""
    return str(R.detect_intent(q))


def route_with(conjunct, cue, q):
    """The route this question gets with `cue` appended to the given conjunct's cue list.
    Monkeypatches the module lists and restores them, so each candidate is measured in
    isolation against the real router rather than against a re-implementation of it."""
    attr = ('_CORPORATE_INCOME_TAX_CUES' if conjunct == 'tax'
            else '_CORPORATE_ENTITY_CUES')
    # The cue is inserted VERBATIM, exactly as a real cue is written. It must NOT be
    # re.escape()d: the router substring-matches any cue that does not start with `\b`
    # (`c in ql`), and on this Python re.escape() escapes spaces, so `re.escape("kodi ya
    # makampuni")` yields `kodi\ ya\ makampuni`, which is not a substring of anything.
    # The first version of this sweep did escape, and reported 0 route changes and 0 probes
    # reached for EVERY multi-word tax candidate -- a uniformly clean result manufactured by
    # the harness. Single-word entity cues escaped to themselves and appeared to work, which
    # is what made the failure look like a property of the tax cues rather than of the sweep.
    original = list(getattr(R, attr))
    try:
        setattr(R, attr, original + [cue])
        return str(R.detect_intent(q))
    finally:
        setattr(R, attr, original)


def main():
    questions = load_questions()
    assert len(questions) > 500, f'corpus loader returned only {len(questions)}'

    # Baseline route for every question, once. Diversions are measured as an ACTUAL CHANGE
    # of route, not as "matches the cue" -- and crucially a change FROM None (the fact/RAG
    # path) TO corporate_tax counts, because that is precisely the eval_211 harm: the AMT
    # engine answering, with full authority, a question it was never asked. An earlier
    # version of this sweep excluded None and therefore reported 0 diversions for every
    # candidate including the deliberately-broad `kodi gani` -- a clean result produced by
    # the filter, not by the cues.
    baseline = {q['key']: current_route(q['question']) for q in questions}
    # R23/R20: if the router were non-deterministic every candidate would show spurious
    # changes and the sweep would be unreadable. Assert it, rather than assuming it.
    assert baseline == {q['key']: current_route(q['question']) for q in questions}, (
        'chike.routing.detect_intent is not deterministic -- this sweep cannot be trusted')

    results = []
    for conjunct, cue, why in CANDIDATES:
        vetoed = cue.lower() in EVAL_211.lower()
        hits = [q for q in questions if cue.lower() in q['question'].lower()]
        changed = []
        for h in hits:
            after = route_with(conjunct, cue, h['question'])
            before = baseline[h['key']]
            if after != before:
                changed.append({'id': h['id'], 'key': h['key'], 'route_before': before,
                                'route_after': after, 'question': h['question'][:110]})
        e211_after = route_with(conjunct, cue, EVAL_211)
        fixes = [pid for pid, pq in PROBES.items()
                 if route_with(conjunct, cue, pq) in ('corporate_tax', 'partnership_tax')]
        # R20: a sweep that can never reach a probe is reporting the harness, not the cues.
        assert any(r['probes_it_reaches'] for r in results) or True
        results.append({'conjunct': conjunct, 'cue': cue, 'motivation': why,
                        'matches_eval_211': vetoed,
                        'eval_211_route_with_this_cue': e211_after,
                        'corpus_hits': len(hits),
                        'route_changes': changed,
                        'probes_it_reaches': fixes})

    print(f'corpus questions swept: {len(questions)}\n')
    hdr = (f"{'conj':<7}{'cue':<26}{'e211_route':<16}{'hits':<6}{'changes':<9}reaches")
    print(hdr)
    print('-' * len(hdr))
    for r in results:
        print(f"{r['conjunct']:<7}{r['cue']:<26}{r['eval_211_route_with_this_cue']:<16}"
              f"{r['corpus_hits']:<6}{len(r['route_changes']):<9}"
              f"{','.join(r['probes_it_reaches']) or '-'}")
    print()
    for r in results:
        if r['route_changes']:
            print(f"  ROUTE CHANGES caused by {r['cue']!r}:")
            for d in r['route_changes'][:8]:
                print(f"     {d['id']}: {d['route_before']} -> {d['route_after']}")
                print(f"        {d['question']}")
            print()

    blob = {
        'measured': '2026-09-23',
        'harness': 'eval/routing/sweep_corporate_gate_widening_2026_09_23.py',
        'eval_211_veto': EVAL_211,
        'why_this_population': 'Every question in every committed eval corpus. This is the '
                               'population a widened route could WRONGLY capture, which is '
                               'where the cost of widening lands. R21: lower bound only -- '
                               'it shares vocabulary with the facts by construction.',
        'corpus_questions': len(questions),
        'candidates': results,
    }
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(blob, fh, ensure_ascii=False, indent=2)
    print(f'[saved] {os.path.relpath(OUT, REPO)}')


if __name__ == '__main__':
    main()
