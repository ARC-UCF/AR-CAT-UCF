import os 
from dotenv import load_dotenv
import asyncio
load_dotenv('sensitive.env')

import discord
from discord.ext import commands

intents = discord.Intents(dm_messages=True, guild_messages=True, guilds=True, members=True, message_content=True, guild_reactions=True)

class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        
client = MyClient()