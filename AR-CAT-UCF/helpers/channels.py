import config
from logger import log

from bot import client

class Channels():
    
    def __init__(self):
        self.synced_channels = {}
        self.synced = False
        log.info(f"Initializing channels")
        self.sync_channels()
        
    def sync_channels(self):
        for channel, cid in config.channels.items():
            self.synced_channels[channel] = client.get_channel(cid)
            
        self.synced = True
        
    def get_channel_from_name(self, name: str):
        if name in self.synced_channels:
            return self.synced_channels[name]
        
channels = Channels()