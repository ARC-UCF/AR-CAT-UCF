import discord
from discord.ext import commands
from alerts import Alerts
from messages import Messenger
from forecasts import ForecastManager
from helpers import AsyncLinks, channels
from logger import log
import asyncio
import traceback

intents = discord.Intents(dm_messages=True, guild_messages=True, guilds=True, members=True, message_content=True, guild_reactions=True)

class CAT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.alerts = Alerts()
        self.messenger = Messenger()
        self.forecastManager = ForecastManager()
        
    async def close(self):
        log.info(f"Closing bot.")
        await AsyncLinks.close()
        await super().close()
        
    async def setup_hook(self):
        await AsyncLinks.setup()
        
    async def on_ready(self):
        if not hasattr(self, "tasks_started"):
            self.alerts_task = asyncio.create_task(
                self.check_alerts()
            )
            self.message_task = asyncio.create_task(
                self.send_messages()
            )
            self.forecasts_task = asyncio.create_task(
                self.check_forecasts()
            )
            
            self.tasks_started = True
            
            channels.sync_channels(self)
        
    async def check_alerts(self):
        while True:
            try:
                await self.alerts.cycle()
            except Exception as e:
                traceback.print_exc()
                log.error(f"Error while running alerts cycle: {e}")
                await asyncio.sleep(10)
                
    async def send_messages(self):
        while True:
            try:
                await self.messenger.check_and_post()
            except Exception as e:
                traceback.print_exc()
                log.error(f"Error while running messenger cycle: {e}")
                await asyncio.sleep(10)
                
    async def check_forecasts(self):
        while True:
            try:
                await self.forecastManager.run()
            except Exception as e:
                traceback.print_exc()
                log.error(f"Error while running forecast manager cycle: {e}")
                await asyncio.sleep(10)
        
client = CAT()