import discord
import os
import time
import requests
import re
from twilio.rest import Client

# --- ENV VARIABLES ---
TOKEN = os.getenv("TOKEN")

SOURCE_CHANNELS = [int(x) for x in os.getenv("SOURCE_CHANNELS", "").split(",") if x]

CHANNEL_A = int(os.getenv("CHANNEL_A"))
CHANNEL_B = int(os.getenv("CHANNEL_B"))

CALL_CHANNEL_A = int(os.getenv("CALL_CHANNEL_A"))
CALL_CHANNEL_B = int(os.getenv("CALL_CHANNEL_B"))

PHONE_A = os.getenv("PHONE_A")
PHONE_B = os.getenv("PHONE_B")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

WEBHOOK_A = os.getenv("WEBHOOK_A")
WEBHOOK_B = os.getenv("WEBHOOK_B")
DEBUG_WEBHOOK = os.getenv("DEBUG_WEBHOOK")
WEBHOOK_CHECKOUT = os.getenv("WEBHOOK_CHECKOUT")

# --- TWILIO SETUP ---
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# --- COOLDOWN ---
last_call_times = {}

def can_call(channel_id):
    now = time.time()
    last = last_call_times.get(channel_id, 0)

    if now - last >= 60:
        last_call_times[channel_id] = now
        return True
    return False

def make_call(phone_number):
    twilio_client.calls.create(
        to=phone_number,
        from_=TWILIO_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml"
    )

# --- DISCORD SETUP ---
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):

    # --- PARSE WEBHOOK EMBEDS ---
    if message.channel.id in SOURCE_CHANNELS:
        text = ""

        if message.embeds:
            for embed in message.embeds:
                if embed.title:
                    text += embed.title + " "
                if embed.description:
                    text += embed.description + " "
                for field in embed.fields:
                    text += field.name + " " + field.value + " "
        else:
            text = message.content

        text = text.strip()
        text_ci = text.lower()
        

        if not text:
            return

        # --- DEBUG OUTPUT ---
        if DEBUG_WEBHOOK:
            requests.post(DEBUG_WEBHOOK, json={
                "content": text,
                "username": "RelayBot Debug"
            })

        # --- EXTRACT AMAZON DATA ---
        asin_match = re.search(r"asin\s*([a-zA-Z0-9]{10})", text, re.IGNORECASE)

        # find the LONG encoded string after "offer id"
        offer_match = re.search(r"offer\s*id\s*[\r\n\s`:=]+([a-zA-Z0-9%]+)", text, re.IGNORECASE)

        asin = asin_match.group(1) if asin_match else None
        offer_id = offer_match.group(1) if offer_match else None

        if asin and offer_id and WEBHOOK_CHECKOUT:
            buy_now_url = f"https://www.amazon.co.uk/checkout/entry/buynow?asin={asin}&offeringID={offer_id}&pipelineType=Chewbacca&quantity=1&buyNow"

            requests.post(WEBHOOK_CHECKOUT, json={
                "content": f"🚀 CHECKOUT LINK READY 🚀 <@409121609333604355> <@409826137645252609>\n{buy_now_url}",
                "username": "RelayBot Checkout",
                "allowed_mentions": {
                    "users": ["409121609333604355", "409826137645252609"]
                }
            })

        # --- KEYWORD LOGIC ---
        has_3ds = "3ds" in text_ci
        has_evan = "evan" in text_ci
        has_jaden = "jaden" in text_ci

        # --- ROUTING ---
        if has_3ds and has_evan:
            print("Matched EVAN alert")
            requests.post(WEBHOOK_B, json={
                "content": "<@409121609333604355> 🚨 3DS ALERT 🚨",
                "username": "RelayBot"
            })

        if has_3ds and has_jaden:
            print("Matched JADEN alert")
            requests.post(WEBHOOK_A, json={
                "content": "<@409826137645252609> 🚨 3DS ALERT 🚨",
                "username": "RelayBot"
            })

    # --- CALL LOGIC (UNCHANGED) ---
    channel_id = message.channel.id

    if channel_id == CALL_CHANNEL_A:
        if can_call(channel_id):
            print("Calling Phone A")
            make_call(PHONE_A)

    elif channel_id == CALL_CHANNEL_B:
        if can_call(channel_id):
            print("Calling Phone B")
            make_call(PHONE_B)

client.run(TOKEN)
