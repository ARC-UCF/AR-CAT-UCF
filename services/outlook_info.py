import requests
from datetime import datetime, time
from utils import zoneManager
from shapely.geometry import Polygon, shape, MultiPolygon
from services.syslogger import log

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
        self.posted_outlooks = {
            "day_1": {
                "morning": {
                    "ran": False,
                    "Start": time(9, 0),
                    "End": time(9, 30),
                },
                "afternoon": {
                    "ran": False,
                    "Start": time(12, 0),
                    "End": time(12, 30),
                },
                "evening": {
                    "ran": False,
                    "Start": time(16, 0),
                    "End": time(16, 30),
                },
                "night": {
                    "ran": False,
                    "Start": time(21, 0),
                    "End": time(21, 30),
                }
            },
            "day_2": {
                "morning": {
                    "ran": False,
                    "Start": time(9, 0),
                    "End": time(9, 30),
                },
                "evening": {
                    "ran": False,
                    "Start": time(13, 0),
                    "End": time(13, 30),
                }
            },
            "day_3": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
            "day_4": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
            "day_5": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
            "day_6": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
            "day_7": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
            "day_8": {
                "ran": False,
                "Start": time(12,0),
                "End": time(12,30),
            },
        }
        
    def check_area(self, day: str):
        print("Checking area")
        hits = {}
        
        data = None
        
        link = outlooks[day]
        
        try:
            data = requests.get(link, timeout=10).json()
        except Exception as e:
            print(f"Error occurred: {e}")
                
        if data:
            for feature in data["features"]:
                print("Found features")
                geom = shape(feature["geometry"])
                props = feature.get("properties", {})
                risk_label = props["LABEL"]
                    
                if risk_label not in RISK_ORDER: continue    
                
                if not geom: continue
                    
                for county_name, county_coords in zoneManager.ZONE_GEOMETRY.items():
                    polygons = []
                    for ply in county_coords:
                        polygons.append(Polygon(ply[0]))
                    multipoly = MultiPolygon(polygons)
                    
                    true_name = zoneManager.name_from_zone(county_name)
                    
                    print("Comparing county geometry " + true_name + " with outlook geometry.")
                        
                    if geom.intersects(multipoly):
                        if true_name not in hits:
                            print("New county hit: " + true_name + " with risk " + risk_label)
                            hits[true_name] = risk_label
                        elif true_name in hits:
                            currentRisk = hits[true_name]
                            currentPrio = RISK_ORDER.index(currentRisk)
                            newPrio = RISK_ORDER.index(risk_label)
                                
                            if newPrio > currentPrio:
                                print("New priority for county.")
                                hits[true_name] = risk_label
                                   
        return hits
    
    def create_day_information(self, day):
        msg = f"**Counties Impacted On $d**"
        
        impacted = self.check_area(day)
        
        highest_risk = "None"
        
        msg = msg.replace("$d", conversions[day])
        
        if impacted is not None:
            for county, risk in impacted.items():
                county = county.title()
                msg += f"\n{county} County"
            
                if highest_risk == "None": highest_risk = risk
            
                if RISK_ORDER.index(highest_risk) < RISK_ORDER.index(risk): highest_risk = risk
            
        return highest_risk, msg
    
    def get_outlook_geo(self, day):
        link = outlooks[day]
        
        try:
            data = requests.get(link, timeout=10).json()
            
            if data and data["features"]:
                return data["features"]
        except Exception as e:
            print(f"Error occurred: {e}")
            
    def check_to_return(self, day):
        hits = self.check_area(day)
        
        if not hits: return None, None, None, None
        
        highest_risk, msg = self.create_day_information(day)
        
        geom = self.get_outlook_geo(day)
        
        if not geom: return None, None, None, None
        
        return hits, highest_risk, msg, geom
            
    def check_outlook(self):
        print("Checking outlook")
        to_post = {}
        
        for day, data in self.posted_outlooks.items():
            if not "ran" in data:
                for time, info in self.posted_outlooks[day].items():
                    if info["Start"] <= datetime.now().time() <= info["End"] and not info["ran"]:
                        print("Checking outlook for " + day + " at time " + time)
                        hits, highest_risk, msg, geom = self.check_to_return(day)
                        
                        if hits is not None:
                            to_post[day] = {
                                "hits": hits,
                                "highest_risk": highest_risk,
                                "msg": msg,
                                "geom": geom,
                            }
                            
                        info["ran"] = True
            else:
                info = self.posted_outlooks[day]
                if info["Start"] <= datetime.now().time() <= info["End"] and not info["ran"]:
                    print("Checking outlook for " + day)
                    hits, highest_risk, msg, geom = self.check_to_return(day)
                    
                    if hits is not None:
                        to_post[day] = {
                            "hits": hits,
                            "highest_risk": highest_risk,
                            "msg": msg,
                            "geom": geom,
                        }
                        
                    info["ran"] = True
                    
        return to_post
            
    def reset_states(self):
        log.info("Resetting outlook states.")
        for day in self.posted_outlooks.values():
            if "ran" in day:
                day["ran"] = False
            else:
                for period in day.values():
                    period["ran"] = False
                
OtlkHandler = OutlookHandler()
