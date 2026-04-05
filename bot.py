import discord
import os

TOKEN = os.getenv("TOKEN")
SOURCE_CHANNELS = [int(x) for x in os.getenv("SOURCE_CHANNELS").split(",")]
OUTPUT_CHANNEL = int(os.getenv("OUTPUT_CHANNEL"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # Only watch selected source channels
    if message.channel.id not in SOURCE_CHANNELS:
        return

    # Only process messages that contain embeds
    if not message.embeds:
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

    # Send all extracted text to output channel
    if text:
        channel = client.get_channel(OUTPUT_CHANNEL)
        await channel.send(text)

client.run(TOKEN)
