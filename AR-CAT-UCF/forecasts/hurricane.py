from datetime import datetime, time, timedelta
import html
import xml.etree.ElementTree as ET
import re
import requests
from bs4 import BeautifulSoup
from logging.syslogger import log
from helpers import channels, post_embed_with_image
import discord
from config import config
from databases import write_hurricane, fetch_hurricane
import difflib

class HurricaneForecasts():
    def __init__(self):
        self.ForecastStates = {
            "Midnight": False,
            "Morning": False,
            "Afternoon": False,
            "Evening": False,
        }
        self.ForecastTimes = {
            "Midnight": {
                "Start": time(2,0),
                "End": time(2,30),
            },
            "Morning": {
                "Start": time(8,0),
                "End": time(8,30),
            },
            "Afternoon": {
                "Start": time(14,0),
                "End": time(14,30),
            },
            "Evening": {
                "Start": time(20,0),
                "End": time(21,30),
            }
        }
        self.previousDiscussion = {}
        
    def format_nhc_html(self, html_text) -> str:
        """
        Converts NHC HTML text to Discord-friendly markdown.
        - <br> becomes newlines
        - Remove other HTML tags
        - Unescape HTML entities
        """
    
        # Replace <br> and <br/> with newlines
        text = re.sub(r'<br\s*/?>', '\n', html_text, flags=re.IGNORECASE)
        # Remove all other HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Unescape HTML entities
        text = html.unescape(text)
        # Remove leading/trailing whitespace and collapse multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text
    
    def get_hurr_img(self):
        rss_url = "https://www.nhc.noaa.gov/gtwo.xml"
    
        response = requests.get(rss_url)
        response.raise_for_status()
    
        root = ET.fromstring(response.content)
    
        # The first item in the feed is the Atlantic basin
        atlantic_item = root.find("./channel/item")
    
        if atlantic_item is None:
            raise ValueError("Could not find Atlantic outlook item.")
    
        description = atlantic_item.findtext("description")
    
        if not description:
            raise ValueError("Atlantic outlook description was empty.")
    
        soup = BeautifulSoup(description, "html.parser")
    
        atlantic_7day_image = soup.find(
            "img",
            alt=lambda alt: alt and "Atlantic 7-Day" in alt
        )
    
        if atlantic_7day_image is None:
            raise ValueError("Could not find Atlantic 7-Day outlook image.")
    
        return atlantic_7day_image["src"]
    
    def get_atlantic_outlook_text(self):
        url = "https://www.nhc.noaa.gov/gtwo.php?basin=atlc&fdays=7"
    
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
            
        for pre in soup.find_all("pre"):
            html = pre.decode_contents()
                
            if "MIATWOAT" in html or "For the North Atlantic" in html:
                return pre.decode_contents()
            
    def _poll_hurricane_info(self):
        image_url = self.get_hurr_img()
        discussion_text = self.get_atlantic_outlook_text()
        
        discussion_text = self.format_nhc_html(discussion_text)
        discussion_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', discussion_text) 
        
        return image_url, discussion_text
    
    def time_to_post(self) -> tuple[bool, str]:
        currentTime = datetime.now().time()
        
        if not 6 <= datetime.now().month <= 11:
            log.info("It is not time to post hurricane information.")
            return False
        
        for time, posted in self.ForecastStates.items():
            if (self.ForecastTimes[time]["Start"] <= currentTime <= self.ForecastTimes[time]["End"]) and not posted:
                self.ForecastStates[time] = True
                return True, time
            
        return False, time
    
    async def run_check(self):
        post, period = self.time_to_post()
        
        if post:
            image, text = self._poll_hurricane_info()
            
            has, previous = self.fetch_previous()
            
            if has:
                result = difflib.SequenceMatcher(None, text, previous).ratio() * 100
                
                if result < 92.5:
                    self.previousDiscussion["discussion"] = text
                    self.previousDiscussion["timestamp"] = datetime.now()
                    
                    await self.post_hurricane(image=image, text=text)
                else:
                    if period == "Morning":
                        await self.post_continuous_hurricane()
            else:
                self.previousDiscussion["discussion"] = text
                self.previousDiscussion["timestamp"] = datetime.now()
                
                await self.post_hurricane(image=image, text=text)
                
            iso_string = datetime.isoformat(self.previousDiscussion["timestamp"])
            
            pkg = {
                "discussion": self.previousDiscussion["discussion"],
                "timestamp": iso_string,
            }
            
            write_hurricane(pkg)
            
            
    async def post_hurricane(self, image, text):
        embed = discord.Embed(
            title="Atlantic Tropical Cyclone Genesis",
            description=text,
            color=0x1e90ff,
        )
        
        new_url = f"{image}?t={int(time.time())}"
        
        embed.set_footer(config.version_id)
        
        channel = channels.get_channel_from_name("hurricane")
        
        success = await post_embed_with_image(channel=channel, content=embed, url=new_url)
        
        if success:
            log.info(f"Sucessfully sent HURRICANE INFO")
        else:
            log.error(f"Failed to send hurricane info")
            
    async def post_continuous_hurricane(self, image, text):
        embed = discord.Embed(
            title="Morning Atlantic Tropical Cyclone Genesis Update",
            description=f"This Atlantic Tropical Cyclone Genesis Update is specially sent between the times of 8 AM to 8:30 AM to remain up to date on current Atlantic systems and disturbances.\nThis post is automatic, and happens regardless of whether or not any changes have been made from the previous discussion. Unless an update to this discussion occurs, this message will not be posted again until 8 AM the next day. The following is the current 8AM NHC advisory message as of {datetime.now().date()}:\n\n{text}",
            color=0x1e90ff,
        )
        
        new_url = f"{image}?t={int(time.time())}"
                
        embed.set_footer(config.version_id)
                
        channel = channels.get_channel_from_name("hurricane")
                
        success = await post_embed_with_image(channel=channel, content=embed, url=new_url)
                
        if success:
            log.info(f"Sucessfully sent HURRICANE INFO")
        else:
            log.error(f"Failed to send hurricane info")
                    
            
    def fetch_previous(self) -> tuple[bool, str]:
        discussion = self.previousDiscussion.get("discussion", "")
        timestamp = self.previousDiscussion.get("timestamp")
        
        if discussion and timestamp:
            return True, discussion
        else:
            has, past = self.read_prev_discussion()
            
            if has:
                self.previousDiscussion["discussion"] = past
                return True, past
            else:
                return False, None
            
    def read_prev_discussion(self) -> tuple[bool, str]:
        if self.previousDiscussion == None:
            prev = fetch_hurricane()
            
            if prev is None:
                log.warn(f"No previous hurricane discussion was fetched.")
            else:
                log.info(f"Fetched stored hurricane discussion")
                
                discussion = prev["discussion"]
                timestamp = datetime.fromisoformat(prev["timestamp"])
                
                currentTime = datetime.now()
                
                if timestamp <= currentTime - timedelta(hours=24):
                    return False, None
                else:
                    return True, discussion
                
    def reset_states(self):
        for period in self.ForecastStates:
            self.ForecastStates[period] = False