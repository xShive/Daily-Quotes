# ========== Imports ==========
import discord
from typing import Any
from config import read_config, get_authorized_users


# ========== Functions ==========
async def validate_user(interaction: discord.Interaction) -> bool:
    """Check if the user is authorized in this guild.
    This function is used as an @app_commands.check.

    Args:
        interaction (discord.Interaction)

    Returns:
        bool: True if authorized, False otherwise.
    """
    authorized_users = get_authorized_users(interaction.guild_id, read_config())
    return str(interaction.user.id) in authorized_users


async def get_channels_from_config(interaction: discord.Interaction, config: dict[str, Any]) -> tuple[discord.TextChannel | discord.Thread, discord.abc.Messageable] | None:
    """Resolve source and target channels for the current guild.

    Args:
        interaction (discord.Interaction)
        config (dict[str, Any]): Loaded configuration dictionary

    Returns:
        tuple[discord.TextChannel | discord.Thread, discord.abc.Messageable] | None: Returns a tuple with the source channel, being of type TextChannel or Thread, and the target channel, inheriting Messageable
    """
    source_id = config["guilds"][str(interaction.guild_id)]["source_channel"]
    target_id = config["guilds"][str(interaction.guild_id)]["target_channel"]
    if source_id is None or target_id is None:
        return None

    try:
        source_channel = await interaction.client.fetch_channel(source_id)
        target_channel = await interaction.client.fetch_channel(target_id)

    except (discord.InvalidData, discord.Forbidden, discord.NotFound):
        return None
    
    if not isinstance(target_channel, discord.abc.Messageable):
        return None
    
    if not isinstance(source_channel, (discord.TextChannel, discord.Thread)):
        return None

    return source_channel, target_channel   # Guaranteed hinted types because of the checks

