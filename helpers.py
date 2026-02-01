# helpers.py
import discord
from typing import Any
from config import read_config, get_authorized_users


async def validate_user(interaction: discord.Interaction) -> bool:
    """Check if the user is authorized to run admin commands.

    Args:
        interaction (discord.Interaction)

    Returns:
        bool: True if authorized, False otherwise. If False, @app_commands.check will raise a CheckFailure
    """
    authorized_users = get_authorized_users(read_config())
    return interaction.user.display_name in authorized_users

async def get_channels_from_config(client: discord.Client, config: dict[str, Any]) -> tuple[discord.TextChannel, discord.abc.Messageable] | None:
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

