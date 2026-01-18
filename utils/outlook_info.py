import requests
from datetime import datetime, time
from utils import zoneManager
from shapely.geometry import shape, MultiPolygon

outlooks = {
    "day_1": "https://www.spc.noaa.gov/products/outlook/day1otlk_cat.lyr.geojson",
    "day_2": "https://www.spc.noaa.gov/products/outlook/day2otlk_cat.lyr.geojson",
    "day_3": "https://www.spc.noaa.gov/products/outlook/day3otlk_cat.lyr.geojson",
    "day_4": "https://www.spc.noaa.gov/products/exper/day4-8/day4prob.lyr.geojson",
    "day_5": "https://www.spc.noaa.gov/products/exper/day4-8/day5prob.lyr.geojson",
    "day_6": "https://www.spc.noaa.gov/products/exper/day4-8/day6prob.lyr.geojson",
    "day_7": "https://www.spc.noaa.gov/products/exper/day4-8/day7prob.lyr.geojson",
    "day_8": "https://www.spc.noaa.gov/products/exper/day4-8/day8prob.lyr.geojson",
}

conversions = {
    "day_1": "Day 1",
    "day_2": "Day 2",
    "day_3": "Day 3",
    "day_4": "Day 4",
    "day_5": "Day 5",
    "day_6": "Day 6",
    "day_7": "Day 7",
    "day_8": "Day 8",
}

RISK_ORDER = ["MRGL", "SLGT", "ENH", "MDT", "HIGH"]

class OutlookHandler():
    def __init__(self):
        print("Running")
        self.posted_outlooks = {}
        
    def check_area(self, day: str):
        hits = {}
        
        data = None
        
        link = outlooks[day]
        
        try:
            data = requests.get(link, timeout=10).json()
        except Exception as e:
            print(f"Error occurred: {e}")
                
        if data:
            for feature in data["features"]:
                geom = shape(feature["geometry"])
                props = feature.get("properties", {})
                risk_label = props["LABEL"]
                    
                if risk_label in RISK_ORDER: continue    
                    
                for county_name, county_coords in zoneManager.ZONE_GEOMETRY:
                    county_geom = MultiPolygon(county_coords)
                        
                    if geom.intersects(county_geom):
                        if county_name not in hits:
                            hits[county_name] = risk_label
                        elif county_name in hits:
                            currentRisk = hits[county_name]
                            currentPrio = RISK_ORDER.index(currentRisk)
                            newPrio = RISK_ORDER.index(risk_label)
                                
                            if newPrio > currentPrio:
                                print("New priority for county.")
                                hits[county_name] = risk_label
                                   
        return hits
    
    def create_day_information(self, day):
        msg = f"**Counties Impacted On $d**"
        
        impacted = self.check_area(day)
        
        highest_risk = "None"
        
        for county, risk in impacted.items():
            county = county.title()
            msg += f"\n{county} County"
            
            if highest_risk == "None": highest_risk = risk
            
            if RISK_ORDER.index(highest_risk) < RISK_ORDER.index(risk): highest_risk = risk
            
        return highest_risk, msg
                                
    