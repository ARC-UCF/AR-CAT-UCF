from .bot import client
from config import config
import discord
from discord.ext import tasks
from logger import log

@client.event
async def on_ready():
    
    log.info(f"Client is ready!")
    log.info(f"Logged in as client {client.user}")
    
    guild = discord.Object(id=config.guild_id)
    
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
        
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Watching the weather"), status=discord.Status.dnd)
    
@client.event
async def on_disconnect():
    log.warn(f"Client disconnected!")