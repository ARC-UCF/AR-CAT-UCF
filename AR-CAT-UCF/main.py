from bot import login
from logging.syslogger import log

class Controller():
    def __init__(self):
        log.info(f"Controller initialized.")
        

def run():
    login()
    
    