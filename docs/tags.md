---
title: Template tags
layout: default
nav_order: 5
description: The $forecast tags weewx-forecast makes available to Cheetah templates -- tides, Zambretti, weather periods and daily summaries.
---

# Template tags

Add the search-list extension to any report that needs forecast data:

```
[StdReport]
    [[StandardReport]]
        [[[CheetahGenerator]]]
            search_list_extensions = user.forecast.ForecastVariables
```

Everything below then hangs off `$forecast`.

## Fields every forecast carries

| Tag | Meaning |
|:----|:--------|
| `dateTime` | When the forecast was requested |
| `issued_ts` | When the source issued the forecast |
| `event_ts` | The time the forecast is *for* |

## Tides

`$forecast.xtide(index)` returns the *n*th tide event from now, counting from 0.

```
$forecast.xtide(0).event_ts     date/time of the event
$forecast.xtide(0).hilo         H or L
$forecast.xtide(0).offset       depth above/below mean low tide
$forecast.xtide(0).location     where the tide is forecast
```

To walk a series of them, use `$forecast.xtides`:

```
#for $tide in $forecast.xtides
  $tide.event_ts $tide.hilo $tide.offset
#end for
```

`$forecast.xtides` accepts `from_ts` (default: now), `max_events` (default 45)
and `startofday` (default false — set it true to begin at midnight rather than
the current moment).

Use [`$forecast.label('Tide', ...)`](skins.md#tide-labels) to turn `H` and `L`
into words.

## Zambretti

A Zambretti forecast is one code with one description.

```
$forecast.zambretti.event_ts    date/time of the forecast
$forecast.zambretti.code        the code, A through Z
```

Turn the code into text with `$forecast.label('Zambretti', $forecast.zambretti.code)`
— see [Zambretti codes](skins.md#zambretti-codes) for all 26.

## Weather forecasts

These apply to the seven downloading weather sources: `NWS`, `WU`, `OWM`,
`UKMO`, `Aeris`, `WWO` and `DS`.  Every call names the source it wants.

### Periods

A period is one forecast interval — three hours, an hour, a day, depending on
the source and its `forecast_type`.

```
#for $period in $forecast.weather_periods('NWS')
  $period.event_ts
  $period.temp
  $period.pop
#end for
```

`weather_periods` accepts `from_ts`, `to_ts` and `max_events` (default 240).

### Daily summaries

A summary aggregates every period falling in one day.

```
#set $summary = $forecast.weather_summary('NWS')
```

| Tag | |
|:----|:--|
| `event_ts`, `dateTime`, `location` | |
| `clouds` | Sky cover code |
| `temp`, `tempMin`, `tempMax` | |
| `dewpoint`, `dewpointMin`, `dewpointMax` | |
| `humidity`, `humidityMin`, `humidityMax` | |
| `windSpeed`, `windSpeedMin`, `windSpeedMax` | |
| `windGust` | |
| `windDir`, `windChar` | The prevailing value |
| `windDirs`, `windChars` | Dictionaries of all values seen that day |
| `pop` | Probability of precipitation |
| `precip` | Array of precipitation codes |
| `obvis` | Array of obstruction-to-visibility codes |

`weather_summary` accepts `ts` to pick a different day, and `periods` to
summarize a set of periods you already have.

## Labels

`$forecast.label(module, key)` looks up the human-readable text for a code.

```
$forecast.label('Zambretti', 'C')     →  Becoming fine
$forecast.label('Weather', 'temp')    →  Temperature
$forecast.label('Tide', 'H')          →  High Tide
$forecast.label('Directions', 'NNE')  →  NNE
```

Every label is overridable in `skin.conf` — see [Skins and labels](skins.md),
which is also how you translate the extension into another language.

## Other

| Tag | |
|:----|:--|
| `$forecast.version` | The extension's version string |
| `$forecast.almanac(ts)` | Almanac data for a timestamp |
