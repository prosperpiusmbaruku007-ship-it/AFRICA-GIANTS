# Chike by Africa Giants — Twilio Function

Connects Twilio WhatsApp sandbox to Chike inference
on Cerebrium.

## Setup in Twilio Console

1. Go to Functions & Assets → Services
2. Create new Service: chike-whatsapp
3. Add new Function: /chike-whatsapp
4. Paste contents of chike-whatsapp.js
5. Add dependency: axios (in Dependencies tab)
6. Add environment variable:
   CEREBRIUM_API_KEY = your cerebrium api key
7. Deploy the service
8. Copy the function URL
9. Go to Messaging → WhatsApp sandbox settings
10. Set webhook URL to the function URL

## Environment Variables

CEREBRIUM_API_KEY — from Cerebrium dashboard
                    Settings → API Keys

## Endpoint

Cerebrium: https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run
