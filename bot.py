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
    # Only watch the source channel
    if message.channel.id != SOURCE_CHANNEL:
        return

    # Only process messages that contain embeds (your webhook)
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

    # Send everything to output channel (no filtering)
    if text:
        channel = client.get_channel(OUTPUT_CHANNEL)
        await channel.send(text)

client.run(TOKEN)
