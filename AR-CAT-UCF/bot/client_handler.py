from .bot import client
from logger import log
    
@client.event
async def on_disconnect():
    log.warn(f"Client disconnected!")