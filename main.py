# ========== Imports ==========
import os
import dotenv
import discord

from discord import app_commands
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
guild_id_str = os.getenv("GUILD_ID")
token = os.getenv("DISCORD_TOKEN")

if token is None:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

if guild_id_str is None:
    raise RuntimeError("GUILD_ID environment variable not set")

try:
    target_guild_id = int(guild_id_str)
except ValueError:
    raise RuntimeError(f"GUILD_ID must be a number, but got: {guild_id_str}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    tree.copy_global_to(guild=discord.Object(id=target_guild_id))
    await tree.sync(guild=discord.Object(id=target_guild_id))
    
    print(f"Commands synced to guild {target_guild_id}")

client.run(token)