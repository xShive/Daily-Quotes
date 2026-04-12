# ========== Imports ==========
import os
import dotenv
import discord
import datetime

from discord import app_commands
from commands.quote_commands import register_commands
from commands.error_handler import register_errors
from core.config_manager import ConfigManager
from core.cache import QuoteCache
from tasks.daily_quote import DailyQuoteScheduler


# ========== Environment Setup ==========
dotenv.load_dotenv()


# ========== Initialize Managers ==========
config_manager = ConfigManager()
cache = QuoteCache()


# ========== Setup ==========
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# CommandTree stores all slash commands
tree = app_commands.CommandTree(client)
# AppCommand objects, each of which knows command name, desc, parameter info, function to call
# So it looks like this: "id" + AppCommand(callback=function, metadata=...)

scheduler = DailyQuoteScheduler(client, config_manager, cache)


# ========== Startup ==========
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    register_commands(tree, config_manager, cache)
    register_errors(tree)

    scheduler.start()
    
    # sync with test server
    guild_id = os.getenv("GUILD_ID")
    if guild_id is None:
        raise RuntimeError("GUILD_ID environment variable not set")
    
    guild = discord.Object(int(guild_id))
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild) 

    # sync all joined guilds
    async for guild in client.fetch_guilds():
        print(guild.name)
        config_manager.add_guild(guild.id)
    config_manager.save()


@client.event
async def on_guild_join(guild: discord.Guild):
    config_manager.add_guild(guild.id)
    config_manager.save()

@client.event
async def on_guild_remove(guild: discord.Guild):
    config_manager.remove_guild(guild.id)
    config_manager.save()

if __name__ == "__main__":
    client.run(token)