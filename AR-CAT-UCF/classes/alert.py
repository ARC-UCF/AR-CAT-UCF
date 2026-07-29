from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from logger import log
import re

@dataclass(eq=True)
class Alert():
    id: str
    sent: str
    expires: str
    title: str
    status: str
    certainty: str
    severity: str
    urgency: str
    senderName: str
    response: str
    desc: str
    messageType: str
    geo_base: str
    counties: list
    parameters: dict | list
    ignore: bool = False
    posted: bool = False
    
    references: Optional[dict] = None
    replacedBy: Optional[str] = None
    replacedAt: Optional[str] = None
    secondary_title: Optional[str] = None
    areaDesc: Optional[str] = None
    instruction: Optional[str] = None
    same: Optional[str] = None
    nws: Optional[str] = None
    event: Optional[str] = None
    geom: Optional[dict | list] = None
    
    @classmethod
    def create_alert(cls, id, props, nws_headline, same, nws, geom, geom_base, counties, parameters):
        
        return cls(
            id=id,
            sent=props.get("sent"),
            expires=props.get("expires"),
            title=nws_headline,
            status=props.get("status"),
            certainty=props.get("certainty"),
            severity=props.get("severity"),
            urgency=props.get("urgency"),
            senderName=props.get("senderName"),
            response=props.get("response"),
            desc=props.get("description"),
            messageType=props.get("messageType"),
            geo_base=geom_base,
            counties=counties,
            parameters=parameters,
            references=props.get("references", ""),
            replacedBy=props.get("replacedBy", ""),
            replacedAt=props.get("replacedAt", ""),
            secondary_title=props.get("headline", ""),
            areaDesc=props.get("areaDesc", ""),
            instruction=props.get("instruction", ""),
            same=same,
            nws=nws,
            event=props.get("event", "UNSPECIFIED"),
            geom=geom,
        )
        
    @property
    def is_expired(cls) -> bool:
        if not cls.expires:
            return False
        
        return datetime.now(timezone.utc) >= datetime.fromisoformat(cls.expires).astimezone(timezone.utc)
    
    def ignore_this_alert(cls):
        cls.ignore = True
        
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
        
    def _scrub_text(cls, text: str) -> str:
        return re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
    def get_formatted_text(cls) -> tuple[str, str]:
        return cls._scrub_text(cls.desc), cls._scrub_text(cls.instruction)
    
    @property
    def update_alert(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                log.error(f"Unable to update value: {key} does not exist")