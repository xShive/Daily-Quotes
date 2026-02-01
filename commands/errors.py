import discord
from discord import app_commands

def register_errors(tree):
    @tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You are not authorized to use this command!", ephemeral=True)
            return
        
        print(f"Unhandled error: {error}")
        await interaction.response.send_message("Something went wrong. Please contact Shive.", ephemeral=True)

