from typing import Optional, Tuple
from core.models import GuildConfig
import discord

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