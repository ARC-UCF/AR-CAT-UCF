from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

@dataclass(frozen=True)
class RenderConfig:
    width: int = 1200
    height: int = 1200
    dpi: int = 150
    
    reflectivity_min: int = -10
    reflectivity_max: int = 90
    
    velocity_min: int = -120
    velocity_max: int = 120
    
    transparent: bool = True
    
PRODUCT_CONFIG = {
    "reflectivity": {
        "cmap": "turbo",
        "vmin": RenderConfig.reflectivity_min,
        "vmax": RenderConfig.reflectivity_max,
    },
    "velocity": {
        "cmap": "RdBu_r",
        "vmin": RenderConfig.velocity_min,
        "vmax": RenderConfig.velocity_max,
    },
}

def render_radar():
    print("Hi")