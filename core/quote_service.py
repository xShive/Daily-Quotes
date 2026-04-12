import discord
from typing import Optional, Tuple

from core.cache import QuoteCache
from core.helpers import get_configured_channels
from core.models import GuildConfig
from quotes.embeds import create_quote_embed
from quotes.fetcher import fetch_random_quote
from my_types.quote_types import Quote


async def fetch_random_quote_for_guild(
    guild_data: GuildConfig,
    client: discord.Client,
    cache: QuoteCache,
) -> Optional[Tuple[discord.TextChannel, discord.abc.Messageable, Quote]]:
    """Return a ready-to-send random quote for a guild.

    The caller is responsible for validating configuration and handling
    the case where there are no quotes or channels are unavailable.
    """
    channels = await get_configured_channels(guild_data, client)
    if channels is None:
        return None

    source_channel, target_channel = channels
    quote = await fetch_random_quote(source_channel, cache)
    if quote is None:
        return None

    return source_channel, target_channel, quote


async def send_random_quote_for_guild(
    guild_data: GuildConfig,
    client: discord.Client,
    cache: QuoteCache,
) -> bool:
    """Send a random quote to the configured target channel."""
    result = await fetch_random_quote_for_guild(guild_data, client, cache)
    if result is None:
        return False

    _, target_channel, quote = result
    await target_channel.send(embed=create_quote_embed(quote))
    return True
