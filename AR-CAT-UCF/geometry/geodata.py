from logger import log
from pyrosm import OSM
from pathlib import Path

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
        
        self._extractRequiredFiles(geodata_dir)
        
        
    def _checkForPBF(self, pathToCheck):
        file_path = pathToCheck / "florida-260723.osm.pbf"
        
        print(file_path)
        
        if not file_path.exists():
            log.critical(f"The required .osm.pbf file for Florida does not exist!")
            raise FileNotFoundError(f"The required .osm.pbf file does not exist! Make sure to install the required .osm.pbf file for the state of Florida!")
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
            
    def _extractRequiredFiles(self, pathToCheck):
        file_path = pathToCheck / "florida-260723.osm.pbf"
        
        package_path = pathToCheck / "florida.gpkg"
        
        osm = OSM(filepath=file_path)
        
        if not package_path.exists():
            log.info(f"Package path does not exist; beginning extraction and placement of file.")
            
            roads = osm.get_network(network_type="driving")
            
            interstates = roads[roads["highway"] == "motorway"]
            
            major_highways = roads[
                roads["highway"].isin([
                    "trunk",
                    "primary"
                ])
            ]
            
            secondary_highways = roads[
                roads["highway"].isin([
                    "secondary",
                    "tertiary"
                ])
            ]
            
            log.info(f"Got roads")
                    
            waterways = osm.get_data_by_custom_criteria(
                custom_filter={"waterway": True},
                filter_type="keep"
            )
            
            log.info("got waterways")
                    
            lakes = osm.get_data_by_custom_criteria(
                custom_filter={"natural": ["water"]},
                filter_type="keep"
            )
            
            log.info(f"Got lakes")
                    
            parks = osm.get_data_by_custom_criteria(
                custom_filter={"leisure": ["park"]},
                filter_type="keep"
            )
            
            log.info(f"Got parks")
                    
            places = osm.get_data_by_custom_criteria(
                custom_filter={
                    "place":    [
                        "city",
                        "town"
                    ]
                },
                filter_type="keep"
            )
            
            log.info(f"Got places")
            
            coastline = osm.get_data_by_custom_criteria(
                custom_filter={"natural": ["coastline"]},
                filter_type="keep"
            )
            
            log.info(f"Got coastline")
            
            log.info(f"Beginning file creation")
            
            roads.to_file(
                "florida.gpkg",
                layer="roads",
                driver="GPKG"
            )
            
            interstates.to_file(
                "florida.gpkg",
                layer="interstates",
                driver="GPKG"
            )
            
            major_highways.to_file(
                "florida.gpkg",
                layer="major_highways",
                driver="GPKG"
            )
            
            secondary_highways.to_file(
                "florida.gpkg",
                layer="secondary_highways",
                driver="GPKG"
            )
            
            log.info(f"Roads to file")
            
            waterways.to_file(
                "florida.gpkg",
                layer="waterways",
                driver="GPKG"
            )
            
            log.info("Waterways to file")
            
            lakes.to_file(
                "florida.gpkg",
                layer="lakes",
                driver="GPKG"
            )
            
            log.info(f"Lakes to file")
            
            parks.to_file(
                "florida.gpkg",
                layer="parks",
                driver="GPKG"
            )
            
            log.info("Parks to file")
            
            places.to_file(
                "florida.gpkg",
                layer="places",
                driver="GPKG"
            )
            
            log.info(f"Places to file")
            
            coastline.to_file(
                "florida.gpkg",
                layer="coastline",
                driver="GPKG"
            )
            
            log.info(f"Coastline to file")
            
GeoHandler = GeoDataHandler()