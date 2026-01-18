# Standard libraries and external modules
import dotenv
import discord
import os
import random
import re
from config import *

# Load .env: token
dotenv.load_dotenv()

# Discord client setup and permissions
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def fetch_message_history_quotes(channel: discord.TextChannel) -> list[list[tuple[str, str]]]:
    pattern = r"\"([^\"]+)\"[\n]+[-~][\s]*(.+)"
    all_matches: list[list[tuple[str, str]]] = []

    async for msg in channel.history(limit=None):
        matches = re.findall(pattern, msg.content)
        if matches:
            all_matches.append(matches)
        
    return all_matches

async def get_channels_from_config(config: dict):
    source_id = config.get("source_channel")
    target_id = config.get("target_channel")

    if source_id is None or target_id is None:
        return None

    try:
        source_channel = await client.fetch_channel(source_id)
        target_channel = await client.fetch_channel(target_id)
        
    except discord.NotFound:
        return None
    except discord.Forbidden:
        return None
    except discord.HTTPException:
        return None

    if not isinstance(target_channel, discord.abc.Messageable):
        return None

    return source_channel, target_channel


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if (message.author.display_name == "Shive" or message.author.display_name == "YaboyUlrich") and "%h" in message.content:
        history = await fetch_message_history_quotes(message.channel)
        
        if len(history) > 0:
            user_msg = random.choice(history)

            user_config = read_config()
            channels = await get_channels_from_config(user_config)

            if channels:
                source_channel, target_channel = channels
                for quote_info in user_msg:
                    await target_channel.send(f"\"{quote_info[0]}\"\n-{quote_info[1]}")

            else:
                await message.channel.send("No source or target channel set / bot cannot access them!") 
        else:
            await message.channel.send("No history found!")
            
    if (message.author.display_name == "Shive" or message.author.display_name == "Hintrill") and "%id" in message.content:
        await message.channel.send(message.channel.id)

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

client.run(token)
