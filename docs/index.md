---
title: Home
layout: default
nav_order: 1
permalink: /
description: Weather and tide forecasts for WeeWX from nine sources, plus Zambretti forecasts from your own barometer and XTide tide predictions.
---

# weewx-forecast — weather and tide forecasts for WeeWX

**Nine forecast sources in one extension**, stored in one database and reachable
from your reports through a single set of `$forecast` tags.

[View on GitHub](https://github.com/chaunceygardiner/weewx-forecast){: .btn .btn-primary }
[Download weewx-forecast.zip](https://github.com/chaunceygardiner/weewx-forecast/releases/latest/download/weewx-forecast.zip){: .btn }
[Report an issue](https://github.com/chaunceygardiner/weewx-forecast/issues){: .btn }

weewx-forecast adds forecasting to WeeWX.  Some sources are **downloaded** from a
public weather service; two are **generated** on your own machine from data you
already have.  You enable only the ones you want, and every source you enable
writes into the same forecast database, so your templates read them all the same
way.

## The sources

| Source | What it is | Needs |
|:-------|:-----------|:------|
| [NWS](sources.md#nws)         | US National Weather Service point forecasts | a forecast office and location id — no account |
| [Zambretti](sources.md#zambretti) | A forecast computed from your own pressure trend | nothing at all |
| [XTide](sources.md#xtide)     | Tide predictions | the `xtide` program, installed locally |
| [WU](sources.md#wu)           | Weather Underground | an API key |
| [OWM](sources.md#owm)         | OpenWeatherMap | an API key |
| [UKMO](sources.md#ukmo)       | UK Met Office Global Spot | an API key |
| [Aeris](sources.md#aeris)     | Aeris Weather | a client id and secret |
| [WWO](sources.md#wwo)         | World Weather Online | an API key |
| [DS](sources.md#ds)           | Pirate Weather, the drop-in Dark Sky replacement | an API key |

Only NWS, Zambretti and XTide work without signing up for anything.  Zambretti
needs no network connection whatsoever — it reads your own barometer.

{: .note }
> This extension supports only the no-cost service level of the subscription
> sources.  A source you have not configured costs nothing: it logs one message
> at startup naming what is missing, never binds, and does no work thereafter.

## Where to go next

- **[Installation](installation.md)** — installing the extension, and building
  `xtide` if you want tides.
- **[Configuration](configuration.md)** — the `[Forecast]` section of
  `weewx.conf`, and every option common to all sources.
- **[Forecast sources](sources.md)** — each source's own options, and where to
  get its API key.
- **[Template tags](tags.md)** — the `$forecast` variables your reports use.
- **[Skins and labels](skins.md)** — the sample skin, and translating or
  rewording every label.
- **[The comparison report](compare-report.md)** — plots that put the sources
  side by side.
- **[Troubleshooting](troubleshooting.md)** — reading the log, and the
  command-line test harness.

## Requirements

WeeWX 4 or 5.  Tide and UK Met Office forecasts additionally require Python 3.7
or later; WeeWX 5 already requires Python 3.7 or later, so this only affects
WeeWX 4 stations.
See [Installation](installation.md#requirements).
