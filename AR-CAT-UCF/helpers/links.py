import requests
from logging.syslogger import log

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