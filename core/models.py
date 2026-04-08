# ========== Imports ==========
from typing import Optional
import discord


# ========== GuildConfig Model ==========
class GuildConfig:
    """
    Represents configuration for a Discord guild.
    Similar to Guild model from League bot.
    
    Provides property-based access to guild settings.
    """
    
    def __init__(self, guild_id: str, data: dict):
        """
        Initialize guild configuration.
        
        Args:
            guild_id: String representation of guild ID
            data: Dictionary containing guild configuration (reference to ConfigManager's data)
        """
        self.guild_id = guild_id
        self._data = data  # Reference to the actual dict in ConfigManager
    
    @property
    def source_channel(self) -> Optional[int]:
        """Get source channel ID."""
        return self._data.get("source_channel")
    
    @source_channel.setter
    def source_channel(self, channel_id: Optional[int]):
        """Set source channel ID."""
        self._data["source_channel"] = channel_id
    
    @property
    def target_channel(self) -> Optional[int]:
        """Get target channel ID."""
        return self._data.get("target_channel")
    
    @target_channel.setter
    def target_channel(self, channel_id: Optional[int]):
        """Set target channel ID."""
        self._data["target_channel"] = channel_id
    
    @property
    def authorized_users(self) -> list:
        """Get list of authorized user IDs.
        Returns an empty list if the config file is either corrupted or empty."""
        return self._data.setdefault("authorized_users", [])
    
    @property
    def admin(self) -> Optional[str]:
        """Get the superior admin sigma as a str."""
        return self._data.get("admin")
    
    @property
    def known_users(self) -> list[str]:
        """Get the known users as strings separated by commas"""
        return self._data.setdefault("known_users", [])
    
    def add_known_user(self, username: str):
        """Add a user to the known users list"""
        if username not in self.known_users:
            self.known_users.append(username)
    
    def add_authorized_user(self, user_id: int):
        """Add a user to authorized users list, safely."""
        if user_id not in self.authorized_users:
            self.authorized_users.append(user_id)
    
    def remove_authorized_user(self, user_id):
        if user_id in self.authorized_users:
            self.authorized_users.remove(user_id)
    
    
    def has_channels_configured(self) -> bool:
        """
        Check if both source and target channels are configured.
        
        Returns:
            True if both channels are set, False otherwise
        """
        return self.source_channel is not None and self.target_channel is not None
