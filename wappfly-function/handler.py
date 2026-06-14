import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Chike Brain - Wappfly Webhook")

WAPPFLY_TOKEN    = os.environ.get("WAPPFLY_TOKEN", "")
CEREBRIUM_KEY    = os.environ.get("CEREBRIUM_KEY", "")
CEREBRIUM_URL    = "https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run"
WAPPFLY_SEND_URL = "https://wappfly.com/api/messages/send"

GREETINGS = {
    "habari","hujambo","mambo","hello","hi","hey",
    "salaam","salam","start","help","msaada",
    "chike","chike brain","chikebrain","karibu",
}

WELCOME = (
    "Habari! Mimi ni *Chike Brain* kutoka *Africa Giants*.\n\n"
    "_Fahamu Biashara Yako, Maarifa Yako._\n\n"
    "Ninakusaidia na maswali ya biashara Tanzania:\n"
    "• Kodi (VAT, PAYE, SDL, WHT)\n"
    "• Usajili (BRELA, TRA, NSSF, OSHA, WCF)\n"
    "• Sheria za biashara (GN 487A, vibali)\n\n"
    "Uliza swali lolote. Ninajibu kwa Kiswahili na Kiingereza.\n\n"
    "---\n\n"
    "Hi! I am *Chike Brain* from *Africa Giants*.\n\n"
    "_Understand Your Business, That Knowledge Is Yours._\n\n"
    "Ask me anything about Tanzanian business, tax, or compliance."
)

FALLBACK = (
    "Samahani, Chike Brain hakuweza kukusaidia sasa hivi. "
    "Tafadhali jaribu tena baadaye.\n\n"
    "Sorry, Chike Brain could not help right now. "
    "Please try again shortly."
)

async def send_whatsapp(to: str, text: str):
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            WAPPFLY_SEND_URL,
            headers={
                "X-API-Token": WAPPFLY_TOKEN,
                "Content-Type": "application/json",
            },
            json={"to": to, "text": text},
        )

async def call_cerebrium(message: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            CEREBRIUM_URL,
            headers={
                "Authorization": f"Bearer {CEREBRIUM_KEY}",
                "Content-Type": "application/json",
            },
            json={"message": message},
        )
        result = response.json()
        return result.get("result", {}).get("reply", FALLBACK)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        import json
        print(f"[wappfly] Full payload: {json.dumps(body, indent=2)}")
        print(f"[wappfly] Keys: {list(body.keys())}")
        if "data" in body:
            print(f"[wappfly] Data keys: {list(body['data'].keys())}")

        # Extract message and sender from Wappfly payload
        message_data = body.get("data", body)
        text = (
            message_data.get("text") or
            message_data.get("body") or
            message_data.get("message") or ""
        ).strip()

        sender = (
            message_data.get("from") or
            message_data.get("sender") or ""
        )

        if not text or not sender:
            return JSONResponse({"status": "ignored"})

        # Skip messages sent by us
        if message_data.get("fromMe") or message_data.get("from_me"):
            return JSONResponse({"status": "ignored"})

        print(f"[chike] From: {sender} — {text[:80]}")

        if text.lower() in GREETINGS:
            asyncio.create_task(send_whatsapp(sender, WELCOME))
        else:
            async def respond():
                reply = await call_cerebrium(text)
                await send_whatsapp(sender, reply)
            asyncio.create_task(respond())

        return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"[webhook] Error: {e}")
        return JSONResponse({"status": "error"}, status_code=200)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "product": "Chike Brain by Africa Giants",
        "tagline": "Fahamu Biashara Yako, Maarifa Yako",
    }
