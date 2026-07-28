from datetime import datetime
from logger import log

class TimeManager():
    def __init__(self):
        self.lastRecordedTime = str(datetime.now().date())
        
    def check_new_day(self) -> bool: 
        currentTime = str(datetime.now().date())
        
        if currentTime != self.lastRecordedTime:
            log.info(f"It is a new day, timings will be reset.")
            self.lastRecordedTime = currentTime
            
            return True
        else:
            log.info(f"Not yet a new day.")
            return False