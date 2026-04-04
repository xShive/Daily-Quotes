# ========== Imports ==========
import discord
import time
from discord import app_commands

from core.config_manager import ConfigManager
from core.cache import QuoteCache
from quotes.fetcher import fetch_random_quote, fetch_message_history_quotes, get_configured_channels
from quotes.embeds import create_quote_embed, create_info_embed, create_leaderboard_embed


class LeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__()      # super is to run discord stuff
        self.page = 0
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        # you can only go back if we're not at the start
        if self.page > 0:
            self.page -=1
        
        await interaction.response.edit_message(
            embed=create_leaderboard_embed(self.page),
            view=self
        )

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1

        await interaction.response.edit_message(
            embed=create_leaderboard_embed(self.page),
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
        
        return str(interaction.user.id) == guild_data.admin
    
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

    import time

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
    @mod_check
    @app_commands.guild_only()
    async def set_source(interaction: discord.Interaction, source_channel: discord.TextChannel):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.source_channel = source_channel.id
        config_manager.save()
        await interaction.response.send_message("Successfully changed the source channel!")


    @tree.command(name="target", description="Set the specified channel as the target channel.")
    @mod_check
    @app_commands.guild_only()
    async def set_target(interaction: discord.Interaction, target_channel: discord.TextChannel):
        assert interaction.guild_id is not None

        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.target_channel = target_channel.id
        config_manager.save()
        await interaction.response.send_message("Successfully changed the target channel!")


    @tree.command(name="info", description="Display the currently configurated settings.")
    @mod_check
    @app_commands.guild_only()
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
    @mod_check
    @app_commands.guild_only()
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
    async def leaderboard(interaction: discord.Interaction):
        lb_view = LeaderboardView()

        await interaction.response.send_message(
            embed = create_leaderboard_embed(0),
            view=lb_view
        )

    
    @tree.command(name="add_admin", description="Gives a member privileges to use the bot to its full extent.")
    @admin_check
    @app_commands.guild_only()
    async def add_admin(interaction: discord.Interaction, user: discord.User):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        print(user.id)
        guild_data.add_authorized_user(user.id)
        config_manager.save()
        await interaction.response.send_message(content=f"Successfully made {user.name} a moderator!")

    @tree.command(name="remove_admin", description="Revokes a member's privileges to use the bot to its full extent.")
    @admin_check
    @app_commands.guild_only()
    async def remove_admin(interaction: discord.Interaction, user: discord.User):
        assert interaction.guild_id is not None
        
        guild_data = config_manager.get_guild(interaction.guild_id)
        guild_data.remove_authorized_user(user.id)
        config_manager.save()
        await interaction.response.send_message(content=f"Successfully removed {user.name} from the moderators!")
        

        
