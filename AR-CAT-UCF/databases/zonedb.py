import json
from logger import log

FILE_LOCATION = "databases/zones.json"

def fetch_zone_data():
    try:
        with open(FILE_LOCATION) as f:
            data = json.load(f)
            log.info(f"Successfully read zonedb file.")
            
            if data:
                return data
    except (FileNotFoundError, Exception) as e:
        log.critical(f"Unable to load zonedb file or it does not exist: {e}")
        return {}
    
def write_zone_data(data):
    try:
        with open(FILE_LOCATION, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.critical(f"Issue when writing data to file: {e}")