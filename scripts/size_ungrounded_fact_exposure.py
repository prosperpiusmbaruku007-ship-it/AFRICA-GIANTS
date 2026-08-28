# -*- coding: utf-8 -*-
"""Sizes the exposure of the 164 ungrounded locked facts (v2 audit) -- not whether they are
wrong (expensive, per-fact), but how much each one MATTERS: is it actually retrievable from the
current 187-row RAG index, does it ever surface in the top-3 for a realistic question (measured
against every question in every committed eval/probe corpus, 1000+ questions), does it carry a
figure a user could act on, and does it sit in a domain a trader actually asks about.

WHY THIS SHAPE. Re-verifying 214 (now 164, post-v2-correction) facts against statute is a weeks-
scale project. A fact that is never retrieved is documentation debt -- wrong or not, no live
answer depends on it. A fact that IS served, carries a figure, and sits in a high-traffic domain
is a live risk regardless of triage order. The four flags below let those two populations be
told apart without adjudicating any individual fact's correctness.

METHOD PER FLAG:
  - in_index / served: reuses check_facts_index_sync.py's own matching machinery (exact/sibling/
    grouped/PINNED present_elsewhere) to find each key's row(s) in the CURRENT shipped 187-row
    index, then runs a real retrieval sweep -- e5, the same model validated this session against
    Kaggle to 3-decimal identity -- over every question in every committed eval/**/*.jsonl
    corpus (1007 unique questions, not just the 400-gate) and records which rows EVER appear in
    a top-3. This is an offline proxy for traffic (every probe/gate/adversarial question this
    project has authored), not live production logs, which do not exist for this project.
  - actionable_figure: the fact/correct_value text (or the bare value itself) contains a TZS
    amount, a percentage, or a specific day/deadline count -- something a user could act on
    directly, as opposed to a purely descriptive or procedural statement.
  - core_domain: keyword-classified against the declared product scope (BRELA/VAT/PAYE/SDL/
    NSSF/OSHA/EFD/WCF/GN487A) plus the measured "ordinary duka owner's month" topic list
    (PROGRESS.md, 2026-08-16/23 coverage-gap entries: presumptive tax, business licence,
    council/LGA service levy, market dues, rent withholding, TIN registration). Peripheral:
    everything else (immigration permit classes, trademark/IP, stamp duty, TRAB appeals,
    royalties WHT, DSE/AMT corporate-tax minutiae -- several of which will MOVE to core once
    the corporate/partnership tax domain is built, flagged explicitly where that applies).

R18: committed before its counts are cited in PROGRESS.md or reported to the founder.
Artifact: eval/results/ungrounded_fact_exposure.json
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS_PATH = os.path.join(REPO, 'scripts', 'locked_facts.json')
INDEX_PATH = os.path.join(REPO, 'kaggle', 'rag_facts_text.json')
V2_AUDIT = os.path.join(REPO, 'eval', 'results', 'locked_facts_verification_provenance_audit_v2.json')
OUT = os.path.join(REPO, 'eval', 'results', 'ungrounded_fact_exposure.json')

sys.path.insert(0, HERE)
from check_facts_index_sync import (  # noqa: E402
    PINNED, _is_sibling, _key_slug, _GROUP_MEMBERS, _FACT_GROUPS,
)

ACTIONABLE_RE = re.compile(
    r'TZS\s*[\d,]+|USD\s*[\d,]+|asilimia\s*[\d.]+|%|\bsiku\s*\d+|\d+\s*(days|siku|weeks|wiki|months|miezi|years|mwaka)',
    re.IGNORECASE)

CORE_KEYWORDS = re.compile(
    r'paye|\bvat\b|\bsdl\b|\bnssf\b|\bwcf\b|\bosha\b|\befd\b|\bbrela\b|gn487a|gn605a|'
    r'minimum.?wage|kima cha chini|presumptive|makadirio|council_service_levy|'
    r'market_dues|business_licen[cs]e|kodi ya mapato|mishahara|ajira|payroll|'
    r'annual_return|company_registration|name_reservation|name_change',
    re.IGNORECASE)

# Corporate/partnership-tax-adjacent keys that are peripheral TODAY but will become core the
# moment that domain is built (the next planned build) -- flagged, not silently folded into
# either bucket, since their traffic profile is about to change by decision, not by measurement.
PENDING_CORE_ON_NEXT_BUILD = re.compile(
    r'corporate_tax|dse_25|amt_loss|provisional_tax|minimum_turnover_tax|partnership',
    re.IGNORECASE)


def domain_class(key, text):
    blob = f'{key} {text}'
    if PENDING_CORE_ON_NEXT_BUILD.search(blob):
        return 'pending_core_on_corporate_tax_build'
    return 'core' if CORE_KEYWORDS.search(blob) else 'peripheral'


def is_actionable(key, value):
    blob = key + ' ' + (json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value)
    return bool(ACTIONABLE_RE.search(blob))


def find_index_rows(key, index, index_slugs):
    """Replicates check_facts_index_sync.check()'s matching order, but returns ROW NUMBERS
    instead of a yes/no verdict, since exposure sizing needs to know WHERE to look for
    retrieval, not just whether a pin exists."""
    slug = _key_slug(key)
    if slug in index_slugs:
        return [index_slugs.index(slug)], 'exact'
    for i, s in enumerate(index_slugs):
        if _is_sibling(slug, s):
            return [i], 'sibling'
    if key in _GROUP_MEMBERS:
        spec = _FACT_GROUPS[_GROUP_MEMBERS[key]]
        stem = spec['text'][:40]
        rows = [i for i, r in enumerate(index) if r.startswith(stem)]
        return rows, 'grouped' if rows else 'grouped_missing'
    pin = PINNED.get(key)
    if pin and pin[0] == 'present_elsewhere':
        row = pin[1]
        if row is not None and row < len(index):
            return [row], 'pinned_present_elsewhere'
    if pin and pin[0] in ('absent', 'fragment', 'pending_r15'):
        return [], pin[0]
    return [], 'unadjudicated'


def load_all_questions():
    seen = {}
    for fp in glob.glob(os.path.join(REPO, 'eval', '**', '*.jsonl'), recursive=True):
        rel = os.path.relpath(fp, REPO).replace('\\', '/')
        if rel.startswith('eval/results/'):
            continue
        with open(fp, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                q = row.get('question_sw') or row.get('question') or row.get('q')
                if q and q not in seen:
                    seen[q] = rel
    return seen


def main():
    with open(FACTS_PATH, encoding='utf-8') as f:
        facts = json.load(f)
    with open(INDEX_PATH, encoding='utf-8') as f:
        index = json.load(f)
    index_slugs = [f.split(':')[0].strip().lower() for f in index]
    with open(V2_AUDIT, encoding='utf-8') as f:
        v2 = json.load(f)
    ungrounded_keys = v2['ungrounded_keys']

    stage1_path = OUT + '.stage1.json'
    if os.path.exists(stage1_path):
        print(f'[resume] loading stage 1 classification from {stage1_path}', flush=True)
        with open(stage1_path, encoding='utf-8') as f:
            rows = json.load(f)['rows']
    else:
        rows = []
        for key in ungrounded_keys:
            v = facts[key]
            is_bare = not isinstance(v, dict)
            text = v if is_bare else json.dumps(v, ensure_ascii=False)
            idx_rows, verdict = find_index_rows(key, index, index_slugs)
            rows.append({
                'key': key,
                'is_bare_value': is_bare,
                'in_index': bool(idx_rows),
                'index_match_kind': verdict,
                'index_rows': idx_rows,
                'actionable_figure': is_actionable(key, v),
                'domain': domain_class(key, text),
            })

    print(f'ungrounded facts: {len(rows)}', flush=True)
    in_index = [r for r in rows if r['in_index']]
    print(f'in current 187-row index (reachable at all): {len(in_index)}', flush=True)
    print(f'NOT in index (never retrieved via RAG, whatever their truth value): {len(rows) - len(in_index)}', flush=True)

    # STAGE 1 checkpoint. Everything above is cheap (JSON + string ops) and has run clean on
    # every attempt; everything below (model load + embedding) segfaulted three times in a row
    # in this same process. Writing the classification here means a crash below costs only the
    # embedding stage on retry, never this one.
    if not os.path.exists(stage1_path):
        with open(stage1_path, 'w', encoding='utf-8') as f:
            json.dump({'rows': rows}, f, ensure_ascii=False, indent=2)
    print(f'[checkpoint] stage 1 (classification) saved to {stage1_path}', flush=True)

    print('loading e5 model...', flush=True)
    import numpy as np
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    print('model loaded. encoding index rows...', flush=True)
    prefixed = ['passage: ' + t for t in index]
    emb = np.array(model.encode(prefixed, show_progress_bar=False, batch_size=16))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    print(f'index encoded: {emb.shape}', flush=True)

    questions = load_all_questions()
    q_list = list(questions.keys())
    print(f'questions loaded from committed corpora: {len(q_list)}', flush=True)

    # Encoded and scored in small chunks, each flushed immediately -- R16's structural fix
    # (write per row, don't buffer to the end) applied to a crash that already happened once
    # here with zero output surviving it. A crash mid-chunk now costs one chunk, not the run.
    CHUNK = 40
    ever_top3 = set()
    hit_count = {}
    for start in range(0, len(q_list), CHUNK):
        chunk = q_list[start:start + CHUNK]
        q_prefixed = ['query: ' + q for q in chunk]
        q_emb = np.array(model.encode(q_prefixed, show_progress_bar=False, batch_size=8))
        q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)
        sims_chunk = q_emb @ emb.T
        for qi in range(len(chunk)):
            order = np.argsort(-sims_chunk[qi])[:3]
            for r in order:
                ever_top3.add(int(r))
                hit_count[int(r)] = hit_count.get(int(r), 0) + 1
        print(f'  ... {min(start + CHUNK, len(q_list))}/{len(q_list)} questions scored', flush=True)

    for r in rows:
        r['served'] = r['in_index'] and any(i in ever_top3 for i in r['index_rows'])
        r['top3_hit_count'] = sum(hit_count.get(i, 0) for i in r['index_rows']) if r['in_index'] else 0

    def tier(r):
        if not r['in_index']:
            return 'not_in_index'
        if not r['served']:
            return 'in_index_never_served'
        if r['actionable_figure'] and r['domain'] in ('core', 'pending_core_on_corporate_tax_build'):
            return 'SERVED_ACTIONABLE_HIGH_TRAFFIC'
        if r['actionable_figure']:
            return 'served_actionable_peripheral'
        return 'served_non_actionable'

    for r in rows:
        r['tier'] = tier(r)

    from collections import Counter
    tier_counts = Counter(r['tier'] for r in rows)
    domain_counts = Counter(r['domain'] for r in rows)

    top_priority = sorted(
        [r for r in rows if r['tier'] == 'SERVED_ACTIONABLE_HIGH_TRAFFIC'],
        key=lambda r: -r['top3_hit_count'])

    out = {
        'measured': '2026-08-28',
        'harness': 'scripts/size_ungrounded_fact_exposure.py',
        'input_ungrounded_set': 'eval/results/locked_facts_verification_provenance_audit_v2.json',
        'total_ungrounded': len(rows),
        'questions_swept': len(q_list),
        'index_rows': len(index),
        'tier_counts': dict(tier_counts),
        'domain_counts': dict(domain_counts),
        'top_priority_served_actionable_high_traffic': [
            {'key': r['key'], 'top3_hit_count': r['top3_hit_count'], 'domain': r['domain']}
            for r in top_priority],
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('\n=== TIER COUNTS ===')
    for t, c in tier_counts.most_common() if hasattr(tier_counts, 'most_common') else tier_counts.items():
        print(f'  {t}: {c}')
    print('\n=== DOMAIN COUNTS ===')
    for d, c in domain_counts.items():
        print(f'  {d}: {c}')
    print(f'\n=== TOP PRIORITY (served, actionable, high-traffic): {len(top_priority)} ===')
    for r in top_priority:
        print(f"  {r['key']:55s} hits={r['top3_hit_count']:3d} domain={r['domain']}")
    print(f'\n[saved] {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
