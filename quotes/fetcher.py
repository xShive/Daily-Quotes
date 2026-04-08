# ========== Imports ==========
import random
import re
import discord
import asyncio
from typing import Optional, Tuple

from core.cache import QuoteCache
from my_types.quote_types import Quote, QuoteHistory
from core.models import GuildConfig


# ========== Quote Fetching Functions ==========
async def fetch_message_history_quotes(
        channel: discord.TextChannel | discord.Thread,
        cache: QuoteCache
    ) -> QuoteHistory:
    """
    Fetch all messages in a channel and extract quotes using a regex.

    Each message may contain multiple quotes with the format:
        "quote text"
        - author

    Args:
        channel (discord.TextChannel | discord.Thread): A text channel or thread to scan.
        cache (QuoteCache): A QuoteCache instance

    Returns:
        list (list[Quote]): A list of messages, where each message is a list of (quote, author) tuples.
        Returns an empty list if no quotes are found.
    """
    
    # check cache
    cached_quotes = cache.get_quote_history()
    if len(cached_quotes) != 0:
        return cached_quotes

    # fetch everything using discord's API
    # Support both straight quotes (") and curly quotes (“ ”)
    QUOTE_REGEX = re.compile(r'(?:"|“|”)([^"“”]+)(?:"|“|”)[\n]+[-~]\s*(.+)')
    all_matches: QuoteHistory = []

    async for msg in channel.history(limit=None):
        matches = QUOTE_REGEX.findall(msg.content)
        if matches:
            # Convert 2-tuples to 3-tuples by adding msg.author.id
            quotes_with_sender = [(quote, author, msg.author.id) for quote, author in matches]
            all_matches.append(quotes_with_sender)

    # save history to cache
    cache.cache_quote_history(all_matches)
    print(all_matches)
    return all_matches


async def fetch_random_quote(
        source_channel: discord.TextChannel | discord.Thread,
        cache: QuoteCache
    ) -> Optional[Quote]:
    """
    Select a random quote message from a channel.

    Args:
        source_channel (discord.TextChannel | discord.Thread): Channel or thread containing quotes.
        cache (QuoteCache): A QuoteCache instance
        
    Returns:
        Optional[Quote]: A list of (quote, author) tuples from a single message.
        Returns None if no quotes exist.
    """
    history = await fetch_message_history_quotes(source_channel, cache)
    if not history:
        return None
    
    return random.choice(history)


async def get_configured_channels(
    guild_config: GuildConfig,
    client: discord.Client
) -> Optional[Tuple[discord.TextChannel, discord.abc.Messageable]]:
    """
    Get source and target channels as Discord objects.
    
    Args:
        guild_config: GuildConfig instance
        client: Discord client (from interaction.client)
    
    Returns:
        (source_channel, target_channel) or None if not configured/invalid
    """
    source_id = guild_config.source_channel
    target_id = guild_config.target_channel
    
    # Check if configured
    if source_id is None or target_id is None:
        return None
    
    # Fetch channels with error handling
    try:
        source_channel = await client.fetch_channel(source_id)
        target_channel = await client.fetch_channel(target_id)
    except (discord.InvalidData, discord.Forbidden, discord.NotFound):
        return None
    
    # Type validation
    if not isinstance(source_channel, discord.TextChannel):
        return None
    
    if not isinstance(target_channel, discord.abc.Messageable):
        return None
    
    return source_channel, target_channel