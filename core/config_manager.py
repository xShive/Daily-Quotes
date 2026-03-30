# ========== Imports ==========
import os
import json
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
        
        # Ensure "guilds" key exists
        if "guilds" not in data or not isinstance(data["guilds"], dict):
            data["guilds"] = {}
        
        return data

    def save(self):
        """Saves the changes made to the config file."""
        with open(self.path, 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
    
    def get_guild(self, guild_id: int) -> Optional[GuildConfig]:
        """Returns GuildConfig loaded from the config if it exists, creates default if not."""
        str_guild_id = str(guild_id)
        guild_data = self.data["guilds"].get(str_guild_id)
        
        if guild_data is None:
            # Create default config
            guild_data = {
                "source_channel": None,
                "target_channel": None,
                "authorized_users": ["514782845181624330"]
            }
            self.data["guilds"][str_guild_id] = guild_data

        return GuildConfig(str_guild_id, guild_data)

    def add_guild(self, guild_id: int):
        """Adds a Discord Guild to the config.json. Needs its ID."""
        self.data["guilds"].setdefault(str(guild_id), {
            "source_channel": None,
            "target_channel": None,
            "authorized_users": ["514782845181624330"]
        })
    
    def remove_guild(self, guild_id: int) -> bool:
        """Removes a Discord Guild from the config.json. Needs its ID.
        Returns:
            bool: True if success, False if Guild doesn't exist.
        """
        if self.data["guilds"].pop(str(guild_id), None) is not None:
            return True
        return False