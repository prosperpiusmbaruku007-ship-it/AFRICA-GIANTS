#Read this file completely then execute every instruction below exactly as written.
First run a full state check to confirm everything is in place:

python -c "
import os, glob, json

print('=== SCRIPTS CHECK ===')
required_scripts = [
    'scripts/locked_facts.json',
    'scripts/check_locked_facts.py',
    'scripts/check_sources.py',
    'scripts/build_question_index.py',
    'scripts/generate_sft.py',
    'scripts/hf_clean_upload.py',
    'scripts/verify_pairs.py',
    'scripts/plan_next_batch.py',
    'scripts/scan_for_keys.py',
    'scripts/clean_temp_files.py',
    'scripts/check_eval_split.py',
]
for s in required_scripts:
    status = 'OK' if os.path.exists(s) else 'MISSING'
    print(f'  {status}: {s}')

print()
print('=== SKILLS CHECK ===')
required_skills = [
    'fact-guardian', 'source-enforcer', 'checkpoint-saver',
    'dedup-guard', 'pair-validator', 'training-preflight',
    'hf-uploader', 'regulatory-verifier', 'batch-planner',
    'flagged-pair-router', 'git-push-guard',
    'locked-facts-updater', 'temp-file-cleaner',
    'eval-split-enforcer',
]
for sk in required_skills:
    path = f'.claude/skills/{sk}/SKILL.md'
    status = 'OK' if os.path.exists(path) else 'MISSING'
    print(f'  {status}: {path}')

print()
print('=== CORPUS CHECK ===')
total = 0
for f in sorted(glob.glob('datasets/tier1a/cleaned_pairs/*.jsonl')):
    basename = os.path.basename(f)
    count = sum(1 for _ in open(f, encoding='utf-8'))
    if 'test' in basename.lower() or 'temp' in basename.lower():
        print(f'  TEMP FILE: {basename} ({count} pairs) — should be removed')
    else:
        print(f'  OK: {basename} ({count} pairs)')
        total += count
print(f'  Total clean pairs: {total}')

print()
print('=== FLAGGED FOLDERS CHECK ===')
folders = [
    'datasets/tier1a/flagged/consensus_blocked',
    'datasets/tier1a/flagged/needs_human_review',
    'datasets/tier1a/flagged/resolved',
]
for folder in folders:
    status = 'OK' if os.path.exists(folder) else 'MISSING'
    print(f'  {status}: {folder}')

print()
print('=== CLAUDE.md CHECK ===')
content = open('CLAUDE.md', encoding='utf-8').read()
key_rules = [
    'MANDATORY SKILLS',
    'git-push-guard',
    'GEMINI_API_KEY',
    'OPENROUTER_API_KEY',
    'Groq — blocked',
    'Cerebras — blocked',
    'locked-facts-updater',
    'eval-split-enforcer',
    'temp-file-cleaner',
]
for rule in key_rules:
    status = 'OK' if rule in content else 'MISSING'
    print(f'  {status}: {rule}')
"

Show output. If anything shows MISSING fix it before committing.

Then run key scan on all scripts:
python scripts/scan_for_keys.py

If CLEAN proceed with commit.
If any keys found fix them first.

Then run fact check on all cleaned pairs:
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_001_cleaned.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl

Both must return CLEAN before committing.

Then commit everything:
git add scripts/
git add .claude/
git add CLAUDE.md
git add datasets/tier1a/flagged/
git add datasets/tier1a/cleaned_pairs/

git commit -m "complete automation setup: 14 skills + 11 scripts + Gemini+OpenRouter cross-AI review + all session fixes applied — batch_003 ready"

git push origin main

Show commit hash then run:
python scripts/clean_temp_files.py --scan
python scripts/plan_next_batch.py

Show both outputs then STOP.
Wait for founder confirmation to start batch_003..