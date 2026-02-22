from utils import zoneManager, identifier
from services.syslogger import log
import difflib
import requests
import os
from dotenv import load_dotenv
import datetime
from datetime import datetime, timezone, timedelta, time
from config import polygon_colors_SAME, storageTime
load_dotenv('../sensitive.env')

IGNORE_LIST = [
    "SVR",
    "TOR",
    "FFW",
    "FFS",
    "SVS",
    "SPS",
]

zones = zoneManager

class Alerts():
    
    def __init__(self): # Initalize
        self.requestHeader = {"User-Agent": os.environ.get('HEADER')}
        self.initialized = True
        self.ActiveAlerts = {}
        log.info("Alerts SERIVCE initialized.")
        
    def normalize(self, text: str) -> str:
        return text.lower().strip()
        
    def cycle(self) -> dict: # Public function called for the function to cycle.
        log.info("Cycling")
        self._clean_up() # Clean up
        # Best to do this first to avoid posting alerts that are no longer active.
        
        aList = self._retrieve_alerts_and_organize() # Fetch alerts
        
        if aList:
            for alert in aList: # Begin checking alerts.
                polyColor = '#6e6e6e'
                
                if alert["SAME_code"] == "NWS": alert["SAME_code"] = alert["NWS_code"]
                
                if alert["SAME_code"] in polygon_colors_SAME:
                    polyColor = polygon_colors_SAME[alert["SAME_code"]]
                    
                alert["polyColor"] = polyColor
                
                log.info(f"Checking {alert["id"]} for existence in active alerts.")
                
                if alert["id"] not in self.ActiveAlerts: # If we don't have the alert, add it.
                    replacement, ref, Type = self._check_for_replacement(alert)
                    
                    if replacement and ref in self.ActiveAlerts and Type == "replaced":
                        log.info("Alert is a replacement.")
                        alert["trackId"] = self.ActiveAlerts[ref]["trackId"]
                        alert["polyColor"] = self.ActiveAlerts[ref]["polyColor"]
                        alert["Replacement"] = True
                    if replacement and ref in self.ActiveAlerts and Type == "referenced":
                        log.info("Alert is referenced elsewhere.")
                        alert["trackId"] = self.ActiveAlerts[ref]["trackId"]
                        alert["polyColor"] = self.ActiveAlerts[ref]["polyColor"]
                        alert["Referenced"] = True
                        
                    similar, ref = self._check_for_similar(alert)
                    
                    if similar and ref in self.ActiveAlerts:
                        log.info("Alert is similar to an existing alert.")
                        alert["trackId"] = self.ActiveAlerts[ref]["trackId"]
                        alert["polyColor"] = self.ActiveAlerts[ref]["polyColor"]
                        alert["ignore"] = True
                        
                    if not similar and not replacement:
                        alert["trackId"] = identifier.issue_identifier()
                        log.info(f"Track Identifier added, {alert["trackId"]}")
                        
                    log.info(f"{alert["id"]} adding to active alerts.")
                        
                    self.ActiveAlerts[alert["id"]] = alert
        else: 
            log.warn("no alert list compiled. This may be an error, check internals.")
                    
        log.info("Complete: returning activealerts")
        return self.ActiveAlerts
    
    def _check_for_replacement(self, alert: dict) -> tuple[bool, str]:
        log.info("checking replacements")
        
        for key, info in self.ActiveAlerts.items():
            refs = info.get("references", "")
            replacedBy = info.get("replacedBy", "")
            
            if replacedBy:
                if replacedBy == alert["id"]:
                    log.info(f"{alert["id"]} is a replacement of {key}")
                    return True, key, "replaced"
                
            if refs:
                for r in refs:
                    if r["@id"] == alert["id"]:
                        log.info(f"{alert["id"]} is referenced in {key}")
                        return True, key, "referenced" 
        
        references = alert.get("references", None)
        
        if references:
            for ref in references:
                refId = ref["@id"]
            
                if refId and refId in self.ActiveAlerts:
                    compareAlert = self.ActiveAlerts[refId]
                
                    replacedBy = compareAlert.get("replacedBy", "")
                
                    if replacedBy is not None:
                        if replacedBy == alert["id"]:
                            log.info("Alert Id matches replacement id for another alert.")
                            return True, refId, "replaced"
                
                    return True, refId, "referenced"
            
                info = self._poll_internal_alerts(refId)
            
                if info and info["properties"]:
                    props = info["properties"]
                
                    replacedBy = props.get("replacedBy", "")
                    replacedAt = props.get("replacedAt", "")
                    rRefs = props.get("references", None)
                
                    if replacedBy:
                        if refId and refId in self.ActiveAlerts:
                            self.ActiveAlerts[refId]["replacedBy"] = replacedBy
                            self.ActiveAlerts[refId]["replacedAt"] = replacedAt
                    
                        if replacedBy == alert["id"] and replacedBy in self.ActiveAlerts:
                            log.info("Alert Id matches replacement id for another alert.")
                            return True, refId, "replaced"
                    else:
                        return True, refId, "referenced"
        
        log.info("Referenced alerts are not recorded.")
        
        return False, None, None
        
    def _clean_up(self): # Clean up our alerts; remove expired alerts or alerts which are expireless.
        log.info("Cleaning")
        now = datetime.now(timezone.utc)
        for aid, data in list(self.ActiveAlerts.items()):
            expires = data.get("expires")
            if not expires or datetime.fromisoformat(expires) + timedelta(hours=storageTime) < now:
                del self.ActiveAlerts[aid]
        
    def _retrieve_alerts_and_organize(self) -> list:
        log.info("Retrieving alerts.")
        compiled_alerts = []
        def first_or_empty(lst): # Helper function for condensing code. Returns important information.
            return lst[0] if lst else ""
        
        if not self.initialized: 
            raise RuntimeError("System not initialized!") # Why haven't you initialized???
        alerts = self._poll_active_alerts() # Poll active alerts from API.
        
        if not alerts: log.warn ("No alerts found."); return None # Gate; return if no alerts exist.
        
        if not alerts["features"]: return None # If "features" is null.
        
        for feature in alerts["features"]: # Define basic parameters.
            props = feature.get("properties")
            geometry = feature.get("geometry", {})
            parameters = props.get("parameters", {})
            
            param_keys = [ # Parameter keys.
                "hailThreat",
                "windThreat",
                "maxWindGust",
                "maxHailSize",
                "tornadoDamageThreat",
                "thunderstormDamageThreat",
                "flashfloodDamageThreat",
                "WEAHandling",
                "tornadoDetection",
                "BLOCKCHANNEL",
                "VTEC",
                "AWIPSidentifier",
                "WMOidentifier",
                "eventMotionDescription",
                "expiredReferences",
            ]
            param_values = {k: first_or_empty(parameters.get(k, [])) for k in param_keys} # Get values for keys. Point of this is to condense code.
            
            nws_headline = first_or_empty(parameters.get("NWSheadline", [])) or props.get("headline", "No title") # Apply helper function to headline.
            
            aZones = props.get("affectedZones", [])
            eventCode = props.get("eventCode", {})
            SAME_LIST = eventCode.get("SAME", [])
            NWS_LIST = eventCode.get("NationalWeatherService", [])
            
            impacted, areas = zones.check_areas_impacted(aZones) # Check if any areas listed in the alert data are impacted by this alert.
            
            if impacted: # If an area or multiple areas are impacted, continue to append information to the alert.
                counties = []
                
                for a in areas:
                    countyName = zones.name_from_zone(a)
                    
                    log.info(countyName)
                    
                    if countyName and countyName not in counties:
                        counties.append(countyName)
                    
                
                coordinates = None
                coordBase = None # Used as a discriminator for geometry script.
                
                if geometry and geometry["coordinates"]: 
                    coordinates = geometry.get("coordinates")
                    coordBase = "Polygon" # Use polygon for storm-based alerts.
                else:
                    coordinates = [zones.get_zone_geo(a) for a in areas] # Check area to zone geodata.
                    coordBase = "Area" # Area for county-based or region-based alerts.
                    
                compiled_alerts.append({ # Compile each individual alert that we have.
                    "id": feature["id"],
                    "sent": props.get("sent", ""),
                    "expires": props.get("expires", ""),
                    "title": nws_headline,
                    "secondary_title": props.get("headline", "No secondary title"),
                    "areaDesc": props.get("areaDesc", ""),
                    "desc": props.get("description", ""),
                    "instruction": props.get("instruction", ""),
                    "messageType": props.get("messageType", ""),
                    "SAME_code": SAME_LIST[0],
                    "NWS_code": NWS_LIST[0],
                    "status": props.get("status", ""),
                    "certainty": props.get("certainty", ""),
                    "severity": props.get("severity", ""),
                    "urgency": props.get("urgency", ""),
                    "senderName": props.get("senderName", ""),
                    "response": props.get("response", ""),
                    "event": props.get("event", "UNSPECIFIED"),
                    "coords": coordinates,
                    "base": coordBase,
                    "countiesAffected": counties,
                    "references": props.get("references", ""),
                    "replacedBy": props.get("replacedBy", ""),
                    "replacedAt": props.get("replacedAt", ""),
                    "ignore": False,
                    **param_values,
                })
        
        return compiled_alerts # Return list of compiled alerts.
    
    def check_internal(self): # Internally check alerts: add specific information if it's been added.
        if self.ActiveAlerts == None: 
            log.info(f"❌ No alerts to filter. {len(self.ActiveAlerts)} are active.")
            return
        
        totalChecked = 0
        failed = 0
        completed = 0
        updated = 0
        
        for alert, info in self.ActiveAlerts.items():
            
            wasUpdated = False
            didFail = False
            
            totalChecked += 1
            newInfo = self._poll_internal_alerts(alert)
            
            if newInfo and newInfo["properties"]:
                props = newInfo["properties"]
                
                replacedBy = props.get("replacedBy", "")
                replacedAt = props.get("replacedAt", "")
                references = props.get("references", "")
                
                if replacedBy or references: 
                    if replacedBy and not info.get("replacedBy"):
                        self.ActiveAlerts[alert]["replacedBy"] = replacedBy
                        self.ActiveAlerts[alert]["replacedAt"] = replacedAt 
                        wasUpdated = True
                    if references:
                        if self.ActiveAlerts[alert].get("references") != references:
                            self.ActiveAlerts[alert]["references"] = references
                            wasUpdated = True
            else:
                failed += 1
                didFail = True
            
            if wasUpdated:
                updated += 1
            
            if not didFail:
                completed += 1
        
        log.info(f"Completed internal checks. {totalChecked} alerts checked, {failed} alerts failed to be checked, {completed} were successfully checked, and {updated} alerts were updated.")
        
    def _check_for_similar(self, alert: dict) -> tuple[bool, str]:
        
        if alert["SAME_code"] in IGNORE_LIST:
            log.info(f"Skipping similarity check for {alert["id"]} because the SAME code is for an alert which might be similar in text but unique in location and other factors.")
            return False, None
        
        log.info("Checking for similar alerts.")
        norm_title = self.normalize(alert["title"])
        norm_description = self.normalize(alert["desc"])
        
        for key, info in self.ActiveAlerts.items():
            if key == alert["id"]:
                continue
            
            ref_title = self.normalize(info["title"])
            ref_description = self.normalize(info["desc"])
            
            title_ratio = difflib.SequenceMatcher(None, norm_title, ref_title).ratio() * 100
            desc_ratio = difflib.SequenceMatcher(None, norm_description, ref_description).ratio() * 100
            
            log.info(f"{alert["id"]} vs {key}: Title similarity {title_ratio:.2f}%, Description similarity {desc_ratio:.2f}%")
            
            if title_ratio >= 85.0 and desc_ratio >= 85.0:
                log.info(f"Similar alert found: {key} and {alert["id"]} with title similarity {title_ratio:.2f}% and description similarity {desc_ratio:.2f}%")
                return True, key
            
        log.info("No similar alerts were found.")
        return False, None
        
    def _poll_active_alerts(self) -> dict:
        url = "https://api.weather.gov/alerts/active?area=FL"

        try:
            r = requests.get(url, headers=self.requestHeader)  # keep as Response object
            if r.status_code != 200:
                log.error(f"⚠️ API returned status {r.status_code}: {r.text[:200]}")
                return []

            try:
                return r.json()
            except requests.exceptions.JSONDecodeError:
                log.error("⚠️ Response was not valid JSON!")
                log.error(f"Response text: {r.text[:200]}")  # Log first 200 chars
                return []
        except requests.exceptions.RequestException as e:
            log.error(f"⚠️ Request failed: {e}")
            return []
        
    def _poll_internal_alerts(self, url: str):
        try:
            r = requests.get(url, headers=self.requestHeader)  # keep as Response object
            if r.status_code != 200:
                log.error(f"⚠️ API returned status {r.status_code}: {r.text[:200]}")
                return []

            try:
                return r.json()
            except requests.exceptions.JSONDecodeError:
                log.error("⚠️ Response was not valid JSON!")
                log.error(f"Response text: {r.text[:200]}")  # Log first 200 chars
                return []
        except requests.exceptions.RequestException as e:
            log.error(f"⚠️ Request failed: {e}")
            return []
        
    def provide_alerts(self):
        return self.ActiveAlerts
    
    def write_to_alerts(self, data: dict):
        self.ActiveAlerts = data
        
alerts = Alerts()