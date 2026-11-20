from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta, timezone
from math import atan2, cos, radians, sin, sqrt
from typing import Optional

import boto3
import pyart
from botocore import UNSIGNED
from botocore.client import Config

NEXRAD_BUCKET = "unidata-nexrad-level2"

class RadarProduct(str, Enum):
    REFLECTIVITY = "reflectivity"
    VELOCITY = "velocity"
    
@dataclass(frozen=True)
class RadarSite:
    identifier: str
    latitude: float
    longitude: float
    
RADAR_SITES = {
    "KMLB": RadarSite(
        identifier="KMLB",
        latitude=28.1132,
        longitude=80.6540,
    ),
    "KJAX": RadarSite(
        identifier="KJAX",
        latitude=30.4847,
        longitude=81.7019,
    ),
    "KTBW": RadarSite(
        identifier="KTBW",
        latitude=27.7054,
        longitude=82.4018,
    ),
}

class NexradClient:
    """
    Responsible for the handling and discovery of NEXRAD Level II data from the NWS.
    
    AWS provides Level II objects in: s3://unidata-nexrad-level2/YYYY/MM/DD/RADAR/
    
    This bucket is openly accessible without credentials.
    """
    
    def __init__(self) -> None:
        self.s3 = boto3.client(
            "s3",
            region_name="us-east-1",
            config=Config(signature_version=UNSIGNED)
        )
        
    @staticmethod
    def _prefix(radar: RadarSite, timestamp: datetime) -> str:
        timestamp = timestamp.astimezone(timezone.utc)
        
        return (
            f"{timestamp.year:04d}/"
            f"{timestamp.month:02d}/"
            f"{timestamp.day:02d}/"
            f"{radar.identifier}/"
        )
        
    def list_files(self, radar: RadarSite, timestamp: datetime) -> list[str]:
        """
        Returns all Level 2 objects for a given radar/site. Does not return any files, just the objects keys. Does not download anything, either.
        """
        
        prefix = self._prefix(radar, timestamp)
        
        paginator = self.s3.get_paginator("list_objects_v2")
        
        files: list[str] = []
        
        for page in paginator.paginate(Bucket=NEXRAD_BUCKET, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                
                if key.endswith("_V06"):
                    files.append(key)
                    
        return files
        
        
    def latest_file(self, radar: RadarSite, timestamp: Optional[datetime] = None, max_age_minutes: int = 30) -> Optional[str]:
        """
        Finds the latest Level II volume near the given timestamp. Checks the requested UTC timestamp, and if necessary, the previous UTC date. Returns an S3 URI or None.
        """
        
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
            
        timestamp = timestamp.astimezone(timezone.utc)
        
        candidates: list[tuple[datetime, str]] = []
        
        for day_offset in (0, -1):
            date = timestamp + timedelta(days=day_offset)
            
            for key in self.list_files(radar, date):
                filename = key.rsplit("/", 1)[-1]
                
                scan_time = self._parse_filename_time(filename, radar.identifier)
                
                if scan_time is None:
                    continue
                
                age = abs((timestamp - scan_time).total_seconds())
                
                if age <= max_age_minutes * 60:
                    candidates.append((scan_time, key))
                    
        if not candidates: return None
        
        _, key = max(candidates, key=lambda item: item[0])
        
        return f"s3://{NEXRAD_BUCKET}/{key}"
                
    @staticmethod
    def _parse_filename_time(filename: str, radar_identifier: str) -> Optional[datetime]:
        """
        Parses the filename's date/time string for use.
        """
        
        prefix = f"{radar_identifier}"
        
        if not filename.startswith(prefix):
            return None
        
        try:
            timestamp_part = filename[len(radar_identifier) + 1 :]
            
            timestamp_part = timestamp_part.split("_V", 1)[0]
            
            return datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
        
        except (ValueError, IndexError):
            return None
        
    def load(self, s3_uri: str, radar: RadarSite):
        return pyart.io.read_nexrad_archive(s3_uri, station=radar.identifier, storage_options={"anon": True})
        
def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
        
    phi1 = radians(lat1)
    phi2 = radians(lat2)
        
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
        
    a = (
        sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    )
        
    return 2 * radius * atan2(sqrt(a), sqrt(1 - a))
    
def degrees_safe(value: float) -> float:
    """
    Internal helper to keep degrees readable.
    """
        
    return value * 180.0 / 3.141592653589793
    
def select_radar(site: str) -> RadarSite:
    """
    Return the proper radar site based upon the value provided by some external function. One of three radar sites are possible:
        
    KMLB (NWS Melbourne)
    KJAX (NWS Jacksonville)
    KTBW (NWS Ruskin)
    """
        
        
    return RADAR_SITES[site]
    
def find_best_sweep(radar, field_name: str) -> int:
    """
    Find the lowest degree sweep relevant to the particular radar product. 
        
    Better than blindly assuming index 0 is the best radar sweep possible.
    """
        
    if field_name not in radar.fields:
        raise ValueError(
            f"Radar volume does not contain field {field_name!r}. Available fields: {list(radar.fields)}"
        )
            
    field = radar.fields[field_name]["data"]
        
    best_sweep = None
    best_count = 0
        
    for sweep in range(radar.nsweeps):
        ray_slice = radar.get_slice(sweep)
            
        data = field[ray_slice]
            
        valid_count = data.count()
            
        if valid_count > best_count:
            best_count = valid_count
            best_sweep = sweep
                
    if best_sweep is None:
        raise ValueError(
            f"No valid {field_name} data found in radar volume."
        )
            
    return best_sweep
    
def extract_product(radar, product: RadarProduct):
    """
    Extract a single radar product and its related geographical coordinates.
        
    Returns:
        
        data
        latitude
        longitude
        sweep_number
    """
        
    field_name = product.value
        
    sweep = find_best_sweep(radar, field_name)
    
    ray_slice = radar.get_slice(sweep)
    
    data = radar.fields[field_name]["data"][ray_slice]
    
    latitude = radar.gate_latitude["data"][ray_slice]
    longitude = radar.gate_longitude["data"][ray_slice]
    
    return (data, latitude, longitude, sweep)
        
        
        