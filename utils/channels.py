import os 
import json
from dotenv import load_dotenv
import config
from services.syslogger import log
load_dotenv("sensitive.env")

from discord import SyncWebhook
from bot import client

class Channels():
    
    def __init__(self):
        self.SYNCED_CHANNELS = {}
        self.synced = False
        log.info("initalizing CHANNELS")
        
    def sync_channels(self): # Probably a better way to handle this, but we'll work about that later.
        for channel, cId in config.channels.items():
            self.SYNCED_CHANNELS[channel] = client.get_channel(cId)
        
        self.synced = True
                
    def get_channel_from_county(self, county: str):
        if county in self.SYNCED_CHANNELS:
            return self.SYNCED_CHANNELS[county]
        
channels = Channels()