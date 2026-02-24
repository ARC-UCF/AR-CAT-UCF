from . import reference_locations
import config
from services.syslogger import log

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import natural_earth, Reader
from cartopy.feature import ShapelyFeature
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import math
import matplotlib.pyplot as plt
from io import BytesIO

CODES_WITH_IMAGES = ["TOR", "SVR", "SPS"]
RADAR_EXTENTS = {
    "KMLB": (-82.5, -79.0, 26.0, 29.5),
    "KJAX": (-84.5, -80.0, 29.0, 32.5),
    "KTBW": (-84.5, -80.0, 26.0, 29.5),
}
COUNTIES_WFO = {
    "KMLB": ["brevard", "orange", "seminole", "volusia", "osceola", "lake"],
    "KJAX": ["st. johns", "flagler"],
    "KBTW": ["polk"],
}

ucf = Point(-81.2001, 28.6024) # UCF coords for shapely polygon checking
ucf_point = gpd.GeoSeries([Point(ucf)], crs="EPSG:4326") # Converting UCF to GeoSeries now so we aren't doing this over and over again for just one point.
ucf_point_m = ucf_point.to_crs(epsg=6439) # Convert to local CRS, this one being Florida East in meters.

meters_to_miles = 1609.34

roads_shp = "natural_earth/roads/ne_10m_roads_north_america.shp" # Natural Earth road shapefile path.
lakes_base_shp = "natural_earth/lakes_base/ne_10m_lakes.shp"
rivers_base_shp = "natural_earth/rivers_base/ne_10m_rivers_lake_centerlines.shp"
lakes_supp_shp = "natural_earth/lakes_supp_ne/ne_10m_lakes_north_america.shp"
rivers_supp_shp = "natural_earth/rivers_supp_ne/ne_10m_rivers_north_america.shp"
urban_shp = "natural_earth/urban/ne_10m_urban_areas.shp"

def ucf_in_or_near_polygon(geodat: list) -> tuple[bool, str]: # Specific to figuring out if UCF is included or near the alert polygon, only for WEAS handling.
    if not geodat:
        return False, ""
    
    poly = Polygon(geodat[0])

    if ucf.within(poly):
        return True, "within"
    
    gdf_alert = gpd.GeoSeries([poly], crs="EPSG:4326")

    gdf_alert_m = gdf_alert.to_crs(epsg=6439)  # NAD83 / Florida East (meters)
    
    poly_m = gdf_alert_m.iloc[0]
    point_m = ucf_point_m.iloc[0]
    
    dist_m = point_m.distance(poly_m)
    
    dist_miles = dist_m / meters_to_miles

    # Buffer UCF point by X miles (1 mile ≈ 1609.34 m)
    
    buffer_meters = config.bufferMiles
    
    buf_m = buffer_meters * meters_to_miles
    
    if dist_m <= buf_m:
        return True, "around"
    
    return False, ""
    
def filter_points_in_bounds(points: list, bounds: float) -> list:
    """
    points: list of tuples (name, lat, lon)
    bounds: min_lon, max_lon, min_lat, max_lat
    returns: filtered list of points inside bounds
    """
    min_lon, max_lon, min_lat, max_lat = bounds
    filtered = []
    for name, lat, lon in points:
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            filtered.append((name, lat, lon))
    return filtered

def get_bounds_from_multipoylgon(multipoly, buffer_miles=0):
    if multipoly is None:
        return None
    
    # Flatten all exterior coordinates of all polygons
    coords = [pt for poly in multipoly.geoms for pt in poly.exterior.coords]

    lons, lats = zip(*coords)
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    if buffer_miles > 0:
        lat_buffer = buffer_miles * 0.0145
        avg_lat = sum(lats) / len(lats)
        lon_buffer = buffer_miles * 0.0145 / max(0.0001, abs(math.cos(math.radians(avg_lat))))
        min_lon -= lon_buffer
        max_lon += lon_buffer
        min_lat -= lat_buffer
        max_lat += lat_buffer

    return min_lon, max_lon, min_lat, max_lat

def safe_geometries(reader):
    return [g for g in reader.geometries() if g is not None]

def generate_outlook_image(risks):
    log.info("Generating outlook image")
    fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_extent(
        [-85.0, -79.0, 24.0, 31.0],  # [west, east, south, north]
        crs=ccrs.PlateCarree()
    )
    
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray', zorder=1)
    ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue', zorder=1)
    ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', zorder=2)
    ax.add_feature(cfeature.RIVERS.with_scale('10m'), edgecolor='lightblue', zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor='black', zorder=3)
    ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black', zorder=3)
    
    counties_shp = natural_earth(resolution='10m', category='cultural', name='admin_2_counties')
    counties_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(counties_shp)),
        crs=ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='red',
        linewidth=1,
        zorder=5,
    )
    if counties_feature is not None:
        ax.add_feature(counties_feature)

    roads_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(roads_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='darkslategray',  # whatever color you like
        facecolor='none',
        zorder=4,
    )
    if roads_feature is not None:
        ax.add_feature(roads_feature)
        
    lakes_base_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(lakes_base_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='lightblue',  # whatever color you like
        facecolor='lightblue',
        zorder=3,
    )
    if lakes_base_feature is not None:
        ax.add_feature(lakes_base_feature)
        
    rivers_base_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(lakes_base_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='lightblue',  # whatever color you like
        facecolor='lightblue',
        zorder=3,
    )
    if rivers_base_feature is not None:
        ax.add_feature(rivers_base_feature)
        
    for risk in risks:
        if risk["geometry"] is None:
            continue
        
        log.info(f"Adding geometry for {risk['properties']['LABEL']} risk")
        
        geom = MultiPolygon(risk["geometry"]["coordinates"])
        
        ax.add_geometries(
            geom,
            crs=ccrs.PlateCarree(),
            facecolor=risk["properties"]["fill"],
            edgecolor=risk["properties"]["stroke"],
            linewidth=2,
            alpha=0.5,
            zorder=6,
        )
        
    buf = BytesIO()
    plt.tight_layout()
    plt.title(
        label=f"Severe Weather Outlook for Central and Northeastern Florida", 
        loc='left',
        fontsize=24,
    )
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_alert_image(coords: list, base: str, alertCode: str, polyColor: str, trackId: str, countiesAffected: list):
    '''
    All CSS colors are valid for facecolors and edgecolors.
    
    Alternatively, you can define hexcodes for colors for different layers.
    '''
    
    if not coords: # If we have no coords, return so we don't error.
        return None
    
    multipoly = None # Define multipoly.
    
    if base == "Polygon": # If a single polygon.
        multipoly = MultiPolygon([Polygon(coords[0])]) # Still make it a multipolygon for easier use.
    elif base == "Area": # If area, and therefore, potentially multiple poylgons.
        polygons = []
        for mp in coords:
            for ply in mp:
                polygons.append(Polygon(ply[0]))
        multipoly = MultiPolygon(polygons)
    else:
        return None # If base is neither Polygon or Area, exit and return None.
    
    if polyColor is None:
        polyColor = '#6e6e6e'
    
    minx, miny, maxx, maxy = multipoly.bounds # Define bounds.
    
    fig, ax = plt.subplots(
        figsize=(14, 10),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    
    # Below is every layer included for alert image generation. Change colors how you like, but make sure they work.
    # And work as in they are still readable and don't hurt the eyes.
    
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray', zorder=1)
    ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue', zorder=1)
    ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', zorder=2)
    ax.add_feature(cfeature.RIVERS.with_scale('10m'), edgecolor='lightblue', zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor='black', zorder=3)
    ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black', zorder=3)
    
    counties_shp = natural_earth(resolution='10m', category='cultural', name='admin_2_counties')
    counties_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(counties_shp)),
        crs=ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='red',
        linewidth=1,
        zorder=5,
    )
    if counties_feature is not None:
        ax.add_feature(counties_feature)

    roads_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(roads_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='darkslategray', 
        facecolor='none',
        zorder=4,
    )
    if roads_feature is not None:
        ax.add_feature(roads_feature)
        
    lakes_base_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(lakes_base_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='lightblue',  
        facecolor='lightblue',
        zorder=3,
    )
    if lakes_base_feature is not None:
        ax.add_feature(lakes_base_feature)
        
    rivers_base_feature = ShapelyFeature(
        geometries=safe_geometries(Reader(lakes_base_shp)),
        crs=ccrs.PlateCarree(),
        edgecolor='lightblue',  
        facecolor='lightblue',
        zorder=3,
    )
    if rivers_base_feature is not None:
        ax.add_feature(rivers_base_feature)
        
    ax.add_geometries(
        multipoly, 
        crs=ccrs.PlateCarree(), 
        facecolor=polyColor, 
        edgecolor=polyColor, 
        linewidth=2, 
        alpha=0.7, 
        zorder=6, 
    )
    
    if alertCode in CODES_WITH_IMAGES: 
        print("Getting radar image")
        
    lon_pad = 1  # wider east-west
    lat_pad = .25  # shorter north-south
    ax.set_extent([minx - lon_pad, maxx + lon_pad, miny - lat_pad, maxy + lat_pad], crs=ccrs.PlateCarree())
    
    bounds = get_bounds_from_multipoylgon(multipoly, 10)
    
    filtered_points = filter_points_in_bounds(reference_locations.city_points, bounds)
    
    for name, lat, lon in filtered_points:
        ax.scatter(lon, lat, color='blue', s=40, transform=ccrs.PlateCarree(), zorder=7, edgecolor='white')
        ax.text(lon, lat + 0.01, name, fontsize=9, transform=ccrs.PlateCarree(), zorder=7)
        
    buf = BytesIO()
    plt.tight_layout()
    plt.title(
        label=f"Alert Area - {alertCode} - #{trackId}", 
        loc='left',
        fontsize=24,
    )
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

def test_image_generation(): # Function is unused. Keep for testing image generation with new layers to ensure they work before push to production.
    '''
    All CSS colors are valid for facecolors and edgecolors.
    
    Altneratively, you can define hexcodes for colors for different layers.
    '''
    
    fig, ax = plt.subplots(
        figsize=(14, 10),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
    ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
    ax.add_feature(cfeature.RIVERS.with_scale('10m'), edgecolor='blue')
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor='black')
    ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black')
    
    counties_shp = natural_earth(resolution='10m', category='cultural', name='admin_2_counties')
    counties_feature = ShapelyFeature(
        geometries=Reader(counties_shp).geometries(),
        crs=ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='red',
        linewidth=1
    )
    if counties_feature is not None:
        ax.add_feature(counties_feature)

    roads_feature = ShapelyFeature(
        Reader(roads_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='grey',  # whatever color you like
        facecolor='none'
    )
    if roads_feature is not None:
        ax.add_feature(roads_feature)
        
    lakes_base_feature = ShapelyFeature(
        Reader(lakes_base_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='grey',  # whatever color you like
        facecolor='none'
    )
    if lakes_base_feature is not None:
        ax.add_feature(lakes_base_feature)
        
    rivers_base_feature = ShapelyFeature(
        Reader(rivers_base_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='grey',  # whatever color you like
        facecolor='none'
    )
    if rivers_base_feature is not None:
        ax.add_feature(rivers_base_feature)
        
    lakes_supp_feature = ShapelyFeature(
        Reader(lakes_supp_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='grey',  # whatever color you like
        facecolor='none'
    )
    if lakes_supp_feature is not None:
        ax.add_feature(lakes_supp_feature)
        
    rivers_supp_feature = ShapelyFeature(
        Reader(rivers_supp_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='grey',  # whatever color you like
        facecolor='none'
    )
    if rivers_supp_feature is not None:
        ax.add_feature(rivers_supp_feature)
        
    urban_feature = ShapelyFeature(
        Reader(urban_shp).geometries(),
        crs=ccrs.PlateCarree(),
        edgecolor='darkslategray',  # whatever color you like
        facecolor='none'
    )
    if urban_feature is not None:
        ax.add_feature(urban_feature)
        
    plt.tight_layout()
    plt.close(fig)
    print("completed image.")
    
