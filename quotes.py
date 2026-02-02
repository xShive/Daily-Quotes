# ========== Imports ==========
import random
import re
import discord


# ========== Functions ==========
async def fetch_message_history_quotes(channel: discord.TextChannel | discord.Thread) -> list[list[tuple[str, str]]]:
    """Fetch all messages in a channel and extract quotes using a regex.

    Each message may contain multiple quotes with the format:
        "quote text"
        - author

    Args:
        channel (discord.TextChannel | discord.Thread): A text channel or thread to scan.

    Returns:
        list (list[list[tuple[str, str]]]): A list of messages, where each message is a list of (quote, author) tuples.
        Returns an empty list if no quotes are found.
    """
    QUOTE_REGEX = re.compile(r'"([^"]+)"[\n]+[-~]\s*(.+)')
    all_matches: list[list[tuple[str, str]]] = []

    async for msg in channel.history(limit=None):
        matches = QUOTE_REGEX.findall(msg.content)
        if matches:
            all_matches.append(matches)
        
    return all_matches


async def fetch_random_quote(source_channel: discord.TextChannel | discord.Thread) -> list[tuple[str, str]] | None:
    """Select a random quote-containing message from a channel.

    Args:
        source_channel (discord.TextChannel | discord.Thread): Channel or thread containing quotes.

    Returns:
        list (list[tuple[str, str]] | None): A list of (quote, author) tuples from a single message.
        Returns None if no quotes exist.
    """
    history = await fetch_message_history_quotes(source_channel)
    if not history:
        return None
    
    return random.choice(history)
