# AFRICA-GIANTS — Claude Code Master Directive v2.0

================================================================================
## MANDATORY FIRST ACTIONS — DO NOT SKIP OR REORDER
================================================================================

Before writing a single line of code, you MUST complete all of these in order:

1. Read this entire directive from top to bottom without skipping anything
2. Read and deeply analyze EVERY file in this repository
3. Read the CODEX HANDOVER section at the bottom of this file completely
4. Cross-reference the Codex work against what exists in the repository
5. Build a complete mental model of the system — past, present, and future state
6. Produce a full audit report (format specified below)
7. Wait for explicit human confirmation before touching any code

Skipping any of these steps will result in misaligned work.
Thinking fast is not the goal here. Thinking correctly is.

================================================================================
## WHO YOU ARE IN THIS PROJECT
================================================================================

You are not just a code assistant. You are the lead engineer, system architect,
and quality guardian of this project. You inherited a partially built system
from OpenAI Codex. Your job is to:

- Deeply understand what was built and why
- Find everything that is broken, inefficient, or incomplete
- Propose better approaches where the current design falls short
- Rebuild weak parts without destroying what works
- Drive the system toward full autonomy with zero compromise on quality
- Think like an engineer who will maintain this system for years

Think harder than you normally would. This is not a quick fix job.
This is an architectural responsibility.

================================================================================
## PROJECT MISSION — READ THIS CAREFULLY
================================================================================

AFRICA-GIANTS is an end-to-end autonomous AI system built specifically for
Tanzanian businesses. It is not a chatbot. It is not a demo. It is a living,
self-improving intelligence pipeline that must eventually run itself.

### Core Purpose
Provide Tanzanian businesses — small shops, markets, service providers,
manufacturers, exporters — with an AI that:
- Understands their world: prices, suppliers, regulations, customers, language
- Speaks their language: Swahili and English, naturally and accurately
- Learns continuously from real Tanzanian business data
- Answers questions, solves problems, and generates insights specific to Tanzania
- Becomes more capable with every training cycle

### The Bigger Vision
This system should become the most knowledgeable AI about Tanzanian business
ever built. Not because it was given that knowledge — but because it collected,
processed, and learned it autonomously from the ground up.

Built in Africa. For Africa. By Africa.

### Success Looks Like
- Pipeline runs on a schedule with zero manual intervention
- New data is scraped, cleaned, and ready for training automatically
- Models are trained on Kaggle, evaluated, and pushed to HuggingFace automatically
- RAG system stays fresh — new knowledge integrated without rebuilding from scratch
- Any Tanzanian business owner can query the system in Swahili or English
- System logs every action, flags every failure, and recovers without human help

================================================================================
## FULL SYSTEM ARCHITECTURE
================================================================================

Understand this architecture completely. Every component must exist,
be tested, and connect cleanly to the next.

### LAYER 1 — Intelligent Data Collection
Purpose: Continuously harvest Tanzanian business knowledge from the web

Requirements:
- Scrape: business directories, news sites, government portals, market prices,
  product listings, company profiles, trade data, regulations, reviews
- Language: handle both Swahili and English pages equally well
- Storage: raw data saved as structured JSON/CSV/Parquet with metadata
  (source URL, scrape timestamp, language, content type, quality score)
- Deduplication: content-based hashing to prevent duplicate entries
- Scheduling: configurable intervals — hourly, daily, weekly per source
- Politeness: respect robots.txt, implement rate limiting, rotate user agents
- Failure handling: retry logic, dead source detection, alert on repeated failure
- Monitoring: scrape success rates, data volume per run, source health dashboard

### LAYER 2 — Data Processing Pipeline
Purpose: Transform raw scraped data into training-ready and RAG-ready formats

Two parallel pipelines must exist:

Pipeline A — Training Data Preparation:
- Clean text: remove HTML, fix encoding, normalize whitespace and punctuation
- Filter quality: minimum length, language detection, relevance scoring
- Format: convert to instruction/response pairs for supervised fine-tuning
- Augment: generate variations to increase dataset diversity
- Split: train/validation/test with stratification
- Output: HuggingFace datasets format, versioned and tracked

Pipeline B — RAG Data Preparation:
- Chunk documents intelligently (semantic chunking, not fixed-length)
- Generate embeddings using a lightweight multilingual model
- Store in vector database with rich metadata for filtered retrieval
- Index: optimized for fast similarity search at scale
- Refresh: incremental updates when new data arrives — no full rebuilds
- Output: FAISS or ChromaDB persistent store, versioned

Quality gates must exist between scraping and processing.
Nothing low-quality enters the training or RAG pipeline.

### LAYER 3 — Model Training on Kaggle
Purpose: Fine-tune a capable base model on Tanzanian business data

Requirements:
- Platform: Kaggle free GPUs only (T4 x2 or P100)
- Base model: select from Qwen3, Mistral, or LLaMA based on task performance
- Method: QLoRA fine-tuning via Unsloth for maximum memory efficiency
- Evaluation: perplexity, ROUGE, human-eval samples after each run
- Checkpointing: save every N steps, resume from checkpoint on interruption
- Auto-upload: push final checkpoint to HuggingFace Hub automatically
- Experiment tracking: log hyperparameters, metrics, dataset version per run
- Reproducibility: every Kaggle notebook must run end-to-end from scratch
- Versioning: every trained model gets a semantic version tag on HF Hub

### LAYER 4 — RAG System
Purpose: Give the model access to fresh Tanzanian business knowledge at query time

Requirements:
- Retriever: dense retrieval using multilingual embeddings
- Reranker: cross-encoder reranking for top-k results
- Generator: fine-tuned model conditioned on retrieved context
- Languages: seamless Swahili/English query handling
- Fallback: if retrieval confidence is low, flag the response as uncertain
- Refresh cycle: new documents integrated into vector store on a schedule
- Evaluation: retrieval precision/recall tracked per query type

### LAYER 5 — Deployment on HuggingFace
Purpose: Make the system accessible and production-ready

Requirements:
- HuggingFace Spaces: Gradio interface for direct user interaction
- API endpoint: REST API for business application integrations
- Model versioning: clear v1, v2, v3... releases with changelogs on HF Hub
- Performance: response latency under 5 seconds for 95% of queries
- Monitoring: track query volume, response quality, error rates
- Fallback: if inference API is down, serve from backup or queue
- Documentation: README on HF Space explaining how to use the system

### LAYER 6 — Automation and Orchestration Engine
Purpose: Tie all layers together into a self-running pipeline

Requirements:
- Orchestrator: master script that triggers all layers in sequence
- Scheduler: cron-based or event-driven triggers per layer
- State management: track pipeline state — which step is running/done/failed
- Error handling: catch failures at every step, retry with backoff
- Alerting: log failures with full context for human review
- Self-healing: if a non-critical step fails, pipeline continues and flags it
- Reporting: after every full pipeline run, generate a run report
- Config: all parameters in a single config.yaml — nothing hardcoded

================================================================================
## YOUR RESPONSIBILITIES AS LEAD ENGINEER
================================================================================

### 1. Deep Problem Detection
Go beyond surface bugs. Look for:
- Architectural flaws that will cause problems at scale
- Logic errors that produce wrong results silently
- Missing error handling that causes silent failures
- Hardcoded values that break in different environments
- Inefficient algorithms that will slow down at scale
- Missing validation that allows bad data to corrupt the pipeline
- Security risks: exposed credentials, unsafe eval, unvalidated inputs
- Dead code: functions defined but never called
- Circular dependencies and poor module boundaries
- Missing tests on critical functions

### 2. Solution Design
For every problem found:
- Explain why it is a problem and what damage it causes
- Propose the best solution with clear reasoning
- If multiple solutions exist, present them with tradeoffs
- Prefer simple and maintainable over clever and complex
- Consider the next engineer who will read this code

### 3. System Improvement
Beyond fixing bugs, actively improve:
- Refactor tangled code into clean, single-responsibility modules
- Replace hardcoded values with config-driven parameters
- Add structured logging to every module (not just print statements)
- Add type hints to every function signature
- Add docstrings to every class and function
- Add unit tests for every critical function
- Make every script runnable standalone AND as part of the full pipeline
- Add a Makefile or run scripts for common operations

### 4. Codex Work Integration
The Codex work below must be:
- Read with full attention — understand intent, not just syntax
- Evaluated critically — what is good, what is flawed, what is missing
- Integrated cleanly — keep what works, improve what is weak, replace what is wrong
- Never discarded blindly — if you remove something Codex built, explain why

================================================================================
## NON-NEGOTIABLE ENGINEERING RULES
================================================================================

1. Never delete working code — refactor, never remove without justification
2. Never assume — if something is unclear, ask before proceeding
3. Never change the tech stack without explicit approval
4. Every file you create must have a header comment block:
   - File purpose
   - Author: Claude Code
   - Date created
   - Dependencies
5. Every function must have:
   - Docstring explaining purpose, parameters, and return value
   - Type hints on all parameters and return types
   - Error handling for expected failure modes
6. No hardcoded values — use config.yaml or environment variables
7. No silent failures — every exception must be logged with context
8. No untested critical paths — write tests for scraping, processing, training
9. After every completed component, update PROGRESS.md immediately
10. Never declare something complete without running it and verifying output

================================================================================
## SESSION WORKFLOW — FOLLOW THIS EVERY TIME
================================================================================

Every Claude Code session must follow this exact structure:

### ORIENT (Start of every session)
- Read PROGRESS.md to understand where the last session ended
- Identify what is in progress, what is blocked, what is next
- State clearly: "Based on PROGRESS.md, I will continue with X because Y"

### PLAN
- Break the work into specific, testable tasks
- Estimate complexity: simple / medium / complex
- Identify dependencies — what must be done before what
- State the plan explicitly before starting

### CONFIRM
- Present the plan to the human
- Wait for explicit approval — do not start coding on assumption
- If the human changes direction, acknowledge and re-plan

### EXECUTE
- Work through one task at a time
- Explain what you are doing as you do it
- Flag unexpected discoveries immediately
- Never silently skip a step because it is hard

### VERIFY
- Run the code or trace through it manually
- Check outputs against expected behavior
- Fix issues before moving to the next task

### DOCUMENT
- Update PROGRESS.md with:
  - What was completed this session
  - What was discovered (bugs, improvements, questions)
  - What comes next in priority order
  - Any blockers or decisions needed from human

================================================================================
## TECHNOLOGY STACK — DO NOT CHANGE WITHOUT APPROVAL
================================================================================

| Layer | Component | Technology |
|---|---|---|
| Scraping | Web crawler | Scrapy / Playwright / BeautifulSoup |
| Storage | Raw data | JSON, CSV, Parquet |
| Processing | Data pipeline | Python, Pandas, HuggingFace Datasets |
| Embeddings | Vector generation | sentence-transformers (multilingual) |
| Vector store | RAG retrieval | FAISS or ChromaDB |
| Training | Platform | Kaggle (T4 x2 / P100 free GPU) |
| Training | Framework | Unsloth + QLoRA + HuggingFace Transformers |
| Base model | LLM | Qwen3 / Mistral / LLaMA |
| Deployment | Interface | HuggingFace Spaces (Gradio) |
| Deployment | API | HuggingFace Inference API |
| Orchestration | Pipeline runner | Python + schedule / cron |
| Config | Parameters | config.yaml |
| Logging | System logs | Python logging module (structured) |
| Languages | NLP | Swahili + English |
| Version control | Code | GitHub |
| Model versioning | Models | HuggingFace Hub |

================================================================================
## IMMEDIATE FIRST TASK — EXECUTE THIS NOW
================================================================================

Do not write any code yet. Do this first:

### STEP 1 — Repository Audit
Analyze every file and produce this exact report:

REPOSITORY AUDIT REPORT
Overall Completion: X%
FILES ANALYZED:

[filename]: [purpose] | Status: [working/broken/incomplete/missing]

LAYER STATUS:

Layer 1 (Scraping): X% complete | Issues: [list]
Layer 2 (Processing): X% complete | Issues: [list]
Layer 3 (Training): X% complete | Issues: [list]
Layer 4 (RAG): X% complete | Issues: [list]
Layer 5 (Deployment): X% complete | Issues: [list]
Layer 6 (Automation): X% complete | Issues: [list]

TOP 5 CRITICAL PROBLEMS (ranked by severity):

[problem] | Severity: Critical/High/Medium | Impact: [what breaks]
...

TOP 5 HIGH IMPACT IMPROVEMENTS (ranked by value):

[improvement] | Effort: Low/Medium/High | Value: [what it unlocks]
...

CODEX WORK ASSESSMENT:

What Codex built that is solid and reusable: [list]
What Codex built that needs improvement: [list]
What Codex left incomplete: [list]
What Codex got wrong architecturally: [list]


### STEP 2 — Roadmap
After the audit, propose a numbered 10-step roadmap to reach full automation.
Each step must include: what it achieves, why it matters, estimated complexity.

### STEP 3 — Confirm
Present the audit report and roadmap. Ask which step to begin.
Do not start any work until confirmed.

================================================================================
## CODEX HANDOVER — WORK DONE BY OPENAI CODEX
================================================================================
================================================================================
## IMPORTANT NOTICE ABOUT THE CODEX SECTION BELOW
================================================================================

CRITICAL: Read this section carefully before reading the Codex work below.

The content below the CODEX HANDOVER section is NOT the complete project.
It is a partial working session — a mix of:
- Some debugging work done with OpenAI Codex
- Exploratory code written during troubleshooting
- Partial implementations that were tested but not finalized
- Notes and fixes made during a single work session

DO NOT treat it as:
- The full system architecture
- Production-ready code
- A complete feature implementation
- The final design decisions for this project

TREAT IT AS:
- Reference material showing what was attempted and why
- A debugging log that reveals pain points in the system
- Partial progress that may or may not align with the architecture above
- Raw material to learn from — not copy blindly

Your job is to:
1. Read it with a critical engineering eye
2. Extract what is genuinely useful and working
3. Discard or rewrite what is hacky, incomplete, or misaligned
4. Integrate the good parts cleanly into the proper architecture
5. Never let the quality of this partial work set the bar for yours

The real architecture and mission are defined ABOVE this section.
That is your north star. The Codex work below is just context.

--- CODEX WORK STARTS HERE ---

(((((Upload your repo training files as a Kaggle Dataset:

data/processed/train_sft.jsonl
data/processed/val_sft.jsonl
data/eval/tanzania_business_qa.jsonl
Name it something like:

africa-giants-training-data
2. Create Kaggle Secrets

In Kaggle notebook settings, add secrets:

HF_TOKEN
Optional later:

WANDB_API_KEY
Your HF_TOKEN must have write access to your Hugging Face repos.

3. Open The Training Notebook

Use:

notebooks/kaggle_train_arque_llama.ipynb
In Kaggle, it should do:

install dependencies
login to Hugging Face
load Afrique Llama 8B
load train_sft.jsonl and val_sft.jsonl
train QLoRA adapter
save adapter
push adapter to Hugging Face
4. Enable GPU

In Kaggle:

Settings → Accelerator → GPU
Use the best available GPU. If memory is low, use QLoRA 4-bit and reduce:

batch_size
max_seq_length
gradient_accumulation_steps
5. Run A Tiny Test First

Do not start full training first.

Test with:

max_steps: 10
epochs: 1
small dataset
Goal is only to confirm:

model loads
dataset loads
training starts
adapter saves
adapter pushes to Hugging Face
6. Push Adapter To Hugging Face

First push only the LoRA adapter:

prospAprospA007/africa-giants-adapter-v1
Later you can merge and push:

prospAprospA007/africa-giants-model-v1
7. Run Evaluation After Training

After Kaggle finishes, run evaluation against:

data/eval/tanzania_business_qa.jsonl
data/eval/business_benchmarks.jsonl
data/eval/safety.jsonl
The model should pass:

accuracy score
hallucination rate
latency
safety behavior
8. Update Hugging Face Deployment

Once adapter/model is pushed:

update config/huggingface.yaml
update MODEL_ID in Hugging Face Space
run smoke tests
Best First Kaggle Goal

Your first successful notebook run should produce:

Afrique Llama 8B + QLoRA adapter → pushed to Hugging Face
Then your live app can load:

prospAprospA007/africa-giants-adapter-v1
or the merged model repo.





Thursday 9:32 PM
how do i create a repo in hf and there is no place to add the secret in kaggle
Thursday 9:41 PM


Worked for 29s
Yes, this part is confusing at first. Do it like this.

Create A Hugging Face Repo

Go to https://huggingface.co/new
Choose Model
Owner: choose your account or org
Repo name, for example:
africa-giants-adapter-v1
Visibility: choose Private while testing
Click Create repository
Create these repos:

prospAprospA007/africa-giants-adapter-v1
prospAprospA007/africa-giants-model-v1
prospAprospA007/africa-giants-dataset
For the app later, create a Space:

Go to https://huggingface.co/new-space
Name:
africa-giants-app
SDK: choose Gradio first, or Docker/FastAPI later.
HF docs also say repos can be created from the web at huggingface.co/new, or with Python/CLI using huggingface_hub.

Alternative: Create Repo From Kaggle Code

In Kaggle notebook:

!pip install -q huggingface_hub
from huggingface_hub import login, create_repo
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HF_TOKEN")

login(token=hf_token)

create_repo(
    repo_id="prospAprospA007/africa-giants-adapter-v1",
    repo_type="model",
    private=True,
    exist_ok=True
)
About Kaggle Secrets

In Kaggle notebooks, the secret area is usually here:

Notebook editor → Add-ons → Secrets
Then click:

Add a new secret
Add:

Label: HF_TOKEN
Value: your_hugging_face_token
Then use it in code:
ackendError                              Traceback (most recent call last)
/tmp/ipykernel_57/1035800691.py in <cell line: 0>()
      3 
      4 user_secrets = UserSecretsClient()
----> 5 hf_token = user_secrets.get_secret("HF_TOKEN")
      6 
      7 login(token=hf_token)

/usr/local/lib/python3.12/dist-packages/kaggle_secrets.py in get_secret(self, label)
     62             'Label': label,
     63         }
---> 64         response_json = self.web_client.make_post_request(request_body, self.GET_USER_SECRET_BY_LABEL_ENDPOINT)
     65         if 'secret' not in response_json:
     66             raise BackendError(

/usr/local/lib/python3.12/dist-packages/kaggle_web_client.py in make_post_request(self, data, endpoint, timeout)
     47                 response_json = json.loads(response.read())
     48                 if not response_json.get('wasSuccessful') or 'result' not in response_json:
---> 49                     raise BackendError(
     50                         f'Unexpected response from the service. Response: {response_json}.')
     51                 return response_json['result']

BackendError: Unexpected response from the service. Response: {'errors': ['No user secrets exist for kernel id 120129326 and label HF_TOKEN.'], 'error': {'code': 5}, 'wasSuccessful': False}.
add Codeadd Markdown

Show more
Thursday 10:09 PM

The error means Kaggle cannot find a secret named:

HF_TOKEN
But you named yours:

AFRICA GIANTS
So change your code to:

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login

user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("AFRICA GIANTS")

login(token=hf_token)
If that gives an error because of the space, rename the Kaggle secret to:

AFRICA_GIANTS
Then use:

hf_token = user_secrets.get_secret("AFRICA_GIANTS")
login(token=hf_token)
I recommend renaming it to:

HF_TOKEN
because most notebook examples expect that name. The label in get_secret("...") must match exactly what you created in Kaggle.





Thursday 10:09 PM
TTPStatusError                           Traceback (most recent call last)
/usr/local/lib/python3.12/dist-packages/huggingface_hub/utils/_http.py in hf_raise_for_status(response, endpoint_name)
    656     try:
--> 657         response.raise_for_status()
    658     except httpx.HTTPStatusError as e:

/usr/local/lib/python3.12/dist-packages/httpx/_models.py in raise_for_status(self)
    828         message = message.format(self, error_type=error_type)
--> 829         raise HTTPStatusError(message, request=request, response=self)
    830 

HTTPStatusError: Client error '401 Unauthorized' for url 'https://huggingface.co/api/whoami-v2'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401

The above exception was the direct cause of the following exception:

HfHubHTTPError                            Traceback (most recent call last)
/usr/local/lib/python3.12/dist-packages/huggingface_hub/hf_api.py in _inner_whoami(self, token)
   1988         try:
-> 1989             hf_raise_for_status(r)
   1990         except HfHubHTTPError as e:

/usr/local/lib/python3.12/dist-packages/huggingface_hub/utils/_http.py in hf_raise_for_status(response, endpoint_name)
    751         # as well (request id and/or server error message)
--> 752         raise _format(HfHubHTTPError, str(e), response) from e
    753 

HfHubHTTPError: Client error '401 Unauthorized' for url 'https://huggingface.co/api/whoami-v2' (Request ID: Root=1-6a0f58b2-148a76b0250977df73c6d665;02ad3000-40de-4898-b12c-32c0cf2228e4)
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401

User Access Token "AFRICA GIANTS" is expired

The above exception was the direct cause of the following exception:

HfHubHTTPError                            Traceback (most recent call last)
/tmp/ipykernel_57/3686984805.py in <cell line: 0>()
      5 hf_token = user_secrets.get_secret("AFRICA_GIANTS")
      6 
----> 7 login(token=hf_token)

/usr/local/lib/python3.12/dist-packages/huggingface_hub/_login.py in login(token, add_to_git_credential, skip_if_logged_in)
    110                 "you want to set the git credential as well."
    111             )
--> 112         _login(token, add_to_git_credential=add_to_git_credential)
    113     elif is_notebook():
    114         notebook_login(skip_if_logged_in=skip_if_logged_in)

/usr/local/lib/python3.12/dist-packages/huggingface_hub/_login.py in _login(token, add_to_git_credential)
    374         raise ValueError("You must use your personal account token, not an organization token.")
    375 
--> 376     token_info = whoami(token)
    377     permission = token_info["auth"]["accessToken"]["role"]
    378     logger.info(f"Token is valid (permission: {permission}).")

/usr/local/lib/python3.12/dist-packages/huggingface_hub/utils/_validators.py in _inner_fn(*args, **kwargs)
     87         kwargs = smoothly_deprecate_legacy_arguments(fn_name=fn.__name__, kwargs=kwargs)
     88 
---> 89         return fn(*args, **kwargs)
     90 
     91     return _inner_fn  # type: ignore

/usr/local/lib/python3.12/dist-packages/huggingface_hub/hf_api.py in whoami(self, token, cache)
   1974 
   1975         # Call Hub
-> 1976         output = self._inner_whoami(token=token)
   1977 
   1978         # Cache result and return

/usr/local/lib/python3.12/dist-packages/huggingface_hub/hf_api.py in _inner_whoami(self, token)
   2001                 elif token == _get_token_from_file():
   2002                     error_message += " The token stored is invalid. Please run hf auth login to update it."
-> 2003                 raise HfHubHTTPError(error_message, response=e.response) from e
   2004             if e.response.status_code == 429:
   2005                 error_message = (

HfHubHTTPError: Invalid user token.

Show more
Thursday 10:11 PM

That error means your Kaggle secret value is wrong. You likely saved the text:

AFRICA GIANTS
as the token value, instead of saving the real Hugging Face token.

Kaggle secret should be:

Name/Label: AFRICA_GIANTS
Value: hf_xxxxxxxxxxxxxxxxxxxxxxxxx
Not:

Value: AFRICA GIANTS
Fix it like this:

Go to Hugging Face tokens:
https://huggingface.co/settings/tokens

Create a new token:

Type: Write
Name: AFRICA_GIANTS
Copy the token. It should start with:
hf_
Go back to Kaggle notebook:
Add-ons → Secrets
Edit or delete your current secret.

Add it again:

Label: AFRICA_GIANTS
Value: hf_your_real_token_here
Then run:

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login, whoami

user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("AFRICA_GIANTS")

print(hf_token[:3])  # should print hf_
login(token=hf_token)

print(whoami(token=hf_token))
If print(hf_token[:3]) does not show:

hf_
then the secret value is still not the real Hugging Face token.





Thursday 10:11 PM
how can i see the repo is create in hf
Thursday 10:16 PM

To see if your Hugging Face repo was created:

Option 1: Browser

Open:

https://huggingface.co/prospAprospA007
Then check your Models, Datasets, or Spaces tabs.

Direct links may look like:

https://huggingface.co/prospAprospA007/africa-giants-adapter-v1
https://huggingface.co/prospAprospA007/africa-giants-model-v1
https://huggingface.co/datasets/prospAprospA007/africa-giants-dataset
https://huggingface.co/spaces/prospAprospA007/africa-giants-app
Option 2: Kaggle Code

After login succeeds, run:

from huggingface_hub import HfApi

api = HfApi()

repo_id = "prospAprospA007/africa-giants-adapter-v1"

info = api.repo_info(repo_id=repo_id, repo_type="model")
print(info.id)
print(info.private)
print(info.sha)
If it exists, it prints repo information.

If it does not exist, you’ll get an error like Repository Not Found.

Option 3: List Your Model Repos

from huggingface_hub import HfApi

api = HfApi()
models = api.list_models(author="prospAprospA007")

for model in models:
    print(model.modelId)
For datasets:

datasets = api.list_datasets(author="prospAprospA007")

for dataset in datasets:
    print(dataset.id)
For Spaces:

spaces = api.list_spaces(author="prospAprospA007")

for space in spaces:
    print(space.id)




Thursday 10:16 PM


from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HF_TOKEN")
If you do not see Add-ons → Secrets, check these:

1. You must be inside a Kaggle Notebook editor, not just the dataset page.
2. The notebook must be your own notebook, not someone else’s read-only notebook.
3. On the right sidebar, open Notebook options/settings and look for Secrets.
4. Try switching to the classic notebook editor if Kaggle UI is hiding it.
Fallback If Secrets Still Missing

For a quick test only, paste the token in a notebook variable:

hf_token = "hf_xxxxxxxxxxxxxxxxx"
Then:

from huggingface_hub import login
login(token=hf_token)
But after the test, delete the cell output and do not make the notebook public. Secrets are safer.

Get Hugging Face Token

Go to:

https://huggingface.co/settings/tokens

Create token with:

Write access
Then use it as HF_TOKEN in Kaggle.





Thursday 9:41 PM
I NAMED THE SECRET AFRICA GIANTS
Thursday 9:49 PM

I NAMED THE SECRET AFRICA GIANTS
Thursday 9:50 PM

I NAMED THE SECRET AFRICA GIANTS
Thursday 9:52 PM

I NAMED THE SECRET AFRICA GIANTS
Thursday 9:54 PM

I NAMED THE SECRET AFRICA GIANTS
how do i set the base model adopter repo merge model repo and dataset repo in kaggle
Friday 1:46 PM

In Kaggle, add a code cell near the top of your notebook, after login:

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login, whoami

hf_token = UserSecretsClient().get_secret("AFRICA_GIANTS")
login(token=hf_token)

print("Logged in as:", whoami(token=hf_token)["name"])
Then in the next cell set your repo variables:

BASE_MODEL = "prospAprospA007/Afrique-llama-8B"

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v1"

MERGED_MODEL_REPO = "prospAprospA007/africa-giants-model-v1"

DATASET_REPO = "prospAprospA007/africa-giants-dataset"
You will use them later like this:

from datasets import load_dataset

dataset = load_dataset(DATASET_REPO)
For loading the base model:

from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=hf_token)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    device_map="auto"
)
For pushing the adapter:

trainer.model.push_to_hub(ADAPTER_REPO, token=hf_token)
tokenizer.push_to_hub(ADAPTER_REPO, token=hf_token)
For pushing the merged model later:

merged_model.push_to_hub(MERGED_MODEL_REPO, token=hf_token)
tokenizer.push_to_hub(MERGED_MODEL_REPO, token=hf_token)
So your notebook order should be:

1. Install packages
2. Login to Hugging Face
3. Set BASE_MODEL, ADAPTER_REPO, MERGED_MODEL_REPO, DATASET_REPO
4. Load dataset
5. Load base model
6. Train adapter
7. Push adapter to Hugging Face
8. Evaluate
9. Merge and push final model if needed




Friday 1:46 PM
i want you to perform the tasks
Friday 1:47 PM


Worked for 2m 31s
Done. I updated and pushed the Kaggle notebook.

Commit:

d4e4278 Configure Kaggle notebook Hugging Face repos
What I changed in kaggle_train_arque_llama.ipynb:

BASE_MODEL = "prospAprospA007/Afrique-llama-8B"
ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v1"
MERGED_MODEL_REPO = "prospAprospA007/africa-giants-model-v1"
DATASET_REPO = "prospAprospA007/africa-giants-dataset"
Also wired:

hf_token = user_secrets.get_secret("AFRICA_GIANTS")
And added:

repo creation/checking from Kaggle
dataset loading from DATASET_REPO
base model loading from BASE_MODEL
adapter push to ADAPTER_REPO
optional merge and push to MERGED_MODEL_REPO
SMOKE_TEST_TRAINING = True for a first tiny 10-step Kaggle run
Next in Kaggle: pull/open the updated notebook from GitHub, run it with GPU + Internet ON, and keep SMOKE_TEST_TRAINING = True for the first test.


Edited kaggle_train_arque_llama.ipynb
+111
-57
Undo
Review
Details




Friday 1:50 PM
where can i get the updated notebook in kaggle
Friday 1:53 PM

You have two easy options.

Option 1: Download From GitHub Then Upload To Kaggle

Open your GitHub repo:

https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
Go to:

notebooks/kaggle_train_arque_llama.ipynb
Click:

Download raw file
Then in Kaggle:

Create → New Notebook → File → Upload Notebook
Upload the .ipynb.

Option 2: Import GitHub Repo In Kaggle

In Kaggle:

Create → New Notebook
Then in notebook settings or sidebar, look for:

Add input → GitHub
or

File → Import Notebook
Use your repo:

prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
Notebook path:

notebooks/kaggle_train_arque_llama.ipynb
Direct GitHub Notebook Link

Use this:

https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/blob/main/notebooks/kaggle_train_arque_llama.ipynb
Make sure the notebook has this line near the top:

hf_token = user_secrets.get_secret("AFRICA_GIANTS")
That confirms it is the updated version.





Friday 1:53 PM
lets start loading the model to kagle first
Friday 2:05 PM

Good. In Kaggle, start with only loading the model, before training.

Run these cells in order.

1. Install Packages

!pip install -q -U transformers accelerate bitsandbytes huggingface_hub sentencepiece
2. Login To Hugging Face

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login, whoami

hf_token = UserSecretsClient().get_secret("AFRICA_GIANTS")
login(token=hf_token)

print("Logged in as:", whoami(token=hf_token)["name"])
3. Set Model Repo

BASE_MODEL = "prospAprospA007/Afrique-llama-8B"
4. Check GPU

import torch

print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("GPU memory GB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
5. Load Tokenizer

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded")
print("Vocab size:", len(tokenizer))
6. Load Model In 4-Bit

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model.eval()
print("Model loaded successfully")
7. Quick Test Generation

prompt = "Explain how a small business in Tanzania can start keeping proper bookkeeping records."

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))

CHANGED TO PUBLIC BUT STILL THE ERROR PERSISTS
Friday 2:29 PM

Changing your repos to public does not fix this specific error because the missing repo is the base model:

prospAprospA007/Afrique-llama-8B
Your created repos are:

prospAprospA007/africa-giants-adapter-v1
prospAprospA007/africa-giants-model-v1
prospAprospA007/africa-giants-dataset
Those are output repos. They do not contain the base model yet.

Run this in Kaggle:

from huggingface_hub import HfApi

api = HfApi(token=hf_token)

models = api.list_models(author="prospAprospA007")

for model in models:
    print(model.modelId)
If you do not see:

prospAprospA007/Afrique-llama-8B
then this line is wrong:

BASE_MODEL = "prospAprospA007/Afrique-llama-8B"
Use a real public base model instead, for example:

BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
For a Llama-style model use:

BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
Then test tokenizer again:

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    trust_remote_code=True
)

print("Tokenizer loaded:", BASE_MODEL)
If that works, the issue is confirmed: prospAprospA007/Afrique-llama-8B does not exist or is named differently.

So for now set:

BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
Then continue.





Friday 2:29 PM
prospAprospA007/africa-giants-adapter-v1
prospAprospA007/africa-giants-model-v1 COMES AFTER RUNNING THE FIRST CODE
Friday 2:32 PM

Exactly. That confirms the problem.

Your account only has:

prospAprospA007/africa-giants-adapter-v1
prospAprospA007/africa-giants-model-v1
It does not have:

prospAprospA007/Afrique-llama-8B
So this line is wrong for now:

BASE_MODEL = "prospAprospA007/Afrique-llama-8B"
Use a real public base model instead.

For Kaggle test, use this smaller model first:

BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
Then run tokenizer:

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded:", BASE_MODEL)
print("Vocab size:", len(tokenizer))
After that, load model:

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model.eval()
print("Model loaded successfully:", BASE_MODEL)
For the real larger version later, use one of these if Kaggle GPU can handle it:

BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
or:

BASE_MODEL = "NousResearch/Meta-Llama-3-8B-Instruct"
But first use SmolLM2-1.7B-Instruct to prove the pipeline works.





Friday 2:32 PM
GIVE THE CODE FOR BASE MODEL TO BE METAS AFRIQUE LLAMA 8B
Friday 2:34 PM


Worked for 26s
Use this. The correct Hugging Face repo for AfriqueLlama 8B is:

BASE_MODEL = "McGill-NLP/AfriqueLlama-8B"
Full Kaggle code:

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login, whoami

hf_token = UserSecretsClient().get_secret("AFRICA_GIANTS")
login(token=hf_token)

print("Logged in as:", whoami(token=hf_token)["name"])
BASE_MODEL = "McGill-NLP/AfriqueLlama-8B"
ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v1"
MERGED_MODEL_REPO = "prospAprospA007/africa-giants-model-v1"
DATASET_REPO = "prospAprospA007/africa-giants-dataset"

print("Base model:", BASE_MODEL)
Then load tokenizer:

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded:", BASE_MODEL)
print("Vocab size:", len(tokenizer))
Then load model in 4-bit:

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model.eval()
print("Model loaded successfully:", BASE_MODEL)
Source: McGill-NLP/AfriqueLlama-8B on Hugging Face





Friday 2:35 PM
NameError                                 Traceback (most recent call last)
/tmp/ipykernel_57/3596308228.py in <cell line: 0>()
     10 
     11 model = AutoModelForCausalLM.from_pretrained(
---> 12     BASE_MODEL,
     13     token=hf_token,
     14     quantization_config=bnb_config,

NameError: name 'BASE_MODEL' is not defined
it returned out puts whats next
Friday 5:21 PM

Good. Next load the tokenizer and model.

First check GPU again:

import torch

print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("Memory GB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
If it says CUDA available: False, stop and turn GPU on.

If it says True, run tokenizer:

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded")
print("Vocab size:", len(tokenizer))
Then load model in 4-bit:

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model.eval()
print("Model loaded successfully:", BASE_MODEL)
After that, test generation:

prompt = "Explain simple bookkeeping steps for a small shop in Tanzania."

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
Send me the output or any error.





Friday 5:21 PM
make the test in swahili
Friday 5:25 PM

Use this Swahili test prompt:

prompt = "Eleza hatua rahisi za kuweka kumbukumbu za mahesabu kwa duka dogo nchini Tanzania."
Full generation cell:

import torch

prompt = "Eleza hatua rahisi za kuweka kumbukumbu za mahesabu kwa duka dogo nchini Tanzania."

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=160,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(answer)
Another good Swahili test:

prompt = "Nina biashara ndogo ya kuuza nguo Dar es Salaam. Nawezaje kupata wateja zaidi na kuweka hesabu vizuri?"




Friday 5:25 PM
the model is already loaded lets now start the training and screaping of data from different sites and also adding vision and speech to the model
Friday 5:30 PM


Worked for 1m 14s
Yes. Start in this order inside Kaggle.

1. Scrape Starter Data

Run this cell first:

!pip install -q beautifulsoup4 requests pandas datasets huggingface_hub
import requests, json, time, re
from bs4 import BeautifulSoup
from datetime import datetime

SITES = [
    {"name": "TNBP", "url": "https://business.go.tz/about-us"},
    {"name": "BRELA", "url": "https://www.brela.go.tz/"},
    {"name": "BRELA_ORS", "url": "https://bos.brela.go.tz/"},
    {"name": "NBS", "url": "https://www.nbs.go.tz/"},
    {"name": "TRA", "url": "https://www.tra.go.tz/"},
]

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

rows = []

for site in SITES:
    try:
        r = requests.get(site["url"], timeout=20, headers={"User-Agent": "AfricaGiantsBot/0.1"})
        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = clean_text(soup.get_text(" "))
        if len(text) > 300:
            rows.append({
                "source_name": site["name"],
                "url": site["url"],
                "title": soup.title.get_text(strip=True) if soup.title else site["name"],
                "text": text[:8000],
                "scraped_at": datetime.utcnow().isoformat()
            })
            print("Scraped:", site["name"], len(text))
        else:
            print("Too short:", site["name"])
        time.sleep(1)
    except Exception as e:
        print("Failed:", site["name"], e)

print("Total docs:", len(rows))
2. Create Training Q&A From Scraped Text

This creates a simple first dataset:

qa_rows = []

SYSTEM = "You are Africa Giants, a Tanzanian business assistant. Help with business registration, tax, bookkeeping, marketing, and business management using verified context."

for row in rows:
    text = row["text"][:2500]
    source = row["source_name"]

    qa_rows.append({
        "instruction": f"What useful business information is available from {source}?",
        "input": text,
        "output": f"According to {source}, this source contains information useful for Tanzanian businesses. Use it to answer carefully, cite the source, and recommend checking the official page when rules may have changed. Source: {row['url']}",
        "source": source,
        "url": row["url"]
    })

manual_qa = [
    {
        "instruction": "Ninaanzaje biashara rasmi Tanzania?",
        "input": "",
        "output": "Anza kwa kuchagua aina ya biashara, sajili jina au kampuni BRELA inapohitajika, pata TIN kupitia TRA, omba leseni sahihi ya biashara, kisha weka kumbukumbu za mauzo, matumizi, stoo, madeni na malipo.",
        "source": "manual"
    },
    {
        "instruction": "Nifanye nini kuweka hesabu za duka dogo?",
        "input": "",
        "output": "Andika mauzo ya kila siku, matumizi, bidhaa zilizoingia na kutoka, fedha taslimu, malipo ya simu, madeni ya wateja, madeni ya wasambazaji na faida ya wiki au mwezi.",
        "source": "manual"
    },
    {
        "instruction": "Nawezaje kupata wateja zaidi kwa biashara ndogo?",
        "input": "",
        "output": "Tambua mteja wako, tengeneza ofa rahisi, tumia WhatsApp Business, Instagram, TikTok, Google Business Profile, na masoko ya mtandaoni. Pima kila wiki njia gani inaleta wateja na mauzo zaidi.",
        "source": "manual"
    }
]

qa_rows.extend(manual_qa)
print("Training rows:", len(qa_rows))
3. Save Train And Validation Files

import random, os, json

random.seed(42)
random.shuffle(qa_rows)

split = max(1, int(len(qa_rows) * 0.8))
train_rows = qa_rows[:split]
val_rows = qa_rows[split:] or qa_rows[:1]

os.makedirs("/kaggle/working/data", exist_ok=True)

def write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

write_jsonl("/kaggle/working/data/train_sft.jsonl", train_rows)
write_jsonl("/kaggle/working/data/val_sft.jsonl", val_rows)

print("Train:", len(train_rows))
print("Validation:", len(val_rows))
4. Push Dataset To Hugging Face

from huggingface_hub import HfApi, upload_file, create_repo

create_repo(
    repo_id=DATASET_REPO,
    repo_type="dataset",
    private=False,
    exist_ok=True,
    token=hf_token
)

upload_file(
    path_or_fileobj="/kaggle/working/data/train_sft.jsonl",
    path_in_repo="train_sft.jsonl",
    repo_id=DATASET_REPO,
    repo_type="dataset",
    token=hf_token
)

upload_file(
    path_or_fileobj="/kaggle/working/data/val_sft.jsonl",
    path_in_repo="val_sft.jsonl",
    repo_id=DATASET_REPO,
    repo_type="dataset",
    token=hf_token
)

print("Dataset pushed:", DATASET_REPO)
5. Load Dataset For Training

from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files={
        "train": "/kaggle/working/data/train_sft.jsonl",
        "validation": "/kaggle/working/data/val_sft.jsonl"
    }
)

print(dataset)
6. Start Tiny LoRA Training

Only run this after the model is already loaded.

!pip install -q peft trl accelerate
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import TrainingArguments
from trl import SFTTrainer

model = prepare_model_for_kbit_training(model)

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
def formatting_prompts_func(example):
    texts = []
    for i in range(len(example["instruction"])):
        instruction = example["instruction"][i]
        context = example["input"][i] if "input" in example and example["input"][i] else ""
        output = example["output"][i]

        if context:
            text = f"""<|im_start|>system
You are Africa Giants, a Tanzanian business assistant. Use verified context when available.<|im_end|>
<|im_start|>user
Context: {context}

Question: {instruction}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>"""
        else:
            text = f"""<|im_start|>system
You are Africa Giants, a Tanzanian business assistant.<|im_end|>
<|im_start|>user
{instruction}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>"""

        texts.append(text)
    return texts
training_args = TrainingArguments(
    output_dir="/kaggle/working/africa-giants-lora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=2e-4,
    max_steps=10,
    logging_steps=1,
    save_strategy="steps",
    save_steps=10,
    report_to="none",
    fp16=True
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    formatting_func=formatting_prompts_func,
    args=training_args,
    max_seq_length=1024,
    packing=False
)

trainer.train()
7. Push Adapter

trainer.model.push_to_hub(ADAPTER_REPO, token=hf_token)
tokenizer.push_to_hub(ADAPTER_REPO, token=hf_token)

print("Adapter pushed:", ADAPTER_REPO)
8. Vision And Speech

Do not train AfriqueLlama as a vision/speech model yet. Add these as tools around it:

Vision:

!pip install -q pillow transformers
Use image captioning/OCR first, then send extracted text to AfriqueLlama.

Speech:

!pip install -q openai-whisper
Use speech-to-text first, then send transcript to AfriqueLlama.

Architecture:

Image → OCR/caption model → text → AfriqueLlama
Voice → Whisper speech-to-text → text → AfriqueLlama
AfriqueLlama answer → optional text-to-speech
First goal today: scrape → create dataset → tiny 10-step LoRA training → push adapter to Hugging Face. Then we add vision and speech cleanly.
i added the trainer=SFTTariner and its taking time is it valid
Friday 5:52 PM

Yes, it can be valid. trainer = SFTTrainer(...) can take time because it is:

formatting the dataset
tokenizing text
building dataloaders
checking model/training config
preparing LoRA training
For an 8B model on Kaggle, this can take a few minutes.

But check these signs:

Valid signs

progress bar appears
CPU/GPU usage is active
RAM/GPU memory changes
no red error traceback
Kaggle cell shows [*] running
Wait time

For your small test dataset:

SFTTrainer creation: 1 to 5 minutes
trainer.train(): 5 to 20 minutes for 10 steps, depending on GPU
If it hangs more than 10 minutes at trainer = SFTTrainer(...), reduce sequence length:

max_length=512
and use:

max_steps=5
Also make sure you are not accidentally using a large scraped dataset.

After trainer = SFTTrainer(...) finishes, run:

trainer.train()
If the cell is still running, let it continue unless Kaggle memory is maxed out or it throws an error.





Friday 5:52 PM
Step	Training Loss
1	0.775898
2	0.383667
3	0.736225
4	1.417340
5	2.198085
6	0.811674
7	1.209637
8	0.597889
9	0.602966
10	2.052277
TrainOutput(global_step=10, training_loss=1.0785656541585922, metrics={'train_runtime': 25.7961, 'train_samples_per_second': 0.388, 'train_steps_per_second': 0.388, 'total_flos': 206249032581120.0, 'train_loss': 1.0785656541585922})
Friday 5:53 PM

Excellent. That means training worked.

Your first 10-step LoRA smoke test completed successfully:

global_step: 10
training_loss: 1.0785
runtime: 25.8 seconds
Next, push the trained adapter to Hugging Face:

trainer.model.push_to_hub(ADAPTER_REPO, token=hf_token)
tokenizer.push_to_hub(ADAPTER_REPO, token=hf_token)

print("Adapter pushed to:", ADAPTER_REPO)
Then check it in browser:

https://huggingface.co/prospAprospA007/africa-giants-adapter-v1
After that, run a quick evaluation:

eval_results = trainer.evaluate()
print(eval_results)
Then test the trained adapter response:

prompt = "Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?"

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
If adapter push works, your next serious step is to increase training from smoke test to real run:

max_steps: 100 to 500
max_length: 1024
better dataset
more official Tanzanian sources




Friday 5:53 PM
dose the eval_results = trainer.evaluate() take time
Friday 6:11 PM

Yes, eval_results = trainer.evaluate() can take time.

For your small test dataset, expect:

30 seconds to 5 minutes
It depends on:

validation dataset size
max_length
GPU type
model size
batch size
If your validation set is very small, it should finish quickly.

If it takes too long, stop it and use fewer validation rows:

small_eval = dataset["validation"].select(range(min(5, len(dataset["validation"]))))
Then:

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=small_eval,
    formatting_func=formatting_prompts_func,
    args=sft_config
)

eval_results = trainer.evaluate()
print(eval_results)
For now, if the cell is running and no error appears, let it continue.
its over 15 minuts and the uploading of adopters is still running is there a problem
Friday 6:35 PM

Maybe. For a LoRA adapter it usually should not take that long. Stop the cell and use a manual save + upload. It is more reliable on Kaggle.

1. Stop the current upload cell

Click stop.

2. Save adapter locally

SAVE_DIR = "/kaggle/working/africa-giants-adapter"

trainer.model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)

print("Saved adapter locally:", SAVE_DIR)
3. Check file sizes

import os

for root, dirs, files in os.walk(SAVE_DIR):
    for file in files:
        path = os.path.join(root, file)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"{path} - {size_mb:.2f} MB")
You should see something like:

adapter_model.safetensors
adapter_config.json
tokenizer.json
4. Upload folder manually

from huggingface_hub import upload_folder

upload_folder(
    folder_path=SAVE_DIR,
    repo_id=ADAPTER_REPO,
    repo_type="model",
    token=hf_token,
    commit_message="Upload Africa Giants LoRA adapter"
)

print("Uploaded adapter:", ADAPTER_REPO)
5. Check repo

Open:

https://huggingface.co/prospAprospA007/africa-giants-adapter-v1
If manual upload also hangs, upload only the required files:

from huggingface_hub import upload_file
import os

for filename in os.listdir(SAVE_DIR):
    path = os.path.join(SAVE_DIR, filename)
    if os.path.isfile(path):
        print("Uploading:", filename)
        upload_file(
            path_or_fileobj=path,
            path_in_repo=filename,
            repo_id=ADAPTER_REPO,
            repo_type="model",
            token=hf_token
        )

print("Uploaded files one by one")




Friday 6:35 PM
SAVE_DIR = "/kaggle/working/africa-giants-adapter"

trainer.model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)

print("Saved adapter locally:", SAVE_DIR) DOSE THIS TAKE TIME
Friday 6:39 PM

Yes, it can take time, but usually not very long.

For a LoRA adapter, expect:

30 seconds to 5 minutes
It uses mostly:

CPU
RAM
disk write
So GPU activity may be zero. That is normal.

It is saving files like:

adapter_model.safetensors
adapter_config.json
tokenizer.json
tokenizer_config.json
special_tokens_map.json
If it takes more than 10 minutes, something may be stuck. Then stop it and try saving only the adapter:

SAVE_DIR = "/kaggle/working/africa-giants-adapter"

model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)

print("Saved adapter locally:", SAVE_DIR)
After it finishes, check files:

import os

for file in os.listdir(SAVE_DIR):
    path = os.path.join(SAVE_DIR, file)
    print(file, round(os.path.getsize(path) / (1024 * 1024), 2), "MB")




Friday 6:39 PM
After uploading whats next
Friday 6:46 PM

After uploading the adapter, do these next:

1. Confirm Files On Hugging Face

Open:

https://huggingface.co/prospAprospA007/africa-giants-adapter-v1
You should see:

adapter_config.json
adapter_model.safetensors
tokenizer_config.json
special_tokens_map.json
tokenizer.json or tokenizer.model
2. Test Loading The Adapter

In a new Kaggle cell:

from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

BASE_MODEL = "McGill-NLP/AfriqueLlama-8B"
ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v1"

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_REPO, token=hf_token)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=hf_token,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_REPO,
    token=hf_token
)

model.eval()
print("Adapter loaded successfully")
3. Test A Swahili Business Question

prompt = "Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?"

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
4. Increase Real Training

Your first training was only 10 steps. Next run should be:

max_steps=100
Then later:

max_steps=500
Only increase after the adapter loading test works.

5. Build Better Dataset

Add more data from:

TRA
BRELA
business.go.tz
NBS
BoT
TIC
NBAA
TBS
TMDA
marketplaces
manual Swahili business Q&A
6. Connect To The App

Once adapter works, update your app/model config:

BASE_MODEL = McGill-NLP/AfriqueLlama-8B
ADAPTER_REPO = prospAprospA007/africa-giants-adapter-v1
Then deploy it through Hugging Face Space or your FastAPI server.

Immediate next step: test loading the adapter from Hugging Face.
HE ANSWER ISINT APROPREATE BECAUSE THE DATA SET WAS SMALL OR WHATNina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja? | JamiiForums | The Home of Great Thinkers 
Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?
Discussion in 'Biashara, Uchumi na Siasa' started by Mwakaboko, Apr 19, 2012.
Mwakaboko
Nina duka dogo la kuuza bidhaa za rejareja, nimekuwa nikifanya biashara hii kwa muda mrefu lakini sijafanikiwa kufanya biashara kwa faida kubwa. Nimekuwa nikifanya biashara kwa faida ndogo sana. Sasa nataka kujua ni njia gani nzuri ya kufanya biashara hii kwa faida 
Friday 6:54 PM

Yes, mainly because of two things:

1. The dataset was too small

You trained only a tiny smoke-test dataset for 10 steps. That proves the pipeline works, but it does not teach strong business-answer behavior yet.

So the model is still mostly behaving like the base model.

2. Your prompt/output looks like scraped forum text

The answer you got looks like the model is continuing a web/forum page:

Nina duka dogo Tanzania... | JamiiForums | The Home of Great Thinkers
Discussion in...
That usually means the training data included raw scraped text without enough clean assistant-style answers.

For fine-tuning, do not train mostly on raw web pages. Convert them into clean instruction answers.

Bad training format:

JamiiForums | Discussion started by...
Good training format:

{
  "instruction": "Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?",
  "input": "",
  "output": "Anza kwa kutenganisha fedha za biashara na binafsi. Andika mauzo ya kila siku, matumizi, bidhaa zilizoingia na kutoka, madeni ya wateja, na malipo ya wasambazaji..."
}
What To Do Next

Create a better Swahili dataset with 200 to 1000 clean examples.

Include categories:

bookkeeping
tax
BRELA registration
business license
marketing
customer service
pricing
inventory
cash flow
sales strategy
supplier management
employee management
Example row:

{
  "instruction": "Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?",
  "input": "",
  "output": "Kwa duka dogo, anza na mfumo rahisi wa kila siku. Andika mauzo yote, bidhaa zilizouzwa, bidhaa zilizoingia, matumizi, madeni ya wateja, na malipo ya wasambazaji. Tenganisha fedha za biashara na matumizi binafsi. Kila mwisho wa wiki angalia bidhaa zinazouza sana na ongeza stoo yake. Kupata wateja zaidi, tumia WhatsApp Business, weka picha za bidhaa, toa ofa ndogo kwa bidhaa zinazotembea, omba wateja wakurudie maoni, na tangaza eneo lako kupitia Google Business Profile na mitandao ya kijamii."
}
Also change generation prompt to instruction style:

prompt = """<|im_start|>system
Wewe ni Africa Giants, mshauri wa biashara Tanzania. Jibu kwa Kiswahili rahisi, toa hatua za vitendo, na usibuni taarifa za kodi au sheria bila chanzo rasmi.<|im_end|>
<|im_start|>user
Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri na kuongeza wateja?<|im_end|>
<|im_start|>assistant
"""
Then generate:

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=220,
        temperature=0.2,
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
Best Next Move

Do not train more yet on the same tiny dataset. First build a clean dataset.

Target:

Minimum useful: 200 examples
Good first version: 1000 examples
Strong version: 5000+ examples
Your pipeline works. Now the quality problem is the data, not the training code.





Friday 6:54 PM
Well it seames like its about to work but one thing is that this is not automated and we have the repo for that what should we do 
Friday 6:56 PM

Exactly. You proved the hard part: model loads, training runs, adapter can be produced. Now the next job is to stop doing it manually in Kaggle cells and connect the repo pipeline so it becomes repeatable.

What we should do next is turn the repo into an automated loop:

scrape data
→ clean data
→ generate clean Q&A
→ push dataset to HF
→ trigger Kaggle training
→ push adapter to HF
→ evaluate adapter
→ deploy/reload server
→ collect feedback
Immediate Plan

Improve the repo dataset builder
Update the repo so it creates clean assistant-style examples, not raw forum/web continuations.

Update the Kaggle notebook
Make it read only from:

prospAprospA007/africa-giants-dataset
and push only to:

prospAprospA007/africa-giants-adapter-v1
Add Kaggle automation
Use Kaggle API from the repo:
python run.py train
That should upload/update the dataset and trigger the Kaggle notebook.

Add evaluation
After training, run:
python run.py evaluate
Deploy only if evaluation passes
If score improves, update the adapter/model repo and reload the app.
What To Build In The Repo Next

Add/fix these files:

src/process/build_instruction_dataset.py
src/synthetic/generate_business_qa.py
src/orchestrator/upload_dataset_hf.py
src/orchestrator/trigger_kaggle.py
src/evaluate/test_adapter.py
And make CLI commands:

python run.py build-dataset
python run.py upload-dataset
python run.py train-kaggle
python run.py evaluate
python run.py deploy
Automation Workflow

The repo should become the control center:

Local/GitHub repo = orchestration and data pipeline
Kaggle = GPU training worker
Hugging Face = dataset/model/app registry
Kaggle should not be where you manually write every step. Kaggle should only run the notebook when triggered.

Best Next Step

We should now update the repo to create a proper clean Swahili/English instruction dataset automatically.

The biggest fix is this:

raw scraped data should go to RAG
clean Q&A examples should go to fine-tuning
Do not fine-tune on raw forum pages.

Fine-tuning dataset should look like:

{
  "instruction": "Nina duka dogo Tanzania. Nawezaje kuweka hesabu vizuri?",
  "input": "",
  "output": "Anza kwa kuandika mauzo ya kila siku..."
}
RAG dataset should keep:

TRA pages
BRELA pages
NBS reports
business.go.tz pages
Then the app uses:

RAG for official knowledge
LoRA for business-coach behavior
So yes: it is close. Now we automate the repo so one command can refresh data, train, evaluate, and deploy.





Friday 6:56 PM
go ahead and complete the task and also screap the forums for a massive  training data first then later make the screaping for rag
Friday 7:01 PM


I’ll turn the repo toward that workflow now: forum scraping for training-data candidates, cleaning into assistant-style Q&A instead of raw forum continuations, HF dataset upload, and CLI commands to run it. I’ll inspect the current scraper/orchestrator first, then patch the pipeline and push it.

Searched web 1 time
The existing pipeline already scrapes official/mock sources and generates simple Q&A, but it is not optimized for forum-style market pain points. I’m adding a separate “forum training data” pipeline so raw discussions become clean coaching examples instead of the model learning to imitate forum pages.

Searched web 1 time
I’m going to make the first automation stage forum-focused but safe: it will crawl public forum listing pages with limits/delays, extract thread titles and posts, then convert them into training examples where the assistant gives practical business advice. The RAG scraper stays separate for later official-source grounding.

Created 3 files
The forum collection and conversion modules are now in place. I’m wiring them into run.py so you can run one command for forum scraping, another for building the fine-tuning dataset, and another for uploading that dataset to Hugging Face before Kaggle training.

Edited 1 file
I’m going to validate the new commands without doing a huge internet scrape yet. First I’ll build the dataset from any existing forum data plus clean manual seed examples, then I’ll test the Python modules compile.

The local dataset builder works and produces clean SFT rows. I’m going to try a small live forum scrape now using the configured public source; if the site blocks crawling or the URL needs adjustment, I’ll keep the automation code and report the exact blocker rather than fabricating scraped data.

The first live scrape reached the forum, but the local environment lacks the lxml parser, so BeautifulSoup refused to parse. I’m switching the forum scraper to Python’s built-in html.parser fallback so it works without extra installs.

Edited 1 file
The scraper code is fixed, but the environment blocked the second live network scrape because the session hit its execution/approval limit. I’ll still finish the repo automation and push it; once you run python run.py scrape-forums --build-dataset --upload from your machine or CI with internet, it will perform the scrape and prepare the HF dataset.

Edited 1 file

Edited 4 files
+402
-15
Undo
Review
config/forums.yaml
src/collect/forum_scraper.py
src/process/build_instruction_dataset.py)))))
--- CODEX WORK ENDS HERE ---


