import requests
import datetime
from datetime import datetime, timezone, timedelta, time
import os
from dotenv import load_dotenv
from services.syslogger import log
load_dotenv("../sensitive.env")

class Forecasts():
    
    def __init__(self):
        self.requestHeader = {f"User-Agent": os.environ.get('HEADER')}
        self.ForecastStates = {
            "Morning": False,
            "Afternoon": False,
            "Night": False,
        }
        self.ForecastTimes = {
            "Morning": {
                "Start": time(9,0),
                "End": time(9,30),
            },
            "Afternoon": {
              "Start": time(13,0),
              "End": time(13,30),
            },
            "Night": {
                "Start": time(19,0),
                "End": time(19,30),
            }
        }
        
    def _poll_forecast(self):
        url = "https://api.weather.gov/gridpoints/MLB/26,68/forecast?units=us"
    
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
        
    def get_forecasts(self) -> list:
        data = self._poll_forecast()
        
        forecastInfo = []
        
        if data:
            
            props = data["properties"]
            days = props["periods"]
            
            for day in days[:4]:
                forecastInfo.append({
                    "timePeriod": day.get("name", "UNKNOWN"),
                    "temperature": day.get("temperature", 0),
                    "precipProbs": day["probabilityOfPrecipitation"]["value"],
                    "windDirection": day.get("windDirection", "N/A"),
                    "windSpeed": day.get("windSpeed", "N/A"),
                    "forecast": day.get("detailedForecast", "FORECAST UNAVAILABLE"),
                    "startTime": datetime.fromisoformat(day["startTime"]),
                    "endTime": datetime.fromisoformat(day["endTime"]),
                })
                
        return forecastInfo
    
    def time_to_post_forecast(self) -> tuple[bool, list]:
        currentTime = datetime.now().time()
        for time, posted in self.ForecastStates.items():
            if (self.ForecastTimes[time]["Start"] <= currentTime <= self.ForecastTimes[time]["End"]) and not posted:
                self.ForecastStates[time] = True
                forecastInfo = self.get_forecasts()
                
                return True, forecastInfo
        
        return False, None
    
    def return_forecast_states(self) -> dict:
        return self.ForecastStates
    
    def write_forecast_states(self, statesToWrite: dict):
        self.ForecastStates = statesToWrite
        
    def reset_states(self):
        for state in self.ForecastStates:
            self.ForecastStates[state] = False
            