import json
from logger import log
from dataclasses import asdict
from classes import Alert

FILE_LOCATION = "databases/alerts.json"

def fetch_alerts() -> dict:
    try:
        with open(FILE_LOCATION) as f:
            data = json.load(f)
            log.info(f"Successfully read alertdb file.")
            
            if data:
                return data
    except (FileNotFoundError, Exception) as e:
        log.critical(f"Unable to load alertdb file: {e}")
        return {}
    
def write_alerts(alerts: dict[str, Alert]):
    try:
        with open(FILE_LOCATION, "w") as f:
            json.dump([asdict(alert) for key, alert in alerts.items()], f, indent=4)
    except Exception as e:
        log.critical(f"Issue when writing a file: {e}")