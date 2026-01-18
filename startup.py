import os 
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord import SyncWebhook
import asyncio
from brain import Controller
from bot import client
import config
from services.syslogger import log
load_dotenv('sensitive.env')

@client.event
async def on_ready():
    
    if not hasattr(client, "controller_task") or client.controller_task is None:
        log.info("🧠 Starting Controller for the first time...")
        client.controller_task = asyncio.create_task(Controller().run())
    else:
        log.info("🔁 Controller already running — skipping restart.")
    
    log.info("Successful login!")
    log.info(f'✅ Logged in as user {client.user})')
    
@client.event
async def on_disconnect():
    log.info("❌ Discord client has disconnected.")
    
@client.event
async def on_message(payload: discord.Message):
    author = payload.author
    
    if author != client.user and author.bot == False:
        if client.user in payload.mentions:
            channel = client.get_channel(payload.channel)
            
            try:
                await payload.reply("Hello!")
            except Exception as e:
                log.error("Error when replying.")
    
def login():
    max_tries = 5 # Max login attempts
    tries = 0 # Current number of attempts to login
    successful = False
    log.info(f"🔑 Attempting to log into Discord...")
    if not client.is_closed():
        try:
            client.run(os.environ.get('API-TOKEN'))
        except Exception as e:
            if client.is_closed():
                log.warn("❌ Discord client is closed. Exiting login attempts.")
    
login()
    

    


