import json
from logger import log

FILE_LOCATION = "databases/hurricane.json"

def fetch_hurricane() -> dict:
    log.info(f"Reading hurricane json.")
    try:
        with open(FILE_LOCATION) as f:
            data = json.load(f)
            log.info(f"Successfully read hurricanedb file")
            
            if data is not None:
                log.info(data)
            
            if data:
                return data
    except (FileNotFoundError, Exception) as e:
        log.critical(f"Unable to load hurricanedb file or it does not exist")
        return {}
    
def write_hurricane(data):
    try:
        with open(FILE_LOCATION, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.critical(f"Error while writing file: {e}")