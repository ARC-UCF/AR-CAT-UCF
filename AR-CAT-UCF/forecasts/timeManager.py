from datetime import datetime

class TimeManager():
    def __init__(self):
        self.lastRecordedTime = str(datetime.now().date())
        
    def check_new_day(self) -> bool: 
        currentTime = str(datetime.now().date())
        
        if currentTime != self.lastRecordedTime:
            self.lastRecordedTime = currentTime
            
            return True
        else:
            return False