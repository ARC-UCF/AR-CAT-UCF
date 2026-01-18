import datetime
from datetime import datetime

class Time():
    
    def __init__(self):
        self.LastDate = str(datetime.now().date())
        
    def is_new_day(self):
        Today = str(datetime.now().date())
        if self.LastDate != Today:
            self.LastDate = Today
            return True
        else:
            return False
        
    def write_last_date(self, varToWrite: str):
        self.LastDate = varToWrite
    
    def provide(self):
        return self.LastDate