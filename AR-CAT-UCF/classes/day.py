from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(eq=True)
class Day():
    name: str
    startTime: str
    endTime: str
    temperature: int
    temperature_unit: str
    wind_speed: str
    wind_direction: str
    probability_of_precip: str
    short_forecast: str
    long_forecast: str
    
    @classmethod
    def compile_day(cls, period):
        
        return cls(
            name = period["name"],
            startTime = datetime.fromisoformat(period["startTime"]),
            endTime = datetime.fromisoformat(period["endTime"]),
            temperature = period["temperature"],
            temperature_unit = period["temperatureUnit"],
            wind_speed = period["windSpeed"],
            wind_direction = period["windDirection"],
            probability_of_precip = period["probabilityOfPrecipitation"]["value"],
            short_forecast = period["shortForecast"],
            long_forecast = period["detailedForecast"]
        )
    