## forecast strip chart - Copyright 2012-2016 Matthew Wall
## Copyright 2020-2026 John A Kline (john@johnkline.com)
## $Id: forecast_strip.inc 1745 2017-09-21 03:54:21Z mwall $
#set $forecast_strip_version = 0.3
##
## Include this file to display forecast data.  This file uses icons from the
## forecast icon set.
##
## To override the default settings in this file, use the following syntax in
## skin.conf or weewx.conf:
##
## [forecast_strip_settings]
##     source = NWS
##     num_periods = 40
##
## To display a single forecast strip from a single source:
##
## #include forecast_strip.inc
##
## <body onload="populate_strip('forecast_strip', 'NWS');">
## <div id='forecast_strip'></div>
## </body>
##
## To display strips from multiple sources in a single page:
##
## #set global $forecast_strip_settings = {}
## #set global $forecast_strip_settings['num_periods'] = 300
## #set global $forecast_strip_settings['source'] = 'NWS'
## #include forecast_strip.inc
##
## #set global $forecast_strip_settings['source'] = 'OWM'
## #include forecast_strip.inc
##
## <body onload="populate_strip('nws', 'NWS'); populate_strip('owm', 'OWM'">
## <div id='nws'></div>
## <div id='owm'></div>
## </body>

#if $varExists('forecast')

#import time
#set $t0 = time.time()

## Which forecasts should be displayed?
#set $strip_source = 'NWS'

## How many forecast periods should be considered?
## Up to 40 for NWS, up to 12 for WU.  More periods take longer to generate.
#set $num_periods = 300

## Orientation: show time shown horizontally or vertically?
#set $orientation = 'horizontal';

## Which columns should be displayed?
#set $show_temp = 1
#set $show_temp_min = 1
#set $show_temp_max = 1
#set $show_dewpoint = 0
#set $show_humidity = 0
#set $show_wind = 1
#set $show_clouds = 1
#set $show_pop = 1
#set $show_snow = 1
#set $show_precip = 1
#set $show_sun = 0
#set $show_moon = 0
#set $show_moonphase = 0
#set $show_tides = 0

#set $local_settings = dict()

## First look for values from skin.conf or weewx.conf
#if $varExists('Extras') and $varExists('Extras.forecast_strip_settings')
#for $sv in $Extras.forecast_strip_settings.keys()
#set $local_settings[$sv] = $Extras.forecast_strip_settings[$sv]
#end for
#end if

## Look for overrides defined by any template that includes this file
#if $varExists('forecast_strip_settings')
#for $sv in $forecast_strip_settings.keys()
#set $local_settings[$sv] = $forecast_strip_settings[$sv]
#end for
#end if

## Now assign the values that will actually be used
#set $strip_source = $local_settings.get('source', $strip_source)
#set $num_periods = int($local_settings.get('num_periods', $num_periods))
#set $orientation = $local_settings.get('orientation', $orientation)
#set $show_temp = int($local_settings.get('show_temp', $show_temp))
#set $show_temp_min = int($local_settings.get('show_temp_min', $show_temp_min))
#set $show_temp_max = int($local_settings.get('show_temp_max', $show_temp_max))
#set $show_dewpoint = int($local_settings.get('show_dewpoint', $show_dewpoint))
#set $show_humidity = int($local_settings.get('show_humidity', $show_humidity))
#set $show_wind = int($local_settings.get('show_wind', $show_wind))
#set $show_clouds = int($local_settings.get('show_clouds', $show_clouds))
#set $show_pop = int($local_settings.get('show_pop', $show_pop))
#set $show_snow = int($local_settings.get('show_snow', $show_snow))
#set $show_precip = int($local_settings.get('show_precip', $show_precip))
#set $show_sun = int($local_settings.get('show_sun', $show_sun))
#set $show_moon = int($local_settings.get('show_moon', $show_moon))
#set $show_moonphase = int($local_settings.get('show_moonphase', $show_moonphase))
#set $show_tides = int($local_settings.get('show_tides', $show_tides))

#set $tides = $forecast.xtides(startofday=True)
#set $periods = $forecast.weather_periods($strip_source, max_events=$num_periods)

## Define this javascript only once
#if not $varExists('forecast_strip_included')
#set global $forecast_strip_included = 1
<script>
// array of forecast data, one element for each forecast source
var forecast_data = {};

// default display settings based on skin parameters
var default_display_settings = {
  'orientation': '$orientation',
  'show_temp': $show_temp,
  'show_temp_min': $show_temp_min,
  'show_temp_max': $show_temp_max,
  'show_dewpoint': $show_dewpoint,
  'show_humidity': $show_humidity,
  'show_wind': $show_wind,
  'show_clouds': $show_clouds,
  'show_pop': $show_pop,
  'show_snow': $show_snow,
  'show_precip': $show_precip,
  'show_sun': $show_sun,
  'show_moon': $show_moon,
  'show_moonphase': $show_moonphase,
  'show_tides': $show_tides,
};

function populate_strip(div_id, data_id, display_settings) {
  if(display_settings === undefined || display_settings === null) {
    display_settings = default_display_settings;
  }
  if(! forecast_data[data_id]) return;
  var elem = document.getElementById(div_id);
  if(! elem) return;
  elem.innerHTML = '';
  var tbl = document.createElement('table');
  if(display_settings.orientation === 'vertical') {
    populate_vertical_strip(tbl, data_id, display_settings);
  } else {
    populate_horizontal_strip(tbl, data_id, display_settings);
  }
  var d = document.createElement('div');
  d.className = 'fc_strip';
  d.appendChild(tbl);
  d.appendChild(create_summary(forecast_data[data_id].summary));
  elem.appendChild(d);
}

function create_col(data) {
  var c = document.createElement('col');
  c.className = data.className;
  return c;
}

function populate_vertical_strip(tbl, data_id, display_settings) {
  tbl.appendChild(create_col(forecast_data[data_id].date));
  tbl.appendChild(create_col(forecast_data[data_id].hour));
  if(display_settings.show_temp_max)
    tbl.appendChild(create_col(forecast_data[data_id].tempMax));
  if(display_settings.show_temp)
    tbl.appendChild(create_col(forecast_data[data_id].temp));
  if(display_settings.show_temp_min)
    tbl.appendChild(create_col(forecast_data[data_id].tempMin));
  if(display_settings.show_dewpoint)
    tbl.appendChild(create_col(forecast_data[data_id].dewpoint));
  if(display_settings.show_humidity)
    tbl.appendChild(create_col(forecast_data[data_id].humidity));
  if(display_settings.show_wind) {
    tbl.appendChild(create_col(forecast_data[data_id].windSpeed));
    tbl.appendChild(create_col(forecast_data[data_id].windGust));
    tbl.appendChild(create_col(forecast_data[data_id].windDir));
  }
  if(display_settings.show_clouds)
    tbl.appendChild(create_col(forecast_data[data_id].clouds));
  if(display_settings.show_pop)
    tbl.appendChild(create_col(forecast_data[data_id].pop));
  if(display_settings.show_precip) {
    tbl.appendChild(create_col(forecast_data[data_id].qpf));
    if(display_settings.show_snow)
      tbl.appendChild(create_col(forecast_data[data_id].qsf));
  }
  if(display_settings.show_sun)
    tbl.appendChild(create_col(forecast_data[data_id].sun));
  if(display_settings.show_moon)
    tbl.appendChild(create_col(forecast_data[data_id].moon));
  if(display_settings.show_moonphase)
    tbl.appendChild(create_col(forecast_data[data_id].moonphase));
#if len($tides) > 0
  if(display_settings.show_tide)
    tbl.appendChild(create_col(forecast_data[data_id].tide));
#end if

  var tr = document.createElement('tr');
  tr.appendChild(create_th_icon(forecast_data[data_id].date));
  tr.appendChild(create_th_icon(forecast_data[data_id].hour));
  if(display_settings.show_temp_max)
    tr.appendChild(create_th_icon(forecast_data[data_id].tempMax));
  if(display_settings.show_temp)
    tr.appendChild(create_th_icon(forecast_data[data_id].temp));
  if(display_settings.show_temp_min)
    tr.appendChild(create_th_icon(forecast_data[data_id].tempMin));
  if(display_settings.show_dewpoint)
    tr.appendChild(create_th_icon(forecast_data[data_id].dewpoint));
  if(display_settings.show_humidity)
    tr.appendChild(create_th_icon(forecast_data[data_id].humidity));
  if(display_settings.show_wind) {
    tr.appendChild(create_th_icon(forecast_data[data_id].windSpeed));
    tr.appendChild(create_th_icon(forecast_data[data_id].windGust));
    tr.appendChild(create_th_icon(forecast_data[data_id].windDir));
  }
  if(display_settings.show_clouds)
    tr.appendChild(create_th_icon(forecast_data[data_id].clouds));
  if(display_settings.show_pop)
    tr.appendChild(create_th_icon(forecast_data[data_id].pop));
  if(display_settings.show_precip) {
    tr.appendChild(create_th_icon(forecast_data[data_id].qpf));
    if(display_settings.show_snow)
      tr.appendChild(create_th_icon(forecast_data[data_id].qsf));
  }
  if(display_settings.show_sun)
    tr.appendChild(create_th_icon(forecast_data[data_id].sun));
  if(display_settings.show_moon)
    tr.appendChild(create_th_icon(forecast_data[data_id].moon));
  if(display_settings.show_moonphase)
    tr.appendChild(create_th_icon(forecast_data[data_id].moonphase));
#if len($tides) > 0
  if(display_settings.show_tide)
    tr.appendChild(create_th_icon(forecast_data[data_id].tide));
#end if
  tbl.appendChild(tr);

  var tr = document.createElement('tr');
  tr.appendChild(create_th_units(forecast_data[data_id].date));
  tr.appendChild(create_th_units(forecast_data[data_id].hour));
  if(display_settings.show_temp_max)
    tr.appendChild(create_th_units(forecast_data[data_id].tempMax));
  if(display_settings.show_temp)
    tr.appendChild(create_th_units(forecast_data[data_id].temp));
  if(display_settings.show_temp_min)
    tr.appendChild(create_th_units(forecast_data[data_id].tempMin));
  if(display_settings.show_dewpoint)
    tr.appendChild(create_th_units(forecast_data[data_id].dewpoint));
  if(display_settings.show_humidity)
    tr.appendChild(create_th_units(forecast_data[data_id].humidity));
  if(display_settings.show_wind) {
    tr.appendChild(create_th_units(forecast_data[data_id].windSpeed));
    tr.appendChild(create_th_units(forecast_data[data_id].windGust));
    tr.appendChild(create_th_units(forecast_data[data_id].windDir));
  }
  if(display_settings.show_clouds)
    tr.appendChild(create_th_units(forecast_data[data_id].clouds));
  if(display_settings.show_pop)
    tr.appendChild(create_th_units(forecast_data[data_id].pop));
  if(display_settings.show_precip) {
    tr.appendChild(create_th_units(forecast_data[data_id].qpf));
    if(display_settings.show_snow)
      tr.appendChild(create_th_units(forecast_data[data_id].qsf));
  }
  if(display_settings.show_sun)
    tr.appendChild(create_th_units(forecast_data[data_id].sun));
  if(display_settings.show_moon)
    tr.appendChild(create_th_units(forecast_data[data_id].moon));
  if(display_settings.show_moonphase)
    tr.appendChild(create_th_units(forecast_data[data_id].moonphase));
#if len($tides) > 0
  if(display_settings.show_tide)
    tr.appendChild(create_th_units(forecast_data[data_id].tide));
#end if
  tbl.appendChild(tr);

  for(var i=0; i<forecast_data[data_id].hour.values.length; i++) {
    tr = document.createElement('tr');
    tr.appendChild(create_td(forecast_data[data_id].date, i));
    tr.appendChild(create_td(forecast_data[data_id].hour, i));
    if(display_settings.show_temp_max)
      tr.appendChild(create_td(forecast_data[data_id].tempMax, i));
    if(display_settings.show_temp)
      tr.appendChild(create_td(forecast_data[data_id].temp, i));
    if(display_settings.show_temp_min)
      tr.appendChild(create_td(forecast_data[data_id].tempMin, i));
    if(display_settings.show_dewpoint)
      tr.appendChild(create_td(forecast_data[data_id].dewpoint, i));
    if(display_settings.show_humidity)
      tr.appendChild(create_td(forecast_data[data_id].humidity, i));
    if(display_settings.show_wind) {
      tr.appendChild(create_td(forecast_data[data_id].windSpeed, i));
      tr.appendChild(create_td(forecast_data[data_id].windGust, i));
      tr.appendChild(create_td(forecast_data[data_id].windDir, i));
    }
    if(display_settings.show_clouds)
      tr.appendChild(create_td(forecast_data[data_id].clouds, i));
    if(display_settings.show_pop)
      tr.appendChild(create_td(forecast_data[data_id].pop, i));
    if(display_settings.show_precip) {
      tr.appendChild(create_td(forecast_data[data_id].qpf, i));
      if(display_settings.show_snow)
        tr.appendChild(create_td(forecast_data[data_id].qsf, i));
    }
    if(display_settings.show_sun)
      tr.appendChild(create_td(forecast_data[data_id].sun, i));
    if(display_settings.show_moon)
      tr.appendChild(create_td(forecast_data[data_id].moon, i));
    if(display_settings.show_moonphase)
      tr.appendChild(create_td(forecast_data[data_id].moonphase, i));
#if len($tides) > 0
    if(display_settings.show_tides)
      tr.appendChild(create_td(forecast_data[data_id].tide, i));
#end if
    tbl.appendChild(tr);
  }
}

function populate_horizontal_strip(tbl, data_id, display_settings) {
  tbl.appendChild(create_tr(forecast_data[data_id].date));
  tbl.appendChild(create_tr(forecast_data[data_id].hour));
  if(display_settings.show_temp_max)
    tbl.appendChild(create_tr(forecast_data[data_id].tempMax));
  if(display_settings.show_temp)
    tbl.appendChild(create_tr(forecast_data[data_id].temp));
  if(display_settings.show_temp_min)
    tbl.appendChild(create_tr(forecast_data[data_id].tempMin));
  if(display_settings.show_dewpoint)
    tbl.appendChild(create_tr(forecast_data[data_id].dewpoint));
  if(display_settings.show_humidity)
    tbl.appendChild(create_tr(forecast_data[data_id].humidity));
  if(display_settings.show_wind) {
    tbl.appendChild(create_tr(forecast_data[data_id].windSpeed));
    tbl.appendChild(create_tr(forecast_data[data_id].windGust));
    tbl.appendChild(create_tr(forecast_data[data_id].windDir));
  }
  if(display_settings.show_clouds)
    tbl.appendChild(create_tr(forecast_data[data_id].clouds));
  if(display_settings.show_pop)
    tbl.appendChild(create_tr(forecast_data[data_id].pop));
  if(display_settings.show_precip) {
    tbl.appendChild(create_tr(forecast_data[data_id].qpf));
    if(display_settings.show_snow)
      tbl.appendChild(create_tr(forecast_data[data_id].qsf));
  }
  if(display_settings.show_sun)
    tbl.appendChild(create_tr(forecast_data[data_id].sun));
  if(display_settings.show_moon)
    tbl.appendChild(create_tr(forecast_data[data_id].moon));
  if(display_settings.show_moonphase)
    tbl.appendChild(create_tr(forecast_data[data_id].moonphase));
#if len($tides) > 0
  if(display_settings.show_tides)
    tbl.appendChild(create_tr(forecast_data[data_id].tide));
#end if
}

function create_tr(data) {
  var tr = document.createElement('tr');
  tr.className = data.className;
  var th = create_th_icon(data);
  tr.appendChild(th);
  th = create_th_units(data);
  tr.appendChild(th);
  for(var i=0; i<data.values.length; i++) {
    tr.appendChild(create_td(data, i, 1));
  }
  return tr;
}

function create_th_icon(data) {
  var th = document.createElement('th');
  if(data.legend && data.legend != '') {
    var img = document.createElement('img');
    img.setAttribute('src', data.legend);
    img.className = 'legend-img';
    th.appendChild(img);
  }
  return th;
}

function create_th_units(data) {
  var th = document.createElement('th');
  if(data.units != '') {
    th.innerHTML = data.units;
  }
  return th;
}

function create_td(data, idx, horizontal) {
  var td = document.createElement('td');
  var v = data.values[idx];
  if(v === undefined) return td;
  if(data.td_type == 'icon') {
    if(v != '') {
      var img = document.createElement('img');
      img.setAttribute('src', 'icons/' + v + '.png')
      td.appendChild(img);
    }
  } else if(data.td_type == 'txt') {
    if((v == '0.00' || v == '0') && data.skip_zeros) {
      ;
    } else {
      var n = document.createTextNode(v);
      td.appendChild(n);
      var bg = get_tint(v, data.className, data.units);
      if(bg != '') {
        td.style.background = bg;
//        td.style.border = '1px solid #dddddd';
      }
//      td.style.border = '1px solid #eeeeee';
    }
  } else if(data.td_type == 'html') {
    td.innerHTML = v;
  } else if(data.td_type == 'date') {
    if(horizontal) {
      x = data.spanvalues[idx];
      if(x !== undefined) {
        if(x.colspan) { td.colSpan = x.colspan; }
        if(x.label) { td.innerHTML = x.label; }
      }
    } else {
      td.innerHTML = v;
    }
  }
  return td;
}

function create_summary(summary_data) {
  var d = document.createElement('div');
  d.className = 'sources';
  var html = summary_data.source + " forecast";
  if(summary_data.location != '') {
    html += " for " + summary_data.location;
  }
  if(summary_data.issued_ts != '') {
    html += " issued on " + summary_data.issued_ts;
  }
  html += "<br>Report generated in " + summary_data.elapsed + " seconds.";
  d.innerHTML = html;
  return d;
}

function get_rgba(r, g, b, a) {
  return 'rgba('+r+','+g+','+b+','+a+')';
}

// table of tint thresholds and limits
// t_max;  maximum tint - anything over this is maximum high color
// t_min;  minimum tint - anything under this is maximum low color
// t_up;   upper threshold - start tinting when over this value
// t_dn;   lower threshold - start tinting when below this value
// the r,g,b values control the tint color
var tint_limits = {
  'pop': {'t_max': 100.0, 't_up': 30.0, // percent
          'r': 0, 'g': 144, 'b': 200},
  'qpf': {'t_max': 2.5, // cm
          'r': 0, 'g': 120, 'b': 250},
  'qsf': {'t_max': 15.0, // cm
          'r': 120, 'g': 120, 'b': 250},
  'wind': {'t_max': 65.0, // kph
           'r': 255, 'g': 144, 'b': 0},
  'temp': {'t_max': 45.0, 't_min': -30.0, 't_up': 15.0, 't_dn': 10.0, // C
           'r_up': 200, 'g_up': 20, 'b_up': 20,
           'r_dn': 60, 'g_dn': 60, 'b_dn': 250},
  'humidity': {'t_max': 100.0, 't_up': 10.0, // percent
               'r': 20, 'g': 120, 'b': 200},
  'moonphase': {'t_max': 100.0, // percent
                'r': 200, 'g': 200, 'b': 210}
};

function get_tint(v, class_name, units) {
  if(v === undefined || v == '') return '';
  if(units === undefined) units = '';
  if(class_name == 'pop') {
    var a = (v - tint_limits[class_name]['t_up']) /
      (tint_limits[class_name]['t_max'] - tint_limits[class_name]['t_up']);
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  if(class_name == 'qpf') {
    var d = v;
    if(units.endsWith('in')) d = d * 2.54; // convert to cm
    if(units.endsWith('mm')) d = d / 10.0; // convert to cm
    var a = d / tint_limits[class_name]['t_max'];
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  if(class_name == 'qsf') {
    var d = v;
    if(units.endsWith('in')) d = d * 2.54; // convert to cm
    if(units.endsWith('mm')) d = d / 10.0; // convert to cm
    var a = d / tint_limits[class_name]['t_max'];
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  if(class_name == 'windSpeed' || class_name == 'windGust') {
    class_name = 'wind';
    var s = v;
    if(units.endsWith('mph')) s = s * 1.60934; // convert to kph
    var a = (s > tint_limits[class_name]['t_max']) ?
      1.0 : s / tint_limits[class_name]['t_max'];
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  if(class_name.indexOf('temp') >= 0 || class_name == 'dewpoint') {
    // blue for cold, red for warm, darker toward either end of spectrum
    class_name = 'temp';
    var c = v;
    if(units.endsWith('F')) c = (v - 32.0) * 5.0 / 9.0; // convert to C
    if(c > tint_limits[class_name]['t_up']) {
      var a = (c > tint_limits[class_name]['t_max']) ?
        1.0 : (c - tint_limits[class_name]['t_up']) /
          (tint_limits[class_name]['t_max'] - tint_limits[class_name]['t_up']);
      if(a > 0.8) { a = 0.8; }
      return get_rgba(tint_limits[class_name]['r_up'],
                      tint_limits[class_name]['g_up'],
                      tint_limits[class_name]['b_up'], a);
    } else if(c < tint_limits[class_name]['t_dn']) {
      var a = (c < tint_limits[class_name]['t_min']) ?
        1.0 : (c - tint_limits[class_name]['t_dn']) /
          (tint_limits[class_name]['t_min'] - tint_limits[class_name]['t_dn']);
      if(a > 0.8) { a = 0.8; }
      return get_rgba(tint_limits[class_name]['r_dn'],
                      tint_limits[class_name]['g_dn'],
                      tint_limits[class_name]['b_dn'], a);
    }
  }
  if(class_name == 'humidity') {
    var a = (v - tint_limits[class_name]['t_up']) /
      (tint_limits[class_name]['t_max'] - tint_limits[class_name]['t_up']);
    a = (a - 0.5 < 0) ? 0 : a - 0.5;
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  if(class_name == 'moonphase') {
    var a = v / tint_limits[class_name]['t_max'];
    return get_rgba(tint_limits[class_name]['r'],
                    tint_limits[class_name]['g'],
                    tint_limits[class_name]['b'], a);
  }
  return '';
}
</script>
#end if ## forecast_strip_included

## Strip chart shows arrows pointing with wind flow, not into the wind
#set $tWind = {'N':'tS', 'NNE':'tSSW', 'NE':'tSW', 'ENE':'tWSW', 'E':'tW', 'ESE':'tWNW', 'SE':'tNW', 'SSE':'tNNW', 'S':'tN', 'SSW':'tNNE', 'SW':'tNE', 'WSW':'tENE', 'W':'tE', 'WNW':'tESE', 'NW':'tSE', 'NNW':'tSSE'}

#set $strip_location = ''
#set $strip_issued_ts = ''

#if len($periods) > 0
#set $strip_location = $periods[0].location
#set $strip_issued_ts = $periods[0].issued_ts
#end if

#set $days = dict()
#for $period in $periods
  #set $thisdate = $period.event_ts.format('%Y.%m.%d')
  #set $thisdow = $period.event_ts.format('%a')
  #if $days.get($thisdate)
    #set $days[$thisdate]['periods'] = $days[$thisdate]['periods'] + 1
  #else
    #set $days[$thisdate] = dict()
    #set $days[$thisdate]['periods'] = 1
    #set $days[$thisdate]['dow'] = $thisdow
  #end if
#end for

<script>
forecast_data.$strip_source = {
  'id': "$strip_source",
  'date': {
    'className': 'date',
    'units': '',
    'td_type': 'date',
    'values':[ #slurp
#for $day in sorted($days)
  #set $label = '<span class="day">%s</span><br><span class="date">%s</span>' % ($days[$day]['dow'], $day)
'$label', #slurp
  #for $p in range($days[$day]['periods'] - 1)
'', #slurp
  #end for
#end for
    ],
    'spanvalues':[ #slurp
#for $day in sorted($days)
  #set $label = ''
  #if $days[$day]['periods'] > 3
    #set $label = '<span class="day">%s</span><br><span class="date">%s</span>' % ($days[$day]['dow'], $day)
  #end if
{'colspan': $days[$day]['periods'], 'label': '$label'}, #slurp
#end for
  ]},
  'hour': {
    'className': 'hour',
    'units': '',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.event_ts.format('%Hh')", #slurp
#end for
  ]},
  'tempMax': {
    'className': 'temp',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.tempMax.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'tempMin': {
    'className': 'temp',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.tempMin.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'temp': {
    'className': 'temp',
    'legend': 'icons/thermometer-red.png',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.temp.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'dewpoint': {
    'className': 'dewpoint',
    'legend': 'icons/thermometer-dewpoint.png',
    'units': '$unit.label.dewpoint',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.dewpoint.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'humidity': {
    'className': 'humidity',
    'legend': 'icons/thermometer-blue.png',
    'units': '%',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.humidity.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windSpeed': {
    'className': 'windSpeed',
    'legend': 'icons/flag.png',
    'units': '$unit.label.wind',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.windSpeed.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windGust': {
    'className': 'windGust',
    'units': '$unit.label.wind',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.windGust.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windDir': {
    'className': 'windDir',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
#set $wd = $tWind.get($period.windDir)
"$wd", #slurp
#end for
  ]},
  'clouds': {
    'className': 'clouds',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $clouds_img = ''
  #if $period.clouds is not None
    #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
    #set $sunrise_ts = $alm.sunrise.raw
    #set $sunset_ts = $alm.sunset.raw
    #if $sunrise_ts < $period.event_ts.raw < $sunset_ts
      #set $clouds_img = $period.clouds
    #else
      #set $clouds_img = $period.clouds + 'n'
    #end if
  #end if
"$clouds_img", #slurp
#end for
  ]},
  'pop': {
    'className': 'pop',
    'legend': 'icons/pop.png',
    'units': '%',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.pop.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'qpf': {
    'className': 'qpf',
    'legend': 'icons/raindrop.png',
    'units': '$unit.label.rain',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.qpf.nolabel('%.2f', '')", #slurp
#end for
  ]},
  'qsf': {
    'className': 'qsf',
    'legend': 'icons/snowflake.png',
    'units': '$unit.label.rain',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.qsf.nolabel('%.2f', '')", #slurp
#end for
  ]},
  'sun': {
    'className': 'sun',
    'legend': 'icons/sunriseset.png',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $img = ''
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
  #set $sunrise_ts = $alm.sunrise.raw
  #set $sunset_ts = $alm.sunset.raw
  #if $period.event_ts.raw < $sunrise_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'sunrise'
  #end if
  #if $period.event_ts.raw < $sunset_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'sunset'
  #end if
"$img", #slurp
#end for
  ]},
  'moon': {
    'className': 'moon',
    'legend': 'icons/moonriseset.png',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $img = ''
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
  #if $alm.hasExtras
    #set $moonrise_ts = $alm.moon.rise.raw
    #set $moonset_ts = $alm.moon.set.raw
    #if $period.event_ts.raw < $moonrise_ts <= $period.event_ts.raw + $period.duration
      #set $img = 'moonrise'
    #end if
    #if $period.event_ts.raw < $moonset_ts <= $period.event_ts.raw + $period.duration
      #set $img = 'moonset'
    #end if
  #end if
"$img", #slurp
#end for
  ]},
  'moonphase': {
    'className': 'moonphase',
    'legend': 'icons/moonphase.png',
    'units': '',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
"$alm.moon_fullness", #slurp
#end for
  ]},
#if len($tides) > 0
  'tide': {
    'className': 'tide',
    'legend': 'icons/water.png',
    'units': '$unit.label.altitude',
    'td_type': 'html',
    'values':[ #slurp
#for $period in $periods
  #set $tide_info = ''
  #for $tide in $tides
    #if $period.event_ts.raw <= $tide.event_ts.raw < $period.event_ts.raw + $period.duration
      #set $tide_info = '<span class="tide_offset">%s</span><br><span class="tide_date">%s</span>' % ($tide.offset.nolabel('%.1f'), $tide.event_ts.format('%H:%M'))
    #end if
  #end for
'$tide_info', #slurp
#end for
  ]},
#end if
  'summary': {
    'source': "$strip_source",
    'location': "$strip_location",
    'issued_ts': "$strip_issued_ts",
#set $elapsed = "%.3f" % (time.time() - $t0)
    'elapsed': "$elapsed"
  }
};
</script>

#else

<p>forecast_strip: forecast search list extension is not installed</p>

#end if
