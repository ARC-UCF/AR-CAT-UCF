class Determiner():
    
    def __init__(self):
        self.mTypes = {
            "alert": 3,
            "update": 2,
            "cancel": 1,
        }
        self.sTypes = {
            "extreme": 5,
            "severe": 4,
            "moderate": 3,
            "minor": 2,
            "unknown": 1,
        }
        self.cTypes = {
            "observed": 5,
            "likely": 4,
            "possible": 3,
            "unlikely": 2,
            "unknown": 1,
        }
        self.uTypes = {
            "immediate": 5,
            "expected": 4,
            "future": 3,
            "past": 2,
            "unknown": 1,
        }
        self.statusTypes = {
            "actual": 2,
            "test": 1,
            "unknown": 0,
        }
    
    def determine(self, WEA, messageType: str, severity: str, certainty: str, urgency: str):
        if WEA: # If WEAhandling is a parameter, then we know WEAS is activated.
            return "BULLETIN - WEA ACTIVIATION REQUESTED"
        
        if self.mTypes[str.lower(messageType)] >= 3 and self.sTypes[str.lower(severity)] >= 4 and self.cTypes[str.lower(certainty)] >= 4 and self.uTypes[str.lower(urgency)] >= 4: # Compare ranks, determine if EAS is likely.
            return "BULLETIN - IMMEDIATE BROADCAST REQUESTED"
        
        return None
            
determiner = Determiner()
            