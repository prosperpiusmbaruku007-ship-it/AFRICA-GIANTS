# READ THIS CLEARLY BEFORE DOING ANY TASK

# AFRICA GIANTS — AUTONOMOUS DATASET PIPELINE v2.0
# Last updated: 2026-06-23
# Status: PENDING EXECUTION

## MISSION
Automate dataset creation from source documents to HuggingFace upload.
Human role: add source documents + run training on Kaggle.
Everything between those two actions runs automatically.

## SCOPE (what this pipeline does)
1. Read PDF/HTML/text source documents placed in data/source_documents/
2. Extract compliance facts automatically
3. Generate Swahili Q&A pairs automatically
4. Review pairs with pure Python deterministic checks (no API)
5. Upload approved pairs to HuggingFace dataset
6. RAG grounding in Cerebrium using locked_facts.json

## OUT OF SCOPE (not built now)
- Web scraping of government sites
- GitHub Actions automation
- Supabase / Railway / Tier 1B
- Outbound WhatsApp reminders
- Model training (human runs Kaggle manually)
- Accuracy gate (human runs eval notebook manually)

---

## PHASE 1 — FIX FOUNDATIONS
Goal: Clean up all audit findings blocking the pipeline.
Prerequisite: None.
Time estimate: Half a day.

### Files to fix:
1. config/huggingface.yaml
   CHANGE: adapter_repo → prospAprospA007/africa-giants-adapter-v8
   CHANGE: dataset_repo → prospAprospA007/africa-giants-dataset

2. config/models.yaml
   CHANGE: lora.r → 128
   CHANGE: lora.alpha → 128

3. scripts/run_eval.py
   CHANGE: remove hardcoded ADAPTER_REPO = "...adapter-v3"
   CHANGE: replace with: ADAPTER_REPO = os.environ.get("ADAPTER_REPO", "prospAprospA007/africa-giants-adapter-v8")

4. requirements.txt
   ADD: pdfplumber>=0.11
   ADD: sentence-transformers>=2.7
   ADD: numpy>=1.26
   (all three needed by Phase 3 — pdfplumber for PDF extraction,
   sentence-transformers + numpy for semantic deduplication in question_generator)

5. run.py
   REWRITE with these commands only:

   generate
     → runs Phase 3 pipeline on data/source_documents/
     → processes all new files not yet in data/raw/processed_files.json

   generate --reprocess {filename}
     → removes {filename} from data/raw/processed_files.json before scanning
     → forces re-processing of a document previously skipped
     → use case: document with all-new facts — approve facts first via approve-facts,
       then: python run.py generate --reprocess vat_guide_2025.pdf

   build-rag
     → runs Phase 2 RAG index rebuild (re-embeds locked_facts.json)

   upload
     → runs Phase 4 HuggingFace upload (rebuilds SFT first, then uploads)

   review
     → shows pending pairs in data/flagged/ for inspection
     → lists batch files with flagged pair counts

   status
     → shows current pipeline state and pair counts

   approve-facts
     → opens data/flagged/new_facts_pending.json for human approval
     → human approves/rejects each new fact candidate
     → approved facts written to scripts/locked_facts.json
     → auto git-commits: git add scripts/locked_facts.json && git commit
       with message: "locked_facts: approved N facts from {source} on {date}"
     → git commit wrapped in try/except — on failure prints manual command

   approve-flags --batch NNN
     → UX for reviewing flagged pairs one-by-one:
       - Print: [pair_index/total] e.g. [1/23]
       - Print: INSTRUCTION: {instruction field}
       - Print: OUTPUT: {output field}
       - Print: FAILED CHECKS: {which checks failed and exact reason}
       - Prompt: [a]pprove  [r]eject  [s]kip  [q]uit:
       - Single keypress accepted (no Enter required)
       - [a]: move pair to data/reviewed/batch_NNN_approved.jsonl
       - [r]: mark as rejected in progress file, skip permanently
       - [s]: skip for now, revisit next session
       - [q]: save progress to data/flagged/batch_NNN_progress.json and exit
       - Resumable: next run with --batch NNN starts where [q] left off
       - --auto-approve-all flag for testing only (approves all without prompting)
     → without this command flagged pairs are permanently lost

6. Create directories:
   data/source_documents/   ← human drops PDFs/HTML/TXT here
   data/raw/extracted/      ← pdf_extractor output (always written)
   data/raw/generated/      ← question_generator output (always written)
   data/raw/reviewed/       ← pair_reviewer scores (always written)
   data/reviewed/           ← approved pairs from approve-flags
   data/flagged/            ← pairs needing human inspection
   data/cost_log.jsonl      ← API cost tracking (touch empty file)

7. Delete: datasets/tier1a/processed/ (stale, misleading)

8. Do NOT touch: src/ directory (dead code, leave as-is)
   Do NOT touch: chike-inference/ (Phase 2 handles this separately)
   Do NOT touch: wappfly-function/ (out of scope)
   Do NOT touch: kaggle/ notebooks (human runs these manually)

### pdf_extractor.py must support three input formats:
- .pdf  → pdfplumber
- .html → BeautifulSoup(content, 'lxml').get_text() with content heuristic (see Phase 3)
- .txt  → plain file read
BeautifulSoup and lxml are already in requirements.txt.

### Commit message:
"fix: Phase 1 foundations — configs updated, directories created, run.py rewritten"

### Done when:
- python run.py status runs without errors
- All 6 directories exist
- configs point to correct versions
- run.py shows help text for all 8 commands

---

## PHASE 2 — RAG IN CEREBRIUM
Goal: Inject relevant locked facts into every Cerebrium inference call.
Reduces hallucination without retraining.
Prerequisite: Phase 1 complete.
Time estimate: One day including deploy and test cycle.

### What to build:
Modify chike-inference/main.py ONLY.
Add these capabilities in this order:

#### 2a — Environment and paths (add before any imports)
```python
# Must be set before importing sentence_transformers
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/persistent-storage/.cache/sentence_transformers'

FACTS_PATH      = 'locked_facts.json'
EMBEDDINGS_PATH = '/persistent-storage/rag_embeddings.npy'
FACTS_TEXT_PATH = '/persistent-storage/rag_facts_text.json'
HASH_PATH       = '/persistent-storage/locked_facts_hash.txt'
EMBED_MODEL     = 'paraphrase-multilingual-MiniLM-L12-v2'
```

#### 2b — Persistent embedding cache (no FAISS — numpy only)
On container startup:
1. Compute MD5 hash of locked_facts.json
2. If EMBEDDINGS_PATH exists AND FACTS_TEXT_PATH exists AND stored hash matches current hash:
   → load embeddings from EMBEDDINGS_PATH (np.load)
   → load fact texts from FACTS_TEXT_PATH (json.load)
   → log "[rag] index loaded from cache — N facts"
3. Else:
   → from sentence_transformers import SentenceTransformer
   → model = SentenceTransformer(EMBED_MODEL)
   → embed all fact strings from locked_facts.json
   → save embeddings: np.save(EMBEDDINGS_PATH, fact_embeddings)
   → save texts: json.dump(fact_texts, open(FACTS_TEXT_PATH, 'w'))
   → save hash to HASH_PATH
   → log "[rag] embeddings rebuilt — N facts embedded"

Both SENTENCE_TRANSFORMERS_HOME and EMBEDDINGS_PATH are on /persistent-storage.
This means: sentence-transformers model downloads once (420MB), embeddings computed once.
Cold starts after scale-to-zero load from disk — no re-download, no re-embedding.

#### 2c — Retrieval function (pure numpy — no FAISS)
```python
def retrieve_facts(question: str, top_k: int = 3) -> list[str]:
    q_emb = embed_model.encode([question])[0]
    scores = np.dot(fact_embeddings, q_emb.T).flatten()
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [fact_texts[i] for i in top_indices]
```

#### 2d — Enriched system prompt
In the run() function, before model.generate():
```python
relevant_facts = retrieve_facts(message)
facts_block = "\n".join(f"- {f}" for f in relevant_facts)
enriched_system = (
    BASE_SYSTEM_PROMPT
    + "\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n"
    + facts_block
    + "\n\nTumia ukweli huu. Usibuni takwimu ambazo hazipo hapa."
)
```

#### 2e — Dependencies
Add to chike-inference/cerebrium.toml under [cerebrium.dependencies.pip]:
- sentence-transformers
- numpy

Do NOT add faiss-cpu. Numpy cosine similarity is sufficient for ~100 facts and
removes a 100MB C++ binary dependency from the container.

NOT to requirements.txt — Cerebrium reads only cerebrium.toml.

### Test before deploying:
Run 3 hard questions via live endpoint after deploy:
Q1: "Ninaajiri wafanyakazi 15, SDL na WCF ni tofauti gani?"
Q2: "NSSF inalipwa tarehe gani hasa?"
Q3: "Raia wa Tanzania anaweza kufanya biashara ya rejareja chini ya GN 487A?"

### Done when (empirical, not assumed):
For each of Q1, Q2, Q3:
- Log the exact response text
- Log the retrieved facts that were injected
- Record: FIXED / STILL WRONG / PARTIALLY CORRECT
- If Q1 still confuses SDL with WCF: RAG injection is insufficient — batch_014 correction
  pairs are required regardless of Phase 2
- If Q2 still says "wiki moja" or "tarehe 7": same — batch_014 required
- If Q3 still says GN487A applies to Tanzanians: same — batch_014 required

Phase 2 is complete when deployed and tested. Whether RAG fixes the answers or not
is the test result, not the pass/fail gate. Both outcomes are valid information.
Batch_014 correction pairs are required in parallel regardless — do not defer them
pending Phase 2 results.

### Commit message:
"feat: Phase 2 RAG — locked_facts injected at inference, persistent numpy embeddings"

---

## PHASE 3 — AUTOMATED Q&A PIPELINE
Goal: Convert source documents to reviewed Swahili Q&A pairs automatically.
No human writes any pair.
No external API for review — pure Python deterministic checks only.
Prerequisite: Phase 1 complete.
Time estimate: Two days.

### Architecture: single in-memory pipeline with always-on intermediate files
All steps run as functions called by qa_factory.py.
Intermediate files always written to data/raw/ for auditability — no debug flag needed.
src/synthetic/ files are function modules, not standalone scripts.
Single final output per run: datasets/tier1a/cleaned_pairs/cleaned_pairs_batch_NNN.jsonl

### Input:
data/source_documents/{category}/{filename}.pdf or .html or .txt
Categories: tra, brela, osha, nssf, wcf, labour, immigration, general
Human drops files here, then runs: python run.py generate
Pipeline detects new files when python run.py generate is run.
Human drops files then runs the command — there is no background file watcher.
Processed files tracked in data/raw/processed_files.json.

### Output:
datasets/tier1a/cleaned_pairs/cleaned_pairs_batch_NNN.jsonl
One new batch file per pipeline run.
Intermediate files (reference only, not pipeline inputs):
  data/raw/extracted/{category}/{filename_md5}.json
  data/raw/generated/batch_{NNN}.jsonl
  data/raw/reviewed/batch_{NNN}_results.json
Format: same Alpaca schema as all existing batches.

### Files to create:

---

#### src/synthetic/api_utils.py (NEW — shared utilities)

Purpose: Shared API utilities imported by fact_extractor and question_generator.

```python
RETRY_ON = {
    'RateLimitError', 'APIConnectionError', 'APITimeoutError',
    'ConnectError', 'TimeoutError', 'ConnectionError'
}
RAISE_ON = {
    'AuthenticationError', 'PermissionDeniedError',
    'InvalidRequestError', 'NotFoundError'
}

def call_api_with_retry(client, **kwargs):
    for attempt in range(3):
        try:
            return client.messages.create(**kwargs)
        except Exception as e:
            err_type = type(e).__name__
            # Known non-retryable errors: raise immediately
            if err_type in RAISE_ON:
                raise
            # Last attempt: raise regardless
            if attempt == 2:
                raise
            # Known retryable errors OR names containing recognised patterns
            if err_type in RETRY_ON or 'error' in err_type.lower():
                wait = 60 * (2 ** attempt)  # 60s, 120s
                print(f"[api] {err_type} — retrying in {wait}s ({attempt+2}/3)")
                time.sleep(wait)
            else:
                raise  # unknown error type — do not retry silently
```

Note: RAISE_ON is checked BEFORE the 'error' in name fallback, so AuthenticationError
and similar are always raised immediately regardless of name substring matching.

Cost logging (always-on, try/finally to capture cost even on downstream failure):
```python
COST_PER_INPUT_TOKEN  = 0.000003   # claude-sonnet-4-6: $3/M input
COST_PER_OUTPUT_TOKEN = 0.000015   # claude-sonnet-4-6: $15/M output

def call_with_cost_tracking(client, script_name, **kwargs):
    response = None
    try:
        response = call_api_with_retry(client, **kwargs)
        return response
    finally:
        if response is not None:
            cost = (response.usage.input_tokens  * COST_PER_INPUT_TOKEN +
                    response.usage.output_tokens * COST_PER_OUTPUT_TOKEN)
            log_cost(script_name,
                     response.usage.input_tokens,
                     response.usage.output_tokens,
                     cost)

def log_cost(script_name, tokens_in, tokens_out, cost_usd):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script": script_name,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost_usd, 6)
    }
    with open('data/cost_log.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')
```

Note: cost cap is best-effort, not a guarantee — actual Anthropic billing is authoritative.
Check Anthropic console for actual spend. Token prices hardcoded as constants (update if
Anthropic changes pricing).

---

#### src/synthetic/pdf_extractor.py — extract_document(path) → dict

Purpose: Extract structured text from a source document.

Input: file path from data/source_documents/
Returns: document dict (ALWAYS written to data/raw/extracted/{category}/{md5}.json)

```json
{
  "source_file": "filename.pdf",
  "source_category": "tra",
  "source_url": "tra.go.tz",
  "source_document": "data/source_documents/tra/vat_guide_2025.pdf",
  "source_md5": "abc123def456",
  "extracted_at": "2026-06-23T10:00:00Z",
  "sections": [
    {
      "heading": "VAT Registration",
      "content": "extracted text"
    }
  ]
}
```

Format handling:
```python
if path.endswith('.pdf'):
    with pdfplumber.open(path) as pdf:
        sections = [{'heading': f'Page {i+1}', 'content': p.extract_text() or ''}
                    for i, p in enumerate(pdf.pages)]
        total_chars = sum(len(s['content']) for s in sections)
        num_pages = len(pdf.pages)
        if total_chars < 100 * num_pages:
            raise ValueError(
                f"PDF appears to be image-only ({total_chars} chars from {num_pages} pages). "
                f"Convert to text-layer PDF or save as .txt first."
            )
elif path.endswith('.html'):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'lxml')
    # Content heuristic — prefer semantic elements over full-page dump
    content_el = (
        soup.find('article') or
        soup.find('main') or
        soup.find(id='content') or
        soup.find(class_='content') or
        soup.find(class_='article-body') or
        soup
    )
    text = content_el.get_text(separator='\n', strip=True)
    sections = [{'heading': 'Main Content', 'content': text}]
elif path.endswith('.txt'):
    sections = [{'heading': 'Full Text', 'content': open(path, encoding='utf-8').read()}]
else:
    raise ValueError(f"Unsupported format: {path}. Supported: .pdf .html .txt")
```

SOURCE_URL_MAP (used to set source_url from category):
```python
SOURCE_URL_MAP = {
    "tra":         "tra.go.tz",
    "brela":       "brela.go.tz",
    "osha":        "osha.go.tz",
    "nssf":        "nssf.or.tz",
    "wcf":         "wcf.go.tz",
    "labour":      "labour.go.tz",
    "immigration": "immigration.go.tz",
    "general":     "tanzlii.org",
}
```

---

#### src/synthetic/fact_extractor.py — extract_facts(document) → list[dict]

Purpose: Extract compliance facts from document using Claude API.
Uses call_with_cost_tracking() from api_utils.py — NOT call_api_with_retry directly.
Imports: from src.synthetic.api_utils import call_with_cost_tracking, COST_PER_INPUT_TOKEN

Input: document dict from extract_document()
Returns: list of confirmed facts (already in locked_facts.json)
Side effect: writes new candidates to data/flagged/new_facts_pending.json

EXTRACTION PROMPT (sent to claude-sonnet-4-6):

```
System:
You are a compliance fact extractor for Tanzania business law.
Extract only numerical facts, deadlines, rates, thresholds, and penalties.
Respond ONLY with a JSON array. No preamble, no explanation, no markdown.

User:
Extract all compliance facts from this document section.
Output format (JSON array only):
[
  {
    "fact_key": "snake_case identifier",
    "value": "exact value as stated",
    "unit": "% or TZS or days or employees or null",
    "source_section": "section heading where found",
    "effective_date": "YYYY-MM-DD or null"
  }
]

Example input: "SDL rate is 3.5% of gross payroll, payable by the 7th"
Example output:
[
  {"fact_key": "sdl_rate", "value": "3.5", "unit": "%",
   "source_section": "SDL Overview", "effective_date": null},
  {"fact_key": "sdl_deadline", "value": "7", "unit": "days_of_month",
   "source_section": "SDL Overview", "effective_date": null}
]

Document section to extract from:
{section_content}
```

LOCKED FACTS COMPARISON ALGORITHM:
```python
def extract_number_unit_pairs(text: str) -> set:
    pattern = r'(\d[\d,\.]*)\s*(%|TZS|milioni|asilimia|M\b|days?|employees?)'
    return set(re.findall(pattern, str(text), re.IGNORECASE))

def is_confirmed_fact(extracted: dict, locked_facts: dict) -> tuple[bool, str | None]:
    """
    Returns (True, matching_key) if extracted fact matches a locked fact.
    Returns (False, None) if fact is a new candidate.
    
    Algorithm: compare (number, unit) pairs extracted from the value field.
    Non-numerical facts (procedures, GN names, categories) always return (False, None)
    and become new candidates for human review — this is intentional and correct.
    Non-numerical facts in the source are almost always already captured in the system
    prompt and pair schema constraints, not in locked_facts.json.
    """
    extracted_pairs = extract_number_unit_pairs(extracted.get('value', ''))
    if not extracted_pairs:
        return False, None  # non-numerical — send to human review queue
    
    for key, fact in locked_facts.items():
        locked_pairs = extract_number_unit_pairs(str(fact))
        if extracted_pairs and extracted_pairs == locked_pairs:
            return True, key
    
    return False, None
```

IMPORTANT — non-blocking locked_facts flow:
- Facts confirmed by is_confirmed_fact() → returned immediately for use in generation
- New fact candidates (not confirmed) → appended to data/flagged/new_facts_pending.json
- Generation proceeds with confirmed facts ONLY — does NOT wait for human approval
- If a document's facts are ALL new candidates: zero pairs generated, log warning,
  instruct human to: run approve-facts, then: python run.py generate --reprocess {filename}
- NEVER auto-update locked_facts.json — human approval required via: python run.py approve-facts

After approve-facts writes to locked_facts.json:
```python
try:
    subprocess.run(
        ['git', 'add', 'scripts/locked_facts.json'],
        check=True
    )
    subprocess.run(
        ['git', 'commit', '-m',
         f'locked_facts: approved {n} facts from {source} on {date}'],
        check=True
    )
except subprocess.CalledProcessError as e:
    print(f"[approve-facts] Warning: git commit failed ({e}).")
    print(f"Run manually: git add scripts/locked_facts.json && git commit")
```

COST CAP CHECK (fires BEFORE processing each document — never mid-document):
```python
MONTHLY_CAP = float(os.environ.get('MONTHLY_BUDGET', '20.0'))
COST_PER_DOCUMENT_BUDGET = float(os.environ.get('COST_PER_DOCUMENT_BUDGET', '0.20'))
# ^ override via environment variable for long documents:
# COST_PER_DOCUMENT_BUDGET=2.00 python run.py generate
# Or skip gate entirely: --no-budget-check flag

def check_budget_before_document():
    current_cost = sum_cost_log_this_month()
    if current_cost + COST_PER_DOCUMENT_BUDGET > MONTHLY_CAP:
        remaining_docs = count_unprocessed_documents()
        print(f"[cost] Monthly cap {MONTHLY_CAP} USD approaching.")
        print(f"[cost] Used: {current_cost:.2f} | Buffer: {COST_PER_DOCUMENT_BUDGET:.2f}")
        print(f"[cost] {remaining_docs} documents unprocessed.")
        print(f"[cost] To continue: COST_PER_DOCUMENT_BUDGET=2.00 python run.py generate")
        print(f"[cost] Or: python run.py generate --no-budget-check")
        return False
    return True
```

Note: COST_PER_DOCUMENT_BUDGET=0.20 is calibrated for advisory documents (2-10 pages).
Long government Acts (50+ pages) may cost up to $2.00. Pre-split large documents into
sections before dropping into source_documents/, or override the budget variable.
The cap is best-effort — Anthropic console is the authoritative cost record.

---

#### src/synthetic/question_generator.py — generate_pairs(facts, document) → list[dict]

Purpose: Generate Swahili Q&A pairs from confirmed facts.
Uses call_with_cost_tracking() from api_utils.py.
Imports: from src.synthetic.api_utils import call_with_cost_tracking

Input: confirmed facts list + document dict
Returns: list of pair dicts (always written to data/raw/generated/batch_{NNN}.jsonl)

Rules:
- 3-5 questions per fact
- Question type distribution: 30% yes_no, 25% number, 20% definition, 15% procedure, 10% penalty
- Each pair includes source_document field for audit trail
- Deduplication check BEFORE including a pair (see below)

GENERATION PROMPT (sent to claude-sonnet-4-6):

```
System:
You are a Swahili compliance question generator for Chike,
a Tanzanian business adviser. Generate natural conversational questions
a small business owner would ask via WhatsApp — not formal exam questions.
Use everyday Swahili mixed with necessary technical terms (VAT, SDL, PAYE).
Respond ONLY with a JSON array. No preamble, no explanation.

User:
Generate {n} compliance questions from this fact.
Fact: {fact_key}: {value} {unit} — source: {source_section}

Question type distribution (follow exactly):
- yes_no: 30% (questions answered with Ndiyo/Hapana)
- number: 25% (questions asking for specific figures)
- definition: 20% (questions asking what something is)
- procedure: 15% (questions asking how to do something)
- penalty: 10% (questions asking about consequences)

Output format (JSON array only):
[
  {
    "instruction": "question in natural conversational Swahili",
    "input": "",
    "output": "direct answer in Swahili citing source domain",
    "system": "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba halijui na mwelekeze kwa mtaalamu.",
    "subdomain": "one of 11 canonical subdomains",
    "answer_type": "yes_no|number|definition|procedure|penalty|out_of_corpus_refusal",
    "source_url": "canonical .go.tz domain from SOURCE_URL_MAP",
    "source_name": "TRA Official|BRELA Official|OSHA Official|etc",
    "generated_date": "YYYY-MM-DD",
    "source_document": "relative path of input file"
  }
]

Example input fact:
fact_key: sdl_rate, value: 3.5, unit: %, source_section: SDL Overview

Example output:
[
  {
    "instruction": "Ninaajiri wafanyakazi 20 — SDL inanigharimu kiasi gani kwa mwezi?",
    "input": "",
    "output": "SDL ni asilimia 3.5 ya jumla ya mishahara yote — mwajiri peke yake ndiye analipa, si mfanyakazi. Kwa mishahara ya jumla TZS 1,000,000 unalipa TZS 35,000. Thibitisha na TRA (tra.go.tz).",
    "system": "Jina lako ni Chike...",
    "subdomain": "sdl_compliance",
    "answer_type": "number",
    "source_url": "https://tra.go.tz",
    "source_name": "TRA Official",
    "generated_date": "2026-06-22",
    "source_document": "data/source_documents/tra/sdl_guide_2025.pdf"
  },
  {
    "instruction": "Je, mfanyakazi analipa sehemu ya SDL?",
    "input": "",
    "output": "Hapana. SDL inalipwa na MWAJIRI peke yake — mfanyakazi halipi chochote. Hii ni tofauti na NSSF ambayo inalipwa na wote wawili. Thibitisha na TRA (tra.go.tz).",
    "system": "Jina lako ni Chike...",
    "subdomain": "sdl_compliance",
    "answer_type": "yes_no",
    "source_url": "https://tra.go.tz",
    "source_name": "TRA Official",
    "generated_date": "2026-06-22",
    "source_document": "data/source_documents/tra/sdl_guide_2025.pdf"
  }
]
```

LLM response repair (handle malformed JSON from Claude):
```python
def parse_llm_response(raw: str) -> list[dict]:
    # Attempt 1: direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Attempt 2: strip markdown fences
    try:
        stripped = raw.split('```json')[-1].split('```')[0].strip()
        return json.loads(stripped)
    except (json.JSONDecodeError, IndexError):
        pass
    # Attempt 3: find first [...] block
    try:
        start = raw.index('[')
        end = raw.rindex(']') + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    # All failed
    print(f"[generator] Failed to parse LLM response. Skipping. Raw: {raw[:200]}")
    return []
```

SEMANTIC DEDUPLICATION:
Pre-compute embedding index of all existing instructions once per run.
Requires: sentence-transformers installed locally (add to requirements.txt — same
model as Phase 2: paraphrase-multilingual-MiniLM-L12-v2).

```python
# Build once per generate run, cache to data/raw/instruction_index.npy
# Rebuild trigger: MD5 of all cleaned_pairs/ files (stored in data/raw/instruction_index_hash.txt)
# If hash unchanged: load from disk (fast). If changed: re-embed all instructions.

def get_instruction_index(cleaned_pairs_dir):
    current_hash = md5_of_directory(cleaned_pairs_dir)
    cached_hash_path = 'data/raw/instruction_index_hash.txt'
    index_path = 'data/raw/instruction_index.npy'
    texts_path = 'data/raw/instruction_index_texts.json'
    
    if (os.path.exists(index_path) and os.path.exists(cached_hash_path)
            and open(cached_hash_path).read() == current_hash):
        embeddings = np.load(index_path)
        texts = json.load(open(texts_path))
        return embeddings, texts
    
    # Rebuild
    all_instructions = load_all_instructions(cleaned_pairs_dir)
    embeddings = embed_model.encode(all_instructions)
    np.save(index_path, embeddings)
    json.dump(all_instructions, open(texts_path, 'w'))
    open(cached_hash_path, 'w').write(current_hash)
    return embeddings, all_instructions

def is_semantic_duplicate(new_instruction, index_embeddings, index_texts, threshold=0.92):
    if len(index_texts) == 0:
        return False
    q_emb = embed_model.encode([new_instruction])[0]
    scores = np.dot(index_embeddings, q_emb.T).flatten()
    if scores.max() > threshold:
        return True
    return False
```

Note: sentence-transformers must be added to requirements.txt for local use.
The same model (paraphrase-multilingual-MiniLM-L12-v2) is used in Phase 2 on
Cerebrium and Phase 3 locally. First local run downloads the model (~420MB).

Generated pair schema (STRICT — enforced):
```json
{
  "instruction": "question in natural conversational Swahili",
  "input": "",
  "output": "answer in Swahili — direct, cites source",
  "system": "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba halijui na mwelekeze kwa mtaalamu.",
  "subdomain": "one of: vat_registration|paye|sdl_compliance|gn487a|brela_registration|nssf_contributions|osha_registration|efd_compliance|vat_withholding|out_of_corpus|wcf_compliance",
  "answer_type": "one of: yes_no|number|definition|procedure|penalty|out_of_corpus_refusal",
  "source_url": "canonical URL from SOURCE_URL_MAP (e.g. tra.go.tz)",
  "source_name": "TRA Official|BRELA Official|OSHA Official|etc",
  "source_document": "data/source_documents/tra/vat_guide_2025.pdf",
  "generated_date": "YYYY-MM-DD"
}
```

NOTE: source_document is metadata only. generate_sft.py's fmt_pair() must exclude it.
Phase 4 asserts this explicitly before upload.

---

#### src/synthetic/pair_reviewer.py — review_pairs(pairs) → tuple[approved, flagged, rejected]

Purpose: Deterministic quality check on generated pairs. NO API. NO LLM.

Input: list of pair dicts from generate_pairs()
Returns: (approved_list, flagged_list, rejected_list)
Output always written to: data/raw/reviewed/batch_{NNN}_results.json

THE 6 CHECKS (pure Python — deterministic):

CHECK 1 — Numerical accuracy (locked_facts compliance):
  Extract all numbers from output field (regex: \d[\d,\.]*\s*(%|TZS|milioni|asilimia))
  For each number found: check if it appears in any locked_facts.json value
  If number not in locked_facts AND not in source document content: FAIL

CHECK 2 — Schema completeness:
  Required fields present: instruction, input, output, system, subdomain, answer_type
  instruction length: 10-200 characters
  output length: 20-500 characters
  subdomain in allowed list (11 values above)
  answer_type in allowed list (6 values above)
  If any field missing or out of range: FAIL

CHECK 3 — Refusal discipline:
  If answer_type == out_of_corpus_refusal:
    Count sentences in output (split on . ! ?)
    If sentence count > 2: FAIL
    If output contains domain-specific regulatory content after refusal phrase: FAIL

CHECK 4 — Source citation:
  output must contain at least one .go.tz domain:
  [tra.go.tz, brela.go.tz, osha.go.tz, nssf.or.tz, wcf.go.tz,
   immigration.go.tz, labour.go.tz, ppra.go.tz, tanzlii.org]
  "Thibitisha" and "thibitisha" are NOT valid — they are refusal phrases, not citations.
  If no .go.tz domain found: FAIL

CHECK 5 — Output completeness:
  output must end with . or ! or ? (not truncated mid-sentence)
  output must not contain: [TODO, PLACEHOLDER, INSERT, ...]
  output word count must be >= 15
  If any condition fails: FAIL

CHECK 6 — Hallucination guard:
  GN numbers: extract all (regex: GN\s*\d+[A-Z]*)
  Valid GN numbers: [GN487A, GN605A]
  If any other GN number found: FAIL

  Percentages: extract all (regex: \d+\.?\d*\s*%)
  Valid percentages (from locked_facts):
  [0%, 3%, 3.5%, 6%, 8%, 10%, 15%, 16%, 18%, 20%, 25%, 30%, 33.4%]
  Key: 15% = non-resident PAYE flat rate; 3% = VAT withholding goods;
       6% = VAT withholding services; 33.4% = GN605A average wage increase
  If percentage not in valid list: FAIL

SCORING:
  0 checks failed → APPROVED
  1-2 checks failed → FLAGGED (human spot-check via: python run.py approve-flags --batch NNN)
  3+ checks failed → REJECTED (logged, source may need re-examination)

---

#### src/synthetic/dataset_builder.py — build_dataset(approved_pairs, batch_num) → str

Purpose: Write approved pairs to cleaned_pairs/ directory.
Does NOT call generate_sft.py — SFT rebuild deferred to python run.py upload.

Input: list of approved pair dicts + batch number
Returns: path to new batch file

Batch numbering (robust against gaps and non-sequential names):
```python
import re
existing = os.listdir('datasets/tier1a/cleaned_pairs/')
numbers = [int(m.group(1)) for f in existing
           if (m := re.search(r'batch_(\d+)', f))]
next_batch = max(numbers, default=0) + 1
filename = f'cleaned_pairs_batch_{next_batch:03d}.jsonl'
```

Steps:
1. Determine next batch number using regex scan above
2. Write approved pairs to datasets/tier1a/cleaned_pairs/{filename}
3. Verify file written: assert file exists and line count == len(approved_pairs)
4. Print: "batch_{NNN}: N pairs written to cleaned_pairs/"
5. Print: "Run 'python run.py upload' to rebuild SFT files and push to HuggingFace"
6. Do NOT call generate_sft.py here. Do NOT upload automatically.

---

#### src/synthetic/qa_factory.py — main orchestrator

Triggered by: python run.py generate [--reprocess {filename}] [--no-budget-check]

Flow:
1. FIRST: Check for new files
```python
new_files = [f for f in scan_source_documents()
             if not already_processed(f)]
if not new_files:
    print("No new files found in data/source_documents/")
    print("Add .pdf/.html/.txt files and re-run.")
    print("Supported categories: tra/ brela/ osha/ nssf/ wcf/ labour/ immigration/ general/")
    return
```

2. Load data/raw/processed_files.json
   Schema: {"relative/path/to/file.pdf": {"md5": "abc123", "processed_at": "2026-06-23"}}
   If --reprocess {filename}: remove that entry from processed_files before step 1

3. MD5-based change detection:
```python
import hashlib

def file_md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()

def already_processed(path):
    entry = processed_files.get(str(path))
    if entry is None:
        return False
    return entry.get('md5') == file_md5(path)
    # If MD5 changed: file was updated — re-process
```

4. Build semantic dedup index once (before document loop):
   instruction_embeddings, instruction_texts = get_instruction_index('datasets/tier1a/cleaned_pairs/')

5. For each new file (check budget BEFORE starting each):
   a. if not check_budget_before_document() and not --no-budget-check: break
   b. doc = extract_document(path)           — writes data/raw/extracted/{cat}/{md5}.json
   c. facts = extract_facts(doc)             — writes candidates to data/flagged/ if new
   d. if not facts: log warning, update processed_files, continue to next file
   e. pairs = generate_pairs(facts, doc)     — writes data/raw/generated/batch_N.jsonl
   f. approved, flagged, rejected = review_pairs(pairs)
                                             — writes data/raw/reviewed/batch_N_results.json
   g. if approved: build_dataset(approved, next_batch_num())
   h. if flagged: write data/flagged/batch_NNN_flagged.jsonl
   i. update processed_files.json with {path: {"md5": file_md5(path), "processed_at": date}}

6. Print final report:
   - Files processed: N
   - Facts confirmed: N (from locked_facts) | N new candidates in data/flagged/new_facts_pending.json
   - Pairs generated: N
   - Pairs approved: N → cleaned_pairs_batch_NNN.jsonl
   - Pairs flagged: N → run 'python run.py approve-flags --batch NNN' to review
   - Pairs rejected: N (see data/raw/reviewed/ for details)
   - Run 'python run.py upload' to push to HuggingFace

### Commit message:
"feat: Phase 3 autonomous Q&A pipeline — PDF/HTML/TXT to reviewed dataset"

### Done when:
- python run.py generate processes one test PDF and produces approved pairs
- Pairs pass all 6 checks
- cleaned_pairs_batch_014.jsonl created with correct schema
- source_document field present in output JSONL
- No manual pair writing required

---

## PHASE 4 — HUGGINGFACE UPLOAD
Goal: Push updated dataset to HuggingFace with one command.
Prerequisite: Phase 3 complete.
Time estimate: Half a day.

### What to build:
Modify scripts/hf_clean_upload.py OR create scripts/upload_dataset.py

Command: python run.py upload

Steps:
1. Run scripts/generate_sft.py to rebuild train_sft.jsonl + val_sft.jsonl from ALL
   cleaned_pairs (this is the only place generate_sft.py is called in the pipeline)

2. Assert SFT output is clean — source_document must not appear in training data:
```python
with open('datasets/tier1a/sft/train_sft.jsonl') as f:
    sft_pairs = [json.loads(l) for l in f if l.strip()]
assert all(
    set(p.keys()) == {'instruction', 'input', 'output', 'system'}
    for p in sft_pairs
), "SFT pairs contain unexpected fields — check generate_sft.py fmt_pair()"
print(f"[upload] SFT assertion passed — {len(sft_pairs)} pairs, 4 fields each")
```

3. Verify schema of train_sft.jsonl (all pairs have required fields)

4. Upload train_sft.jsonl to prospAprospA007/africa-giants-dataset

5. Upload val_sft.jsonl to prospAprospA007/africa-giants-dataset

6. Update README.md on HuggingFace dataset repo with new pair count

7. Print confirmation: "Dataset uploaded. train=N val=N. Ready for Kaggle training."

Requires: HF_TOKEN environment variable

### Commit message:
"feat: Phase 4 one-command HuggingFace upload"

### Done when:
- python run.py upload pushes dataset to HuggingFace successfully
- HuggingFace dataset repo shows correct pair count
- SFT assertion passes (4-key schema confirmed)

---

## EXECUTION ORDER
Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 1 unblocks everything. Phase 2 has immediate production value (better
inference) and can be built in parallel with Phase 3 once Phase 1 is done.
Phase 3 is the core value. Phase 4 completes the loop.

---

## HUMAN WORKFLOW AFTER ALL PHASES COMPLETE
1. Download PDF/HTML/TXT from TRA/BRELA/PKF/VELMA → drop in data/source_documents/tra/ (or relevant category)
   Note: .html files must be saved from browser as complete HTML files.
   Note: scanned PDFs must be converted to text-layer first.
2. Run: python run.py generate
3. Run: python run.py review (inspect what flagged pairs exist)
4. Run: python run.py approve-flags --batch NNN (promote or discard flagged pairs)
5. Run: python run.py approve-facts (approve any new locked facts, auto git-commits)
6. If step 5 approved new facts and some documents had zero pairs:
   Run: python run.py generate --reprocess {filename}
7. Run: python run.py upload
8. Go to Kaggle → run africa_giants_V2.ipynb manually
9. Run eval notebook manually
10. If gate passes: cerebrium deploy from chike-inference/

---

## ENVIRONMENT VARIABLES REQUIRED
HF_TOKEN                  - HuggingFace token (existing)
ANTHROPIC_API_KEY         - For fact_extractor and question_generator only
CEREBRIUM_API_KEY         - For deployment (existing)
MONTHLY_BUDGET            - Optional. Override $20 monthly cap (e.g. MONTHLY_BUDGET=50)
COST_PER_DOCUMENT_BUDGET  - Optional. Override $0.20 per-doc budget gate

## COSTS
Anthropic API calls: fact_extractor + question_generator only
Estimated cost per source document: $0.05-0.20 for advisory (2-10 pages)
                                    up to $2.00 for long Acts (50+ pages)
Monthly cap: $20 default (enforced in code — stops cleanly before a document that
             would exceed cap; override via MONTHLY_BUDGET env var or --no-budget-check)
cost_log.jsonl: audit trail for every API call (try/finally — logs even on failure)
Actual spend authoritative: Anthropic console (not cost_log.jsonl)
Everything else: free (pure Python, no API)

## CURRENT PRODUCTION STATE
Model serving: v8 on Cerebrium (reverted from v10)
WhatsApp: +255637809070 via Wappfly
Endpoint: https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run
Dataset: 2,672 pairs (batches 001-013) on HuggingFace
Best gate scores: v8 (82.1% in-corpus, 70% out-of-corpus)
Gate target: >85% in-corpus AND >70% out-of-corpus (never passed)
