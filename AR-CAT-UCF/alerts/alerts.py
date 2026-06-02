from config import config
from logging.syslogger import log
import difflib
from datetime import datetime, timezone, timedelta
from geometry import zones
from helpers import AsyncLinks, channels
from classes import Alert
from databases import fetch_alerts, write_alerts
import asyncio

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
        self.ActiveAlerts: dict[Alert] = {}
        log.info("Alerts have been initialized")
        
    async def cycle(self) -> dict:
        log.info("Running cycle")
        
        await self._filter_alerts()
        
        asyncio.sleep()
        
    def normalize(self, text: str) -> str:
        return text.lower().strip()
    
    def load_alerts(self):
        alerts = fetch_alerts()
        
        for a in alerts:
            alert = Alert.from_dict(a)
            
            self.ActiveAlerts[alert.id] = alert
            
    async def post_alerts(self):
        for alert in self.ActiveAlerts:
            if not alert.posted and not alert.ignore:
                log.info(f"Working alert {alert.id}")
                
                
    
    def save_alerts(self):
        write_alerts(self.ActiveAlerts)
        
    def first_or_empty(self, lst) -> list: # Helper function for lists.
        return lst[0] if lst else ""
    
    async def _filter_alerts(self): # Filter alerts.
        filtered_alerts: list[Alert] = await self._fetch_active_alerts()
        
        if not filtered_alerts: log.warn(f"No active alerts were found in this cycle. This could be an error: considering checking logs. Or, no alerts could be active at the current moment.")
        
        for alert in filtered_alerts:
            for a in self.ActiveAlerts:
                replaces, method = self._check_for_ref(alert, a)
                
                if replaces and method == "references":
                    alert.ignore_this_alert()
                    alert.same = a.same
                elif replaces and method == "replaces":
                    alert.same = a.same
                    
                if self._check_for_similar(alert, a):
                    alert.ignore_this_alert()
            
            if alert.id not in self.ActiveAlerts:
                log.info(f"New alert appended: {alert.title} ({alert.id})")
                self.ActiveAlerts[alert.id] = alert
            else:
                log.info(f"This alert is already active {alert.title}")
                
    def _check_for_similar(self, alert1: Alert, alert2: Alert) -> bool:
        
        a1_norm_title = self.normalize(alert1.title)
        a1_norm_desc = self.normalize(alert1.desc)
        a2_norm_title = self.normalize(alert2.title)
        a2_norm_desc = self.normalize(alert2.desc)
        
        title_ratio = difflib.SequenceMatcher(None, a1_norm_title, a2_norm_title).ratio() * 100
        desc_ratio = difflib.SequenceMatcher(None, a1_norm_desc, a2_norm_desc).ratio() * 100
        
        if title_ratio >= 85.0 and desc_ratio >= 85.0:
            log.info(f"Alert is similar, {alert1.id} and {alert2.id} are similar")
            return True
        
        log.info(f"{alert1.id} is not similar to {alert2.id}")
        return False
        
                
    def _check_for_ref(self, alert1: Alert, alert2: Alert) -> tuple[bool, str]:
        alert1_refs = alert1.get("references")
        alert2_refs = alert2.get("references")
        
        if alert1_refs:
            for r in alert1_refs:
                if r["@id"] == alert2.id:
                    return True, "references"
        
        if alert2_refs:
            for r in alert2_refs:
                if r["@id"] == alert1.id:
                    return True, "references"
                
        alert2_replace = alert2.replacedBy
        
        if alert2_replace:
            if alert2_replace == alert1.id :
                return True, "replaces"
            
        return False, "no"
        
    async def _refresh_current_alerts(self):
        if not self.ActiveAlerts: log.warn(f"No alerts were active to filter through or update."); return
        
        refAlerts = await self._poll_old_alerts()
        
        if not refAlerts: log.warn(f"Unable to compile list of old alerts."); return
        
        if not refAlerts["features"]: log.error(f"Unable to find features property for old alerts."); return
        
        for alert in alert["features"]:
            if not alert["id"]: log.error(f"This alert has no id") # Id is separate from properties, so we check id first.
            
            aid = alert["id"]
            
            if aid in self.ActiveAlerts: # If the id is in active alerts, then it's worth checking.
                log.info(f"{aid} is in active alerts.")
                props = alert.get("properties")
                
                if not props: log.error(f"Unable to locate properties for this alert."); continue
            
                parameters = props.get("parameters", {})
            
                if not props or not parameters: log.error(f"Unable to find alert properties or alert parameters."); continue
                
                replacedBy = props.get("replacedBy", "")
                
                if replacedBy:
                    replacedAt = props.get("replacedAt")
                    localAlert: Alert = self.ActiveAlerts[aid]
                    
                    if localAlert.replacedBy is None:
                        log.info(f"Alert {aid} was replaced by {replacedBy}")
                        localAlert.replacedBy = replacedBy
                        localAlert.replacedAt = replacedAt
                        
                references = props.get("references", {})
                
                if references:
                    localAlert: Alert = self.ActiveAlerts[aid]
                    
                    if localAlert.references is None:
                        log.info(f"Updated references for {aid}")
                        localAlert.references = references
                    else:
                        log.info(f"{aid} has updated references.")
                        if localAlert.references != references:
                            localAlert.references = references
                    
        
    async def _fetch_active_alerts(self) -> dict:
        compiled_alerts = []
        
        if not self.initialized:
            log.critical(f"The alerts service was not initialized!")
            raise RuntimeError(f"System not initialized!")
        
        alerts = await self._poll_alerts()
        
        if not alerts: log.warn(f"No active alerts were found. This could be an error.")
        
        if not alerts["features"]: return None
        
        for alert in alerts["features"]:
            props = alert.get("properties")
            geometry = alert.get("geometry", {})
            
            if not props: log.error(f"Unable to locate properties for alert."); continue # Guard statement
            
            parameters = props.get("parameters", {})
            
            if not props or not parameters: log.error(f"Unable to find alert properties or alert parameters."); continue # Second guard statement, kinda redundant. This is to make sure all alerts we compile contain valid initial information. We want to make sure alerts work.
            
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
    
    async def _poll_alerts(self) -> dict: 
        # Right now this gets and returns only the active alerts.
        # We may want to consider making this poll api.weather.gov/alerts?area=FL instead, and find which alerts are new and issue them, while also simultaneously be able to verify and track which alerts are replacing and updating others.
        # This is asynchronous.
        url = "https://api.weather.gov/alerts/active?area=FL"
        
        dict = await AsyncLinks.fetch_url_with_header(url=url, header=config.contact_header)
        
        if dict:
            return dict
        else:
            return None
        
    async def _poll_old_alerts(self) -> dict:
        url = "https://api.weather.gov/alerts?area=FL"
        
        dict = await AsyncLinks.fetch_url_with_header(url=url, header=config.contact_header)
        
        if dict:
            return dict
        else:
            return None