from dataclasses import dataclass
from classes import Schedule
from datetime import datetime

@dataclass(eq=True)
class Message():
    id: str
    header: str
    message: str
    footer: str | None = None
    channel: str
    schedule: Schedule
    last_sent: datetime | None = None
    
    @classmethod
    def new(cls, id, header, message, footer, channel, schedule):
        
        return cls(
            id=id,
            header=header,
            message=message,
            footer=footer,
            channel=channel,
            schedule=schedule
        )
    
    @property
    def to_dict(cls):
        return {
            "id": cls.id,
            "header": cls.header,
            "message": cls.message,
            "footer": cls.footer,
            "channel": cls.channel,
            "schedule": cls.schedule.to_dict(),
            "last_sent": (cls.last_sent.isoformat() if cls.last_sent is not None else None)
        }
        
    @property
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            header=data["header"],
            message=data["message"],
            footer=data["footer"],
            channel=data["channel"],
            schedule=Schedule.from_dict(data["schedule"]),
            last_sent=(datetime.fromisoformat(data["last_sent"]) if data["last_sent"] is not None else None)
        )
    