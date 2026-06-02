from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from logging.syslogger import log
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
    def create_alert(cls, feature, props, nws_headline, same, nws, geom, geom_base, counties, parameters):
        
        return cls(
            id=feature["@id"],
            sent=props.get("sent"),
            expires=props.get("expires"),
            title=nws_headline,
            status=props.get("status"),
            certainty=props.get("certainty"),
            severity=props.get("severity"),
            urgency=props.get("urgency"),
            senderName=props.get("senderName"),
            response=props.get("sender"),
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
    def is_expired(self) -> bool:
        if not self.expires:
            return False
        
        return datetime.now(timezone.utc) >= datetime.fromisoformat(self.expires).astimezone(timezone.utc)
    
    @property
    def ignore_this_alert(self):
        self.ignore = True
        
    @property
    def _scrub_text(self, text: str) -> str:
        return re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
    @property
    def get_formatted_text(self) -> tuple[str, str]:
        return self._scrub_text(self.desc), self._scrub_text(self.instruction)
    
    @property
    def update_alert(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                log.error(f"Unable to update value: {key} does not exist")