from config import config
from logger import log
import difflib
from datetime import datetime, timezone, timedelta
from geometry import zones
from helpers import AsyncLinks, channels, post_embed_with_image, post_message
from classes import Alert
from databases import fetch_alerts, write_alerts
import asyncio
from alerts.determiner import determiner
from io import BytesIO
import discord
from geometry import generate_alert_image, ucf_in_or_near_polygon

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
        self.severity_colors = { # This severity index is based on the severity property in alerts.
            "Extreme": 0xA020F0,   # Purple
            "Severe": 0xFF0000,    # Red
            "Moderate": 0xFFA500,  # Orange
            "Minor": 0xFFFF00,     # Yellow
            "Unknown": 0x808080    # Gray
        }
        self.load_alerts()
        
    async def cycle(self) -> dict:
        log.info("Running cycle")
        
        await self._filter_alerts()
        
        log.info(f"Posting alerts")
        
        await self.post_alerts()
        
        write_alerts(self.ActiveAlerts)
        
        await asyncio.sleep(30)
        
        log.info(f"Refreshing alerts.")
        
        await self._refresh_current_alerts()
        
        await asyncio.sleep(30)
        
    def normalize(self, text: str) -> str:
        return text.lower().strip()
    
    def load_alerts(self):
        alerts = fetch_alerts()
        
        for a in alerts:
            alert = Alert.from_dict(a)
            
            self.ActiveAlerts[alert.id] = alert
            
    async def post_alerts(self):
        for _, alert in self.ActiveAlerts.items():
            if not alert.posted and not alert.ignore:
                log.info(f"Working alert {alert.id}")
                
                # Begins the process of compiling the alert.
                
                severity = alert.severity or "unknown"
                color = self.severity_colors.get(severity, 0x808080)
                
                header = f"{alert.title}"
                
                header = (header[:256-4] + "...") if len (header) > 256 else header
                
                preambleList = [
                    "WMOidentifier",
                    "AWIPSidentifier",
                    "VTEC",
                    "space",
                    "event",
                    "senderName",
                    "bulletin",
                ]
                
                preamble_lines = []
                
                for param in preambleList:
                    if param == "space":
                        preamble_lines.append("")
                    elif param == "bulletin":
                        bulletin = determiner.determine(alert.parameters.get("WEAHandling", ""), alert.messageType, alert.severity, alert.certainty, alert.urgency)
                        if bulletin:
                            preamble_lines.append(bulletin)
                    elif param == "senderName":
                        preamble_lines.append(alert.senderName)
                    elif alert.parameters.get(param, ""):
                        preamble_lines.append(alert.parameters.get(param, ""))
                        
                preambleString = "\n".join(preamble_lines)
                
                main_lines = []
                
                if alert.secondary_title: main_lines.append(alert.secondary_title)
                if alert.desc: main_lines.append(alert._scrub_text(alert.desc))
                
                mainString = "\n\n".join(main_lines)
                
                trunc_text = (mainString[:3850-3] + "...") if len(mainString) > 3850 else mainString
                
                if alert.parameters.get("eventMotionDescription"): trunc_text = trunc_text + "\n\n" + alert.parameters.get("eventMotionDescription")
                
                full_body = preambleString + "\n\n" + trunc_text
                
                info_lines = []
                
                information_to_fetch = {
                    "hailThreat": "Hail Threat: ",
                    "maxHailSize": "Max Hail Size: ",
                    "windThreat": "Wind Threat: ",
                    "maxWindGust": "Max Wind Gust: ",
                    "tornadoDetection": "Tornado Detection: ",
                    "tornadoDamageThreat": "Damage Threat: ",
                    "thunderstormDamageThreat": "Damage Threat: ",
                    "flashfloodDamageThreat": "Damage Threat: ",
                }
                
                if alert.id: info_lines.append("Alert Id: " + alert.id)
                if alert.same: 
                    if alert.same == "NWS":
                        alert.same = alert.nws
                        
                    info_lines.append("SAME: " + alert.same)
                    
                if alert.severity: info_lines.append("Severity: " + alert.severity)
                if alert.urgency: info_lines.append("Urgency: " + alert.urgency)
                if alert.certainty: info_lines.append("Certainty: " + alert.certainty)
                if alert.response: info_lines.append("Response: " + alert.response)
                
                for key, lead in information_to_fetch.items():
                    if alert.parameters.get(key):
                        info_lines.append(lead + alert.parameters.get("key"))
                
                infoMessage = "\n".join(info_lines)
                
                embed = discord.Embed(
                    title=header,
                    description=full_body,
                    color=color
                )
                
                if alert.instruction:
                    instruction_text = alert._scrub_text(alert.instruction)
                    
                    embed.add_field(name="Precautionary/Preparedness Instructions", value=instruction_text, inline=False)
                    
                embed.add_field(name="Alert Information", value=infoMessage, inline=False)
                embed.set_footer(text=config.version_id)
                
                buf = generate_alert_image(alert.geom, alert.geo_base, alert.same)
                
                fileName = "alert_map.png"
                
                embed.set_image(url="attachment://alert_map.png")
                
                for county in alert.counties:
                    channel = channels.get_channel_from_name(county)
                    
                    if channel:
                        log.info(f"Channel found for {county}")
                        
                        if alert.same in config.ping_alerts and alert.status == "Actual":
                            ping = config.ping_roles[county]
                            successful = await post_message(channel=channel, content=ping)
                            
                            if successful:
                                log.info(f"Ping sent")
                            
                        success = await post_embed_with_image(channel=channel, content=embed, buf=buf, fileName=fileName)
                        if success:
                            log.info(f"Embed sent with image.")
                    if county == "orange" and alert.geo_base == "County":
                        channel = channels.get_channel_from_name("arc")
                        
                        if alert.same in config.ping_alerts and alert.status == "Actual":
                            ping = config.ping_roles["arc"]
                            successful = await post_message(channel=channel, content=ping)
                            
                            if successful:
                                log.info(f"Sent ping successfully")
                        
                        success = await post_embed_with_image(channel=channel, content=embed, buf=buf, fileName=fileName)
                        
                        if success:
                            log.info(f"Sent embed successfully")
                    if (county == "orange" or county == "seminole") and alert.geo_base == "Polygon":
                        ucfAffected = ucf_in_or_near_polygon(alert.geom)
                        
                        if ucfAffected:
                            channel = channels.get_channel_from_name("arc")
                            
                            if alert.same in config.ping_alerts and alert.status == "Actual":
                                ping = config.ping_roles["arc"]
                                successful = await post_message(channel=channel, content=ping)
                                
                                if successful:
                                    log.info(f"Sent ping successfully")
                                    
                            success = await post_embed_with_image(channel=channel, content=embed, buf=buf, fileName=fileName)
                            
                            if success:
                                log.info(f"Sent embed successfully")
                
                log.info(f"Finished sending alert {alert.id} for {alert.counties}")
                log.info(f"Moving onto next alert")
                alert.posted = True
                
                await asyncio.sleep(5)
                        
            else:
                if alert.posted:
                    log.info(f"Alert {alert.id} has already been posted.")
                
                if alert.ignore:
                    log.info(f"Alert {alert.id} was ignored.")
                
                
    
    def save_alerts(self):
        write_alerts(self.ActiveAlerts)
        
    def first_or_empty(self, lst) -> list: # Helper function for lists.
        return lst[0] if lst else ""
    
    async def _filter_alerts(self): # Filter alerts.
        filtered_alerts: list[Alert] = await self._fetch_active_alerts()
        
        if not filtered_alerts: log.warn(f"No active alerts were found in this cycle. This could be an error: considering checking logs. Or, no alerts could be active at the current moment.")
        
        for alert in filtered_alerts:
            if alert is None: continue
            
            for _, a in self.ActiveAlerts.items():
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
        alert1_refs = alert1.references
        alert2_refs = alert2.references
        
        if alert1_refs or alert2_refs is None:
            log.info(f"This alert has no references.")
            return False, "no"
        
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
        
        for alert in refAlerts["features"]:
            if not alert["id"]: log.error(f"This alert has no id"); continue # Id is separate from properties, so we check id first.
            
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
                    
        
    async def _fetch_active_alerts(self) -> list[Alert]:
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
                        
                compiled_alerts.append(Alert.create_alert(id=alert["id"], props=props, nws_headline=nws_headline, same=same_listing[0], nws=nws_listing[0], geom=geom, geom_base=coordBase, counties=counties, parameters=param_values))
                
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
        # This polls all alerts from the Florida area, which we can then filter.
        url = "https://api.weather.gov/alerts?area=FL"
        
        dict = await AsyncLinks.fetch_url_with_header(url=url, header=config.contact_header)
        
        if dict:
            return dict
        else:
            return None