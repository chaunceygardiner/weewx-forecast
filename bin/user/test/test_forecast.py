#!/usr/bin/env python
# Copyright: 2013-2020 Matthew Wall
# Copyright: 2020-2026 John A Kline (john@johnkline.com)
# License: GPLv3

"""Tests for weewx forecasting module."""

from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function
import importlib
import importlib.util
import io
import json
import math
import os
import shutil
import sys
import time
import unittest

import configobj
import weecfg.extension
import weeutil.config


import weewx
import weewx.engine as engine

import forecast

def find_tide():
    """Locate the xtide 'tide' binary for the live XTide tests, or None so the
    test skips.  Source builds land in /usr/local/bin; distro packages in
    /usr/bin."""
    return (shutil.which('tide')
            or next((p for p in ('/usr/local/bin/tide', '/usr/bin/tide')
                     if os.path.exists(p)), None))

# to run manual tests, remove the x from xtest
# parameters for manual testing:

# weather underground credentials
WU_LOCATION = '02139'
WU_API_KEY = 'INSERT_KEY_HERE'

# open weathermap credentials
OWM_LOCATION = 'Boston,us'
OWM_API_KEY = 'INSERT_KEY_HERE'

# uk met office credentials
UKMO_LOCATION = '3772'
UKMO_API_KEY = 'INSERT_KEY_HERE'

# aeris credentials
AERIS_LOCATION = '02139'
AERIS_CLIENT_ID = 'INSERT_ID_HERE'
AERIS_CLIENT_SECRET = 'INSERT_SECRET_HERE'

# wwo credentials
WWO_LOCATION = 'London'
WWO_API_KEY = 'INSERT_KEY_HERE'

# this is where to look for the unit test data files
TSTDIR = os.path.dirname(os.path.realpath(__file__))

# FIXME: these belong in a common testing library for weewx
TMPDIR = '/var/tmp/weewx_test'

def rmdir(d):
    try:
        os.rmdir(d)
    except:
        pass

def rmtree(d):
    try:
        shutil.rmtree(d)
    except:
        pass

def mkdir(d):
    try:
        os.makedirs(d)
    except:
        pass

def rmfile(name):
    try:
        os.remove(name)
    except:
        pass

def readfile(name, dir=TSTDIR):
    data = []
    fn = name if dir is None else dir + '/' + name
    with open(fn, 'r') as f:
        for line in f:
            data.append(line)
    return ''.join(data)
    
def get_tmpdir():
    return TMPDIR + '/test_forecast'

def get_testdir(name):
    return get_tmpdir() + '/' + name

# common methods to set up and tear down forecasting unit tests

def create_config(test_dir, service, skin_dir='testskin'):
    cd = configobj.ConfigObj()
    cd['debug'] = 1
    cd['WEEWX_ROOT'] = test_dir
    cd['Station'] = {
        'station_type': 'Simulator',
        'altitude': [10,'foot'],
        'latitude': 42.358,
        'longitude': -71.106}
    cd['Simulator'] = {
        'driver': 'weewx.drivers.simulator',
        'mode': 'generator'}
    cd['Engine'] = {
        'Services': {
            'archive_services' : service}}
    cd['DataBindings'] = {
        'wx_binding': {
            'database': 'wx_sqlite'},
        'forecast_binding': {
            'database': 'forecast_sqlite',
            'manager': 'weewx.manager.Manager',
            'schema': 'forecast.schema'}}
    cd['Databases'] = {
        'wx_sqlite' : {
            'root': '%(WEEWX_ROOT)s',
            'database_name': test_dir + '/weewx.sdb',
            'driver': 'weedb.sqlite'},
        'forecast_sqlite' : {
            'root': '%(WEEWX_ROOT)s',
            'database_name': test_dir + '/forecast.sdb',
            'driver': 'weedb.sqlite'}}
    cd['StdReport'] = {
        'HTML_ROOT': test_dir + '/html',
        'SKIN_ROOT': test_dir,
        'TestReport': { 'skin' : skin_dir }}
    cd['StdArchive'] = {
        'data_binding': 'wx_binding'}
    cd['Forecast'] = {
        'data_binding': 'forecast_binding',
        'single_thread': True}
    return cd

metric_unit_groups = '''
        group_altitude     = meter
        group_degree_day   = degree_C_day
        group_direction    = degree_compass
        group_moisture     = centibar
        group_percent      = percent
        group_pressure     = inHg
        group_radiation    = watt_per_meter_squared
        group_rain         = mm
        group_rainrate     = mm_per_hour
        group_speed        = km_per_hour
        group_speed2       = km_per_hour2
        group_temperature  = degree_C
        group_uv           = uv_index
        group_volt         = volt
'''

us_unit_groups = '''
        group_altitude     = foot
        group_degree_day   = degree_F_day
        group_direction    = degree_compass
        group_moisture     = centibar
        group_percent      = percent
        group_pressure     = mbar
        group_radiation    = watt_per_meter_squared
        group_rain         = inch
        group_rainrate     = inch_per_hour
        group_speed        = mile_per_hour
        group_speed2       = knot2
        group_temperature  = degree_F
        group_uv           = uv_index
        group_volt         = volt
'''

# FIXME: make weewx work without having to specify so many items in config
#   Units
#   Labels
#   archive/stats databases
skin_contents = '''
[Units]
    [[Groups]]
        GROUPS

        # The following groups are used internally and should not be changed:
        group_count        = count
        group_interval     = minute
        group_time         = unix_epoch
        group_elapsed      = second

    [[StringFormats]]
        centibar           = %.0f
        cm                 = %.2f
        cm_per_hour        = %.2f
        degree_C           = %.1f
        degree_F           = %.1f
        degree_compass     = %.0f
        foot               = %.0f
        hPa                = %.1f
        inHg               = %.3f
        inch               = %.2f
        inch_per_hour      = %.2f
        km_per_hour        = %.0f
        km_per_hour2       = %.1f
        knot               = %.0f
        knot2              = %.1f
        mbar               = %.1f
        meter              = %.0f
        meter_per_second   = %.1f
        meter_per_second2  = %.1f
        mile_per_hour      = %.1f
        mile_per_hour2     = %.1f
        mm                 = %.1f
        mmHg               = %.1f
        mm_per_hour        = %.1f
        percent            = %.0f
        uv_index           = %.1f
        volt               = %.1f
        watt_per_meter_squared = %.0f
        NONE               = "    -"

    [[Labels]]
        centibar          = " cb"
        cm                = " cm"
        cm_per_hour       = " cm/hr"
        degree_C          =   C
        degree_F          =   F
        degree_compass    =   deg
        foot              = " feet"
        hPa               = " hPa"
        inHg              = " inHg"
        inch              = " in"
        inch_per_hour     = " in/hr"
        km_per_hour       = " kph"
        km_per_hour2      = " kph"
        knot              = " knots"
        knot2             = " knots"
        mbar              = " mbar"
        meter             = " meters"
        meter_per_second  = " m/s"
        meter_per_second2 = " m/s"
        mile_per_hour     = " mph"
        mile_per_hour2    = " mph"
        mm                = " mm"
        mmHg              = " mmHg"
        mm_per_hour       = " mm/hr"
        percent           =   %
        volt              = " V"
        watt_per_meter_squared = " W/m^2"
        NONE              = ""
        
    [[TimeFormats]]
        day        = %H:%M
        week       = %H:%M on %A
        month      = %d.%m.%Y %H:%M
        year       = %d.%m.%Y %H:%M
        rainyear   = %d.%m.%Y %H:%M
        current    = %d.%m.%Y %H:%M
        ephem_day  = %H:%M
        ephem_year = %d.%m.%Y %H:%M
    [[DegreeDays]]
[Labels]
[Almanac]
    moon_phases = n,wc,fq,wg,f,wg,lq,wc
[CheetahGenerator]
    search_list = forecast.ForecastVariables
    encoding = html_entities
    [[ToDate]]
        [[[current]]]
            template = index.html.tmpl
[Generators]
    generator_list = weewx.cheetahgenerator.CheetahGenerator
'''

# generic templates for combinations of summary and period
# should work with each forecast source

PERIODS_TEMPLATE = '''<html>
  <body>
#for $f in $forecast.weather_periods('SOURCE', from_ts=TS, max_events=20)
$f.event_ts $f.duration $f.tempMin $f.temp $f.tempMax $f.humidity $f.dewpoint $f.windSpeed $f.windGust $f.windDir $f.windChar $f.pop $f.qpf $f.qpfMin $f.qpfMax $f.qsf $f.qsfMin $f.qsfMax $f.precip $f.obvis
#end for
  </body>
</html>
'''

SUMMARY_TEMPLATE = '''<html>
  <body>
#set $summary = $forecast.weather_summary('SOURCE', ts=TS)
forecast for $summary.location for the day $summary.event_ts as of $summary.issued_ts
$summary.clouds
$summary.tempMin
$summary.tempMax
$summary.temp
$summary.dewpointMin
$summary.dewpointMax
$summary.dewpoint
$summary.humidityMin
$summary.humidityMax
$summary.humidity
$summary.windSpeedMin
$summary.windSpeedMax
$summary.windSpeed
$summary.windGust
$summary.windDir
#for $d in $summary.windDirs
  $d
#end for
$summary.windChar
#for $c in $summary.windChars
  $c
#end for
$summary.pop
$summary.qpf
$summary.qpfMin
$summary.qpfMax
$summary.qsf
$summary.qsfMin
$summary.qsfMax
#for $p in $summary.precip
  $p
#end for
#for $o in $summary.obvis
  $o
#end for
  </body>
</html>
'''

SUMMARY_PERIODS_TEMPLATE = '''<html>
  <body>
#set $periods = $forecast.weather_periods('SOURCE', from_ts=TS)
#set $summary = $forecast.weather_summary('SOURCE', ts=TS, periods=$periods)
forecast for $summary.location for the day $summary.event_ts as of $summary.issued_ts
$summary.tempMin
$summary.tempMax
$summary.temp
$summary.dewpointMin
$summary.dewpointMax
$summary.dewpoint
$summary.windSpeedMin
$summary.windSpeedMax
$summary.windSpeed
  </body>
</html>
'''

TABLE_TEMPLATE = '''<html>
<body>

#set $lastday = None
#set $periods = $forecast.weather_periods('SOURCE', from_ts=TS, max_events=40)
#for $period in $periods
  #set $thisday = $period.event_ts.format('%d')
  #set $thisdate = $period.event_ts.format('%Y.%m.%d')
  #set $hourid = $thisdate + '.hours'
  #if $lastday != $thisday
    #if $lastday is not None
    END_TABLE
  END_DIV
    #end if
    #set $lastday = $thisday
    #set $summary = $forecast.weather_summary('SOURCE', $period.event_ts.raw)

  BEG_DIV id='$thisdate'
    BEG_TABLE
      $thisdate
      $summary.event_ts.format('%a') $summary.event_ts.format('%d %b %Y')
    #if $summary.clouds is not None
      #set $simg = 'forecast-icons/' + $summary.clouds + '.png'
      $simg
    #end if
      $summary.tempMax.raw $summary.tempMin.raw
      $summary.dewpointMax.raw<br/>$summary.dewpointMin.raw
      $summary.humidityMax.raw<br/>$summary.humidityMin.raw
      $summary.windSpeedMin.raw - $summary.windSpeedMax.raw $summary.windGust.raw $summary.windDir $summary.windChar
      $summary.pop
      $summary.precip
      $summary.obvis
    END_TABLE
  END_DIV

  BEG_DIV id='$hourid'
    BEG_TABLE
  #end if
  #set $hour = $period.event_ts.format('%H:%M')
      BEG_ROW
      $hour
    #if $period.clouds is not None
      #set $img = 'forecast-icons/' + $period.clouds + '.png'
      $img
    #end if
      $period.temp.raw
      $period.dewpoint.raw
      $period.humidity.raw
      $period.windSpeed.raw $period.windGust.raw $period.windDir $period.windChar
      $period.pop
  #for $k,$v in $period.precip.items()
      $forecast.label('NWS',$k): $forecast.label('NWS',$v) ($k,$v)
  #end for
      $period.obvis
      END_ROW
#end for
    END_TABLE
  END_DIV
'''

def create_skin_conf(test_dir, skin_dir='testskin', units=weewx.US):
    '''create minimal skin config file for testing'''
    groups = metric_unit_groups if units == weewx.METRIC else us_unit_groups
    contents = skin_contents.replace('GROUPS', groups)
    mkdir(test_dir + '/' + skin_dir)
    fn = test_dir + '/' + skin_dir + '/skin.conf'
    f = open(fn, 'w')
    f.write(contents)
    f.close()

def create_template(text, source, ts):
    template = text.replace('SOURCE', source)
    template = template.replace('TS', ts)
    return template


class FakeData(object):
    '''generate fake data for testing. portions copied from gen_fake_data.py'''

    start_tt = (2010,1,1,0,0,0,0,0,-1)
    stop_tt  = (2010,1,2,0,0,0,0,0,-1)
    start_ts = int(time.mktime(start_tt))
    stop_ts  = int(time.mktime(stop_tt))
    interval = 600

    @staticmethod
    def create_weather_database(config_dict,
                                start_ts=start_ts, stop_ts=stop_ts,
                                interval=interval,
                                units=weewx.US, ranges=None):
        with weewx.manager.open_manager_with_config(
                config_dict, data_binding='wx_binding',
                initialize=True) as dbm:
            dbm.addRecord(FakeData.gen_fake_data(start_ts, stop_ts, interval,
                                                 units, ranges))
            dbm.backfill_day_summary()
            
    @staticmethod
    def create_forecast_database(config_dict, records):
        with weewx.manager.open_manager_with_config(
                config_dict, data_binding='forecast_binding',
                initialize=True) as dbm:
            dbm.addRecord(records)

    @staticmethod
    def gen_fake_zambretti_data():
        ts = int(time.mktime((2013,8,22,12,0,0,0,0,-1)))
        codes = ['A', 'B', 'C', 'D', 'E', 'F', 'A', 'A', 'A']
        records = []
        for code in codes:
            record = {}
            record['method'] = 'Zambretti'
            record['usUnits'] = weewx.US
            record['dateTime'] = ts
            record['issued_ts'] = ts
            record['event_ts'] = ts
            record['zcode'] = code
            ts += 300
            records.append(record)
        return records

    @staticmethod
    def gen_fake_nws_data():
        data = readfile('FAKE_NWS_DATA')
        matrix = forecast.NWSParseForecast(data, 'MAZ014')
        records = forecast.NWSProcessForecast('BOX', 'MAZ014', matrix)
        return records

    @staticmethod
    def gen_fake_wu_data():
        # FIXME:
        pass

    @staticmethod
    def gen_fake_xtide_data():
        records = [{'hilo': 'L', 'offset': '-0.71', 'event_ts': 1377031620,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'H', 'offset': '11.56', 'event_ts': 1377054240,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'L', 'offset': '-1.35', 'event_ts': 1377077040,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'H', 'offset': '10.73', 'event_ts': 1377099480,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'L', 'offset': '-0.95', 'event_ts': 1377121260,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'H', 'offset': '11.54', 'event_ts': 1377143820,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 },
                   {'hilo': 'L', 'offset': '-1.35', 'event_ts': 1377166380,
                    'method': 'XTide', 'usUnits': 1, 'dateTime': 1377043837,
                    'issued_ts': 1377031620 }]
        return records

    @staticmethod
    def gen_fake_data(start_ts=start_ts, stop_ts=stop_ts, interval=interval,
                      units=weewx.US, ranges=None):
        if units == weewx.METRIC:
            daily_temp_range = 30.0 # C
            annual_temp_range = 60.0 # F
            avg_temp = 5.0 # F
            baro_range = 67.726
            wind_range = 16.0934 # kph
            avg_baro = 1015.9166
            rain = 0.254 # cm
        elif units == weewx.METRICWX:
            daily_temp_range = 30.0 # C
            annual_temp_range = 60.0 # F
            avg_temp = 5.0
            baro_range = 67.726
            wind_range = 4.4704 # m/s
            avg_baro = 1015.9166
            rain = 2.54 # mm
        else:
            daily_temp_range = 54.0 # F
            annual_temp_range = 108.0 # F
            avg_temp = 41.0 # F
            baro_range = 2.0
            wind_range = 15.0 # mph
            avg_baro = 30.0
            rain = 0.1 # in

        if ranges is None:
            ranges = dict()
        daily_temp_range = ranges.get('daily_temp_range', daily_temp_range)
        annual_temp_range = ranges.get('annual_temp_range', annual_temp_range)
        avg_temp = ranges.get('avg_temp', avg_temp)
        baro_range = ranges.get('baro_range', baro_range)
        wind_range = ranges.get('wind_range', wind_range)
        avg_baro = ranges.get('avg_baro', avg_baro)
        rain = ranges.get('rain', rain)
            
        # Four day weather cycle:
        weather_cycle = 3600*24.0*4
        count = 0
        for ts in range(start_ts, stop_ts+interval, interval):
            daily_phase  = (ts - start_ts) * 2.0 * math.pi / (3600*24.0)
            annual_phase = (ts - start_ts) * 2.0 * math.pi / (3600*24.0*365.0)
            weather_phase= (ts - start_ts) * 2.0 * math.pi / weather_cycle
            record = {}
            record['dateTime']  = ts
            record['usUnits']   = units
            record['interval']  = interval
            record['outTemp']   = 0.5 * (-daily_temp_range*math.sin(daily_phase) - annual_temp_range*math.cos(annual_phase)) + avg_temp
            record['barometer'] = 0.5 * baro_range*math.sin(weather_phase) + avg_baro
            record['windSpeed'] = abs(wind_range*(1.0 + math.sin(weather_phase)))
            record['windDir'] = math.degrees(weather_phase) % 360.0
            record['windGust'] = 1.2*record['windSpeed']
            record['windGustDir'] = record['windDir']
            if math.sin(weather_phase) > .95:
                record['rain'] = rain if math.sin(weather_phase) > 0.98 else 0.01
            else:
                record['rain'] = 0.0

        # Make every 71st observation (a prime number) a null. This is a
        # deterministic algorithm, so it will produce the same results every
        # time.                             
            for obs_type in [x for x in record if x not in ['dateTime', 'usUnits', 'interval']]:
                count+=1
                if count%71 == 0:
                    record[obs_type] = None
            yield record


class ForecastTest(unittest.TestCase):

    def compareLineCount(self, filename, expected):
        actual = open(filename)
        actual_lines = []
        for actual_line in actual:
            actual_lines.append(actual_line)
        actual.close()
        if len(actual_lines) != expected:
            raise AssertionError('wrong number of lines in %s: %d != %d' %
                                 (filename, len(actual_lines), expected))

    def compareContents(self, filename, expected):
        expected_lines = expected.splitlines()

        actual = open(filename)
        actual_lines = actual.read().splitlines()
        actual.close()
        if len(actual_lines) != len(expected_lines):
            raise AssertionError('wrong number of lines in %s: %d != %d' %
                                 (filename, len(actual_lines),
                                  len(expected_lines)))

        lineno = 0
        diffs = []
        for actual_line in actual_lines:
            try:
                self.assertEqual(actual_line.rstrip(),
                                 expected_lines[lineno])
            except AssertionError as e:
                diffs.append('line %d: %s' % (lineno+1, e))
            lineno += 1
        if len(diffs) > 0:
            raise AssertionError('differences found in %s:\n%s' %
                                 (filename, '\n'.join(diffs)))

    def setupTemplateTest(self, tname, module, data, tmpl, units=weewx.US):
        tdir = get_testdir(tname)
        rmtree(tdir)
        cd = create_config(tdir, module)
        FakeData.create_weather_database(cd)
        FakeData.create_forecast_database(cd, data)
        create_skin_conf(tdir, units=units)

        stn_info = weewx.station.StationInfo(**cd['Station'])
        t = weewx.reportengine.StdReportEngine(cd, stn_info)
        fn = tdir + '/testskin/index.html.tmpl'
        f = open(fn, 'w')
        f.write(tmpl)
        f.close()
        return t, tdir
          
    def runTemplateTest(self, tname, module, data, tmpl, expected_lines,
                        units=weewx.US):
        t, tdir = self.setupTemplateTest(tname, module, data, tmpl,
                                         units=units)
        t.run()
        self.compareContents(tdir + '/html/index.html', expected_lines)

    def runTemplateLineTest(self, tname, module, data, tmpl, expected_count,
                            units=weewx.US):
        t, tdir = self.setupTemplateTest(tname, module, data, tmpl,
                                         units=units)
        t.run()
        self.compareLineCount(tdir + '/html/index.html', expected_count)


    # -------------------------------------------------------------------------
    # zambretti tests
    # -------------------------------------------------------------------------

    def test_zambretti_code(self):
        """run through all of the zambretti permutations"""

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 0, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 0, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 0, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 0, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 0, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 0, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 1, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 1, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 1, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 1, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 1, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 1, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 2, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 2, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 2, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 2, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 2, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 2, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 3, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 3, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 3, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 3, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 3, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 3, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 4, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 4, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 4, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 4, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 4, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 4, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 5, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 5, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 5, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 5, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 5, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 5, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 6, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 6, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 6, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 6, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 6, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 6, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 7, 1), 'G')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 7, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 7, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 7, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 7, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 7, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 8, 1), 'G')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 8, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 8, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 8, 1), 'G')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 8, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 8, -1), 'U')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 9, 1), 'G')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 9, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 9, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 9, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 9, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 9, -1), 'U')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 10, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 10, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 10, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 10, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 10, 0), 'N')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 10, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 11, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 11, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 11, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 11, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 11, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 11, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 12, 1), 'F')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 12, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 12, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 12, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 12, 0), 'K')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 12, -1), 'R')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 13, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 13, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 13, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 13, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 13, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 13, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 14, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 14, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 14, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 14, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 14, 0), 'E')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 14, -1), 'O')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 15, 1), 'C')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 15, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 15, -1), 'H')

        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 15, 1), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 15, 0), 'B')
        self.assertEqual(forecast.ZambrettiCode(1013.0, 5, 15, -1), 'O')

    def test_zambretti_text(self):
        '''check zambretti code/text correlation'''
        self.assertEqual(forecast.ZambrettiText('A'), 'Settled fine')
        self.assertEqual(forecast.ZambrettiText('B'), 'Fine weather')
        self.assertEqual(forecast.ZambrettiText('C'), 'Becoming fine')
        self.assertEqual(forecast.ZambrettiText('D'), 'Fine, becoming less settled')
        self.assertEqual(forecast.ZambrettiText('E'), 'Fine, possible showers')
        self.assertEqual(forecast.ZambrettiText('F'), 'Fairly fine, improving')
        self.assertEqual(forecast.ZambrettiText('G'), 'Fairly fine, possible showers early')
        self.assertEqual(forecast.ZambrettiText('H'), 'Fairly fine, showery later')
        self.assertEqual(forecast.ZambrettiText('I'), 'Showery early, improving')
        self.assertEqual(forecast.ZambrettiText('J'), 'Changeable, mending')
        self.assertEqual(forecast.ZambrettiText('K'), 'Fairly fine, showers likely')
        self.assertEqual(forecast.ZambrettiText('L'), 'Rather unsettled clearing later')
        self.assertEqual(forecast.ZambrettiText('M'), 'Unsettled, probably improving')
        self.assertEqual(forecast.ZambrettiText('N'), 'Showery, bright intervals')
        self.assertEqual(forecast.ZambrettiText('O'), 'Showery, becoming less settled')
        self.assertEqual(forecast.ZambrettiText('P'), 'Changeable, some rain')
        self.assertEqual(forecast.ZambrettiText('Q'), 'Unsettled, short fine intervals')
        self.assertEqual(forecast.ZambrettiText('R'), 'Unsettled, rain later')
        self.assertEqual(forecast.ZambrettiText('S'), 'Unsettled, some rain')
        self.assertEqual(forecast.ZambrettiText('T'), 'Mostly very unsettled')
        self.assertEqual(forecast.ZambrettiText('U'), 'Occasional rain, worsening')
        self.assertEqual(forecast.ZambrettiText('V'), 'Rain at times, very unsettled')
        self.assertEqual(forecast.ZambrettiText('W'), 'Rain at frequent intervals')
        self.assertEqual(forecast.ZambrettiText('X'), 'Rain, very unsettled')
        self.assertEqual(forecast.ZambrettiText('Y'), 'Stormy, may improve')
        self.assertEqual(forecast.ZambrettiText('Z'), 'Stormy, much rain')

    def test_zambretti_generator(self):
        '''verify behavior of the zambretti forecaster'''

        tname = 'test_zambretti_generator'
        tdir = get_testdir(tname)
        rmtree(tdir)
        cd = create_config(tdir, 'forecast.ZambrettiForecast')
        eng = weewx.engine.StdEngine(cd)
        zf = forecast.ZambrettiForecast(eng, cd)

        event = weewx.Event(weewx.NEW_ARCHIVE_RECORD)
        event.record = { 'dateTime': 1409087474 } # 26 aug 2014 21:11:12 GMT

        # no database, so zambretti cannot be calculated
        record = zf.get_forecast(event)
        self.assertEqual(record, None)

        # nothing in the database, so zambretti cannot be calculated
        record = zf.get_forecast(event)
        self.assertEqual(record, None)

        # enough data for a valid forecast
        FakeData.create_weather_database(
            cd,
            start_ts=int(time.mktime((2014,8,24,0,0,0,0,0,-1))),
            stop_ts=int(time.mktime((2014,8,26,10,0,0,0,0,-1))),
            interval=600, units=weewx.US)

        # check the forecast
        ts0 = 1409087474 # 26 aug 2014 21:11:12 GMT
        ts = ts0
        event.record = { 'dateTime': ts }
        record = zf.get_forecast(event)
        self.assertEqual(record, [{'event_ts': 1409058000, 'dateTime': 1409087474, 'zcode': 'X', 'issued_ts': 1409087474, 'method': 'Zambretti', 'usUnits': 1}])
        # FIXME: this code was 'P'

        # check the forecast a few hours later (should be same forecast)
        ts = ts0 + 2*3600 # 26 aug 2014 23:11:12 GMT
        event.record = { 'dateTime': ts }
        record = zf.get_forecast(event)
        self.assertEqual(record, None)

        # test previous day forecast
        ts = ts0 - 24*3600 # 25 aug 2014 21:11:12 GMT
        event.record = { 'dateTime': ts }
        record = zf.get_forecast(event)
        self.assertEqual(record, [{'event_ts': 1408971600, 'dateTime': 1409001074, 'zcode': 'B', 'issued_ts': 1409001074, 'method': 'Zambretti', 'usUnits': 1}])
        # FIXME: this code was 'A'

        # now the pressure goes up slightly
        FakeData.create_weather_database(
            cd,
            start_ts=int(time.mktime((2014,8,26,11,0,0,0,0,-1))),
            stop_ts=int(time.mktime((2014,8,27,10,0,0,0,0,-1))),
            interval=600, units=weewx.US,
            ranges={'avg_baro': 31.0, 'baro_range': 1.0})
        ts = ts0 + 24*3600 # 27 aug 2014 21:11:12 GMT
        event.record = { 'dateTime': ts }
        record = zf.get_forecast(event)
        self.assertEqual(record, [{'event_ts': 1409144400, 'dateTime': 1409173874, 'zcode': 'A', 'issued_ts': 1409173874, 'method': 'Zambretti', 'usUnits': 1}])

        # now the pressure drops
        FakeData.create_weather_database(
            cd,
            start_ts=int(time.mktime((2014,8,27,11,0,0,0,0,-1))),
            stop_ts=int(time.mktime((2014,8,28,10,0,0,0,0,-1))),
            interval=600, units=weewx.US,
            ranges={'avg_baro': 29.0, 'baro_range': 2.0})
        ts = ts0 + 48*3600 # 28 aug 2014 21:11:12 GMT
        event.record = { 'dateTime': ts }
        record = zf.get_forecast(event)
        self.assertEqual(record, [{'event_ts': 1409230800, 'dateTime': 1409260274, 'zcode': 'B', 'issued_ts': 1409260274, 'method': 'Zambretti', 'usUnits': 1}])

    def test_zambretti_US(self):
        self.func_test_zambretti_units(weewx.US)

    def test_zambretti_METRIC(self):
        self.func_test_zambretti_units(weewx.METRIC)

    def test_zambretti_METRICWX(self):
        self.func_test_zambretti_units(weewx.METRICWX)

    def func_test_zambretti_units(self, units):
        '''ensure that zambretti works with specified unit system'''

        tname = 'test_zambretti_units'
        tdir = get_testdir(tname)
        rmtree(tdir)
        cd = create_config(tdir, 'forecast.ZambrettiForecast')
        eng = weewx.engine.StdEngine(cd)
        zf = forecast.ZambrettiForecast(eng, cd)

        event = weewx.Event(weewx.NEW_ARCHIVE_RECORD)
        event.record = { 'dateTime': 1409087474 } # 26 aug 2014 21:11:12 GMT

        FakeData.create_weather_database(
            cd,
            start_ts=int(time.mktime((2014,8,24,0,0,0,0,0,-1))),
            stop_ts=int(time.mktime((2014,8,26,10,0,0,0,0,-1))),
            interval=600, units=units)
        record = zf.get_forecast(event)
        self.assertEqual(record, [{'event_ts': 1409058000, 'dateTime': 1409087474, 'zcode': 'X', 'issued_ts': 1409087474, 'method': 'Zambretti', 'usUnits': 1}])
        # FIXME: this code was 'P'

    def test_zambretti_bogus_values(self):
        '''confirm behavior when we get bogus values'''
        self.assertEqual(forecast.ZambrettiCode(0, 0, 0, 0), 'Z')
        self.assertEqual(forecast.ZambrettiCode(None, 0, 0, 0), None)
        self.assertEqual(forecast.ZambrettiCode(1013.0, 0, 16, 0), None)
        self.assertEqual(forecast.ZambrettiCode(1013.0, 12, 0, 0), None)

    def test_zambretti_templates(self):
        self.runTemplateTest('test_zambretti_templates',
                             'forecast.ZambrettiForecast',
                             FakeData.gen_fake_zambretti_data(),
                             '''<html>
  <body>
$forecast.zambretti.dateTime
$forecast.zambretti.issued_ts
$forecast.zambretti.event_ts
$forecast.zambretti.code
$forecast.label('Zambretti', $forecast.zambretti.code)
  </body>
</html>
''',
                             '''<html>
  <body>
22-Aug-2013 12:40
22-Aug-2013 12:40
22-Aug-2013 12:40
A
Settled fine
  </body>
</html>
''')

    def test_zambretti_template_errors(self):
        t, tdir = self.setupTemplateTest('test_zambretti_template_errors',
                                         'forecast.ZambrettiForecast',
                                         [], '''<html>
  <body>
$forecast.zambretti.dateTime
$forecast.zambretti.code
  </body>
</html>
''')

        # test behavior when empty database
        t.run()
        self.compareContents(tdir + '/html/index.html', '''<html>
  <body>


  </body>
</html>
''')

        # test behavior when no database
        rmfile(tdir + '/html/index.html')
        rmfile(tdir + '/forecast.sdb')
        t.run()
        self.assertEqual(os.path.exists(tdir + '/html/index.html'), False)


    # -------------------------------------------------------------------------
    # NWS tests
    # -------------------------------------------------------------------------

    def xtest_nws_forecast(self):
        '''end-to-end test of nws forecast; inspect manually'''
        fcast = forecast.NWSDownloadForecast('BOX') # BOX, GYX
        print(fcast)
        matrix = forecast.NWSParseForecast(fcast, 'MAZ014') # MAZ014, ME027
        print(matrix)
        records = forecast.NWSProcessForecast('BOX', 'MAZ014', matrix)
        print(records)

    def xtest_nws_download(self):
        '''spit out a current text forecast from nws; inspect manually'''
        fcast = forecast.NWSDownloadForecast('GYX')
        print(fcast)
        lines = forecast.NWSExtractLocation(fcast, 'MEZ027')
        print('\n', '\n'.join(lines))

    def test_nws_date_to_ts(self):
        data = {'418 PM EDT SAT MAY 11 2013': 1368303480,
                '400 PM EDT SAT MAY 11 2013': 1368302400,
                '1200 AM EDT SAT MAY 11 2013': 1368244800,
                '1201 AM EDT SAT MAY 11 2013': 1368244860,
                '1200 PM EDT SAT MAY 11 2013': 1368288000,
                '1201 PM EDT SAT MAY 11 2013': 1368288060,
                '1100 AM EDT SAT MAY 11 2013': 1368284400,
                '418 AM EDT SAT MAY 11 2013': 1368260280,
                '400 AM EDT SAT MAY 11 2013': 1368259200,
#                '000 AM EDT SAT MAY 11 2013': 1368244800,
                '1239 PM EDT TUE SEP 3 2013': 1378226340,
                '645 AM EDT WED SEP 4 2013': 1378291500,
                }

        for x in data.keys():
            a = '%s : %d' % (x, forecast.date2ts(x))
            b = '%s : %d' % (x, data[x])
            self.assertEqual(a, b)

    def test_nws_bogus_location(self):
        data = readfile('PFM_BOS')
        matrix = forecast.NWSParseForecast(data, 'foobar')
        self.assertEqual(matrix, None)

    def test_nws_parse_multiple(self):
        data = readfile('PFM_BOS')
        matrix = forecast.NWSParseForecast(data, 'CTZ002')
        expected = {}
        expected['temp'] = [None, None, None, '68', '67', '66', '62', '59', '57', '59', '63', '69', '65', '58', '48', '43', '40', '45', '56', '61', '61', '52', '40', '44', '62', '54', '43', '49', '70', '63', '52', '56', '72', '66', '56', '60', '75', '66']
        expected['tempMin'] = [None, None, None, None, None, None, None, None, None, '55', None, None, None, None, None, None, None, '38', None, None, None, None, None, '36', None, None, None, '39', None, None, None, '48', None, None, None, '53', None, None]
        expected['tempMax'] = [None, None, None, None, None, '71', None, None, None, None, None, None, None, '69', None, None, None, None, None, None, None, '63', None, None, None, '64', None, None, None, '72', None, None, None, '74', None, None, None, '77']
        expected['qsf'] = [None, None, None, None, None, '00-00', None, None, None, '00-00', None, None, None, '00-00', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

        matrix = forecast.NWSParseForecast(data, 'RIZ004')
        expected = {}
        expected['temp'] = [None, None, None, '66', '65', '63', '60', '59', '59', '60', '64', '71', '68', '62', '52', '47', '43', '48', '57', '61', '60', '53', '43', '46', '61', '55', '45', '49', '65', '60', '52', '55', '68', '63', '56', '59', '71', '64']
        expected['tempMin'] = [None, None, None, None, None, None, None, None, None, '58', None, None, None, None, None, None, None, '42', None, None, None, None, None, '39', None, None, None, '42', None, None, None, '49', None, None, None, '53', None, None]
        expected['tempMax'] = [None, None, None, None, None, '70', None, None, None, None, None, None, None, '72', None, None, None, None, None, None, None, '62', None, None, None, '63', None, None, None, '67', None, None, None, '70', None, None, None, '72']
        expected['qsf'] = [None, None, None, None, None, '00-00', None, None, None, '00-00', None, None, None, '00-00', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_0(self):
        data = readfile('PFM_BOS_SINGLE')
        matrix = forecast.NWSParseForecast(data, 'MAZ014')
        expected = {}
        expected['ts'] = [1368262800, 1368273600, 1368284400, 1368295200, 1368306000, 1368316800, 1368327600, 1368338400, 1368349200, 1368360000, 1368370800, 1368381600, 1368392400, 1368403200, 1368414000, 1368424800, 1368435600, 1368446400, 1368457200, 1368468000, 1368478800, 1368489600, 1368511200, 1368532800, 1368554400, 1368576000, 1368597600, 1368619200, 1368640800, 1368662400, 1368684000, 1368705600, 1368727200, 1368748800, 1368770400, 1368792000, 1368813600, 1368835200]
        expected['hour'] = ['05', '08', '11', '14', '17', '20', '23', '02', '05', '08', '11', '14', '17', '20', '23', '02', '05', '08', '11', '14', '17', '20', '02', '08', '14', '20', '02', '08', '14', '20', '02', '08', '14', '20', '02', '08', '14', '20']
        expected['temp'] = [None, None, None, '69', '68', '66', '63', '61', '59', '62', '66', '68', '68', '61', '52', '47', '44', '48', '56', '60', '59', '53', '44', '47', '59', '53', '45', '49', '65', '60', '52', '55', '67', '63', '56', '59', '69', '63']
        expected['tempMin'] = [None, None, None, None, None, None, None, None, None, '57', None, None, None, None, None, None, None, '43', None, None, None, None, None, '41', None, None, None, '42', None, None, None, '49', None, None, None, '54', None, None]
        expected['tempMax'] = [None, None, None, None, None, '72', None, None, None, None, None, None, None, '69', None, None, None, None, None, None, None, '61', None, None, None, '60', None, None, None, '67', None, None, None, '68', None, None, None, '70']
        expected['qsf'] = [None, None, None, None, None, '00-00', None, None, None, '00-00', None, None, None, '00-00', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_1(self):
        # this forecast was downloaded on 25aug2013
        # it contains 100% for many rh values, which means parsing on
        # whitespace fails
        data = readfile('PFM_GYX_SINGLE_1')
        matrix = forecast.NWSParseForecast(data, 'MEZ027')
        expected = {}
        expected['humidity'] = ['48', '63', '78', '93', '100', '93', '75', '73', '78', '87', '100', '100', '100', '97', '73', '66', '71', '90', '97', '100', '100', '100', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_2(self):
        # this forecast was downloaded around 13:00 on 26aug2013
        # it has MM instead of numeric values and odd values for wind chill
        data = readfile('PFM_GYX_SINGLE_2')
        matrix = forecast.NWSParseForecast(data, 'MEZ027')
        expected = {}
        expected['humidity'] = [None, None, None, '76', '76', '90', '93', '100', '96', '97', '90', '84', '87', '93', '100', '100', '100', '97', None, '100', None, '100', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_3(self):
        # this forecast was downloaded around 19:45 on 26aug2013
        # this forecast cleared the MM values, but still contains many 100 values
        data = readfile('PFM_GYX_SINGLE_3')
        matrix = forecast.NWSParseForecast(data, 'MEZ027')
        expected = {}
        expected['humidity'] = [None, '90', '97', '100', '100', '100', '87', '79', '76', '90', '93', '96', '100', '100', '100', '100', '97', '97', '100', '100', '100', '97', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_4(self):
        data = readfile('PFM_GYX_SINGLE_4')
        matrix = forecast.NWSParseForecast(data, 'MEZ027')
        expected = {}
        expected['ts'] = [1378198800, 1378209600, 1378220400, 1378231200, 1378242000, 1378252800, 1378263600, 1378274400, 1378285200, 1378296000, 1378306800, 1378317600, 1378328400, 1378339200, 1378350000, 1378360800, 1378371600, 1378382400, 1378393200, 1378404000, 1378414800, 1378425600, 1378447200, 1378468800, 1378490400, 1378512000, 1378533600, 1378555200, 1378576800, 1378598400, 1378620000, 1378641600, 1378663200, 1378684800, 1378706400, 1378728000, 1378749600, 1378771200]
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_parse_5(self):
        # this forecast was downloaded around 13:00 on 05feb2017
        # it has leading negative double-digit values for TEMP and DEWPT
        data = readfile('PFM_BIS_170205')
        matrix = forecast.NWSParseForecast(data, 'NDZ011')
        expected = {}
        expected['temp'] = [None, None, None, '8', '13', '13', '13', '11', '10', '7', '5', '7', '7', '8', '5', '3', '1', '-1', '-3', '0', '2', '0', '-10', '-13', '-4', '-5', '-8', '-5', '11', '16', '18', '22', '33', '32', '25', '17', '21', '22']
        expected['dewpoint'] = [None, None, None, '1', '6', '7', '10', '9', '6', '3', '1', '2', '3', '2', '0', '-2', '-4', '-7', '-8', '-7', '-6', '-9', '-14', '-19', '-14', '-11', '-13', '-10', '2', '8', '14', '18', '27', '25', '17', '12', '15', '14']
        for label in expected.keys():
            self.assertEqual(matrix[label], expected[label])

    def test_nws_template_periods(self):
        data = readfile('PFM_BOS_SINGLE')
        matrix = forecast.NWSParseForecast(data, 'MAZ014')
        records = forecast.NWSProcessForecast('BOX', 'MAZ014', matrix)
        template = create_template(PERIODS_TEMPLATE, 'NWS', '1368328140')
        self.runTemplateTest('test_nws_template_periods',
                             'forecast.NWSForecast',
                             records,
                             template,
                             '''<html>
  <body>
12-May-2013 02:00 10800     - 61.0F     - 87% 57.0F 8.0 mph     - S      -     -     -     -     -     -     - {'rainshwrs': 'C', 'tstms': 'S'} PF
12-May-2013 05:00 10800     - 59.0F     - 90% 56.0F 8.0 mph     - S      -     -     -     -     -     -     - {'rainshwrs': 'L'} PF
12-May-2013 08:00 10800 57.0F 62.0F     - 81% 56.0F 10.0 mph     - SW  90% 0.14 in 0.14 in 0.14 in 0.00 in 0.00 in 0.00 in {'rainshwrs': 'L'} PF
12-May-2013 11:00 10800     - 66.0F     - 68% 55.0F 11.0 mph     - W      -     -     -     -     -     -     - {'rainshwrs': 'C', 'tstms': 'S'}
12-May-2013 14:00 10800     - 68.0F     - 51% 49.0F 16.0 mph     - W      -     -     -     -     -     -     - {'rainshwrs': 'C', 'tstms': 'S'}
12-May-2013 17:00 10800     - 68.0F     - 37% 41.0F 18.0 mph     - W      -     -     -     -     -     -     - {'rainshwrs': 'S'}
12-May-2013 20:00 10800     - 61.0F 69.0F 41% 37.0F 14.0 mph 27.0 mph W  70% 0.05 in 0.05 in 0.05 in 0.00 in 0.00 in 0.00 in {}
12-May-2013 23:00 10800     - 52.0F     - 48% 33.0F 11.0 mph     - W      -     -     -     -     -     -     - {}
13-May-2013 02:00 10800     - 47.0F     - 53% 31.0F 10.0 mph     - W      -     -     -     -     -     -     - {}
13-May-2013 05:00 10800     - 44.0F     - 55% 29.0F 8.0 mph     - W      -     -     -     -     -     -     - {}
13-May-2013 08:00 10800 43.0F 48.0F     - 47% 29.0F 12.0 mph 23.0 mph W  0% 0.00 in 0.00 in 0.00 in     -     -     - {}
13-May-2013 11:00 10800     - 56.0F     - 35% 29.0F 9.0 mph 20.0 mph W      -     -     -     -     -     -     - {}
13-May-2013 14:00 10800     - 60.0F     - 27% 26.0F 16.0 mph     - W      -     -     -     -     -     -     - {}
13-May-2013 17:00 10800     - 59.0F     - 30% 28.0F 12.0 mph 23.0 mph SW      -     -     -     -     -     -     - {}
13-May-2013 20:00 10800     - 53.0F 61.0F 35% 26.0F 9.0 mph     - W  5% 0.00 in 0.00 in 0.00 in     -     -     - {}
14-May-2013 02:00 21600     - 44.0F     -     - 35.0F     -     -       -     -     -     -     -     -     - {}
14-May-2013 08:00 21600 41.0F 47.0F     -     - 33.0F     -     - NW GN 5%     -     -     -     -     -     - {}
14-May-2013 14:00 21600     - 59.0F     -     - 29.0F     -     -       -     -     -     -     -     -     - {'rainshwrs': 'S'}
14-May-2013 20:00 21600     - 53.0F 60.0F     - 32.0F     -     - NW LT 10%     -     -     -     -     -     - {'rainshwrs': 'S'}
15-May-2013 02:00 21600     - 45.0F     -     - 33.0F     -     -       -     -     -     -     -     -     - {}
  </body>
</html>
''')

    def test_nws_template_summary(self):
        template = create_template(SUMMARY_TEMPLATE, 'NWS', '1377525600')
        self.runTemplateTest('test_nws_template_summary',
                             'forecast.NWSForecast',
                             FakeData.gen_fake_nws_data(),
                             template,
                             '''<html>
  <body>
forecast for BOX MAZ014 for the day 26-Aug-2013 00:00 as of 26-Aug-2013 07:19
OV
68.0F
81.0F
74.8F
57.0F
67.0F
63.0F
58%
81%
67%
5.0 mph
12.0 mph
9.3 mph
21.0 mph
SW
  SW
  W

50%
0.11 in
0.11 in
0.11 in
0.00 in
0.00 in
0.00 in
  rainshwrs
  tstms
  </body>
</html>
''')

    def test_nws_template_table(self):
        '''exercise the period and summary template elements'''
        template = create_template(TABLE_TEMPLATE, 'NWS', '1377525600')
        self.runTemplateLineTest('test_nws_template_table',
                                 'forecast.NWSForecast',
                                 FakeData.gen_fake_nws_data(),
                                 template,
                                 538)


    # -------------------------------------------------------------------------
    # WU tests
    # -------------------------------------------------------------------------

    def xtest_wu_download_daily(self):
        '''spit out a current text forecast from wu; inspect manually'''
        fcast = forecast.WUForecast.download(WU_API_KEY, WU_LOCATION,
                                             fc_type='forecast10day')
        print(fcast)

    def xtest_wu_download_hourly(self):
        '''spit out a text forecast from wu; inspect manually'''
        fcast = forecast.WUForecast.download(WU_API_KEY, WU_LOCATION,
                                             fc_type='hourly10day')
        print(fcast)

    def xtest_wu_parse(self):
        '''parse wu forecast and spit out records'''
        data = readfile('wu', None)
        records, msgs = forecast.WUForecast.parse(data)
        print(records)

    def xtest_wu_forecast(self):
        '''end-to-end test of wu forecast; inspect manually'''
        fcast = forecast.WUForecast.download(WU_API_KEY, WU_LOCATION,
                                             fc_type='hourly10day')
        print(fcast)
        records, msgs = forecast.WUForecast.parse(fcast)
        print(records)

    def test_wu_parse_forecast_daily(self):
        ts = 1377298279
        data = readfile('WU_BOS_DAILY')
        records,msgs = forecast.WUForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(records[0:2], [
                {'method': 'WU', 'usUnits': 1, 'dateTime': 1377298279, 'issued_ts': 1377298279, 'event_ts': 1784329200, 'hour': 19, 'duration': 43200, 'clouds': 'SC', 'tempMax': None, 'tempMin': 63.0, 'temp': 63, 'humidity': 61, 'pop': 1, 'qpf': 0.0, 'qsf': 0.0, 'windSpeed': 4.0, 'windDir': 'SW', 'heatIndex': 73.0, 'windChill': 63.0, 'uvIndex': 0.0},
                {'method': 'WU', 'usUnits': 1, 'dateTime': 1377298279, 'issued_ts': 1377298279, 'event_ts': 1784372400, 'hour': 7, 'duration': 43200, 'clouds': 'OV', 'rain': 'C', 'tstms': 'C', 'tempMax': 84.0, 'tempMin': 68.0, 'temp': 84, 'humidity': 61, 'pop': 57, 'qpf': 0.1, 'qsf': 0.0, 'windSpeed': 18.0, 'windDir': 'SSW', 'heatIndex': 85.0, 'windChill': 68.0, 'uvIndex': 7.0}
                ])

    def test_wu_bad_key(self):
        '''a bad-api-key error response yields no records (hermetic; the file
        WU_ERROR_NOKEY holds a real v3 "Invalid apiKey" body, no network).'''
        data = readfile('WU_ERROR_NOKEY')
        records, msgs = forecast.WUForecast.parse(data)
        self.assertEqual(records, [])
        self.assertTrue(len(msgs) > 0)

    def test_wu_detect_download_errors(self):
        '''ensure proper behavior when server replies with error'''
        data = readfile('WU_ERROR_NOKEY')
        records,msgs = forecast.WUForecast.parse(data)
        self.assertEqual(records, [])

    def test_wu_template_periods_daily(self):
        '''verify the period behavior'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(PERIODS_TEMPLATE, 'WU', '1784329200')
        self.runTemplateTest('test_wu_template_periods_daily',
                             'forecast.WUForecast', records, template,
                             '''<html>
  <body>
17-Jul-2026 19:00 43200 54.0F 54.0F     - 82%     - 2.0 mph     - WNW  4% 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in {}
18-Jul-2026 07:00 43200 63.0F 69.0F 69.0F 77%     - 20.0 mph     - S  66% 0.18 in 0.18 in 0.18 in 0.00 in 0.00 in 0.00 in {'rain': 'L'}
18-Jul-2026 19:00 43200 63.0F 63.0F 69.0F 96%     - 22.0 mph     - SW  68% 0.07 in 0.07 in 0.07 in 0.00 in 0.00 in 0.00 in {'rain': 'L'}
19-Jul-2026 07:00 43200 56.0F 76.0F 76.0F 57%     - 16.0 mph     - WNW  18% 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in {}
19-Jul-2026 19:00 43200 56.0F 56.0F 76.0F 68%     - 11.0 mph     - WNW  2% 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in {}
20-Jul-2026 07:00 43200 58.0F 73.0F 73.0F 59%     - 13.0 mph     - WSW  2% 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in {}
20-Jul-2026 19:00 43200 58.0F 58.0F 73.0F 84%     - 10.0 mph     - SSW  7% 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in 0.00 in {}
21-Jul-2026 07:00 43200 61.0F 71.0F 71.0F 78%     - 13.0 mph     - SSE  48% 0.02 in 0.02 in 0.02 in 0.00 in 0.00 in 0.00 in {'rain': 'C'}
21-Jul-2026 19:00 43200 61.0F 61.0F 71.0F 97%     - 13.0 mph     - SSE  83% 0.49 in 0.49 in 0.49 in 0.00 in 0.00 in 0.00 in {'rain': 'O'}
22-Jul-2026 07:00 43200 60.0F 71.0F 71.0F 88%     - 15.0 mph     - SSW  82% 0.34 in 0.34 in 0.34 in 0.00 in 0.00 in 0.00 in {'rain': 'O', 'tstms': 'C', 'hail': 'O'}
22-Jul-2026 19:00 43200 60.0F 60.0F 71.0F 92%     - 13.0 mph     - SW  52% 0.10 in 0.10 in 0.10 in 0.00 in 0.00 in 0.00 in {'rain': 'C', 'tstms': 'C'}
  </body>
</html>
''')

    def test_wu_template_summary_daily(self):
        '''verify the summary behavior'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(SUMMARY_TEMPLATE, 'WU', '1784329200')
        self.runTemplateTest('test_wu_template_summary_daily',
                             'forecast.WUForecast', records, template,
                             '''<html>
  <body>
forecast for  for the day 17-Jul-2026 00:00 as of 17-Jul-2026 19:00
SC
54.0F
54.0F
54.0F
    -
    -
    -
82%
82%
82%
2.0 mph
2.0 mph
2.0 mph
    -
WNW
  WNW

4%
0.00 in
0.00 in
0.00 in
0.00 in
0.00 in
0.00 in
  </body>
</html>
''')

    def test_wu_template_summary_daily_metric(self):
        '''verify the summary behavior'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(SUMMARY_TEMPLATE, 'WU', '1784329200')
        self.runTemplateTest('test_wu_template_summary_daily_metric',
                             'forecast.WUForecast', records, template,
                             '''<html>
  <body>
forecast for  for the day 17-Jul-2026 00:00 as of 17-Jul-2026 19:00
SC
12.2C
12.2C
12.2C
    -
    -
    -
82%
82%
82%
3 kph
3 kph
3 kph
    -
WNW
  WNW

4%
0.0 mm
0.0 mm
0.0 mm
0.0 mm
0.0 mm
0.0 mm
  </body>
</html>
''', units=weewx.METRIC)

    def test_wu_template_summary_periods_daily(self):
        '''verify the summary behavior using periods'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(SUMMARY_PERIODS_TEMPLATE,'WU','1784329200')
        self.runTemplateTest('test_wu_template_summary_periods_daily',
                             'forecast.WUForecast', records, template,
                             '''<html>
  <body>
forecast for  for the day 17-Jul-2026 00:00 as of 17-Jul-2026 19:00
54.0F
54.0F
54.0F
    -
    -
    -
2.0 mph
2.0 mph
2.0 mph
  </body>
</html>
''')

    def test_wu_template_summary_periods_daily_metric(self):
        '''verify the summary behavior using periods'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(SUMMARY_PERIODS_TEMPLATE,'WU','1784329200')
        self.runTemplateTest('test_wu_template_summary_periods_daily_metric',
                             'forecast.WUForecast', records, template,
                             '''<html>
  <body>
forecast for  for the day 17-Jul-2026 00:00 as of 17-Jul-2026 19:00
12.2C
12.2C
12.2C
    -
    -
    -
3 kph
3 kph
3 kph
  </body>
</html>
''', units=weewx.METRIC)

    def test_wu_template_table_daily(self):
        '''exercise the period and summary template elements'''
        data = readfile('WU_TENANTS_HARBOR_DAILY')
        records,msgs = forecast.WUForecast.parse(
            data, issued_ts=1784329200, now=1784329200)
        template = create_template(TABLE_TEMPLATE, 'WU', '1784329200')
        self.runTemplateLineTest('test_wu_template_table_daily',
                                 'forecast.WUForecast', records, template,
                                 242)


    # -------------------------------------------------------------------------
    # OWM tests
    # -------------------------------------------------------------------------

    def xtest_owm_download(self):
        '''download a forecast from owm; inspect manually'''
        fcast = forecast.OWMForecast.download(OWM_API_KEY, OWM_LOCATION)
        print(fcast)

    def xtest_owm_parse(self):
        '''parse owm forecast and spit out records; inspect manually'''
        data = readfile('owm', None)
        records, msgs = forecast.OWMForecast.parse(data)
        print(records)

    def xtest_owm_forecast(self):
        '''download and parse owm forecast; inspect manually'''
        fcast = forecast.OWMForecast.download(OWM_API_KEY, OWM_LOCATION)
        print(fcast)
        records, msgs = forecast.OWMForecast.parse(fcast)
        print(records)

    def test_owm_location(self):
        """be sure that the location field is parsed properly"""
        s = forecast.OWMForecast.get_location_string('Boston,us')
        self.assertEqual(s, 'q=Boston,us')
        s = forecast.OWMForecast.get_location_string('4930956')
        self.assertEqual(s, 'id=4930956')
        s = forecast.OWMForecast.get_location_string('42.543,-72.444')
        self.assertEqual(s, 'lat=42.543&lon=-72.444')

    def test_owm_bos_1(self):
        """parse an owm 5-day forecast"""
        ts = 1453669141
        data = readfile('OWM_BOS_1')
        records, msgs = forecast.OWMForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(len(records), 39)
        self.assertEqual(records[0:2], [
            {'clouds': 'SC', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453528800, 'humidity': 63, 'issued_ts': 1453669141, 'method': 'OWM', 'temp': 26.52800000000002, 'usUnits': 1, 'windDir': 'N', 'windSpeed': 4.71993496},
            {'clouds': 'FW', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453539600, 'humidity': 78, 'issued_ts': 1453669141, 'method': 'OWM', 'temp': 26.50999999999999, 'usUnits': 1, 'windDir': 'N', 'windSpeed': 6.4871144}
        ])
        # check for snow (qsf) in the forecast
        self.assertEqual(records[4:8], [
            {'clouds': 'OV', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453572000, 'humidity': 79, 'issued_ts': 1453669141, 'method': 'OWM', 'qsf': 0.0044291338582677165, 'temp': 33.60200000000003, 'usUnits': 1, 'windDir': 'NE', 'windSpeed': 10.78203152},
            {'clouds': 'OV', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453582800, 'humidity': 76, 'issued_ts': 1453669141, 'method': 'OWM', 'qsf': 0.005413385826771654, 'temp': 32.593999999999994, 'usUnits': 1, 'windDir': 'NE', 'windSpeed': 10.22279752},
            {'clouds': 'OV', 'qsf': 0.0019685039370078744, 'temp': 30.055999999999983, 'event_ts': 1453593600, 'dateTime': 1453669141, 'windDir': 'NE', 'windSpeed': 10.89387832, 'duration': 10800, 'humidity': 78, 'issued_ts': 1453669141, 'method': 'OWM', 'usUnits': 1},
            {'clouds': 'OV', 'qsf': 0.0015748031496062994, 'temp': 27.680000000000007, 'event_ts': 1453604400, 'dateTime': 1453669141, 'windDir': 'N', 'windSpeed': 10.75966216, 'duration': 10800, 'humidity': 71, 'issued_ts': 1453669141, 'method': 'OWM', 'usUnits': 1}
        ])
        # check for rain (qpf) in the forecast
        self.assertEqual(records[30:34], [
            {'clouds': 'SC', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453852800, 'humidity': 76, 'issued_ts': 1453669141, 'method': 'OWM', 'temp': 46.70960000000002, 'usUnits': 1, 'windDir': 'SW', 'windSpeed': 11.2965268},
            {'clouds': 'B2', 'dateTime': 1453669141, 'duration': 10800, 'event_ts': 1453863600, 'humidity': 84, 'issued_ts': 1453669141, 'method': 'OWM', 'qpf': 0.003149606299212599, 'temp': 45.96260000000001, 'usUnits': 1, 'windDir': 'W', 'windSpeed': 9.10432952},
            {'clouds': 'CL', 'temp': 39.668000000000006, 'event_ts': 1453874400, 'qpf': 0.0007874015748031497, 'dateTime': 1453669141, 'windDir': 'W', 'windSpeed': 8.99248272, 'duration': 10800, 'humidity': 69, 'issued_ts': 1453669141, 'method': 'OWM', 'usUnits': 1},
            {'clouds': 'FW', 'temp': 33.85759999999999, 'event_ts': 1453885200, 'dateTime': 1453669141, 'windDir': 'W', 'windSpeed': 8.18718576, 'duration': 10800, 'humidity': 67, 'issued_ts': 1453669141, 'method': 'OWM', 'usUnits': 1}
        ])


    def test_owm_bos_2(self):
        """parse a current owm 5-day forecast (OWM_BOS_2 captured 2026-07-18,
        a summer forecast: exercises rain/qpf but has no snow)."""
        ts = 1453669141
        data = readfile('OWM_BOS_2')
        records, msgs = forecast.OWMForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(len(records), 40)
        self.assertEqual(records[0:2], [
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784343600, 'duration': 10800, 'clouds': 'B2', 'temp': 67.55000000000001, 'humidity': 57, 'windSpeed': 3.04223296, 'windDir': 'S'},
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784354400, 'duration': 10800, 'clouds': 'B2', 'temp': 66.37999999999994, 'humidity': 56, 'windSpeed': 4.96599792, 'windDir': 'SW'}
        ])
        # check for rain (qpf) in the forecast
        self.assertEqual(records[31:35], [
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784678400, 'duration': 10800, 'clouds': 'OV', 'temp': 70.68199999999996, 'humidity': 85, 'windSpeed': 7.58321304, 'windDir': 'SE', 'qpf': 0.010236220472440946},
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784689200, 'duration': 10800, 'clouds': 'OV', 'temp': 68.44999999999999, 'humidity': 99, 'windSpeed': 9.46223928, 'windDir': 'E', 'qpf': 0.16929133858267717},
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784700000, 'duration': 10800, 'clouds': 'OV', 'temp': 72.13999999999993, 'humidity': 98, 'windSpeed': 13.13081432, 'windDir': 'SW', 'qpf': 0.6059055118110237},
            {'method': 'OWM', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784710800, 'duration': 10800, 'clouds': 'OV', 'temp': 71.04199999999997, 'humidity': 97, 'windSpeed': 9.283284400000001, 'windDir': 'SW', 'qpf': 0.010236220472440946}
        ])


    # -------------------------------------------------------------------------
    # UKMO tests
    # -------------------------------------------------------------------------

    def xtest_ukmo_download(self):
        '''download a forecast from ukmo; inspect manually'''
        fcast = forecast.UKMOForecast.download(UKMO_API_KEY, UKMO_LOCATION)
        print(fcast)

    def xtest_ukmo_parse(self):
        '''parse ukmo forecast and spit out records; inspect manually'''
        data = readfile('ukmo', None)
        records, msgs = forecast.UKMOForecast.parse(data)
        print(records)

    def xtest_ukmo_forecast(self):
        '''download and parse ukmo forecast; inspect manually'''
        fcast = forecast.UKMOForecast.download(UKMO_API_KEY, UKMO_LOCATION)
        print(fcast)
        records, msgs = forecast.UKMOForecast.parse(fcast)
        print(records)

    def test_ukmo_redwood_city(self):
        """parse a ukmo DataHub site-specific three-hourly forecast.
        UKMO_REDWOOD_CITY was captured 2026-07-18 from the live DataHub API for
        the local station; regenerate it (and these expected values) if the
        DataHub response format changes."""
        ts = 1453669141
        data = readfile('UKMO_REDWOOD_CITY')
        records, msgs = forecast.UKMOForecast.parse(data, now=ts)
        self.assertEqual(len(records), 57)
        self.assertEqual(records[0:2], [
            {'method': 'UKMO', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1784336400.0, 'event_ts': 1784332800.0, 'duration': 10800, 'tempMin': 65.48, 'tempMax': 67.85600000000001, 'temp': 66.668, 'humidity': 59.15, 'windSpeed': 9.10432952, 'windGust': 23.08517952, 'windDir': 'W', 'pop': 0, 'qpf': 0.0, 'qsf': 0.0, 'rain': None, 'rainshwrs': None, 'tstms': None, 'snow': None, 'snowshwrs': None, 'hail': None, 'uvIndex': 4, 'location': 'Redwood City'},
            {'method': 'UKMO', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1784336400.0, 'event_ts': 1784343600.0, 'duration': 10800, 'tempMin': 60.692, 'tempMax': 66.866, 'temp': 63.778999999999996, 'humidity': 74.58, 'windSpeed': 7.13582584, 'windGust': 19.26001896, 'windDir': 'W', 'pop': 0, 'qpf': 0.0, 'qsf': 0.0, 'rain': None, 'rainshwrs': None, 'tstms': None, 'snow': None, 'snowshwrs': None, 'hail': None, 'uvIndex': 1, 'location': 'Redwood City'}
        ])

    def test_ukmo_period_date(self):
        s = '2016-01-26Z'
        ts = forecast.UKMOForecast.pv2ts(s)
        self.assertEqual(ts, 1453766400)
        self.assertEqual(time.strftime('%Y-%m-%dZ', time.gmtime(ts)), s)

    def test_ukmo_data_date(self):
        s = '2016-01-26T19:00:00Z'
        ts = forecast.UKMOForecast.dd2ts(s)
        self.assertEqual(ts, 1453834800)
        self.assertEqual(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts)), s)


    # -------------------------------------------------------------------------
    # Aeris tests
    # -------------------------------------------------------------------------

    def xtest_aeris_download(self):
        '''download a forecast from aeris; inspect manually'''
        fcast = forecast.AerisForecast.download(
            AERIS_CLIENT_ID, AERIS_CLIENT_SECRET, AERIS_LOCATION)
        print(fcast)

    def xtest_aeris_parse(self):
        '''parse aeris forecast and spit out records; inspect manually'''
        data = readfile('aeris', None)
        records, msgs = forecast.AerisForecast.parse(data)
        print(records)

    def xtest_aeris_forecast(self):
        '''download and parse aeris forecast; inspect manually'''
        fcast = forecast.AerisForecast.download(
            AERIS_CLIENT_ID, AERIS_CLIENT_SECRET, AERIS_LOCATION)
        print(fcast)
        records, msgs = forecast.AerisForecast.parse(fcast)
        print(records)

    def test_aeris_build_url(self):
        # check an explicit url
        url = forecast.AerisForecast.build_url(
            None, None, None, None, 'http://foobar.com')
        self.assertEqual(url, 'http://foobar.com')
        # check a city,state
        url = forecast.AerisForecast.build_url(
            'id', 'secret', 'seattle,wa', '1hr', forecast.AerisForecast.DEFAULT_URL)
        self.assertEqual(url, 'http://api.aerisapi.com/forecasts/seattle,wa?client_id=id&client_secret=secret&filter=1hr')
        # check a lat/lon
        url = forecast.AerisForecast.build_url(
            'id', 'secret', '42,-70', '1hr', forecast.AerisForecast.DEFAULT_URL)
        self.assertEqual(url, 'http://api.aerisapi.com/forecasts/closest?client_id=id&client_secret=secret&p=42,-70&filter=1hr')

    def test_aeris_invalid_client(self):
        ts = 1453669141
        data = readfile('AERIS_INVALID_CLIENT')
        records, msgs = forecast.AerisForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(0, 0)
        self.assertEqual(msgs, [u'Aeris: invalid_client: The client provided is invalid.'])

    def test_aeris_02139_1(self):
        ts = 1453669141
        data = readfile('AERIS_02139_1')
        records, msgs = forecast.AerisForecast.parse(data, issued_ts=ts, now=ts)
        # AERIS_02139_1 recaptured 2026-07-18 from the live Aeris/Xweather API
        self.assertEqual(len(records), 376)
        self.assertEqual(msgs, [])
        self.assertEqual(records[0:2], [
            {'method': 'Aeris', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784343600, 'duration': 3600, 'tempMax': 70.0, 'tempMin': 70.0, 'temp': 70.0, 'pop': 0.0, 'qpf': 0.0, 'humidity': 52, 'uvIndex': 0, 'qsf': 0.0, 'dewpoint': 52.0, 'windDir': 'SW', 'windGust': 6.0, 'windSpeed': 4.0, 'clouds': 'SC'},
            {'method': 'Aeris', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784347200, 'duration': 3600, 'tempMax': 69.0, 'tempMin': 69.0, 'temp': 69.0, 'pop': 0.0, 'qpf': 0.0, 'humidity': 56, 'uvIndex': 0, 'qsf': 0.0, 'dewpoint': 53.0, 'windDir': 'SW', 'windGust': 5.0, 'windSpeed': 4.0, 'clouds': 'SC'}
        ])


    # -------------------------------------------------------------------------
    # WWO tests
    # -------------------------------------------------------------------------

    def xtest_wwo_download(self):
        '''download a forecast from wwo; inspect manually'''
        fcast = forecast.WWOForecast.download(WWO_API_KEY, WWO_LOCATION)
        print(fcast)

    def xtest_wwo_parse(self):
        '''parse wwo forecast and spit out records; inspect manually'''
        data = readfile('wwo', None)
        records, msgs = forecast.WWOForecast.parse(data)
        print(records)

    def xtest_wwo_forecast(self):
        '''download and parse wwo forecast; inspect manually'''
        fcast = forecast.WWOForecast.download(WWO_API_KEY, WWO_LOCATION)
        print(fcast)
        records, msgs = forecast.WWOForecast.parse(fcast)
        print(records)

    def test_wwo_invalid_client(self):
        ts = 1453669141
        data = readfile('WWO_KEY_ERROR')
        records, msgs = forecast.WWOForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(0, 0)
        self.assertEqual(msgs, [u"WWO: KeyError: 'XXX' is not a valid key for 'Free-Weather-API-V2'"])

    def test_wwo_london_1(self):
        ts = 1453669141
        data = readfile('WWO_LONDON_1')
        records, msgs = forecast.WWOForecast.parse(data, issued_ts=ts, now=ts)
        self.assertEqual(len(records), 40)
        self.assertEqual(msgs, [])
        self.assertEqual(records[0:2], [
            {'clouds': 'OV', 'temp': 53.0, 'dewpoint': 50.0, 'event_ts': 1453870800, 'heatIndex': 53.0, 'qpf': 0.007874015748031498, 'dateTime': 1453669141, 'windDir': u'SW', 'windSpeed': 26.0, 'windGust': 41.0, 'duration': 10800, 'humidity': 88.0, 'issued_ts': 1453669141, 'method': 'WWO', 'usUnits': 1, 'windChill': 47.0},
            {'clouds': 'OV', 'temp': 53.0, 'dewpoint': 50.0, 'event_ts': 1453881600, 'heatIndex': 53.0, 'qpf': 0.015748031496062995, 'dateTime': 1453669141, 'windDir': u'SW', 'windSpeed': 30.0, 'windGust': 45.0, 'duration': 10800, 'humidity': 88.0, 'issued_ts': 1453669141, 'method': 'WWO', 'usUnits': 1, 'windChill': 47.0}
        ])


    # -------------------------------------------------------------------------
    # Pirate Weather tests (the DS source; Pirate Weather is Dark Sky-compatible)
    # -------------------------------------------------------------------------

    def test_ds_bos_daily(self):
        """parse a Pirate Weather daily forecast (DS_BOS_DAILY captured
        2026-07-18 from the live api.pirateweather.net for Boston)."""
        ts = 1453669141
        data = readfile('DS_BOS_DAILY')
        records, msgs = forecast.DSForecast.parse(
            data, issued_ts=ts, now=ts, fc_type='daily')
        self.assertEqual(msgs, [])
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0:2], [
            {'method': 'DS', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784260800, 'hour': 0, 'duration': 86400, 'clouds': 'FW', 'tempMin': 66.11, 'tempMax': 84.11, 'temp': 75.11, 'dewpoint': 53.9, 'humidity': 49, 'pop': 0, 'qpf': 0.0, 'windSpeed': 5.99, 'windDir': 'NW', 'windGust': 10.32, 'uvIndex': 7},
            {'method': 'DS', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784347200, 'hour': 0, 'duration': 86400, 'clouds': 'B1', 'tempMin': 70.97, 'tempMax': 86.27, 'temp': 78.62, 'dewpoint': 63.66, 'humidity': 68, 'pop': 43, 'qpf': 0.6505, 'windSpeed': 9.89, 'windDir': 'SW', 'windGust': 17.34, 'uvIndex': 5}
        ])

    def test_ds_bos_hourly(self):
        """parse a Pirate Weather hourly forecast (DS_BOS_HOURLY captured
        2026-07-18 from the live api.pirateweather.net for Boston)."""
        ts = 1453669141
        data = readfile('DS_BOS_HOURLY')
        records, msgs = forecast.DSForecast.parse(
            data, issued_ts=ts, now=ts, fc_type='hourly')
        self.assertEqual(msgs, [])
        self.assertEqual(len(records), 48)
        self.assertEqual(records[0:2], [
            {'method': 'DS', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784343600, 'hour': 23, 'duration': 3600, 'clouds': 'SC', 'temp': 71.87, 'dewpoint': 54.41, 'humidity': 54, 'windSpeed': 1.34, 'windDir': 'SW', 'windGust': 2.46, 'pop': 0, 'qpf': 0.0, 'uvIndex': 0},
            {'method': 'DS', 'usUnits': 1, 'dateTime': 1453669141, 'issued_ts': 1453669141, 'event_ts': 1784347200, 'hour': 0, 'duration': 3600, 'clouds': 'SC', 'temp': 70.61, 'dewpoint': 54.95, 'humidity': 56, 'windSpeed': 1.12, 'windDir': 'W', 'windGust': 2.01, 'pop': 0, 'qpf': 0.0, 'uvIndex': 0}
        ])

    def test_ds_precip_type_routing(self):
        """precipAccumulation is total precip in inches; it must go to qpf for
        rain and to qsf only for snow (the live summer fixtures contain no
        snow, so exercise the routing directly)."""
        def period(precip_type):
            return {'time': 1784260800, 'cloudCover': 0.5,
                    'temperatureLow': 30.0, 'temperatureHigh': 34.0,
                    'dewPoint': 25.0, 'humidity': 0.9,
                    'precipProbability': 0.9, 'precipAccumulation': 1.5,
                    'precipType': precip_type, 'windSpeed': 5.0,
                    'windGust': 8.0, 'windBearing': 270, 'uvIndex': 1}
        obj = {'daily': {'data': [period('rain'), period('snow')]}}
        records, msgs = forecast.DSForecast.parse(
            json.dumps(obj), issued_ts=1, now=1, fc_type='daily')
        self.assertEqual(msgs, [])
        # rain -> qpf (in inches, no cm conversion), not qsf
        self.assertEqual(records[0]['qpf'], 1.5)
        self.assertNotIn('qsf', records[0])
        # snow -> qsf, not qpf
        self.assertEqual(records[1]['qsf'], 1.5)
        self.assertNotIn('qpf', records[1])


    # -------------------------------------------------------------------------
    # xtide tests
    #
    # xtide must be installed: apt-get install xtide
    # -------------------------------------------------------------------------

    def test_xtide(self):
        tdir = get_testdir('test_xtide')
        rmtree(tdir)

        config_dict = create_config(tdir, 'forecast.XTideForecast')
        config_dict['Forecast']['XTide'] = {}
        config_dict['Forecast']['XTide']['location'] = 'Tenants Harbor'

        # create a simulator with which to test
        e = engine.StdEngine(config_dict)
        f = forecast.XTideForecast(e, config_dict)

        # check a regular set of tides
        st = '2013-08-20 12:00'
        tt = time.strptime(st, '%Y-%m-%d %H:%M')
        sts = time.mktime(tt)
        et = '2013-08-22 12:00'
        tt = time.strptime(et, '%Y-%m-%d %H:%M')
        ets = time.mktime(tt)
        prog = find_tide()
        if prog is None:
            # xtide is not installed
            return
        lines = f.generate('Tenants Harbor', sts=sts, ets=ets, prog=prog)
        if lines is None:
            # xtide ran but produced no usable output
            return

        # Times are UTC (tide is run with -z); values reflect the harmonics
        # file installed on this host (regenerate if the harmonics change).
        expect = '''"Tenants Harbor, Maine",2013.08.20,20:44,-0.66 ft,"Low Tide"
"Tenants Harbor, Maine",2013.08.20,23:00,,"Moonrise"
"Tenants Harbor, Maine",2013.08.20,23:32,,"Sunset"
"Tenants Harbor, Maine",2013.08.21,01:45,,"Full Moon"
"Tenants Harbor, Maine",2013.08.21,03:02,11.56 ft,"High Tide"
"Tenants Harbor, Maine",2013.08.21,09:21,-1.32 ft,"Low Tide"
"Tenants Harbor, Maine",2013.08.21,09:47,,"Sunrise"
"Tenants Harbor, Maine",2013.08.21,10:28,,"Moonset"
"Tenants Harbor, Maine",2013.08.21,15:37,10.72 ft,"High Tide"
"Tenants Harbor, Maine",2013.08.21,21:39,-0.90 ft,"Low Tide"
"Tenants Harbor, Maine",2013.08.21,23:31,,"Sunset"
"Tenants Harbor, Maine",2013.08.21,23:33,,"Moonrise"
"Tenants Harbor, Maine",2013.08.22,03:56,11.55 ft,"High Tide"
"Tenants Harbor, Maine",2013.08.22,09:48,,"Sunrise"
"Tenants Harbor, Maine",2013.08.22,10:12,-1.33 ft,"Low Tide"
"Tenants Harbor, Maine",2013.08.22,11:40,,"Moonset"
'''
        self.assertEqual(''.join(lines), expect)

        # verify that records are created properly
        expect = [{'hilo': 'L', 'offset': -0.66, 'event_ts': 1377031440,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'H', 'offset': 11.56, 'event_ts': 1377054120,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'L', 'offset': -1.32, 'event_ts': 1377076860,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'H', 'offset': 10.72, 'event_ts': 1377099420,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'L', 'offset': -0.90, 'event_ts': 1377121140,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'H', 'offset': 11.55, 'event_ts': 1377143760,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' },
                  {'hilo': 'L', 'offset': -1.33, 'event_ts': 1377166320,
                   'method': 'XTide', 'usUnits': 1, 'issued_ts': 1377043837,
                   'dateTime': 1377043837, 'location': 'Tenants Harbor' }]
        records = f.parse(lines, now=1377043837, location='Tenants Harbor')
        self.assertEqual(records, expect)

    def test_xtide_nonfree(self):
        """generate() as a staticmethod for a free US station (Palo Alto)"""
        tdir = get_testdir('test_xtide_nonfree')
        rmtree(tdir)

        prog = find_tide()
        if prog is None:
            # xtide is not installed
            return
        st = '2013-08-20 12:00'
        tt = time.strptime(st, '%Y-%m-%d %H:%M')
        sts = time.mktime(tt)
        et = '2013-08-22 12:00'
        tt = time.strptime(et, '%Y-%m-%d %H:%M')
        ets = time.mktime(tt)
        lines = forecast.XTideForecast.generate('Palo Alto Yacht Harbor',
                                                sts=sts, ets=ets, prog=prog)
        if lines is None:
            # xtide ran but produced no usable output
            return

        # Times are UTC (tide is run with -z); values reflect the harmonics
        # file installed on this host (regenerate if the harmonics change).
        actual = ''.join(lines) if lines else ''
        expect = '''"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.20,20:11,7.48 ft,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,01:45,,"Full Moon"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:30,,"Moonrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:39,1.10 ft,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:53,,"Sunset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,07:41,8.85 ft,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,13:29,,"Sunrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,14:15,,"Moonset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,15:14,-0.33 ft,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,20:50,7.77 ft,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,02:52,,"Sunset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,03:07,,"Moonrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,03:30,0.89 ft,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,08:33,8.47 ft,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,13:30,,"Sunrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,15:23,,"Moonset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,15:56,-0.10 ft,"Low Tide"
'''
        self.assertEqual(actual, expect)

    def test_xtide_error_handling(self):
        tdir = get_testdir('test_xtide_error_handling')
        rmtree(tdir)

        # we need a barebones config
        config_dict = create_config(tdir, 'forecast.XTideForecast')
        config_dict['Forecast']['XTide'] = {}
        config_dict['Forecast']['XTide']['location'] = ['Bangor','North']

        # create a simulator with which to test
        e = engine.StdEngine(config_dict)
        f = forecast.XTideForecast(e, config_dict)

        # check a regular set of tides with the bogus location
        st = '2013-08-20 12:00'
        tt = time.strptime(st, '%Y-%m-%d %H:%M')
        sts = time.mktime(tt)
        et = '2013-08-22 12:00'
        tt = time.strptime(et, '%Y-%m-%d %H:%M')
        ets = time.mktime(tt)
        prog = find_tide()
        if prog is None:
            # xtide is not installed
            return
        # a bogus location makes tide error out, so generate returns None
        lines = f.generate('Bangor, North', sts=sts, ets=ets, prog=prog)
        self.assertEqual(lines, None)

    def test_xtide_templates(self):
        self.runTemplateTest('test_xtide_templates',
                             'forecast.XTideForecast',
                             FakeData.gen_fake_xtide_data(),
                             '''<html>
  <body>
$forecast.xtide(0, from_ts=1377043837).dateTime
$forecast.xtide(0, from_ts=1377043837).event_ts
$forecast.xtide(0, from_ts=1377043837).hilo
$forecast.xtide(0, from_ts=1377043837).offset

$forecast.xtide(1, from_ts=1377043837).dateTime
$forecast.xtide(1, from_ts=1377043837).event_ts
$forecast.xtide(1, from_ts=1377043837).hilo
$forecast.xtide(1, from_ts=1377043837).offset

tide forecast as of $forecast.xtide(0, from_ts=1377043837).dateTime
#for $tide in $forecast.xtides(from_ts=1377043837, max_events=4):
  $tide.hilo of $tide.offset at $tide.event_ts
#end for

tide forecast as of $forecast.xtide(0, from_ts=1377043837).dateTime.format("%Y.%m.%d %H:%M")
#for $tide in $forecast.xtides(from_ts=1377043837, max_events=4):
  $tide.hilo of $tide.offset.format("%.2f") at $tide.event_ts.format("%H:%M %A")
#end for
  </body>
</html>
''',
                             '''<html>
  <body>
20-Aug-2013 20:10
20-Aug-2013 23:04
H
12 feet

20-Aug-2013 20:10
21-Aug-2013 05:24
L
-1 feet

tide forecast as of 20-Aug-2013 20:10
  H of 12 feet at 20-Aug-2013 23:04
  L of -1 feet at 21-Aug-2013 05:24
  H of 11 feet at 21-Aug-2013 11:38
  L of -1 feet at 21-Aug-2013 17:41

tide forecast as of 2013.08.20 20:10
  H of 11.56 feet at 23:04 Tuesday
  L of -1.35 feet at 05:24 Wednesday
  H of 10.73 feet at 11:38 Wednesday
  L of -0.95 feet at 17:41 Wednesday
  </body>
</html>
''')

    def test_xtide_templates_bad_index(self):
        '''verify behavior when given a bad tide index'''
        self.runTemplateTest('test_xtide_templates_bad_index',
                             'forecast.XTideForecast',
                             FakeData.gen_fake_xtide_data(),
                             '''<html>
  <body>
$forecast.xtide(10, from_ts=1377043837).dateTime
$forecast.xtide(-1, from_ts=1377043837).dateTime
  </body>
</html>
''',
                             '''<html>
  <body>


  </body>
</html>
''')

    def test_xtide_metric(self):
        tdir = get_testdir('test_xtide')
        rmtree(tdir)

        config_dict = create_config(tdir, 'forecast.XTideForecast')
        config_dict['Forecast']['XTide'] = {}
        config_dict['Forecast']['XTide']['location'] = 'Palo Alto Yacht Harbor'

        # create a simulator with which to test
        e = engine.StdEngine(config_dict)
        f = forecast.XTideForecast(e, config_dict)

        # check a regular set of tides
        st = '2013-08-20 12:00'
        tt = time.strptime(st, '%Y-%m-%d %H:%M')
        sts = time.mktime(tt)
        et = '2013-08-22 12:00'
        tt = time.strptime(et, '%Y-%m-%d %H:%M')
        ets = time.mktime(tt)
        prog = find_tide()
        if prog is None:
            # xtide is not installed
            return
        # Palo Alto Yacht Harbor is a free US station; force metric output
        # (-u m) so this exercises parse()'s meter -> US conversion.  It is a
        # Pacific station run under the suite's Eastern TZ, so it also
        # exercises the UTC (-z) timezone handling.
        lines = f.generate('Palo Alto Yacht Harbor', sts=sts, ets=ets,
                           prog=prog, units='m')
        if lines is None:
            # xtide ran but produced no usable output
            return

        # Times are UTC (tide is run with -z); values reflect the harmonics
        # file installed on this host (regenerate if the harmonics change).
        expect = '''"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.20,20:11,2.28 m,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,01:45,,"Full Moon"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:30,,"Moonrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:39,0.33 m,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,02:53,,"Sunset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,07:41,2.70 m,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,13:29,,"Sunrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,14:15,,"Moonset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,15:14,-0.10 m,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.21,20:50,2.37 m,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,02:52,,"Sunset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,03:07,,"Moonrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,03:30,0.27 m,"Low Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,08:33,2.58 m,"High Tide"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,13:30,,"Sunrise"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,15:23,,"Moonset"
"Palo Alto Yacht Harbor, San Francisco Bay, California",2013.08.22,15:56,-0.03 m,"Low Tide"
'''
        self.assertEqual(''.join(lines), expect)

        # verify that records are created properly (metric offsets are
        # converted from meters to US feet by parse())
        expect = [{'event_ts': 1377029460, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'H', 'offset': 7.480333552885034,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377052740, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'L', 'offset': 1.0826798563386235,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377070860, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'H', 'offset': 8.858289733679646,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377098040, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'L', 'offset': -0.32808480495109804,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377118200, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'H', 'offset': 7.775609877341023,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377142200, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'L', 'offset': 0.8858289733679646,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377160380, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'H', 'offset': 8.464587967738328,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1},
                  {'event_ts': 1377186960, 'dateTime': 1377043837,
                   'location': 'Palo Alto Yacht Harbor',
                   'hilo': 'L', 'offset': -0.0984254414853294,
                   'issued_ts': 1377043837, 'method': 'XTide', 'usUnits': 1}]
        records = f.parse(lines, now=1377043837, location='Palo Alto Yacht Harbor')
        self.assertEqual(records, expect)

    # -------------------------------------------------------------------------
    # astronomy tests
    # -------------------------------------------------------------------------

    # FIXME: rename almanac to astronomy
    # FIXME: how to use the $almanac(almanac_time=xx) syntax?
    def test_astronomy(self):
        self.runTemplateTest('test_astronomy',
                             '',
                             [],
                             '''<html>
  <body>
#set $a = $forecast.almanac(ts=1325376000)
$a.sunrise
$a.sunset
$a.moon_fullness
#set $a = $forecast.almanac(ts=1325548800)
$a.sunrise
$a.sunset
$a.moon_fullness
  </body>
</html>
''',
                             '''<html>
  <body>
07:13
16:21
48
07:13
16:23
66
  </body>
</html>
''')

    def test_astronomy_iteration(self):
        self.runTemplateTest('test_astronomy_iteration',
                             '',
                             [],
                             '''<html>
  <body>
#for $x in range(0,96,12)
#set $ts = 1381536000 + $x * 3600
#set ($y,$m,$d) = time.gmtime($ts)[:3]
#set $gmstr = time.strftime('%Y.%m.%d %H:%M:%S UTC', time.gmtime($ts))
#set $a = $forecast.almanac(ts=$ts)
$ts $a.sunrise $a.sunset $gmstr
#end for
  </body>
</html>
''',
                             '''<html>
  <body>
1381536000 06:52 18:08 2013.10.12 00:00:00 UTC
1381579200 06:53 18:07 2013.10.12 12:00:00 UTC
1381622400 06:53 18:07 2013.10.13 00:00:00 UTC
1381665600 06:54 18:05 2013.10.13 12:00:00 UTC
1381708800 06:54 18:05 2013.10.14 00:00:00 UTC
1381752000 06:56 18:03 2013.10.14 12:00:00 UTC
1381795200 06:56 18:03 2013.10.15 00:00:00 UTC
1381838400 06:57 18:02 2013.10.15 12:00:00 UTC
  </body>
</html>
''')

    # FIXME: in almanac.py, line 172 should be gmtime not localtime?
    # Sun.sunRiseSet is UTC, so why pass y,m,d as localtime?
    # it is a problem whenever the timezone offset crosses midnight

    def xtest_ss(self):
        import weeutil.weeutil
        lat = 42.358
        lon = -71.106
        tsbase = 1381536000 # 00:00:00 12oct2013
        # for fri, 11oct2013 emacs says sunrise at 06:54 sunset at 18:08
        # for fri, 11oct2013 wu says sunrise at 06:52 sunset at 18:08
        for x in range(0,96,12):
            (y,m,d) = time.gmtime(tsbase+x*3600)[0:3]
            (sunrise_utc,sunset_utc) = weeutil.Sun.sunRiseSet(y,m,d,lon,lat)
            sunrise_tt = weeutil.weeutil.utc_to_local_tt(y, m, d, sunrise_utc)
            sunset_tt  = weeutil.weeutil.utc_to_local_tt(y, m, d, sunset_utc)
            sunrise_str = time.strftime("%H:%M", sunrise_tt)
            sunset_str = time.strftime("%H:%M", sunset_tt)
            print(y,m,d,sunrise_utc,sunset_utc,sunrise_str,sunset_str)
            
            (y,m,d) = time.localtime(tsbase+x*3600)[0:3]
            (sunrise_utc,sunset_utc) = weeutil.Sun.sunRiseSet(y,m,d,lon,lat)
            sunrise_tt = weeutil.weeutil.utc_to_local_tt(y, m, d, sunrise_utc)
            sunset_tt  = weeutil.weeutil.utc_to_local_tt(y, m, d, sunset_utc)
            sunrise_str = time.strftime("%H:%M", sunrise_tt)
            sunset_str = time.strftime("%H:%M", sunset_tt)
            print(y,m,d,sunrise_utc,sunset_utc,sunrise_str,sunset_str)

            print('')


    # -------------------------------------------------------------------------
    # general forecast tests
    # -------------------------------------------------------------------------

    def test_config_inheritance(self):
        tdir = get_testdir('test_config_inheritance')
        rmtree(tdir)
        config_dict = create_config(tdir, 'forecast.ZambrettiForecast')
        config_dict['Forecast']['max_age'] = 1
        e = engine.StdEngine(config_dict)
        f = forecast.ZambrettiForecast(e, config_dict)
        self.assertEqual(f.max_age, 1)

        config_dict['Forecast']['Zambretti'] = {}
        config_dict['Forecast']['Zambretti']['max_age'] = 300
        f = forecast.ZambrettiForecast(e, config_dict)
        self.assertEqual(f.max_age, 300)

    def setup_pruning_tests(self, tdir, numfc):
        config_dict = create_config(tdir, 'forecast.XTideForecast')
        config_dict['Forecast']['XTide'] = {}
        # 'Tenants Harbor' is an exact free-harmonics station that yields real
        # tide events; 'Boston' is ambiguous to xtide and returns none, which
        # made these tests degenerate (0 records, DB never grows to vacuum).
        config_dict['Forecast']['XTide']['location'] = 'Tenants Harbor'
        # point the forecaster at the actual tide binary so get_forecast()
        # produces real events
        prog = find_tide()
        if prog is not None:
            config_dict['Forecast']['XTide']['prog'] = prog
        method_id = 'XTide'
        dbm = weewx.manager.open_manager_with_config(
            config_dict, data_binding='forecast_binding',
            initialize=True)

        # create a tide forecaster and simulator with which to test
        e = engine.StdEngine(config_dict)
        f = forecast.XTideForecast(e, config_dict)
        record = {}
        record['usUnits'] = weewx.METRIC
        event = weewx.Event(weewx.NEW_ARCHIVE_RECORD)
        event.record = record
        event.record['dateTime'] = int(time.time())
        r = f.get_forecast(event)
        self.assertNotEqual(r, None)
        n = len(r)
        for _ in range(0,numfc):
            time.sleep(1)
            event.record['dateTime'] = int(time.time())
            forecast.Forecast.save_forecast(dbm, f.get_forecast(event), 'test')
        time.sleep(1)
        return (dbm, method_id, event.record['dateTime'], n)


    def test_pruning(self):
        tdir = get_testdir('test_pruning')
        rmtree(tdir)

        numfc = 4
        (dbm, m_id, ts, n) = self.setup_pruning_tests(tdir, numfc)

        # make sure the records have been saved
        records = forecast.Forecast.get_saved_forecasts(dbm, m_id)
        self.assertEqual(len(records), n*numfc)

        # there should be one remaining after a prune
        forecast.Forecast.prune_forecasts(dbm, m_id, ts)
        records = forecast.Forecast.get_saved_forecasts(dbm, m_id)
        self.assertEqual(len(records), n)

    def test_vacuuming(self):
        tdir = get_testdir('test_vacuuming')
        rmtree(tdir)
        dbfile = tdir + '/forecast.sdb'

        numfc = 10
        (dbm, m_id, ts, n) = self.setup_pruning_tests(tdir, numfc)

        # make sure the records have been saved
        records = forecast.Forecast.get_saved_forecasts(dbm, m_id)
        self.assertEqual(len(records), n*numfc)
        size1 = os.path.getsize(dbfile)

        # there should be one remaining after a prune
        forecast.Forecast.prune_forecasts(dbm, m_id, ts)
        forecast.Forecast.vacuum_database(dbm, m_id)
        records = forecast.Forecast.get_saved_forecasts(dbm, m_id)
        self.assertEqual(len(records), n)
        size2 = os.path.getsize(dbfile)

        self.assertNotEqual(size1, size2)

    # weewxd stops by raising Terminate from its SIGTERM handler, inside
    # whatever the main thread is running.  With 'single_thread = True' that
    # can be do_forecast, whose broad handler must hand Terminate back -- it
    # is a shutdown request, not a forecast failure.

    class Terminate(Exception):
        """Stands in for weewxd's Terminate, which is recognized by name
        (weewxd runs as __main__, so the real class cannot be imported)."""

    class FailingForecast(forecast.Forecast):
        """A forecaster whose download raises, with only the attributes
        do_forecast touches."""
        def __init__(self, exc):
            self.exc = exc
            self.updating = False
            self.delay = 0
            self.method_id = 'TEST'

        def get_forecast(self, event):
            raise self.exc

    def test_terminate_is_not_swallowed(self):
        fc = ForecastTest.FailingForecast(ForecastTest.Terminate())
        with self.assertRaises(ForecastTest.Terminate):
            fc.do_forecast(None)
        self.assertFalse(fc.updating)

    def test_download_failure_is_logged_not_raised(self):
        """The guard must not change handling of real failures -- and the
        handler itself must not blow up: it reports dbm_dict, which is unset
        when the failure comes from get_forecast."""
        fc = ForecastTest.FailingForecast(ValueError('download failed'))
        fc.do_forecast(None)  # must not raise
        self.assertFalse(fc.updating)


class InstallerConfigTest(unittest.TestCase):
    """install.py's configuration stanza.  It is only ever read on a fresh
    `weectl extension install`: weecfg merges it with conditional_merge,
    which fills in absent keys and never rewrites an existing weewx.conf.  A
    mistake here is therefore invisible on every station that already has the
    extension, and permanent on every station that installs it next."""

    REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))

    @classmethod
    def install_module(cls):
        """install.py, loaded as a module.  Loading it needs weecfg.extension
        imported first: that module aliases itself as 'setup' in sys.modules
        for installers written against the pre-5.0 name."""
        importlib.import_module('weecfg.extension')  # registers the alias
        spec = importlib.util.spec_from_file_location(
            'forecast_install', os.path.join(cls.REPO_DIR, 'install.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_version_is_in_lockstep(self):
        """The version lives in three places and they must agree: install.py's
        version=, VERSION in forecast.py, and [Extras] version in
        skins/forecast/skin.conf.  A release that bumps two of the three ships
        a skin reporting the wrong version, which nothing else would catch."""
        installer_version = self.install_module().ForecastInstaller()['version']
        skin = configobj.ConfigObj(
            os.path.join(self.REPO_DIR, 'skins', 'forecast', 'skin.conf'),
            encoding='utf-8', file_error=True)
        self.assertEqual(installer_version, forecast.VERSION)
        self.assertEqual(skin['Extras']['version'], forecast.VERSION)

    def test_no_section_of_the_stanza_is_empty(self):
        """Every section must keep at least one live key.  Comment an option
        out and it leaves the parsed stanza, so a section whose only option is
        commented out becomes empty -- and its comment block then attaches to
        whatever key comes next.  Where that is a SIBLING subsection, as
        [[NWS]] is to [[Zambretti]], the block is written one level out, at the
        parent's indent: a user who uncomments an assignment there sets the
        option on [Forecast], where nothing reads it, and neither weewx nor
        this extension says a word.

        The indent check in the test below cannot see that, because ConfigObj
        writes the block at exactly the indent of the key it moved to -- the
        two agree, which is the whole problem.  Emptiness is what shows it."""
        def check(section, path):
            self.assertTrue(
                section.scalars or section.sections,
                '%s has no live keys left -- every option in it is commented '
                'out, so its comments will be written against the next '
                'section instead' % path)
            for name in section.sections:
                check(section[name], '%s [%s]' % (path, name))

        stanza = self.install_module().ForecastInstaller()['config']
        for name in stanza.sections:
            check(stanza[name], '[%s]' % name)

    def test_merged_stanza_keeps_every_comment_in_its_own_section(self):
        """The whole point of writing the stanza as text is that its comments
        reach the user's weewx.conf.  Two ways they silently do not, both of
        which have shipped in other extensions:

        - conditional_merge copies a key's comments only when it ADDS the key.
          A block attached to a key the target already has is dropped
          entirely, not misplaced -- so a block left trailing after a
          section's last key, where it attaches to whatever section comes
          next, vanishes on exactly the fresh installs it was written for.
        - ConfigObj writes a comment block at the indent of the key it is
          attached to.  If that key is shallower than the block's own section,
          the block is dedented out of it, and an assignment inside the block
          then reads as an option on the wrong section.

        Neither shows up as an error, so put the stanza through the path
        weectl actually takes -- weecfg.extension._inject_config copies it
        (deep_copy for a Section, a shallow dict() on WeeWX 4.0-4.4) and
        prepends HTML_ROOT before merging, and it is those copies that can
        drop comments -- then check the output: every comment line survives,
        and each sits at the indent of the live line that follows it."""
        module = self.install_module()
        stanza = module.ForecastInstaller()['config']
        # Mirror _inject_config: copy first, then prepend_path, then merge.
        # Merging the stanza object itself would skip the two steps that carry
        # the risk.
        stanza = weeutil.config.deep_copy(stanza)
        weecfg.extension.ExtensionEngine.prepend_path(
            stanza, 'HTML_ROOT', 'public_html')
        # A REALISTIC target: one that already has the sections this stanza
        # merges into.  A virgin file cannot show the dropped-comment case,
        # because there is no pre-existing key for a block to attach to.
        target = configobj.ConfigObj(io.StringIO("""
[DataBindings]
    [[wx_binding]]
        database = archive_sqlite
[Databases]
    [[archive_sqlite]]
        database_name = weewx.sdb
[StdReport]
    HTML_ROOT = public_html
    [[SeasonsReport]]
        skin = Seasons
[Engine]
    [[Services]]
        archive_services = weewx.engine.StdArchive
"""), encoding='utf-8')
        weeutil.config.conditional_merge(target, stanza)
        buf = io.BytesIO()
        target.write(buf)
        merged = buf.getvalue().decode('utf-8').splitlines()

        def comment_lines(lines):
            return [line for line in lines if line.strip().startswith('#')]

        written = comment_lines(module.CONFIG.splitlines())
        self.assertTrue(written, 'the stanza has no comments at all')
        # Sorted, not in order: the merged file lists the sections the target
        # already had before the ones the stanza appends, so the blocks come
        # out in a different order than they are written here.
        self.assertEqual(sorted(line.strip() for line in comment_lines(merged)),
                         sorted(line.strip() for line in written),
                         'comment lines were dropped by the merge')

        def indent(line):
            return len(line) - len(line.lstrip())

        for i, line in enumerate(merged):
            if not line.strip().startswith('#'):
                continue
            following = next((nxt for nxt in merged[i + 1:]
                              if nxt.strip() and not nxt.strip().startswith('#')),
                             None)
            self.assertIsNotNone(
                following, 'comment block at the end of the file: %r' % line)
            self.assertEqual(
                indent(line), indent(following),
                'comment %r is written at indent %d but the line it is '
                'attached to, %r, is at indent %d -- move the block above a '
                'live key in its own section'
                % (line.strip(), indent(line), following.strip(),
                   indent(following)))


# use this to run individual tests while debugging
def suite(testname):
    tests = [testname]
    return unittest.TestSuite(list(map(ForecastTest, tests)))


# PYTHONPATH=.:/home/weewx/bin python test/test_forecast.py
#
# use '--test test_name' to specify a single test

if __name__ == '__main__':
    # get api_key from ~/.weewx if there are any
    cfgfn = os.path.expanduser('~') + '/.weewx'
    if os.path.exists(cfgfn):
        f = open(cfgfn)
        for line in f:
            if line.startswith('wu_api_key'):
                k,v = line.split('=')
                WU_API_KEY = v.strip()
            if line.startswith('owm_api_key'):
                k,v = line.split('=')
                OWM_API_KEY = v.strip()
            if line.startswith('ukmo_api_key'):
                k,v = line.split('=')
                UKMO_API_KEY = v.strip()
            if line.startswith('aeris_client_id'):
                k,v = line.split('=')
                AERIS_CLIENT_ID = v.strip()
            if line.startswith('aeris_client_secret'):
                k,v = line.split('=')
                AERIS_CLIENT_SECRET = v.strip()
            if line.startswith('wwo_api_key'):
                k,v = line.split('=')
                WWO_API_KEY = v.strip()
        f.close()
    # check for a single test, if not then run them all
    testname = None
    if len(sys.argv) == 3 and sys.argv[1] == '--test':
        testname = sys.argv[2]
    if testname is not None:
        unittest.TextTestRunner(verbosity=2).run(suite(testname))
    else:
        unittest.main()
