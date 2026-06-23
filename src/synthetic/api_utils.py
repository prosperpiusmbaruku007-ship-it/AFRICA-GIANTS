import json
import os
import time
from datetime import datetime

import requests

# === Provider configuration ===
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openrouter')

if LLM_PROVIDER == 'anthropic':
    BASE_URL      = 'https://api.anthropic.com/v1'
    API_KEY       = os.environ.get('ANTHROPIC_API_KEY')
    DEFAULT_MODEL = 'claude-sonnet-4-6'
    HEADERS = {
        'x-api-key':           API_KEY or '',
        'anthropic-version':   '2023-06-01',
        'content-type':        'application/json',
    }

elif LLM_PROVIDER == 'openrouter':
    BASE_URL      = 'https://openrouter.ai/api/v1'
    API_KEY       = os.environ.get('OPENROUTER_API_KEY')
    DEFAULT_MODEL = os.environ.get('OPENROUTER_MODEL', 'google/gemini-2.5-flash-lite')
    HEADERS = {
        'Authorization': f'Bearer {API_KEY or ""}',
        'Content-Type':  'application/json',
        'HTTP-Referer':  'https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS',
        'X-Title':       'Africa Giants Chike AI',
    }

elif LLM_PROVIDER == 'ollama':
    BASE_URL      = 'http://localhost:11434/api'
    API_KEY       = 'ollama'
    DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
    HEADERS       = {'Content-Type': 'application/json'}

else:
    raise ValueError(
        f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Valid values: anthropic | openrouter | ollama"
    )

# Cost per token — only Anthropic charges per token; free-tier providers treated as $0
COST_PER_INPUT_TOKEN  = 0.000003 if LLM_PROVIDER == 'anthropic' else 0.0
COST_PER_OUTPUT_TOKEN = 0.000015 if LLM_PROVIDER == 'anthropic' else 0.0

COST_LOG_PATH = 'data/cost_log.jsonl'

_KEY_VAR = {
    'anthropic':  'ANTHROPIC_API_KEY',
    'openrouter': 'OPENROUTER_API_KEY',
    'ollama':     None,
}
_KEY_URL = {
    'anthropic':  'console.anthropic.com',
    'openrouter': 'openrouter.ai',
    'ollama':     None,
}


# === Normalised response — callers always use response.content[0].text ===

class _Content:
    __slots__ = ('text',)
    def __init__(self, text: str):
        self.text = text

class _Usage:
    __slots__ = ('input_tokens', 'output_tokens')
    def __init__(self, input_tokens: int, output_tokens: int):
        self.input_tokens  = input_tokens
        self.output_tokens = output_tokens

class NormalizedResponse:
    def __init__(self, text: str, input_tokens: int = 0, output_tokens: int = 0):
        self.content = [_Content(text)]
        self.usage   = _Usage(input_tokens, output_tokens)


# === Provider check ===

def check_provider():
    """Print provider/model/key status. Call once before a generate run."""
    print(f"[api] Provider: {LLM_PROVIDER}")
    print(f"[api] Model:    {DEFAULT_MODEL}")
    if LLM_PROVIDER == 'ollama':
        print("[api] API key:  not required (local)")
        return
    key_var = _KEY_VAR.get(LLM_PROVIDER, 'API_KEY')
    if API_KEY:
        print("[api] API key:  present")
    else:
        key_url = _KEY_URL.get(LLM_PROVIDER, '')
        print(f"[api] ERROR: {key_var} not set")
        print(f"[api] Set it with: $env:{key_var}='your-key-here'")
        if key_url:
            print(f"[api] Get a free key at: {key_url}")


# === HTTP request builder ===

def _make_request(model: str, max_tokens: int,
                  messages: list, system: str = None) -> NormalizedResponse:
    if LLM_PROVIDER == 'anthropic':
        payload = {'model': model, 'max_tokens': max_tokens, 'messages': messages}
        if system:
            payload['system'] = system
        r = requests.post(
            f"{BASE_URL}/messages", headers=HEADERS, json=payload, timeout=120
        )
        r.raise_for_status()
        data          = r.json()
        text          = data['content'][0]['text']
        input_tokens  = data.get('usage', {}).get('input_tokens',  0)
        output_tokens = data.get('usage', {}).get('output_tokens', 0)

    elif LLM_PROVIDER == 'openrouter':
        full_messages = []
        if system:
            full_messages.append({'role': 'system', 'content': system})
        full_messages.extend(messages)
        payload = {'model': model, 'max_tokens': max_tokens, 'messages': full_messages}
        r = requests.post(
            f"{BASE_URL}/chat/completions", headers=HEADERS, json=payload, timeout=120
        )
        r.raise_for_status()
        data          = r.json()
        text          = data['choices'][0]['message']['content']
        input_tokens  = data.get('usage', {}).get('prompt_tokens',     0)
        output_tokens = data.get('usage', {}).get('completion_tokens', 0)

    elif LLM_PROVIDER == 'ollama':
        user_parts = [m.get('content', '') for m in messages if m.get('role') == 'user']
        prompt     = ((system + '\n\n') if system else '') + '\n'.join(user_parts)
        payload    = {'model': model, 'prompt': prompt, 'stream': False}
        r = requests.post(
            f"{BASE_URL}/generate", headers=HEADERS, json=payload, timeout=300
        )
        r.raise_for_status()
        data          = r.json()
        text          = data.get('response', '')
        input_tokens  = data.get('prompt_eval_count', 0)
        output_tokens = data.get('eval_count',        0)

    return NormalizedResponse(text, input_tokens, output_tokens)


# === Retry wrapper ===

def call_api_with_retry(model: str = None, max_tokens: int = 1024,
                        messages: list = None, system: str = None,
                        **_ignored) -> NormalizedResponse:
    """
    Provider-agnostic API call with exponential backoff.
    Accepts Anthropic-style kwargs: model, max_tokens, messages, system.
    Returns NormalizedResponse so callers always use response.content[0].text.
    """
    model    = model    or DEFAULT_MODEL
    messages = messages or []

    for attempt in range(3):
        try:
            return _make_request(model, max_tokens, messages, system)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status in (401, 402, 403, 404, 422):
                if status == 402:
                    raise Exception(
                        '[api] Payment Required (402) -- add credits at '
                        'openrouter.ai/billing or platform.anthropic.com'
                    )
                raise  # auth / permission / not-found — never retry
            if attempt == 2:
                raise
            wait = 60 * (2 ** attempt)
            print(f"[api] HTTP {status} -- retrying in {wait}s ({attempt + 2}/3)")
            time.sleep(wait)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if attempt == 2:
                raise
            wait = 60 * (2 ** attempt)
            print(f"[api] {type(e).__name__} -- retrying in {wait}s ({attempt + 2}/3)")
            time.sleep(wait)


# === Cost tracking ===

def log_cost(script_name: str, tokens_in: int, tokens_out: int, cost_usd: float):
    entry = {
        "timestamp":  datetime.utcnow().isoformat(),
        "script":     script_name,
        "provider":   LLM_PROVIDER,
        "model":      DEFAULT_MODEL,
        "tokens_in":  tokens_in,
        "tokens_out": tokens_out,
        "cost_usd":   round(cost_usd, 6),
    }
    with open(COST_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def call_with_cost_tracking(script_name: str, **kwargs) -> NormalizedResponse:
    """Call call_api_with_retry and log cost. Always uses try/finally so cost is logged even on error."""
    response = None
    try:
        response = call_api_with_retry(**kwargs)
        return response
    finally:
        if response is not None:
            cost = (response.usage.input_tokens  * COST_PER_INPUT_TOKEN +
                    response.usage.output_tokens * COST_PER_OUTPUT_TOKEN)
            log_cost(script_name,
                     response.usage.input_tokens,
                     response.usage.output_tokens,
                     cost)


def sum_cost_log_this_month() -> float:
    month_str = datetime.utcnow().strftime('%Y-%m')
    total = 0.0
    try:
        with open(COST_LOG_PATH, encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('timestamp', '').startswith(month_str):
                        total += entry.get('cost_usd', 0.0)
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return total
