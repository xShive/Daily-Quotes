# ========== Imports ==========
import discord


# ========== Functions ==========
def create_quote_embed(quote_data: list[tuple[str, str]]) -> discord.Embed:
    """Create an embed containing one or more quotes.

    Args:
        quote_data (list[tuple[str, str]]): List of (quote, author) tuples.
    Returns:
        discord.Embed
    """
    embed = discord.Embed(
        title="📜 Quote",
        color=discord.Colour.from_rgb(130, 182, 217),
    )

    lines: list[str] = [f"“{q}”\n— *{a}*" for q, a in quote_data]
    embed.description = "\n\n".join(lines)
    embed.set_footer(text="Daily Quotes")

    return embed


def create_info_embed(source_channel: discord.TextChannel | discord.Thread, target_channel: discord.abc.Messageable) -> discord.Embed:
    """Create an embed describing current source and target channel. 

    Args:
        source_channel (discord.TextChannel | discord.Thread): Configured source channel.
        target_channel (discord.abc.Messageable): Configured target channel.

    Returns:
        discord.Embed
    """
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