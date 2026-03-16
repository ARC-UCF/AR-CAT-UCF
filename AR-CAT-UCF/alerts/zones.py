IGNORE_ZONES = [ # These zones, uh, are weird, and they make the bot break. So we'll ignore them :)
    "https://api.weather.gov/zones/fire/FLZ163",
    "https://api.weather.gov/zones/fire/FLZ167",
]

from config import config
from databases import fetch_zone_data, write_zone_data
from helpers import fetch_url_with_header
from logging.syslogger import log

COUNTIES = config.counties_to_watch

class Zones():
    
    def __init__(self):
        self.zone_map = {}
        self.zone_to_county = {} 
        self.state_appendix = {}
        self.zone_geometry = {}
        self.request_header = config.contact_header
        log.info(f"Initializing zone information")
        
        self.load_current_zone_db()
        self.determine_state_appendix()
        self.load_and_filter_zones()
        self.compile_zone_geometry()
        
    def determine_state_appendix(self):
        for c in COUNTIES: 
            parts = c.lower().strip().split(",")
            state_appendix = parts[1].strip()
            if state_appendix not in self.StateAppendixs:
                self.StateAppendixs[state_appendix] = state_appendix
            else: 
                log.info("Appendix already included.")
                
    def load_current_zone_db(self):
        stored = fetch_zone_data()
        
        if stored:
            for key, val in stored.items():
                self.zone_geometry[key] = val
                
    def load_and_filter_zones(self):
        self.discretionaryZoneMap = {}
        self.countyNormalized = {}
        
        links = [
            "https://api.weather.gov/zones?type=county&area=FL",
            "https://api.weather.gov/zones?type=forecast&area=FL",
            "https://api.weather.gov/zones?type=fire&area=FL",
        ]
        
        for url in links:
            r = fetch_url_with_header(url, self.request_header)
            
            if "features" not in r:
                log.critical(f"Did not get a response from API!")
                raise RuntimeError(f"No response from API!")
            
            for feature in r["features"]:
                if feature["id"] in IGNORE_ZONES:
                    log.info(f"Zone {feature["id"]} is in the ignore list, skipping the zone.")
                    continue
                
                zoneId = feature["id"]
                name = feature["properties"]["name"]
                state = feature["properties"]["state"] 
                self.discretionaryZoneMap[zoneId] = f"{name}, {state}"
        
        for c in COUNTIES: # Normalize county names for easier comparison and to avoid missing a zone with the correct county name.
            parts = c.lower().replace(",", "").strip().split()
            county_name = " ".join(parts[:-1])
            county_state = parts[-1] 
            self.countyNormalized[county_name] = f"{county_name}, {county_state}"
            
        for zone in self.discretionaryZoneMap: # Begin filtering out which zones we care about.
            parts = self.discretionaryZoneMap[zone].lower().replace(",", " ").strip().split() # Split by spaces and commas to handle different variations of County Names. Ie., Mainland Northern Brevard.
            
            formattedZoneName = None # Reset for each zone.
            
            for length in range(len(parts), 0, -1):
                for i in range(len(parts) - length + 1):
                    phrase = " ".join(parts[i:i+length])
                    if phrase in self.countyNormalized:
                        formattedZoneName = self.countyNormalized[phrase]
                        break
                if formattedZoneName:
                    break
                    
            if formattedZoneName and formattedZoneName in self.countyNormalized.values(): # Compare.
                log.info(f"✅ Match found: {self.discretionaryZoneMap[zone]} matches monitored county {formattedZoneName}")
                log.info(f"This matches with {zone}, which corresponds to {self.discretionaryZoneMap[zone]}")
                log.info(f"Therefore, adding {zone} to zone_map.")
                self.zone_map[zone] = zone
                parts = formattedZoneName.split(",")
                self.zone_to_county[zone] = parts[0]
                log.info(f"zone_to_county updated: {zone} → {parts[0]}")
                
        log.info(f"zone_map compiled. Contains {len(self.zone_map)} entries after filtering.") 
        log.info(f"Contains following zones: {self.zone_map}")
        log.info(f"zone_to_county: {self.zone_to_county}")
        
    def compile_zone_geometry(self):
        updated = False
        
        for z in self.zone_map:
            url = self.zone_map[z]
            
            if not url in self.zone_geometry:
                
                if not updated: updated = True
                
                r = fetch_url_with_header(url, self.request_header)
                
                if r["geometry"]:
                    geo = r["geometry"]
                    
                    self.zone_geometry[z] = geo
                    
                    log.info(f"Stored zone geometry from API for zone {z}")
                else:
                    log.warn(f"Unable to load geometry for zone {z}")
                    
        log.info(f"Compiled zone geometry.")
        
        if updated:
            write_zone_data(self.zone_geometry)
            
    def check_area_impacted(self, zones: list) -> tuple[bool, list]:
        impacted = [z for z in zones if z in self.zone_map]
        
        if len(impacted) > 0:
            return True, impacted
        return False, None
    
    def name_from_zone(self, zone_id: str) -> str: # Retrieve a county name from a ZoneID.
        if zone_id in self.zone_to_county: # If Zone_Id exists...
            return self.zone_to_county[zone_id] # ...return the county name.
        return None # Or return none if no zone is found in this list.
    
    def get_zone_geo(self, zone_id: str) -> list:
        if zone_id in self.zone_geometry:
            return self.zone_geometry[zone_id]
        return None
    
zones = Zones()