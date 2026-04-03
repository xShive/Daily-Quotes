# ========== Imports ==========
import random
import re
import discord
from typing import Optional

from core.cache import QuoteCache
from types.quote_types import Quote, QuoteHistory


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
    if cached_quotes is not None:
        return cached_quotes

    # fetch everything using discord's API
    QUOTE_REGEX = re.compile(r'"([^"]+)"[\n]+[-~]\s*(.+)')
    all_matches: list[Quote] = []

    async for msg in channel.history(limit=None):
        matches = QUOTE_REGEX.findall(msg.content)
        if matches:
            all_matches.append(matches)
    
    # save history to cache
    cache.cache_quote_history(all_matches)

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
