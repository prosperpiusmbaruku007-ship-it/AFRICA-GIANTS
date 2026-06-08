# CHECKPOINT-SAVER

## Rule
Never hold more than 50 new pairs in memory without saving to disk.
Count every pair written. At 50: save immediately, reset counter.

## Save procedure
```python
# Append current batch to raw file
with open('datasets/tier1a/raw_sources/raw_pairs_batch_XXX.jsonl',
          'a', encoding='utf-8') as f:
    for pair in current_batch:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')
current_batch = []  # reset

# Confirm save
count = sum(1 for _ in open(
    'datasets/tier1a/raw_sources/raw_pairs_batch_XXX.jsonl',
    encoding='utf-8'))
print(f'Saved. Total in file: {count}')
```

## Context pressure rule
If context is above 70%:
1. Save whatever is in memory immediately
2. Update PROGRESS.md with current count
3. Run /compact
4. Continue from saved position

## Never do this
- Hold 100+ pairs in memory before saving
- Continue writing when context > 85%
- Trust that context compaction will preserve unsaved work

---

PASS CASE:
  Writes pairs 1-50, saves, continues. Context hits at pair 73.
  Pairs 1-50 are on disk. Loss: pairs 51-72 (22 pairs maximum).

FAIL CASE (what this prevents):
  Writes 150 pairs without saving. Context hits at pair 127.
  127 pairs lost. Happened with batch_002 during scraping phase.
