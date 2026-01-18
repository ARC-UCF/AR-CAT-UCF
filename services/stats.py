from datetime import datetime, time

class AlertStatistics():
    def __init__(self):
        self.Statistics = {
            "postTimes": {
                "yearly": False,
                "monthly": False,
                "daily": False,
            },
            "stats": {},
        }
        
    def add_stat(self, counties: list, alertCode: str):
        stats = self.Statistics["stats"]
        
        refYear = str(datetime.now().year)
        refMonth = str(datetime.now().month)
        refDay = str(datetime.now().day)
        
        if refYear not in stats:
            stats[refYear] = {}
        year = stats[refYear]
        
        if refMonth not in year:
            year[refMonth] = {}
        month = year[refMonth]
        
        if refDay not in month:
            month[refDay] = {}
        day = month[refDay]
        
        if "individuals" not in day:
            day["individuals"] = {}
        
        ind = day["individuals"]
        
        currentCount = ind.get(alertCode, 0)
        
        if currentCount == 0:
            ind[alertCode] = 1
        else:
            ind[alertCode] = currentCount + 1
            
        for county in counties:
            if "counties" not in day:
                day["counties"] = {}
            dCounties = day["counties"]
            
            if county not in dCounties:
                dCounties[county] = {}
            
            c = dCounties[county]
            currentCount = c.get(alertCode, 0)
            
            if currentCount == 0:
                c[alertCode] = 1
            else:
                c[alertCode] = currentCount + 1
        
    def write_to_stats(self, newData):
        self.Statistics = newData
        
    def provide_stats(self) -> dict:
        return self.Statistics