#Read this file completely then execute every instruction below exactly as written.

TASK: Deep review of the accuracy gate evaluation system.
This is a research and analysis task — no training data
changes yet. Read everything, analyze everything, report
findings in detail.

============================================================
STEP 1 — Read all evaluation infrastructure files
============================================================

Read these files completely and report their full contents:

1. eval/accuracy_gate/eval_questions_001.jsonl
   — all 200 questions, note the structure of each

2. scripts/run_eval.py
   — the scoring logic, threshold checks, output format

3. Any other files in eval/ or scripts/ related to evaluation

For each file report:
- Full path
- Number of lines
- Key functions or structures
- Any hardcoded values that affect scoring

============================================================
STEP 2 — Analyze the 200 eval questions by subdomain
============================================================

For each of the 9 subdomains report:

| Subdomain | Count | Answer types used | Score in v3 gate |
|-----------|-------|-------------------|-----------------|

Answer types found in the questions:
- number
- yes_no  
- definition
- procedure
- penalty
- out_of_corpus_refusal

For each subdomain identify:
a) Which answer types are tested
b) Which answer types are NOT tested but exist in the corpus
c) Whether the question distribution matches the corpus distribution
d) Any questions that are testing the same fact multiple ways
   (duplicate coverage)
e) Any critical subdomain facts that have ZERO eval coverage

============================================================
STEP 3 — Analyze the scoring function in detail
============================================================

Look at score_question() in the eval script and for each
answer type report:

NUMBER scoring:
- What patterns does extract_numbers() detect
- What number formats does it MISS
  (Swahili words like "kumi", "ishirini", "thelathini"?)
- What happens if the correct answer has TZS 10,000,000
  but the model says "milioni kumi"?
- Does it handle percentage words like "asilimia kumi"?

YES_NO scoring:
- What Swahili yes words are checked
- What Swahili no words are checked
- Are there yes/no words missing from the lists
- What happens on ambiguous answers

DEFINITION scoring:
- Uses word overlap — minimum 3 words over 4 chars
- Is 3 words enough? Could a wrong answer pass this?
- Could a correct answer fail this?
- What if the model answers in English when question is Swahili?

PROCEDURE scoring:
- Same word overlap as definition
- Same weaknesses apply
- Are step-number words like "kwanza", "pili", "tatu" counted?

PENALTY scoring:
- Same as NUMBER — does it catch penalty amounts?
- Does it catch "miezi 6" for 6 months imprisonment?
- Does it catch "milioni kumi" for TZS 10 million?

OUT_OF_CORPUS_REFUSAL scoring:
- List every phrase in REFUSAL_PHRASES
- For each phrase: would Chike actually use this phrase?
- Run a check — look at the actual model outputs from the
  last gate run (gate_001_results.json if it exists) and
  find the 5 out_of_corpus questions that FAILED
- What did the model actually say for those 5?
- Do those responses contain any refusal signals that
  REFUSAL_PHRASES missed?

============================================================
STEP 4 — Cross-AI review of question quality
============================================================

For each subdomain pick the 3 hardest questions
(highest information density) and evaluate:

a) AMBIGUITY CHECK — could the question be interpreted
   differently by a human vs a model?

b) ANSWER COMPLETENESS CHECK — is the correct_answer_sw
   complete enough to score against, or is it so brief
   that a more complete correct answer would score as wrong?

c) LANGUAGE CONSISTENCY CHECK — are question and answer
   both in Swahili, both in English, or mixed?
   Mixed is fine but scoring must handle it.

d) FACT ACCURACY CHECK — cross-reference each hard question
   against known verified sources in CLAUDE.md
   Are any of the 200 questions testing WRONG facts?
   List any suspected fact errors.

e) SCORER BIAS CHECK — for each hard question manually
   trace through score_question() and determine if a
   correct model answer would actually score as PASS

============================================================
STEP 5 — GN487A specific deep dive
============================================================

GN487A scored 28/40 = 70% in both v2 and v3 gates.
Identical score across two different models means either:
a) The model genuinely cannot learn these facts, OR
b) The scorer is failing to detect correct answers

Do this analysis:

1. Look at gate_001_results.json (in /kaggle/working/ 
   or uploaded to HuggingFace adapter-v3 repo)
   Find all 12 GN487A questions that scored FAIL

2. For each failed question show:
   - The question text
   - The correct answer
   - What the model actually generated
   - Why the scorer marked it as FAIL
   - Whether the model answer was actually correct
     (human judgment)

3. Count: how many of the 12 failures were:
   - Model gave genuinely wrong answer
   - Model gave correct answer but scorer missed it
   - Model refused when it should have answered

4. Report: is the 70% GN487A score a MODEL problem
   or a SCORER problem?

============================================================
STEP 6 — OUT_OF_CORPUS deep dive
============================================================

Out of corpus scored 5/10 = 50% in both v2 and v3.
Same analysis as GN487A:

1. Find the 5 out_of_corpus questions that FAILED
2. For each show what the model actually said
3. Determine: did the model attempt an answer (bad)
   or did it refuse in a way REFUSAL_PHRASES missed?
4. Is 50% a MODEL problem or a SCORER problem?

============================================================
STEP 7 — Recommendations for eval_questions_002.jsonl
============================================================

Based on everything above produce a detailed report:

A) SCORING FIXES NEEDED (fix before next eval run):
   - List every fix needed in score_question()
   - List every addition needed to REFUSAL_PHRASES
   - List every addition needed to extract_numbers()
   - Estimate: if these fixes are applied to the existing
     v3 results, what would the corrected score be?

B) QUESTION DESIGN PRINCIPLES for batch_002 questions:
   For each subdomain list:
   - How many questions to add
   - Which answer types are underrepresented
   - Which specific facts need better coverage
   - What question formats produced the clearest scores
   - What question formats produced ambiguous scores

C) NEW SUBDOMAIN COVERAGE for eval_questions_002.jsonl:
   Current eval covers 9 subdomains. The corpus has more.
   List every subdomain in the training data that has
   ZERO eval coverage and propose 5-10 questions for each.

D) CROSS-AI REVIEW PROTOCOL:
   Write a detailed prompt that can be sent to Groq
   (llama-3.1-8b-instant) and Gemini to cross-review
   each new eval question before it is added.
   The prompt should check:
   - Fact accuracy against primary sources
   - Question clarity and unambiguity
   - Answer completeness
   - Scorer compatibility
   - Whether the question tests one fact or multiple

E) EVAL ARCHITECTURE RECOMMENDATION:
   Should the eval stay as a single 200-question file
   or split into:
   - Tier 1: Core facts (number, yes_no) — fast to run
   - Tier 2: Reasoning (definition, procedure) — slower
   - Tier 3: Edge cases (penalty, out_of_corpus) — hardest
   Argue both sides then make a recommendation.

============================================================
STEP 8 — Final deliverable
============================================================

Produce a single markdown report saved to:
eval/accuracy_gate/eval_review_001.md

Sections:
1. Executive summary (5 bullet points)
2. Scorer bugs found (with code fixes)
3. Question quality issues (with rewrites)
4. GN487A root cause (model vs scorer)
5. Out-of-corpus root cause (model vs scorer)
6. Corrected v3 score estimate
7. eval_questions_002.jsonl design specification
8. Cross-AI review protocol
9. Recommended eval architecture

After saving the report:
git add eval/accuracy_gate/eval_review_001.md
git commit -m "eval review: deep analysis of gate scoring, question quality, and v3 failure modes"
git push origin main
Show commit hash and paste the executive summary
section of the report then STOP.