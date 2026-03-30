# ========== Imports ==========
import discord
from typing import Optional
from datetime import datetime, timedelta


# ========== QuoteCache Class ==========
class QuoteCache:
    """
    RAM cache for frequently accessed data.
    Follows the same pattern as AssetCache from League bot.
    
    Caches:
    - Channel objects (avoid repeated Discord API calls)
    - Quote history from channels (expensive to fetch)
    
    All data stored in CLASS-LEVEL attributes (shared across all instances).
    """
    
    # Class-level storage (shared across ALL instances automatically!)
    _channels: dict[int, discord.abc.GuildChannel] = {}
    _quote_history: dict[int, tuple[list, datetime]] = {}  # (quotes, timestamp)
    
    # Cache expiration time for quote history (5 minutes)
    CACHE_EXPIRY = timedelta(minutes=5)
    
    def get_channel(self, channel_id: int) -> Optional[discord.abc.GuildChannel]:
        """
        Get cached channel object.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            Cached channel object or None if not cached
        """
        return self._channels.get(channel_id)
    
    def cache_channel(self, channel_id: int, channel: discord.abc.GuildChannel):
        """
        Cache a channel object.
        
        Args:
            channel_id: Discord channel ID
            channel: Channel object to cache
        """
        self._channels[channel_id] = channel
    
    def get_quote_history(self, channel_id: int) -> Optional[list]:
        """
        Get cached quote history for a channel.
        Returns None if not cached or expired.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            List of quotes or None if not cached/expired
        """
        cached_data = self._quote_history.get(channel_id)
        if cached_data is None:
            return None
        
        quotes, timestamp = cached_data
        
        # Check if cache is expired
        if datetime.now() - timestamp > self.CACHE_EXPIRY:
            # Remove expired cache
            del self._quote_history[channel_id]
            return None
        
        return quotes
    
    def cache_quote_history(self, channel_id: int, quotes: list):
        """
        Cache quote history for a channel.
        
        Args:
            channel_id: Discord channel ID
            quotes: List of quotes to cache
        """
        self._quote_history[channel_id] = (quotes, datetime.now())
    
    def invalidate_quote_history(self, channel_id: Optional[int] = None):
        """
        Clear quote history cache.
        
        Args:
            channel_id: If provided, only clear that channel's cache.
                       If None, clear all quote history.
        """
        if channel_id is not None:
            self._quote_history.pop(channel_id, None)
        else:
            self._quote_history.clear()
    
    @classmethod
    def clear_all(cls):
        """Clear all caches (useful for testing or resetting)."""
        cls._channels.clear()
        cls._quote_history.clear()
