"""Run 2, parts 1-2 — numeric-query retrieval A/B (single-arm v15 vs two-arm chike/).

WHAT THIS ANSWERS
-----------------
`chike/retrieval.py` carries a two-arm hybrid (commit d92e63f, 2026-07-18) that production
(`chike-inference/modal_app.py::retrieve_facts`) and the live gate (`kaggle/eval.py`) do NOT
have: on a digit-bearing query it runs a SECOND number-stripped retrieval and APPENDS the
first new fact it surfaces. That is the largest untested fact-path divergence in the tree,
and the 005b dual-path probe could not exercise it at all — all five of its questions are
digit-free, so the second arm never fired.

The hybrid is APPEND-ONLY by construction: the full-query top-3 is preserved verbatim, never
reordered or dropped. So displacement is structurally zero and the entire question is what the
appended 4th fact does — recovery (it is the fact the answer needed) vs dilution (it is noise
in the prompt). This script measures exactly that, with NO model and NO GPU.

Part 3 of Run 2 (the generation de-confound arm: v16 run twice over the digit-bearing subset,
two-arm vs single-arm) rides along with the Run 1 paired GPU notebook — not here.

KAGGLE SETUP
------------
  Accelerator : NONE (CPU only)
  Internet    : ON  (GitHub raw + the public e5-base model from HuggingFace)
  Secrets     : NONE required. No HF token, no OpenRouter key, no Modal token.
  Runtime     : ~5-10 min (e5-base download + ~600 CPU encodes)

Everything is fetched from GitHub main with cache-busting, and the live HEAD sha is printed
at startup (R15 discipline: raw.githubusercontent has a ~5 min CDN TTL, so a stale copy would
silently measure old logic). Paste back the SUMMARY BLOCK at the end.
"""
import ast
import io
import json
import time

import numpy as np
import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
NOCACHE = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
CB = str(int(time.time() * 1000))

EXPECTED_FACT_COUNT = 217   # the deployed index (R15, 2026-07-27). A mismatch must be loud.

print('=' * 78)
print('RUN 2 (parts 1-2) — numeric-query retrieval A/B: single-arm vs two-arm')
print('=' * 78)

# ── Provenance: prove we are measuring the current commit, not a CDN-cached one ──
try:
    _sha = requests.get(f'https://api.github.com/repos/{REPO}/commits/main',
                        headers=NOCACHE, timeout=20).json().get('sha', '?')[:7]
    print(f'[chike] GitHub main HEAD = {_sha} (all sources fetched from THIS commit)')
except Exception as e:                                          # noqa: BLE001
    _sha = '?'
    print(f'[chike] HEAD sha check FAILED ({e}) — provenance unverified, treat results with care')


def _get(path, binary=False):
    r = requests.get(f'{RAW}/{path}?cb={CB}', headers=NOCACHE, timeout=60)
    r.raise_for_status()
    print(f'[fetch] {path} ({len(r.content)} bytes)')
    return r.content if binary else r.text


# ── The module UNDER TEST: the real committed chike/retrieval.py, exec'd standalone ──
# Leaf module (numpy + stdlib, no chike-internal imports), same fetch+exec pattern eval.py
# uses for prompting/generation_cleanup/classification. We test the actual shipped code, not
# a reimplementation of it.
_retr_src = _get('chike/retrieval.py')
_retr = {'__file__': 'retrieval.py', '__name__': 'chike_retrieval_under_test'}
exec(compile(_retr_src, 'chike/retrieval.py', 'exec'), _retr)          # noqa: S102
Retriever = _retr['Retriever']
strip_numeric_amounts = _retr['strip_numeric_amounts']
print(f'[chike] chike/retrieval.py loaded ({len(_retr_src)} bytes)')

# ── Data: the 400-question corpus + the deployed 217-fact index (all git-tracked) ──
QFILES = [
    ('gate_001', 'eval/accuracy_gate/eval_questions_001.jsonl', 200),
    ('additions_002', 'eval/accuracy_gate/eval_questions_002_additions.jsonl', 50),
    ('additions_003', 'eval/accuracy_gate/eval_questions_003.jsonl', 150),
]
ALL = []
for src, path, n in QFILES:
    rows = [json.loads(l) for l in _get(path).splitlines() if l.strip()]
    assert len(rows) == n, f'{src}: expected {n}, got {len(rows)}'
    for r in rows:
        r['_src'] = src
    ALL += rows
print(f'[data] {len(ALL)} questions (200 gate + 50 additions + 150 adversarial)')

open('rag_embeddings.npy', 'wb').write(_get('kaggle/rag_embeddings.npy', binary=True))
open('rag_facts_text.json', 'wb').write(_get('kaggle/rag_facts_text.json', binary=True))

# Construct through the real fail-loud contract (commit 149938d): explicit paths +
# expected_fact_count + preflight. If the index is stale or inconsistent this raises HERE,
# before any measurement, instead of quietly measuring the wrong index.
retriever = Retriever(emb_path='rag_embeddings.npy', texts_path='rag_facts_text.json',
                      expected_fact_count=EXPECTED_FACT_COUNT)
n_facts = retriever.preflight()
print(f'[rag] index preflight OK — {n_facts} facts')

FACTS = retriever.fact_texts
FACTS_LOWER = [f.lower() for f in FACTS]

print('[e5] loading intfloat/multilingual-e5-base (CPU) ...')
retriever._ensure_embed_model()
print('[e5] ready')


def single_arm(q, top_k=3):
    """Production's retrieval, byte-identical to modal_app.retrieve_facts: one 'query: '
    encode, cosine over L2-normalized vectors, top-k. This is the v15 arm."""
    return [FACTS[i] for i in retriever._encode_and_rank(q, top_k)]


def two_arm(q, top_k=3):
    """chike/retrieval.py's shipped retrieve(): the v16 arm."""
    return retriever.retrieve(q, top_k=top_k)


# ══════════════════════════════════════════════════════════════════════════════
# PART 1 — how often does the second arm fire, and what does it append?
# ══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 78)
print('PART 1 — second-arm firing rate + appended-fact inventory')
print('=' * 78)

digit = [r for r in ALL if any(c.isdigit() for c in r['question_sw'])]
eligible = [r for r in digit
            if strip_numeric_amounts(r['question_sw']) not in ('', r['question_sw'])]
print(f'digit-bearing: {len(digit)}/{len(ALL)} | second-arm eligible: {len(eligible)}')

append_only_violations = []
gained, unchanged = [], []
appended_counts = {}
by_subdomain = {}

for i, r in enumerate(eligible):
    q = r['question_sw']
    sa = single_arm(q)
    ta = two_arm(q)

    # The structural claim being VERIFIED, not assumed: the first 3 must be byte-identical.
    if ta[:3] != sa:
        append_only_violations.append({'id': r['id'], 'single': sa, 'two': ta[:3]})

    sd = r.get('subdomain', '?')
    slot = by_subdomain.setdefault(sd, {'eligible': 0, 'gained': 0})
    slot['eligible'] += 1

    if len(ta) > 3:
        extra = ta[3]
        gained.append({'id': r['id'], 'subdomain': sd, 'question': q,
                       'appended': extra, 'top3': sa})
        appended_counts[extra] = appended_counts.get(extra, 0) + 1
        slot['gained'] += 1
    else:
        unchanged.append(r['id'])

    if (i + 1) % 40 == 0:
        print(f'  ... {i + 1}/{len(eligible)}')

print(f'\ngained a 4th fact : {len(gained)}/{len(eligible)}')
print(f'no change         : {len(unchanged)}/{len(eligible)}')
print(f'append-only VIOLATIONS (top-3 changed): {len(append_only_violations)}')
for v in append_only_violations[:5]:
    print(f'  !! {v["id"]}')

print('\nmost frequently appended facts (fact -> times appended):')
for fact, cnt in sorted(appended_counts.items(), key=lambda kv: -kv[1])[:15]:
    print(f'  {cnt:>4}x  {fact[:100]}')

print('\nby subdomain (gained / eligible):')
for sd in sorted(by_subdomain):
    s = by_subdomain[sd]
    print(f'  {sd:<24} {s["gained"]:>4} / {s["eligible"]:<4}')

# ══════════════════════════════════════════════════════════════════════════════
# PART 2, SET A — the R15 critical known-failure queries (keyword gold labels)
# ══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 78)
print('PART 2 / SET A — R15 critical queries: rank-of-correct, single-arm vs two-arm')
print('=' * 78)

# Parsed straight out of kaggle/regenerate_rag_e5.py so this set can never drift from the
# R15 verification list (ast.literal_eval on the assignment — the file is NOT executed).
_regen_src = _get('kaggle/regenerate_rag_e5.py')
critical_queries = []
for node in ast.walk(ast.parse(_regen_src)):
    if (isinstance(node, ast.Assign) and node.targets
            and getattr(node.targets[0], 'id', None) == 'critical_queries'):
        critical_queries = ast.literal_eval(node.value)
        break
print(f'[setA] {len(critical_queries)} critical queries parsed from regenerate_rag_e5.py')


def rank_of_gold(facts, expected_keywords):
    """1-based rank of the first fact containing ANY expected keyword; 0 = not found."""
    for rank, f in enumerate(facts, 1):
        low = f.lower()
        if any(kw.lower() in low for kw in expected_keywords):
            return rank
    return 0


setA_rows = []
for name, query, expected in critical_queries:
    q = query[len('query: '):] if query.startswith('query: ') else query
    has_digit = any(c.isdigit() for c in q)
    sa, ta = single_arm(q), two_arm(q)
    r_sa, r_ta = rank_of_gold(sa, expected), rank_of_gold(ta, expected)
    setA_rows.append({'name': name, 'digit': has_digit, 'n_two': len(ta),
                      'rank_single': r_sa, 'rank_two': r_ta})

a_hit_sa = sum(1 for r in setA_rows if r['rank_single'])
a_hit_ta = sum(1 for r in setA_rows if r['rank_two'])
a_recovered = [r for r in setA_rows if not r['rank_single'] and r['rank_two']]
a_lost = [r for r in setA_rows if r['rank_single'] and not r['rank_two']]

print(f'hit (gold retrieved)  single-arm {a_hit_sa}/{len(setA_rows)} | '
      f'two-arm {a_hit_ta}/{len(setA_rows)}')
print(f'recovered by the 2nd arm: {len(a_recovered)}  | lost: {len(a_lost)} '
      '(lost MUST be 0 — the hybrid is append-only)')
for r in a_recovered:
    print(f'  + RECOVERED  {r["name"]} (rank {r["rank_two"]})')
for r in a_lost:
    print(f'  ! LOST       {r["name"]}')
print('\nper-query (name | digits | rank single -> rank two):')
for r in setA_rows:
    print(f'  {r["name"][:46]:<46} {"D" if r["digit"] else " "}  '
          f'{r["rank_single"]} -> {r["rank_two"]}')

# ══════════════════════════════════════════════════════════════════════════════
# PART 2, SET B — auto-labelled gold FACT SET over the digit-bearing 400 subset
# ══════════════════════════════════════════════════════════════════════════════
# Honest labelling note: a *unique* gold fact per question is not derivable — only 11 of the
# 197 eligible questions map to exactly one fact. So the label is a gold SET: every index fact
# containing a >=4-digit number that also appears in the question's correct_answer_sw. A
# question is "on target" if ANY gold-set fact is retrieved. Questions with no numeric label
# are reported as uncovered rather than silently scored.
print('\n' + '=' * 78)
print('PART 2 / SET B — gold-fact-SET hit rate over the digit-bearing subset')
print('=' * 78)

import re                                                        # noqa: E402

NUM = re.compile(r'\d[\d,\.]{3,}')


def _norm_num(s):
    return s.replace(',', '').replace('.', '')


def _numbers_in(text):
    """Normalized numeric tokens in a string. Tokenised (not substring-matched) so that
    e.g. '50,000,000' in a fact does not spuriously match a question whose gold answer
    mentions '5,000,000' — a real false label seen in the dry run."""
    return {_norm_num(m.group()) for m in NUM.finditer(text or '')}


_fact_numsets = [_numbers_in(f) for f in FACTS]


def gold_set(row):
    nums = {n for n in _numbers_in(row.get('correct_answer_sw', '')) if len(n) >= 4}
    if not nums:
        return set()
    return {i for i, fn in enumerate(_fact_numsets) if nums & fn}


labelled, uncovered = [], 0
for r in eligible:
    gs = gold_set(r)
    if gs:
        labelled.append((r, gs))
    else:
        uncovered += 1

print(f'labelled: {len(labelled)}/{len(eligible)}  | uncovered (no numeric label): {uncovered}')

b_hit_sa = b_hit_ta = 0
b_recovered, b_diluted = [], []
for r, gs in labelled:
    q = r['question_sw']
    sa, ta = single_arm(q), two_arm(q)
    gold_texts = {FACTS[i] for i in gs}
    hit_sa = any(f in gold_texts for f in sa)
    hit_ta = any(f in gold_texts for f in ta)
    b_hit_sa += hit_sa
    b_hit_ta += hit_ta
    if not hit_sa and hit_ta:
        b_recovered.append({'id': r['id'], 'subdomain': r.get('subdomain'),
                            'appended': ta[3] if len(ta) > 3 else None})
    if len(ta) > 3 and ta[3] not in gold_texts:
        b_diluted.append(r['id'])

den = len(labelled) or 1
print(f'gold-set hit  single-arm {b_hit_sa}/{len(labelled)} ({b_hit_sa / den:.1%}) | '
      f'two-arm {b_hit_ta}/{len(labelled)} ({b_hit_ta / den:.1%})')
print(f'RECOVERED (gold missed by top-3, supplied by the appended fact): {len(b_recovered)}')
for r in b_recovered[:20]:
    print(f'  + {r["id"]} [{r["subdomain"]}] <- {str(r["appended"])[:80]}')
print(f'DILUTION (appended fact is NOT a gold fact): {len(b_diluted)}/{len(labelled)} labelled')

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY BLOCK — paste this back
# ══════════════════════════════════════════════════════════════════════════════
print('\n\n' + '#' * 78)
print('### RUN 2 PARTS 1-2 SUMMARY — PASTE EVERYTHING BETWEEN THE # LINES ###')
print('#' * 78)
summary = {
    'github_head': _sha,
    'index_facts': n_facts,
    'corpus_total': len(ALL),
    'part1': {
        'digit_bearing': len(digit),
        'second_arm_eligible': len(eligible),
        'gained_4th_fact': len(gained),
        'unchanged': len(unchanged),
        'append_only_violations': len(append_only_violations),
        'violation_ids': [v['id'] for v in append_only_violations][:20],
        'top_appended_facts': [
            {'times': c, 'fact': f[:120]}
            for f, c in sorted(appended_counts.items(), key=lambda kv: -kv[1])[:10]
        ],
        'by_subdomain': by_subdomain,
    },
    'part2_setA_critical': {
        'n': len(setA_rows),
        'hit_single_arm': a_hit_sa,
        'hit_two_arm': a_hit_ta,
        'recovered': [r['name'] for r in a_recovered],
        'lost': [r['name'] for r in a_lost],
        'rank_changes': [
            {'name': r['name'], 'single': r['rank_single'], 'two': r['rank_two']}
            for r in setA_rows if r['rank_single'] != r['rank_two']
        ],
    },
    'part2_setB_goldset': {
        'eligible': len(eligible),
        'labelled': len(labelled),
        'uncovered_no_numeric_label': uncovered,
        'hit_single_arm': b_hit_sa,
        'hit_two_arm': b_hit_ta,
        'recovered': b_recovered[:30],
        'dilution_count': len(b_diluted),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=1))
print('#' * 78)
print('### END SUMMARY ###')
print('#' * 78)

with open('rag_numeric_ab_run2_summary.json', 'w', encoding='utf-8') as fh:
    json.dump({'summary': summary, 'gained_detail': gained, 'setA_rows': setA_rows},
              fh, ensure_ascii=False, indent=1)
print('\n[done] full detail also written to rag_numeric_ab_run2_summary.json '
      '(Kaggle output — download it if the paste is truncated)')
