from logging.syslogger import log
from pyrosm import OSM
from pathlib import Path

class GeoDataHandler():
    def __init__(self):
        log.info("Initializing geodata services.")
        
    # Internal function to check for geometry data.
    def _checkForGeoData(self):
        base_dir = Path(__file__).resolve().parent
                        
        data_dir = base_dir / "geometry"
        geodata_dir = data_dir / "geodata"
        
        self._checkForPBF(geodata_dir)
        self._checkForSHP(geodata_dir)
        
        self._extractRequiredFiles(geodata_dir)
        
        
    def _checkForPBF(self, pathToCheck):
        file_path = pathToCheck / "florida-260723.osm.pbf"
        
        if not file_path.exists():
            log.critical(f"The required .osm.pbf file for Florida does not exist!")
            raise FileNotFoundError(f"The required .osm.pbf file does not exist! Make sure to install the required .osm.pbf file for the state of Florida!")
        else:
            log.info(f"Found the file at {file_path}")
            
    def _checkForSHP(self, pathToCheck):
        fullPath = pathToCheck / "census_data" / "tI_2025_us_county.shp"
        
        if not fullPath.exists():
            log.critical(f"The required.shp file for the United States counties does not exist!")
            raise FileNotFoundError(f"The required .shp file for United States counties doesn't exist; make sure you've installed the required .shp file and assosciated files with the project.")
        else:
            log.info(f"Found the file at {fullPath}")
            
    def _extractRequiredFiles(self, pathToCheck):
        file_path = pathToCheck / "florida-260723.osm.pbf"
        
        package_path = pathToCheck / "florida.gpkg"
        
        osm = OSM(filepath=file_path)
        
        if not package_path.exists():
            roads = osm.get_network(network_type="driving")
                    
            waterways = osm.get_data_by_custom_criteria(
                custom_filter={"waterway": True},
                filter_type="keep"
            )
                    
            lakes = osm.get_data_by_custom_criteria(
                custom_filter={"natural": ["water"]},
                filter_type="keep"
            )
                    
            parks = osm.get_data_by_custom_criteria(
                custom_filter={"leisure": ["park"]},
                filter_type="keep"
            )
                    
            places = osm.get_data_by_custom_criteria(
                custom_filter={
                    "place":    [
                        "city",
                        "town"
                    ]
                },
                filter_type="keep"
            )
            
            coastline = osm.get_data_by_custom_criteria(
                custom_filter={"natural": ["coastline"]},
                filter_type="keep"
            )
            
            roads.to_file(
                "florida.gpkg",
                layer="roads",
                driver="GPKG"
            )
            
            waterways.to_file(
                "florida.gpkg",
                layer="waterways",
                driver="GPKG"
            )
            
            lakes.to_file(
                "florida.gpkg",
                layer="lakes",
                driver="GPKG"
            )
            
            parks.to_file(
                "florida.gpkg",
                layer="parks",
                driver="GPKG"
            )
            
            places.to_file(
                "florida.gpkg",
                layer="places",
                driver="GPKG"
            )
            
            coastline.to_file(
                "florida.gpkg",
                layer="coastline",
                driver="GPKG"
            )
            
GeoHandler = GeoDataHandler()