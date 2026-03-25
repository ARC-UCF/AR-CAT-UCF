from config import config
from logging.syslogger import log
import difflib
from datetime import datetime, timezone, timedelta
from geometry import zones

storageTime = config.storage_time
polygonColors = config.alert_colors

IGNORE_LIST = [
    "TOR",
    "SVR",
    "FFW",
    "SVS",
    "SPS",
    "FFS",
]

class Alerts():
    def __init__(self):
        self.request_header = config.contact_header
        self.initialized = True
        self.ActiveAlerts = {}
        log.info("Alerts have been initialized")
        
    def cycle(self) -> dict:
        log.info("Running cycle")
        
        