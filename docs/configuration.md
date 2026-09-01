---
title: Configuration
layout: default
nav_order: 3
description: The [Forecast] section of weewx.conf, the options every source shares, and the database and service entries the installer writes.
---

# Configuration

Everything lives in a `[Forecast]` section of `weewx.conf`.  Options set
directly under `[Forecast]` apply to every source; the same option inside a
source's own subsection overrides it for that source alone.

```
[Forecast]
    # The database in which to record forecast information, defined in the
    # 'DataBindings' section of the weewx configuration.
    data_binding = forecast_binding

    # How often to calculate/download the forecast, in seconds
    #interval = 1800

    # How long to keep old forecasts, in seconds.  Use None to keep forever.
    #max_age = 604800

    [[Zambretti]]
        #hemisphere = NORTH

    [[NWS]]
        lid = MAZ005
        foid = BOX
```

## Options every source shares

| Option | Default | What it does |
|:-------|:--------|:-------------|
| `interval` | `1800` | How often to download or generate this forecast, in seconds.  Most sources override this — see the table below. |
| `max_age` | `604800` | How long to keep old forecasts, in seconds.  `None` keeps them forever. |
| `data_binding` | `forecast_binding` | Which binding to store records in.  Set once, under `[Forecast]`. |
| `single_thread` | `False` | Run the forecast on the main thread instead of its own. |
| `delay` | none | Seconds to wait before the first forecast after startup. |
| `vacuum` | `False` | Vacuum the database after pruning. |
| `database_max_tries` | `3` | Retries for a failing database operation. |
| `database_retry_wait` | `10` | Seconds between those retries. |
| `save_raw` | `False` | Keep every downloaded document.  See [Troubleshooting](troubleshooting.md#saving-raw-and-failed-forecasts). |
| `save_failed` | `False` | Keep documents whose parsing produced messages. |
| `diagnostic_dir` | none | Where `save_raw` and `save_failed` write. |

All of these are read the same way: set one under `[Forecast]` to change every
source, or inside a source's subsection to change that source alone.

Because `interval` and `max_age` are inherited, setting them under `[Forecast]`
changes every source at once, which is rarely what you want — a Zambretti
forecast costs nothing to recompute, while an API-key source has a request quota.
Set them per source instead.

### The default interval of each source

Each source ships with an interval suited to how often its data actually
changes.  These are the defaults if you set nothing:

| Source | Default `interval` | |
|:-------|-------------------:|:--|
| Zambretti | `600` | 10 minutes — computed locally, so it is cheap |
| NWS, WU, OWM, UKMO, Aeris, WWO, DS | `10800` | 3 hours |
| XTide | `1209600` | 14 days — tides are predicted, not observed |

XTide also sets `max_age` to `2419200` (28 days) and adds a `duration` of the
same length, being the span of time it asks xtide to predict.

## Enabling and disabling sources

The installer appends all nine services to `archive_services` in
`[Engine] [[Services]]`:

```
[Engine]
    [[Services]]
        archive_services = ..., user.forecast.ZambrettiForecast, user.forecast.NWSForecast, user.forecast.XTideForecast, user.forecast.WUForecast, user.forecast.OWMForecast, user.forecast.UKMOForecast, user.forecast.AerisForecast, user.forecast.WWOForecast, user.forecast.DSForecast
```

Remove the ones you do not want.  Leaving an unconfigured source in the list is
harmless — it logs once at startup and never binds — but removing it keeps the
log clean.

## Where the data goes

All nine sources write into a single table in a database of their own:

```
[DataBindings]
    [[forecast_binding]]
        database = forecast_sqlite

[Databases]
    [[forecast_sqlite]]
        database_type = SQLite
        database_name = archive/forecast.sdb
```

For MySQL, point the binding at a `forecast_mysql` database instead:

```
[Databases]
    [[forecast_mysql]]
        database_type = MySql
        database_name = forecast
```

One table holds every source's records, each tagged with its `method`.  That
means an individual record has many unused fields — a tide record has no
humidity — and those stay NULL.  This is deliberate: it keeps querying and
database management simple, and it keeps the number of template variables down.

Every record carries `method`, `event_ts` (when the forecast is *for*) and
`issued_ts` (when the source issued it), whatever its source.

## Making forecasts available to reports

Add the search-list extension to whichever report should see the data:

```
[StdReport]
    [[StandardReport]]
        [[[CheetahGenerator]]]
            search_list_extensions = user.forecast.ForecastVariables
```

Then use the [template tags](tags.md).  The installer already does this for the
sample `forecast` skin it installs.

## Threading

Forecasting runs on its own thread, one per source, and the main thread does not
wait for it.  No more than one thread per source runs at a time, so a slow or
unreachable service cannot pile up requests or hold up your archive cycle.
