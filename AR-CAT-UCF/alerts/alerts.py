from config import config
from logging.syslogger import log
import difflib
from datetime import datetime, timezone, timedelta
from geometry import zones
from helpers import fetch_url_with_header
from classes import Alert

storageTime = config.storage_time
polygonColors = config.alert_colors

IGNORE_LIST = [
    "TOR",
    "SVR",
    "FFW",
    "SVS",
    "SPS",
    "FFS",
]

class Alerts():
    def __init__(self):
        self.request_header = config.contact_header
        self.initialized = True
        self.ActiveAlerts = {}
        log.info("Alerts have been initialized")
        
    def cycle(self) -> dict:
        log.info("Running cycle")
        
    def first_or_empty(self, lst) -> list:
        return lst[0] if lst else ""
    
    def _filter_alerts(self):
        filtered_alerts = self._fetch_active_alerts()
        
        if not filtered_alerts: log.warn(f"No active alerts were found in this cycle. This could be an error: considering checking logs. Or, no alerts could be active at the current moment.")
        
        for alert in filtered_alerts:
            if alert.id not in self.ActiveAlerts:
                log.info(f"New alert appended: {alert.title} ({alert.id})")
                self.ActiveAlerts[alert.id] = alert
            else:
                log.info(f"This alert is already active {alert.title}")
        
    def _fetch_active_alerts(self) -> dict:
        compiled_alerts = []
        
        if not self.initialized:
            log.critical(f"The alerts service was not initialized!")
            raise RuntimeError(f"System not initialized!")
        
        alerts = self._poll_alerts()
        
        if not alerts: log.warn(f"No active alerts were found. This could be an error.")
        
        if not alerts["features"]: return None
        
        for alert in alerts["features"]:
            props = alert.get("properties")
            geometry = alert.get("geometry", {})
            
            if not props: log.error(f"Unable to locate properties for alert."); return # Guard statement
            
            parameters = props.get("parameters", {})
            
            if not props or not parameters: log.error(f"Unable to find alert properties or alert parameters."); return # Second guard statement, kinda redundant. This is to make sure all alerts we compile contain valid initial information. We want to make sure alerts work.
            
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
            
            param_values = {k: self.first_or_empty(parameters.get(k, [])) for k in param_keys} # Get values for keys. Point of this is to condense code.
            
            nws_headline = self.first_or_empty(parameters.get("NWSheadline", [])) or props.get("headline", "No title") # Apply helper function to headline.
            
            aZones = props.get("affectedZones", {})
            eventCode = props.get("eventCode", {})
            same_listing = eventCode.get("SAME", {})
            nws_listing = eventCode.get("NationalWeatherService", {}) # The SAME code sometimes isn't used, but the NWS listing is, so we get this one so we can later replace the SAME code if needed. In other cases, it won't be needed. But, in some cases, like Flood Advisories, no code is provided, so we replace the SAME code of none, with the NWS listing, which is "FAY"
            
            impacted, areas = zones.check_area_impacted(aZones)
            
            if impacted: # We only add the alert to our dict if it is in an impacted area.
                counties = []
                
                for a in areas:
                    county_name = zones.name_from_zone(a) # This bit of code gets the county name for the zone, and then adds it to a list, so we can use it in later features.
                    
                    log.info(f"This alert impacts {county_name} county")
                    
                    if county_name and county_name not in counties:
                        counties.append(county_name)
                        
                geom = None
                coordBase = None
                    
                if geometry and geometry["coordinates"]:
                    geom = geometry
                    coordBase = "Polygon"
                else:
                    geom = areas
                    coordBase = "County"
                        
                compiled_alerts.append(Alert.create_alert(feature=alert["features"], props=props, nws_headline=nws_headline, same=same_listing, nws=nws_listing, geom=geom, geom_base=coordBase, counties=counties, parameters=param_values))
                
        return compiled_alerts
        
    def _poll_alerts(self) -> dict:
        url = "https://api.weather.gov/alerts/active?area=FL"
        
        dict = fetch_url_with_header(url, self.request_header)
        
        if dict:
            return dict
        else:
            return None