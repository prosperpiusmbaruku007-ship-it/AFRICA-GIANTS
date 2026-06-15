# Chike — Wappfly Webhook

Receives WhatsApp messages from Wappfly,
calls Cerebrium, sends reply back via Wappfly.

## Environment variables needed

WAPPFLY_TOKEN = your Wappfly X-API-Token
CEREBRIUM_KEY = your full Cerebrium API key

## Deploy to Railway

Railway detects FastAPI automatically.
Set the start command to:
uvicorn wappfly-function.handler:app --host 0.0.0.0 --port $PORT

## Local test

pip install -r wappfly-function/requirements.txt
export WAPPFLY_TOKEN=your_token
export CEREBRIUM_KEY=your_key
uvicorn wappfly-function.handler:app --reload --port 8000

curl http://localhost:8000/health
