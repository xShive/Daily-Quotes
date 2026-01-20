# ==========
# Imports
# ==========
# Standard libraries
import os
import random
import re
from typing import Any

# Third-party libraries
import dotenv
import discord
from discord import app_commands

# local modules
from config import read_config, update_config


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

async def validate_user(interaction: discord.Interaction) -> bool:
    """Check if the user is authorized to run admin commands.

    Args:
        interaction (discord.Interaction)

    Returns:
        bool: True if authorized, False otherwise. If False, @app_commands.check will raise a CheckFailure
    """
    authorized_users = get_authorized_users(read_config())
    return interaction.user.display_name in authorized_users

        
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
    QUOTE_REGEX = re.compile(r'"([^"]+)"[\n]+[-~]\s*(.+)')
    all_matches: list[list[tuple[str, str]]] = []

    async for msg in channel.history(limit=None):
        matches = QUOTE_REGEX.findall(msg.content)
        if matches:
            all_matches.append(matches)
        
    return all_matches


async def fetch_random_quote(source_channel: discord.TextChannel) -> list[tuple[str, str]] | None:
    """Pick a random message containing quotes and send all quotes from it to the target channel

    Args:
        source_channel (discord.TextChannel): this not only guarantees a .send() method, but also others like .history()
    
    Returns:
        str: the formatted text
    """
    history = await fetch_message_history_quotes(source_channel)
    if not history:
        return None
    return random.choice(history)


def create_quote_embed(quote_data: list[tuple[str, str]]) -> discord.Embed:
    embed = discord.Embed(
        title="📜 Quote",
        color=discord.Colour.from_rgb(130, 182, 217),
    )

    lines: list[str] = []

    lines: list[str] = [f"“{q}”\n— *{a}*" for q, a in quote_data]
    embed.description = "\n\n".join(lines)
    embed.set_footer(text="Daily Quotes")
    return embed


def create_info_embed(source_channel: discord.TextChannel, target_channel: discord.abc.Messageable) -> discord.Embed:
    embed = discord.Embed(
        title="⚙️ Info",
        color=discord.Colour.from_rgb(160, 231, 125)
    )
    description = f"Source channel: {source_channel.mention}"

    if isinstance(target_channel, (discord.TextChannel, discord.Thread)):
        description += f"\nTarget channel: {target_channel.mention}"
    else:
        description += f"\nTarget channel: ERROR"
    
    embed.description = description
    return embed


# ==========
# Config helpers (config.py, config.json related)
# ==========

async def get_channels_from_config(config: dict[str, Any]) -> tuple[discord.TextChannel, discord.abc.Messageable] | None:
    """Retrieves source and target channels from config.

    Args:
        config (dict[str, Any]

    Returns:
        tuple[discord.TextChannel, discord.abc.Messageable] | None: Returns the channels and None if invalid
    """
    source_id = config.get("source_channel")
    target_id = config.get("target_channel")
    if source_id is None or target_id is None:
        return None

    try:
        source_channel = await client.fetch_channel(source_id)
        target_channel = await client.fetch_channel(target_id)
    except (discord.InvalidData, discord.Forbidden, discord.NotFound):
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
    print(f"Logged in as {client.user}")
    MY_GUILD_ID = discord.Object(id=1422675442866847837) 
    tree.copy_global_to(guild=MY_GUILD_ID)
    await tree.sync(guild=MY_GUILD_ID)


# ==========
# Slash commands
# ==========

@tree.command(name="id", description="Get the ID of the current channel")
@app_commands.check(validate_user)
async def current_channel_id(interaction: discord.Interaction):
    """Returns the current channel ID (debug command)
    """
    await interaction.response.send_message(f"Current channel ID: {interaction.channel_id}")


@tree.command(name="quote", description="Send a random quote from a source channel to a target channel")
@app_commands.check(validate_user)
async def random_quote(interaction: discord.Interaction):
    """Send a random quote from the configured channel to the target channel
    """
    # Check if channel ID's exist in user_config
    channels = await get_channels_from_config(read_config())
    if channels is None:
        await interaction.response.send_message("No source and/or target channel set!", ephemeral=True)
        return
    
    source_channel, target_channel = channels

    # Fetching random quotes takes time (>3sec) so we defer. This sets flag True (by thinking)
    await interaction.response.defer()

    quote = await fetch_random_quote(source_channel)
    if quote is None:
        await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
        return
    
    quote_embed = create_quote_embed(quote)
    await interaction.edit_original_response(embed=quote_embed)


@tree.command(name="source", description="Set the specified channel as the source channel.")
@app_commands.check(validate_user)
async def set_source(interaction: discord.Interaction, source_channel: discord.TextChannel):
    update_config("source_channel", source_channel.id)
    await interaction.response.send_message("Successfully changed the source channel!")


@tree.command(name="target", description="Set the specified channel as the target channel.")
@app_commands.check(validate_user)
async def set_target(interaction: discord.Interaction, target_channel: discord.TextChannel):
    update_config("target_channel", target_channel.id)
    await interaction.response.send_message("Successfully changed the target channel!")


@tree.command(name="info", description="Display the current source- and target-channel.")
@app_commands.check(validate_user)
async def show_info(interaction: discord.Interaction):
    user_config = read_config()
    
    channels = await get_channels_from_config(user_config)
    if channels is None:
        await interaction.response.send_message("No source and/or target channel set!", ephemeral=True)
        return
    
    source_channel, target_channel = channels
    info_embed = create_info_embed(source_channel, target_channel)
    await interaction.response.send_message(embed=info_embed)


@tree.command(name="total_quotes", description="Display the total amount of correctly formatted quotes in set source channel")
@app_commands.check(validate_user)
async def get_total_quotes(interaction: discord.Interaction):
    channels = await get_channels_from_config(read_config())
    if channels is None:
        await interaction.response.send_message("No source channel set!", ephemeral=True)
        return

    source_channel = channels[0]

    await interaction.response.defer()

    history = await fetch_message_history_quotes(source_channel)
    if not history:
        await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
        return
    
    total_count = sum(len(message) for message in history)
    
    plural = "s" if total_count != 1 else ""
    verb = "are" if total_count != 1 else "is"
    
    msg = f"There {verb} {total_count} quote{plural} in {source_channel.mention}"
    
    await interaction.edit_original_response(content=msg)

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You are not authorized to use this command!", ephemeral=True)
        return
    
    print(f"Unhandled error: {error}")
    await interaction.response.send_message("Something went wrong. Please contact Shive.", ephemeral=True)


# ==========
# Startup
# ==========
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

client.run(token)