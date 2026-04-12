# ========== Imports ==========
import discord
import asyncio
from my_types.quote_types import Quote
from core.models import GuildConfig


# ========== Embed Creation Functions ==========
def create_quote_embed(quote_data: Quote) -> discord.Embed:
    """
    Create an embed containing one or more quotes.

    Args:
        quote_data (Quote): List of (quote, author) tuples.
        
    Returns:
        discord.Embed
    """
    embed = discord.Embed(
        title="📜 Quote",
        color=discord.Colour.from_rgb(130, 182, 217),
    )

    lines: list[str] = [f"“{q}”\n— *{a}*" for q, a, _ in quote_data]
    embed.description = "\n\n".join(lines)
    embed.set_footer(text="Daily Quotes")

    return embed


async def create_info_embed(
    source_channel: discord.TextChannel | discord.Thread,
    target_channel: discord.abc.Messageable,
    guild_data: GuildConfig,
    client: discord.Client
) -> discord.Embed:
    """Create a detailed embed describing info about the current configuration"""
    
    embed = discord.Embed(
        title="⚙️ Channel Info",
        color=discord.Colour.from_rgb(160, 231, 125)
    )
    
    # Source channel field
    embed.add_field(
        name="Source Channel",
        value=(
            f"Name: {source_channel.name}\n"
            f"ID: {source_channel.id}\n"
            f"Type: {'Thread' if isinstance(source_channel, discord.Thread) else 'TextChannel'}\n"
            f"Mention: {source_channel.mention}"
        ),
        inline=False
    )
    
    # Target channel field
    if isinstance(target_channel, (discord.TextChannel, discord.Thread)):
        embed.add_field(
            name="Target Channel",
            value=(
                f"Name: {target_channel.name}\n"
                f"ID: {target_channel.id}\n"
                f"Type: {'Thread' if isinstance(target_channel, discord.Thread) else 'TextChannel'}\n"
                f"Mention: {target_channel.mention}"
            ),
            inline=False
        )
    else:
        embed.add_field(name="Target Channel", value="ERROR: Invalid channel type", inline=False)
    
    # MOD fields
    # client.fetch_user() is async coroutine. normally, awaiting many of them one by one is slow (serie).
    # asyncio runs them all at the same time (parallel), returning a list of all results
    # we have a generator. * unpacks everything. else you do something like next()
    embed.add_field(
        name="Moderators",
        value=(
            f"Users: {", ".join(f'<@{uid}>' for uid in guild_data.authorized_users)}\n"
            f"User_IDs: {", ".join([str(user_id) for user_id in guild_data.authorized_users])}\n"
        ),
        inline=False
    )

    embed.set_footer(text="Daily Quotes")
    
    return embed


def create_leaderboard_embed(
        sender_data,
        quoted_data: list[tuple[str, int]],
        page: int
    ) -> discord.Embed:

    match(page):
        case 0:
            title = "Quoted Others"
        
        case 1:
            title = "Times quoted"

        case _:
            title = "Unknown"
    
    embed = discord.Embed(
        title=f"🏆 Leaderboard\n{f"{page + 1} | {title}"}",
        color=discord.Color.gold()
    )
    
    match(page):
        case 0:
            slice_data = sender_data[:10]
            if not slice_data:
                embed.description = "No data."
                return embed
            
            lines = [f"**#{i + 1}** <@{uid}> | quoted others {count} times" for i, (uid, count) in enumerate(slice_data)]
            embed.description = "\n\n".join(lines)
        
        case 1:
            slice_data = quoted_data[:10]
            if not slice_data:
                embed.description = "No data."
                return embed
            
            lines = [f"**#{i + 1}** {name} | got quoted {count} times" for i, (name, count) in enumerate(slice_data)]
            embed.description = "\n\n".join(lines)


            
    
    return embed