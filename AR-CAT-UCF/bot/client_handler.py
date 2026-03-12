from bot import client
from config import config
import discord
from logging.syslogger import log

@client.event
async def on_ready():
    
    log.info(f"Client is ready!")
    log.info(f"Logged in as client {client.user}")
    
    guild = discord.Object(id=config.guild_id)
    
    