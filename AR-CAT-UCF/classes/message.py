from dataclasses import dataclass
from classes import Schedule
from datetime import datetime

@dataclass(eq=True)
class Message():
    id: str
    header: str
    message: str
    channel: str
    schedule: Schedule
    footer: str | None = None
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
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "message": self.message,
            "footer": self.footer,
            "channel": self.channel,
            "schedule": self.schedule.to_dict(),
            "last_sent": (self.last_sent.isoformat() if self.last_sent is not None else None)
        }
        
    @classmethod
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
    