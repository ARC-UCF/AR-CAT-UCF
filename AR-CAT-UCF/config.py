from dataclasses import dataclass
import os
from dotenv import load_dotenv

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
    
    @staticmethod
    def load() -> "Config":
        token = os.getenv("API-TOKEN")
        guild_id = 300

