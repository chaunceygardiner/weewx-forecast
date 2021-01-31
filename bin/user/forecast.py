#!/usr/bin/env python
# Copyright 2013-2020 Matthew Wall
# Distributed under the terms of the GNU Public License (GPLv3)
"""weewx module that provides forecasts

Compatibility:

   US National Weather Service (NWS) point forecasts as of July 2013
   Weather Underground (WU) 5day as of ~January 2020
   OpenWeatherMap 5-day/3-hour forecast as of January 2016
   UK Met Office 5-day/3-hour forecast as of 26 January 2016
   Aeris Weather as of 27 January 2016
   XTide 2.10 (possibly earlier versions as well)
   Dark Sky daily and hourly forecasts as of 6 January 2019

Design

   The forecasting module supports various forecast methods for weather and
   tides.  Weather forecasting can be downloaded (NWS, WU, OWM, UKMO, ...) or
   generated (Zambretti).  Tide forecasting is generated using XTide.

   There are two parts: a service that downloads/generates the forecasts, and
   a search list extension that provides access to the forecast data in weewx
   reports.

   A single table stores all forecast information.  This means that each record
   may have many unused fields, but it makes querying and database management
   a bit easier.  It also minimizes the number of variables needed for use in
   templates.  There are a few fields in each record that are common to every
   forecast method.  See the Database section in this file for details.

   The forecasting runs in a separate thread.  It is fire-and-forget - the
   main thread starts a forecasting thread and does not bother to check its
   status.  The main thread will never run more than one thread per forecast
   method.

Prerequisites

   The XTide forecast requires xtide.  On debian systems, do this:
     sudo apt-get install xtide

   Many of the forecasts require json.  json should be included in python
   2.6 and 2.7.  For python 2.5 on debian systems, do something like this:
     sudo apt-get install python-cjson

   Some of the forecasting sites require a subscription.  This extension
   supports only those services with a no-cost level of service.

Configuration

   To enable forecasting, add a [Forecast] section to weewx.conf, add a
   section to [Databases] to indicate where forecast data should be stored,
   then append user.forecast.XXXForecast to the service list for each
   forecasting method that should be enabled.

   To make forecast data available in reports, extend the CheetahGenerator
   then optionally customize the [Forecast] strings and parameters in the
   skin configuration.

   Some parameters can be defined in the Forecast section of weewx.conf, then
   overridden for specific forecasting methods as needed.  In the sample
   configuration below, the commented parameters will default to the indicated
   values.  Uncommented parameters must be specified.

[Forecast]
    # The database in which to record forecast information, defined in the
    # 'DataBindings' section of the weewx configuration.
    data_binding = forecast_binding

    # How often to calculate/download the forecast, in seconds
    #interval = 1800

    # How long to keep old forecasts, in seconds.  use None to keep forever.
    #max_age = 604800

    [[XTide]]
        # Location for which tides are desired
        location = Boston

        # How often to generate the tide forecast, in seconds
        #interval = 1209600

        # The length of the time period for forecasts, in seconds
        #duration = 2419200

        # How often to prune old tides from database, None to keep forever
        #max_age = 2419200

    [[Zambretti]]
        # hemisphere can be NORTH or SOUTH
        #hemisphere = NORTH

        # How often to generate the forecast, in seconds
        #interval = 3600

        # The period, in seconds, used to determine an average wind direction
        #winddir_period = 1800

        # The period, in seconds, used to determine the pressure trend
        #pressure_period = 10800

        # The lower and upper pressure define the range to which the forecaster
        # should be calibrated, in units of millibar (hPa).  The 'barometer'
        # pressure (not station pressure) is used to calculate the forecast.
        #lower_pressure = 950.0
        #upper_pressure = 1050.0

    [[NWS]]
        # First figure out your forecast office identifier (foid), then request
        # a point forecast using a url of this form in a web browser:
        #   http://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt&issuedby=YOUR_THREE_LETTER_FOID
        # Scan the output for a service location identifier corresponding
        # to your location.

        # National Weather Service location identifier
        lid = MAZ014

        # National Weather Service forecast office identifier
        foid = BOX

        # URL for point forecast matrix
        #url = http://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt

        # How often to download the forecast, in seconds
        #interval = 10800

    [[WU]]
        # An API key is required to access the weather underground.
        # obtain an API key here:
        #   http://www.wunderground.com/weather/api/
        api_key = KEY

        # To specify the location for which to generate a forecast, one can specify
        # the Geocode (lat, long), IATA Code, ICAO Code, Place ID or Postal Key.
        #
        # These options are listed here:
        # https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/
        #
        # If none of the following is specified, the station's latititude and longitude
        # will be used.  If more than one is specified, the first will be used according
        # to the order listed here.
        #
        # geocode   - "33.74,-84.39"
        # iataCode  - DEN
        # icaoCode  - KDEN
        # placeid   - 327145917e06d09373dd2760425a88622a62d248fd97550eb4883737d8d1173b
        # postalKey - 81657:US

        # The 5day forecast will be generated.  It is the forecast available with the
        # free API key one can obtain for providing station data to WU.
        # The 5day forecast is actually six days (if the current day is counted).

        # How often to download the forecast, in seconds
        #interval = 10800

    [[OWM]]
        # An API key is required to access the open weathermap forecasts.
        # Obtain a token here:
        #   http://openweathermap.org/appid
        api_key = APPID

        # The location can be one of the following:
        #   Boston,us            - city name, country code
        #   524901               - city ID
        #   37.8,-122.4          - latitude,longitude
        # If no location is specified, station latitude and longitude are used
        #location = 524901

        # There are two types of forecast available, 5-day/3-hour and
        # 16-day/daily.  Only the 5-day/3-hour forecasts are supported.
        #forecast_type = 5day3hour

        # How often to download the forecast, in seconds
        #interval = 10800

    [[UKMO]]
        # An API key is required to access the UK Met Office forecasts.
        # Create an account and obtain datapoint access here:
        #   http://metoffice.gov.uk/datapoint
        api_key = API_KEY

        # The location is one of the 5,000 or so locationIDs in the UK
        #location = 3772

        # How often to download the forecast, in seconds
        #interval = 10800

    [[Aeris]]
        # An ID and secret key are required to access Aeris forecasts.
        # Create an account then register an app here:
        #   http://www.aerisweather.com/account
        client_id = XXXXXXXXXXXXXXXXXXXXX
        client_secret = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY

        # The location is a 'supported place', which can be specified by:
        #   coordinate            37.25,-97.25
        #   city,state            seattle,wa
        #   city,state,country    new+york,new+york,us
        #   city,country          paris,fr
        #   zip/postal code       M3C4H9
        #   ICAO                  KBFI
        #   IATA airport code     ROA
        #   county/parish         fips:53033
        #   NOAA zone             MNZ029
        # If no location is specified, station latitude and longitude are used
        #location = MAZ014

        # Forecasts are available in 1, 3, 6, 12, or 24 hour increments.
        #forecast_type = 1hr

    [[WWO]]
        # An API key is required to access WWO forecasts.
        api_key = XXXX

        # The location can be specified by:
        #   US ZIP code           02139
        #   UK POST code          X
        #   Canadian Postal code  M3C4H9
        #   IP address            x.x.x.x
        #   coordinate            37.25,-97.25
        #   city name             London
        # If no location is specified, station latitude and longitude are used
        #location = 02139

        # Forecasts are available in 3, 6, 12, and 24 hour increments.
        #forecast_type = 3

    [[DS]]
        # An API key is required to access Dark Sky forecasts.
        api_key = XXXX

        # The location is specified using latitude and longitude in the format
        # latitude, longitude. If no location is specified, station latitude
        # and longitude are used
        #location = lat, long

        # How often to download the forecast, in seconds
        #interval = 10800

        # Two types of forecast are supported; hourly out to two or optionally
        # seven days and daily out to seven days. Default is daily.
        #forecast_type = hourly|daily

        # Extend the hourly forecast to 7 days. True extends the hourly
        # forecast to 7 days up from the default 2 days. Only applies if
        # forecast_type == hourly. Default is False.
        #extend_hourly = True|False

[DataBindings]
    [[forecast_binding]]
        database = forecast_sqlite

[Databases]
    [[forecast_sqlite]]
        database_type = SQLite
        database_name = archive/forecast.sdb
    [[forecast_mysql]]
        database_type = MySql
        database_name = forecast

[Engine]
    [[Services]]
        # append only the forecasting service(s) that you need
        archive_services = ... , user.forecast.XTideForecast, user.forecast.ZambrettiForecast, user.forecast.NWSForecast, user.forecast.WUForecast, user.forecast.OWMForecast, user.forecast.UKMOForecast, user.forecast.AerisForecast, user.forecast.WWOForecast, user.forecast.DSForecast


Skin Configuration

  To use the forecast variables in a skin, extend the search_list by adding
  something like this to weewx.conf:

[StdReport]
    [[StandardReport]]
        [[[CheetahGenerator]]]
            search_list_extensions = user.forecast.ForecastVariables

   Here are the options that can be specified in the skin.conf file.  The
   values below are the defaults.  Add these only to override the defaults,
   for example to translate to languages other than English.

[Forecast]
    [[Labels]]
        [[[Directions]]]
            # labels for compass directions
            N = N
            NNE = NNE
            NE = NE
            ENE = ENE
            E = E
            ESE = ESE
            SE = SE
            SSE = SSE
            S = S
            SSW = SSW
            SW = SW
            WSW = WSW
            W = W
            WNW = WNW
            NW = NW
            NNW = NNW

        [[[Tide]]]
            # labels for tides
            H = High Tide
            L = Low Tide

        [[[Zambretti]]]
            # mapping between zambretti codes and descriptive labels
            A = Settled fine
            B = Fine weather
            C = Becoming fine
            D = Fine, becoming less settled
            E = Fine, possible showers
            F = Fairly fine, improving
            G = Fairly fine, possible showers early
            H = Fairly fine, showery later
            I = Showery early, improving
            J = Changeable, mending
            K = Fairly fine, showers likely
            L = Rather unsettled clearing later
            M = Unsettled, probably improving
            N = Showery, bright intervals
            O = Showery, becoming less settled
            P = Changeable, some rain
            Q = Unsettled, short fine intervals
            R = Unsettled, rain later
            S = Unsettled, some rain
            T = Mostly very unsettled
            U = Occasional rain, worsening
            V = Rain at times, very unsettled
            W = Rain at frequent intervals
            X = Rain, very unsettled
            Y = Stormy, may improve
            Z = Stormy, much rain

        [[[Weather]]]
            # labels for components of a weather forecast
            temp = Temperature
            dewpt = Dewpoint
            humidity = Relative Humidity
            winddir = Wind Direction
            windspd = Wind Speed
            windchar = Wind Character
            windgust = Wind Gust
            clouds = Sky Coverage
            windchill = Wind Chill
            heatindex = Heat Index
            obvis = Obstructions to Visibility

            # types of precipitation
            rain = Rain
            rainshwrs = Rain Showers
            sprinkles = Rain Sprinkles
            tstms = Thunderstorms
            drizzle = Drizzle
            snow = Snow
            snowshwrs = Snow Showers
            flurries = Snow Flurries
            sleet = Ice Pellets
            frzngrain = Freezing Rain
            frzngdrzl = Freezing Drizzle
            hail = Hail

            # codes for sky cover
            CL = Clear
            FW = Few Clouds
            SC = Scattered Clouds
            BK = Broken Clouds
            B1 = Mostly Cloudy
            B2 = Considerable Cloudiness
            OV = Overcast

            # codes for precipitation
            S = Slight Chance
            C = Chance
            L = Likely
            O = Occasional
            D = Definite

            IS = Isolated
            #SC = Scattered      # conflicts with scattered clouds
            NM = Numerous
            EC = Extensive Coverage
            PA = Patchy
            AR = Areas
            WD = Widespread

            # quantifiers for the precipitation codes
            Sq  = '<20%'
            Cq  = '30-50%'
            Lq  = '60-70%'
            Oq  = '80-100%'
            Dq  = '80-100%'

            ISq = '<20%'
            SCq = '30-50%'
            NMq = '60-70%'
            ECq = '80-100%'
            PAq = '<25%'
            ARq = '25-50%'
            WDq = '>50%'

            # codes for obstructions to visibility
            F = Fog
            PF = Patchy Fog
            F+ = Dense Fog
            PF+ = Patchy Dense Fog
            H = Haze
            BS = Blowing Snow
            K = Smoke
            BD = Blowing Dust
            AF = Volcanic Ash
            M = Mist
            FF = Freezing Fog
            DST = Dust
            SND = Sand
            SP = Spray
            DW = Dust Whirls
            SS = Sand Storm
            LDS = Low Drifting Snow
            LDD = Low Drifting Dust
            LDN = Low Drifting Sand
            BN = Blowing Sand
            SF = Shallow Fog

            # codes for wind character:
            LT = Light
            GN = Gentle
            BZ = Breezy
            WY = Windy
            VW = Very Windy
            SD = Strong/Damaging
            HF = Hurricane Force

Variables for Templates

  This section shows some of the variables that can be used in template files.

Labels

  Labels are grouped by module and identified by key.  For example, specifying
  $forecast.label('Zambretti', 'C') returns 'Becoming fine', and specifying
  $forecast.label('Weather', 'temp') returns 'Temperature'.

$forecast.label(module, key)

XTide

  The index is the nth event from the current time.

$forecast.xtide(0).dateTime     date/time that the forecast was requested
$forecast.xtide(0).issued_ts    date/time that the forecast was created
$forecast.xtide(0).event_ts     date/time of the event
$forecast.xtide(0).hilo         H or L
$forecast.xtide(0).offset       depth above/below mean low tide
$forecast.xtide(0).location     where the tide is forecast

for tide in $forecast.xtides
  $tide.event_ts $tide.hilo $tide.offset

Zambretti

  The Zambretti forecast consists of a code and corresponding description.

$forecast.zambretti.dateTime    date/time that the forecast was requested
$forecast.zambretti.issued_ts   date/time that the forecast was created
$forecast.zambretti.event_ts    date/time of the forecast
$forecast.zambretti.code        zambretti forecast code (A-Z)

NWS, WU, OWM, UKMO, Aeris, WWO

  Elements of a weather forecast are referred to by period or daily summary.
  A forecast source must be specified.

for $period in $forecast.weather_periods('NWS')
  $period.dateTime
  $period.event_ts
  ...

  The summary is a single-day aggregate of any periods in that day.

$summary = $forecast.weather_summary('NWS')
$summary.dateTime
$summary.event_ts
$summary.location
$summary.clouds
$summary.temp
$summary.tempMin
$summary.tempMax
$summary.dewpoint
$summary.dewpointMin
$summary.dewpointMax
$summary.humidity
$summary.humidityMin
$summary.humidityMax
$summary.windSpeed
$summary.windSpeedMin
$summary.windSpeedMax
$summary.windGust
$summary.windDir
$summary.windDirs        dictionary
$summary.windChar
$summary.windChars       dictionary
$summary.pop
$summary.precip          array
$summary.obvis           array
"""


# here are a few web sites with weather/tide summaries, some more concise than
# others, none quite what we want:
#
# http://www.tides4fishing.com/
# http://www.surf-forecast.com/
# http://ocean.peterbrueggeman.com/tidepredict.html

from __future__ import absolute_import
from __future__ import print_function
import calendar
import configobj
import datetime
import gzip
import hashlib
import logging
import six.moves.http_client
import os, errno
import re
import socket
import subprocess
import threading
import time
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse

from io import BytesIO
from six.moves import range

import weeutil.logger

log = logging.getLogger(__name__)

try:
    import cjson as json
    setattr(json, 'dumps', json.encode)
    setattr(json, 'loads', json.decode)
except (ImportError, AttributeError):
    try:
        import simplejson as json
    except ImportError:
        import json

import weewx
import weedb
import weewx.manager
import weeutil.weeutil
from weewx.engine import StdService
from weewx.cheetahgenerator import SearchList

VERSION = "3.4.0b11"

if weewx.__version__ < "4":
    raise weewx.UnsupportedFeature(
        "WeeWX 4 is required, found %s" % weewx.__version__)


def logdbg(msg):
    log.debug('%s: %s' % (threading.currentThread().getName(), msg))

def loginf(msg):
    log.info('%s: %s' % (threading.currentThread().getName(), msg))

def logerr(msg):
    log.error('%s: %s' % (threading.currentThread().getName(), msg))

def mkdir_p(path):
    """equivalent to 'mkdir -p'"""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# FIXME: 'method' should be called 'source'
# FIXME: obvis should be an array?
# FIXME: add field for tornado, hurricane/cyclone?
# FIXME: 'hour' is not being used properly, probably could be punted
# FIXME: provide a 'reported_location' field for loc as returned by api call

# FIXME: extend the schema to include the following attributes:

# OWM defines the following:
#  pressure
#  sea_level
#  grnd_level

# UKMO defines the following:
#  F - feels-like temperature, C
#  V - visibility (UN, VP, PO, MO, GO, VG, EX)
#  W - weather type (0-30)
#
# textual description
# wind direction is 16-point compass
# air quality index
# UV index is 1-11

# Aeris defines the following:
# avgTempF
# iceaccum
# maxHumidity
# minHumidity
# pressureIN
# sky
# feelslikeF
# minFeelslikeF
# maxFeelslikeF
# avgFeelslikeF
# maxDewpointF
# minDewpointF
# avgDewpointF
# windDirMax
# windDirMin
# windSpeedMaxMPH
# windSpeedMinMPH
# windDir80m
# windDirMax80m
# windDirMin80m
# windGust80mMPH
# windSpeed80mMPH
# windSpeedMax80mMPH
# windSpeedMin80mMPH
# weather
# weatherCoded
# weatherCoded.timestamp
# weatherCoded.wx
# weatherPrimary
# weatherPrimaryCoded
# cloudsCoded
# icon
# isDay
# sunrise
# sunriseISO
# sunset
# sunsetISO

# WWO defines the following:
# chanceoffog
# chanceoffrost
# chanceofovercast
# chanceofrain
# chanceofremdry
# chanceofsnow
# chanceofsunshine
# chanceofthunder
# chanceofwindy
# feelslike
# pressure
# visibility
# weatherCode
# weatherDesc
# weatherIconUrl
# winddirDegree

"""Database Schema

   The schema assumes that forecasts are deterministic - a forecast made at
   time t will always return the same results.

   For most use cases, the database will contain only the latest forecast or
   perhaps the latest plus one or two previous forecasts.  However there is
   also a use case in which forecasts are retained indefinitely for analysis.

   The names in the schema are based on NWS point and area forecasts, plus
   extensions to include additional information from Weather Underground and
   other forecast sources.

   When deciding what to store in the database, try to focus on just the facts.
   There is room for interpretation in the description field, but otherwise
   leave the interpretation out.  For example, storm surge warnings, small
   craft advisories are derivative - they are based on wind/wave levels.

   This schema captures all forecasts and defines the following fields:

   method     - forecast method, e.g., Zambretti, NWS, XTide
   usUnits    - units of the forecast, either US or METRIC
   dateTime   - timestamp in seconds when forecast was obtained
   issued_ts  - timestamp in seconds when forecast was made
   event_ts   - timestamp in seconds for the event
   duration   - length of the forecast period
   location
   desc       - textual description of the forecast

   hilo       indicates whether this is a high or low tide
   offset     how high or low the tide is relative to mean low
   waveheight average wave height
   waveperiod average wave period

   zcode      used only by zambretti forecast

   database   nws                  wu-5day                       owm
   ---------- -------------------- ----------------------------- ----------

   hour       3HRLY | 6HRLY        5day                          3
   tempMin    MIN/MAX | MAX/MIN    tempertureMax                 temp_min
   tempMax    MIN/MAX | MAX/MIN    tempertureMin                 temp_max
   temp       TEMP                 daypart.temperature           temp
   dewpoint   DEWPT
   humidity   RH                   daypart.relativeHumidity      humidity
   windDir    WIND DIR | PWIND DIR daypart.windDirectionCardinal wind.deg
   windSpeed  WIND SPD             daypart.windSpeed             wind.speed
   windGust   WIND GUST
   windChar   WIND CHAR
   clouds     CLOUDS | AVG CLOUDS  daypart.wxDayShort            clouds.all
   pop        POP 12HR             daypart.precipChance          pop
   qpf        QPF 12HR             daypart.qpf                   rain.3h
   qsf        SNOW 12HR            daypart.qpfSnow               snow.3h
   rain       RAIN
   rainshwrs  RAIN SHWRS
   tstms      TSTMS
   drizzle    DRIZZLE
   snow       SNOW
   snowshwrs  SNOWSHWRS
   flurries   FLURRIES
   sleet      SLEET
   frzngrain  FRZNG RAIN
   frzngdrzl  FRZNG DRZL
   hail
   obvis      OBVIS
   windChill  WIND CHILL           daypart.temperatureWindChill
   heatIndex  HEAT INDEX           daypart.temperatureHeatIndex
   uvIndex                         daypart.uvIndex
   airQuality

   database   ukmo     aeris         wwo            dark sky
   ---------- -------- ------------- -------------- ---------

   hour       3        1,3,6,12,24   3,6,12,24      time
   tempMin             minTempF                     temperatureLow
   tempMax             maxTempF                     temperatureHigh
   temp       T        tempF         tempF          temperature
   dewpoint            dewpointF     DewPointF      dewPoint
   humidity   H        humidity      humidity       humidity
   windDir    D        windDir       winddir16Point windBearing
   windSpeed  S        windSpeedMPH  windspeedMiles windSpeed
   windGust   G        windGustMPH   WindGustMiles  windGust
   windChar   
   clouds                            cloudcover     cloudCover
   pop        Pp       pop                          precipProbability
   qpf                 precipIN      precipMM
   qsf                 showIN                       precipAccumulation
   rain       
   rainshwrs  
   tstms      
   drizzle    
   snow       
   snowshwrs  
   flurries   
   sleet      
   frzngrain  
   frzngdrzl  
   hail       
   obvis      
   windChill                         WindChillF
   heatIndex                         HeatIndexF
   uvIndex    U        uvi                          uvIndex
   airQuality 
"""

schema = [('method',     'VARCHAR(10) NOT NULL'),
          ('usUnits',    'INTEGER NOT NULL'),  # weewx.US
          ('dateTime',   'INTEGER NOT NULL'),  # epoch
          ('issued_ts',  'INTEGER NOT NULL'),  # epoch
          ('event_ts',   'INTEGER NOT NULL'),  # epoch
          ('duration',   'INTEGER'),           # seconds
          ('location',   'VARCHAR(64)'),
          ('desc',       'VARCHAR(256)'),

          # Zambretti fields
          ('zcode',      'CHAR(1)'),

          # weather fields
          ('hour',       'INTEGER'),     # 00 to 23
          ('tempMin',    'REAL'),        # degree F
          ('tempMax',    'REAL'),        # degree F
          ('temp',       'REAL'),        # degree F
          ('dewpoint',   'REAL'),        # degree F
          ('humidity',   'REAL'),        # percent
          ('windDir',    'VARCHAR(3)'),  # N,NE,E,SE,S,SW,W,NW (NNE,ENE,...)
          ('windSpeed',  'REAL'),        # mph
          ('windGust',   'REAL'),        # mph
          ('windChar',   'VARCHAR(2)'),  # GN,LT,BZ,WY,VW,SD,HF
          ('clouds',     'VARCHAR(2)'),  # CL,FW,SC,BK,OV,B1,B2
          ('pop',        'REAL'),        # percent
          ('qpf',        'VARCHAR(8)'),  # range or value (inch)
          ('qsf',        'VARCHAR(5)'),  # range or value (inch)
          ('rain',       'VARCHAR(2)'),  # S,C,L,O,D
          ('rainshwrs',  'VARCHAR(2)'),  # S,C,L,O,D
          ('tstms',      'VARCHAR(2)'),  # S,C,L,O,D
          ('drizzle',    'VARCHAR(2)'),  # S,C,L,O,D
          ('snow',       'VARCHAR(2)'),  # S,C,L,O,D
          ('snowshwrs',  'VARCHAR(2)'),  # S,C,L,O,D
          ('flurries',   'VARCHAR(2)'),  # S,C,L,O,D
          ('sleet',      'VARCHAR(2)'),  # S,C,L,O,D
          ('frzngrain',  'VARCHAR(2)'),  # S,C,L,O,D
          ('frzngdrzl',  'VARCHAR(2)'),  # S,C,L,O,D
          ('hail',       'VARCHAR(2)'),  # S,C,L,O,D
          ('obvis',      'VARCHAR(3)'),  # F,PF,F+,PF+,H,BS,K,BD
          ('windChill',  'REAL'),        # degree F
          ('heatIndex',  'REAL'),        # degree F

          ('uvIndex',    'INTEGER'),     # 1-15
          ('airQuality', 'INTEGER'),     # 1-10

          # tide fields
          ('hilo',       'CHAR(1)'),     # H or L
          ('offset',     'REAL'),        # relative to mean low

          # marine-specific conditions
          ('waveheight', 'REAL'),
          ('waveperiod', 'REAL'),
          ]

precip_types = [
    'rain',
    'rainshwrs',
    'tstms',
    'drizzle',
    'snow',
    'snowshwrs',
    'flurries',
    'sleet',
    'frzngrain',
    'frzngdrzl',
    'hail']

directions_label_dict = {
    'N':   'N',
    'NNE': 'NNE',
    'NE':  'NE',
    'ENE': 'ENE',
    'E':   'E',
    'ESE': 'ESE',
    'SE':  'SE',
    'SSE': 'SSE',
    'S':   'S',
    'SSW': 'SSW',
    'SW':  'SW',
    'WSW': 'WSW',
    'W':   'W',
    'WNW': 'WNW',
    'NW':  'NW',
    'NNW': 'NNW'}

tide_label_dict = {
    'H': 'High Tide',
    'L': 'Low Tide'}

weather_label_dict = {
    'temp'      : 'Temperature',
    'dewpt'     : 'Dewpoint',
    'humidity'  : 'Relative Humidity',
    'winddir'   : 'Wind Direction',
    'windspd'   : 'Wind Speed',
    'windchar'  : 'Wind Character',
    'windgust'  : 'Wind Gust',
    'clouds'    : 'Sky Coverage',
    'windchill' : 'Wind Chill',
    'heatindex' : 'Heat Index',
    'obvis'     : 'Obstructions to Visibility',
    # types of precipitation
    'rain'      : 'Rain',
    'rainshwrs' : 'Rain Showers',
    'sprinkles' : 'Rain Sprinkles',     # FIXME: no db field for this
    'tstms'     : 'Thunderstorms',
    'drizzle'   : 'Drizzle',
    'snow'      : 'Snow',
    'snowshwrs' : 'Snow Showers',
    'flurries'  : 'Snow Flurries',
    'sleet'     : 'Ice Pellets',
    'frzngrain' : 'Freezing Rain',
    'frzngdrzl' : 'Freezing Drizzle',
    'hail'      : 'Hail',
    # codes for clouds
    'CL': 'Clear',
    'FW': 'Few Clouds',
#    'SC': 'Scattered Clouds',
    'BK': 'Broken Clouds',
    'B1': 'Mostly Cloudy',
    'B2': 'Considerable Cloudiness',
    'OV': 'Overcast',
    # codes for precipitation
    'S' : 'Slight Chance',      'Sq' : '<20%',
    'C' : 'Chance',             'Cq' : '30-50%',
    'L' : 'Likely',             'Lq' : '60-70%',
    'O' : 'Occasional',         'Oq' : '80-100%',
    'D' : 'Definite',           'Dq' : '80-100%',
    'IS': 'Isolated',           'ISq': '<20%',
    'SC': 'Scattered',          'SCq': '30-50%',
    'NM': 'Numerous',           'NMq': '60-70%',
    'EC': 'Extensive',          'ECq': '80-100%',
    'PA': 'Patchy',             'PAq': '<25%',
    'AR': 'Areas',              'ARq': '25-50%',
    'WD': 'Widespread',         'WDq': '>50%',
    # codes for obstructed visibility
    'F'  : 'Fog',
    'PF' : 'Patchy Fog',
    'F+' : 'Dense Fog',
    'PF+': 'Patchy Dense Fog',
    'H'  : 'Haze',
    'BS' : 'Blowing Snow',
    'K'  : 'Smoke',
    'BD' : 'Blowing Dust',
    'AF' : 'Volcanic Ash',
    'M'  : 'Mist',              # WU
    'FF' : 'Freezing Fog',      # WU
    'DST': 'Dust',              # WU
    'SND': 'Sand',              # WU
    'SP' : 'Spray',             # WU
    'DW' : 'Dust Whirls',       # WU
    'SS' : 'Sand Storm',        # WU
    'LDS': 'Low Drifting Snow', # WU
    'LDD': 'Low Drifting Dust', # WU
    'LDN': 'Low Drifting Sand', # WU
    'BN' : 'Blowing Sand',      # WU
    'SF' : 'Shallow Fog',       # WU
    # codes for wind character
    'LT': 'Light',
    'GN': 'Gentle',
    'BZ': 'Breezy',
    'WY': 'Windy',
    'VW': 'Very Windy',
    'SD': 'Strong/Damaging',
    'HF': 'Hurricane Force',
    # weather type
    'A' : 'Hail',              # aeris
    'BR': 'Mist',              # aeris
    'BY': 'Blowing Spray',     # aeris
    'FR': 'Frost',             # aeris
    'IC': 'Ice Crystals',      # aeris
    'IF': 'Ice Fog',           # aeris
    'IP': 'Ice Pellets/Sleet', # aeris
    'L' : 'Drizzle',           # aeris
    'R' : 'Rain',              # aeris
    'RW': 'Rain Showers',      # aeris
    'RS': 'Rain/Snow Mix',     # aeris
    'SI': 'Snow/Sleet Mix',    # aeris
    'WM': 'Wintry Mix',        # aeris
#    'S' : 'Snow,               # aeris
    'SW': 'Snow Showers',      # aeris
    'T' : 'Thunderstorms',     # aeris
    'UP': 'Unknown Precipitation', # aeris
    'VA': 'Volcanic Ash',      # aeris
    'WP': 'Waterspouts',       # aeris
    'ZF': 'Freezing Fog',      # aeris
    'ZL': 'Freezing Drizzle',  # aeris
    'ZR': 'Freezing Rain',     # aeris
    'ZY': 'Freezing Spray',    # aeris
    }

class ForecastThread(threading.Thread):
    def __init__(self, target, *args):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)

class Forecast(StdService):
    """Base class for forecasting services."""

    def __init__(self, engine, config_dict, fid,
                 interval=1800, max_age=604800):
        super(Forecast, self).__init__(engine, config_dict)
        loginf('%s: forecast version %s' % (fid, VERSION))
        self.method_id = fid

        # single database for all different types of forecasts
        d = config_dict.get('Forecast', {})
        self.binding = d.get('data_binding', 'forecast_binding')

        # these options can be different for each forecast method

        # how often to do the forecast
        self.interval = self._get_opt(d, fid, 'interval', interval)
        self.interval = int(self.interval)
        # how long to keep forecast records
        self.max_age = self._get_opt(d, fid, 'max_age', max_age)
        self.max_age = self.toint('max_age', self.max_age, None, fid)
        # option to vacuum the sqlite database
        self.vacuum = self._get_opt(d, fid, 'vacuum', False)
        self.vacuum = weeutil.weeutil.tobool(self.vacuum)
        # how often to retry database failures
        self.db_max_tries = self._get_opt(d, fid, 'database_max_tries', 3)
        self.db_max_tries = int(self.db_max_tries)
        # how long to wait between retries, in seconds
        self.db_retry_wait = self._get_opt(d, fid, 'database_retry_wait', 10)
        self.db_retry_wait = int(self.db_retry_wait)
        # use single_thread for debugging
        self.single_thread = self._get_opt(d, fid, 'single_thread', False)
        self.single_thread = weeutil.weeutil.tobool(self.single_thread)
        # option to save raw forecast to disk
        self.save_raw = self._get_opt(d, fid, 'save_raw', False)
        self.save_raw = weeutil.weeutil.tobool(self.save_raw)
        # option to save failed foreast to disk for diagnosis
        self.save_failed = self._get_opt(d, fid, 'save_failed', False)
        self.save_failed = weeutil.weeutil.tobool(self.save_failed)
        # where to save the raw forecasts
        self.diag_dir = self._get_opt(d, fid, 'diagnostic_dir', '/var/tmp/fc')
        # how long to wait before doing the forecast
        self.delay = int(self._get_opt(d, fid, 'delay', 0))

        self.last_ts = 0
        self.updating = False
        self.last_raw_digest = None
        self.last_fail_digest = None

        # setup database
        dbm_dict = weewx.manager.get_manager_dict_from_config(config_dict, self.binding)
        with weewx.manager.open_manager(dbm_dict, initialize=True) as dbm:
            # ensure schema on disk matches schema in memory
            dbcol = dbm.connection.columnsOf(dbm.table_name)
            memcol = [x[0] for x in dbm_dict['schema']]
            if dbcol != memcol:
                raise Exception('%s: schema mismatch: %s != %s' %
                                (self.method_id, dbcol, memcol))
            # find out when the last forecast happened
            self.last_ts = Forecast.get_last_forecast_ts(dbm, self.method_id)

    def _bind(self):
        # ensure that the forecast has a chance to update on each new record
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.update_forecast)

    def _get_opt(self, d, fid, label, default_v):
        """get an option from dict, prefer specialized value if one exists"""
        v = d.get(label, default_v)
        dd = d.get(fid, {})
        v = dd.get(label, v)
        return v

    @staticmethod
    def get_loc_from_station(config_dict):
        # FIXME: get this from station object, not the config_dict
        lat = config_dict['Station'].get('latitude', None)
        lon = config_dict['Station'].get('longitude', None)
        if lat is not None and lon is not None:
            return '%s,%s' % (lat, lon)
        return None

    @staticmethod
    def obfuscate(s):
        return 'X' * (len(s) - 4) + s[-4:]

    @staticmethod
    def get_masked_url(url, api_key):
        """look for specified key in the url and mask all but 4 characters"""
        masked = list(url)
        idx = url.find(api_key)
        if idx >= 0:
            for i in range(len(api_key) - 4):
                masked[idx + i] = 'X'
        return ''.join(masked)

    @staticmethod
    def toint(label, value, default_value, method):
        """convert to integer but also permit a value of None"""
        if isinstance(value, str) and value.lower() == 'none':
            value = None
        if value is not None:
            try:
                value = int(value)
            except ValueError:
                logerr("%s: bad value '%s' for %s" %
                       (method, value, label))
                value = default_value
        return value

    @staticmethod
    def str2int(n, s, method):
        if s is not None and s != '':
            try:
                return int(s)
            except (ValueError, TypeError) as e:
                logerr("%s: conversion error for %s from '%s': %s" %
                       (method, n, s, e))
        return None

    @staticmethod
    def str2float(n, s, method):
        if s is not None and s != '':
            try:
                return float(s)
            except (ValueError, TypeError) as e:
                logerr("%s: conversion error for %s from '%s': %s" %
                       (method, n, s, e))
        return None

    @staticmethod
    def pct2clouds(value):
        # map a percentage to a cloud indicator
        try:
            v = int(value)
        except ValueError as TypeError:
            return None
        if 0 <= v <= 5:
            return 'CL'
        elif 5 < v <= 25:
            return 'FW'
        elif 25 < v <= 50:
            return 'SC'
        elif 50 < v <= 69:
            return 'B1'
        elif 69 < v <= 87:
            return 'B2'
        elif 87 < v <= 100:
            return 'OV'
        return None

    @staticmethod
    def deg2dir(value):
        # map a decimal degree to a compass direction
        try:
            v = float(value)
        except ValueError as TypeError:
            return None
        if 0 <= v <= 22.5:
            return 'N'
        elif 22.5 < v <= 65.5:
            return 'NE'
        elif 65.5 < v <= 112.5:
            return 'E'
        elif 112.5 < v <= 157.5:
            return 'SE'
        elif 157.5 < v <= 202.5:
            return 'S'
        elif 202.5 < v <= 247.5:
            return 'SW'
        elif 247.5 < v <= 292.5:
            return 'W'
        elif 292.5 < v <= 337.5:
            return 'NW'
        elif 337.5 < v <= 360:
            return 'N'
        return None

    @staticmethod
    def save_fc_data(fc, dirname, basename='forecast-data', msgs=None):
        """save raw forecast data to disk, typically for diagnostics"""
        ts = int(time.time())
        tstr = time.strftime('%Y%m%d%H%M', time.localtime(ts))
        mkdir_p(dirname)
        fn = '%s/%s-%s' % (dirname, basename, tstr)
        with open(fn, 'w') as f:
            if msgs is not None:
                for m in msgs:
                    f.write("%s\n" % m)
            f.write(fc)

    def save_raw_forecast(self, fc, basename='raw', msgs=None):
        m = hashlib.md5()
        m.update(fc)
        digest = m.hexdigest()
        if self.last_raw_digest == digest:
            return
        Forecast.save_fc_data(fc, self.diag_dir, basename=basename, msgs=msgs)
        self.last_raw_digest = digest

    def save_failed_forecast(self, fc, basename='fail', msgs=None):
        m = hashlib.md5()
        m.update(fc)
        digest = m.hexdigest()
        if self.last_fail_digest == digest:
            return
        Forecast.save_fc_data(fc, self.diag_dir, basename=basename, msgs=msgs)
        self.last_fail_digest = digest

    def update_forecast(self, event):
        if self.single_thread:
            self.do_forecast(event)
        elif self.updating:
            logdbg('%s: update thread already running' % self.method_id)
        elif self.last_ts is None or time.time() - self.interval > self.last_ts:
            t = ForecastThread(self.do_forecast, event)
            t.setName(self.method_id + 'Thread')
            logdbg('%s: starting thread' % self.method_id)
            t.start()
        else:
            logdbg('%s: not yet time to do the forecast' % self.method_id)

    def do_forecast(self, event):
        self.updating = True
        try:
            if self.delay:
                time.sleep(self.delay)
            records = self.get_forecast(event)
            if records is None:
                return
            dbm_dict = weewx.manager.get_manager_dict_from_config(self.config_dict, self.binding)
            with weewx.manager.open_manager(dbm_dict) as dbm:
                Forecast.save_forecast(dbm, records, self.method_id,
                                       self.db_max_tries, self.db_retry_wait)
                self.last_ts = int(time.time())
                if self.max_age is not None:
                    Forecast.prune_forecasts(dbm, self.method_id,
                                             self.last_ts - self.max_age,
                                             self.db_max_tries,
                                             self.db_retry_wait)
                if self.vacuum:
                    Forecast.vacuum_database(dbm, self.method_id)
        except Exception as e:
            logerr('%s: forecast failure: %s, dbm_dict: %s' % (self.method_id, e, dbm_dict))
        finally:
            logdbg('%s: terminating thread' % self.method_id)
            self.updating = False

    def get_forecast(self, event):
        """get the forecast, return an array of forecast records."""
        return None

    @staticmethod
    def get_last_forecast_ts(dbm, method_id):
        sql = "select dateTime,issued_ts from %s where method = '%s' and dateTime = (select max(dateTime) from %s where method = '%s') limit 1" % (dbm.table_name, method_id, dbm.table_name, method_id)
#        sql = "select max(dateTime),issued_ts from %s where method = '%s'" % (table, method_id)
        r = dbm.getSql(sql)
        if r is None:
            return None
        logdbg('%s: last forecast issued %s, requested %s' %
               (method_id,
                weeutil.weeutil.timestamp_to_string(r[1]),
                weeutil.weeutil.timestamp_to_string(r[0])))
        return int(r[0])

    @staticmethod
    def save_forecast(dbm, records, method_id, max_tries=3, retry_wait=10):
        for count in range(max_tries):
            try:
                logdbg('%s: saving %d forecast records' %
                       (method_id, len(records)))
                dbm.addRecord(records)
                loginf('%s: saved %d forecast records' %
                       (method_id, len(records)))
                break
            except weedb.DatabaseError as e:
                logerr('%s: save failed (attempt %d of %d): %s' %
                       (method_id, (count + 1), max_tries, e))
                logdbg('%s: waiting %d seconds before retry' %
                       (method_id, retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('save failed after %d attempts' % max_tries)

    @staticmethod
    def prune_forecasts(dbm, method_id, ts, max_tries=3, retry_wait=10):
        """remove forecasts older than ts from the database"""

        sql = "delete from %s where method = '%s' and dateTime < %d" % (
            dbm.table_name, method_id, ts)
        for count in range(max_tries):
            try:
                logdbg('%s: deleting forecasts prior to %d' % (method_id, ts))
                dbm.getSql(sql)
                loginf('%s: deleted forecasts prior to %d' % (method_id, ts))
                break
            except weedb.DatabaseError as e:
                logerr('%s: prune failed (attempt %d of %d): %s' %
                       (method_id, (count + 1), max_tries, e))
                logdbg('%s: waiting %d seconds before retry' %
                       (method_id, retry_wait))
                time.sleep(retry_wait)
        else:
            raise Exception('prune failed after %d attemps' % max_tries)

    @staticmethod
    def vacuum_database(dbm, method_id):
        # vacuum will only work on sqlite databases.  it will compact the
        # database file.  if we do not do this, the file grows even though
        # we prune records from the database.  it should be ok to run this
        # on a mysql database - it will silently fail.
        try:
            logdbg('%s: vacuuming the database' % method_id)
            dbm.getSql('vacuum')
        except weedb.DatabaseError as e:
            logdbg('%s: vacuuming failed: %s' % (method_id, e))

    # this method is used only by the unit tests
    @staticmethod
    def get_saved_forecasts(dbm, method_id, since_ts=None):
        """return saved forecasts since the indicated timestamp

        since_ts - timestamp, in seconds.  a value of None will return all.
        """
        sql = "select * from %s where method = '%s'" % (
            dbm.table_name, method_id)
        if since_ts is not None:
            sql += " and dateTime > %d" % since_ts
        records = []
        for r in dbm.genSql(sql):
            records.append(r)
        return records


# -----------------------------------------------------------------------------
# Zambretti Forecaster
#
# The zambretti forecast is based upon recent weather conditions.  Supposedly
# it is about 90% to 94% accurate.  It is simply a table of values based upon
# the current barometric pressure, pressure trend, winter/summer, and wind
# direction.  Apparently it is most accurate when used at 09:00 to provide
# the forecast for the day.
#
# The forecast is generated using data from a period of time prior to 09:00.
# The forecast will be the same no matter what time of day it is requested, as
# long as there are data for the period prior to 09:00.  A request for forecast
# before 09:00 will return the previous day forecast.  If the forecast has
# already been generated, it will not be re-generated.
#
# The periods for calculating wind direction and pressure trend can be
# specified via configuration file.
#
# brief history of Nagretti and Zambra:
#   http://www.whitbyweather.com/index.php?p=1_56_Zambretti-Forecaster
#
# meteormetrics zambretti description:
#   http://www.meteormetrics.com/zambretti.htm
#
# beteljuice implementation:
#   http://www.beteljuice.co.uk/zambretti/forecast.html
#   http://www.whitbyweather.com/Zambretti/forecaster.html
# -----------------------------------------------------------------------------

Z_KEY = 'Zambretti'

class ZambrettiForecast(Forecast):
    """calculate zambretti code"""

    def __init__(self, engine, config_dict):
        super(ZambrettiForecast, self).__init__(engine, config_dict, Z_KEY,
                                                interval=600)
        d = config_dict.get('Forecast', {}).get(Z_KEY, {})
        self.hemisphere = d.get('hemisphere', 'NORTH')
        self.lower_pressure = float(d.get('lower_pressure', 950.0))
        self.upper_pressure = float(d.get('upper_pressure', 1050.0))
        self.winddir_period = int(d.get('winddir_period', 1800))
        self.pressure_period = int(d.get('pressure_period', 10800))
        # keep track of the last time for which we issued a forecast
        self.last_event_ts = 0
        loginf('%s: interval=%s max_age=%s winddir_period=%s pressure_period=%s hemisphere=%s lower_pressure=%s upper_pressure=%s' %
               (Z_KEY, self.interval, self.max_age,
                self.winddir_period, self.pressure_period,
                self.hemisphere, self.lower_pressure, self.upper_pressure))
        self._bind()

    def get_forecast(self, event):
        """Generate a zambretti forecast using data from 09:00.  If the
        current time is before 09:00, use the data from the previous day."""
        now = event.record['dateTime']
        ts = weeutil.weeutil.startOfDay(now) + 32400
        if now < ts:
            ts -= 86400
        if self.last_event_ts == ts:
            logdbg('%s: forecast was already calculated for %s' %
                   (Z_KEY, weeutil.weeutil.timestamp_to_string(ts)))
            return None

        logdbg('%s: generating forecast for %s' %
               (Z_KEY, weeutil.weeutil.timestamp_to_string(ts)))
        logdbg('%s: using winddir from %s to %s' %
               (Z_KEY,
                weeutil.weeutil.timestamp_to_string(ts - self.winddir_period),
                weeutil.weeutil.timestamp_to_string(ts)))
        logdbg('%s: using pressure from %s to %s' %
               (Z_KEY,
                weeutil.weeutil.timestamp_to_string(ts - self.pressure_period),
                weeutil.weeutil.timestamp_to_string(ts)))

        try:
            dbm_dict = weewx.manager.get_manager_dict_from_config(self.config_dict, 'wx_binding')
            with weewx.manager.open_manager(dbm_dict) as dbm:
                r = dbm.getSql('SELECT usUnits FROM %s LIMIT 1' %
                               dbm.table_name)
                units = r[0]
                r = dbm.getSql('SELECT AVG(windDir) FROM %s '
                               'WHERE dateTime >= %s AND dateTime <= %s' %
                               (dbm.table_name, ts - self.winddir_period, ts))
                winddir = r[0]
                r = dbm.getSql('SELECT AVG(barometer) FROM %s '
                               'WHERE dateTime >= %s AND dateTime <= %s' %
                               (dbm.table_name, ts - self.pressure_period, ts))
                pressure = r[0]
                r = dbm.getSql('SELECT MIN(dateTime),barometer FROM %s '
                               'WHERE dateTime >= %s AND dateTime <= %s' %
                               (dbm.table_name, ts - self.pressure_period, ts))
                first_p = r[1]
                r = dbm.getSql('SELECT MAX(dateTime),barometer FROM %s '
                               'WHERE dateTime >= %s AND dateTime <= %s' %
                               (dbm.table_name, ts - self.pressure_period, ts))
                last_p = r[1]
        except weedb.DatabaseError as e:
            loginf('%s: skipping forecast: %s' % (Z_KEY, e))
            return None

        logdbg('%s: units=%s winddir=%s pressure=%s first_p=%s last_p=%s'
               % (Z_KEY, units, winddir, pressure, first_p, last_p))

        # pressures need to be in mbar
        if units == weewx.US:
            if pressure is not None:
                vt = (float(pressure), "inHg", "group_pressure")
                pressure = weewx.units.convert(vt, 'mbar')[0]
            if first_p is not None:
                vt = (float(first_p), "inHg", "group_pressure")
                first_p = weewx.units.convert(vt, 'mbar')[0]
            if last_p is not None:
                vt = (float(last_p), "inHg", "group_pressure")
                last_p = weewx.units.convert(vt, 'mbar')[0]

        # for trend we need mbar per hour
        trend = None
        if first_p is not None and last_p is not None:
            trend = (last_p - first_p) * 3600 / self.pressure_period

        # for wind dir we need a value in [0-15]
        if winddir is not None:
            winddir = int(16 * winddir / 360.0)
            if winddir == 16:
                winddir = 0

        tt = time.gmtime(ts)
        month = tt.tm_mon - 1  # month is [0-11]
        north = self.hemisphere.lower() != 'south'
        logdbg('%s: pressure=%s month=%s winddir=%s trend=%s north=%s' %
               (Z_KEY, pressure, month, winddir, trend, north))
        code = ZambrettiCode(pressure, month, winddir, trend, north,
                             baro_bottom=self.lower_pressure,
                             baro_top=self.upper_pressure)
        logdbg('%s: code is %s' % (Z_KEY, code))
        if code is None:
            return None

        self.last_event_ts = ts
        record = {}
        record['method'] = Z_KEY
        record['usUnits'] = weewx.US
        record['dateTime'] = now
        record['issued_ts'] = now
        record['event_ts'] = ts
        record['zcode'] = code
        loginf('%s: generated 1 forecast record' % Z_KEY)
        return [record]

zambretti_label_dict = {
    'A': "Settled fine",
    'B': "Fine weather",
    'C': "Becoming fine",
    'D': "Fine, becoming less settled",
    'E': "Fine, possible showers",
    'F': "Fairly fine, improving",
    'G': "Fairly fine, possible showers early",
    'H': "Fairly fine, showery later",
    'I': "Showery early, improving",
    'J': "Changeable, mending",
    'K': "Fairly fine, showers likely",
    'L': "Rather unsettled clearing later",
    'M': "Unsettled, probably improving",
    'N': "Showery, bright intervals",
    'O': "Showery, becoming less settled",
    'P': "Changeable, some rain",
    'Q': "Unsettled, short fine intervals",
    'R': "Unsettled, rain later",
    'S': "Unsettled, some rain",
    'T': "Mostly very unsettled",
    'U': "Occasional rain, worsening",
    'V': "Rain at times, very unsettled",
    'W': "Rain at frequent intervals",
    'X': "Rain, very unsettled",
    'Y': "Stormy, may improve",
    'Z': "Stormy, much rain",
}

def ZambrettiText(code):
    return zambretti_label_dict[code]

def ZambrettiCode(pressure, month, wind, trend,
                  north=True, baro_top=1050.0, baro_bottom=950.0):
    """Simple implementation of Zambretti forecaster algorithm based on
    implementation in pywws, inspired by beteljuice.com Java algorithm,
    as converted to Python by honeysucklecottage.me.uk

    pressure - barometric pressure in millibars

    month - month of the year as number in [0,11]

    wind - wind direction as number in [0,15] or None

    trend - pressure change in millibars per hour
    """

    if pressure is None:
        return None
    if trend is None:
        return None
    if month < 0 or month > 11:
        return None
    if wind is not None and (wind < 0 or wind > 15):
        return None

    # normalise pressure
    pressure = 950.0 + ((1050.0 - 950.0) *
                        (pressure - baro_bottom) / (baro_top - baro_bottom))
    # adjust pressure for wind direction
    if wind is not None:
        if not north:
            # southern hemisphere, so add 180 degrees
            wind = (wind + 8) % 16
        pressure += (  5.2,  4.2,  3.2,  1.05, -1.1, -3.15, -5.2, -8.35,
                     -11.5, -9.4, -7.3, -5.25, -3.2, -1.15,  0.9,  3.05)[wind]
    # compute base forecast from pressure and trend (hPa / hour)
    if trend >= 0.1:
        # rising pressure
        if north == (month >= 4 and month <= 9):
            pressure += 3.2
        F = 0.1740 * (1031.40 - pressure)
        LUT = ('A','B','B','C','F','G','I','J','L','M','M','Q','T','Y')
    elif trend <= -0.1:
        # falling pressure
        if north == (month >= 4 and month <= 9):
            pressure -= 3.2
        F = 0.1553 * (1029.95 - pressure)
        LUT = ('B','D','H','O','R','U','V','X','X','Z')
    else:
        # steady
        F = 0.2314 * (1030.81 - pressure)
        LUT = ('A','B','B','B','E','K','N','N','P','P','S','W','W','X','X','X','Z')
    # clip to range of lookup table
    F = min(max(int(F + 0.5), 0), len(LUT) - 1)
    # convert to letter code
    return LUT[F]


# -----------------------------------------------------------------------------
# US National Weather Service Point Forecast Matrix
#
# For an explanation of point forecasts, see:
#   http://www.srh.weather.gov/jetstream/webweather/pinpoint_max.htm
#
# For details about how to decode the NWS point forecast matrix, see:
#   http://www.srh.noaa.gov/mrx/?n=pfm_explain
#   http://www.srh.noaa.gov/bmx/?n=pfm
# For details about the NWS area forecast matrix, see:
#   http://www.erh.noaa.gov/car/afmexplain.htm
#
# For actual forecasts, see:
#   http://www.weather.gov/
#
# For example:
#   http://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt&issuedby=BOX
#
# 12-hour:
# pop12hr: likelihood of measurable precipitation (1/100 inch)
# qpf12hr: quantitative precipitation forecast; amount or range in inches
# snow12hr: snowfall accumulation; amount or range in inches; T indicates trace
# mx/mn: temperature in degrees F
#
# 3-hour:
# temp - degrees F
# dewpt - degrees F
# rh - relative humidity %
# winddir - 8 compass points
# windspd - miles per hour
# windchar - wind character
# windgust - only displayed if gusts exceed windspd by 10 mph
# clouds - sky coverage
# precipitation types
#   rain      - rain
#   rainshwrs - rain showers
#   sprinkles - sprinkles
#   tstms     - thunderstorms
#   drizzle   - drizzle
#   snow      - snow, snow grains/pellets
#   snowshwrs - snow showers
#   flurries  - snow flurries
#   sleet     - ice pellets
#   frzngrain - freezing rain
#   frzngdrzl - freezing drizzle
# windchill
# heatindex
# minchill
# maxheat
# obvis - obstructions to visibility
#
# codes for clouds:
#   CL - clear (0 <= 6%)
#   FW - few - mostly clear (6% <= 31%)
#   SC - scattered - partly cloudy (31% <= 69%)
#   BK - broken - mostly cloudy (69% <= 94%)
#   OV - overcast - cloudy (94% <= 100%)
#
#   CL - sunny or clear (0% <= x <= 5%)
#   FW - sunny or mostly clear (5% < x <= 25%)
#   SC - mostly sunny or partly cloudy (25% < x <= 50%)
#   B1 - partly sunny or mostly cloudy (50% < x <= 69%)
#   B2 - mostly cloudy or considerable cloudiness (69% < x <= 87%)
#   OV - cloudy or overcast (87% < x <= 100%)
#
# PFM/AFM codes for precipitation types (rain, drizzle, flurries, etc):
#   S - slight chance (< 20%)
#   C - chance (30%-50%)
#   L - likely (60%-70%)
#   O - occasional (80%-100%)
#   D - definite (80%-100%)
#
#   IS - isolated < 20%
#   SC - scattered 30%-50%
#   NM - numerous 60%-70%
#   EC - extensive coverage 80%-100%
#
#   PA - patchy < 25%
#   AR - areas 25%-50%
#   WD - widespread > 50%
#
# codes for obstructions to visibility:
#   F   - fog
#   PF  - patchy fog
#   F+  - dense fog
#   PF+ - patchy dense fog
#   H   - haze
#   BS  - blowing snow
#   K   - smoke
#   BD  - blowing dust
#   AF  - volcanic ashfall
#
# codes for wind character:
#   LT - light < 8 mph
#   GN - gentle 8-14 mph
#   BZ - breezy 15-22 mph
#   WY - windy 23-30 mph
#   VW - very windy 31-39 mph
#   SD - strong/damaging >= 40 mph
#   HF - hurricane force >= 74 mph
#
# -----------------------------------------------------------------------------

# sample URL pre-v3
# http://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt&issuedby=BOX
# sample v3 URL
# https://forecast-v3.weather.gov/products/types/PFM/BOX/1?format=text

# The default URL contains the bare minimum to request a point forecast, less
# the forecast office identifier.
NWS_DEFAULT_PFM_URL = 'http://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt'
NWS_DEFAULT_PFM_URL_v3 = 'https://forecast-v3.weather.gov/products/types/PFM/%s/1?format=text'

NWS_KEY = 'NWS'

class NWSForecast(Forecast):
    """Download forecast from US National Weather Service."""

    def __init__(self, engine, config_dict):
        super(NWSForecast, self).__init__(engine, config_dict, NWS_KEY,
                                          interval=10800)
        d = config_dict.get('Forecast', {}).get(NWS_KEY, {})
        self.url = d.get('url', NWS_DEFAULT_PFM_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.lid = d.get('lid', None)
        self.foid = d.get('foid', None)

        errmsg = []
        if self.lid is None or self.lid.startswith('INSERT_'):
            errmsg.append('location ID (lid) is not specified')
        if self.foid is None or self.foid.startswith('INSERT_'):
            errmsg.append('forecast office ID (foid) is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (NWS_KEY, e))
            logerr('%s: forecast will not be run' % NWS_KEY)
            return

        loginf('%s: interval=%s max_age=%s lid=%s foid=%s' %
               (NWS_KEY, self.interval, self.max_age, self.lid, self.foid))
        self._bind()

    def get_forecast(self, dummy_event):
        text = NWSDownloadForecast(self.foid, url=self.url,
                                   max_tries=self.max_tries)
        if text is None:
            logerr('%s: no PFM data for %s from %s' %
                   (NWS_KEY, self.foid, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='nws-raw')
        matrix = NWSParseForecast(text, self.lid)
        if matrix is None:
            logerr('%s: no PFM found for %s in forecast from %s' %
                   (NWS_KEY, self.lid, self.foid))
            return None
        logdbg('%s: forecast matrix: %s' % (NWS_KEY, matrix))
        records = NWSProcessForecast(self.foid, self.lid, matrix)
        if len(records) == 0 and self.save_failed:
            self.save_failed_forecast(text, basename='nws-fail')
        msg = 'got %d forecast records' % len(records)
        if 'desc' in matrix or 'location' in matrix:
            msg += ' for %s %s' % (matrix.get('desc', ''),
                                   matrix.get('location', ''))
        loginf('%s: %s' % (NWS_KEY, msg))
        return records

# mapping of NWS names to database fields
nws_schema_dict = {
    'HOUR'      : 'hour',
    'MIN/MAX'   : 'tempMinMax',
    'MAX/MIN'   : 'tempMaxMin',
    'TEMP'      : 'temp',
    'DEWPT'     : 'dewpoint',
    'RH'        : 'humidity',
    'WIND DIR'  : 'windDir',
    'PWIND DIR' : 'windDir',
    'WIND SPD'  : 'windSpeed',
    'WIND GUST' : 'windGust',
    'WIND CHAR' : 'windChar',
    'CLOUDS'    : 'clouds',
    'AVG CLOUDS': 'clouds',
    'POP 12HR'  : 'pop',
    'QPF 12HR'  : 'qpf',
    'SNOW 12HR' : 'qsf',
    'RAIN'      : 'rain',
    'RAIN SHWRS': 'rainshwrs',
    'TSTMS'     : 'tstms',
    'DRIZZLE'   : 'drizzle',
    'SNOW'      : 'snow',
    'SNOWSHWRS' : 'snowshwrs', # official docs indicate no space
    'SNOW SHWRS': 'snowshwrs', # but space shows up in some cases
    'FLURRIES'  : 'flurries',
    'SLEET'     : 'sleet',
    'FRZNG RAIN': 'frzngrain',
    'FRZG RAIN' : 'frzngrain', # this was witnessed in report NDZ043-132200
    'FRZNG DRZL': 'frzngdrzl',
    'OBVIS'     : 'obvis',
    'WIND CHILL': 'windChill',
    'HEAT INDEX': 'heatIndex',
}

def NWSDownloadForecast(foid, url=NWS_DEFAULT_PFM_URL, max_tries=3):
    """Download a point forecast matrix from the US National Weather Service"""

    u = url
    if url == NWS_DEFAULT_PFM_URL:
        u = '%s&issuedby=%s' % (url, foid)
    elif url == NWS_DEFAULT_PFM_URL_v3:
        u = url % foid
    loginf("%s: downloading forecast from '%s'" % (NWS_KEY, u))
    for count in range(max_tries):
        try:
            response = six.moves.urllib.request.urlopen(u)
            text = response.read()
            return text.decode('utf-8')
        except (six.moves.urllib.error.URLError, socket.error,
                six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
            logerr('%s: failed attempt %d to download NWS forecast: %s' %
                   (NWS_KEY, count + 1, e))
    else:
        logerr('%s: failed to download forecast' % NWS_KEY)
    return None

def NWSExtractLocation(text, lid):
    """Extract a single location from a US National Weather Service PFM."""

    alllines = text.splitlines()
    lines = None
    for line in iter(alllines):
        if line.startswith(lid):
            lines = []
            lines.append(line)
        elif lines is not None:
            if line.startswith('$$'):
                break
            else:
                lines.append(line)
    return lines

def NWSParseForecast(text, lid):
    """Parse a United States National Weather Service point forcast matrix.
    Save it into a dictionary with per-hour elements for wind, temperature,
    etc. extracted from the point forecast.
    """

    lines = NWSExtractLocation(text, lid)
    if lines is None:
        return None

    rows3 = {}
    rows6 = {}
    ts = None
    mode = None

    for line in lines:
        if ts is None and len(line.split(' ')) == 7:
            ts = date2ts(line)
            continue
        label = line[0:14].strip().upper()
        if label.startswith('UTC'):
            continue
        prefix = ' ' # pad with a leading space to deal with possible negatives
        if label.endswith('3HRLY'):
            label = 'HOUR'
            mode = 3
        elif label.endswith('6HRLY'):
            label = 'HOUR'
            mode = 6
        elif label.endswith('-'):
            label = label[:-1].strip()
            prefix = '-'
        if label in nws_schema_dict:
            row = "%s%s" % (prefix, line[14:])
            if mode == 3:
                rows3[nws_schema_dict[label]] = row
            elif mode == 6:
                rows6[nws_schema_dict[label]] = row
            else:
                loginf("%s: mode unset for label '%s'" % (NWS_KEY, label))
        else:
            logdbg("%s: ignore label '%s'" % (NWS_KEY, label))

    if ts is None:
        loginf("%s: no time string found for %s" % (NWS_KEY, lid))
        return None
    day_ts = weeutil.weeutil.startOfDay(ts)

    matrix = {}
    matrix['lid'] = lid
    matrix['desc'] = lines[1]
    matrix['location'] = lines[2]
    matrix['issued_ts'] = ts
    matrix['ts'] = []
    matrix['hour'] = []
    matrix['duration'] = []

    idx = 0
    day = day_ts
    lasth = None

    # get the 3-hour indexing
    indices3 = {} # index in the hour string mapped to index of the hour
    idx2hr3 = []  # index of the hour mapped to location in the hour string
    for i in range(1, len(rows3['hour']), 3):
        h = int(rows3['hour'][i:i + 2])
        if lasth is not None and h < lasth:
            day += 24 * 3600
        lasth = h
        matrix['ts'].append(day + h * 3600)
        matrix['hour'].append(h)
        matrix['duration'].append(3 * 3600)
        indices3[i + 1] = idx
        idx += 1
        idx2hr3.append(i + 1)

    # get the 6-hour indexing
    indices6 = {} # index in the hour string mapped to index of the hour
    idx2hr6 = []  # index of the hour mapped to location in the hour string
    s = ''
    for i in range(0, len(rows6['hour'])):
        if rows6['hour'][i].isspace():
            if len(s) > 0:
                h = int(s)
                if lasth is not None and h < lasth:
                    day += 24 * 3600
                lasth = h
                matrix['ts'].append(day + h * 3600)
                matrix['hour'].append(h)
                matrix['duration'].append(6 * 3600)
                indices6[i - 1] = idx
                idx += 1
                idx2hr6.append(i - 1)
            s = ''
        else:
            s += rows6['hour'][i]
    if len(s) > 0:
        h = int(s)
        matrix['ts'].append(day + h * 3600)
        matrix['hour'].append(h)
        matrix['duration'].append(3 * 3600)
        indices6[len(rows6['hour']) - 1] = idx
        idx += 1
        idx2hr6.append(len(rows6['hour']) - 1)

    # get the 3 and 6 hour data
    filldata(matrix, idx, rows3, indices3, idx2hr3)
    filldata(matrix, idx, rows6, indices6, idx2hr6)
    return matrix

def filldata(matrix, nidx, rows, indices, i2h):
    """fill matrix with data from rows"""
    n = {'qpf': 8, 'qsf': 5} # field widths
    for label in rows:
        if label not in matrix:
            matrix[label] = [None] * nidx
        l = n.get(label, 3) # default to field width of 3
        q = 0
        for i in reversed(i2h):
            if l == 3 or q % 4 == 0:
                s = 0 if i - l + 1 < 0 else i - l + 1
                chunk = rows[label][s:i + 1].strip()
                if len(chunk) > 0 and chunk != 'MM':
                    matrix[label][indices[i]] = chunk
            q += 1

    # deal with min/max temperatures
    if 'tempMin' not in matrix:
        matrix['tempMin'] = [None] * nidx
    if 'tempMax' not in matrix:
        matrix['tempMax'] = [None] * nidx
    if 'tempMinMax' in matrix:
        state = 0
        for i in range(nidx):
            if matrix['tempMinMax'][i] is not None:
                if state == 0:
                    matrix['tempMin'][i] = matrix['tempMinMax'][i]
                    state = 1
                else:
                    matrix['tempMax'][i] = matrix['tempMinMax'][i]
                    state = 0
        del matrix['tempMinMax']
    if 'tempMaxMin' in matrix:
        state = 1
        for i in range(nidx):
            if matrix['tempMaxMin'][i] is not None:
                if state == 0:
                    matrix['tempMin'][i] = matrix['tempMaxMin'][i]
                    state = 1
                else:
                    matrix['tempMax'][i] = matrix['tempMaxMin'][i]
                    state = 0
        del matrix['tempMaxMin']

def date2ts(tstr):
    """Convert NWS date string to timestamp in seconds.
    sample format: 418 PM EDT SAT MAY 11 2013
    """

    parts = tstr.split(' ')
    s = '%s %s %s %s %s' % (parts[0], parts[1], parts[4], parts[5], parts[6])
    ts = time.mktime(time.strptime(s, "%I%M %p %b %d %Y"))
    return int(ts)

def NWSProcessForecast(foid, lid, matrix):
    """convert NWS matrix to records"""
    now = int(time.time())
    records = []
    if matrix is not None:
        for i, ts in enumerate(matrix['ts']):
            record = {}
            record['method'] = NWS_KEY
            record['usUnits'] = weewx.US
            record['dateTime'] = now
            record['issued_ts'] = matrix['issued_ts']
            record['event_ts'] = ts
            record['location'] = '%s %s' % (foid, lid)
            for label in matrix:
                if isinstance(matrix[label], list):
                    record[label] = matrix[label][i]
            records.append(record)
    return records


# -----------------------------------------------------------------------------
# Dark Sky Forecasts
#
# Forecasts from Dark Sky (www.darksky.net). Dark Sky provides an api that
# returns json data.
#
# For the Dark SKy api, see:
#   https://darksky.net/dev/docs
#
# There are three Dark Sky forecasts:
#   minutely - minute-by-minute out to one hour
#   hourly - hour-by-hour out to seven days (default two days)
#   daily - day-by-day out to seven days
#
# Only hourly and daily forecasts are supported by this class.
#
# Each forecast (known as a data block) consists of a number of data point
# objects with each data point object consisting of a number of data fields.
# The Dark Sky API documentation indicates all fields are optional though some
# fields are annotated as only available in certain data blocks.
#
# hourly -----------------------------------------------------------------
#
# apparentTemperature
# cloudCover
# dewPoint
# humidity
# icon
# ozone
# precipAccumulation
# precipIntensity
# precipIntensityError
# precipProbability
# precipType
# pressure
# summary
# temperature
# time
# uvIndex
# visibility
# windBearing
# windGust
# windSpeed
#
# daily -----------------------------------------------------------------------
#
# apparentTemperatureHigh
# apparentTemperatureHighTime
# apparentTemperatureLow
# apparentTemperatureLowTime
# cloudCover
# dewPoint
# humidity
# icon
# moonPhase
# ozone
# precipAccumulation
# precipIntensity
# precipIntensityError
# precipIntensityMax
# precipIntensityMaxTime
# precipProbability
# precipType
# pressure
# summary
# sunriseTime
# sunsetTime
# temperature
# temperatureHigh
# temperatureHighTime
# temperatureLow
# temperatureLowTime
# time
# uvIndex
# uvIndexTime
# visibility
# windBearing
# windGust
# windGustTime
# windSpeed
# -----------------------------------------------------------------------------

DS_KEY = 'DS'
DS_DEFAULT_URL = 'https://api.darksky.net/forecast'
DS_BLOCKS = ['currently', 'minutely', 'hourly', 'daily', 'alerts', 'flags']


class DSForecast(Forecast):

    def __init__(self, engine, config_dict):
        super(DSForecast, self).__init__(engine, config_dict, DS_KEY,
                                         interval=10800)
        d = config_dict.get('Forecast', {}).get(DS_KEY, {})
        self.url = d.get('url', DS_DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.api_key = d.get('api_key', None)
        self.location = d.get('location', None)
        self.forecast_type = d.get('forecast_type', 'daily')
        _extend = d.get('extend_hourly', False)
        # extend only applies if the hourly forecast is being used
        self.extend = _extend if self.forecast_type == 'hourly' else False
        self.language = d.get('language', 'en')
        self.use_compression = weeutil.weeutil.tobool(d.get('use_compression',
                                                            True))

        if self.location is None:
            self.location = Forecast.get_loc_from_station(config_dict)

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.api_key is None or self.api_key.startswith('INSERT_'):
            errmsg.append('API key (api_key) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (DS_KEY, e))
            logerr('%s: forecast will not be run' % DS_KEY)
            return

        loginf('%s: interval=%s max_age=%s api_key=%s location=%s fc=%s' %
               (DS_KEY, self.interval, self.max_age,
                self.obfuscate(self.api_key), self.location,
                self.forecast_type))
        self._bind()

    def get_forecast(self, dummy_event):
        """Return a parsed forecast."""

        text = self.download(api_key=self.api_key, location=self.location,
                             url=self.url, fc_type=self.forecast_type,
                             extend=self.extend, language=self.language,
                             compression=self.use_compression)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (DS_KEY, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='ds-raw')
        records, msgs = self.parse(text, fc_type=self.forecast_type,
                                   location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='ds-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (DS_KEY, len(records)))
        return records

    @staticmethod
    def download(api_key, location, url=DS_DEFAULT_URL, fc_type='daily',
                 extend=False, language='en', compression=True, units='us',
                 max_tries=3):
        """Download a forecast from the Dark Sky

        api_key - key for downloading

        location - location for which the forecast is required. string in the
                   format lat,lon.

        url - URL to the forecast service.  if anything other than the
              default is specified, that entire URL is used.  if the default
              is specified, it is used as the base and other items are added
              to it.

        fc_type - forecast type, one of hourly or daily

        extend - if using the hourly forecast extend the forecast to 7 days
                 from the default 2 days.

        language - forecast language. must be one of the Dark Sky language
                   codes.

        compression - whether to use gzip compression in the request header.
                      Dark Sky rcommends using compression for extended hourly
                      forecast.

        units - units to be used in the forecast. must be one of the Dark Sky
                units codes but this method requires 'us'.

        max_tries - how many times to try before giving up
        """

        if url == DS_DEFAULT_URL:
            # construct the basic URL for the API call
            u = '/'.join([url, api_key, location])
            # build the optional parameters string, first get the exclude string
            exclude = ','.join([x for x in DS_BLOCKS if x != fc_type])
            # now build the optional string
            optional_str = DSForecast._build_optional(exclude=exclude,
                                                      extend=extend,
                                                      language=language,
                                                      units=units)
            # construct the final URL including optional parameters
            u = '?'.join([u, optional_str]) if len(optional_str) > 0 else u
        else:
            u = url
        request = six.moves.urllib.request.Request(u)
        if compression:
            request.add_header('Accept-Encoding', 'gzip')
        masked = Forecast.get_masked_url(u, api_key)
        loginf("%s: downloading forecast from '%s'" % (DS_KEY, masked))
        for count in range(max_tries):
            try:
                response = six.moves.urllib.request.urlopen(request)
                if response.info().get('Content-Encoding') == 'gzip':
                    buf = BytesIO(response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    text = f.read()
                else:
                    text = response.read()
                return text.decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (DS_KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % DS_KEY)
        return None

    @staticmethod
    def _build_optional(exclude=None, extend=False, language='en', units='auto'):
        """Build the optional parameters string."""

        # initialise a list of non-None optional parameters and their values
        opt_params_list = []
        # exclude
        if exclude is not None:
            opt_params_list.append('exclude=%s' % exclude)
        # extend
        if extend:
            opt_params_list.append('extend=hourly')
        # language
        if language is not None:
            opt_params_list.append('lang=%s' % language)
        # units
        if units is not None:
            opt_params_list.append('units=%s' % units)
        # now if we have any parameters concatenate them separating each with
        # an ampersand
        opt_params = "&".join(opt_params_list)
        # return the resulting string
        return opt_params

    @staticmethod
    def parse(text, issued_ts=None, now=None, fc_type='daily', location=None):
        """Parse a raw forecast."""

        obj = json.loads(text)
        if fc_type not in obj:
            msg = "%s: no '%s' forecast in json object" % (DS_KEY, fc_type)
            logerr(msg)
            return [], [msg]
        fc = obj[fc_type]

        if issued_ts is None or now is None:
            n = int(time.time())
            if issued_ts is None:
                issued_ts = n
            if now is None:
                now = n

        records = []
        msgs = []
        if fc_type == 'hourly':
            records, msgs = DSForecast.create_records_from_hourly(fc,
                                                                  issued_ts,
                                                                  now,
                                                                  location=location)
        elif fc_type == 'daily':
            records, msgs = DSForecast.create_records_from_daily(fc,
                                                                 issued_ts,
                                                                 now,
                                                                 location=location)
        else:
            msg = "%s: cannot find 'hourly' or 'daily' forecast" % DS_KEY
            logerr(msg)
            msgs.append(msg)
        return records, msgs

    @staticmethod
    def create_records_from_daily(fc, issued_ts, now, location=None):
        """create from daily forecast data"""

        msgs = []
        records = []
        cnt = 0
        for period in fc['data']:
            try:
                cnt += 1
                r = {}
                r['method'] = DS_KEY
                r['usUnits'] = weewx.US
                r['dateTime'] = now
                r['issued_ts'] = issued_ts
                r['event_ts'] = Forecast.str2int('epoch',
                                                 period['time'],
                                                 DS_KEY)
                _dt = datetime.datetime.fromtimestamp(int(period['time']))
                r['hour'] = _dt.hour
                r['duration'] = 24 * 3600
                r['clouds'] = Forecast.pct2clouds(100 * float(period['cloudCover']))
                r['tempMin'] = Forecast.str2float('temperatureLow',
                                                  period['temperatureLow'],
                                                  DS_KEY)
                r['tempMax'] = Forecast.str2float('temperatureHigh',
                                                  period['temperatureHigh'],
                                                  DS_KEY)
                # It appears that dark sky does not include `temperature` in
                # daily forecasts. Use 'temperature' if available otherwise
                # fallback to the average of the high/low.
                if 'temperature' in period:
                    r['temp'] = Forecast.str2float('temperature',
                                                   period['temperature'],
                                                   DS_KEY)
                else:
                    r['temp'] = (r['tempMin'] + r['tempMax']) / 2
                r['dewpoint'] = Forecast.str2float('dewPoint',
                                                   period['dewPoint'],
                                                   DS_KEY)
                _humidity = Forecast.str2float('humidity',
                                               period['humidity'],
                                               DS_KEY)
                r['humidity'] = int(_humidity * 100) if _humidity is not None else None
                _pop = Forecast.str2float('precipProbability',
                                          period['precipProbability'],
                                          DS_KEY)
                r['pop'] = int(_pop * 100) if _pop is not None else None
                # Dark Sky provides snowfall in cm in optional precipAccumulation field
                if 'precipAccumulation' in period:
                    _qsf = Forecast.str2float('precipAccumulation',
                                              period['precipAccumulation'],
                                              DS_KEY)
                    r['qsf'] = _qsf / 2.54 if _qsf is not None else None
                r['windSpeed'] = Forecast.str2float('windSpeed',
                                                    period['windSpeed'],
                                                    DS_KEY)
                if 'windBearing' in period:
                    r['windDir'] = Forecast.deg2dir(period['windBearing'])
                r['windGust'] = Forecast.str2float('windGust',
                                                   period['windGust'],
                                                   DS_KEY)
                if 'uvIndex' in period:
                    r['uvIndex'] = Forecast.str2int('uvIndex',
                                                    period['uvIndex'],
                                                    DS_KEY)
                if location is not None:
                    r['location'] = location
                records.append(r)
            except KeyError as e:
                msg = '%s: failure in daily forecast period %d: %s' % (
                    DS_KEY, cnt, e)
                msgs.append(msg)
                logerr(msg)
        return records, msgs

    @staticmethod
    def create_records_from_hourly(fc, issued_ts, now, location=None):
        """create from hourly forecast"""

        msgs = []
        records = []
        cnt = 0
        for period in fc['data']:
            try:
                cnt += 1
                r = {}
                r['method'] = DS_KEY
                r['usUnits'] = weewx.US
                r['dateTime'] = now
                r['issued_ts'] = issued_ts
                r['event_ts'] = Forecast.str2int('epoch',
                                                 period['time'],
                                                 DS_KEY)
                _dt = datetime.datetime.fromtimestamp(int(period['time']))
                r['hour'] = _dt.hour
                r['duration'] = 3600
                r['clouds'] = Forecast.pct2clouds(100 * float(period['cloudCover']))
                r['temp'] = Forecast.str2float('temperature',
                                               period['temperature'],
                                               DS_KEY)
                r['dewpoint'] = Forecast.str2float('dewPoint',
                                                   period['dewPoint'],
                                                   DS_KEY)
                _humidity = Forecast.str2float('humidity',
                                               period['humidity'],
                                               DS_KEY)
                r['humidity'] = int(_humidity * 100) if _humidity is not None else None
                r['windSpeed'] = Forecast.str2float('windSpeed',
                                                    period['windSpeed'],
                                                    DS_KEY)
                if 'windBearing' in period:
                    r['windDir'] = Forecast.deg2dir(period['windBearing'])
                r['windGust'] = Forecast.str2float('windGust',
                                                   period['windGust'],
                                                   DS_KEY)
                _pop = Forecast.str2float('precipProbability',
                                          period['precipProbability'],
                                          DS_KEY)
                r['pop'] = int(_pop * 100) if _pop is not None else None
                # Dark Sky provides snowfall in cm in optional precipAccumulation field
                if 'precipAccumulation' in period:
                    _qsf = Forecast.str2float('precipAccumulation',
                                              period['precipAccumulation'],
                                              DS_KEY)
                    r['qsf'] = _qsf / 2.54 if _qsf is not None else None
                if 'uvIndex' in period:
                    r['uvIndex'] = Forecast.str2int('uvIndex',
                                                    period['uvIndex'],
                                                    DS_KEY)
                if location is not None:
                    r['location'] = location
                records.append(r)
            except KeyError as e:
                msg = '%s: failure in hourly forecast period %d: %s' % (
                    DS_KEY, cnt, e)
                msgs.append(msg)
                logerr(msg)
        return records, msgs


# -----------------------------------------------------------------------------
# Weather Underground Forecasts
#
# Forecasts from the weather underground (www.wunderground.com).  WU provides
# an api that returns json/xml data.  This implementation uses the json format.
#
# For the weather underground api, see:
#   https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/
#
# WU provides a 5-day daily forecast
#
# -----------------------------------------------------------------------------

WU_KEY = 'WU'
WU_DEFAULT_URL = 'https://api.weather.com/'

class WUForecast(Forecast):

    def __init__(self, engine, config_dict):
        super(WUForecast, self).__init__(engine, config_dict, WU_KEY,
                                         interval=10800)
        d = config_dict.get('Forecast', {}).get(WU_KEY, {})
        self.url = d.get('url', WU_DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.api_key = d.get('api_key', None)
        # geocode   - "33.74,-84.39"
        # iataCode  - DEN
        # icaoCode  - KDEN
        # placeid   - 327145917e06d09373dd2760425a88622a62d248fd97550eb4883737d8d1173b
        # postalKey - 81657
        geocode = d.get('geocode', None)
        iataCode = d.get('iataCode', None)
        icaoCode = d.get('icaoCode', None)
        placeid = d.get('placeid', None)
        postalKey = d.get('postalKey', None)

        if geocode is None and iataCode is None and icaoCode is None and placeid is None and postalKey is None:
            geocode = Forecast.get_loc_from_station(config_dict)

        if geocode is not None:
            self.location = 'geocode=%s' % geocode
        elif iataCode is not None:
            self.location = 'iataCode=%s' % iataCode
        elif icaoCode is not None:
            self.location = 'icaoCode=%s' % icaoCode
        elif placeid is not None:
            self.location = 'placeid=%s' % placeid
        elif postalKey is not None:
            self.location = 'postalKey=%s' % postalKey

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.api_key is None or self.api_key.startswith('INSERT_'):
            errmsg.append('API key (api_key) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (WU_KEY, e))
            logerr('%s: forecast will not be run' % WU_KEY)
            return

        loginf('%s: interval=%s max_age=%s api_key=%s %s' %
               (WU_KEY, self.interval, self.max_age,
                self.obfuscate(self.api_key), self.location))
        self._bind()

    def get_forecast(self, dummy_event):
        text = self.download(self.api_key, self.location, url=self.url,
                             max_tries=self.max_tries)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (WU_KEY, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='wu-raw')
        records, msgs = self.parse(text, location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='wu-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (WU_KEY, len(records)))
        return records

    @staticmethod
    def download(api_key, location, url=WU_DEFAULT_URL, max_tries=3):
        """Download a forecast from the Weather Underground

        api_key - key for downloading

        location - lat/lon

        url - URL to the forecast service.  if anything other than the
              default is specified, that entire URL is used.  if the default
              is specified, it is used as the base and other items are added
              to it.

        max_tries - how many times to try before giving up
        """

        u = '%s/v3/wx/forecast/daily/5day?%s&format=json&units=e&language=en-US&apiKey=%s' % (url, location, api_key) \
            if url == WU_DEFAULT_URL else url
        masked = Forecast.get_masked_url(u, api_key)
        loginf("%s: download forecast from '%s'" % (WU_KEY, masked))
        for count in range(max_tries):
            try:
                response = six.moves.urllib.request.urlopen(u)
                text = response.read()
                return text.decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (WU_KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % WU_KEY)
        return None

    @staticmethod
    def parse(text, issued_ts=None, now=None, location=None):
        response = json.loads(text)
        if not 'validTimeUtc' in response:
            msg = "%s: no 'validTimeUtc' in json object" % WU_KEY
            logerr(msg)
            return [], [msg]

        if issued_ts is None or now is None:
            n = int(time.time())
            if issued_ts is None:
                issued_ts = n
            if now is None:
                now = n

        records = []
        msgs = []
        records, msgs = WUForecast.create_records_from_five_day(
           response, issued_ts, now, location=location)
        return records, msgs

    @staticmethod
    def create_records_from_five_day(fc, issued_ts, now, location=None):
        msgs = []
        records = []
        day_index = 0
        for seven_am_date in fc['validTimeUtc']:
            try:
                event_ts = Forecast.str2int('epoch', seven_am_date, WU_KEY)
                for half_day_index in range(2):
                    daypart_index = day_index * 2
                    hour = 7
                    if half_day_index == 1:
                        # Add 12 hours
                        event_ts += 12 * 3600
                        hour += 12
                        daypart_index += 1
                    if fc['daypart'][0]['daypartName'][daypart_index] is not None:
                        r = {}
                        r['method'] = WU_KEY
                        r['usUnits'] = weewx.US
                        r['dateTime'] = now
                        r['issued_ts'] = issued_ts
                        r['event_ts'] = event_ts
                        r['hour'] = hour
                        r['duration'] = 12 * 3600
                        # Clouds
                        cloud_cover_pct = fc['daypart'][0]['cloudCover'][daypart_index]
                        if cloud_cover_pct == 0:
                            r['clouds'] = 'CL'
                        elif cloud_cover_pct < 25:
                            r['clouds'] = 'FW'
                        elif cloud_cover_pct < 50:
                            r['clouds'] = 'SC'
                        elif cloud_cover_pct == 50:
                            r['clouds'] = 'BK'
                        elif cloud_cover_pct < 75:
                            r['clouds'] = 'B1'
                        else:
                            r['clouds'] = 'OV'
                        # Precip
                        precip_type = fc['daypart'][0]['precipType'][daypart_index]
                        precip_chance = fc['daypart'][0]['precipChance'][daypart_index]
                        if precip_chance > 20 and (precip_type == 'rain' or precip_type == 'snow'):
                            r[precip_type] = WUForecast.code_from_precip_chance(precip_chance)
                        # ThunderStorms
                        thunder_index = fc['daypart'][0]['thunderIndex'][daypart_index]
                        if thunder_index > 0:
                            r['tstms'] = WUForecast.tstms_dict[thunder_index]
                        # Look for other precip in iconCode
                        icon_code = fc['daypart'][0]['iconCode'][daypart_index]
                        #if icon_code == 4 or icon_code == 37 or icon_code == 38 or icon_code == 47:
                        #    if precip_chance > 20:
                        #        r['tstms'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 4 or icon_code == 17 or icon_code == 35:
                            if precip_chance > 20:
                                r['hail'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 9:
                            if precip_chance > 20:
                                r['drizzle'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 6 or icon_code == 7 or icon_code == 18:
                            if precip_chance > 20:
                                r['sleet'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 8:
                            if precip_chance > 20:
                                r['frzngdrzl'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 10:
                            if precip_chance > 20:
                                r['frzngrain'] = WUForecast.code_from_precip_chance(precip_chance)
                        if icon_code == 13:
                            if precip_chance > 20:
                                r['flurries'] = WUForecast.code_from_precip_chance(precip_chance)
                        r['tempMax'] = Forecast.str2float(
                            'temperatureMax', fc['temperatureMax'][day_index], WU_KEY)
                        r['tempMin'] = Forecast.str2float(
                            'temperatureMin', fc['temperatureMin'][day_index], WU_KEY)
                        r['temp'] = fc['daypart'][0]['temperature'][daypart_index]
                        r['humidity'] = Forecast.str2int(
                            'relativeHumidity', fc['daypart'][0]['relativeHumidity'][daypart_index], WU_KEY)
                        r['pop'] = Forecast.str2int(
                            'precipChance', fc['daypart'][0]['precipChance'][daypart_index], WU_KEY)
                        r['qpf'] = Forecast.str2float(
                            'qpf', fc['daypart'][0]['qpf'][daypart_index], WU_KEY)
                        r['qsf'] = Forecast.str2float(
                            'qsfSnow', fc['daypart'][0]['qpfSnow'][daypart_index], WU_KEY)
                        r['windSpeed'] = Forecast.str2float(
                            'windSpeed', fc['daypart'][0]['windSpeed'][daypart_index], WU_KEY)
                        r['windDir'] = fc['daypart'][0]['windDirectionCardinal'][daypart_index]
                        r['heatIndex'] = Forecast.str2float(
                            'temperatureHeatIndex', fc['daypart'][0]['temperatureHeatIndex'][daypart_index], WU_KEY)
                        r['windChill'] = Forecast.str2float(
                            'temperatureWindChill', fc['daypart'][0]['temperatureWindChill'][daypart_index], WU_KEY)
                        r['uvIndex'] = Forecast.str2float(
                            'uvIndex', fc['daypart'][0]['uvIndex'][daypart_index], WU_KEY)
                        if location is not None:
                            r['location'] = location
                        records.append(r)
                day_index += 1
            except KeyError as e:
                weeutil.logger.log_traceback(log.error, "    ****  ")
                try:
                    msg = '%s: failure in forecast period, day_index: %d, half_day_index: %d:  %s' % (
                        WU_KEY, day_index, half_day_index if half_day_index is not None else -1, e)
                    msgs.append(msg)
                    logerr(msg)
                except Exception as e1:
                    logerr('KeyError: %s' % e1)
            except Exception as e:
                weeutil.logger.log_traceback(log.error, "    ****  ")
                try:
                    msg = 'create_records_from_five_day: %s: failure in forecast period, day_index: %d, half_day_index: %d:  %s' % (
                        WU_KEY, day_index, half_day_index if half_day_index is not None else -1, e)
                    msgs.append(msg)
                    logerr(msg)
                except Exception as e1:
                    logerr('Exception: %s' % e1)

        return records, msgs

    tstms_dict = {
        0: None,
        1: 'S',
        2: 'C',
        3: 'L',
        4: 'O',
        5: 'D'}

    str2precip_dict = {
        # nws precip strings
        'Rain': 'rain',
        'Rain Showers': 'rainshwrs',
        'Thunderstorms': 'tstms',
        'Drizzle': 'drizzle',
        'Snow': 'snow',
        'Snow Showers': 'snowshwrs',
        'Flurries': 'flurries',
        'Sleet': 'sleet',
        'Freezing Rain': 'frzngrain',
        'Freezing Drizzle': 'frzngdrzl',
        # precip strings supported by wu but not nws
        'Snow Grains': 'snow',
        'Ice Crystals': 'sleet',
        'Hail': 'hail',
        'Thunderstorm': 'tstms',
        'Rain Mist': 'rain',
        'Ice Pellets': 'sleet',
        'Ice Pellet Showers': 'sleet',
        'Hail Showers': 'hail',
        'Small Hail': 'hail',
        'Small Hail Showers': 'hail',
    }

    str2obvis_dict = {
        # nws obvis strings
        'Fog': 'F',
        'Patchy Fog': 'PF',
        'Dense Fog': 'F+',
        'Patchy Dense Fog': 'PF+',
        'Haze': 'H',
        'Blowing Snow': 'BS',
        'Smoke': 'K',
        'Blowing Dust': 'BD',
        'Volcanic Ash': 'AF',
        # obvis strings supported by wu but not nws
        'Mist': 'M',
        'Fog Patches': 'PF',
        'Freezing Fog': 'FF',
        'Widespread Dust': 'DST',
        'Sand': 'SND',
        'Spray': 'SP',
        'Dust Whirls': 'DW',
        'Sandstorm': 'SS',
        'Low Drifting Snow': 'LDS',
        'Low Drifting Widespread Dust': 'LDD',
        'Low Drifting Sand': 'LDs',
        'Blowing Widespread Dust': 'BD',
        'Blowing Sand': 'Bs',
        'Snow Blowing Snow Mist': 'BS',
        'Patches of Fog': 'PF',
        'Shallow Fog': 'SF',
        'Partial Fog': 'PF',
        'Blizzard': 'BS',
        'Rain Mist': 'M',
    }

    # mapping from string to probability code
    wx2chance_dict = {
        'Slight Chance': 'S',
        'Chance': 'C',
        'Likely': 'L',
        'Occasional': 'O',
        'Definite': 'D',
        'Isolated': 'IS',
        'Scattered': 'SC',
        'Numerous': 'NM',
        'Extensive': 'EC',
    }

    # mapping from wu fctcode to a precipitation,chance tuple
    fct2precip_dict = {
        '10': ('rainshwrs', 'C'),
        '11': ('rainshwrs', 'L'),
        '12': ('rain', 'C'),
        '13': ('rain', 'L'),
        '14': ('tstms', 'C'),
        '15': ('tstms', 'L'),
        '16': ('flurries', 'L'),
        '18': ('snowshwrs', 'C'),
        '19': ('snowshwrs', 'L'),
        '20': ('snow', 'C'),
        '21': ('snow', 'L'),
        '22': ('sleet', 'C'),
        '23': ('sleet', 'L'),
        '24': ('snowshwrs', 'L'),
    }

    # mapping from wu fctcode to obvis code
    fct2obvis_dict = {
        '5': 'H',
        '6': 'F',
        '9': 'BS',
        '24': 'BS',
    }

    @staticmethod
    def code_from_precip_chance(precip_chance):
        if precip_chance < 30:
            return 'S'
        elif precip_chance < 60:
            return 'C'
        elif precip_chance < 80:
            return 'L'
        elif precip_chance < 100:
            return 'O'
        else:
            return 'D'

    @staticmethod
    def str2pc(s):
        """parse a wu wx string for the precipitation type and likeliehood

        Slight Chance Light Rain Showers -> rainshwrs,S
        Chance of Light Rain Showers     -> rainshwrs,C
        Isolated Thunderstorms           -> tstms,IS
        """
        for x in WUForecast.str2precip_dict:
            if s.endswith(x):
                for y in WUForecast.wx2chance_dict:
                    if s.startswith(y):
                        return WUForecast.str2precip_dict[x], WUForecast.wx2chance_dict[y]
                return WUForecast.str2precip_dict[x], ''
        return None, 0

    @staticmethod
    def wu2precip(period):
        """return a dictionary of precipitation with corresponding
        likeliehoods.  precipitation information may be in the fctcode,
        condition, or wx field, so look at each one and extract
        precipitation."""

        p = {}
        # first try the condition field
        if period['condition'].find(' and ') >= 0:
            for w in period['condition'].split(' and '):
                precip, chance = WUForecast.str2pc(w.strip())
                if precip is not None:
                    p[precip] = chance
        elif period['condition'].find(' with ') >= 0:
            for w in period['condition'].split(' with '):
                precip, chance = WUForecast.str2pc(w.strip())
                if precip is not None:
                    p[precip] = chance
        else:
            precip, chance = WUForecast.str2pc(period['condition'])
            if precip is not None:
                p[precip] = chance
        # then augment or possibly override with precip info from the fctcode
        if period['fctcode'] in WUForecast.fct2precip_dict:
            precip, chance = WUForecast.fct2precip_dict[period['fctcode']]
            p[precip] = chance
        # wx has us nws forecast strings, so trust it the most
        if len(period['wx']) > 0:
            for w in period['wx'].split(','):
                precip, chance = WUForecast.str2pc(w.strip())
                if precip is not None:
                    p[precip] = chance
        return p

    @staticmethod
    def wu2obvis(period):
        """return a single obvis type.  look in wx, fctcode, then condition."""

        if len(period['wx']) > 0:
            for x in [w.strip() for w in period['wx'].split(',')]:
                if x in WUForecast.str2obvis_dict:
                    return WUForecast.str2obvis_dict[x]
        if period['fctcode'] in WUForecast.fct2obvis_dict:
            return WUForecast.fct2obvis_dict[period['fctcode']]
        if period['condition'] in WUForecast.str2obvis_dict:
            return WUForecast.str2obvis_dict[period['condition']]
        return None


# -----------------------------------------------------------------------------
# Open Weather Map 5-day/3-hour forecast
#
# Forecasts from open weathermap (www.openweathermap.org).  OWM provides an
# api that returns json/xml data.  This implementation uses the json format.
#
# For the API, see:
#   http://www.openweathermap.org/forecast5
#   http://www.openweathermap.org/forecast16
#
# Warning!  The OWM forecasts are poorly and inconsistently documented.
# For example, units of snow is 'volume'.  Temperatures default to degree K.
# Weather conditions are ill-defined, non-orthogonal, and incompletely
# enumerated.  XML and JSON output use different names with different meanings,
# and thus have different data for the same forecast.
#
# There are two forecasts - 5-day/3-hour and 16-day/daily
#
# 5day3hour -------------------------------------------------------------------
#
# dt
# temp (K, C, or F)
# temp_min (K, C, or F)
# temp_max (K, C, or F)
# pressure (hPa)
# sea_level (hPa)
# grnd_level (hPa)
# humidity (%)
# temp_kf
# weather.id
# weather.main
# weather.description
# weather.icon
# clouds.all (%)
# wind.speed (m/s, mph)
# wind.deg
# snow.3h (mm)
# rain.3h (?)
# sys.pod
# dt_txt
#
# 16day -----------------------------------------------------------------------
#
# not yet supported

class OWMForecast(Forecast):

    KEY = 'OWM'
    DEFAULT_URL = 'http://api.openweathermap.org/data/2.5/forecast'

    def __init__(self, engine, config_dict):
        super(OWMForecast, self).__init__(engine, config_dict,
                                          OWMForecast.KEY, interval=10800)
        d = config_dict.get('Forecast', {}).get(OWMForecast.KEY, {})
        self.url = d.get('url', OWMForecast.DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.api_key = d.get('api_key', None)
        self.location = d.get('location', None)
        self.forecast_type = d.get('forecast_type', '5day3hour')

        if self.location is None:
            self.location = Forecast.get_loc_from_station(config_dict)

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.api_key is None or self.api_key.startswith('INSERT_'):
            errmsg.append('API key (api_key) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (self.method_id, e))
            logerr('%s: forecast will not be run' % self.method_id)
            return

        loginf('%s: interval=%s max_age=%s api_key=%s location=%s fc=%s' %
               (self.method_id, self.interval, self.max_age,
                self.obfuscate(self.api_key), self.location,
                self.forecast_type))
        self._bind()

    def get_forecast(self, dummy_event):
        text = self.download(self.api_key, self.location,
                             url=self.url, fc_type=self.forecast_type,
                             max_tries=self.max_tries)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (self.method_id, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='owm-raw')
        records, msgs = self.parse(text, location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='owm-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (self.method_id, len(records)))
        return records

    @staticmethod
    def download(api_key, location, url=DEFAULT_URL,
                 fc_type='5day3hour', max_tries=3):
        """Download a forecast from Open WeatherMap

        api_key - key for downloading from OwM

        location - lat/lon, post code, or other location identifier

        url - URL to the openweathermap service.  if anything other than the
              default is specified, that entire URL is used.  if the default
              is specified, it is used as the base and other items are added
              to it.

        fc_type - forecast type, one of 5day3hour or 16day

        max_tries - how many times to try before giving up
        """

        locstr = OWMForecast.get_location_string(location)
        u = '%s?APPID=%s&%s' % (url, api_key, locstr) \
            if url == OWMForecast.DEFAULT_URL else url
        masked = Forecast.get_masked_url(u, api_key)
        loginf("%s: download forecast from '%s'" % (OWMForecast.KEY, masked))

        for count in range(max_tries):
            try:
                response = six.moves.urllib.request.urlopen(u)
                return response.read().decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (OWMForecast.KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % OWMForecast.KEY)
        return None

    @staticmethod
    def parse(text, issued_ts=None, now=None, location=None):
        if issued_ts is None or now is None:
            n = int(time.time())
            if issued_ts is None:
                issued_ts = n
            if now is None:
                now = n
        msgs = []
        records = []
        cnt = 0
        fc = json.loads(text)
        total = fc.get('cnt', 0)
        for period in fc['list']:
            try:
                cnt += 1
                r = {}
                r['method'] = OWMForecast.KEY
                r['usUnits'] = weewx.US
                r['dateTime'] = now
                r['issued_ts'] = issued_ts
                r['event_ts'] = Forecast.str2int(
                    'dt', period['dt'], OWMForecast.KEY)
                r['duration'] = 3 * 3600
                if 'clouds' in period and 'all' in period['clouds']:
                    r['clouds'] = Forecast.pct2clouds(period['clouds']['all'])
                r['temp'] = Forecast.str2float(
                    'temp', period['main']['temp'],
                    OWMForecast.KEY) * 9.0 / 5.0 - 459.67
                r['humidity'] = Forecast.str2int(
                    'humidity', period['main']['humidity'], OWMForecast.KEY)
                r['windSpeed'] = Forecast.str2float(
                    'wind.speed', period['wind']['speed'],
                    OWMForecast.KEY) * 2.236936
                r['windDir'] = Forecast.deg2dir(period['wind']['deg'])
                if 'rain' in period and '3h' in period['rain']:
                    r['qpf'] = Forecast.str2float(
                        'rain.3h', period['rain']['3h'],
                        OWMForecast.KEY) / 25.4
                if 'snow' in period and '3h' in period['snow']:
                    r['qsf'] = Forecast.str2float(
                        'snow.3h', period['snow']['3h'],
                        OWMForecast.KEY) / 25.4
                if 'main' in period and 'description' in period['main']:
                    r['desc'] = period['main']['description']
                if location is not None:
                    r['location'] = location
                if 'pop' in period:
                    r['pop'] = Forecast.str2float('pop',period['pop'],OWMForecast.KEY)*100
                if 'main' in period and 'temp_min' in period['main']:
                    r['tempMin'] = Forecast.str2float('pop',period['main']['temp_min'],OWMForecast.KEY)* 9.0 / 5.0 - 459.67
                if 'main' in period and 'temp_max' in period['main']:
                    r['tempMax'] = Forecast.str2float('pop',period['main']['temp_max'],OWMForecast.KEY)* 9.0 / 5.0 - 459.67
                if 'visibility' in period:
                    r['obvis'] = Forecast.str2float('pop',period['visibility'],OWMForecast.KEY) / 1609.344
                
                # FIXME pressure
                # FIXME sea_level
                # FIXME grnd_level
                records.append(r)
            except KeyError as e:
                msg = '%s: failure in forecast period %d: %s' % (
                    OWMForecast.KEY, cnt, e)
                msgs.append(msg)
                logerr(msg)
        if total != cnt:
            msgs.append('record mismatch: total=%s != parsed=%s' % (total, cnt))
        return records, msgs

    @staticmethod
    def get_location_string(loc):
        idx = loc.find(',')
        if idx == len(loc) - 3:
            return "q=%s" % loc
        elif idx >= 0:
            return "lat=%s&lon=%s" % (loc[0:idx], loc[idx + 1:])
        return "id=%s" % loc


# -----------------------------------------------------------------------------
# UK Met Office 5-day/3-hour forecast
#
# Forecasts from open UK Met Office (www.metoffice.gov.uk).  UKMO provides an
# api that returns json/xml data.  This implementation uses the json format.
#
# For the API, see:
#   http://www.metoffice.gov.uk/datapoint/product/uk-3hourly-site-specific-forecast/detailed-documentation
#
# 5day3hour -------------------------------------------------------------------
#
# D  - wind direction, compass
# F  - feels-like temperature, C
# G  - wind gust, mph
# H  - humidity, %
# Pp - precipitation probability, %
# S  - wind speed, mph
# T  - temperature, C
# V  - visibility
# W  - weather type
# U  - max uv index
# $  - number of minutes after midnight GMT on day of period object
#
# weather types
# NA - not available
#  0 - clear night
#  1 - sunny day
#  2 - partly cloudy (night)
#  3 - partly cloudy (day)
#  4 - not used
#  5 - mist
#  6 - fog
#  7 - cloudy
#  8 - overcast
#  9 - light rain shower (night)
# 10 - light rain shower (day)
# 11 - drizzle
# 12 - light rain
# 13 - heavy rain shower (night)
# 14 - heavy rain shower (day)
# 15 - heavy rain
# 16 - sleet shower (night)
# 17 - sleet shower (day)
# 18 - sleet
# 19 - hail shower (night)
# 20 - hail shower (day)
# 21 - hail
# 22 - light snow shower (night)
# 23 - light snow shower (day)
# 24 - light snow
# 25 - heavy snow shower (night)
# 26 - heavy snow shower (day)
# 27 - heavy snow
# 28 - thunder shower (night)
# 29 - thunder shower (day)
# 30 - thunder
#
# visibility
# UN - unknown
# VP - very poor (less than 1 km)
# PO - poor (1-4 km)
# MO - moderate (4-10 km)
# GO - good (10-20 km)
# VG - very good (20-40 km)
# EX - excellent (more than 40 km)

class UKMOForecast(Forecast):

    KEY = 'UKMO'
    DEFAULT_URL = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/'

    def __init__(self, engine, config_dict):
        super(UKMOForecast, self).__init__(engine, config_dict,
                                           UKMOForecast.KEY, interval=10800)
        d = config_dict.get('Forecast', {}).get(UKMOForecast.KEY, {})
        self.url = d.get('url', UKMOForecast.DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.api_key = d.get('api_key', None)
        self.location = d.get('location', None)

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.api_key is None or self.api_key.startswith('INSERT_'):
            errmsg.append('API key (api_key) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (self.method_id, e))
            logerr('%s: forecast will not be run' % self.method_id)
            return

        loginf('%s: interval=%s max_age=%s api_key=%s location=%s' %
               (self.method_id, self.interval, self.max_age,
                self.obfuscate(self.api_key), self.location))
        self._bind()

    def get_forecast(self, dummy_event):
        text = self.download(self.api_key, self.location,
                             url=self.url, max_tries=self.max_tries)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (self.method_id, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='ukmo-raw')
        records, msgs = self.parse(text, location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='ukmo-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (self.method_id, len(records)))
        return records

    @staticmethod
    def download(api_key, location, url=DEFAULT_URL, max_tries=3):
        """Download a forecast from UK Met Office

        api_key - key for downloading

        location - location identifier

        url - URL to the forecast service.  if anything other than the default
              is specified, that entire URL is used.  if the default is
              specified, it is used as the base and other items are added
              to it.

        max_tries - how many times to try before giving up
        """

        u = '%s%s?res=3hourly&key=%s' % (url, location, api_key) \
            if url == UKMOForecast.DEFAULT_URL else url
        masked = Forecast.get_masked_url(u, api_key)
        loginf("%s: download forecast from '%s'" % (UKMOForecast.KEY, masked))

        for count in range(max_tries):
            try:
                user_agent = {'User-Agent': 'Mozilla/5.0'}
                requester = six.moves.urllib.request.Request(u, headers=user_agent)
                response = six.moves.urllib.request.urlopen(requester)
                return response.read().decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (UKMOForecast.KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % UKMOForecast.KEY)
        return None

    @staticmethod
    def parse(text, now=None, location=None):
        if now is None:
            now = int(time.time())
        msgs = []
        records = []
        cnt = 0
        fc = json.loads(text)
        try:
            fc['SiteRep']['DV']['dataDate']
            fc['SiteRep']['DV']['Location']['Period']
            loc = fc['SiteRep']['DV']['Location']['i']
            if loc != location:
                loginf("%s: location mismatch: %s != %s" %
                       (UKMOForecast.KEY, loc, location))
        except KeyError as e:
            logerr("%s: missing field %s" % (UKMOForecast.KEY, e))
            return records, msgs
        issued_ts = UKMOForecast.dd2ts(fc['SiteRep']['DV']['dataDate'])
        for period in fc['SiteRep']['DV']['Location']['Period']:
            day_ts = UKMOForecast.pv2ts(period['value'])
            for rep in period['Rep']:
                try:
                    cnt += 1
                    r = {}
                    r['method'] = UKMOForecast.KEY
                    r['usUnits'] = weewx.US
                    r['dateTime'] = now
                    r['issued_ts'] = issued_ts
                    r['event_ts'] = Forecast.str2int(
                        'offset', rep['$'], UKMOForecast.KEY) * 60 + day_ts
                    r['duration'] = 3 * 3600
                    r['temp'] = Forecast.str2float(
                        'temp', rep['T'], UKMOForecast.KEY) * 9.0 / 5.0 + 32
                    r['humidity'] = Forecast.str2int(
                        'humidity', rep['H'], UKMOForecast.KEY)
                    r['windSpeed'] = Forecast.str2float(
                        'windSpeed', rep['S'], UKMOForecast.KEY)
                    r['windGust'] = Forecast.str2float(
                        'windGust', rep['G'], UKMOForecast.KEY)
                    r['windDir'] = rep['D']
                    r['pop'] = Forecast.str2int(
                        'pop', rep['Pp'], UKMOForecast.KEY)
                    r['uvIndex'] = Forecast.str2int(
                        'uvIndex', rep['U'], UKMOForecast.KEY)
                    # feelslike 'F'
                    # weather type 'W'
                    # visibility 'V'
                    if location is not None:
                        r['location'] = location
                    records.append(r)
                except KeyError as e:
                    msg = '%s: failure in forecast period %d: %s' % (
                        UKMOForecast.KEY, cnt, e)
                    msgs.append(msg)
                    logerr(msg)
        return records, msgs

    @staticmethod
    def dd2ts(s):
        s = s.replace('T', ' ')
        s = s.replace('Z', '')
        tt = time.strptime(s, '%Y-%m-%d %H:%M:%S')
        return int(calendar.timegm(tt))

    @staticmethod
    def pv2ts(s):
        s = s.replace('Z', '')
        tt = time.strptime(s, '%Y-%m-%d')
        return int(calendar.timegm(tt))


# -----------------------------------------------------------------------------
# Aeris forecast
#
# For the API, see:
#   http://www.aerisweather.com/support/docs/api
#
# 'developer' level has 'premium' access, i.e., 15-day/1-hour forecasts.
#
# Forecasts are available in 1, 3, 6, 12, and 24 hour intervals.
#
# coded weather
#
# codes may be combinged to coverage:intensity:weather, e.g., S:L:RW or ::FW
#
# cloud codes
# CL - clear (0-7%)
# FW - fair/mostly sunny (7-32%)
# SC - partly cloudy (32-70%)
# BK - mostly cloudy (70-95%)
# OV - cloudy/overcast (95-100%)
#
# coverage codes
# AR - areas of
# BR - brief
#  C - chance of
#  D - definite
# FQ - frequent
# IN - intermittent
# IS - isolated
#  L - likely
# NM - numerous
#  O - occasional
# PA - patchy
# PD - periods of
#  S - slight chance
# SC - scattered
# VC - in the vicinity/nearby
# WD - widespread
#
# intensity codes
# VL - very light
#  L - light
#  H - heavy
# VH - very heavy
#
# weather codes
#  A - hail
# BD - blowing dust
# BN - blowing sand
# BR - mist
# BS - blowing snow
# BY - blowing spray
#  F - fog
# FR - frost
#  H - haze
# IC - ice crystals
# IF - ice fog
# IP - ice pellets/sleet
#  K - smoke
#  L - drizzle
#  R - rain
# RW - rain showers
# RS - rain/snow mix
# SI - snow/sleet mix
# WM - wintry mix (snow, sleet, rain)
#  S - snow
# SW - snow showers
#  T - thunderstorms
# UP - unknown precipitation
# VA - volcanic ash
# WP - waterspouts
# ZF - freezing fog
# ZL - freezing drizzle
# ZR - freezing rain
# ZY - freezing spray

class AerisForecast(Forecast):

    KEY = 'Aeris'
    DEFAULT_URL = 'http://api.aerisapi.com/forecasts/'

    def __init__(self, engine, config_dict):
        super(AerisForecast, self).__init__(engine, config_dict,
                                            AerisForecast.KEY, interval=10800)
        d = config_dict.get('Forecast', {}).get(AerisForecast.KEY, {})
        self.url = d.get('url', self.DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.client_id = d.get('client_id', None)
        self.client_secret = d.get('client_secret', None)
        self.location = d.get('location', None)
        self.forecast_type = d.get('forecast_type', '1hr')

        if self.location is None:
            self.location = Forecast.get_loc_from_station(config_dict)

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.client_id is None or self.client_id.startswith('INSERT_'):
            errmsg.append('client identifier (client_id) is not specified')
        if self.client_secret is None or self.client_secret.startswith('INSERT_'):
            errmsg.append('client secret (client_secret) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (self.method_id, e))
            logerr('%s: forecast will not be run' % self.method_id)
            return

        loginf('%s: interval=%s max_age=%s client_id=%s client_secret=%s location=%s' %
               (self.method_id, self.interval, self.max_age,
                self.obfuscate(self.client_id),
                self.obfuscate(self.client_secret), self.location))
        self._bind()

    def get_forecast(self, dummy_event):
        text = self.download(self.client_id, self.client_secret, self.location,
                             self.forecast_type,
                             url=self.url, max_tries=self.max_tries)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (self.method_id, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='aeris-raw')
        records, msgs = self.parse(text, location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='aeris-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (self.method_id, len(records)))
        return records

    _LATLON = re.compile('[\d\+\-]+,[\d\+\-]+')

    @staticmethod
    def build_url(client_id, client_secret, location, fc_type, url):
        ep = location
        opts = ['client_id=%s' % client_id, 'client_secret=%s' % client_secret]
        if location and AerisForecast._LATLON.search(location):
            ep = 'closest'
            opts.append('p=%s' % location)
        opts.append('filter=%s' % fc_type)
        u = '%s%s?%s' % (url, ep, '&'.join(opts)) \
            if url == AerisForecast.DEFAULT_URL else url
        return u

    @staticmethod
    def download(client_id, client_secret, location,
                 fc_type='1hr', url=DEFAULT_URL, max_tries=3):
        """Download a forecast from Aeris

        client_id, client_secret - credentials for downloading

        location - location identifier

        fc_type - filter can be one of 1hr, 3hr, 6hr, 12hr, or 24hr

        url - URL to the forecast service.  if anything other than the default
              is specified, that entire URL is used.  if the default is
              specified, it is used as the base and other items are added to it.

        max_tries - how many times to try before giving up
        """

        u = AerisForecast.build_url(
            client_id, client_secret, location, fc_type, url)
        masked = Forecast.get_masked_url(u, client_id)
        masked = Forecast.get_masked_url(masked, client_secret)
        loginf("%s: download forecast from '%s'" % (AerisForecast.KEY, masked))

        for count in range(max_tries):
            try:
                response = six.moves.urllib.request.urlopen(u)
                return response.read().decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (AerisForecast.KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % AerisForecast.KEY)
        return None

    @staticmethod
    def parse(text, issued_ts=None, now=None, location=None):
        msgs = []
        records = []

        obj = json.loads(text)
        if not ('response' in obj and 'success' in obj and 'error' in obj):
            msg = "%s: no response/success/error in reply" % AerisForecast.KEY
            logerr(msg)
            return [], [msg]
        if obj['error'] is not None:
            msg = '%s: %s: %s' % (
                AerisForecast.KEY,
                obj['error']['code'], obj['error']['description'])
            logerr(msg)
            msgs.append(msg)
        if obj['success'] != True:
            return [], [msg]
        if len(obj['response']) > 1:
            msg = '%s: unexpected number of responses (%s)' % (
                AerisForecast.KEY, len(obj['response']))
            return [], [msg]

        if issued_ts is None or now is None:
            n = int(time.time())
            if issued_ts is None:
                issued_ts = n
            if now is None:
                now = n

        response = obj['response'][0]
        istr = response['interval'][0:-2]
        dur = 3600 * int(istr)
        cnt = 0
        for p in response['periods']:
            try:
                cnt += 1
                r = {}
                r['method'] = AerisForecast.KEY
                r['usUnits'] = weewx.US
                r['dateTime'] = now
                r['issued_ts'] = issued_ts
                r['event_ts'] = AerisForecast.str2int(p, 'timestamp')
                r['duration'] = dur
                r['tempMax'] = AerisForecast.str2float(p, 'maxTempF')
                r['tempMin'] = AerisForecast.str2float(p, 'minTempF')
                # avgTempF
                r['temp'] = AerisForecast.str2float(p, 'tempF')
                r['pop'] = AerisForecast.str2float(p, 'pop')
                r['qpf'] = AerisForecast.str2float(p, 'precipIN')
                # iceaccum
                r['humidity'] = AerisForecast.str2int(p, 'humidity')
                # maxHumidity
                # minHumidity
                r['uvIndex'] = AerisForecast.str2int(p, 'uvi')
                # pressureIN
                # skye
                r['qsf'] = AerisForecast.str2float(p, 'snowIN')
                # feelslikeF
                # minFeelslikeF
                # maxFeelslikeF
                # avgFeelslikeF
                r['dewpoint'] = AerisForecast.str2float(p, 'dewpointF')
                # maxDewpointF
                # minDewpointF
                # avgDewpointF
                r['windDir'] = p['windDir']
                # windDirMax
                # windDirMin
                r['windGust'] = AerisForecast.str2float(p, 'windGustMPH')
                r['windSpeed'] = AerisForecast.str2float(p, 'windSpeedMPH')
                # windSpeedMaxMPH
                # windSpeedMinMPH
                # windDir80m
                # windDirMax80m
                # windDirMin80m
                # windGust80mMPH
                # windSpeed80mMPH
                # windSpeedMax80mMPH
                # windSpeedMin80mMPH
                # weather
                # weatherCoded
                # weatherCoded.timestamp
                # weatherCoded.wx
                # weatherPrimary
                # weatherPrimaryCoded
                r['clouds'] = p['cloudsCoded']
                # icon
                # isDay
                # sunrise
                # sunriseISO
                # sunset
                # sunsetISO
                if location is not None:
                    r['location'] = location
                records.append(r)
            except KeyError as e:
                msg = '%s: failure in forecast period %d: %s' % (
                    AerisForecast.KEY, cnt, e)
                msgs.append(msg)
                logerr(msg)
        return records, msgs

    @staticmethod
    def str2float(pkt, label):
        return Forecast.str2float(label, pkt[label], AerisForecast.KEY)

    @staticmethod
    def str2int(pkt, label):
        return Forecast.str2int(label, pkt[label], AerisForecast.KEY)


# -----------------------------------------------------------------------------
# WWO forecast
#
# condition codes
# code    condition
# 395     Moderate or heavy snow in area with thunder
# 392     Patchy light snow in area with thunder
# 389     Moderate or heavy rain in area with thunder
# 386     Patchy light rain in area with thunder
# 377     Moderate or heavy showers of ice pellets
# 374     Light showers of ice pellets
# 371     Moderate or heavy snow showers
# 368     Light snow showers
# 365     Moderate or heavy sleet showers
# 362     Light sleet showers
# 359     Torrential rain shower
# 356     Moderate or heavy rain shower
# 353     Light rain shower
# 350     Ice pellets
# 338     Heavy snow
# 335     Patchy heavy
# 332     Moderate snow
# 329     Patchy moderate snow
# 326     Light snow
# 323     Patchy light snow
# 320     Moderate or heavy sleet
# 317     Light sleet
# 314     Moderate or Heavy freezing rain
# 311     Light freezing rain
# 308     Heavy rain
# 305     Heavy rain at times
# 302     Moderate rain
# 299     Moderate rain at times
# 296     Light rain
# 293     Patchy light rain
# 284     Heavy freezing drizzle
# 281     Freezing drizzle
# 266     Light drizzle
# 263     Patchy light drizzle
# 260     Freezing fog
# 248     Fog
# 230     Blizzard
# 227     Blowing snow
# 200     Thundery outbreaks in nearby
# 185     Patchy freezing drizzle nearby
# 182     Patchy sleet nearby
# 179     Patchy snow nearby
# 176     Patchy rain nearby
# 143     Mist
# 122     Overcast
# 119     Cloudy
# 116     Partly Cloudy
# 113     Clear/Sunny

class WWOForecast(Forecast):

    KEY = 'WWO'
    DEFAULT_URL = 'http://api.worldweatheronline.com/free/v2/weather.ashx'

    def __init__(self, engine, config_dict):
        super(WWOForecast, self).__init__(engine, config_dict,
                                          WWOForecast.KEY, interval=10800)
        d = config_dict.get('Forecast', {}).get(WWOForecast.KEY, {})
        self.url = d.get('url', self.DEFAULT_URL)
        self.max_tries = int(d.get('max_tries', 3))
        self.api_key = d.get('api_key', None)
        self.location = d.get('location', None)
        self.forecast_type = int(d.get('forecast_type', 3))

        if self.location is None:
            self.location = Forecast.get_loc_from_station(config_dict)

        errmsg = []
        if json is None:
            errmsg.append('json is not installed')
        if self.api_key is None or self.api_key.startswith('INSERT_'):
            errmsg.append('API key (api_key) is not specified')
        if self.location is None:
            errmsg.append('location is not specified')
        if errmsg:
            for e in errmsg:
                logerr("%s: %s" % (self.method_id, e))
            logerr('%s: forecast will not be run' % self.method_id)
            return

        loginf('%s: interval=%s max_age=%s api_key=%s location=%s' %
               (self.method_id, self.interval, self.max_age,
                self.obfuscate(self.api_key), self.location))
        self._bind()

    def get_forecast(self, dummy_event):
        text = self.download(self.api_key, self.location, self.forecast_type,
                             url=self.url, max_tries=self.max_tries)
        if text is None:
            logerr('%s: no forecast data for %s from %s' %
                   (self.method_id, self.location, self.url))
            return None
        if self.save_raw:
            self.save_raw_forecast(text, basename='wwo-raw')
        records, msgs = self.parse(text, location=self.location)
        if self.save_failed and len(msgs) > 0:
            self.save_failed_forecast(text, basename='wwo-fail', msgs=msgs)
        loginf('%s: got %d forecast records' % (self.method_id, len(records)))
        return records

    @staticmethod
    def build_url(api_key, location, fc_type, url):
        opts = ['key=%s' % api_key,
                'q=%s' % location,
                'tp=%s' % fc_type,
                'format=json',
                'num_of_days=5',
                'includelocation=yes',
                'cc=no']
        u = '%s?%s' % (url, '&'.join(opts)) \
            if url == WWOForecast.DEFAULT_URL else url
        return u

    @staticmethod
    def download(api_key, location, fc_type=3, url=DEFAULT_URL, max_tries=3):
        """Download a forecast from WWO

        api_key - credentials for downloading

        location - location identifier

        fc_type - can be one of 3, 6, 12, 24

        url - URL to the forecast service.  if anything other than the default
              is specified, that entire URL is used.  if the default is
              specified, it is used as the base and other items are added to it.

        max_tries - how many times to try before giving up
        """

        u = WWOForecast.build_url(api_key, location, fc_type, url)
        masked = Forecast.get_masked_url(u, api_key)
        loginf("%s: download forecast from '%s'" % (WWOForecast.KEY, masked))

        for count in range(max_tries):
            try:
                response = six.moves.urllib.request.urlopen(u)
                return response.read().decode('utf-8')
            except (six.moves.urllib.error.URLError, socket.error,
                    six.moves.http_client.BadStatusLine, six.moves.http_client.IncompleteRead) as e:
                logerr('%s: failed attempt %d to download forecast: %s' %
                       (WWOForecast.KEY, count + 1, e))
        else:
            logerr('%s: failed to download forecast' % WWOForecast.KEY)
        return None

    @staticmethod
    def parse(text, issued_ts=None, now=None, location=None):
        obj = json.loads(text)
        if 'results' in obj and 'error' in obj['results']:
            msg = "%s: %s: %s" % (WWOForecast.KEY,
                                  obj['results']['error']['type'],
                                  obj['results']['error']['message'])
            logerr(msg)
            return [], [msg]
        if not 'data' in obj or not 'weather' in obj['data']:
            msg = "%s: no data.weather in reply" % WWOForecast.KEY
            logerr(msg)
            return [], [msg]

        if issued_ts is None or now is None:
            n = int(time.time())
            if issued_ts is None:
                issued_ts = n
            if now is None:
                now = n

        msgs = []
        records = []
        cnt = 0
        ival = 3 # FIXME
        # FIXME: loc = obj['data']['request']['query']
        for day in obj['data']['weather']:
            day_tt = time.strptime(day['date'], '%Y-%m-%d')
            day_ts = int(time.mktime(day_tt))
            for p in day['hourly']:
                try:
                    cnt += 1
                    local_ts = WWOForecast.str2int(p, 'time') * 36 + day_ts
                    local_tt = time.localtime(local_ts)
                    r = {}
                    r['method'] = WWOForecast.KEY
                    r['usUnits'] = weewx.US
                    r['dateTime'] = now
                    r['issued_ts'] = issued_ts
                    r['event_ts'] = int(time.mktime(local_tt))
                    r['duration'] = ival * 3600 # FIXME
                    # chanceoffog
                    # chanceoffrost
                    # chanceofovercast
                    # chanceofrain
                    # chanceofremdry
                    # chanceofsnow
                    # chanceofsunshine
                    # chanceofthunder
                    # chanceofwindy
                    r['clouds'] = Forecast.pct2clouds(p['cloudcover'])
                    r['dewpoint'] = WWOForecast.str2float(p, 'DewPointF')
                    # feelslike
                    r['heatIndex'] = WWOForecast.str2float(p, 'HeatIndexF')
                    r['humidity'] = WWOForecast.str2float(p, 'humidity')
                    r['qpf'] = WWOForecast.str2float(p, 'precipMM') / 25.4
                    # pressure
                    r['temp'] = WWOForecast.str2float(p, 'tempF')
                    # visibility
                    # weatherCode
                    # weatherDesc
                    # weatherIconUrl
                    r['windChill'] = WWOForecast.str2float(p, 'WindChillF')
                    r['windDir'] = p['winddir16Point']
                    # winddirDegree
                    r['windGust'] = WWOForecast.str2float(p, 'WindGustMiles')
                    r['windSpeed'] = WWOForecast.str2float(p, 'windspeedMiles')
                    if location is not None:
                        r['location'] = location
                    records.append(r)
                except KeyError as e:
                    msg = '%s: failure in forecast period %d: %s' % (
                        WWOForecast.KEY, cnt, e)
                    msgs.append(msg)
                    logerr(msg)
        return records, msgs

    @staticmethod
    def str2float(pkt, label):
        return Forecast.str2float(label, pkt[label], WWOForecast.KEY)

    @staticmethod
    def str2int(pkt, label):
        return Forecast.str2int(label, pkt[label], WWOForecast.KEY)


# -----------------------------------------------------------------------------
# xtide tide predictor
#
# The xtide application must be installed for this to work.  For example, on
# debian systems do this:
#
#   sudo apt-get install xtide
#
# This forecasting module uses the command-line 'tide' program, not the
# x-windows application.
# -----------------------------------------------------------------------------

XT_KEY = 'XTide'
XT_PROG = '/usr/bin/tide'
XT_HILO = {'High Tide': 'H', 'Low Tide': 'L'}

class XTideForecast(Forecast):
    """generate tide forecast using xtide"""

    def __init__(self, engine, config_dict):
        super(XTideForecast, self).__init__(engine, config_dict, XT_KEY,
                                            interval=1209600, max_age=2419200)
        d = config_dict.get('Forecast', {}).get(XT_KEY, {})
        self.duration = int(d.get('duration', 2 * self.interval))
        self.tideprog = d.get('prog', XT_PROG)
        self.location = weeutil.weeutil.list_as_string(d.get('location', None))

        if self.location is None or self.location.startswith('INSERT_'):
            logerr('%s: location (location) has not been specified' % XT_KEY)
            logerr('%s: forecast will not be run' % XT_KEY)
            return

        loginf("%s: interval=%s max_age=%s location='%s' duration=%s" %
               (XT_KEY, self.interval, self.max_age,
                self.location, self.duration))
        self._bind()

    def get_forecast(self, dummy_event):
        lines = self.generate(
            self.location, dur=self.duration, prog=self.tideprog)
        if lines is None:
            return None
        records = self.parse(lines, location=self.location)
        if records is None:
            return None
        logdbg('%s: tide matrix: %s' % (self.method_id, records))
        return records

    @staticmethod
    def parse(lines, now=None, location=None):
        """Convert the text output into an array of records."""
        if now is None:
            now = int(time.time())
        records = []
        for line in lines:
            line = line.rstrip()
            if not line:
                continue
            fields = line.split(',')
            if len(fields) != 5:
                logdbg("expected 5 fields, found %s: %s" % (len(fields), line))
                continue
            if fields[4] == 'High Tide' or fields[4] == 'Low Tide':
                s = '%s %s' % (fields[1], fields[2])
                tt = time.strptime(s, '%Y.%m.%d %H:%M')
                ts = time.mktime(tt)
                ofields = fields[3].split(' ')
                if ofields[1] == 'ft':
                    offset = ofields[0]
                elif ofields[1] == 'm':
                    vt = (float(ofields[0]), 'meter', 'group_altitude')
                    offset = weewx.units.convertStd(vt, weewx.US)[0]
                else:
                    logerr("%s: unknown units '%s'" % (XT_KEY, ofields[1]))
                    continue
                record = {}
                record['method'] = XT_KEY
                record['usUnits'] = weewx.US
                record['dateTime'] = int(now)
                record['issued_ts'] = int(now)
                record['event_ts'] = int(ts)
                record['hilo'] = XT_HILO[fields[4]]
                record['offset'] = offset
                record['location'] = location
                records.append(record)
        return records

    @staticmethod
    def generate(location, sts=None, ets=None, dur=2419200, prog=XT_PROG):
        """Generate tide information from the indicated period.  If no start
        and end time are specified, start with the start of the day of the
        current time and end at today plus duration."""
        if sts is None:
            sts = weeutil.weeutil.startOfDay(int(time.time()))
        if ets is None:
            ets = sts + dur
        st = time.strftime('%Y-%m-%d %H:%M', time.localtime(sts))
        et = time.strftime('%Y-%m-%d %H:%M', time.localtime(ets))
        cmd = "%s -fc -df'%%Y.%%m.%%d' -tf'%%H:%%M' -l'%s' -b'%s' -e'%s'" % (
            prog, location, st, et)
        try:
            loginf('%s: generating tides from %s to %s' %
                   (XT_KEY,
                    weeutil.weeutil.timestamp_to_string(sts),
                    weeutil.weeutil.timestamp_to_string(ets)))
            logdbg("%s: running command '%s'" % (XT_KEY, cmd))
            p = subprocess.Popen(cmd, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            rc = p.returncode
            if rc is not None:
                logerr("%s: generate forecast failed: loc='%s' code=%s" %
                       (XT_KEY, location, -rc))
                return None

            # look for comma-delimited output.  we expect lines like this:
            #   location,YYYY-MM-DD,HH:MM xM xxx,offset,description
            # xtide replaces commas in the location with |
            out = []
            for line in p.stdout:
                line = line.decode('utf-8')
                if line.count(',') == 4:
                    out.append(line)
                else:
                    logdbg("%s: ignoring line: %s" % (XT_KEY, line))
            if out:
                logdbg("%s: got %d lines of output" % (XT_KEY, len(out)))
                fields = out[0].split(',')
                loc = fields[0].replace('|', ',')
                loc = loc.replace(' - READ flaterco.com/pol.html', '')
                if loc != location:
                    loginf("%s: location mismatch: '%s' != '%s'" %
                           (XT_KEY, location, loc))
                return out
            loginf("%s: got no tidal events" % XT_KEY)

            # we got no recognizable output, so try to make sense of any errors
            err = []
            preamble = True
            for line in p.stderr:
                if line.startswith('Indexing'):
                    preamble = False
                if not line.startswith('Indexing') and not preamble:
                    line = line.rstrip()
                    err.append(line)
            errmsg = ' '.join(err)
            idx = errmsg.find('XTide Error:')
            if idx >= 0:
                errmsg = errmsg[idx:]
            idx = errmsg.find('XTide Fatal Error:')
            if idx >= 0:
                errmsg = errmsg[idx:]
            if len(errmsg):
                logerr('%s: generate forecast failed: %s' % (XT_KEY, errmsg))

            return None
        except OSError as e:
            logerr('%s: generate forecast failed: %s' % (XT_KEY, e))
        return None


# -----------------------------------------------------------------------------
# ForecastVariables
# -----------------------------------------------------------------------------

TRACE_AMOUNT = 0.001

# FIXME: weewx should define 'length' rather than (as well as?) 'altitude'
DEFAULT_UNITS = {
    weewx.US: {
        'group_time': 'unix_epoch',
        'group_altitude': 'foot',
        'group_temperature': 'degree_F',
        'group_speed': 'mile_per_hour',
        'group_rain': 'inch',
        'group_percent': 'percent',
    },
    weewx.METRIC: {
        'group_time': 'unix_epoch',
        'group_altitude': 'meter',
        'group_temperature': 'degree_C',
        'group_speed': 'km_per_hour',
        'group_rain': 'cm',
        'group_percent': 'percent',
    },
    weewx.METRICWX: {
        'group_time': 'unix_epoch',
        'group_altitude': 'meter',
        'group_temperature': 'degree_C',
        'group_speed': 'meter_per_second',
        'group_rain': 'mm',
        'group_percent': 'percent',
    }
}

UNIT_GROUPS = {
    'dateTime':     'group_time',
    'issued_ts':    'group_time',
    'event_ts':     'group_time',
    'temp':         'group_temperature',
    'tempMin':      'group_temperature',
    'tempMax':      'group_temperature',
    'dewpoint':     'group_temperature',
    'dewpointMin':  'group_temperature',
    'dewpointMax':  'group_temperature',
    'humidity':     'group_percent',
    'humidityMin':  'group_percent',
    'humidityMax':  'group_percent',
    'windSpeed':    'group_speed',
    'windSpeedMin': 'group_speed',
    'windSpeedMax': 'group_speed',
    'windGust':     'group_speed',
    'pop':          'group_percent',
    'qpf':          'group_rain',
    'qpfMin':       'group_rain',
    'qpfMax':       'group_rain',
    'qsf':          'group_rain',
    'qsfMin':       'group_rain',
    'qsfMax':       'group_rain',
    'windChill':    'group_temperature',
    'heatIndex':    'group_temperature',
    }

PERIOD_FIELDS_WITH_UNITS = [
    'dateTime',
    'issued_ts',
    'event_ts',
    'temp',
    'tempMin',
    'tempMax',
    'dewpoint',
    'humidity',
    'windSpeed',
    'windGust',
    'pop',
    'qpf',
    'qpfMin',
    'qpfMax',
    'qsf',
    'qsfMin',
    'qsfMax',
    'windChill',
    'heatIndex',
]

SUMMARY_FIELDS_WITH_UNITS = [
    'dateTime',
    'issued_ts',
    'event_ts',
    'temp',
    'tempMin',
    'tempMax',
    'dewpoint',
    'dewpointMin',
    'dewpointMax',
    'humidity',
    'humidityMin',
    'humidityMax',
    'windSpeed',
    'windSpeedMin',
    'windSpeedMax',
    'windGust',
    'pop',
    'qpf',
    'qpfMin',
    'qpfMax',
    'qsf',
    'qsfMin',
    'qsfMax',
]

def _parse_precip_qty(s):
    """convert the string to a qty,min,max tuple

    0.4       -> 0.4,0.4,0.4
    0.5-0.8   -> 0.65,0.5,0.8
    0.00-0.00 -> 0,0,0
    00-00     -> 0,0,0
    T         -> 0
    MM        -> None (indicates missing data)
    3.93700787401575e-05
    """
    if s is None or s == '':
        return None, None, None
    elif s == 'MM':
        return None, None, None
    elif s.find('T') >= 0:
        return TRACE_AMOUNT, TRACE_AMOUNT, TRACE_AMOUNT
    elif s.find('-') >= 0 and s[s.find('-') - 1] != 'e':
        try:
            [lo, hi] = s.split('-')
            xmin = float(lo)
            xmax = float(hi)
            x = (xmax + xmin) / 2
            return x, xmin, xmax
        except (ValueError, TypeError, AttributeError) as e:
            logerr("unrecognized precipitation quantity '%s': %s" % (s, e))
    else:
        try:
            x = float(s)
            xmin = x
            xmax = x
            return x, xmin, xmax
        except ValueError as e:
            logerr("unrecognized precipitation quantity '%s': %s" % (s, e))
    return None, None, None

def _create_from_histogram(histogram):
    """use the item with highest count in the histogram"""
    x = None
    cnt = 0
    for key in histogram:
        if histogram[key] > cnt:
            x = key
            cnt = histogram[key]
    return x


def _get_stats(key, a, b):
    try:
        s = a.get(key, None)
        if s is None:
            return
        elif type(s) == weewx.units.ValueHelper:
            x = weewx.units.convertStd(s.value_t, weewx.US)[0]
        else:
            x = float(s)
        if x is None:
            return
        if b[key] is None:
            b[key] = x
            b[key + 'N'] = 1
            b[key + 'Min'] = x
            _m = a.get(key + 'Min')
            if _m is not None:
                if type(_m) == weewx.units.ValueHelper:
                    _min = weewx.units.convertStd(_m.value_t, weewx.US).value
                else:
                    _min = float(_m)
                if _min is not None:
                    b[key + 'Min'] = min(b[key + 'Min'], _min)
            b[key + 'Max'] = x
            _m = a.get(key + 'Max')
            if _m is not None:
                if type(_m) == weewx.units.ValueHelper:
                    _max = weewx.units.convertStd(_m.value_t, weewx.US).value
                else:
                    _max = float(_m)
                if _max is not None:
                    b[key + 'Max'] = max(b[key + 'Max'], _max)
        else:
            n = b[key + 'N'] + 1
            b[key] = (b[key] * b[key + 'N'] + x) / n
            b[key + 'N'] = n
            if b[key + 'Min'] is None or x < b[key + 'Min']:
                b[key + 'Min'] = x
            _m = a.get(key + 'Min')
            if _m is not None:
                if type(_m) == weewx.units.ValueHelper:
                    _min = weewx.units.convertStd(_m.value_t, weewx.US).value
                else:
                    _min = float(_m)
                if _min is not None:
                    b[key + 'Min'] = min(b[key + 'Min'], _min)
            if b[key + 'Max'] is None or x > b[key + 'Max']:
                b[key + 'Max'] = x
            _m = a.get(key + 'Max')
            if _m is not None:
                if type(_m) == weewx.units.ValueHelper:
                    _max = weewx.units.convertStd(_m.value_t, weewx.US).value
                else:
                    _max = float(_m)
                if _max is not None:
                    b[key + 'Max'] = max(b[key + 'Max'], _max)
    except (ValueError, TypeError) as e:
        logdbg("_get_stats: %s" % e)
        weeutil.logger.log_traceback(log.error, "    ****  ")

def _get_sum(key, a, b):
    y = b.get(key, None)
    try:
        s = a.get(key, None)
        if s is not None:
            if type(s) == weewx.units.ValueHelper:
                x = weewx.units.convertStd(s.value_t, weewx.US)[0]
            else:
                x = float(s)
            if y is not None and x is not None:
                return y + x
            if x is not None:
                return x
    except (ValueError, TypeError) as e:
        logdbg("_get_sum: %s" % e)
        weeutil.logger.log_traceback(log.error, "    ****  ")
    return y

def _get_min(key, a, b):
    try:
        s = a.get(key, None)
        if s is not None:
            if type(s) == weewx.units.ValueHelper:
                x = weewx.units.convertStd(s.value_t, weewx.US)[0]
                if x is None:
                    return b.get(key, None)
            else:
                x = float(s)
            if b.get(key, None) is None or x < b[key]:
                return x
    except (ValueError, TypeError) as e:
        logdbg("_get_min: %s" % e)
        weeutil.logger.log_traceback(log.error, "    ****  ")
    return b.get(key, None)

def _get_max(key, a, b):
    try:
        s = a.get(key, None)
        if s is not None:
            if type(s) == weewx.units.ValueHelper:
                x = weewx.units.convertStd(s.value_t, weewx.US)[0]
                if x is None:
                    return b.get(key, None)
            else:
                x = float(s)
            if b.get(key, None) is None or x > b[key]:
                return x
    except (ValueError, TypeError) as e:
        logdbg("_get_max: %s" % e)
        weeutil.logger.log_traceback(log.error, "    ****  ")
    return b.get(key, None)


class ForecastVariables(SearchList):
    """Bind forecast variables to database records."""

    def __init__(self, generator):
        SearchList.__init__(self, generator)

        self.latitude = generator.stn_info.latitude_f
        self.longitude = generator.stn_info.longitude_f
        self.altitude = generator.stn_info.altitude_vt[0]
        self.moon_phases = generator.skin_dict.get('Almanac', {}).get('moon_phases', weeutil.Moon.moon_phases)
        self.formatter = generator.formatter
        self.converter = generator.converter

        # the 'Forecast' section of weewx.conf
        fd = generator.config_dict.get('Forecast', {})
        self.binding = fd.get('data_binding', 'forecast_binding')

        # the 'Forecast' section of skin.conf
        sd = generator.skin_dict.get('Forecast', {})
        label_dict = sd.get('Labels', {})
        self.labels = {}
        self.labels['Directions'] = dict(
            list(directions_label_dict.items()) +
            list(label_dict.get('Directions', {}).items()))
        self.labels['Tide'] = dict(
            list(tide_label_dict.items()) +
            list(label_dict.get('Tide', {}).items()))
        self.labels['Weather'] = dict(
            list(weather_label_dict.items()) +
            list(label_dict.get('Weather', {}).items()))
        self.labels['Zambretti'] = dict(
            list(zambretti_label_dict.items()) +
            list(label_dict.get('Zambretti', {}).items()))

        self.db_max_tries = 3
        self.db_retry_wait = 5 # seconds

    def get_extension_list(self, timespan, db_lookup):
        return [{'forecast': self}]

    def _getTides(self, context, from_ts=None, max_events=1):
        dbm_dict = weewx.manager.get_manager_dict_from_config(self.generator.config_dict, self.binding)
        with weewx.manager.open_manager(dbm_dict) as dbm:
            if from_ts is None:
                from_ts = int(time.time())
            sql = "select dateTime,issued_ts,event_ts,hilo,offset,usUnits,location from %s where method = 'XTide' and dateTime = (select max(dateTime) from %s where method = 'XTide') and event_ts >= %d order by event_ts asc" % (dbm.table_name, dbm.table_name, from_ts)
            if max_events is not None:
                sql += ' limit %d' % max_events
            for count in range(self.db_max_tries):
                try:
                    records = []
                    for rec in dbm.genSql(sql):
                        r = {}
                        r['dateTime'] = self._create_value(
                            context, 'dateTime', rec[0], 'group_time')
                        r['issued_ts'] = self._create_value(
                            context, 'issued_ts', rec[1], 'group_time')
                        r['event_ts'] = self._create_value(
                            context, 'event_ts', rec[2], 'group_time')
                        r['hilo'] = rec[3]
                        r['offset'] = self._create_value(
                            context, 'offset', rec[4], 'group_altitude',
                            unit_system=rec[5])
                        r['location'] = rec[6]
                        records.append(r)
                    return records
                except (IndexError, weedb.DatabaseError) as e:
                    logerr('get tides failed (attempt %d of %d): %s' %
                           ((count + 1), self.db_max_tries, e))
                    logdbg('waiting %d seconds before retry' %
                           self.db_retry_wait)
                    time.sleep(self.db_retry_wait)
        return []

    def _getRecords(self, fid, from_ts, to_ts, max_events=1):
        """get the latest requested forecast of indicated type for the
        indicated period of time, limiting to max_events records"""
        # NB: this query assumes that forecasting is deterministic, i.e., two
        # queries to a single forecast will always return the same results.
        dbm_dict = weewx.manager.get_manager_dict_from_config(self.generator.config_dict, self.binding)
        with weewx.manager.open_manager(dbm_dict) as dbm:
            sql = "select * from %s where method = '%s' and event_ts >= %d and event_ts <= %d and dateTime = (select max(dateTime) from %s where method = '%s') order by event_ts asc" % (dbm.table_name, fid, from_ts, to_ts, dbm.table_name, fid)
            if max_events is not None:
                sql += ' limit %d' % max_events
            for count in range(self.db_max_tries):
                try:
                    records = []
                    columns = dbm.connection.columnsOf(dbm.table_name)
                    for rec in dbm.genSql(sql):
                        r = {}
                        for i, f in enumerate(columns):
                            r[f] = rec[i]
                        records.append(r)
                    return records
                except (IndexError, weedb.DatabaseError) as e:
                    logerr('get %s failed (attempt %d of %d): %s' %
                           (fid, (count + 1), self.db_max_tries, e))
                    logdbg('waiting %d seconds before retry' %
                           self.db_retry_wait)
                    time.sleep(self.db_retry_wait)
        return []

    def _create_value(self, context, label, value_str, group,
                      fid='', units=None, unit_system=weewx.US):
        """create a value with units from the specified string"""
        v = None
        try:
            if value_str in [None, 'None', '']:
                pass
            elif value_str in ['A', 'W', 'Y']:
                logdbg("ignoring value for %s: '%s' (%s:%s)" %
                       (label, value_str, fid, context))
            elif group == 'group_time':
                v = int(value_str)
            else:
                v = float(value_str)
        except ValueError as e:
            logerr("cannot create value for %s from '%s' (%s:%s): %s" %
                   (label, value_str, fid, context, e))
        if units is None:
            units = DEFAULT_UNITS[unit_system][group]
        vt = weewx.units.ValueTuple(v, units, group)
        vh = weewx.units.ValueHelper(vt, context,
                                     self.formatter, self.converter)
        return vh

    def version(self):
        return VERSION

    def label(self, module, txt):
        if module == 'NWS':  # for backward compatibility
            module = 'Weather'
        return self.labels.get(module, {}).get(txt, txt)

    def xtide(self, index, from_ts=None):
        if from_ts is None:
            from_ts = int(time.time())
        records = self._getTides('xtide', from_ts=from_ts, max_events=index + 1)
        if 0 <= index < len(records):
            return records[index]
        return {'dateTime': '', 'issued_ts': '', 'event_ts': '',
                'hilo': '', 'offset': '', 'location': ''}

    def xtides(self, from_ts=None, max_events=45, startofday=False):
        """The tide forecast returns tide events into the future from the
        indicated time using the latest tide forecast.

        from_ts - timestamp in epoch seconds.  if nothing is specified, the
                  current time is used.

        max_events - maximum number of events to return.  default to 10 days'
                     worth of tides."""
        if from_ts is None:
            from_ts = int(time.time())
        if startofday:
            from_ts = weeutil.weeutil.startOfDay(from_ts)
        records = self._getTides('xtides', from_ts=from_ts, max_events=max_events)
        return records

    def zambretti(self):
        """The zambretti forecast applies at the time at which it was created,
        and is good for about 6 hours.  So there is no difference between the
        created timestamp and event timestamp."""
        dbm_dict = weewx.manager.get_manager_dict_from_config(self.generator.config_dict, self.binding)
        with weewx.manager.open_manager(dbm_dict) as dbm:
            sql = "select dateTime,zcode from %s where method = 'Zambretti' order by dateTime desc limit 1" % dbm.table_name
            for count in range(self.db_max_tries):
                try:
                    record = dbm.getSql(sql)
                    if record is not None:
                        th = self._create_value('zambretti', 'dateTime',
                                                record[0], 'group_time')
                        code = record[1]
                        text = self.labels['Zambretti'].get(code, code)
                        return {'dateTime': th, 'issued_ts': th,
                                'event_ts': th, 'code': code, 'text': text}
                except (KeyError, weedb.DatabaseError) as e:
                    logerr('get zambretti failed (attempt %d of %d): %s' %
                           ((count + 1), self.db_max_tries, e))
                    logdbg('waiting %d seconds before retry' %
                           self.db_retry_wait)
                    time.sleep(self.db_retry_wait)
        return {'dateTime': '', 'issued_ts': '',
                'event_ts': '', 'code': '', 'text': ''}

    def weather_periods(self, fid, from_ts=None, to_ts=None, max_events=240):
        """Returns forecast records for the indicated source from the
        specified time.  For quantities that have units, create an appropriate
        ValueHelper so that units conversions can happen.

        fid - a weather forecast identifier,
              e.g., 'NWS', 'WU', 'OWM', 'UKMO', 'Aeris', 'WWO'

        from_ts - timestamp in epoch seconds.  if None specified then the
                  current time is used.

        to_ts - timestamp in epoch seconds.  if None specified then 14
                days from the from_ts is used.

        max_events - maximum number of events to return.  None is no limit.
                     default to 240 (24 hours * 10 days).
        """
        if from_ts is None:
            from_ts = int(time.time())
        if to_ts is None:
            to_ts = from_ts + 14 * 24 * 3600 # 14 days into the future
        records = self._getRecords(fid, from_ts, to_ts, max_events=max_events)
        for r in records:
            r['qpf'], r['qpfMin'], r['qpfMax'] = _parse_precip_qty(r['qpf'])
            r['qsf'], r['qsfMin'], r['qsfMax'] = _parse_precip_qty(r['qsf'])
            for f in PERIOD_FIELDS_WITH_UNITS:
                r[f] = self._create_value('weather_periods',
                                          f, r[f], UNIT_GROUPS[f],
                                          fid=fid, unit_system=r['usUnits'])
            r['precip'] = {}
            for p in precip_types:
                v = r.get(p, None)
                if v is not None:
                    r['precip'][p] = v
            # all other fields are strings
        return records

    # the 'periods' option is a weak attempt to reduce database hits when
    # the summary is used in tables.  early testing shows a reduction in
    # time to generate 'toDate' files from about 40s to about 16s on a slow
    # arm cpu for the exfoliation skin (primarily the forecast.html page).
    def weather_summary(self, fid, ts=None, periods=None):
        """Create a weather summary from periods for the day of the indicated
        timestamp.  If the timestamp is None, use the current time.

        fid - forecast identifier, e.g., 'NWS', 'XTide'

        ts - timestamp in epoch seconds during desired day
        """
        if ts is None:
            ts = int(time.time())
        from_ts = weeutil.weeutil.startOfDay(ts)
        dur = 24 * 3600 # one day
        rec = {
            'dateTime': ts,
            'usUnits': weewx.US,
            'issued_ts': None,
            'event_ts': int(from_ts),
            'duration': dur,
            'location': None,
            'clouds': None,
            'temp': None, 'tempMin': None, 'tempMax': None,
            'dewpoint': None, 'dewpointMin': None, 'dewpointMax': None,
            'humidity': None, 'humidityMin': None, 'humidityMax': None,
            'windSpeed': None, 'windSpeedMin': None, 'windSpeedMax': None,
            'windGust': None,
            'windDir': None, 'windDirs': {},
            'windChar': None, 'windChars': {},
            'pop': None,
            'qpf': None, 'qpfMin': None, 'qpfMax': None,
            'qsf': None, 'qsfMin': None, 'qsfMax': None,
            'precip': [],
            'obvis': [],
        }
        outlook_histogram = {}
        if periods is not None:
            for p in periods:
                if from_ts <= p['event_ts'].raw <= from_ts + dur:
                    if rec['location'] is None:
                        rec['location'] = p['location']
                    if rec['issued_ts'] is None:
                        rec['issued_ts'] = p['issued_ts'].raw
                    rec['usUnits'] = p['usUnits']
                    x = p['clouds']
                    if x is not None:
                        outlook_histogram[x] = outlook_histogram.get(x, 0) + 1
                    for s in ['temp', 'dewpoint', 'humidity', 'windSpeed']:
                        _get_stats(s, p, rec)
                    rec['windGust'] = _get_max('windGust', p, rec)
                    x = p['windDir']
                    if x is not None:
                        rec['windDirs'][x] = rec['windDirs'].get(x, 0) + 1
                    x = p['windChar']
                    if x is not None:
                        rec['windChars'][x] = rec['windChars'].get(x, 0) + 1
                    rec['pop'] = _get_max('pop', p, rec)
                    for s in ['qpf', 'qsf']:
                        rec[s] = _get_sum(s, p, rec)
                    for s in ['qpfMin', 'qsfMin']:
                        rec[s] = _get_min(s, p, rec)
                    for s in ['qpfMax', 'qsfMax']:
                        rec[s] = _get_max(s, p, rec)
                    for pt in p['precip']:
                        if pt not in rec['precip']:
                            rec['precip'].append(pt)
                    if p['obvis'] is not None and p['obvis'] not in rec['obvis']:
                        rec['obvis'].append(p['obvis'])
        else:
            records = self._getRecords(fid, from_ts, from_ts + dur, max_events=40)
            for r in records:
                if rec['location'] is None:
                    rec['location'] = r['location']
                if rec['issued_ts'] is None:
                    rec['issued_ts'] = r['issued_ts']
                rec['usUnits'] = r['usUnits']
                x = r['clouds']
                if x is not None:
                    outlook_histogram[x] = outlook_histogram.get(x, 0) + 1
                for s in ['temp', 'dewpoint', 'humidity', 'windSpeed']:
                    _get_stats(s, r, rec)
                rec['windGust'] = _get_max('windGust', r, rec)
                x = r['windDir']
                if x is not None:
                    rec['windDirs'][x] = rec['windDirs'].get(x, 0) + 1
                x = r['windChar']
                if x is not None:
                    rec['windChars'][x] = rec['windChars'].get(x, 0) + 1
                rec['pop'] = _get_max('pop', r, rec)
                r['qpf'], r['qpfMin'], r['qpfMax'] = _parse_precip_qty(r['qpf'])
                r['qsf'], r['qsfMin'], r['qsfMax'] = _parse_precip_qty(r['qsf'])
                for s in ['qpf', 'qsf']:
                    rec[s] = _get_sum(s, r, rec)
                for s in ['qpfMin', 'qsfMin']:
                    rec[s] = _get_min(s, r, rec)
                for s in ['qpfMax', 'qsfMax']:
                    rec[s] = _get_max(s, r, rec)
                for pt in precip_types:
                    if r.get(pt, None) is not None and pt not in rec['precip']:
                        rec['precip'].append(pt)
                if r['obvis'] is not None and r['obvis'] not in rec['obvis']:
                    rec['obvis'].append(r['obvis'])

        for f in SUMMARY_FIELDS_WITH_UNITS:
            rec[f] = self._create_value('weather_summary',
                                        f, rec[f], UNIT_GROUPS[f],
                                        fid=fid, unit_system=rec['usUnits'])
        rec['clouds'] = _create_from_histogram(outlook_histogram)
        rec['windDir'] = _create_from_histogram(rec['windDirs'])
        rec['windChar'] = _create_from_histogram(rec['windChars'])
        return rec

    # FIXME: this is more appropriately called astronomy, at least from
    #        the template point of view.
    def almanac(self, ts=None):
        """Returns the almanac object for the indicated timestamp."""
        if ts is None:
            ts = int(time.time())
        return weewx.almanac.Almanac(ts,
                                     self.latitude, self.longitude,
                                     self.altitude,
                                     moon_phases=self.moon_phases,
                                     formatter=self.formatter)


""" Forecast Plot Generator

This generator creates a set of plots of forecast data.  It can compare
different forecasts from a single source over time, different forecasts from
multiple sources over a single time period, or a combination of these.

The generator requires some basic parameters.  It copies data from the forecast
database into a new, temporary database.  Then it creates a configuration that
it feeds to the ImageGenerator to create plots.

For example, this configuration:

[ForecastPlotGenerator]
    issued_since = None   # if no issue date, use latest forecast
    source = NWS, WU      # must specify one or more forecast sources
    [[plots]]
        [[[temp_nws]]]          # compare NWS temperature forecasts
            issued_since = 1d   # use all forecasts issued in the past day
            source = NWS        # only NWS in this plot
            data_type = temp    # plot the temperatures
        [[[temp_wu]]]           # compare WU temperature forecasts
            issued_since = 1d
            source = WU
            data_type = temp
        [[[temp]]]         # compare latest NWS and WU temperature forecasts
        [[[humidity]]]     # plot latest humidity forecast from NWS
            source = NWS
    [[plot_settings]]      # these apply to all plots
        width = 1          # parameters are passed through to image generator
        plot_type = line
        aggregate_type = None
        ...

results in this temporary database:

/var/tmp/fc.sdb

with this database configuration:

[DataBindings]
    [[fc]]
        database = fc
        table_name = archive
        manager = weewx.manager.DaySummaryManager
        [[[schema]]]
            dateTime = INTEGER NOT NULL PRIMARY KEY
            usUnits = INTEGER
            interval = INTEGER NOT NULL
            temp_NWS_2016_01_30_12_00 = REAL
            temp_NWS_2016_01_30_16_00 = REAL
            temp_NWS_2016_01_30_20_00 = REAL
            temp_NWS_2016_01_31_00_00 = REAL
            humidity_NWS_2016_01_30_12_00 = REAL
            humidity_NWS_2016_01_30_16_00 = REAL
            humidity_NWS_2016_01_30_20_00 = REAL
            humidity_NWS_2016_01_31_00_00 = REAL
            temp_WU_2016_01_30_12_00 = REAL
            temp_WU_2016_01_30_16_00 = REAL
            temp_WU_2016_01_30_20_00 = REAL
            temp_WU_2016_01_31_00_00 = REAL
            humidity_WU_2016_01_30_12_00 = REAL
            humidity_WU_2016_01_30_16_00 = REAL
            humidity_WU_2016_01_30_20_00 = REAL
            humidity_WU_2016_01_31_00_00 = REAL

[Databases]
    [[fc]]
        database_name = fc.sdb
        database_type = SQLiteTMP

[DatabaseTypes]
    [[SQLiteTMP]]
        driver = weedb.sqlite
        SQLITE_ROOT = /var/tmp

and the following in-memory configuration for image generator:

[ImageGenerator]
    data_binding = fc
    width = 1
    plot_type = line
    aggregate_type = None
    ...
    time_length = X  # end of last forecast minus start of first forecast
    [[plots]]
        [[[temp_nws]]]
            [[[[NWS_2016_01_30_12_00]]]]
                data_type = temp_NWS_2016_01_30_12_00
            [[[[NWS_2016_01_30_16_00]]]]
                data_type = temp_NWS_2016_01_30_16_00
            [[[[NWS_2016_01_30_20_00]]]]
                data_type = temp_NWS_2016_01_30_20_00
            [[[[NWS_2016_01_31_00_00]]]]
                data_type = temp_NWS_2016_01_31_00_00
        [[[temp_wu]]]
            [[[[WU_2016_01_30_12_00]]]]
                data_type = temp_WU_2016_01_30_12_00
            [[[[WU_2016_01_30_16_00]]]]
                data_type = temp_WU_2016_01_30_16_00
            [[[[WU_2016_01_30_20_00]]]]
                data_type = temp_WU_2016_01_30_20_00
            [[[[WU_2016_01_31_00_00]]]]
                data_type = temp_WU_2016_01_31_00_00
        [[[temp]]]
            [[[[NWS_2016_01_30_12_00]]]]
                data_type = temp_NWS_2016_01_30_12_00
            [[[[NWS_2016_01_30_16_00]]]]
                data_type = temp_NWS_2016_01_30_16_00
            [[[[NWS_2016_01_30_20_00]]]]
                data_type = temp_NWS_2016_01_30_20_00
            [[[[NWS_2016_01_31_00_00]]]]
                data_type = temp_NWS_2016_01_31_00_00
            [[[[WU_2016_01_30_12_00]]]]
                data_type = temp_WU_2016_01_30_12_00
            [[[[WU_2016_01_30_16_00]]]]
                data_type = temp_WU_2016_01_30_16_00
            [[[[WU_2016_01_30_20_00]]]]
                data_type = temp_WU_2016_01_30_20_00
            [[[[WU_2016_01_31_00_00]]]]
                data_type = temp_WU_2016_01_31_00_00
        [[[humidity]]]
            [[[[NWS_2016_01_31_00_00]]]]
                data_type = humidity_NWS_2016_01_31_00_00
"""

class ForecastPlotGenerator(weewx.reportengine.ReportGenerator):
    """Generate plots that contain data from multiple forecasts"""

    DBFN = '/var/tmp/fpg.sdb'
    MANAGER_DICT = {
        'database': 'fpg',
        'manager': 'weewx.manager.DaySummaryManager',
        'table_name': 'archive',
        'database_dict': {
            'database_name': DBFN,
            'driver': 'weedb.sqlite'}}

    def run(self):
        fc_dict = self.skin_dict.get('ForecastPlotGenerator', {})
        formatter = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        converter = weewx.units.Converter.fromSkinDict(self.skin_dict)
        log_success = weeutil.weeutil.tobool(fc_dict.get('log_success', True))

        # for each observation we need a source and issued_since.  if specified
        # for the observation, then use it.  otherwise fallback to whatever is
        # specified for the global scope.
        now = int(time.time())
        request = dict()
        plots = fc_dict.get('plots', {})
        for p in plots:
            s = plots[p].get('source', fc_dict.get('source', []))
            if not hasattr(s, '__iter__'):
                s = [s]
            ts = weeutil.weeutil.to_int(
                plots[p].get('issued_since', fc_dict.get('issued_since')))
            if ts is not None and ts < 0:
                ts = now + ts
            request[p] = {
                'data_type': plots[p].get('data_type', p),
                'source': s,
                'issued_since': ts}
        if not request:
            loginf("generator abort: no plots requested")
            return

        # we will end up with an array of plot specs.  each plot has a name,
        # and each plot will be an array of tuples that contain
        # (label, data_type, issued_ts, source)
        min_ts = 9999999999
        max_ts = 0

        # scan the old database for the issued timestamps that we need to plot
        logdbg("scan forecast database")
        dbm_dict = weewx.manager.get_manager_dict_from_config(self.config_dict, self.config_dict['Forecast']['data_binding'])
        with weewx.manager.open_manager(src_dbm_dict) as src_dbm:
            for p in request:
                request[p]['plots'] = []
                for s in request[p]['source']:
                    # get list of issued timestamps
                    issued = []
                    if request[p]['issued_since']: # get all since this ts
                        sql = "select distinct issued_ts from archive where method='%s' and issued_ts >= %s" % (s, request[p]['issued_since'])
                    else: # just the latest one
                        sql = "select max(issued_ts) from archive where method='%s'" % s
                    logdbg("find issue dates for plot %s source %s" % (p, s))
                    for r in src_dbm.genSql(sql):
                        if r and r[0] is not None:
                            issued.append(r[0])
                    # label them and insert into the data list in each plot
                    for ts in issued:
                        tstr = time.strftime("%Y_%m_%d_%H", time.localtime(ts))
                        label = "%s_%s" % (s, tstr)
                        data_type = "%s_%s_%s" % (
                            request[p]['data_type'], s, tstr)
                        request[p]['plots'].append((label, data_type, ts, s))
                    logdbg("found %s:%s: %s" % (p, s, issued))

            try:
                os.remove(self.DBFN)
                logdbg('delete leftover temporary database %s' % self.DBFN)
            except OSError:
                pass

            # set up and create the temporary database
            logdbg("create schema for temporary database")
            dst_dbm_dict = dict(self.MANAGER_DICT)
            dst_dbm_dict['schema'] = [
                ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
                ('interval', 'INTEGER NOT NULL'),
                ('usUnits', 'INTEGER')]
            for p in request:
                for (label, data_type, issued_ts, src) in request[p]['plots']:
                    if (data_type, 'REAL') not in dst_dbm_dict['schema']:
                        dst_dbm_dict['schema'].append((data_type, 'REAL'))
            logdbg("create temporary database %s" % self.DBFN)
            with weewx.manager.open_manager(dst_dbm_dict, initialize=True) as x:
                pass

            completed = 1
            todo = 0
            for p in request:
                for (_, data_type, issued_ts, src) in request[p]['plots']:
                    todo += 1

            # insert the data
            with weewx.manager.open_manager(dst_dbm_dict) as dst_dbm:
                for p in request:
                    for (_, data_type, issued_ts, src) in request[p]['plots']:
                        sql = "select event_ts,%s from archive where issued_ts=%s and method='%s'" % (request[p]['data_type'], issued_ts, src)
                        data = []
                        logdbg("get data for %s from source %s at %s" %
                               (request[p]['data_type'], src, issued_ts))
                        for r in src_dbm.genSql(sql):
                            data.append(r)
                        interval = 0
                        logdbg("insert %d records into %s (%s of %s)" %
                               (len(data), data_type, completed, todo))
                        for (ts, v) in data:
                            if v is None:
                                v = 'NULL'
                            sql = 'update archive set %s=%s where dateTime=%s' % (data_type, v, ts)
                            dst_dbm.getSql(sql)
                            sql = "insert or ignore into archive (dateTime,usUnits,`interval`,%s) values (%s,%s,%s,%s)" % (data_type, ts, weewx.US, interval, v)
                            dst_dbm.getSql(sql)
                            interval += ts
                            if ts < min_ts:
                                min_ts = ts
                            if ts > max_ts:
                                max_ts = ts
                        completed += 1

        logdbg("set up for image generation")
        # allocate a dictionary for the image generator configuration
        cfg = dict()
        # get parameters for the image generator
        for p in fc_dict.get('plot_settings', {}):
            cfg[p] = fc_dict['plot_settings'][p]
        # create the dictionary of image specs for the image generator
        cfg['plots'] = dict()
        for p in request:
            cfg['plots'][p] = dict()
            for (label, data_type, issued_ts, source) in request[p]['plots']:
                cfg['plots'][p][label] = dict()
                cfg['plots'][p][label]['data_type'] = data_type
        img_dict = configobj.ConfigObj()
        img_dict['ImageGenerator'] = cfg
        img_dict['HTML_ROOT'] = self.config_dict['StdReport']['HTML_ROOT']
        img_dict['SKIN_ROOT'] = self.skin_dict['SKIN_ROOT']
        img_dict['skin'] = self.skin_dict['skin']
        img_dict['REPORT_NAME'] = 'ForecastPlot'
        img_dict['data_binding'] = 'fpg'
        img_dict.setdefault('chart_line_colors', ["0xc4b272", "0x7272c4", "0x72c472"])
        img_dict.setdefault('show_daynight', True)
        img_dict.setdefault('time_length', max_ts - min_ts)
        img_dict.setdefault('image_width', 1000)
        img_dict.setdefault('image_height', 400)
        img_dict.setdefault('x_label_format', "%d %b")
        img_dict.setdefault('marker_size', 5)
        img_dict.setdefault('marker_type', 'box')
        img_dict.setdefault('width', 1)
#        img_dict.setdefault('line_gap_fraction', 0.9)
        cfg_dict = dict(self.config_dict)
        cfg_dict['DataBindings'] = {
            'fpg': {
                'database': 'fpg',
                'table_name': 'archive',
                'manager': 'weewx.manager.DaySummaryManager'}}
        cfg_dict['Databases'] = {
            'fpg': {
                'database_name': 'fpg.sdb',
                'database_type': 'SQLiteTMP'}}
        cfg_dict['DatabaseTypes'] = {
            'SQLiteTMP': {
                'driver': 'weedb.sqlite',
                'SQLITE_ROOT': '/var/tmp'}}

        logdbg('run the image generator')
        g = weeutil.weeutil._get_object('weewx.imagegenerator.ImageGenerator')(
            cfg_dict, img_dict, max_ts, self.first_run, self.stn_info)
        g.run()

        logdbg('delete temporary database %s' % self.DBFN)
        os.remove(self.DBFN)


# simple interface for manual downloads and diagnostics
#
# cd /home/weewx
# PYTHONPATH=bin python bin/user/forecast.py --help
# forecast.py --method=nws --foid=box --lid=maz014
# forecast.py --method=wu --api-key=X --loc=02139
# forecast.py --method=ds --api_key=X --type=hourly
# forecast.py --method=xtide --loc=Boston
# forecast.py --action=compare --method=nws
# forecast.py --action=compare --method=nws,wu start=24*3600

if __name__ == "__main__":
    usage = """%prog [options] [--help] [--debug]"""

    import weeutil.logger

    def main():
        import optparse
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--version', dest='version', action='store_true',
                          help='display the version')
        parser.add_option('--debug', dest='debug', action='store_true',
                          help='display diagnostic information while running')
        parser.add_option("--action", dest="action", type=str, metavar="ACTION",
                          help='what to do: download, parse, compare',
                          default='download')
        parser.add_option("--method", dest="method", type=str, metavar="METHOD",
                          help="specify the forecast method, e.g., NWS, WU",
                          default='nws')
        parser.add_option("--foid", dest="foid", type=str, metavar="FOID",
                          help="specify the forecast office ID, e.g., BOX",
                          default='unspecified_foid')
        parser.add_option("--lid", dest="lid", type=str, metavar="LID",
                          help="specify the location ID, e.g., MAZ014",
                          default='unspecified_lid')
        parser.add_option("--type", dest="type", type=str, metavar="TYPE",
                          help="specify the forecast type, e.g., hourly or "
                               "daily", default='daily')
        parser.add_option("--loc", dest="loc", type=str, metavar="LOC",
                          help="specify the location")
        parser.add_option("--api-key", dest="api_key", type=str, metavar="KEY",
                          help="specify the api key")
        parser.add_option("--client-id", dest="client_id", type=str,
                          metavar="ID", help="specify the client id")
        parser.add_option("--client-secret", dest="client_secret", type=str,
                          metavar="SECRET", help="specify the client secret")
        parser.add_option("--filename", dest="filename", metavar="FILENAME",
                          help="file that contains forecast data",
                          default="forecast.txt")
        parser.add_option("--prog", metavar="XTIDE_PROGRAM",
                          help="path to xtide program",
                          default='/usr/bin/tide')
        (options, args) = parser.parse_args()

        weeutil.logger.setup('forecast', {})

        if options.version:
            print("forecast version %s" % VERSION)
            exit(0)

        if options.debug:
            weewx.debug = 1
        else:
            weewx.debug = 0

        if options.action == 'download':
            if not options.method:
                print("no method specified")
                exit(1)
            if options.method.lower() == 'nws':
                fcast = NWSDownloadForecast(options.foid)
                lines = NWSExtractLocation(fcast, options.lid)
                for line in lines:
                    print(line)
            elif options.method.lower() == 'wu':
                fcast = WUForecast.download(options.api_key, options.loc)
                print(fcast)
            elif options.method.lower() == 'owm':
                fcast = OWMForecast.download(options.api_key, options.loc)
                print(fcast)
            elif options.method.lower() == 'ukmo':
                fcast = UKMOForecast.download(options.api_key, options.loc)
                print(fcast)
            elif options.method.lower() == 'ukmet':
                fcast = AerisForecast.download(
                    options.client_id, options.client_secret, options.loc)
                print(fcast)
            elif options.method.lower() == 'aeris':
                fcast = AerisForecast.download(options.client_id, options.client_secret, options.loc)
                print(fcast)
            elif options.method.lower() == 'wwo':
                fcast = WWOForecast.download(options.api_key, options.loc)
                print(fcast)
            elif options.method.lower() == 'xtide':
                lines = XTideForecast.generate(options.loc, prog=options.prog)
                if lines is not None:
                    for line in lines:
                        print(line)
            elif options.method.lower() == 'ds':
                fcast = DSForecast.download(options.api_key, options.loc,
                                            fc_type=options.type)
                print(fcast)
            else:
                print('unsupported forecast method %s' % options.method)
        elif options.action == 'parse':
            # tide wants lines, other forecasts want a block of text
            if options.method.lower() == 'xtide':
                lines = []
                with open(options.filename, 'r') as f:
                    for line in f:
                        lines.append(line)
                records = XTideForecast.parse(lines, location=options.loc)
                print(records)
            else:
                text = ''
                with open(options.filename, 'r') as f:
                    text = f.read()
                if options.method.lower() == 'nws':
                    matrix = NWSParseForecast(text, options.lid)
                    print(matrix)
                elif options.method.lower() == 'ukmo':
                    records, msgs = UKMOForecast.parse(text,
                                                       location=options.loc)
                    print(records)
                    print(msgs)
                elif options.method.lower() == 'ds':
                    records, msgs = DSForecast.parse(text,
                                                     location=options.loc,
                                                     fc_type=options.type)
                    print(records)
                    print(msgs)
                elif options.method.lower() == 'wu':
                    records, msgs = WUForecast.parse(text,
                                                     location=options.loc)
                    print(records)
                    print(msgs)
        elif options.action == 'compare':
            pass
        else:
            print('unknown action %s' % options.action)

    main()
