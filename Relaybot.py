import discord
import os

TOKEN = os.getenv("TOKEN")
SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
OUTPUT_CHANNEL = int(os.getenv("OUTPUT_CHANNEL"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != SOURCE_CHANNEL:
        return

    # Only process webhook messages
    if message.webhook_id is None:
        return

    text = ""

    for embed in message.embeds:
        if embed.title:
            text += embed.title + " "
        if embed.description:
            text += embed.description + " "

        for field in embed.fields:
            text += field.name + " " + field.value + " "

    text = text.lower().strip()

    # 🔥 YOUR KEYWORD LOGIC HERE
    if "3ds" in text and "evan mum" in text:
        channel = client.get_channel(OUTPUT_CHANNEL)
        await channel.send("@JadenDH 🚨 ALERT 🚨")

client.run(TOKEN)