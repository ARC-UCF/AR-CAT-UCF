# IMPORTANT INFORMATION: ARC @ UCF DOCUMENTATION

## API Note

This system primarily utilizes [api.weather.gov](api.weather.gov), a web-based service provided by NOAA utilizing FEMA-IPAWS to disseminate weather alert information. 

Most of the functionality of this bot derives from this service, but also utilizes RSS, XML, and GIS shapefile feeds. For example, there's an XML feed provided for the hurricane information portion of this bot. 

## Config

Config contains the features for customizing most of the bot. Most of the features are based off of this, especially the alerting area. For this particular purpose, you're going to want to define the county name and state as `county, state`. As of now, the link is tied to specifically the florida area. The links which collect zone information utilize [https://api.weather.gov/zones?type=county&area=FL](https://api.weather.gov/zones?type=county&area=FL). For any changes, you want to specify the `area=FL` as the two digit code of your specified state. There are additional types provided in the `zones.py` code in the `utils` folder.

You will be required to change 3 different links in order to adjust their areas. Alternatively, you could remove `area=FL` if you wish to specify the entire CONUS. Good if you want to incorporate more than one state, but specifiying state areas should (theoretically) lessen computation times. Further, there is no reason to specify any state outside of Florida, as UCF is within Florida. However, if we are, say, FSU or UNF, universities in Tallahassee and Jcaksonville, respectively, including `area=GA` and `area=FL` would both be relavant due to the proximity of the FL/GA border.

More areas specified for the county area and state area will increase start up times considering that the zone geometry must be compiled at run time. This geometry is compiled by using the zone's api.weather.gov url, which includes the zone type and relevant information. County zones are `MultiPolygon` types, whereas alerts are typically `Polygon` types.

The provided links use `forecast`, `county`, and `fire` zone types for their polygon information. Each of these are used individually based upon the type of alert; `county` is used for flood alerts, `forecast` is often used for storm-based alerts, and `fire` is used for fire alerts. 

The bot also consists of a config which allows you to configure channels and pings. The bot will not work if it cannot find the channel it needs.

Configure the following as necessary:

* `countiesToMonitor`: include the names of counties to watch in the {county, state} format. Names are particular about punctuation. Capitalization does not matter, the names are normalized at runtime.
* `pings`: should be a dictionary linking each respective county/area to a ping. `arc` is uniquely determined. Remember that, to ping a role, it must be in the `<@&>` format for discord to recognize it.
* `channels`: utlizies a dictionary for specifying where each alert should go. This has to be the id, `channels.py` in the utils section automatically fetches the channel for you to use at runtime.
* `cycleTime`: the total amount of time the cycle should last. Each cycle is the total time it takes to run all parts. Each part is half of the cycle time.
* `bufferMiles`: how many miles the edge of an alert polygon must be for it to trigger the ARC alerts
* `storageTime`: the time, in hours, to store alerts after they are received.