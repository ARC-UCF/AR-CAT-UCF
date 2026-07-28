from logger import log
from forecasts import DailyForecast, HurricaneForecasts, SevereWeatherOtlk, TimeManager
import asyncio

class ForecastManager():
    def __init__(self):
        log.info("initializing the forecast manager")
        self.dailyForecast = DailyForecast()
        self.hurricaneForecasts = HurricaneForecasts()
        self.severeWeatherForecasts = SevereWeatherOtlk()
        self.timeManager = TimeManager()
        
    async def run(self): # The forecast manager will manage the things in the forecast section.
        log.info(f"Running the forecast manager")
        
        new_day = self.timeManager.check_new_day()
        
        if new_day:
            self.dailyForecast.reset()
            self.hurricaneForecasts.reset_states()
            self.severeWeatherForecasts.reset_states()
            
        success = await self.severeWeatherForecasts.check_and_post()
        
        if not success:
            log.error(f"Failed to properly execute severe weather forecasts.")
        else:
            log.info(f"Executed severe weather forecasts.")
            
        success = await self.dailyForecast.check()
        
        if not success:
            log.error(f"Failed to properly execute daily forecasts.")
        else:
            log.info(f"Ran daily forecasts.")
            
        success = await self.hurricaneForecasts.run_check()
        
        if not success:
            log.error(f"Error while executing hurricane forecasts.")
        else:
            log.info(f"Successfully ran hurricane forecasts.")
            
        log.info("Sleeping for 10 minutes.")
            
        asyncio.sleep(10 * 60)