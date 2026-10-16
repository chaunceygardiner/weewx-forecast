# weewx-forecast — weather and tide forecasts for WeeWX
Open source plugin for WeeWX software.

Copyright (C)2013-2020 by Matthew Wall

Copyright (C)2020-2026 by John A Kline (john@johnkline.com)

[![Read the manual](assets/btn-manual.svg)](https://chaunceygardiner.github.io/weewx-forecast/)
[![Download weewx-forecast.zip](assets/btn-download.svg)](https://github.com/chaunceygardiner/weewx-forecast/releases/latest/download/weewx-forecast.zip)
[![Report an issue](assets/btn-issue.svg)](https://github.com/chaunceygardiner/weewx-forecast/issues)

The manual covers installation, every option of all nine forecast sources, the
`$forecast` template tags, the labels you can translate, the comparison report
and troubleshooting — with search.

**This extension requires WeeWX 4 or 5.  Tide (xtide) and UK Met Office
forecasts additionally require Python 3.7 or later; WeeWX 5 already requires
Python 3.7 or later, so that affects only WeeWX 4 stations.**

Originally written by Matthew Wall; maintained since 2020 by John A Kline.

## Description

weewx-forecast adds forecasting to WeeWX.  Some sources are **downloaded** from
a public weather service; two are **generated** on your own machine from data
you already have.  You enable only the ones you want, every source you enable
writes into the same forecast database, and your templates read them all the
same way.

Only three sources need no account at all — and one of those, Zambretti, needs
no network connection either, because it forecasts from your own barometer.

## The nine sources

| Source | What it is | Needs |
|:-------|:-----------|:------|
| **NWS** | US National Weather Service point forecasts | a forecast office and location id — no account |
| **Zambretti** | A forecast computed from your own pressure trend | nothing at all |
| **XTide** | Tide predictions | the `xtide` program, installed locally |
| **WU** | Weather Underground | an API key |
| **OWM** | OpenWeatherMap | an API key |
| **UKMO** | UK Met Office Global Spot | an API key |
| **Aeris** | Aeris Weather | a client id and secret |
| **WWO** | World Weather Online | an API key |
| **DS** | Pirate Weather, the drop-in Dark Sky replacement | an API key |

→ [Every source's options, and where to get each API key](https://chaunceygardiner.github.io/weewx-forecast/sources.html)

This extension supports only the no-cost service level of the subscription
sources.  A source you have not configured costs nothing: it logs one message
at startup naming what is missing, never binds, and does no work thereafter.

## What you get

- **A forecast engine** that downloads or generates the data, on its own
  thread, one thread per source, so a slow or unreachable service never holds
  up your archive cycle.
  → [Configuration](https://chaunceygardiner.github.io/weewx-forecast/configuration.html)

- **One normalized database** for all nine sources, so a template that reads
  NWS reads Pirate Weather the same way.  It lives in SQLite by default, or in
  MySQL or MariaDB.
  → [Where the data goes](https://chaunceygardiner.github.io/weewx-forecast/configuration.html#where-the-data-goes)

- **A search list extension** giving reports `$forecast.weather_periods('NWS')`,
  `$forecast.weather_summary('NWS')`, `$forecast.zambretti.code`,
  `$forecast.xtide(0).hilo` and the rest.
  → [Template tags](https://chaunceygardiner.github.io/weewx-forecast/tags.html)

- **Four ready-made layouts**, each a Cheetah include you can drop into your own
  templates: a table with time running down the page, a strip with time running
  left to right, an icon-led horizontal timeline, and a condensed summary.
  → [Skins and labels](https://chaunceygardiner.github.io/weewx-forecast/skins.html)

- **An icon set** for cloud cover, storms, rain, snow, sleet, freezing rain and
  hail, derived from Adam Whitcroft's climacons.

- **Every label overridable**, which is also how you translate the extension —
  no text is hard-coded in English.
  → [The complete label reference](https://chaunceygardiner.github.io/weewx-forecast/skins.html#labels)

- **An optional comparison report** that plots your configured sources against
  each other, so you can see which one actually gets your location right.
  → [The comparison report](https://chaunceygardiner.github.io/weewx-forecast/compare-report.html)

## Installation

Download `weewx-forecast.zip` from the
[latest release](https://github.com/chaunceygardiner/weewx-forecast/releases/latest).

For WeeWX 5, pip install (`weectl` lives in the virtual environment, so
activate it first; yours may sit elsewhere, `~/weewx-venv` is the usual place):

```
source ~/weewx-venv/bin/activate
weectl extension install weewx-forecast.zip
```

For WeeWX 5, Debian or Red Hat package install (`weectl` is already on the
path, and that install put your account in the `weewx` group, which owns the
files):

```
weectl extension install weewx-forecast.zip
```

For WeeWX 4:

```
sudo wee_extension --install weewx-forecast.zip
```

On a setup.py install, use the full path — e.g.
`/home/weewx/bin/wee_extension`.

Then restart WeeWX.

The installer writes a fully commented `[Forecast]` section into `weewx.conf`,
so the options and the API keys you need are explained where you edit them.
Fill in the sources you want and remove the ones you do not from
`archive_services`.

→ [Full installation instructions, including building xtide for tide forecasts](https://chaunceygardiner.github.io/weewx-forecast/installation.html)

## Almanac

If you would like a Skyfield-based almanac in WeeWX (accurate sun, moon, and
planet rise/set and phase data), install
[weewx-skyfield](https://github.com/chaunceygardiner/weewx-skyfield); it works
alongside weewx-forecast.

Do not use `weewx-skyfield-almanac` — it introduced breaking changes that
cause problems.  Use `weewx-skyfield`.

## Credits

Icons were derived from Adam Whitcroft's climacons.

## Licensing

weewx-forecast is licensed under the GNU Public License v3.
