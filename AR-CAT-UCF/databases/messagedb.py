import json
from logging.syslogger import log

FILE_LOCATION = "databases/messages.json"

def fetch_messages() -> dict:
    try:
        with open(FILE_LOCATION) as f:
            data = json.load(f)
            log.info(f"Successfully loaded JSON file")
            
            if data:
                return data
    except (FileNotFoundError, Exception) as e:
        log.critical(f"Unable to load messages JSON file or it does not exist.")
        return {}
    
def write_messages(data):
    try:
        with open(FILE_LOCATION, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.critical(f"An error occurred while writing to file: {e}")
        