# Importing!!
import geopandas as gpd
from pathlib import Path

import cartopy.crs as ccrs
from shapely.geometry import Point, shape
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
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
ucf_point = gpd.GeoSeries(ucf, crs="EPSG:4326") # Converting UCF to GeoSeries now so we aren't doing this over and over again for just one point.
ucf_point_m = ucf_point.to_crs(epsg=6439) # Convert to local CRS, this one being Florida East in meters.

meters_to_miles = 1609.34

base_dir = Path(__file__).resolve().parent

census_shp = base_dir /  "census_data" / "tl_2025_us_county.shp"

def ucf_in_or_near_polygon(geodat) -> tuple[bool, str]:
    log.info(f"Checking geometry for near UCF.")
    
    if not geodat:
        return False, ""
    
    polygon = shape(geodat)
    
    gdf_alert = gpd.GeoSeries([polygon], crs="EPSG:4326")
    
    gdf_m = gdf_alert.to_crs(epsg=6439)
    
    poly_m = gdf_m.iloc[0]
    point_m = ucf_point_m.iloc[0]
    
    dist_m = point_m.distance(poly_m)
    
    totalDist = dist_m / meters_to_miles
    
    log.info(f"Polygon bounds: {polygon.bounds}")
    log.info(f"UCF: {ucf.x}, {ucf.y}")
    log.info(f"Distance meters: {dist_m}")
    log.info(f"Distance miles: {dist_m / 1609.344}")
    
    bufferMiles = config.buffer
    
    if ucf.within(polygon):
        return True, "within"
    
    if totalDist <= bufferMiles:
        return True, "around"
    
    return False, ""

def generate_outlook_image(risks: dict[str, RiskArea]):
    geodat_gpkg = base_dir / "geodata" / "florida_export.gpkg"
        
    places = gpd.read_file(geodat_gpkg, layer="places")
    lakes = gpd.read_file(geodat_gpkg, layer="lakes")
    waterways = gpd.read_file(geodat_gpkg, layer="waterways")
    roads = gpd.read_file(geodat_gpkg, layer="roads") # Not used, but still worth keeping around
    counties=gpd.read_file(census_shp)
    counties=counties.to_crs("EPSG:4326")
    
    lakes.to_crs("EPSG:4326")
    waterways.to_crs("EPSG:4326")
    roads.to_crs("EPSG:4326")
    places.to_crs("EPSG:4326")
        
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
        zorder=1,
        transform=ccrs.PlateCarree(),
    )
        
    lakes.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=2,
        transform=ccrs.PlateCarree(),
    )
        
    roads.plot(
        ax=ax,
        facecolor=None,
        edgecolor="#d22c2c",
        linewidth=1,
        zorder=4,
        transform=ccrs.PlateCarree(),
    )
        
    for label, risk in risks.items():
        if risk.geometry is None:
            log.critical(f"Forced to skip {label} due to no geometry data.")
            continue
        
        log.info(f"Adding geometry data for {label} risk")
        
        risk_geom = shape(risk.geometry)
        
        risk_area = gpd.GeoDataFrame(geometry=[risk_geom], crs="EPSG:4326")
        
        risk_area.plot(
            ax=ax,
            facecolor=risk.fill,
            edgecolor=risk.stroke,
            linewidth=2,
            alpha=0.5,
            zorder=risk.display_num+5
        )
        
    buf = BytesIO()
    plt.title(
        label=f"Severe Weather Outlook",
        loc="left",
        fontsize=24
    )
    plt.subplots_adjust(
        left=0,
        right=1,
        top=1,
        bottom=0
    )
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_alert_image(coords, coordBase, alertCode):
    geodat_gpkg = base_dir /  "geodata" / "florida_export.gpkg"
    
    places = gpd.read_file(geodat_gpkg, layer="places")
    lakes = gpd.read_file(geodat_gpkg, layer="lakes")
    waterways = gpd.read_file(geodat_gpkg, layer="waterways")
    roads = gpd.read_file(geodat_gpkg, layer="roads")
    counties=gpd.read_file(census_shp)
    counties=counties.to_crs("EPSG:4326")
    
    lakes.to_crs("EPSG:4326")
    waterways.to_crs("EPSG:4326")
    roads.to_crs("EPSG:4326")
    places.to_crs("EPSG:4326")
    
    alert = None
    
    if coordBase == "Polygon":
        polygon = shape(coords)
        alert = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
    elif coordBase == "County":
        polygons = []
        
        for zone in coords:
            geom = zones.get_zone_geo(zone)
            
            polygon = shape(geom)
            
            polygons.append(polygon)
            
        alert = gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")
    
    polygonColor = config.alert_colors.get(alertCode, "None")
    
    minx, miny, maxx, maxy = alert.total_bounds
    
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
        zorder=12,
        transform=ccrs.PlateCarree()
    )
    
    counties.plot(
        ax=ax,
        facecolor="#333333",
        edgecolor="#858585",
        linewidth=1,
        zorder=1,
        transform=ccrs.PlateCarree(),
    )
            
    lakes.plot(
        ax=ax,
        facecolor="#2d73b5",
        edgecolor=None,
        linewidth=1,
        zorder=2,
        transform=ccrs.PlateCarree(),
    )
            
    roads.plot(
        ax=ax,
        facecolor=None,
        edgecolor="#d22c2c",
        linewidth=1,
        zorder=4,
        transform=ccrs.PlateCarree(),
    )
    
    visible = places.cx[minx:maxx, miny:maxy]
    
    min_dist = 0.04
    
    placed = []
    
    for _, place in visible.iterrows():
        if place["fclass"] == "city":
            text = ax.text(
                place.geometry.x,
                place.geometry.y,
                place["name"],
                fontsize=8,
                ha="center",
                zorder=15,
                color="white",
                transform=ccrs.PlateCarree(),
            )
                    
            text.set_path_effects([
                pe.withStroke(linewidth=2, foreground="black")
            ])
        elif place["fclass"] == "town":
            x = place.geometry.x
            y = place.geometry.y

            if any((x-px)**2 + (y-py)**2 < min_dist**2 for px, py in placed):
                continue

            placed.append((x, y))
            
            text = ax.text(
                place.geometry.x,
                place.geometry.y,
                place["name"],
                fontsize=6,
                ha="center",
                zorder=14,
                color="white",
                transform=ccrs.PlateCarree(),
            )
            
            text.set_path_effects([
                pe.withStroke(linewidth=1, foreground="black")
            ])
        
    lon_pad = .5  # wider east-west
    lat_pad = .1  # shorter north-south
    
    print(alert.total_bounds)
    print(minx, miny, maxx, maxy)
    
    buf = BytesIO()
    ax.set_extent([minx - lon_pad, maxx + lon_pad, miny - lat_pad, maxy + lat_pad], crs=ccrs.PlateCarree())
    plt.title(
        label=f"Alert Area - {alertCode}",
        loc="left",
        fontsize=24
    )
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    plt.close(fig)
    return buf
    
    
    
    
    
    
    
    
    
    