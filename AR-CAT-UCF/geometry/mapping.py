# Importing!!
import geopandas as gpd
from pathlib import Path

import cartopy.crs as ccrs
from shapely.geometry import Point, shape
import matplotlib.pyplot as plt
from io import BytesIO
from config import config
from logger import log
from geometry import zones
from classes import RiskArea

# Miscelleanous variables for this system

CODES_WITH_IMAGES = ["TOR", "SVR", "SPS"] # Alerts which will require codes
RADAR_EXTENTS = { # Radar points
    "KMLB": (-82.5, -79.0, 26.0, 29.5),
    "KJAX": (-84.5, -80.0, 29.0, 32.5),
    "KTBW": (-84.5, -80.0, 26.0, 29.5),
}
COUNTIES_WFO = { # Radar WFOs
    "KMLB": ["brevard", "orange", "seminole", "volusia", "osceola", "lake"],
    "KJAX": ["st. johns", "flagler"],
    "KBTW": ["polk"],
}

ucf = Point(-81.2001, 28.6024) # UCF coords for shapely polygon checking
ucf_point = gpd.GeoSeries([Point(ucf)], crs="EPSG:4326") # Converting UCF to GeoSeries now so we aren't doing this over and over again for just one point.
ucf_point_m = ucf_point.to_crs(epsg=6439) # Convert to local CRS, this one being Florida East in meters.

meters_to_miles = 1609.34

base_dir = Path(__file__).resolve().parent

census_shp = base_dir / "geometry" / "census_data" / "tI_2025_us_county.shp"

def ucf_in_or_near_polygon(geodat) -> tuple[bool, str]:
    if not geodat:
        return False, ""
    
    polygon = shape(geodat)
    
    gdf_alert = gpd.GeoSeries([polygon], crs="ESPG:4326")
    
    gdf_m = gdf_alert.to_crs(espg=6439)
    
    poly_m = gdf_m.iloc[0]
    point_m = ucf_point_m.iloc[0]
    
    dist_m = point_m.distance(poly_m)
    
    totalDist = dist_m / meters_to_miles
    
    bufferMiles = config.buffer
    
    if ucf.within(polygon):
        return True, "within"
    
    if totalDist <= bufferMiles:
        return True, "around"
    
    return False, ""

def generate_outlook_image(risks: dict[str, RiskArea]):
    geodat_gpkg = base_dir / "geometry" / "geodata" / "florida_export.gpkg"
        
    places = gpd.read_file(geodat_gpkg, layer="places")
    lakes = gpd.read_file(geodat_gpkg, layer="lakes")
    waterways = gpd.read_file(geodat_gpkg, layer="waterways")
    roads = gpd.read_file(geodat_gpkg, layer="roads") # Not used, but still worth keeping around
    counties=gpd.read_file(census_shp)
    counties=counties.to_crs(ccrs.PlateCarree())
        
    fig, ax = plt.subplots(
        figsize=(14, 10),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    
    ax.set_extent(
        [-85.0, -78.0, 26.0, 31.0],  # [west, east, south, north]
        crs=ccrs.PlateCarree()
    )
        
    ax.set_facecolor("#2d73b5")
        
    counties.plot(
        ax=ax,
        facecolor="#333333",
        edgecolor="#858585",
        linewidth=1,
        zorder=11
    )
        
    lakes.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=10
    )
        
    waterways.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=9
    )
        
    roads.plot(
        ax=ax,
        facecolor="#d22c2c",
        edgecolor=None,
        linewidth=1,
        zorder=6
    )
        
    for _, place in places.iterrows():
        ax.text(
            place.geometry.x,
            place.geometry.y,
            place["name"],
            fontsize=10,
            ha="center"
        )
        
    for label, risk in risks.items():
        if risk.geometry is None:
            log.critical(f"Forced to skip {label} due to no geometry data.")
            continue
        
        log.info(f"Adding geometry data for {label} risk")
        
        risk_geom = shape(risk.geometry)
        
        risk_area = gpd.GeoDataFrame(geometry=[risk_geom], crs="ESPG:4326")
        
        risk_area.plot(
            ax=ax,
            facecolor=risk.fill,
            edgecolor=risk.stroke,
            linewidth=2,
            alpha=0.5,
            zorder=risk.display_num
        )
        
    buf = BytesIO()
    plt.tight_layout()
    plt.title(
        label=f"Severe Weather Outlook",
        loc="left",
        fontsize=24
    )
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_alert_image(coords, coordBase, alertCode):
    geodat_gpkg = base_dir / "geometry" / "geodata" / "florida_export.gpkg"
    
    places = gpd.read_file(geodat_gpkg, layer="places")
    lakes = gpd.read_file(geodat_gpkg, layer="lakes")
    waterways = gpd.read_file(geodat_gpkg, layer="waterways")
    roads = gpd.read_file(geodat_gpkg, layer="roads")
    counties=gpd.read_file(census_shp)
    counties=counties.to_crs(ccrs.PlateCarree())
    
    alert = None
    
    if coordBase == "Polygon":
        polygon = shape(coords)
        alert = gpd.GeoDataFrame(geometry=[polygon], crs="ESPG:4326")
    elif coordBase == "County":
        polygons = []
        
        for zone in coords:
            geom = zones.get_zone_geo(zone)
            
            polygon = shape(geom)
            
            polygons.append(polygon)
            
        alert = gpd.GeoDataFrame(geometry=polygons, crs="ESPG:4326")
    
    polygonColor = config.alert_colors.get(alertCode, "None")
    
    minx, miny, maxx, maxy = polygon.bounds
    
    fig, ax = plt.subplots(
        figsize=(14, 10),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    
    ax.set_facecolor("#2d73b5")
    
    alert.plot(
        ax=ax,
        facecolor=polygonColor,
        edgecolor=polygonColor,
        linewidth=2,
        alpha=0.5,
        zorder=1
    )
    
    counties.plot(
        ax=ax,
        facecolor="#333333",
        edgecolor="#858585",
        linewidth=1,
        zorder=11
    )
            
    lakes.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=10
    )
            
    waterways.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=9
    )
            
    roads.plot(
        ax=ax,
        facecolor="#d22c2c",
        edgecolor=None,
        linewidth=1,
        zorder=6
    )
    
    for _, place in places.iterrows():
        ax.text(
            place.geometry.x,
            place.geometry.y,
            place["name"],
            fontsize=10,
            ha="center"
        )
        
    lon_pad = 1  # wider east-west
    lat_pad = .25  # shorter north-south
    ax.set_extent([minx - lon_pad, maxx + lon_pad, miny - lat_pad, maxy + lat_pad], crs=ccrs.PlateCarree())
    
    buf = BytesIO()
    plt.tight_layout()
    plt.title(
        label=f"Alert Area - {alertCode}",
        loc="left",
        fontsize=24
    )
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf
    
    
    
    
    
    
    
    
    
    