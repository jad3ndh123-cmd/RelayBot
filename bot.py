import requests
import discord
import os
import time
from twilio.rest import Client

# --- ENV VARIABLES ---
TOKEN = os.getenv("TOKEN")

SOURCE_CHANNELS = [int(x) for x in os.getenv("SOURCE_CHANNELS", "").split(",") if x]
OUTPUT_CHANNEL = int(os.getenv("OUTPUT_CHANNEL"))

CALL_CHANNEL_A = int(os.getenv("CALL_CHANNEL_A"))
CALL_CHANNEL_B = int(os.getenv("CALL_CHANNEL_B"))

PHONE_A = os.getenv("PHONE_A")
PHONE_B = os.getenv("PHONE_B")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

# --- TWILIO SETUP ---
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# --- COOLDOWN TRACKING ---
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
    # --- RELAY (webhook embeds → text → YAG) ---
    if message.channel.id in SOURCE_CHANNELS and message.embeds:
        text = ""

        for embed in message.embeds:
            if embed.title:
                text += embed.title + " "
            if embed.description:
                text += embed.description + " "
            for field in embed.fields:
                text += field.name + " " + field.value + " "

        text = text.lower().strip()

        if text:
            out = client.get_channel(OUTPUT_CHANNEL)
            WEBHOOK_URL = os.getenv("OUTPUT_WEBHOOK")  requests.post(WEBHOOK_URL, json={     "content": text,     "username": "RelayBot" })

    # --- CALL TRIGGERS (ANY message in channel) ---
    channel_id = message.channel.id

    if channel_id == CALL_CHANNEL_A:
        if can_call(channel_id):
            print("Calling Phone A")
            make_call(PHONE_A)

    elif channel_id == CALL_CHANNEL_B:
        if can_call(channel_id):
            print("Calling Phone B")
            make_call(PHONE_B)

# --- RUN BOT ---
client.run(TOKEN)
