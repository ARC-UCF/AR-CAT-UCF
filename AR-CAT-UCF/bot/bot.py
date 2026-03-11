import discord
from discord.ext import commands

intents = discord.Intents(dm_messages=True, guild_messages=True, guilds=True, members=True, message_content=True, guild_reactions=True)

class CAT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        
client = CAT()