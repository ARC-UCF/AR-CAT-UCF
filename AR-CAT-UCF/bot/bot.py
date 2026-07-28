import discord
from discord.ext import commands
from alerts import Alerts
from messages import Messenger
from forecasts import ForecastManager
from logger import log
import asyncio

intents = discord.Intents(dm_messages=True, guild_messages=True, guilds=True, members=True, message_content=True, guild_reactions=True)

class CAT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.alerts = Alerts()
        self.messenger = Messenger()
        self.forecastManager = ForecastManager()
        
    async def setup_hook(self):
        self.alerts_task = asyncio.create_task(
            self.check_alerts()
        )
        self.message_task = asyncio.create_task(
            self.send_messages()
        )
        self.forecasts_task = asyncio.create_task(
            self.check_forecasts()
        )
        
    async def check_alerts(self):
        while True:
            try:
                await self.alerts.cycle()
            except Exception as e:
                log.error(f"Error while running alerts cycle: {e}")
                
    async def send_messages(self):
        while True:
            try:
                await self.messenger.check_and_post()
            except Exception as e:
                log.error(f"Error while running messenger cycle: {e}")
                
    async def check_forecasts(self):
        while True:
            try:
                await self.forecastManager.run()
            except Exception as e:
                log.error(f"Error while running forecast manager cycle: {e}")
        
client = CAT()