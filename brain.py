from services import State, Forecasts, Hurricane, AlertStatistics, alerts
from services.syslogger import log
from utils import Time, identifier, determiner, generate_alert_image, ucf_in_or_near_polygon, channels
import config
import asyncio
import discord
from discord import Webhook, SyncWebhook
import os
from io import BytesIO
import datetime
import time
from datetime import datetime, timezone, timedelta
import aiohttp
import re

tManager = Time()
deter = determiner
st = State()
fcast = Forecasts()
hurr = Hurricane()
alertStats = AlertStatistics()
aManager = alerts
webs = channels

DONOTPOST = False

severity_colors = { # This severity index is based on the severity property in alerts.
    "Extreme": 0xA020F0,   # Purple
    "Severe": 0xFF0000,    # Red
    "Moderate": 0xFFA500,  # Orange
    "Minor": 0xFFFF00,     # Yellow
    "Unknown": 0x808080    # Gray
}

'''
This is the sort of central system basically. This thing manages the services.
I optimized waht I could/wanted to in the moment, further optimization can be expected, well, later.
'''

class Controller():
    def __init__(self):
        log.info("CONTROLLER INIT")
        self.posted_alerts = {}
        log.info("CURRENT ALERTS")
        self.establish()
    
    async def run(self):
        while True:
            if not channels.synced: channels.sync_channels()
            
            await self.handle_and_post_alerts()
            self.clean()
            self.save_info()
            await asyncio.sleep(self.timeDelay)
            aManager.check_internal()
            await self.handle_and_post_forecasts()
            
            newDay = tManager.is_new_day()
            
            if newDay:
                fcast.reset_states()
                hurr.reset_states()
            
            self.save_info()
            
            await asyncio.sleep(self.timeDelay)
            
    async def post_to_channel(self, channel, embed, buf=None, url=None): # Handle method of posting to a discord channel.
        timebuffer = 7 # Change to update how much time should be spent before next attempt. Multiplies.
        max_attempts = 4 # Max number of attempts.
        for attempt_num in range(1, max_attempts + 1): # For loop
            try:
                if isinstance(embed, str):
                    await channel.send(content=embed)
                elif isinstance(embed, discord.Embed):
                    
                    if buf and not url: # Filter for buf object
                        buf.seek(0)
                        file = discord.File(fp=buf, filename="alert_map.png")
                        await channel.send(embed=embed, file=file)
                    elif url and not buf:
                        embed.set_image(url=url)
                        await channel.send(embed=embed)
                    else:
                        await channel.send(embed=embed)
                else:
                    log.error("Invalid type!")
                    return False
                    
                log.info(f"Message successfully sent on attempt {attempt_num}!") # If successful
                return True
            except aiohttp.ClientConnectionError: # Client connection error
                log.error(f"⚠️ Connection error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
            except aiohttp.ClientError as e: # Client error
                log.error(f"⚠️ Client error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
            except Exception as e: # Other exceptions
                log.error(f"⚠️ Unexpected error occurred: {e} ... (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
            
            if attempt_num < max_attempts: # If we have attempts left
                    await asyncio.sleep(timebuffer * attempt_num) # Sleep, again, multiplies. 
                    
        log.warn(f"Failure to send message after successive attempts! Ending attempt to deliver.")
        return False
        
            
    def establish(self):
        data = st.send_to_disseminate()
    
        if data.get("alerts"):
            self.posted_alerts = data["alerts"].copy()
            aManager.write_to_alerts(data["alerts"].copy())         
        
        if data.get("forecast"):
            fcast.write_forecast_states(data["forecast"])
        
        if data.get("hurricane"):
            hurr.write_forecast_states(data["hurricane"])
        
        if data.get("timing"):
            tManager.write_last_date(data["timing"])
        
        if data.get("trackId"):
            identifier.write_to_id(data["trackId"])
        
        if data.get("stats"):
           alertStats.write_to_stats(data["stats"])
        
        self.timeDelay = config.checkTime
    
        if self.timeDelay < 20: self.timeDelay = 20
    
        self.timeDelay = self.timeDelay/2
        
    def save_info(self):
        hInfo = hurr.return_forecast_states()
        fInfo = fcast.return_forecast_states()
        sInfo = alertStats.provide_stats()
        tim = tManager.provide()
        tID = identifier.provide_next_id()
        
        st.write_data(fInfo, hInfo, self.posted_alerts, tim, tID, sInfo)
        
    async def handle_and_post_forecasts(self):
        post, info = fcast.time_to_post_forecast()
        
        if post:
            
            embed = discord.Embed(
                title="Forecast Information",
                color=0x53eb31,
            )
            
            embed.set_footer(text=config.VERSION)
            
            forecastWeb = channels.get_channel_from_county("forecast")
            
            for day in info:
                fullName = f"{day["timePeriod"]} // {day["startTime"].date()} {day["startTime"].time()} - {day["endTime"].date()} {day["endTime"].time()}"
                
                forecastString = f"Temperature: {day["temperature"]}\nWind: {day["windDirection"]} @ {day["windSpeed"]}\nPrecip Chance: {day["precipProbs"]}%\n\n{day["forecast"]}"
                
                embed.add_field(name=fullName, value=forecastString, inline=False)
                
            await self.post_to_channel(forecastWeb, embed)
            
        post, image, discussion = hurr.time_to_post_hurricane()
        
        if post:
            
            discussion = (discussion[:4000] + "...") if len(discussion) > 4000 else discussion
            
            hurricaneWeb = channels.get_channel_from_county("hurricane")
            
            embed = discord.Embed(
                title="Hurricane Discussion",
                description=discussion,
                color=0x1e90ff,
            )
            
            new_url = f"{image}?t={int(time.time())}"
            
            embed.set_footer(text=config.VERSION)
            
            await self.post_to_channel(hurricaneWeb, embed, url=new_url) 
    
    def clean(self):
        now = datetime.now(timezone.utc)
        expired = []
        for alert, info in self.posted_alerts.items():
            if not info["expires"] or datetime.fromisoformat(info["expires"]) + timedelta(hours=24) < now:
                expired.append(alert)

        for alert in expired:
            del self.posted_alerts[alert]
    
    async def handle_and_post_alerts(self):
        alertList = aManager.cycle() # Handling this cycle is the chunkiest thing in here I swear
        
        if alertList is None: return
        
        for a in alertList:
            log.info("Comparing alerts.")
            alrt = alertList[a]
            Id = alrt["id"]
            
            log.info(f"Checking {Id}.")
            
            if Id not in self.posted_alerts:
                
                log.info(f"{Id} not in posted alerts, working to add.")
                
                log.info(f"Working {Id}")
                
                severity = alrt.get("severity", "Unknown")
                color = severity_colors.get(severity, 0x808080) # Determine color based on severity property.
                
                header = f"(#{alrt["trackId"]}) - {alrt["title"]}"
                
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
                
                for field in preambleList:
                    if field == "space":
                        preamble_lines.append("")  # adds a blank line
                    elif field == "bulletin":
                        bulletin = deter.determine(alrt["WEAHandling"], alrt["messageType"], alrt["severity"], alrt["certainty"], alrt["urgency"])
                        if bulletin:
                            preamble_lines.append(bulletin)
                    elif alrt.get(field):
                        preamble_lines.append(alrt[field])
                        
                preambleString = "\n".join(preamble_lines)
                            
                mainList = [
                    "secondary_title",
                    "desc",
                ]
                
                main_lines = []

                for field in mainList:
                    if alrt.get(field):
                        main_lines.append(alrt[field])

                mainString = "\n\n".join(main_lines)
                
                truncated_text = (mainString[:3850-3] + "...") if len(mainString) > 3850 else mainString
                
                truncated_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', truncated_text) # Scrub text for single newlines and removes them, double new lines preserved.
                
                if alrt["eventMotionDescription"]:
                    truncated_text = truncated_text + "\n\n" + alrt["eventMotionDescription"]
                    
                total = preambleString + "\n\n" + truncated_text
                
                informationToFetch = {
                    "id": "Alert Id: ",
                    "SAME_code": "SAME: ",
                    "severity": "Severity: ",
                    "urgency": "Urgency: ",
                    "certainty": "Certainty: ",
                    "response": "Response: ",
                    "hailThreat": "Hail Threat: ",
                    "maxHailSize": "Max Hail Size: ",
                    "windThreat": "Wind Threat: ",
                    "maxWindGust": "Max Wind Gust: ",
                    "tornadoDetection": "Tornado Detection: ",
                    "tornadoDamageThreat": "Damage Threat: ",
                    "thunderstormDamageThreat": "Damage Threat: ",
                }
                
                info_lines = []
                
                for key, lead in informationToFetch.items():
                    if alrt.get(key):
                        info_lines.append(lead + alrt.get(key))
                        
                infoMessage = "\n".join(info_lines)
                
                embed = discord.Embed(
                    title=header,
                    description=total,
                    color=color,
                )
                
                if alrt["instruction"]:
                    embed.add_field(name="Precautionary/Preparedness Instructions", value=alrt["instruction"], inline=False)
                    
                embed.add_field(name="Alert Information", value=infoMessage, inline=False)
                embed.set_footer(text=config.VERSION)
                
                buf = generate_alert_image(alrt["coords"], alrt["base"], alrt["SAME_code"], alrt["polyColor"], alrt["trackId"])
                
                embed.set_image(url="attachment://alert_map.png")
                
                posted_successfully = False
                
                for c in alrt["countiesAffected"]:
                    channel = channels.get_channel_from_county(c)
                    
                    if channel:
                        log.info("webhook found")
                        if alrt["SAME_code"] in config.alertCodes and alrt["status"] == "Actual":
                            ping = config.pings[c]
                            await self.post_to_channel(channel=channel, embed=ping)
                        scs = await self.post_to_channel(channel=channel, embed=embed, buf=buf)
                        if scs:
                            posted_successfully = True
                    if c == "orange" and alrt["base"] == "Area" and channel:
                        channel = channels.get_channel_from_county("arc")
                        
                        if alrt["SAME_code"] in config.alertCodes and alrt["status"] == "Actual":
                            ping = config.pings["arc"]
                            await self.post_to_channel(channel=channel, embed=ping)
                        scs = await self.post_to_channel(channel=channel, embed=embed, buf=buf)
                        if scs:
                            posted_successfully = True
                    elif (c == "orange" or c == "seminole") and alrt["base"] == "Polygon":
                        ucfAffected = ucf_in_or_near_polygon(alrt["coords"])
                        
                        if ucfAffected:
                            channel = channels.get_channel_from_county("arc")
                        
                            if alrt["SAME_code"] in config.alertCodes and alrt["status"] == "Actual":
                                if alrt["SAME_code"] in config.alertCodes:
                                    ping = config.pings["arc"]
                                    await self.post_to_channel(channel=channel, embed=ping)
                            scs = await self.post_to_channel(channel=channel, embed=embed, buf=buf)
                            if scs:
                                posted_successfully = True
                    
                if posted_successfully == True:
                    self.posted_alerts[Id] = alrt
                    alertStats.add_stat(alrt["countiesAffected"], alrt["SAME_code"])
                    log.info(f"✅🔗 Alert pushed.")
                    log.info("Sent " + Id)
                
                await asyncio.sleep(5)
            else:
                log.info(f"{Id} is in active alerts.")
                log.info(f"Confirming {Id} is in active alerts, {self.posted_alerts[Id]["id"]}")
                        
                
                
                
                
                
                
    
    