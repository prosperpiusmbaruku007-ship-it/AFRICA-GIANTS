"""Slot-extraction stress-test review via frontier LLM-as-judge (qwen/qwen3-32b on OpenRouter).

Same pattern/discipline as kaggle/judge_regression.py: self-contained, reusable, results
PERSISTED to disk (not just printed). Read-only w.r.t. the source stress-test file — writes a
SEPARATE reviewed file. Reviews each entry of data/reviewed/slot_extraction_stress_test_001.jsonl
against scripts/locked_facts.json on three axes:

  (1) NUMBER FIDELITY  — where the question implies a specific rate/threshold/calculation, does
      `expected_behavior` state the correct resolution vs the relevant locked fact?
  (2) CATEGORY FIT     — is `failure_category` accurate for what the question actually tests?
  (3) SELF-CONSISTENCY — is `expected_behavior` clear and internally consistent, or does it carry
      an error of its own (the eval_176/eval_190 class: a reference that contradicts locked_facts)?

Verdict per entry: correct | needs_revision | flag_for_human_review  (+ one-sentence reason).
Output is ADDITIVE ONLY: appends _review_verdict, _review_reason. No existing field touched.

Run modes:
  python kaggle/slot_extraction_review.py sample   # ~13 entries spanning subdomains/categories
  python kaggle/slot_extraction_review.py full      # all 205 -> writes the reviewed .jsonl + summary

Auth: OPENROUTER_API_KEY from env (local) or Kaggle secret. Reads local repo files if present,
else fetches from GitHub raw (so it also runs on Kaggle with Internet ON, no GPU).
"""
import os, sys, json, re, time, requests
from concurrent.futures import ThreadPoolExecutor

REPO_RAW = ('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
            'AFRICA-GIANTS/main')
SRC_REL = 'data/reviewed/slot_extraction_stress_test_001.jsonl'
OUT_REL = 'data/reviewed/slot_extraction_stress_test_001_reviewed.jsonl'
FACTS_REL = 'scripts/locked_facts.json'

MODEL = 'qwen/qwen3-32b'
PRICE_IN = 0.00000008     # USD/prompt token  (OpenRouter listing)
PRICE_OUT = 0.00000028    # USD/completion token

# ---- auth ------------------------------------------------------------------
try:
    import kaggle_secrets
    OR_KEY = kaggle_secrets.UserSecretsClient().get_secret('OPENROUTER_API_KEY')
    print('[auth] OpenRouter secret loaded from Kaggle')
except Exception:
    OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    print(f'[auth] env OPENROUTER_API_KEY={"set" if OR_KEY else "MISSING"}')
assert OR_KEY, 'OPENROUTER_API_KEY missing'


def _load(rel):
    if os.path.exists(rel):
        return open(rel, encoding='utf-8').read()
    print(f'[fetch] {rel} not local -> GitHub raw')
    r = requests.get(f'{REPO_RAW}/{rel}?cb={int(time.time())}',
                     headers={'Cache-Control': 'no-cache'}, timeout=30)
    r.raise_for_status()
    return r.text


rows = [json.loads(l) for l in _load(SRC_REL).splitlines() if l.strip()]
FACTS = json.loads(_load(FACTS_REL))
print(f'[data] {len(rows)} stress-test entries | {len(FACTS)} locked facts')

# ---- compact all-subdomain compliance digest (numbers/thresholds/methods) --
# Included in EVERY call so compound cross-subdomain questions are fully covered.
DIGEST_KEYS = [
    'sdl_rate', 'sdl_threshold', 'sdl_payer', 'sdl_payment_deadline', 'sdl_calculation_example',
    'nssf_employer_rate', 'nssf_total_rate', 'nssf_penalty', 'nssf_payment_deadline',
    'nssf_calculation_example', 'nssf_employer_registration_deadline',
    'paye_all_bands_sequence', 'paye_nonresident_flat_rate', 'paye_personal_relief',
    'paye_penalty_rate', 'paye_bands_with_examples',
    'wcf_rate_0_5_percent_confirmed', 'wcf_threshold_no_minimum', 'wcf_accident_reporting',
    'wcf_new_employer_registration',
    'vat_registration_threshold', 'vat_standard_rate', 'efd_threshold_tzs_11m',
    'brela_annual_return_fee', 'company_name_reservation_fee', 'BRELA_fees_hedge',
    'osha_registration_threshold_b004', 'OSHA_safety_officer_threshold', 'OSHA_annual_inspection',
    'gn487a_nature', 'gn487a_effective_date', 'gn487a_penalty_noncitizen',
    'gn487a_penalty_citizen_facilitator', 'gn487a_mgeni_cap357_definition',
    'gn487a_shareholder_vs_operator_distinction', 'gn487a_total_prohibited_activities',
]


def _digest():
    lines = []
    for k in DIGEST_KEYS:
        f = FACTS.get(k)
        if not f:
            continue
        if isinstance(f, str):
            fact, cv = f, ''
        else:
            fact = str(f.get('fact', '')).strip()
            cv = str(f.get('correct_value', '')).strip()
        fact = fact.replace('�', '-').strip()
        lines.append(f'- {k}: {fact}' + (f'  [correct_value: {cv}]' if cv else ''))
    return '\n'.join(lines)


DIGEST = _digest()
print(f'[digest] {len(DIGEST_KEYS)} facts, {len(DIGEST)} chars')

SUBDOMAINS = sorted(set(r['subdomain'] for r in rows))
CATEGORIES = sorted(set(r['failure_category'] for r in rows))

# ---- judge prompt ----------------------------------------------------------
REVIEW_SYS = (
    "You are a bilingual Kiswahili/English reviewer auditing a SLOT-EXTRACTION stress-test set "
    "for a Tanzanian tax/labour/business-registration assistant. Each test entry is a Swahili "
    "user question that DELIBERATELY contains a vague, missing, approximate, or ambiguous number "
    "(that is the point of the test). The entry's `expected_behavior` describes how a correct "
    "extraction stage should react — very often the correct reaction is to ASK the user for the "
    "exact figure and NOT guess. That is CORRECT design, never an error.\n\n"
    "You are given a table of LOCKED FACTS (authoritative Tanzanian rates, thresholds, and "
    "calculation methods). Audit the entry on exactly three axes:\n"
    "(1) NUMBER FIDELITY: if `expected_behavior` asserts any rate/threshold/figure/calculation "
    "method (e.g. 'SDL 10-employee threshold', 'WCF 0.5%', 'PAYE bands', 'NSSF 20%'), does it "
    "MATCH the locked fact? A wrong or contradicted number is the most serious problem.\n"
    "(2) CATEGORY FIT: does `failure_category` accurately describe what the question actually "
    "tests? Use this fixed taxonomy — if a DIFFERENT label clearly fits better, that is a "
    "needs_revision defect:\n"
    "   - vague_quantity: a non-numeric fuzzy quantity word (wachache/wengi/ndogo) with NO figure.\n"
    "   - swahili_number_words: a figure IS given but in Swahili/mixed word form needing parsing.\n"
    "   - period_conversion: a figure is given for the WRONG period (annual/weekly/quarterly) and "
    "must be converted to the required period.\n"
    "   - aggregate_vs_per_person: both a total and a headcount appear, inviting a wrong per-head "
    "vs aggregate step.\n"
    "   - non_uniform_figures: several people on DIFFERENT stated salaries.\n"
    "   - gross_net_allowance: tests gross vs net / allowance inclusion in the base.\n"
    "   - missing_antecedent: references an earlier turn ('hao', 'ile') — empty without memory.\n"
    "   - casual_slang: colloquial hedges ('ka-12 hivi', 'around ten', 'na kitu').\n"
    "   - compound_question: two unrelated compliance domains stacked in one message.\n"
    "   - wrong_calculation_number: a real, precise number is present but is the WRONG base for "
    "the asked tax (a trap, e.g. sales turnover offered for a payroll-based levy).\n"
    "(3) SELF-CONSISTENCY: is `expected_behavior` clear and internally consistent, or does it "
    "contain its own ambiguity/error (like a reference that contradicts the locked facts)?\n\n"
    "Verdicts:\n"
    "- correct: all three axes fine; asking-for-clarification is fine; no factual conflict.\n"
    "- needs_revision: a concrete, fixable defect you can name (wrong number vs locked fact, "
    "mislabeled category, or a clear internal inconsistency).\n"
    "- flag_for_human_review: genuinely ambiguous, or depends on a fact NOT in the locked table, "
    "or you cannot confidently decide — escalate rather than guess.\n"
    "Judge substance, not surface wording. Keep the reason to ONE sentence."
)


VALID = ('correct', 'needs_revision', 'flag_for_human_review')


def _parse_verdict(msg):
    """Robustly pull {verdict, reason} from a (possibly reasoning-prefixed) reply."""
    # 1) last balanced {...} object that mentions "verdict"
    cands = []
    for m in re.finditer(r'\{', msg):
        depth, i = 0, m.start()
        for j in range(m.start(), len(msg)):
            if msg[j] == '{':
                depth += 1
            elif msg[j] == '}':
                depth -= 1
                if depth == 0:
                    blk = msg[i:j + 1]
                    if '"verdict"' in blk:
                        cands.append(blk)
                    break
    for blk in reversed(cands):
        try:
            o = json.loads(blk)
            v = str(o.get('verdict', '')).lower().strip()
            if v in VALID:
                return v, str(o.get('reason', ''))[:240]
        except Exception:
            continue
    # 2) field-level regex fallback
    vm = re.search(r'"verdict"\s*:\s*"([^"]+)"', msg)
    rm = re.search(r'"reason"\s*:\s*"([^"]*)"', msg)
    if vm:
        v = vm.group(1).lower().strip()
        if v in VALID:
            return v, (rm.group(1)[:240] if rm else '')
    # 3) bare keyword scan
    lm = msg.lower()
    for v in ('needs_revision', 'flag_for_human_review', 'correct'):
        if v in lm:
            return v, (rm.group(1)[:240] if rm else '')
    return '', ''


def review(entry):
    user = (
        f"LOCKED FACTS (authoritative):\n{DIGEST}\n\n"
        f"--- TEST ENTRY TO AUDIT ---\n"
        f"id: {entry['id']}\n"
        f"subdomain: {entry['subdomain']}\n"
        f"failure_category: {entry['failure_category']}\n"
        f"question_sw: {entry['question_sw']}\n"
        f"expected_behavior: {entry['expected_behavior']}\n"
        f"why_hard: {entry.get('why_hard','')}\n\n"
        'Return ONLY a JSON object, no other text:\n'
        '{"verdict": "correct" | "needs_revision" | "flag_for_human_review", '
        '"reason": "<one sentence>"}'
    )
    # NOTE: qwen3-32b via OpenRouter ignores reasoning.enabled=false (still emits reasoning
    # tokens), so we give a generous cap to guarantee the final JSON is not truncated.
    body = {'model': MODEL, 'temperature': 0, 'max_tokens': 1500,
            'messages': [{'role': 'system', 'content': REVIEW_SYS},
                         {'role': 'user', 'content': user}]}
    t = time.time()
    verdict, reason, pin, pout, err = 'flag_for_human_review', '', 0, 0, ''
    for attempt in range(3):
        try:
            resp = requests.post('https://openrouter.ai/api/v1/chat/completions',
                                 headers={'Authorization': 'Bearer ' + OR_KEY,
                                          'Content-Type': 'application/json'},
                                 json=body, timeout=120)
            j = resp.json()
            if 'choices' not in j:
                err = str(j.get('error', j))[:160]
                time.sleep(2 + attempt * 3); continue
            msg = j['choices'][0]['message']['content'] or ''
            u = j.get('usage', {}) or {}
            pin, pout = u.get('prompt_tokens', 0), u.get('completion_tokens', 0)
            verdict, reason = _parse_verdict(msg)
            if verdict not in ('correct', 'needs_revision', 'flag_for_human_review'):
                err = f'unparseable: {msg[:120]!r}'
                verdict = 'flag_for_human_review'
            else:
                err = ''
            break
        except Exception as e:
            err = f'{type(e).__name__}: {e}'[:160]
            time.sleep(2 + attempt * 3)
    return {'id': entry['id'], 'verdict': verdict, 'reason': reason,
            'pin': pin, 'pout': pout, 'dt': round(time.time() - t, 2), 'err': err}


# ---- sample selection (spans all 8 subdomains + 6 categories) --------------
SAMPLE_IDS = ['extract_001', 'extract_003', 'extract_007', 'extract_011', 'extract_014',
              'extract_006', 'extract_025', 'extract_027', 'extract_041', 'extract_062',
              'extract_074', 'extract_088', 'extract_120']


def run(items, workers):
    out = {}
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(review, items):
            out[r['id']] = r
            done += 1
            if done % 40 == 0:
                print(f'   ...{done}/{len(items)} ({time.time()-t0:.0f}s)', flush=True)
    return out, time.time() - t0


def summarize(results, items):
    from collections import Counter, defaultdict
    verdicts = Counter(results[i['id']]['verdict'] for i in items)
    by_cat = defaultdict(Counter)
    by_sub = defaultdict(Counter)
    for i in items:
        v = results[i['id']]['verdict']
        by_cat[i['failure_category']][v] += 1
        by_sub[i['subdomain']][v] += 1
    return verdicts, by_cat, by_sub


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sample'
    by_id = {r['id']: r for r in rows}

    if mode == 'sample':
        items = [by_id[i] for i in SAMPLE_IDS]
        print(f'\n[sample] {len(items)} entries, 6 workers ...', flush=True)
        results, wall = run(items, 6)
        print('\n' + '=' * 72)
        for i in items:
            r = results[i['id']]
            print(f"\n{i['id']}  [{i['subdomain']} / {i['failure_category']}]  -> {r['verdict'].upper()}")
            print(f"   Q: {i['question_sw']}")
            print(f"   expected: {i['expected_behavior'][:150]}")
            print(f"   REASON: {r['reason']}")
            if r['err']:
                print(f"   ERR: {r['err']}")
        v, _, _ = summarize(results, items)
        tin = sum(results[i['id']]['pin'] for i in items)
        tout = sum(results[i['id']]['pout'] for i in items)
        cost = tin * PRICE_IN + tout * PRICE_OUT
        mean = sum(results[i['id']]['dt'] for i in items) / len(items)
        print('\n' + '=' * 72)
        print(f'[sample] verdicts: {dict(v)}')
        print(f'[sample] tokens in/out={tin}/{tout}  cost=${cost:.4f}  mean/call={mean:.2f}s  wall={wall:.0f}s')
        print(f'\n[full-batch estimate] 205 calls:')
        print(f'   cost  ~ ${cost/len(items)*205:.3f}')
        print(f'   wall  ~ {mean*205/8:.0f}s at 8 workers (~{mean:.1f}s/call)')
        json.dump({'mode': 'sample', 'model': MODEL, 'ids': SAMPLE_IDS,
                   'results': [results[i] for i in SAMPLE_IDS]},
                  open('data/reviewed/_review_sample.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        print('\n[persist] data/reviewed/_review_sample.json')
        print('\nSAMPLE_DONE — confirm the prompt behaves, then run: full')

    elif mode == 'full':
        items = rows
        print(f'\n[full] {len(items)} entries, 8 workers ...', flush=True)
        results, wall = run(items, 8)
        # additive write — original fields untouched, append _review_verdict/_review_reason
        with open(OUT_REL, 'w', encoding='utf-8') as f:
            for r in rows:
                rec = dict(r)
                jr = results[r['id']]
                rec['_review_verdict'] = jr['verdict']
                rec['_review_reason'] = jr['reason']
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        v, by_cat, by_sub = summarize(results, items)
        tin = sum(r['pin'] for r in results.values())
        tout = sum(r['pout'] for r in results.values())
        cost = tin * PRICE_IN + tout * PRICE_OUT
        mean = sum(r['dt'] for r in results.values()) / len(results)
        errs = [r for r in results.values() if r['err']]
        summary = {
            'mode': 'full', 'model': MODEL, 'n': len(items),
            'verdicts': dict(v),
            'by_category': {k: dict(c) for k, c in by_cat.items()},
            'by_subdomain': {k: dict(c) for k, c in by_sub.items()},
            'needs_revision': [{'id': i['id'], 'subdomain': i['subdomain'],
                                'failure_category': i['failure_category'],
                                'question_sw': i['question_sw'],
                                'expected_behavior': i['expected_behavior'],
                                'reason': results[i['id']]['reason']}
                               for i in items if results[i['id']]['verdict'] == 'needs_revision'],
            'flag_for_human_review': [{'id': i['id'], 'subdomain': i['subdomain'],
                                       'failure_category': i['failure_category'],
                                       'question_sw': i['question_sw'],
                                       'expected_behavior': i['expected_behavior'],
                                       'reason': results[i['id']]['reason']}
                                      for i in items if results[i['id']]['verdict'] == 'flag_for_human_review'],
            'cost_usd': round(cost, 4), 'tokens_in': tin, 'tokens_out': tout,
            'wall_s': round(wall, 1), 'mean_per_call_s': round(mean, 2),
            'api_errors': [{'id': e['id'], 'err': e['err']} for e in errs],
        }
        json.dump(summary, open('data/reviewed/_review_summary.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        print('\n' + '=' * 72)
        print(f'[full] verdicts: {dict(v)}')
        print(f'[full] cost=${cost:.4f} tokens={tin}/{tout} wall={wall:.0f}s mean/call={mean:.2f}s errors={len(errs)}')
        print(f'[persist] {OUT_REL}')
        print(f'[persist] data/reviewed/_review_summary.json')
        print('\nFULL_DONE')
    else:
        print(f'unknown mode {mode!r} — use "sample" or "full"')


if __name__ == '__main__':
    main()
