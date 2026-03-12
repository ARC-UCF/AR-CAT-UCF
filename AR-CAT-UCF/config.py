from dataclasses import dataclass
import os
from configuration import settings

@dataclass(frozen=True)
class Config:
    token: str
    guild_id: int
    contact_header: str
    channels: dict[str, int]
    cycle_time: int
    version_id: str
    alert_colors: dict[str, str]
    counties_to_watch: dict[str]
    ping_roles: dict[str, str]
    ping_alerts: dict[str]
    buffer: int
    
    @staticmethod
    def load() -> "Config":
        token = os.getenv("API-TOKEN")
        guild_id = settings.guild_id
        contact_header = os.getenv('HEADER')
        cycle_time = settings.cycleTime
        version_id = settings.version
        alert_colors = settings.polygon_colors_SAME
        channels = settings.channels
        ping_roles = settings.pings
        ping_alerts = settings.alertCodes
        counties_to_watch = settings.countiesToMonitor
        buffer = settings.bufferMiles
        
        return Config(
            token=token,
            guild_id=guild_id,
            contact_header=contact_header,
            channels=channels,
            cycle_time=cycle_time,
            version_id=version_id,
            alert_colors=alert_colors,
            counties_to_watch=counties_to_watch,
            ping_roles=ping_roles,
            ping_alerts=ping_alerts,
            buffer=buffer
        )
        
config = Config()