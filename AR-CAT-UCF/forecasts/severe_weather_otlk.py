from logger import log
from datetime import datetime, time
from geometry import zones, generate_outlook_image
from shapely.geometry import shape
from classes import RiskArea
from helpers import fetch_url, post_embed_with_image
import discord
from config import config

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

risk_names_full = {
    "MRGL": "Marginal",
    "SLGT": "Slight",
    "ENH": "Enhanced",
    "MDT": "Moderate",
    "HIGH": "High",
}

RISK_ORDER = ["MRGL", "SLGT", "ENH", "MDT", "HIGH"]

class SevereWeatherOtlk():
    def __init__(self):
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
    
    def check_outlook_day(self, day) -> tuple[dict, dict[str, RiskArea]]:
        hits = {}
        risks = {}
        
        link = outlooks[day]
        
        data = fetch_url(link)
        
        if not data:
            log.critical("Failed to get JSON!")
            return None
        
        if data:
            features = data.get("features", {})
            
            if features:
                for feature in features:
                    Risk = RiskArea.build_area(feature=feature)
                    
                    risks[Risk.label] = Risk
                    
                    if Risk.label not in RISK_ORDER: continue
                    
                    if not Risk.geometry: continue
                    
                    risk_geom = shape(Risk.geometry)
                    
                    for county_name, geom in zones.zone_geometry.items():
                        county_geom = shape(geom)
                    
                        true_name = zones.get_zone_geo(county_name)
                    
                        log.info(f"Comparing {true_name} county with risk geometry.")
                        
                        if risk_geom.intersects(county_geom):
                            if true_name not in hits:
                                log.info(f"New county hit for {true_name} on {Risk.title}")
                                hits[true_name] = Risk.label
                            elif true_name in hits:
                                currentRisk = hits[true_name]
                                currentPriority = RISK_ORDER.index(currentRisk)
                                newPriority = RISK_ORDER.index(Risk.label)
                                
                                if newPriority > currentPriority:
                                    log.info(f"{true_name} county has new priority of {newPriority}, upgrade from old priority {currentPriority}")
                                    hits[true_name] = Risk.label
        
        if hits and risks:
            return hits, risks
        else:
            return None, None
        
    def create_day_information(self, day: str, hits: dict, risks: dict[str, RiskArea]) -> tuple[str, str, str]:
        valid_str = datetime.fromisoformat(risks[0].valid) # Grab the valid time for the day based on the first risk in the table.
        expires_str = datetime.fromisoformat[risks[0].expires] # Grab the expired time from that same risk.
        
        header = f"$d Severe Weather Outlook From {valid_str} to {expires_str}" # Put the valid time and expire time in the header of the message.
        
        highest_risk = "None" # Set the highest risk to none by default.
        
        header = header.replace("$d", conversions[day]) # Replace the "day_#" format in the header with the "Day #" format
        
        base_body = f"The following counties are in the following severe weather risks: \n" # The base of the string body, which will list counties impacted.
        
        if hits is not None: # If we got hits
            for risk_label in risks.keys(): # Begin indexing each risk label by the risk dictionary keys.
                base_body += f"**In the {risk_names_full[risk_label]} risk:**" # Using the risk label key, fetch the full name of the risk, and then attach it as a header for a section.
                # This effectively lets us display which counties are in each risk.
                
                if highest_risk == "None": highest_risk = risk_label # If no previous highest risk has been set, set it to the current risk.
                
                if RISK_ORDER.index(highest_risk) < RISK_ORDER.index(risk_label): # Check the risk. If the highest risk is a lower priority then the current risk, set the highest risk to the current risk.
                    log.info(f"{risk_label} is replacing {highest_risk} as the highest risk for this day.")
                    highest_risk = risk_label
                
                for county, risk in hits.items(): # For each county and their risk, compare.
                    if risk_label == risk: # If the county's risk assignment is equal to the current risk we're indexing...
                        base_body += f"{county} County\n" # ...add it to the string of counties.
                        
                base_body += "\n" # Padding at the bottom for any extra strings (which we will add)
                
            return highest_risk, base_body, header # Return the highest risk, the message body, and the header.    
                        
    def run_check(self, day) -> tuple[dict, dict[str, RiskArea], str, str, str]:
        hits, risks = self.check_outlook_day(day=day)
        
        if not hits or risks: return None, None, None, None, None
        
        highest_risk, msg, header = self.create_day_information(day=day, hits=hits, risks=risks)
        
        if hits and risks and highest_risk and msg:
            return hits, risks, highest_risk, msg, header
        else:
            log.critical(f"Failed to return necessary information for severe weather outlooks!")
            return None, None, None, None, None
        
    async def check_and_post(self):
        log.info(f"Running severe weather outlook check at {datetime.isoformat(datetime.now())}")
        
        to_post = {}
        
        for day, data in self.posted_outlooks.items():
            if not "ran" in data:
                for period, info in self.posted_outlooks[day].items():
                    if info["Start"] <= datetime.now().time() <= info["End"] and not info["ran"]:
                        log.info(f"Checking outlook information for {day} at {period} or {datetime.now().time()}")
                        
                        hits, risks, highest_risk, msg, header = self.run_check(day=day)
                        
                        to_post[day] = {
                            "hits": hits,
                            "risks": risks,
                            "highest_risk": highest_risk,
                            "message": msg,
                            "header": header
                        }
                        
                        self.posted_outlooks[day][period]["ran"] = True
                        
            else:
                ran = data.get("ran")
                
                if ran is not None:
                    if not ran:
                        start = data.get("start")
                        end = data.get("end")
                        
                        if start and end:
                            if start <= datetime.now().time <= end:
                                
                                self.run_check(day=day)
                                
                                to_post[day] = {
                                    "hits": hits,
                                    "risks": risks,
                                    "highest_risk": highest_risk,
                                    "message": msg,
                                    "header": header
                                }
                                
                                self.posted_outlooks[day]["ran"] = True
        
        if to_post is not None:
            success = await self.push_posts(to_post=to_post)
            
            if success: return True
            
            return False
        
    async def push_posts(self, to_post: dict) -> bool:
        for day, data in to_post.items():
            risks = data["risks"] = RiskArea
            highest_risk = data.get("highest_risk", "")
            message = data.get("message", "")
            header = data.get("header", "")
            
            buf = generate_outlook_image(risks=risks)
            
            embed = discord.Embed(
                title=header,
                description=f"The highest risk for our area is {highest_risk}\n\n{message}\n\nThe above listed counties are in a severe weather threat: **be weather aware!**\nSevere weather risks indicate the potential for damaging wind gusts, large hail, and/or tornadoes within any storm that becomes severe. Listen to NOAA weather radio, local news stations, listen for outdoor sirens, have a cellular device, or have a method of communication with neighbors or other persons in the event a severe weather alert is issued for your area! The NWS recommends having at least threat methods of receiving alerts, in case one fails.",
                color=0x6382e0
            )
            
            embed.set_footer(text=config.version_id)
            
            embed.set_image(url="attachment://outlook_map.png")
            
            success = await post_embed_with_image(channel="forecast", embed=embed, buf=buf, fileName="outlook_map.png")
            
            if success:
                return True
            else:
                return False
            
    def reset_states(self):
        for day, data in self.posted_outlooks.items():
            if "run" not in data:
                for period, info in data.items():
                    info["ran"] = False
            else:
                data["ran"] = False
                        
                        
         
        