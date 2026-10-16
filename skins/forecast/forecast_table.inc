#errorCatcher Echo
#encoding UTF-8
## forecast table - Copyright 2012-2016 Matthew Wall
## Copyright 2020-2026 John A Kline (john@johnkline.com)
## $Id: forecast_table.inc 1745 2017-09-21 03:54:21Z mwall $
#set $forecast_table_version = 0.6
##
## Include this file to display forecast data.  This file uses icons from the
## forecast icon set.
##
## To override the default settings in this file, use the following syntax in
## skin.conf or weewx.conf:
##
## [forecast_table_settings]
##     source = NWS
##     num_periods = 40
##     show_sun = 1
##     show_moon = 1
##     show_tides = 1

<div class='fc_table'>

#if $varExists('forecast')

#import time
#import html
#set $t0 = time.time()

## Which forecasts should be displayed?
#set $forecast_source = 'NWS'

## How many forecast periods should be considered?
## Up to 40 for NWS, up to 240 for WU.  More periods take longer to generate.
#set $num_periods = 40

## If number of days is specified, then display up to that many days
#set $num_days = None

## Which columns should be displayed?
#set $show_legend = 1
#set $show_hourly = 0
#set $show_day = 1
#set $show_date = 1
#set $show_outlook = 1
#set $show_temp = 1
#set $show_dewpoint = 0
#set $show_humidity = 0
#set $show_wind = 1
#set $show_tides = 1
#set $show_sun = 0
#set $show_moon = 0
#set $show_pop = 1
#set $show_precip = 1
#set $show_obvis = 1

#set $local_settings = dict()

## First look for values from skin.conf or weewx.conf
#if $varExists('Extras') and $varExists('Extras.forecast_table_settings')
#for $sv in $Extras.forecast_table_settings.keys()
#set $local_settings[$sv] = $Extras.forecast_table_settings[$sv]
#end for
#end if

## Look for overrides defined by any template that includes this file
#if $varExists('forecast_table_settings')
#for $sv in $forecast_table_settings.keys()
#set $local_settings[$sv] = $forecast_table_settings[$sv]
#end for
#end if

## Now assign the values that will actually be used
#set $forecast_source = $local_settings.get('source', $forecast_source)
#set $num_periods = int($local_settings.get('num_periods', $num_periods))
#set $show_legend = int($local_settings.get('show_legend', $show_legend))
#set $show_hourly = int($local_settings.get('show_hourly', $show_hourly))
#set $show_day = int($local_settings.get('show_day', $show_day))
#set $show_date = int($local_settings.get('show_date', $show_date))
#set $show_outlook = int($local_settings.get('show_outlook', $show_outlook))
#set $show_temp = int($local_settings.get('show_temp', $show_temp))
#set $show_dewpoint = int($local_settings.get('show_dewpoint', $show_dewpoint))
#set $show_humidity = int($local_settings.get('show_humidity', $show_humidity))
#set $show_wind = int($local_settings.get('show_wind', $show_wind))
#set $show_tides = int($local_settings.get('show_tides', $show_tides))
#set $show_sun = int($local_settings.get('show_sun', $show_sun))
#set $show_moon = int($local_settings.get('show_moon', $show_moon))
#set $show_pop = int($local_settings.get('show_pop', $show_pop))
#set $show_precip = int($local_settings.get('show_precip', $show_precip))
#set $show_obvis = int($local_settings.get('show_obvis', $show_obvis))

#set $num_days = $local_settings.get('num_days', $num_days)
#if $num_days is not None
#set $num_days = int($num_days)
#end if

## Define this javascript only once
#if not $varExists('forecast_table_included')
#set global $forecast_table_included = 1
<script>
function toggle_hours(control, id) {
  elem = document.getElementById(id + '.hours');
  if(elem) {
    if(elem.style.display != 'none') {
      elem.style.display = 'none';
    } else {
      elem.style.display = 'inline';
    }
  }
}
</script>
#end if ## forecast_table_included

## Global variables for reporting the location and time.
#set $wloc = ''
#set $wts = ''

## Some forecasts return 16-points of the compass, but the icons support
## only 8-points.  This dictionary maps the 16 points to 8 points.
#set $wind_dir_dict = {'SSW':'SW','WSW':'SW','NNW':'NW','WNW':'NW','SSE':'SE','ESE':'SE','NNE':'NE','ENE':'NE'}

## Get any tide predictions
#set $tides = $forecast.xtides(startofday=True)

#set $lastday = None
## If the database has not yet been queried, do it here.
#if not $varExists('periods')
#set $periods = $forecast.weather_periods($forecast_source, max_events=$num_periods)
#end if
## If number of days was specified, then trim periods to that number of days.
#if $num_days is not None and $periods is not None and len($periods) > 0
  #set $filtered_periods = []
  #set $start_time = time.mktime(time.strptime($periods[0]['event_ts'].format("%Y.%m.%d 00:00"), '%Y.%m.%d %H:%M'))
  #set $end_time = $start_time + $num_days * 86400
  #for $p in $periods
    #if $p['event_ts'].raw < $end_time
      $filtered_periods.append($p)
    #end if
  #end for
  #set $periods = $filtered_periods
#end if


#if $show_legend and $periods is not None and len($periods) > 0
  <div class='legend'>
    <table>
      <tr>
#if $show_day or $show_date
        <td class='col-date'></td>
#end if
#if $show_outlook
        <td class='col-outlook'></td>
#end if
#if $show_temp
        <td class='col-temp'><img src='icons/thermometer-red.png' class='legend-img' alt='T' title='temperature'><br><span class='units'>$unit.label.outTemp</span></td>
#end if
#if $show_dewpoint
        <td class='col-dewpoint'><img src='icons/thermometer-dewpoint.png' class='legend-img' alt='D' title='dewpoint'><br><span class='units'>$unit.label.dewpoint</span></td>
#end if
#if $show_humidity
        <td class='col-humidity'><img src='icons/thermometer-blue.png' class='legend-img' alt='H' title='humidity'><br><span class='units'>$unit.label.outHumidity</span></td>
#end if
#if $show_wind
        <td class='col-wind' style='text-align:center'><img src='icons/flag.png' class='legend-img' alt='W' title='wind'><br><span class='units'>$unit.label.wind</span></td>
#end if
#if $show_tides and $tides is not None and len($tides) > 0
        <td class='col-tides'><img src='icons/water.png' class='legend-img' alt='tide' title='tides'><br><span class='units'>$unit.label.altitude</span></td>
#end if
#if $show_sun
        <td class='col-sun'><img src='icons/sunriseset.png' class='legend-img' alt='S' title='sun'><br></td>
#end if
#if $show_moon
#if $almanac.hasExtras
        <td class='col-moon'><img src='icons/moonriseset.png' class='legend-img' alt='M' title='moon'><br></td>
#end if
        <td class='col-moonphase'><img src='icons/moonphase.png' class='legend-img' alt='MP' title='moon phase'><br></td>
#end if
#if $show_pop
        <td class='col-pop'><img src='icons/pop.png' class='legend-img' alt='PoP' title='probability of precipitation'><br><span class='units'>$unit.label.rain</span></td>
#end if
#if $show_precip
        <td class='col-precip'></td>
#end if
#if $show_obvis
        <td class='col-obvis'></td>
#end if
      </tr>
    </table>
  </div>
#end if ## show_legend

#if len($periods) == 0
<p>No data for forecast $forecast_source</p>
#end if

#for $period in $periods
  #set $thisday = $period.event_ts.format('%d')
  #set $thisdate = $period.event_ts.format('%Y.%m.%d')
  #set $smryid = $forecast_source + '.' + $thisdate
  #set $hourid = $forecast_source + '.' + $thisdate + '.hours'
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
  #set $nextday_ts = time.mktime(time.strptime($thisdate + ' 00:00', '%Y.%m.%d %H:%M')) + 24*3600
  #if $alm.hasExtras
    #set $sunrise_ts = $alm.sunrise.raw
    #set $sunset_ts = $alm.sunset.raw
    #set $moonrise_ts = $alm.moon.rise.raw
    #set $moonset_ts = $alm.moon.set.raw
  #else
    ## no moon in non-extras almanac
    #set $sunrise_ts = $alm.sunrise.raw
    #set $sunset_ts = $alm.sunset.raw
    ## use these for weewx older than 3.2.0 where non-pyephem sunrise/sunset
    ## is not a ValueHelper so do conversions
    ##set $sunrise_ts = time.mktime(time.strptime($thisdate + ' ' + $alm.sunrise, '%Y.%m.%d %H:%M'))
    ##set $sunset_ts = time.mktime(time.strptime($thisdate + ' ' + $alm.sunset, '%Y.%m.%d %H:%M'))
  #end if
  #set $wts = $period.issued_ts

  #if $lastday != $thisday
#if $show_hourly
    #if $lastday is not None
    </table>
  </div>
    #end if
#end if
    #set $lastday = $thisday
    #set $summary = $forecast.weather_summary($forecast_source, $period.event_ts.raw, periods=$periods)
    #set $wloc = $summary.location

  <div id='$smryid' class='summary'>
    <table>
      <tr>
#if $show_day or $show_date
        <td class='col-date' onclick="toggle_hours(this, '$smryid')">
#if $show_day
          <span class='day'>$summary.event_ts.format('%a')</span><br>
#end if
#if $show_date
          <span class='date'>$summary.event_ts.format('%d %b')</span>
#end if
        </td>
#end if
#if $show_outlook
        <td class='col-outlook'>
    #if $summary.clouds is not None
      #set $simg = 'icons/' + $summary.clouds + '.png'
          <img class='outlook-img' src='$simg' alt='$summary.clouds' title='$forecast.label('Weather', $summary.clouds)'>
    #end if
        </td>
#end if
#if $show_temp
        <td class='col-temp'><span class='temphi'>$summary.tempMax.nolabel('%.0f')</span><br><span class='templo'>$summary.tempMin.nolabel('%.0f')</span></td>
#end if
#if $show_dewpoint
        <td class='col-dewpoint'>$summary.dewpointMax.nolabel('%.0f')<br>$summary.dewpointMin.nolabel('%.0f')</td>
#end if
#if $show_humidity
        <td class='col-humidity'>$summary.humidityMax.nolabel('%.0f',' ')<br>$summary.humidityMin.nolabel('%.0f',' ')</td>
#end if
#if $show_wind
        <td class='col-wind'
    #if $summary.windDirs is not None
            style='vertical-align:middle; text-align:center; background: url()
      #for $d in $summary.windDirs
        #set $winddir_img = 'icons/' + $wind_dir_dict.get($d,$d) + '.png'
            ,url($winddir_img)
      #end for
            ; background-repeat:no-repeat; background-position:center; background-size:48px;'
    #end if
            >
    #if $summary.windSpeedMin == $summary.windSpeedMax or $summary.windSpeedMin.raw == $summary.windSpeedMax.raw
          $summary.windSpeedMin.nolabel('%.0f',' ')
    #else
          $summary.windSpeedMin.nolabel('%.0f',' ')-$summary.windSpeedMax.nolabel('%.0f',' ')
    #end if
          <span class='windgust'>$summary.windGust.nolabel('%.0f',' ')</span>$summary.windChar
        </td>
#end if
#if $show_tides and $tides is not None and len($tides) > 0
        <td class='col-tides'>
          <table style='width: 100%;padding: 0px;'>
  #for $tide in $tides
    #if $summary.event_ts.raw <= $tide.event_ts.raw < $summary.event_ts.raw + $summary.duration
            <tr>
              <td style='font-size:100%'>$tide.event_ts.format('%H:%M')</td><td class='tide-hilo' style='font-size:100%'>$tide.hilo</td><td style='font-size:100%; text-align:right;'>$tide.offset.nolabel('%.1f')</td>
            </tr>
    #end if
  #end for
          </table>
        </td>
#end if
#if $show_sun
        <td class='col-sun'>
  #if $alm.hasExtras
          $alm.sun.rise<br>
          $alm.sun.set
  #else
          $alm.sunrise<br>
          $alm.sunset
  #end if
        </td>
#end if
#if $show_moon
  #if $alm.hasExtras
        <td class='col-moon'>
          $alm.moon.rise<br>
          $alm.moon.set
        </td>
  #end if
        <td class='col-moonphase'>
          $alm.moon_fullness%
        </td>
#end if
#if $show_pop
        <td class='col-pop'>
  #if $summary.pop.raw is not None and $summary.pop.raw > 0
          $summary.pop.format('%.0f','')
  #end if
<br>
  #if $summary.qpf.raw is not None and $summary.qpf.raw > 0
          $summary.qpf.nolabel('%.2f','') <img class='pop-img' src='icons/raindrop.png' alt='raindrop'>
  #end if
<br>
  #if $summary.qsf.raw is not None and $summary.qsf.raw > 0
          $summary.qsf.nolabel('%.2f','') <img class='pop-img' src='icons/snowflake.png' alt='snowflake'>
  #end if
        </td>
#end if
#if $show_precip
        <td class='col-precip'>
  #for $k in $summary.precip
    #set $precip_img = 'icons/' + $k + '.png'
         <img class='precip-img' src='$precip_img' alt='$k' title='$forecast.label('Weather', $k)'>
  #end for
        </td>
#end if
#if $show_obvis
        <td class='col-obvis'>
  #for $k in $summary.obvis
    #set $obvis_img = 'icons/' + $k + '.png'
         <img class='obvis-img' src='$obvis_img' alt='$k' title='$forecast.label('Weather', $k)'>
  #end for
        </td>
#end if
      </tr>
    </table>
  </div>


#if $show_hourly
  <div id='$hourid' class='period' style='display:none'>
    <table>
#end if
  #end if ## lastday != thisday


#if $show_hourly
  #set $hour = $period.event_ts.format('%H:%M')
      <tr>
#if $show_day or $show_date
        <td class='col-date'>$hour<br></td>
#end if
#if $show_outlook
        <td class='col-outlook'>
  #if $period.clouds is not None
    #if $sunrise_ts < $period.event_ts.raw < $sunset_ts
      #set $outlook_img = 'icons/' + $period.clouds + '.png'
    #else
      #set $outlook_img = 'icons/' + $period.clouds + 'n.png'
    #end if
          <img class='outlook-img' src='$outlook_img' alt='$period.clouds' title='$forecast.label('Weather', $period.clouds)'>
  #end if
        </td>
#end if
#if $show_temp
        <td class='col-temp'>$period.temp.nolabel('%.0f')</td>
#end if
#if $show_dewpoint
        <td class='col-dewpoint'>$period.dewpoint.nolabel('%.0f')</td>
#end if
#if $show_humidity
        <td class='col-humidity'>$period.humidity.nolabel('%.0f',' ')</td>
#end if
#if $show_wind
        <td class='col-wind'
  #if $period.windDir is not None
    #set $winddir_img = 'icons/' + $wind_dir_dict.get($period.windDir,$period.windDir) + '.png'
          style='text-align:center; background: url($winddir_img); background-repeat:no-repeat; background-position:center; background-size:32px;'
  #end if
            >
          $period.windSpeed.nolabel('%.0f',' ') <span class='windgust'>$period.windGust.nolabel('%.0f',' ')</span>$period.windChar<br>
        </td>
#end if
#if $show_tides and $tides is not None and len($tides) > 0
        <td class='col-tides'>
  #for $tide in $tides
    #if $period.event_ts.raw <= $tide.event_ts.raw < $period.event_ts.raw + $period.duration and $tide.event_ts.raw < $nextday_ts
           $tide.event_ts.format('%H:%M') $tide.hilo $tide.offset.nolabel('%.1f')
    #end if
  #end for
        </td>
#end if
#if $show_sun
        <td class='col-sun'>
  #if $period.event_ts.raw <= $sunrise_ts < $period.event_ts.raw + $period.duration
          $alm.sunrise
  #end if
  #if $period.event_ts.raw <= $sunset_ts < $period.event_ts.raw + $period.duration
          $alm.sunset
  #end if
        </td>
#end if
#if $show_moon
  #if $alm.hasExtras
        <td class='col-moon'>
  #if $period.event_ts.raw <= $moonrise_ts < $period.event_ts.raw + $period.duration and $moonrise_ts < $nextday_ts
          $alm.moon.rise
  #end if
  #if $period.event_ts.raw <= $moonset_ts < $period.event_ts.raw + $period.duration and $moonset_ts < $nextday_ts
          $alm.moon.set
  #end if
        </td>
  #end if
        <td class='col-moonphase'></td>
#end if
#if $show_pop
        <td class='col-pop'>
  #if $period.pop.raw is not None and $period.pop.raw > 0
          $period.pop.format('%.0f',' ')
  #end if
<br>
  #if $period.qpf.raw is not None and $period.qpf.raw > 0
          $period.qpf.nolabel('%.2f',' ') <img class='pop-img' src='icons/raindrop.png' alt='raindrop'>
  #end if
<br>
  #if $period.qsf.raw is not None and $period.qsf.raw > 0
          $period.qsf.nolabel('%.2f',' ') <img class='pop-img' src='icons/snowflake.png' alt='snowflake'>
  #end if
        </td>
#end if
#if $show_precip
        <td class='col-precip'>
#if len($period.precip.items()) > 0
          <table style='width:100%;'><tr>
#end if
  #for $k,$v in $period.precip.items()
          <td>
    #set $precip_img = 'icons/' + $k + '.png'
            <img class='precip-img' src='$precip_img' alt='$k' title='$forecast.label('Weather', $k)'>
            <br>
    #if $v != ''
#set escaped_text = html.escape($forecast.label('Weather', $v+'q'))
            $escaped_text
    #else
            &nbsp;
    #end if
          </td>
  #end for
#if len($period.precip.items()) > 0
          </tr></table>
#end if
        </td>
#end if
#if $show_obvis
        <td class='col-obvis'>
  #if $period.obvis is not None
    #set $obvis_img = 'icons/' + $period.obvis + '.png'
          <img class='obvis-img' src='$obvis_img' alt='$period.obvis' title='$forecast.label('Weather', $period.obvis)'>
  #end if
        </td>
#end if
      </tr>
#end if  ## show_hourly
#end for ## period in periods

#if $show_hourly and $periods is not None and len($periods) > 0
    </table>
  </div>
#end if

  <div class='sources'>
    <p>
      $forecast_source forecast
#if $wloc is not None and $wloc != ''
 for $wloc
#end if
#if $wts is not None and $wts != ''
 issued on $wts.
#end if
#if $show_tides and $tides is not None and len($tides) > 0
      <br>Tides for $tides[0].location issued on $tides[0].issued_ts
#end if
#set $t1 = time.time()
#set $elapsed = "%.3f" % ($t1 - $t0)
     <br>Report generated in $elapsed seconds.
    </p>
  </div>

#else

<p>forecast_table: forecast search list extension is not installed</p>

#end if

</div>
