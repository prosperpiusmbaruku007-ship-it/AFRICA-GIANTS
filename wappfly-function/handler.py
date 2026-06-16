import os
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Chike - Wappfly Webhook")

WAPPFLY_TOKEN    = os.environ.get("WAPPFLY_TOKEN", "")
CEREBRIUM_KEY    = os.environ.get("CEREBRIUM_KEY", "")
CEREBRIUM_URL    = "https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run"
WAPPFLY_SEND_URL = "https://wappfly.com/api/messages/send"

GREETINGS = {
    "habari","hujambo","mambo","hello","hi","hey",
    "salaam","salam","start","help","msaada",
    "chike","karibu",
}

WELCOME = (
    "🌍 *Chike* — mshauri wako wa biashara Tanzania.\n"
    "_Fahamu Biashara Yako, Maarifa Yako._\n\n"
    "Ninajibu maswali yote ya biashara kwa sekunde chache:\n\n"
    "💰 *Kodi* — VAT · PAYE · SDL · WHT · EFD\n"
    "📋 *Usajili* — BRELA · TRA · NSSF · OSHA · WCF\n"
    "⚖️ *Sheria* — GN 487A · Vibali · Leseni\n"
    "📊 *Mishahara* — GN 605A · SDL · WCF\n\n"
    "Uliza swali lolote sasa hivi. 👇\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌍 *Chike* — your Tanzanian business adviser.\n"
    "_Understand Your Business, That Knowledge Is Yours._\n\n"
    "I answer all business questions in seconds:\n\n"
    "💰 *Tax* — VAT · PAYE · SDL · WHT · EFD\n"
    "📋 *Registration* — BRELA · TRA · NSSF · OSHA · WCF\n"
    "⚖️ *Law* — GN 487A · Permits · Licences\n"
    "📊 *Wages* — GN 605A · SDL · WCF\n\n"
    "Ask me anything right now. 👇\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⚠️ _Chike iko katika awamu ya majaribio (beta)._\n"
    "_Thibitisha majibu muhimu na TRA au mshauri wa kodi._\n\n"
    "⚠️ _Chike is in beta. Always verify important_\n"
    "_answers with TRA or a qualified adviser._"
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
                reply = await call_cerebrium(text)
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
