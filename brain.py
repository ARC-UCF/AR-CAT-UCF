from services import State, Forecasts, Hurricane, AlertStatistics, alerts, OtlkHandler
from services.syslogger import log
from utils import Time, identifier, determiner, generate_alert_image, ucf_in_or_near_polygon, channels, generate_outlook_image
import config
import asyncio
import discord
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
I optimized what I could/wanted to in the moment, further optimization can be expected, well, later.
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
                OtlkHandler.reset_states()
            
            self.save_info()
            
            await asyncio.sleep(self.timeDelay)
            
            await self.handle_and_post_outlooks()
            
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
        
            
    def establish(self): # This function fetches our json file to load all stored timings and alerts.
        data = st.send_to_disseminate() # Fetches our saved data we load at runtime.
        
        # From here we go through each piece of stored information and correspondingly write it to each module for use during each cycle.
        
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
        
        self.timeDelay = config.cycleTime
    
        if self.timeDelay < 30: self.timeDelay = 30 # This is hard-coded to prevent excessive requests to the api.weather.gov endpoint. 
    
        self.timeDelay = self.timeDelay/3
        
    def save_info(self):
        hInfo = hurr.return_forecast_states()
        fInfo = fcast.return_forecast_states()
        sInfo = alertStats.provide_stats()
        tim = tManager.provide()
        tID = identifier.provide_next_id()
        
        st.write_data(fInfo, hInfo, self.posted_alerts, tim, tID, sInfo)
        
    async def handle_and_post_outlooks(self):
        to_post = OtlkHandler.check_outlook()
        
        if to_post:
            print("Preparing to post outlook information")
            for day, info in to_post.items():
                buf = generate_outlook_image(info["geom"])
                
                embed = discord.Embed(
                    title=f"{day.capitalize()} Outlook Information",
                    description=f"The Highest Risk for the area is {info["highest_risk"]}\n\nThe following areas are at risk of severe weather:\n\n{info["msg"]}\n\nAreas outlined are at risk for experiencing severe weather, including hail 1 inch or greater, wind gusts of 58 mph or greater, and/or tornadoes.\n\n**Be weather aware!** Have a way to receive watches and warnings, such as a cellular device, a NOAA weather radio, a news source, or a weather app. Be prepared to take action if severe weather occurs.",
                    color=0x6382e0,
                )
                embed.set_footer(text=config.VERSION)
                
                embed.set_image(url="attachment://alert_map.png")
                
                await self.post_to_channel(channels.get_channel_from_county("forecast"), embed=embed, buf=buf)
        else:
            log.info("No outlook information for any selected period is avaiable to post at this time.")
                
                
        
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
            
        post = hurr.time_to_post_preparedness()
        
        if post:
            hurricaneWeb = channels.get_channel_from_county("hurricane")
            
            embed = discord.Embed(
                title="Hurricane Season Starts Soon: Are You Prepared?",
                description="Hurricane season in the Atlantic starts on June 1st and ends November 31st. Now is the time to prepare for the hurricane season. Consider getting batteries, water, non-perishable food, and multiple ways to receive alerts, such as a NOAA weather radio, a weather app, a radio tuned to a local news station, a cellular device, or by word of mouth. Make a plan for what to do if a hurricane threatens the area, such as where to shelter and protecting your property from wind and water damage. If you are in a flood-prone area, consider getting sandbags, flood barriers, or taking similar steps to ensure you are ready to protect your home from flooding. \n\n **Below are helpful resources for being prepared this hurricane season!**\n[UCF Hurricane Information](https://www.ucf.edu/hurricane/)\n[National Hurricane Center: Hurricane Preparedness](https://www.noaa.gov/hurricane-prep)\n[Graphical Tropical Weather Outlooks](http://www.nhc.noaa.gov/gtwo_atl.shtml)\n[CECS Wiki Hurricane Links and Info](https://newton.i2lab.ucf.edu/wiki/Hurricanes)",
                color=0x1e90ff,
            )
            
            embed.set_footer(text=f"{config.VERSION} | This message is sent automatically on the 1st of May")
            
            await self.post_to_channel(hurricaneWeb, embed)
    
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
            alrt = alertList[a]
            Id = alrt["id"]
            ignore = alrt.get("ignore", False)
            
            if Id in self.posted_alerts:
                log.info(f"Alert {Id} already has been posted.")
            
            if Id not in self.posted_alerts:
                
                if ignore:
                    log.info(f"{Id} marked as ignored.")
                    self.posted_alerts[Id] = alrt
                    continue
                
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
                    instruction_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', alrt["instruction"])
                    
                    embed.add_field(name="Precautionary/Preparedness Instructions", value=instruction_text, inline=False)
                    
                embed.add_field(name="Alert Information", value=infoMessage, inline=False)
                embed.set_footer(text=config.VERSION)
                
                buf = generate_alert_image(alrt["coords"], alrt["base"], alrt["SAME_code"], alrt["polyColor"], alrt["trackId"], alrt["countiesAffected"])
                
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
                        
                
                
                
                
                
                
    
    