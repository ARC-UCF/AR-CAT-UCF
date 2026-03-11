import os
from dotenv import load_dotenv
from bot import client
import asyncio
from logging.syslogger import log

load_dotenv('./sensitive.env')

def login():
    if not client.is_closed():
        try:
            client.run(os.environ.get('API-TOKEN'))
        except Exception as e:
            if client.is_closed():
                log.error(f"Client is closed")
            else:
                log.error(f"Error while logging in: {e}")
                
commence = login()