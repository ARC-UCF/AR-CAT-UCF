from logger import log
from pyrosm import OSM
from pathlib import Path
import geopandas as gpd

class GeoDataHandler():
    def __init__(self):
        log.info("Initializing geodata services.")
        self._checkForGeoData()
        
    # Internal function to check for geometry data.
    def _checkForGeoData(self):
        base_dir = Path(__file__).resolve().parent
                        
        geodata_dir = base_dir / "geodata"
        
        self._checkForPBF(geodata_dir)
        self._checkForSHP(base_dir)
        
        origin_file = geodata_dir / "florida.gpkg"
        export_file = geodata_dir / "florida_export.gpkg"
        
        self._createSimpleGPKG(origin_file, export_file)
        
        
    def _checkForPBF(self, pathToCheck):
        file_path = pathToCheck / "florida.gpkg"
        
        print(file_path)
        
        if not file_path.exists():
            log.critical(f"The required .gpkg file for Florida does not exist!")
            raise FileNotFoundError(f"The required .gpkg file does not exist! Make sure to install the required .osm.pbf file for the state of Florida!")
        else:
            log.info(f"Found the file at {file_path}")
            
    def _checkForSHP(self, pathToCheck):
        fullPath = pathToCheck / "census_data" / "tl_2025_us_county.shp"
        
        print(fullPath)
        
        if not fullPath.exists():
            log.critical(f"The required.shp file for the United States counties does not exist!")
            raise FileNotFoundError(f"The required .shp file for United States counties doesn't exist; make sure you've installed the required .shp file and assosciated files with the project.")
        else:
            log.info(f"Found the file at {fullPath}")
            
    def _createSimpleGPKG(self, filePath, exportPath):
        
        if exportPath.exists():
            
            log.info(f"Found file at {exportPath}")
            
            return
        
        roads = gpd.read_file(
            filePath,
            layer = "gis_osm_roads_free"
        )
        water = gpd.read_file(
            filePath,
            layer = "gis_osm_water_a_free"
        )
        waterways = gpd.read_file(
            filePath,
            layer = "gis_osm_waterways_free"
        )
        places = gpd.read_file(
            filePath,
            layer = "gis_osm_places_free"
        )
        landuse = gpd.read_file(
            filePath,
            layer = "gis_osm_landuse_a_free"
        )
        
        major_roads = roads[
            roads["fclass"].isin([
                "motorway",
                "motorway_link",
                "trunk",
                "trunk_link",
                "primary",
                "primary_link",
                "secondary",
                "secondary_link",
            ])
        ]
        
        lakes = water[
            water["fclass"].isin([
                "water",
                "wetland",
                "resovoir"
            ])
        ]
        
        rivers = waterways[
            waterways["fclass"].isin([
                "river",
                "stream",
                "canal"
            ])
        ]
        
        locations = places[
            places["fclass"].isin([
                "city",
                "town"
            ])
        ]
        
        major_roads.to_file(
            exportPath,
            layer="roads",
            driver="GPKG"
        )
        
        lakes.to_file(
            exportPath,
            layer="lakes",
            driver="GPKG"
        )
        
        rivers.to_file(
            exportPath,
            layer="waterways",
            driver="GPKG"
        )
        
        locations.to_file(
            exportPath,
            layer="places",
            driver="GPKG"
        )
        
            
GeoHandler = GeoDataHandler()