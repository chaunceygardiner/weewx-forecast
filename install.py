# installer for the forecast extension
# Copyright 2014-2020 Matthew Wall
# Copyright 2020-2026 John A Kline (john@johnkline.com)
# Distributed under the terms of the GNU Public License (GPLv3)

from io import StringIO

import configobj

from weecfg.extension import ExtensionInstaller

# Written as weewx.conf text rather than a dict so that the stanza weectl
# merges into a fresh weewx.conf arrives with its comments: ConfigObj keeps
# them, a dict has nowhere to put them.
#
# Every option here is written LIVE.  Most are names another section has to
# agree with, or placeholders the user must replace, so there is nothing a
# later release could improve by leaving them commented out.  The one
# exception is [[Zambretti]] hemisphere, which IS a pure default: it stays
# live because it is that section's only key.  Commenting it out would empty
# the section, and ConfigObj would then attach its comment block to the
# sibling [[NWS]] header, at the parent's indent -- where uncommenting the
# assignment would set hemisphere on [Forecast], which nothing reads.
#
# The other options each source accepts are listed, with their defaults, in
# the manual at
#   https://chaunceygardiner.github.io/weewx-forecast/sources.html
# Add them here only to override a default.
#
# Comments are written INSIDE their section, never above a top-level header:
# WeeWX 4.0 through 4.4 shallow-copy the installer's config and drop the
# top-level comments, while comments inside a section survive on every
# version.  A commented line is also attached to the key that FOLLOWS it, so
# each block sits directly above the live key it describes, and no block is
# left trailing after a section's last key: there it would attach to whatever
# comes next, which on a fresh install is a section the user's file already
# has -- and a comment on a key that is already present is dropped, not
# merged.
CONFIG = """
[Forecast]
    # The installer appends all nine forecast services to archive_services in
    # [Engine] [[Services]].  A source whose credentials below are still
    # placeholders logs an error naming what is missing when weewx starts and
    # then does nothing at all -- it never binds, so the error does not
    # repeat.  Remove the sources you do not use from that list if you would
    # rather not see those startup errors.
    #
    # Each source accepts more options than are set here; they are listed,
    # with their defaults, in the manual:
    # https://chaunceygardiner.github.io/weewx-forecast/sources.html
    #
    # The database in which to record forecast information, defined in the
    # 'DataBindings' and 'Databases' sections that this installer also writes.
    data_binding = forecast_binding

    [[XTide]]
        # A location the xtide 'tide' program knows; list them with 'tide -ml'.
        location = "INSERT_LOCATION_HERE (e.g., Boston)"

    [[Zambretti]]
        # Calculated from the station's own pressure trend; no credentials
        # needed.  Set to SOUTH for a southern hemisphere station.
        hemisphere = NORTH

    [[NWS]]
        # US National Weather Service location (lid) and forecast office
        # (foid) identifiers.  Find your foid, then request a point forecast
        # matrix in a browser and scan it for your lid:
        #     https://forecast.weather.gov/product.php?site=NWS&product=PFM&format=txt&issuedby=YOUR_THREE_LETTER_FOID
        # There is also a lookup at https://hads.ncep.noaa.gov/USGS/
        lid = "INSERT_LOCATION_ID_HERE (e.g., MAZ014)"
        foid = "INSERT_FORECAST_OFFICE_ID_HERE (e.g., BOX)"

    [[WU]]
        # Weather Underground API key:
        #     http://www.wunderground.com/weather/api/
        api_key = INSERT_WU_API_KEY_HERE

    [[OWM]]
        # OpenWeatherMap API key:
        #     http://openweathermap.org/appid
        api_key = INSERT_OWM_API_KEY_HERE

    [[UKMO]]
        # UK Met Office API key.  It must be a key from the Met Office
        # Datahub service; sign up there for global spot data:
        #     https://www.metoffice.gov.uk/services/data/met-office-weather-datahub
        api_key = INSERT_UKMO_API_KEY_HERE

    [[Aeris]]
        # AerisWeather: create an account, then register an app to get an ID
        # and secret key:
        #     http://www.aerisweather.com/account
        client_id = INSERT_AERIS_CLIENT_ID_HERE
        client_secret = INSERT_AERIS_CLIENT_SECRET_HERE

    [[WWO]]
        # World Weather Online API key (a free account's key works):
        #     https://www.worldweatheronline.com/weather-api/
        api_key = INSERT_WWO_API_KEY_HERE

    [[DS]]
        # Pirate Weather API key (Pirate Weather is the drop-in replacement
        # for Dark Sky).
        api_key = INSERT_DS_API_KEY_HERE

[DataBindings]
    # The binding the forecast services read and write.  It is separate from
    # the station's own wx_binding: forecasts live in their own database.
    [[forecast_binding]]
        manager = weewx.manager.Manager
        schema = user.forecast.schema
        table_name = archive
        database = forecast_sqlite

[Databases]
    # The forecast database, named by the binding above.  To keep forecasts in
    # MySQL instead, define a MySQL database here and point the binding at it.
    [[forecast_sqlite]]
        database_name = forecast.sdb
        database_type = SQLite

[StdReport]
    # The sample report, which illustrates every way this extension can
    # present a forecast.  The value below already carries this station's
    # [StdReport] HTML_ROOT, prepended at install time; edit it only to put
    # the pages somewhere else.
    #
    # The extension also ships an optional 'compare' skin, which plots
    # forecasts from several sources side by side.  It is installed but not
    # enabled; see the README for how to turn it on.
    [[forecast]]
        skin = forecast
        HTML_ROOT = forecast
"""

def loader():
    return ForecastInstaller()

class ForecastInstaller(ExtensionInstaller):
    def __init__(self):
        super(ForecastInstaller, self).__init__(
            version="5.4",
            name='forecast',
            description='Generate and display weather and tide forecasts.',
            author="Matthew Wall",
            author_email="mwall@users.sourceforge.net",
            archive_services=['user.forecast.ZambrettiForecast',
                              'user.forecast.NWSForecast',
                              'user.forecast.WUForecast',
                              'user.forecast.OWMForecast',
                              'user.forecast.UKMOForecast',
                              'user.forecast.AerisForecast',
                              'user.forecast.WWOForecast',
                              'user.forecast.DSForecast',
                              'user.forecast.XTideForecast'],
            config=configobj.ConfigObj(StringIO(CONFIG)),
            files=[('bin/user',
                    ['bin/user/forecast.py']),
                   ('skins/compare',
                    ['skins/compare/skin.conf',
                     'skins/compare/index.html.tmpl']),
                   ('skins/forecast',
                    ['skins/forecast/skin.conf',
                     'skins/forecast/forecast.css',
                     'skins/forecast/forecast-periods.html.tmpl',
                     'skins/forecast/forecast_compact.css',
                     'skins/forecast/forecast_compact.inc',
                     'skins/forecast/forecast_iconic.css',
                     'skins/forecast/forecast_iconic.inc',
                     'skins/forecast/forecast_strip.css',
                     'skins/forecast/forecast_strip.inc',
                     'skins/forecast/forecast_table.css',
                     'skins/forecast/forecast_table.inc',
                     'skins/forecast/compact.html.tmpl',
                     'skins/forecast/iconic.html.tmpl',
                     'skins/forecast/iconic-horizontal.html.tmpl',
                     'skins/forecast/index.html.tmpl',
                     'skins/forecast/multiple-strips.html.tmpl',
                     'skins/forecast/multiple-tables.html.tmpl',
                     'skins/forecast/single-strip.html.tmpl',
                     'skins/forecast/single-strip-vertical.html.tmpl',
                     'skins/forecast/single-table.html.tmpl',
                     'skins/forecast/tides.html.tmpl',
                     'skins/forecast/zambretti.html.tmpl']),
                   ('skins/forecast/icons',
                    ['skins/forecast/icons/AF.png',
                     'skins/forecast/icons/B1.png',
                     'skins/forecast/icons/B1n.png',
                     'skins/forecast/icons/B2.png',
                     'skins/forecast/icons/B2n.png',
                     'skins/forecast/icons/BD.png',
                     'skins/forecast/icons/BK.png',
                     'skins/forecast/icons/BKn.png',
                     'skins/forecast/icons/BS.png',
                     'skins/forecast/icons/CL.png',
                     'skins/forecast/icons/CLn.png',
                     'skins/forecast/icons/E.png',
                     'skins/forecast/icons/F+.png',
                     'skins/forecast/icons/F.png',
                     'skins/forecast/icons/FW.png',
                     'skins/forecast/icons/FWn.png',
                     'skins/forecast/icons/H.png',
                     'skins/forecast/icons/K.png',
                     'skins/forecast/icons/N.png',
                     'skins/forecast/icons/NE.png',
                     'skins/forecast/icons/NW.png',
                     'skins/forecast/icons/OV.png',
                     'skins/forecast/icons/OVn.png',
                     'skins/forecast/icons/PF+.png',
                     'skins/forecast/icons/PF.png',
                     'skins/forecast/icons/S.png',
                     'skins/forecast/icons/SC.png',
                     'skins/forecast/icons/SCn.png',
                     'skins/forecast/icons/SE.png',
                     'skins/forecast/icons/SW.png',
                     'skins/forecast/icons/W.png',
                     'skins/forecast/icons/blizzard.png',
                     'skins/forecast/icons/drizzle.png',
                     'skins/forecast/icons/flag-yellow.png',
                     'skins/forecast/icons/flag.png',
                     'skins/forecast/icons/flurries.png',
                     'skins/forecast/icons/frzngdrzl.png',
                     'skins/forecast/icons/frzngrain.png',
                     'skins/forecast/icons/hail.png',
                     'skins/forecast/icons/moon.png',
                     'skins/forecast/icons/moonphase.png',
                     'skins/forecast/icons/moonrise.png',
                     'skins/forecast/icons/moonriseset.png',
                     'skins/forecast/icons/moonset.png',
                     'skins/forecast/icons/pop.png',
                     'skins/forecast/icons/rain.png',
                     'skins/forecast/icons/raindrop.png',
                     'skins/forecast/icons/rainshwrs.png',
                     'skins/forecast/icons/raintorrent.png',
                     'skins/forecast/icons/sleet.png',
                     'skins/forecast/icons/snow.png',
                     'skins/forecast/icons/snowflake.png',
                     'skins/forecast/icons/snowshwrs.png',
                     'skins/forecast/icons/sprinkles.png',
                     'skins/forecast/icons/sun.png',
                     'skins/forecast/icons/sunmoon.png',
                     'skins/forecast/icons/sunrise.png',
                     'skins/forecast/icons/sunriseset.png',
                     'skins/forecast/icons/sunset.png',
                     'skins/forecast/icons/tE.png',
                     'skins/forecast/icons/tENE.png',
                     'skins/forecast/icons/tESE.png',
                     'skins/forecast/icons/tN.png',
                     'skins/forecast/icons/tNE.png',
                     'skins/forecast/icons/tNNE.png',
                     'skins/forecast/icons/tNNW.png',
                     'skins/forecast/icons/tNW.png',
                     'skins/forecast/icons/tS.png',
                     'skins/forecast/icons/tSE.png',
                     'skins/forecast/icons/tSSE.png',
                     'skins/forecast/icons/tSSW.png',
                     'skins/forecast/icons/tSW.png',
                     'skins/forecast/icons/tW.png',
                     'skins/forecast/icons/tWNW.png',
                     'skins/forecast/icons/tWSW.png',
                     'skins/forecast/icons/thermometer-blue.png',
                     'skins/forecast/icons/thermometer-dewpoint.png',
                     'skins/forecast/icons/thermometer-red.png',
                     'skins/forecast/icons/thermometer.png',
                     'skins/forecast/icons/triangle-down.png',
                     'skins/forecast/icons/triangle-right.png',
                     'skins/forecast/icons/tstms.png',
                     'skins/forecast/icons/water.png']),
                   ]
            )
