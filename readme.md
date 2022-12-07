# This is a forecasting extension for the weewx weather system.

Copyright 2013-2020 Matthew Wall
Distributed under terms of the GPLv3

This package includes the forecasting module, unit tests, and a sample skin.
The following forecast sources are supported:

  US National Weather Service (NWS)
  the weather underground (WU)
  open weathermap (OWM)
  UK Met Office (UKMO)
  Aeris Weather
  World Weather Online (WWO)
  Dark Sky (DS)
  Zambretti
  tide predictions using xtide

The forecast extension includes a few independent parts:

- a forecast engine that downloads and/or generates forecast data
- a database schema that is normalized to store data from various sources
- a search list extension for using forecast data in reports
- a pre-defined forecast_table for inclusion in reports
- a pre-defined forecast_strip for inclusion in reports
- icons for cloud cover, storms, rainfall, snow, etc.

The forecast_table displays forecast data in a table with time going down the
page.  The forecast_table.inc file is a cheetah template designed to be
included in other templates.  At the beginning of the file is a list of
variables that determine which forecast data will be displayed.

The forecast_strip displays forecast data in a compact form with time going
from left to right.  The forecast_strip.inc file is a cheetah template designed
to be included in other templates.  At the beginning of the file is a list of
variables that determine which forecast data will be displayed.

Iconic color strip adds color gradient to the temperature bar. 
Weather outlook icons have been replaced with the current official WU ones downloaded from WU API documentation.

Iconic Color strip sample :

![Iconic color image strip](https://piwifotos.ddns.net/images/2021/02/06/image.png)

## Pre-requisites

- If you want NWS forecasts, determine your 3-character forecast office identifier and 6-character location identifier:
    <http://www.nws.noaa.gov/oh/hads/USGS/>

- If you want WU forecasts, obtain an api_key:
    <http://www.wunderground.com/weather/api/>

- If you want OWM forecasts, obtain an api_key:
  <http://openweathermap.org/appid>

- If you want UK Met Office forecasts, obtain an api_key:

  <http://metoffice.gov.uk/datapoint>

- If you want Aeris forecasts, obtain a client id and client secret:

  <http://www.aerisweather.com/account>

- If you want WWO forecasts, obtain an api_key:

  <https://developer.worldweatheronline.com/auth/register>

- If you want DS forecasts, obtain an api_key:

  <https://darksky.net/dev/register>

- If you want tide forecasts, install xtides:
    sudo apt-get install xtide
  Then determine your location:
    <http://tides.mobilegeographics.com/>

## Installation instructions:

1. run the installer:

    wee_extension --install weewx-forecast-3.4.0b12.zip

2. modify weewx.conf for your location:

- [Forecast]
  - [[NWS]]
  
| Parameter | Description |
| --- | --- |
|lid = MAZ014 | specify a location identifier |
| foid = BOX | specify a forecast office identifier |
| lid_desc = Framingham-Middlesex MA  | (optional) specify a lid description for cases where the lid is repeated in the forecast file and the user does not want the first entry for that lid. |
| | Just omit this entry entirely unless you have examined the forecast file and know the description of the repeated lid entry that you want to use. |
  - [[WU]]
    - api_key = XXXXXXXXXXXXXXXX    specify a weather underground api_key  
      - A location may be specified.  If it isn't, your stations lat/long will be used.

      - To specify the location for which to generate a forecast, one can specify the Geocode (lat, long), IATA Code, ICAO Code, Place ID or Postal Key.

      - These options are listed here:
        - <https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/>

        - If none of the following is specified, the station's latititude and longitude will be used.  If more than one is specified, the first will be used according to the order listed here.

        - geocode = "33.74,-84.39"
        - iataCode = DEN
        - icaoCode = KDEN
        - placeid = 327145917e06d09373dd2760425a88622a62d248fd97550eb4883737d8d1173b
        - postalKey = 81657:US
  - [[OWM]]
    - api_key = XXXXXXXXXXXXXXXX   # specify an open weathermap api_key
  - [[UKMO]]
    - api_key = XXXXXXXXXXXXXXXX   # specify a UK met office api_key
    - location = 2337              # specify code for UK location
  - [[Aeris]]
    - client_id = XXXXXXXXXXXXXXXX      # specify client identifier
    - client_secret = XXXXXXXXXXXXXXXX  # specify client secret key
  - [[DS]]
    -api_key = XXXXXXXXXXXXXXXX   # specify a dark sky api_key
  - [[XTide]]
    - location = Boston            # specify a location

1. restart weewx:

```sh
sudo /etc/init.d/weewx stop
sudo /etc/init.d/weewx start

```

This will result in a skin called forecast with web pages that illustrate how
to use the forecasts.  See comments in forecast.py for detailed customization
options.

## Credits

Icons were derived from Adam Whitcroft's climacons.
WU Icons : <https://docs.google.com/document/d/1eKCnKXI9xnoMGRRzOL1xPCBihNV2rOet08qpE_gArAY/edit>
