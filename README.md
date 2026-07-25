# ARCatUCF V3.0.0

## About

AR-CAT-UCF V3 is the latest iteration of the weather alert discord bot for the ARC @ UCF discord. V3, compared to its predecessors, is intended to be the most "intelligent", capable, and organized version. The current product here is just a re-integration of desired systems, before more systems are then introduced on top of this already existing system.

AR-CAT-UCF V3 also works to reduce the amount of requests made per-minute and works to reduce delays within the system. In example, at initiation, AR-CAT-UCF v2 fetches all the zone data and stores it, each time on startup. However, V3 works by fetching the zone data once, at first startup, and saves that information to a local json file. That information is then kept and is not overwritten or edited unless a new zone with missing information appears or the file is corrupted, at which point, the bot will automatically re-fetch the zone information and create a new JSON file. This means an internet request is not needed each time the bot starts up, and the zone information can be acquired immediately with little to no delay.

## Setup Guide

> [!WARNING]
> To ensure the bot operates properly, please follow the following setup instructions.
>
> Failing to follow these setup instructions means the bot will not be able to operate normally. This includes downloading the required files and setting up the configuration.

ARCatUCF **requires** two key files in order to function properly, particularly the OpenStreetMap data file and the Census Bureau County data from 2025 (or later if you're able to find it). 

These two things aare required in order to complete the mapping process for the bot, which will allow it to map out the alert images for you on an actual map, which will be included with any alerts that get sent by the bot. 

You can download the TIGER/Line census data from [this link](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2025&layergroup=Counties+%28and+equivalent%29). 

You can download the Florida OSM data from [this link](https://download.geofabrik.de/north-america/us.html) and by navigating to the "Florida" **.osm.pbf** file. 

Once you have done so, go to `AR-CAT-UCF -> geometry` and create **two new folders**. One will be titled **census_data**, which is where the files included in the zip file downloaded from the US Census Bureau will go. Make sure to include all the files in the zip file. Your second folder will be titled **geodata**, and is where the Florida OSM file will be placed. This should be the .osm.pbf file. Do not download any other versions.

> [!WARNING]
> Do NOT rename any of the files you download. 

Under the `AR-CAT-UCF` directory, create a new `sensitive.env` file. In this file, create two parameters: `API-TOKEN` and `HEADER`. This is case sensitive.

Place your discord API token in the `API-TOKEN` field as a string, like so: 

```
API-TOKEN="EXAMPLE"
```

Then create a `HEADER` field. This field is what gets sent to NOAA to know who is interacting with their system. You **should include** a valid email address in this header, so that NOAA is able to contact you if they have any concerns regarding your use of their API. 

Create this field like so:

```
HEADER="AR-CAT-UCF (example@email.com)"
```

Once this is setup, the bot is ready to go! You can change any configuration options by navigating to `AR-CAT-UCF -> configuration -> settings.py`. 