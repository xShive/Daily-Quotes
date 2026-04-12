import datetime
import discord
from discord.ext import tasks

from core.cache import QuoteCache
from core.config_manager import ConfigManager
from core.quote_service import send_random_quote_for_guild


class DailyQuoteScheduler:
    def __init__(
        self,
        client: discord.Client,
        config_manager: ConfigManager,
        cache: QuoteCache,
        hour: int = 9,
        minute: int = 0,
    ):
        self.client = client
        self.config_manager = config_manager
        self.cache = cache
        self.daily_quote_loop = tasks.loop(time=datetime.time(hour=hour, minute=minute))(self._run_daily_quote)

    async def _run_daily_quote(self):
        # ensure bot is ready
        await self.client.wait_until_ready()

        for guild_data in self.config_manager.iter_guilds():
            if not guild_data.has_channels_configured():
                continue

            try:
                await send_random_quote_for_guild(guild_data, self.client, self.cache)
                
            except Exception as exc:
                print(f"Failed daily quote for guild {guild_data.guild_id}: {exc}")

    def start(self):
        if not self.daily_quote_loop.is_running():
            self.daily_quote_loop.start()

    def stop(self):
        if self.daily_quote_loop.is_running():
            self.daily_quote_loop.stop()
