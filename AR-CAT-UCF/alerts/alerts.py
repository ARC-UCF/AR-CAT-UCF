from config import config
from logging.syslogger import log
import difflib
from datetime import datetime, timezone, timedelta
from geometry import zones

storageTime = config.storage_time
polygonColors = config.alert_colors

