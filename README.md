# IMPORTANT INFORMATION: ARC @ UCF DOCUMENTATION

## API Note

This system primarily utilizes [api.weather.gov](api.weather.gov), a web-based service provided by NOAA utilizing FEMA-IPAWS to disseminate weather alert information. 

Most of the functionality of this bot derives from this service, but also utilizes RSS, XML, and GIS shapefile feeds. For example, there's an XML feed provided for the hurricane information portion of this bot. 

## Config

Config contains the features for customizing most of the bot. Most of the features are based off of this, especially the alerting area. For this particular purpose, you're going to want to define the county name and state as `county, state`. As of now, the link is tied to specifically the florida area. The links which collect zone information utilize [https://api.weather.gov/zones?type=county&area=FL](https://api.weather.gov/zones?type=county&area=FL). For any changes, you want to specify the `area=FL` as the two digit code of your specified state. There are additional types provided in the `zones.py` code in the `utils` folder.

You will be required to change 3 different links in order to adjust their areas. Alternatively, you could remove `area=FL` if you wish to specify the entire CONUS. Good if you want to incorporate more than one state, but specifiying state areas should (theoretically) lessen computation times. 

More areas specified for the county area and state area will increase start up times considering that the zone geometry must be compiled at run time.

The provided links use `forecast`, `county`, and `fire` zone types for their polygon information. Each of these are used individually based upon the type of alert; `county` is used for flood alerts, `forecast` is often used for storm-based alerts, and `fire` is used for fire alerts. 