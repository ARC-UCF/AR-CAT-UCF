from logger import log
from config import config
from datetime import datetime, time
from helpers import post_message, fetch_url_with_header, channels
import discord
from classes import Day

class DailyForecast():
    def __init__(self):
        self.requestHeader = config.contact_header
        self.ForecastStates = {
            "Morning": False,
            "Afternoon": False,
            "Evening": False,
        }
        self.ForecastTimes = {
            "Morning": {
                "Start": time(9, 0),
                "End": time(9,30)
            },
            "Afternoon": {
                "Start": time(13,0),
                "End": time(13,30)
            },
            "Evening": {
                "Start": time(19,0),
                "End": time(19,30)
            }
        }
        
    def _poll_forecast(self):
        url = "https://api.weather.gov/gridpoints/MLB/26,68/forecast?units=us"
        
        data = fetch_url_with_header(url, self.requestHeader)
        
        if data is None:
            log.critical(f"No forecast information was returned!")
            return None
        
        return data
    
    def get_forecasts(self) -> list[Day]:
        data = self._poll_forecast()
        
        props = data.get("properties", "")
        
        if props:
            periods = props.get("periods", {})
            
            if periods:
                days = []
                
                for period in periods[:4]:
                    day = Day.compile_day(period=period)
                    
                    days.append(day)
                    
                if days is not None:
                    log.info(f"Compiled days")
                    return days
                else:
                    return None
            else:
                log.critical(f"Error when locating periods for forecast.")
                return None
        else:
            log.critical(f"Unable to find forecast properties!")
            return None
        
    async def post_forecasts(self, days: list[Day], time_of_day):
        embed = discord.Embed(
            title=f"{time_of_day} Forecast for {datetime.now().strftime("%A")}",
            color=0x53eb31
        )
        
        embed.set_footer(text=config.version_id)
        
        forecastChannel = channels.get_channel_from_name("forecast")
        
        for day in days:   
            fullName = f"{day.name} // {day.startTime.date()} {day.startTime.time()} - {day.endTime.date()} {day.endTime.time()}"
            
            description = f"**Summary:** {day.short_forecast}\nTemperature: {day.temperature}{day.temperature_unit}\nWind: {day.wind_direction} @ {day.wind_speed}\nChance of Precipitation: {day.probability_of_precip}%\n\n{day.long_forecast}"
            
            embed.add_field(name=fullName, value=description, inline=False)
            
        success = await post_message(forecastChannel, embed)
        
        if success:
            return True
        
        return False
        
    def check_time(self):
        currentTime = datetime.now().time()
        
        for period, posted in self.ForecastStates.items():
            if (self.ForecastTimes[period]["Start"] <= currentTime <= self.ForecastTimes[period]["End"]) and not posted:
                self.ForecastStates[period] = True
                
                return True, period
            
        return False, None
    
    def reset(self):
        for period in self.ForecastStates.keys():
            self.ForecastStates[period] = False
        
    async def check(self):
        log.info(f"Checking forecast")
        
        post, period = self.check_time()
        
        if post:
            days = self.get_forecasts()
            
            success = await self.post_forecasts(days=days, time_of_day=period)
            
            if success: return True
            
            return False
        
        return True
            