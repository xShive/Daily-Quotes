import discord
from discord import app_commands
from config import read_config, update_config
from helpers import validate_user, get_channels_from_config
from quotes import fetch_random_quote, fetch_message_history_quotes
from embeds import create_quote_embed, create_info_embed


# ==========
# Slash commands
# ==========
def register_commands(tree):
    @tree.command(name="quote", description="Send a random quote from a source channel to a target channel")
    @app_commands.check(validate_user)
    async def random_quote(interaction: discord.Interaction):
        """Send a random quote from the configured channel to the target channel
        """
        # Check if channel ID's exist in user_config
        channels = await get_channels_from_config(interaction.client, read_config())
        if channels is None:
            await interaction.response.send_message("No source and/or target channel set!", ephemeral=True)
            return
        
        source_channel, target_channel = channels

        # Fetching random quotes takes time (>3sec) so we defer. This sets flag True (by thinking)
        await interaction.response.defer()

        quote = await fetch_random_quote(source_channel)
        if quote is None:
            await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
            return
        
        quote_embed = create_quote_embed(quote)
        await interaction.edit_original_response(embed=quote_embed)


    @tree.command(name="source", description="Set the specified channel as the source channel.")
    @app_commands.check(validate_user)
    async def set_source(interaction: discord.Interaction, source_channel: discord.TextChannel):
        update_config("source_channel", source_channel.id)
        await interaction.response.send_message("Successfully changed the source channel!")


    @tree.command(name="target", description="Set the specified channel as the target channel.")
    @app_commands.check(validate_user)
    async def set_target(interaction: discord.Interaction, target_channel: discord.TextChannel):
        update_config("target_channel", target_channel.id)
        await interaction.response.send_message("Successfully changed the target channel!")


    @tree.command(name="info", description="Display the current source- and target-channel.")
    @app_commands.check(validate_user)
    async def show_info(interaction: discord.Interaction):
        channels = await get_channels_from_config(interaction.client, read_config())
        if channels is None:
            await interaction.response.send_message("No source and/or target channel set!", ephemeral=True)
            return
        
        source_channel, target_channel = channels
        info_embed = create_info_embed(source_channel, target_channel)
        await interaction.response.send_message(embed=info_embed)


    @tree.command(name="total_quotes", description="Display the total amount of correctly formatted quotes in set source channel")
    @app_commands.check(validate_user)
    async def get_total_quotes(interaction: discord.Interaction):
        channels = await get_channels_from_config(interaction.client, read_config())
        if channels is None:
            await interaction.response.send_message("No source channel set!", ephemeral=True)
            return

        source_channel = channels[0]

        await interaction.response.defer()

        history = await fetch_message_history_quotes(source_channel)
        if not history:
            await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
            return
        
        total_count = sum(len(message) for message in history)
        
        plural = "s" if total_count != 1 else ""
        verb = "are" if total_count != 1 else "is"
        
        msg = f"There {verb} {total_count} quote{plural} in {source_channel.mention}"
        
        await interaction.edit_original_response(content=msg)
