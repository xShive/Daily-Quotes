# ========== Imports ==========
import discord
import time
from discord import app_commands

from core.config_manager import ConfigManager
from core.cache import QuoteCache
from quotes.fetcher import fetch_random_quote, fetch_message_history_quotes
from core.helpers import get_configured_channels
from quotes.embeds import create_quote_embed, create_info_embed, create_leaderboard_embed
from core.quotestats import QuoteStats


class LeaderboardView(discord.ui.View):
    def __init__(self, sender_data, quoted_data):
        super().__init__()      # super is to run discord stuff
        self.page = 0
        self.sender_data = sender_data
        self.quoted_data = quoted_data
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        # you can only go back if we're not at the start
        if self.page > 0:
            self.page -=1
        
        await interaction.response.edit_message(
            embed=create_leaderboard_embed(self.sender_data, self.quoted_data, self.page),
            view=self)


    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1

        await interaction.response.edit_message(
        embed=create_leaderboard_embed(self.sender_data, self.quoted_data, self.page),
        view=self
    )

# ========== Admin Wrapper ==========
def validation(config_manager: ConfigManager, admin_flag: bool = False):
    """
    Creates a decorator to check if a user is allowed to run a command.

    How it works:
    1. This function runs **once** when the bot starts / commands are registered.
       - You give it your ConfigManager and optionally admin=True.

    2. It returns a decorator: `app_commands.check(predicate)`.
       - This decorator is what you usually put above your command (@admin_only).
       Now you return it, so it can have a different name.

    3. Inside, `predicate(interaction)` is the function Discord actually calls
       when a user runs the command.
       - Discord only passes `interaction` to predicate because `app_commands.check(predicate)`.
       - But predicate still "knows" config_manager and admin=True
         because of Python closures (variables from the outer function are remembered).

    4. predicate returns True or False:
       - True → command runs
       - False → Discord cancels the command (CheckFailure)
    
    TL;DR:
    - Outer function = runs once, packs config_manager and admin into the closure
    - Inner function (predicate) = runs on every command call, checks permission
    - Return value = decorator Discord can use
    """
    async def predicate(interaction: discord.Interaction):
        if interaction.guild_id is None:
            return False
        
        guild_data = config_manager.get_guild(interaction.guild_id)

        if not admin_flag:
            return interaction.user.id in guild_data.authorized_users
        
        return interaction.user.id == guild_data.admin
    
    return app_commands.check(predicate)


# ========== Slash Command Registration ==========
def register_commands(tree, config_manager: ConfigManager, cache: QuoteCache):
    """
    Register all slash commands.
    
    Args:
        tree: Discord command tree
        config_manager: ConfigManager instance
        cache: QuoteCache instance
    """
    mod_check = validation(config_manager)
    admin_check = validation(config_manager, True)


    @tree.command(name="quote", description="Send a random quote from a source channel to a target channel")
    @app_commands.guild_only()
    async def random_quote(interaction: discord.Interaction):
        start = time.perf_counter()

        assert interaction.guild_id is not None
        
        channels = await get_configured_channels(config_manager.get_guild(interaction.guild_id), interaction.client)
        if channels is None:
            await interaction.response.send_message("Channels not configured!", ephemeral=True)
            return
        
        source_channel, target_channel = channels

        await interaction.response.defer()

        quote = await fetch_random_quote(source_channel, cache)
        if quote is None:
            await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
            return
        
        quote_embed = create_quote_embed(quote)
        await target_channel.send(embed=quote_embed)

        end = time.perf_counter()
        print(f"Total took: {end - start:.3f}s")

        if isinstance(target_channel, discord.abc.GuildChannel):
            await interaction.delete_original_response()


    @tree.command(name="source", description="Set the specified channel as the source channel.")
    @app_commands.guild_only()
    @mod_check
    async def set_source(interaction: discord.Interaction, source_channel: discord.TextChannel):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.source_channel = source_channel.id
        config_manager.save()
        await interaction.response.send_message("Successfully changed the source channel!")


    @tree.command(name="target", description="Set the specified channel as the target channel.")
    @app_commands.guild_only()
    @mod_check
    async def set_target(interaction: discord.Interaction, target_channel: discord.TextChannel):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.target_channel = target_channel.id
        config_manager.save()
        await interaction.response.send_message("Successfully changed the target channel!")


    @tree.command(name="info", description="Display the currently configurated settings.")
    @app_commands.guild_only()
    @mod_check
    async def show_info(interaction: discord.Interaction):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)

        channels = await get_configured_channels(guild_data, interaction.client)
        if channels is None:
            await interaction.response.send_message("Channels not configured!", ephemeral=True)
            return
        
        source_channel, target_channel = channels
        info_embed = await create_info_embed(source_channel, target_channel, guild_data, interaction.client)
        await interaction.response.send_message(embed=info_embed)


    @tree.command(name="total_quotes", description="Display the total amount of correctly formatted quotes in set source channel")
    @app_commands.guild_only()
    @mod_check
    async def get_total_quotes(interaction: discord.Interaction):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)

        channels = await get_configured_channels(guild_data, interaction.client)
        if channels is None:
            await interaction.response.send_message("Channels not configured!", ephemeral=True)
            return
        
        source_channel = channels[0]

        await interaction.response.defer()

        history = await fetch_message_history_quotes(source_channel, cache)
        if not history:
            await interaction.edit_original_response(content=f"No quotes found in {source_channel.mention}!")
            return
        
        total_count = sum(len(message) for message in history)
        
        plural = "s" if total_count != 1 else ""
        verb = "are" if total_count != 1 else "is"
        
        msg = f"There {verb} {total_count} quote{plural} in {source_channel.mention}"
        
        await interaction.edit_original_response(content=msg)


    @tree.command(name="leaderboard", description="Display a leaderboard with cool info.")
    @app_commands.guild_only()
    async def leaderboard(interaction: discord.Interaction):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)
        known_users = guild_data.known_users

        channels = await get_configured_channels(guild_data, interaction.client)
        if channels is None:
            await interaction.response.send_message("Channels not configured!", ephemeral=True)
            return
        
        await interaction.response.defer()

        stats = QuoteStats(await fetch_message_history_quotes(channels[0], cache))
        sender_data = stats.count_quotes_made()
        quoted_data = stats.count_total_quotes(known_users)
        lb_view = LeaderboardView(sender_data, quoted_data)

        await interaction.edit_original_response(
            embed=create_leaderboard_embed(sender_data, quoted_data, 0),
            view=lb_view
        )

    @tree.command(name="set_names", description="Add a user to *the list* known by the system which is used for filtering")
    @app_commands.guild_only()
    @mod_check
    async def set_names(interaction: discord.Interaction, names: str):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)
        for name in [name.strip() for name in names.split(',') if name.strip()]:
            guild_data.add_known_user(name.capitalize())

        config_manager.save()
        await interaction.response.send_message(content="Successfully added everyone!", ephemeral=True)
    
    @tree.command(name="add_alias", description="Link an alias to a primary user (e.g., primary: Sabato, alias: Safloet)")
    @app_commands.guild_only()
    @mod_check
    async def add_alias(interaction: discord.Interaction, primary_name: str, alias: str):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)
        
        primary_clean = primary_name.strip()
        alias_clean = alias.strip()

        # check if primary exists
        existing_primaries = {k.lower(): k for k in guild_data.known_users.keys()}
        if primary_clean.lower() not in existing_primaries:
            await interaction.response.send_message(f"Primary user '{primary_clean}' not found. Add them with /set_names first.", ephemeral=True)
            return
        
        actual_primary = existing_primaries[primary_clean.lower()]

        guild_data.add_known_alias(actual_primary, alias_clean)
        config_manager.save()
        
        await interaction.response.send_message(content=f"Successfully linked '{alias_clean}' to **{actual_primary}**!", ephemeral=True)

    @tree.command(name="add_admin", description="Gives a member privileges to use the bot to its full extent.")
    @app_commands.guild_only()
    @admin_check
    async def add_admin(interaction: discord.Interaction, user: discord.User):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.add_authorized_user(user.id)
        config_manager.save()
        await interaction.response.send_message(content=f"Successfully made <@{user.id}> a moderator!")

    @tree.command(name="remove_admin", description="Revokes a member's privileges to use the bot to its full extent.")
    @app_commands.guild_only()
    @admin_check
    async def remove_admin(interaction: discord.Interaction, user: discord.User):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.remove_authorized_user(user.id)
        config_manager.save()
        await interaction.response.send_message(content=f"Successfully removed <@{user.id}> from the moderators!")
        

        
