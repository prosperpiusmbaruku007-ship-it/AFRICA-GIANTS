import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Chike - Wappfly Webhook")

WAPPFLY_TOKEN    = os.environ.get("WAPPFLY_TOKEN", "")
MODAL_API_TOKEN  = os.environ.get("MODAL_API_TOKEN", "")
MODAL_URL        = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
WAPPFLY_SEND_URL = "https://wappfly.com/api/messages/send"

GREETINGS = {
    "habari","hujambo","mambo","hello","hi","hey",
    "salaam","salam","start","help","msaada",
    "chike","karibu",
}

WELCOME = (
    "Habari! Karibu sana. 🙏\n\n"
    "Mimi ni *Chike* — mshauri wako wa biashara\n"
    "kutoka *Africa Giants*.\n"
    "_Fahamu Biashara Yako, Maarifa Yako._\n\n"
    "Ninakusaidia na:\n"
    "• Kodi — VAT, PAYE, SDL, EFD\n"
    "• Usajili — BRELA, TRA, NSSF, OSHA\n"
    "• Sheria — GN 487A, vibali, leseni\n"
    "• Mishahara — GN 605A, WCF\n\n"
    "Uliza swali lako sasa hivi. 👇\n\n"
    "---\n\n"
    "Hello! Welcome. 🙏\n\n"
    "I am *Chike* — your business adviser\n"
    "from *Africa Giants*.\n"
    "_Understand Your Business, That Knowledge Is Yours._\n\n"
    "I can help with:\n"
    "• Tax — VAT, PAYE, SDL, EFD\n"
    "• Registration — BRELA, TRA, NSSF, OSHA\n"
    "• Law — GN 487A, permits, licences\n"
    "• Wages — GN 605A, WCF\n\n"
    "Ask your question now. 👇\n\n"
    "---\n"
    "_⚠ Beta: thibitisha majibu muhimu na TRA._\n"
    "_⚠ Beta: verify important answers with TRA._"
)

FALLBACK = (
    "Samahani, Chike hakuweza kukusaidia sasa hivi. "
    "Tafadhali jaribu tena baadaye.\n\n"
    "Sorry, Chike could not help right now. "
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

async def call_modal(message: str) -> str:
    # timeout 180s: Modal cold starts (~100-216s) exceed the old 120s and would FALLBACK
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            MODAL_URL,
            params={"token": MODAL_API_TOKEN},
            headers={"Content-Type": "application/json"},
            json={"message": message},
        )
        result = response.json()
        return result.get("reply", FALLBACK)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()

        # Only handle incoming messages
        event = body.get("event", "")
        if event != "messages.received":
            return JSONResponse({"status": "ignored"})

        messages = body.get("data", {}).get("messages", {})

        # Skip messages sent by us
        if messages.get("fromMe") or messages.get("key", {}).get("fromMe"):
            return JSONResponse({"status": "ignored"})

        # Extract message text
        text = (
            messages.get("conversation") or
            messages.get("messageBody") or
            messages.get("text") or ""
        ).strip()

        # Extract sender JID
        sender = (
            messages.get("remoteJid") or
            messages.get("key", {}).get("remoteJid") or ""
        )

        if not text or not sender:
            print(f"[chike] No text or sender found — ignoring")
            return JSONResponse({"status": "ignored"})

        print(f"[chike] From: {sender} — {text[:80]}")

        if text.lower() in GREETINGS:
            asyncio.create_task(send_whatsapp(sender, WELCOME))
        else:
            async def respond():
                reply = await call_modal(text)
                await send_whatsapp(sender, reply)
            asyncio.create_task(respond())

        return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"[webhook] Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"status": "error"}, status_code=200)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "product": "Chike by Africa Giants",
        "tagline": "Fahamu Biashara Yako, Maarifa Yako",
    }
