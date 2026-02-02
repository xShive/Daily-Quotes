# ========== Imports ==========
import os
import dotenv
import discord

from discord import app_commands
from config import update_config
from commands.commands import register_commands
from commands.errors import register_errors


# ========== Environment Setup ==========
# Load environment variables from .env file
dotenv.load_dotenv()


# ========== Discord client + command tree setup ==========
# Intents: describe what data Discord is allowed to send
intents = discord.Intents.default()
intents.message_content = True  # reading message history permission

# Client handles connection to Discord
client = discord.Client(intents=intents)

# CommandTree stores all slash commands
tree = app_commands.CommandTree(client)
# AppCommand objects, each of which knows command name, desc, parameter info, function to call
# So it looks like this: "id" + AppCommand(callback=function, metadata=...)


# ========== Register commands + errors ==========
# Must be called to register in the tree
# Otherwise, commands.py might run before main has initialized tree -> error
register_commands(tree)
register_errors(tree)


# ========== Startup ==========
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    async for guild in client.fetch_guilds():
        update_config(guild.id)

    await tree.sync()


@client.event
async def on_guild_join(guild: discord.Guild):
    update_config(guild.id)
    
client.run(token)