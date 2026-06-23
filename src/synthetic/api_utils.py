import json
import time
from datetime import datetime

RETRY_ON = {
    'RateLimitError', 'APIConnectionError', 'APITimeoutError',
    'ConnectError', 'TimeoutError', 'ConnectionError',
}
RAISE_ON = {
    'AuthenticationError', 'PermissionDeniedError',
    'InvalidRequestError', 'NotFoundError',
}

COST_PER_INPUT_TOKEN  = 0.000003   # claude-sonnet-4-6: $3/M input
COST_PER_OUTPUT_TOKEN = 0.000015   # claude-sonnet-4-6: $15/M output

COST_LOG_PATH = 'data/cost_log.jsonl'


def call_api_with_retry(client, **kwargs):
    for attempt in range(3):
        try:
            return client.messages.create(**kwargs)
        except Exception as e:
            err_type = type(e).__name__
            if err_type in RAISE_ON:
                raise
            if attempt == 2:
                raise
            if err_type in RETRY_ON or 'error' in err_type.lower():
                wait = 60 * (2 ** attempt)  # 60s, 120s
                print(f"[api] {err_type} -- retrying in {wait}s ({attempt + 2}/3)")
                time.sleep(wait)
            else:
                raise


def log_cost(script_name: str, tokens_in: int, tokens_out: int, cost_usd: float):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script":     script_name,
        "tokens_in":  tokens_in,
        "tokens_out": tokens_out,
        "cost_usd":   round(cost_usd, 6),
    }
    with open(COST_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def call_with_cost_tracking(client, script_name: str, **kwargs):
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
