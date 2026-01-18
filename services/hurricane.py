import html
import xml.etree.ElementTree as ET
import datetime
import re
import requests
from datetime import datetime, timezone, timedelta, time

class Hurricane():
    
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
                "End": time(20,30),
            }
        }
        
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
        
    def _poll_hurricane_info(self) -> tuple[str, str]:
        xml_content = None
        rss_url = "https://www.nhc.noaa.gov/gtwo.xml"
        if xml_content is None:
            response = requests.get(rss_url)
            response.raise_for_status()
            xml_content = response.content

        root = ET.fromstring(xml_content)

        image_url = None
        discussion_text = None

        # Find the Atlantic Outlook item
        for item in root.findall(".//item"):
            title = item.findtext("title")
            if title and "Atlantic Outlook" in title:
                description = item.findtext("description")
                if description:
                # Extract the 7-day image URL from the description
                    match = re.search(r'<img\s+src="([^"]+)"\s+alt="Atlantic 7-Day Graphical Outlook Image"', description)
                    if match:
                        image_url = match.group(1)
                    # Extract the discussion text (strip HTML tags)
                    # The discussion is inside <div class='textproduct'>...</div>
                    discussion_match = re.search(
                        r"<div class='textproduct'>(.*?)</div>", description, re.DOTALL
                    )
                    if discussion_match:
                        discussion_html = discussion_match.group(1)
                        # Format the HTML text for Discord
                        discussion_text = self.format_nhc_html(discussion_html)
            break
        
        discussion_text.replace("Gulf of America", "Gulf of Mexico")
        
        return image_url, discussion_text
    
    def time_to_post_hurricane(self) -> tuple[bool, str, str]: # Determine if the timing is right to post hurricane information.
        currentTime = datetime.now().time() # Current time.
        
        if not 6 <= datetime.now().month <= 11:
            print("It is not hurricane season.")
            return False, None, None
        
        for time, posted in self.ForecastStates.items(): 
            if (self.ForecastTimes[time]["Start"] <= currentTime <= self.ForecastTimes[time]["End"]) and not posted: # Check every period's start and end time.
                self.ForecastStates[time] = True # If we are within the start and end time and we have not posted, then we will post.
                image, discussion = self._poll_hurricane_info()
                
                return True, image, discussion # Return True, and then the image and discussion text.
            
        return False, None, None # Not time to post.
    
    def return_forecast_states(self) -> dict:
        return self.ForecastStates
    
    def write_forecast_states(self, statesToWrite: dict):
        self.ForecastStates = statesToWrite
        
    def reset_states(self):
        for state in self.ForecastStates:
            self.ForecastStates[state] = False