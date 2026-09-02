# -*- coding: utf-8 -*-
"""Drains the queue nobody was draining (2026-09-02, per founder instruction after
`permit_class_d_does_not_exist` and `nssf_payment_deadline` sat hedged for weeks while the
document that would have closed them was already sitting in `data/source_documents/`).

WHAT THE GAP WAS. Both facts were first checked in mid-June, against a live government site
that failed (immigration.go.tz's JS shell, an unreachable nssf.go.tz deadline page). A later,
unrelated scrape (for GN487A, for the NSSF Act itself) cached the exact document that would have
closed each fact -- weeks later -- and nothing re-examined the hedge when that material landed.
Two facts closed for free once someone thought to check; nothing was watching for the third.

WHAT THIS SCRIPT DOES. For every dict-shaped fact that is CURRENTLY marked as a hedge or a
tooling-blocked "unknown" (verified_as_at == "unknown" AND its own text names an access failure
-- unavailable, blocked, JS shell, CAPTCHA, 403, "could not locate"), guesses which
`data/source_documents/<topic>/` directory is relevant by keyword match against the fact's own
key + fact text + primary_source, and flags it if:
  (a) a file already exists in that directory, AND
  (b) the fact's own verified_by/primary_source/source field does NOT already reference a
      data/source_documents/ path (i.e. the cache was never checked as a fallback).

Deliberately NOT date-based. All of `data/source_documents/`'s current files cluster in a single
~2-day scrape window (2026-06-30/07-01); comparing mtimes against a fact's last-check date is
noise for anything checked after that window and would MISS both of the actual incidents this
script was built from (checked mid-June, closed by a cache populated three weeks later -- the gap
that matters is "never checked," not "checked before a specific date").

R20 discipline: a topic match with zero files in the directory is not flagged (nothing to find);
a fact that already cites a local path is not flagged (the cache WAS checked, whatever it found).
Neither is a false positive waiting to happen -- both are legitimate "nothing to do here" outcomes,
recorded as such in the report rather than silently dropped.

R18: committed before running. Artifact: eval/results/revisitable_hedges_2026_09_02.json
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS_PATH = os.path.join(REPO, 'scripts', 'locked_facts.json')
SOURCE_DOCS_DIR = os.path.join(REPO, 'data', 'source_documents')
OUT = os.path.join(REPO, 'eval', 'results', 'revisitable_hedges_2026_09_02.json')

_BLOCKED_SIGNAL = re.compile(
    r'unavailable|blocked|js shell|403|captcha|tooling failure|unreachable|'
    r'unable to (locate|confirm)|could not (locate|confirm)|not (located|found)|'
    r'no source (found|located)', re.I)

_LOCAL_PATH_ALREADY_CITED = re.compile(r'data[/\\]source_documents', re.I)

# Keyword -> topic directory. Ordered; first match wins. Deliberately hand-curated rather than
# fuzzy-matched against directory names, because a wrong topic match is worse than no match --
# it sends the next person to look in the wrong folder and report "nothing there."
_TOPIC_KEYWORDS = [
    (('brela', 'company', 'business name', 'annual return', 'memorandum', 'articles of',
      'certificate of registration', 'company_', 'foreign_late_filing'), 'brela'),
    (('immigration', 'permit_class', 'gn487a', 'mgeni', 'non-citizen', 'noncitizen',
      'residence', 'visa'), 'immigration'),
    (('gn605a', 'minimum_wage', 'elra', 'labour', 'labor'), 'labour'),
    (('nssf', 'pension', 'social security'), 'nssf'),
    (('osha', 'safety_officer', 'electrical_test', 'workplace safety'), 'osha'),
    (('wcf', 'workers compensation', 'workmens compensation'), 'wcf'),
    (('vat_', 'paye_', 'sdl_', 'efd_', 'presumptive', 'tra ', 'income tax', 'trademark_renewal',
      'name_similarity', 'course_fee', 'business_licence'), 'tra'),
]


def _guess_topic(key, fact_text):
    # LEADING word-boundary only, not `kw in blob` -- found live 2026-09-02:
    # `efd_tra_closure_authority`'s fact text says "suspension of EFD device/licence", and a bare
    # substring check for 'pension' (an nssf keyword) matches inside "suspension", misrouting a
    # pure TRA/EFD fact to the nssf topic. `\bpension` requires a boundary before the match, which
    # "suspension" never has (s-u-s-PENSION has no non-word character before "pension"), while
    # still matching a real standalone "pension". No trailing boundary requirement, deliberately:
    # several keywords ('vat_', 'efd_', 'company_') are intentional prefixes ending in `_`, and a
    # trailing \b would never fire there since `_` and the following letter are both \w chars.
    blob = (key + ' ' + fact_text).lower()
    for keywords, topic in _TOPIC_KEYWORDS:
        if any(re.search(r'\b' + re.escape(kw), blob) for kw in keywords):
            return topic
    return None


def _is_currently_blocked_hedge(v):
    if v.get('verified_as_at') != 'unknown':
        return False
    blob = ' '.join(str(v.get(f, '')) for f in ('status', 'verified_by', 'correction_note'))
    return bool(_BLOCKED_SIGNAL.search(blob))


def _already_cites_local_cache(v):
    blob = ' '.join(str(v.get(f, '')) for f in ('verified_by', 'primary_source', 'source'))
    return bool(_LOCAL_PATH_ALREADY_CITED.search(blob))


def main():
    with io.open(FACTS_PATH, encoding='utf-8') as f:
        facts = json.load(f)

    topic_files = {}
    for topic in os.listdir(SOURCE_DOCS_DIR):
        topic_dir = os.path.join(SOURCE_DOCS_DIR, topic)
        if not os.path.isdir(topic_dir):
            continue
        files = [fn for fn in os.listdir(topic_dir)
                 if os.path.isfile(os.path.join(topic_dir, fn)) and fn != '.gitkeep']
        topic_files[topic] = files

    candidates = []
    skipped_already_cited = []
    skipped_no_local_files = []
    revisit_now = []

    for key, v in facts.items():
        if key.startswith('_') or not isinstance(v, dict):
            continue
        if not _is_currently_blocked_hedge(v):
            continue
        candidates.append(key)

        topic = _guess_topic(key, str(v.get('fact', '')))
        if topic is None or not topic_files.get(topic):
            skipped_no_local_files.append({'key': key, 'guessed_topic': topic})
            continue
        if _already_cites_local_cache(v):
            skipped_already_cited.append({'key': key, 'topic': topic})
            continue
        revisit_now.append({
            'key': key,
            'guessed_topic': topic,
            'candidate_files': topic_files[topic],
            'current_status': v.get('status'),
            'current_primary_source': v.get('primary_source'),
        })

    report = {
        'measured': '2026-09-02',
        'harness': 'scripts/find_revisitable_hedges.py',
        'purpose': 'Find hedged/tooling-blocked facts where a local data/source_documents/ '
                   'cache for a plausible topic exists and was never checked as a fallback -- '
                   'the gap that let permit_class_d_does_not_exist and nssf_payment_deadline '
                   'sit hedged for weeks after the closing document was already on disk.',
        'total_currently_blocked_hedges': len(candidates),
        'skipped_no_local_files_for_topic': len(skipped_no_local_files),
        'skipped_already_cites_local_cache': len(skipped_already_cited),
        'REVISIT_NOW_count': len(revisit_now),
        'revisit_now': revisit_now,
        'skipped_no_local_files_detail': skipped_no_local_files,
        'skipped_already_cited_detail': skipped_already_cited,
    }
    print(json.dumps({k: v for k, v in report.items()
                       if k not in ('revisit_now', 'skipped_no_local_files_detail',
                                    'skipped_already_cited_detail')},
                      ensure_ascii=False, indent=2))
    if revisit_now:
        print('\nREVISIT NOW:')
        for r in revisit_now:
            print(f"  {r['key']}  (topic: {r['guessed_topic']}, "
                  f"{len(r['candidate_files'])} local file(s))")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
