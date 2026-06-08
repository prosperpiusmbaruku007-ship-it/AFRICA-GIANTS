import json

with open('eval/accuracy_gate/eval_questions_001.jsonl', encoding='utf-8') as f:
    questions = [json.loads(l.strip()) for l in f if l.strip()]

# Known correct facts from CLAUDE.md
facts = {
    'vat_standard_rate': '18',
    'vat_zanzibar_rate': '15',
    'vat_threshold_12m': '200',
    'vat_threshold_6m': '100',
    'vat_withholding_goods': '3',
    'vat_withholding_services': '6',
    'vat_return_deadline': '20',
    'sdl_rate': '3.5',
    'sdl_threshold': '10',
    'sdl_deadline': '7',
    'nssf_total': '20',
    'nssf_employer_standard': '10',
    'nssf_employee_standard': '10',
    'nssf_penalty': '5',
    'wcf_rate': '0.5',
    'gn487a_categories': '15',
    'gn487a_noncitizen_fine': '10',
    'gn487a_noncitizen_prison': '6',
    'gn487a_facilitator_fine': '5',
    'gn487a_facilitator_prison': '3',
    'osha_safety_officer': '50',
    'gn605a_average_wage': '358',
}

# Known WRONG numbers that must NOT appear as correct answers
wrong_facts = {
    'sdl_threshold_wrong': ['4', 'wanne'],
    'vat_rate_wrong': ['16', '15'],  # 16 only for B2C electronic, 15 is Zanzibar only
    'nssf_deadline_wrong': ['20'],   # 20th is VAT deadline not NSSF
    'gn487a_categories_wrong': ['14', '16', '20'],
    'gn487a_fine_wrong': ['5000000', 'milioni 5'],  # 5M is facilitator fine not non-citizen
}

print("=" * 60)
print(f"FULL EVAL SET REVIEW — {len(questions)} questions")
print("=" * 60)

issues = []

for q in questions:
    qid = q['id']
    sub = q['subdomain']
    ans_sw = q['correct_answer_sw']
    ans_en = q['correct_answer_en']
    ans_type = q['answer_type']
    q_sw = q['question_sw']

    # Check out_of_corpus questions have canonical refusal text
    if ans_type == 'out_of_corpus_refusal':
        if 'nje ya maarifa' not in ans_sw:
            issues.append(f"{qid}: out_of_corpus missing canonical refusal text")
        continue

    # Check SDL threshold — must never say 4
    if sub == 'sdl_compliance':
        if ' 4 ' in ans_sw or 'wanne' in ans_sw.lower():
            issues.append(f"{qid}: SDL threshold wrong — says 4, should be 10")

    # Check VAT rate questions — standard rate must be 18 not 16
    if sub == 'vat_registration' and 'kiwango' in q_sw.lower() and 'standard' in q_sw.lower():
        if '16' in ans_sw and '18' not in ans_sw:
            issues.append(f"{qid}: VAT standard rate wrong — says 16, should be 18")

    # Check NSSF deadline — must not say 20th
    if sub == 'nssf_contributions' and 'deadline' in q_sw.lower() or 'tarehe' in q_sw.lower():
        if 'siku ya 20' in ans_sw and 'VAT' not in ans_sw:
            issues.append(f"{qid}: NSSF deadline wrong — says 20th without clarifying that is VAT")

    # Check GN487A non-citizen fine — must be 10M not 5M
    if sub == 'gn487a' and ('faini' in q_sw.lower() or 'adhabu' in q_sw.lower()):
        if 'milioni 5' in ans_sw and 'milioni 10' not in ans_sw and 'msaidizi' not in ans_sw.lower() and 'facilitator' not in ans_en.lower():
            issues.append(f"{qid}: GN487A fine may be wrong — 5M is facilitator fine, 10M is non-citizen fine. Review: {ans_sw[:80]}")

    # Check NeST not TANePS
    if 'tAneps' in ans_sw.lower() or 'taneps' in ans_sw.lower():
        issues.append(f"{qid}: BANNED — mentions TANePS which was decommissioned. Use NeST.")

    # Check empty answers
    if not ans_sw.strip() or not ans_en.strip():
        issues.append(f"{qid}: Empty answer field")

# Subdomain counts
from collections import Counter
counts = Counter(q['subdomain'] for q in questions)
targets = {
    'vat_registration': 30,
    'vat_withholding': 20,
    'efd_compliance': 20,
    'brela_registration': 15,
    'nssf_contributions': 25,
    'sdl_compliance': 25,
    'gn487a': 40,
    'osha_registration': 15,
    'out_of_corpus': 10,
}

print("\nSUBDOMAIN COUNTS vs TARGETS:")
for sub, target in targets.items():
    actual = counts.get(sub, 0)
    status = "OK" if actual == target else f"WRONG — got {actual}"
    print(f"  {sub}: {actual}/{target} {status}")

print(f"\nFACT CHECKS — scanning all answers for known wrong values:")
print(f"  Issues found: {len(issues)}")
if issues:
    for issue in issues:
        print(f"  ⚠ {issue}")
else:
    print("  No fact errors detected")

print("\nSAMPLE REVIEW — printing every 20th question for human spot check:")
for i in range(0, len(questions), 20):
    q = questions[i]
    print(f"\n  {q['id']} [{q['subdomain']}] [{q['answer_type']}]")
    print(f"  Q: {q['question_sw']}")
    print(f"  A: {q['correct_answer_sw'][:120]}")