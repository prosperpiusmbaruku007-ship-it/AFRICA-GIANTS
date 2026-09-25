# -*- coding: utf-8 -*-
"""Does VOCABULARY SUBSTITUTION defeat the OOC classifier the way orthographic variation
does? Offline, classifier only, no model.

THE HYPOTHESIS UNDER TEST: the orthographic axes may be the wrong frame; real users may
vary by reaching for a DIFFERENT WORD for the same concept rather than misspelling the
term the cue list happens to hold.

=== RESULT, 2026-09-24: 22/22 LEAK. And that is NOT the hypothesis confirmed. ===

The orthographic arm is 20/20. Both arms are 100%, so this does not show vocabulary
substitution is the bigger hole. It shows something stronger and less comfortable:
**the cue list does not generalise beyond the exact strings it holds, along either axis.**
42 of 42 probes, across two unrelated variation types, leak.

The consequence is a scoping one. Adding metathesis cues would close 20 probes worth of one
unbounded axis; adding vocabulary phrases would close 22 of another. Neither is a fix,
because neither axis is finite -- and an OOC list grown one phrase at a time, driven by
whichever leak was found last, is the failure-driven approach R21 warns is expensive
precisely in the blocking direction. This is evidence about the MECHANISM, not about which
phrases to add next.

WHAT THIS CAN AND CANNOT SHOW:
  CAN  -- whether vocabulary-substituted OOC questions leak past the classifier, and at
          what rate, compared with the orthographic arm.
  CANNOT -- which variation type real users actually produce. That is a claim about traffic
          frequency and NO offline sweep can establish it; it needs transcripts.
          Do not let a leak-rate result be read as a realism result.

AUTHORSHIP CAVEAT, because the obvious objection is that this is rigged: I wrote these 22 to
avoid all 136 cues, and someone could call that a strawman. The answer is that a real user
does not know the cue list either -- the question is whether the list GENERALISES, and the
finding is that plausible natural phrasings of every OOC topic avoid all 136 of its strings.
Whether these particular phrasings are the ones real users produce is a separate question
this cannot answer, and a native-speaker or transcript pass is what would settle it.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import classification

# OOC topics, asked with ORDINARY vocabulary instead of the term the cue list holds.
# No misspellings anywhere -- every word is correctly spelt standard Swahili.
VOCAB = [
    ("v01", "capital_gains_land", "Nilipata faida kwa kuuza eneo langu la ujenzi. Nalipa kodi gani?"),
    ("v02", "capital_gains_land", "Shamba langu nimelipatia bei nzuri zaidi ya niliyonunua. Kuna kodi?"),
    ("v03", "capital_gains_land", "Nimebadilisha umiliki wa nyumba yangu kwa malipo. Kodi ni kiasi gani?"),
    ("v04", "import_duty", "Mzigo wangu unatoka nje ya nchi -- serikali inadai malipo gani kabla nichukue?"),
    ("v05", "import_duty", "Nalipa kiasi gani kwa serikali kwa vitu ninavyoleta kutoka nje?"),
    ("v06", "import_duty", "Vitu vinavyoingia nchini vinatozwa kiasi gani?"),
    ("v07", "stamp_duty", "Gharama ya kuthibitisha mkataba wa mauzo kisheria ni kiasi gani?"),
    ("v08", "stamp_duty", "Nyaraka za kuhamisha umiliki zinahitaji malipo gani ya serikali?"),
    ("v09", "mining_royalty", "Nalipa serikali kiasi gani kwa mawe ninayochimba na kuuza?"),
    ("v10", "mining_royalty", "Mchimbaji mdogo anatoa sehemu gani ya mapato yake kwa serikali?"),
    ("v11", "transfer_pricing", "Kampuni zetu mbili zinauziana bidhaa -- bei tunapanga vipi kikodi?"),
    ("v12", "transfer_pricing", "Tunatoza nini kati ya kampuni mama na tawi lake nje ya nchi?"),
    ("v13", "zanzibar_scope", "Biashara yangu iko visiwani -- sheria za kodi ni zile zile?"),
    ("v14", "zanzibar_scope", "Duka langu ni Stone Town. Kodi zinatofautiana na huku?"),
    ("v15", "property_tax", "Nyumba yangu ya kupangisha inatozwa kodi ya mwaka na manispaa?"),
    ("v16", "property_tax", "Jengo langu linatozwa kiasi gani kila mwaka na halmashauri?"),
    ("v17", "crypto", "Nimepata faida kwa pesa za mtandao. Nalipa kodi?"),
    ("v18", "crypto", "Biashara ya sarafu ya kimtandao inatozwa kodi Tanzania?"),
    ("v19", "stock_market", "Nimenunua umiliki kwenye kampuni iliyoorodheshwa. Faida yake inatozwa kodi?"),
    ("v20", "stock_market", "Gawio nilipata kutoka kampuni nilizowekeza -- kodi ni ngapi?"),
    ("v21", "insurance_premium_levy", "Malipo ya kinga ya mali yanatozwa ushuru wa serikali?"),
    ("v22", "epz", "Kiwanda changu kiko kanda ya uzalishaji kwa mauzo ya nje -- kodi zake?"),
]

cfg = os.path.join(REPO, 'kaggle', 'chike_config.json')
ooc, in_scope = classification.resolve_phrases(json.load(open(cfg, encoding='utf-8')))
print(f'[config] {len(ooc)} ooc phrases\n')
print('=== VOCABULARY-SUBSTITUTION ARM (all correctly spelt; must REFUSE) ===')
leaks = []
for vid, topic, q in VOCAB:
    passed = classification.classify(q, ooc, in_scope)
    matched = [p for p in ooc if p in q.lower()]
    if passed:
        leaks.append(vid)
    print(f"  {vid}  {topic:<24} {'LEAKS' if passed else 'refused via ' + str(matched[:2])}")
print(f'\nVOCAB ARM LEAK RATE: {len(leaks)}/{len(VOCAB)} = '
      f'{round(100.0*len(leaks)/len(VOCAB))}%  {leaks}')
print('ORTHOGRAPHIC ARM, for comparison: 20/20 = 100% (eval/refusal_gate/'
      'orthographic_heldout_038.jsonl)')
print('\nREAD THIS AS A COVERAGE RESULT, NOT A REALISM RESULT. It says nothing about which '
      'variation type real users produce -- that needs transcripts.')

OUT = os.path.join(REPO, 'eval', 'results', 'vocab_substitution_arm_2026_09_24.json')
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump({
        'measured': '2026-09-24',
        'harness': 'eval/refusal_gate/measure_vocab_substitution_arm.py',
        'question': 'Does vocabulary substitution defeat the OOC classifier the way '
                    'orthographic variation does?',
        'vocab_arm': {'n': len(VOCAB), 'leaks': len(leaks), 'leak_pct': 100,
                      'leaking_ids': leaks},
        'orthographic_arm': {'n': 20, 'leaks': 20, 'leak_pct': 100,
                             'source': 'eval/refusal_gate/orthographic_heldout_038.jsonl'},
        'finding': 'BOTH ARMS 100%. This does NOT establish vocabulary substitution as the '
                   'bigger hole. It establishes that the cue list does not generalise beyond '
                   'the exact strings it holds, along either axis -- 42 of 42 probes across '
                   'two unrelated variation types leak. Evidence about the MECHANISM, not '
                   'about which phrases to add next.',
        'what_it_cannot_show': 'Which variation type real users actually produce. That is a '
                               'traffic-frequency claim and no offline sweep can establish '
                               'it. A leak-rate result must not be read as a realism result.',
        'authorship_caveat': 'The 22 vocab probes were authored to avoid all 136 cues. The '
                             'objection that this is rigged is answered by noting a real user '
                             'does not know the cue list either -- but whether THESE phrasings '
                             'are the ones users produce needs transcripts or a native-speaker '
                             'pass.',
        'rows': [{'id': i, 'topic': t, 'question_sw': q, 'leaked': i in leaks}
                 for i, t, q in VOCAB],
    }, fh, ensure_ascii=False, indent=2)
print(f'[saved] {os.path.relpath(OUT, REPO)}')
