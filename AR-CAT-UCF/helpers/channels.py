from config import config
from logger import log

class Channels():
    
    def __init__(self):
        self.synced_channels = {}
        self.synced = False
        log.info(f"Initializing channels")
        self.bot = None
        
    def sync_channels(self, bot):
        self.bot = bot
        
        for channel, cid in config.channels.items():
            discord_channel = self.bot.get_channel(cid)
            
            log.info(f"Syncing {channel}: {cid} -> {discord_channel}")
            
            self.synced_channels[channel] = discord_channel
            
        self.synced = True
        
    def get_channel_from_name(self, name: str):
        if not self.synced: log.error(f"Cannot get channels without being synced!"); return None
        
        if name in self.synced_channels:
            return self.synced_channels[name]
        
channels = Channels()