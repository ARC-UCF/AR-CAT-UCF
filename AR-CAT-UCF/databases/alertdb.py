import json
from logging.syslogger import log

FILE_LOCATION = "databases/alerts.json"

def fetch_alerts():
    try:
        with open(FILE_LOCATION) as f:
            data = json.load(f)
            log.info(f"Successfully read alertdb file.")
            
            if data:
                return data
    except (FileNotFoundError, Exception) as e:
        log.critical(f"Unable to load alertdb file: {e}")
        return {}
    
def write_alerts(data):
    try:
        with open(FILE_LOCATION, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.critical(f"Issue when writing a file: {e}")