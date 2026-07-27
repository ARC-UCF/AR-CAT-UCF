from dataclasses import dataclass
from datetime import datetime
from logging.syslogger import log

@dataclass(eq=True)
class RiskArea():
    label: str
    title: str
    valid: str
    expires: str
    issued: str
    stroke: str
    fill: str
    display_num: int
    geometry: dict
    
    @classmethod
    def build_area(cls, feature):
        
        props = feature.get("properties", {})
        
        if not props:
            log.critical(f"Failed to compile risk area, no properties were found.")
            return None
        
        return cls(
            label = props.get("LABEL", ""),
            title = props.get("LABEL2", ""),
            valid = props.get("VALID_ISO", ""),
            expires = props.get("EXPIRES_ISO", ""),
            issued = props.get("ISSUED_ISO", ""),
            stroke = props.get("stroke"),
            fill = props.get("fill"),
            geometry = feature.get("geometry")
        )