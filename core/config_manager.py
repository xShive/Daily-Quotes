# ========== Imports ==========
import os
import json
import dotenv
dotenv.load_dotenv()
from typing import Optional

from core.models import GuildConfig


# ========== Constants ==========
FILE = "data/config.json"


# ========== Class ConfigManager ==========
class ConfigManager:
    """
    ConfigManager manages guild configurations stored in config.json.
    Follows the same pattern as TrackManager from League bot.

    *Functions*:
        `get_guild()`: Get configuration for a specific guild
        `add_guild()`: Add a new guild with default configuration
        `remove_guild()`: Remove a guild's configuration
        `save()`: Save changes to config.json
    
    **IMPORTANT**
        Whenever you're editing or adding to the config you're forced to use the `save()` function or else your changes won't go through!!
    
    {
    "guilds": {
        "123456 (guild_id)": {
        "source_channel": 789,
        "target_channel": 101,
        "authorized_users": ["514782845181624330"],
        "admin" : 2341987043217890
        }
      }
    }
    """


    def __init__(self):
        self.path = FILE
        self.data = self._load()

    def _load(self) -> dict:
        """Load configuration from JSON file."""
        if not os.path.exists(self.path):
            return {"guilds": {}}

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Ensure "guilds" key exists & check if it's a dict
        if "guilds" not in data or not isinstance(data["guilds"], dict):
            data["guilds"] = {}
        
        return data

    def save(self):
        """Saves the changes made to the config file."""
        with open(self.path, 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
    
    def get_guild(self, guild_id: int) -> GuildConfig:
        """Returns GuildConfig, creates defaul if missing (using add_guild method)"""
        str_guild_id = str(guild_id)
        if str_guild_id not in self.data["guilds"]:
            self.add_guild(guild_id)
        
        return GuildConfig(str_guild_id, self.data["guilds"][str_guild_id])

    def add_guild(self, guild_id: int):
        """Adds a Discord Guild to the config.json using default values. Needs its ID."""
        str_guild_id = str(guild_id)
        admin_id = os.getenv("ADMIN")
        if not admin_id:
            raise RuntimeError("ADMIN environment variable not set")

        self.data["guilds"].setdefault(str_guild_id, {
            "source_channel" : None,
            "target_channel" : None,
            "authorized_users" : [int(admin_id)],
            "admin" : int(admin_id)
        })
    
    def remove_guild(self, guild_id: int) -> bool:
        """Removes a Discord Guild from the config.json. Needs its ID.
        Returns:
            bool: True if success, False if Guild doesn't exist.
        """
        if self.data["guilds"].pop(str(guild_id), None) is not None:
            return True
        return False