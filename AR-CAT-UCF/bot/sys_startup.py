from .bot import client
from logging.syslogger import log
from config import config

def login():
    if not client.is_closed():
        try:
            client.run(config.token)
        except Exception as e:
            if client.is_closed():
                log.error(f"Client is closed")
            else:
                log.error(f"Error while logging in: {e}")