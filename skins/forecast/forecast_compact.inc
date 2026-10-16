## forecast compact - Copyright 2016 Matthew Wall
## Copyright 2020-2026 John A Kline (john@johnkline.com)
## $Id: forecast_compact.inc 1745 2017-09-21 03:54:21Z mwall $
#set $forecast_compact_version = 0.1
##
## Include this file to display forecast data.  This file uses icons from the
## forecast icon set.
##
## To override the default settings in this file, use the following syntax in
## skin.conf or weewx.conf:
##
## [forecast_compact_settings]
##     source = NWS
##     num_days = 7
##     show_wind = 1
##     show_pop = 1
##     show_precip = 1
##     show_obvis = 1

<div class='fc_compact'>

#if $varExists('forecast')

#import time
#set $t0 = time.time()

## Which forecast should be displayed?
#set $forecast_source = 'NWS'

## How many days should be considered?
#set $num_days = 7

## Which data should be displayed?
#set $show_wind = 1
#set $show_pop = 1
#set $show_precip = 1
#set $show_obvis = 1

#set $local_settings = dict()

## First look for values from skin.conf or weewx.conf
#if $varExists('Extras') and $varExists('Extras.forecast_compact_settings')
  #for $sv in $Extras.forecast_compact_settings.keys()
    #set $local_settings[$sv] = $Extras.forecast_compact_settings[$sv]
  #end for
#end if

## Look for overrides defined by any template that includes this file
#if $varExists('forecast_compact_settings')
  #for $sv in $forecast_compact_settings.keys()
    #set $local_settings[$sv] = $forecast_compact_settings[$sv]
  #end for
#end if

## Now assign the values that will actually be used
#set $forecast_source = $local_settings.get('source', $forecast_source)
#set $num_days = int($local_settings.get('num_days', $num_days))
#set $show_wind = int($local_settings.get('show_wind', $show_wind))
#set $show_pop = int($local_settings.get('show_pop', $show_pop))
#set $show_precip = int($local_settings.get('show_precip', $show_precip))
#set $show_obvis = int($local_settings.get('show_obvis', $show_obvis))

## pre-calculate the periods
#set $num_periods = $num_days * 24
#set $periods = $forecast.weather_periods($forecast_source, max_events=$num_periods)

#if len($periods)
#set $start_ts = $t0

<table>
  <tr>
    <td class='first-column'>
      <div class='row-day'>&nbsp;</div>
      <div class='row-outlook'></div>
      <div class='row-temp'>
        <div>Max</div>
        <div>Min</div>
      </div>
      <div class='row-wind'>Wind</div>
#if $show_pop
      <div class='row-pop'>PoP</div>
#end if
    </td>
#for $d in range($num_days)
#set $summary = $forecast.weather_summary($forecast_source, $start_ts + $d * 24*3600, periods=$periods)
    <td>
      <div class='row-day'>
        <span class='day'>$summary.event_ts.format('%a')</span>
      </div>
      <div class='row-outlook'>
#if $summary.clouds is not None
#set $simg = 'icons/' + $summary.clouds + '.png'
        <img class='outlook-img' src='$simg' alt='$summary.clouds' title='$forecast.label("Weather", $summary.clouds)'>
#end if
      </div>
      <div class='row-temp'>
        <div>$summary.tempMax.nolabel('%.0f')</div>
        <div>$summary.tempMin.nolabel('%.0f')</div>
      </div>
#if $show_wind
      <div class='row-wind'>
        $summary.windSpeed.nolabel('%.1f')
      </div>
#end if
#if $show_pop
      <div class='row-pop'>
        $summary.pop.nolabel('%.0f')
      </div>
#end if
#if $show_precip
      <div class='row-precip'>
  #for $k in $summary.precip
    #set $precip_img = 'icons/' + $k + '.png'
      <img class='precip-img' src='$precip_img' alt='$k' title='$forecast.label('Weather', $k)'><br>
  #end for
      </div>
#end if
#if $show_obvis
      <div class='row-obvis'>
  #for $k in $summary.obvis
    #set $obvis_img = 'icons/' + $k + '.png'
      <img class='obvis-img' src='$obvis_img' alt='$k' title='$forecast.label('Weather', $k)'><br>
  #end for
      </div>
#end if
    </td>
#end for
    <td class='last-column'>
      <div class='row-day'>&nbsp;</div>
      <div class='row-outlook'></div>
      <div class='row-temp'>
        <div>$unit.label.outTemp</div>
        <div>$unit.label.outTemp</div>
      </div>
      <div class='row-wind'>
        $unit.label.windSpeed
      </div>
#if $show_pop
      <div class='row-pop'>%</div>
#end if
    </td>
  </tr>
</table>


#else

<p>No forecast data for $forecast_source</p>

#end if

#set $t1 = time.time()
#set $elapsed = "%.3f" % ($t1 - $t0)
<!-- report generated in $elapsed s -->

#else

<p>forecast_iconic: forecast search list extension is not installed</p>

#end if

</div>
