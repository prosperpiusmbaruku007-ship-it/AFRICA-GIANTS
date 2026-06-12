# Chike by Africa Giants — WhatsApp Inference Server

FastAPI server that connects Twilio WhatsApp to the
Chike AI adapter (adapter-v3, 1,650 training pairs).

## How it works

1. User sends a WhatsApp message to the Twilio number
2. Twilio forwards it to POST /webhook
3. Chike runs inference using adapter-v3
4. Response goes back through Twilio to the user

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Product info |
| /health | GET | Model status |
| /webhook | POST | Twilio webhook |

## Environment variables

| Variable | Description |
|----------|-------------|
| HF_TOKEN | HuggingFace token with access to adapter-v3 |
| PORT | Set automatically by Railway |

## Local development

pip install -r server/requirements.txt
export HF_TOKEN=your_token
uvicorn server.app:app --reload --port 8000

Then test health:
curl http://localhost:8000/health

## Logs

Every conversation is logged to:
server/logs/conversations.jsonl

Fields: timestamp, phone_hash (privacy),
question, answer, duration_ms, was_greeting, product
