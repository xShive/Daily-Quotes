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
    def authorized_users(self) -> list[str]:
        """Get list of authorized user IDs."""
        return self._data.get("authorized_users", [])
    
    @authorized_users.setter
    def authorized_users(self, user_ids: list[str]):
        """Set list of authorized user IDs."""
        self._data["authorized_users"] = user_ids
    
    def is_user_authorized(self, user_id: str) -> bool:
        """
        Check if a user is authorized.
        
        Args:
            user_id: String representation of user ID
            
        Returns:
            True if user is authorized, False otherwise
        """
        return user_id in self.authorized_users
    
    def has_channels_configured(self) -> bool:
        """
        Check if both source and target channels are configured.
        
        Returns:
            True if both channels are set, False otherwise
        """
        return self.source_channel is not None and self.target_channel is not None
