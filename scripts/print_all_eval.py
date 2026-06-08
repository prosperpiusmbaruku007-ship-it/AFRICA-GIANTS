import json

src = 'eval/accuracy_gate/eval_questions_001.jsonl'
out = 'eval_full_review.txt'

with open(src, encoding='utf-8') as f:
    questions = [json.loads(l) for l in f if l.strip()]

lines = []
for q in questions:
    lines.append(f"{q['id']} | {q['subdomain']} | {q['answer_type']}")
    lines.append(f"SW:  {q['question_sw']}")
    lines.append(f"ANS: {q['correct_answer_sw']}")
    lines.append("---")

text = '\n'.join(lines) + '\n'

with open(out, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Written {len(questions)} questions to {out}")
