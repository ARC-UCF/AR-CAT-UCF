import json
import warnings
from services.syslogger import log

fileLocation = "json_data.json"

class State():
    def __init__(self):
        self.data = {
            "forecast": {},
            "hurricane": {},
            "alerts": {},
            "timing": {},
            "trackId": {},
            "stats": {},
        }
        self.open_data()
        
    def open_data(self):
        try:
            with open(fileLocation) as f:
                data = json.load(f)
                log.info("File found and read.")
                if data:
                    self.data = data
        except (FileNotFoundError, Exception) as E:
            log.critical("Error while attempting to load JSON file!")
            raise RuntimeError(f"ERROR OCCURRED WHILE LOADING JSON FILE. ERROR: {E}")
            
    def write_data(self, forecast: dict | None, hurricane: dict | None, alerts: dict | None, timing: str | None, trackId: str | None, stats: dict | None):
        tempData = {
            "forecast": forecast,
            "hurricane": hurricane,
            "alerts": alerts,
            "timing": timing,
            "trackId": trackId,
            "stats": stats,
        }
        
        for d, v in tempData.items():
            if v is not None:
                self.data[d] = v
                
        try:
            with open(fileLocation, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as E:
            log.warn(f"ISSUE WHEN WRITING TO FILE: {E}")
                
    def send_to_disseminate(self):
        return self.data