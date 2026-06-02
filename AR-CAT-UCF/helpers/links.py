import requests
from logging.syslogger import log
import aiohttp

def fetch_url_with_header(url, header):
    try:
        r = requests.get(url, headers=header)  # keep as Response object
        if r.status_code != 200:
            log.error(f"API returned status {r.status_code}: {r.text[:200]}")
            return []

        try:
            return r.json()
        except requests.exceptions.JSONDecodeError:
            log.error("Response was not valid JSON!")
            log.error(f"Response text: {r.text[:200]}")  # Log first 200 chars
            return []
    except requests.exceptions.RequestException as e:
        log.error(f"Request failed: {e}")
    return []

def fetch_url(url):
    try:
        r = requests.get(url)  # keep as Response object
        if r.status_code != 200:
            log.error(f"API returned status {r.status_code}: {r.text[:200]}")
            return []

        try:
            return r.json()
        except requests.exceptions.JSONDecodeError:
            log.error("Response was not valid JSON!")
            log.error(f"Response text: {r.text[:200]}")  # Log first 200 chars
            return []
    except requests.exceptions.RequestException as e:
        log.error(f"Request failed: {e}")
    return []

class ALinks():
    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    async def fetch_url_with_header(self, url, header):
        async with self.session.get(url, headers=header) as response:
            return await response.json()
        
    async def fetch_url(self, url):
        async with self.session.get(url) as response:
            return await response.json()
        
AsyncLinks = ALinks()