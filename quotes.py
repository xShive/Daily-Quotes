# ========== Imports ==========
import random
import re
import discord


# ========== Functions ==========
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
