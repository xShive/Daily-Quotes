# ==========
# Imports
# ==========
# Standard libraries
import os
import random
import re

# Third-party libraries
import dotenv
import discord
from discord import app_commands

# local modules
from config import read_config


# ==========
# Environment setup
# ==========
# Load environment variables from .env file
dotenv.load_dotenv()


# ==========
# Discord client & command tree setup
# ==========
# Intents: describe what data Discord is allowed to send
intents = discord.Intents.default()
intents.message_content = True  # reading message history permission

# Client handles connection to Discord
client = discord.Client(intents=intents)

# CommandTree stores all slash commands
tree = app_commands.CommandTree(client)
    # AppCommand objects, each of which knows command name, desc, paramter info, functin to call  ) 
    # so it looks like this: "id" + AppCommand(callback=function, metadata=...)


# ==========
# Logic helpers
# ==========

async def fetch_message_history_quotes(channel: discord.TextChannel) -> list[list[tuple[str, str]]]:
    """Fetch all messages in a channel and extract quotes using regular expressions.
    Each message may contain multiple quotes with format:
    "quote"
    -author

    Args:
        channel (discord.TextChannel)

    Returns:
        list[list[tuple[str, str]]]: list[list[tuple[str, str]]]: A list of messages, where each message is a list of (quote, author) tuples.
    """
    pattern = r"\"([^\"]+)\"[\n]+[-~][\s]*(.+)"
    all_matches: list[list[tuple[str, str]]] = []

    async for msg in channel.history(limit=None):
        matches = re.findall(pattern, msg.content)
        if matches:
            all_matches.append(matches)
        
    return all_matches


async def send_random_quote(source_channel: discord.TextChannel, target_channel: discord.abc.Messageable):
    """Pick a random message containing quotes and send all quotes from it to the target channel

    Args:
        source_channel (discord.TextChannel): this not only guarantees a .send() method, but also others like .history()
        target_channel (discord.abc.Messageable): anything that has a .send() method (TextChannel, Thread, ...)
    """
    history = await fetch_message_history_quotes(source_channel)
    if not history:
        return
    
    user_msg = random.choice(history)

    for quote_info in user_msg:
        await target_channel.send(f"\"{quote_info[0]}\"\n-{quote_info[1]}")


# ==========
# Config helpers (config.py, config.json related)
# ==========

async def get_channels_from_config(config: dict) -> tuple[discord.TextChannel, discord.abc.Messageable] | None:
    source_id = config.get("source_channel")
    target_id = config.get("target_channel")

    # Channels not set
    if source_id is None or target_id is None:
        return None

    try:
        source_channel = await client.fetch_channel(source_id)
        target_channel = await client.fetch_channel(target_id)
    except discord.InvalidData or discord.Forbidden or discord.NotFound:
        return None
    
    if not isinstance(target_channel, discord.abc.Messageable):
        return None
    
    if not isinstance(source_channel, discord.TextChannel):
        return None

    return source_channel, target_channel   # Guaranteed hinted types because of the checks


def get_authorized_users(config: dict) -> list[str]:
    """Get list of display names allowed to use admin commands
    """
    return config.get("authorized_users", [])


# ==========
# Discord events
# ==========

@client.event
async def on_ready():
    """Called once the bot has successfully established a connection to Discord
    """
    print(f"Logged in as {client.user}")

    # Sync slash commands to Discord
    await tree.sync()


# ==========
# Slash commands
# ==========

@tree.command(name="id", description="Get the ID of the current channel")
async def current_channel_id(interaction: discord.Interaction):
    """Returns the current channel ID (debug command)
    """
    await interaction.response.send_message(f"Current channel ID: {interaction.channel_id}")


@tree.command(name="quote", description="Send a random quote from a source channel to a target channel")
async def random_quote(interaction: discord.Interaction):
    """Send a random quote from the configured channel to the target channel
    """
    user_config = read_config()
    authorized_users = get_authorized_users(user_config)

    # Permission check
    if interaction.user.display_name not in authorized_users:
        await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)
        return
    
    # Check if channel ID's exist in user_config
    channels = await get_channels_from_config(user_config)
    if channels is None:
        await interaction.response.send_message("No source and/or target channel set!", ephemeral=True)
        return
    
    source_channel, target_channel = channels
    await send_random_quote(source_channel, target_channel)

    await interaction.response.send_message("Quote sent!", ephemeral=True)


# ==========
# Startup
# ==========
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

client.run(token)