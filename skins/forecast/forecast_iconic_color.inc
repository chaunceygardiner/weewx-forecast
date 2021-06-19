## forecast iconic - Copyright 2016 Matthew Wall
## $Id: forecast_iconic.inc 1789 2019-01-10 03:30:48Z mwall $
#set $forecast_iconic_color_version = 0.1
##
## Include this file to display forecast data.  This file uses icons from the
## forecast icon set.
##
## To override the default settings in this file, use the following syntax in
## skin.conf or weewx.conf:
##
## [forecast_iconic_settings]
##     source = NWS
##     orientation = vertical (horizontal not tested)
##     num_days = 7
##     bar_size = 150
##     show_date = 0
##     show_pop = 0
##     show_precip = 1
##     show_obvis = 1

<script>

function HSVtoRGB(t) 
{
// Thankyou SO
// https://stackoverflow.com/questions/17242144/javascript-convert-hsb-hsv-color-to-rgb-accurately
//
    var h=t[0]/360;
    var s= t[1];
    var v= t[2];
    
	//console.log(t)
	//console.log("H:"+h+ " s "+ s+" " +Math.floor(h * 6));
    var r, g, b, i, f, p, q, t;
    
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) 
    {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }
    return "rgb("+Math.round(r * 255)+","+Math.round(g * 255)+","+Math.round(b * 255)+")";
    
};

function get_tint(Min,Max, units) 
{
	var Temp_Colors = [[240.0,1.0,1],[239.0,1,1.0],[220.0,1,1.0],[210.0,.47,1.0],[180.0,1,1],[140.0,1.0,1],[100.0,1.0,1],[40.0,1.0,1.0],[0.0,1.0,1.0]];
	var MinTemp = -40;
	var MaxTemp = 40;
	var MaxIndex = (MaxTemp-MinTemp)/10;
	var Colors=[];
  if(units === undefined) units = 'degC';
  if (units === 'degF')
  {
	Min=(Min-32)*5/9;
	Max=(Max-32)*8/9;
  }
  
  var ret="linear-gradient(to right";
   var Temp = MinTemp;
  var Index=0;
  var StartIndex = 0;
  
  if (Min < MinTemp)
  {
	StartIndex=0;
	  while (Temp < MinTemp) 
	  {
		Colors.push(HSVtoRGB( Temp_Colors[Index]));
		//ret += ","+;
		Temp += 10;
	  }
  }
  else
  {
	StartIndex = (-MinTemp+Min -( Min %10 ))/10;
  }
  EndIndex = (-MinTemp+Max - (Max % 10))/10;
  
  if (EndIndex >= MaxIndex)
  {
	EndIndex=MaxIndex;
  }
  
  var StartColor=null;
  
  if (Min%10 && StartIndex > 0)
  {
	f=(Min%10)/10;
	var i = StartIndex;
	h=(Temp_Colors[i-1][0]+(Temp_Colors[i][0]-Temp_Colors[i-1][0])/10*f);
	s=(Temp_Colors[i-1][1]+(Temp_Colors[i][1]-Temp_Colors[i-1][1])/10*f);
    v=(Temp_Colors[i-1][2]+(Temp_Colors[i][2]-Temp_Colors[i-1][2])/10*f);
	StartColor=HSVtoRGB([h,s,v]);
	Colors.push(StartColor);
  }
  
  if (StartIndex==EndIndex)
  {
	if (!StartColor)
	{
		var i = StartIndex;
		
		StartColor=HSVtoRGB(Temp_Colors[i]);
		Colors.push(StartColor);
	}
	if (Max % 10 && Max < MaxTemp)
	{
		f=(Min%10)/10;
		var i = EndIndex;
		h=(Temp_Colors[i][0]+(Temp_Colors[i+1][0]-Temp_Colors[i][0])/10*f);
		s=(Temp_Colors[i][1]+(Temp_Colors[i+1][1]-Temp_Colors[i][1])/10*f);
		v=(Temp_Colors[i][2]+(Temp_Colors[i+1][2]-Temp_Colors[i][2])/10*f);		
		Colors.push(HSVtoRGB([h,s,v]));
	}
	else
	{
		Colors.push(StartColor);
	}
  }
  else
  {
	  for (i= StartIndex; i<=EndIndex ; i++)
	  {
		Colors.push(HSVtoRGB(Temp_Colors[i]));
	  }
	  
	  if (Max % 10 && Max < MaxTemp)
	  {
		f=(Min%10)/10;
		var i = EndIndex;
		h=(Temp_Colors[i][0]+(Temp_Colors[i+1][0]-Temp_Colors[i][0])/10*f);
		s=(Temp_Colors[i][1]+(Temp_Colors[i+1][1]-Temp_Colors[i][1])/10*f);
		v=(Temp_Colors[i][2]+(Temp_Colors[i+1][2]-Temp_Colors[i][2])/10*f);		
		Colors.push(HSVtoRGB([h,s,v]));
	  }
  }  
  
  ret+=','+Colors.join(",")+")";
  
  return ret;
	
}


// Tests
console.log(get_tint(0,0));
console.log(get_tint(7,14));
console.log(get_tint(6,11));
console.log(get_tint(6,21));

</script>
<div class='fc_iconic'>


#if $varExists('forecast')

	#import time
	#set $t0 = time.time()

	## Which forecast should be displayed?
	#set $forecast_source = 'WU'

	## How many days should be considered?
	#set $num_days = 7

	## How big to make the bars, in pixels
	#set $bar_size = 150

	## Orientation can be vertical or horizontal
	#set $orientation = 'vertical'

	## Which data should be shown?
	#set $show_date = 1
	#set $show_pop = 1
	#set $show_precip = 1
	#set $show_obvis = 0

	#set $local_settings = dict()

	#set $WU_ICON_LABELS = ["Tornado","Tropical Storm","Hurricane","Strong Storms","Thunderstorms","Rain / Snow","Rain / Sleet","Wintry Mix","Freezing Drizzle","Drizzle","Freezing Rain","Showers","Rain","Flurries","Snow Showers","Blowing / Drifting Snow","Snow","Hail","Sleet","Blowing Dust / Sandstorm","Foggy","Haze","Smoke","Breezy","Windy","Frigid / Ice Crystals","Cloudy","Mostly Cloudy","Mostly Cloudy","Partly Cloudy","Partly Cloudy","Clear","Sunny","Fair / Mostly Clear","Fair / Mostly Sunny","Mixed Rain and Hail","Hot","Isolated Thunderstorms","Scattered Thunderstorms","Scattered Showers","Heavy Rain","Scattered Snow Showers","Heavy Snow","Blizzard","Not Available (N/A)","Scattered Showers","Scattered Snow Showers","Scattered Thunderstorms"]


	## First look for values from skin.conf or weewx.conf
	#if $varExists('Extras') and $varExists('Extras.forecast_iconic_settings')
		#for $sv in $Extras.forecast_iconic_settings.keys()
			#set $local_settings[$sv] = $Extras.forecast_iconic_settings[$sv]
		#end for
	#end if


	## Look for overrides defined by any template that includes this file
	#if $varExists('forecast_iconic_settings')
		#for $sv in $forecast_iconic_settings.keys()
			#set $local_settings[$sv] = $forecast_iconic_settings[$sv]
		#end for
	#end if

	## Now assign the values that will actually be used
	#set $forecast_source = $local_settings.get('source', $forecast_source)
	#set $num_days = int($local_settings.get('num_days', $num_days))
	#set $bar_size = int($local_settings.get('bar_size', $bar_size))
	#set $orientation = $local_settings.get('orientation', $orientation)
	#set $show_date = int($local_settings.get('show_date', $show_date))
	#set $show_pop = int($local_settings.get('show_pop', $show_pop))
	#set $show_precip = int($local_settings.get('show_precip', $show_precip))
	#set $show_obvis = int($local_settings.get('show_obvis', $show_obvis))

	## pre-calculate the periods
	#set $num_periods = $num_days * 24
	#set $periods = $forecast.weather_periods($forecast_source, max_events=$num_periods)

#if len($periods)

	## pre-calculate the ranges for each summary
	#set $start_ts = $t0
	#set $t_min = 200
	#set $t_max = -200
	#for $d in range($num_days)
		#set $summary = $forecast.weather_summary($forecast_source, $start_ts + $d * 24*3600, periods=$periods)
		#if $summary.tempMin.raw is not None and $summary.tempMin.raw < $t_min
			#set $t_min = $summary.tempMin.raw
		#end if
		#if $summary.tempMax.raw is not None and $summary.tempMax.raw > $t_max
			#set $t_max = $summary.tempMax.raw
		#end if
	#end for

	#if $orientation == 'vertical'

	#set $Id=0

	<table class='iconic-vertical'>
	## emit one row for each day
	#for $d in range($num_days)
		#set $summary = $forecast.weather_summary($forecast_source, $start_ts + $d * 24*3600, periods=$periods)

		#set $offset_width = 0
		#set $range_width = 0
		#set $trailing_width = 0
		#if $summary.tempMin.raw is not None and $summary.tempMax.raw is not None
			#set $lo = $bar_size * ($summary.tempMin.raw - $t_min) / ($t_max - $t_min)
			#set $hi = $bar_size * ($summary.tempMax.raw - $t_min) / ($t_max - $t_min)
			#set $offset_width = int($lo)
			#set $range_width = int($hi) - $offset_width
			#set $trailing_width = $bar_size - int($hi)
			#set $Id = $Id+1
		#end if
		<tr>
		<td class='col-outlook'>
		#if $summary.clouds is not None
			#set $simg = 'icons/' + ("00"+str($summary.clouds))[-2:] + '.png'
			#set $WUTitle=$summary.clouds
			
			#if $WUTitle is not None and $WUTitle.isdigit()
				#set $WUTitle=int($WUTitle)
			#else
				#set $WUTitle='N/A'
			#end if

			<img class='outlook-img' src='$simg' alt='$WU_ICON_LABELS[int($summary.clouds)]' title='$WU_ICON_LABELS[int($summary.clouds)]' />
		#end if
		</td>
		<td class='col-day'>
		  $summary.event_ts.format('%a')
		#if $show_date
		  <br/>$summary.event_ts.format('%d')
		#end if
		</td>
		<td>
		  <div class='temp' style='width:${offset_width}px'>&nbsp;</div>
		  <div class='temp'>$summary.tempMin.nolabel('%.0f')</div>
		  <div Id='Temp $Id' class='temp temp-range' style='width:${range_width}px'>&nbsp;
		  <script>
			document.getElementById("Temp $Id").style.background=  get_tint ($summary.tempMin.nolabel('%.0f'),$summary.tempMax.nolabel('%.0f'));
		  </script>
		  </div>
		  <div class='temp'>$summary.tempMax.nolabel('%.0f')</div>
		  <div class='temp' style='width:${trailing_width}px'>&nbsp;</div>
		</td>
		#if $show_pop
		<td class='col-pop'>$summary.pop.format('%.0f','')</td>
		#end if
		#if $show_precip
		<td class='col-precip'>
			#for $k in $summary.precip
				#set $precip_img = 'icons/' + $k + '.png'
		  <img class='precip-img' src='$precip_img' alt='$k' title='$forecast.label('Weather', $k)' />
			#end for
		</td>
		#end if

		#if $show_obvis
		<td class='col-obvis'>
			#for $k in $summary.obvis
				#set $obvis_img = 'icons/' + $k + '.png'
		  <img class='obvis-img' src='$obvis_img' alt='$k' title='$forecast.label('Weather', $k)' />
			#end for
		</td>
		#end if
	  </tr>
	#end for
	</table>

#else


<table class='iconic-horizontal'>
  <tr>
#for $d in range($num_days)
#set $summary = $forecast.weather_summary($forecast_source, $start_ts + $d * 24*3600, periods=$periods)
#set $offset_height = 0
#set $range_height = 0
#set $trailing_height = 0
#if $summary.tempMin.raw is not None and $summary.tempMax.raw is not None
#set $lo = $bar_size * ($summary.tempMin.raw - $t_min) / ($t_max - $t_min)
#set $hi = $bar_size * ($summary.tempMax.raw - $t_min) / ($t_max - $t_min)
#set $offset_height = $bar_size - int($hi)
#set $range_height = int($hi) - int($lo)
#set $trailing_height = int($lo)
#end if
    <td>
      <div class='row-day'>
        <span class='day'>$summary.event_ts.format('%a')</span>
#if $show_date
        <br/><span class='date'>$summary.event_ts.format('%d')</span>
#end if
      </div>
      <div class='row-outlook'>
#if $summary.clouds is not None
#set $simg = 'icons/' + $summary.clouds + '.png'
        <img class='outlook-img' src='$simg' alt='$summary.clouds' title='$forecast.label("Weather", $summary.clouds)' />
#end if
      </div>
      <div class='row-temp'>
        <div style='height:${offset_height}px'>&nbsp;</div>
        <div>$summary.tempMax.nolabel('%.0f')</div>
        <div id='Temp_$Id' class='temp-range' style='height:${range_height}px'>&nbsp;</div>
        <div>$summary.tempMin.nolabel('%.0f')</div>
        <div style='height:${trailing_height}px'>&nbsp;</div>
      </div>
#if $show_pop
      <div class='row-pop'>
        $summary.pop.format('%.0f','')
      </div>
#end if
#if $show_precip
      <div class='row-precip'>
  #for $k in $summary.precip
    #set $precip_img = 'icons/' + $k + '.png'
      <img class='precip-img' src='$precip_img' alt='$k' title='$forecast.label('Weather', $k)' /><br/>
  #end for
      </div>
#end if
#if $show_obvis
      <div class='row-obvis'>
  #for $k in $summary.obvis
    #set $obvis_img = 'icons/' + $k + '.png'
      <img class='obvis-img' src='$obvis_img' alt='$k' title='$forecast.label('Weather', $k)' /><br/>
  #end for
      </div>
#end if
    </td>
#end for
  </tr>
</table>


#end if

#else

<p>No forecast data for $forecast_source</p>

#end if

#set $t1 = time.time()
#set $elapsed = "%.3f" % ($t1 - $t0)
<!-- report generated in $elapsed s -->
<span class="small">Data Source : $forecast_source</span>
#else

<p>forecast_iconic: forecast search list extension is not installed</p>

#end if

</div>

