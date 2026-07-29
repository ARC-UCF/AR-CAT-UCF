from .bot import client
from logger import log
from config import config
import traceback

def login():
    if not client.is_closed():
        try:
            client.run(config.token)
        except Exception as e:
            traceback.print_exc()
            raise