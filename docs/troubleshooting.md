---
title: Troubleshooting
layout: default
nav_order: 8
description: Reading weewx-forecast's log messages, and using its command-line harness to test a source's download and parsing without running WeeWX.
---

# Troubleshooting

## Start with the log

Every source logs one line at startup naming the options it read, which is the
quickest way to confirm your configuration reached the code:

```
Zambretti: interval=600 max_age=604800 winddir_period=1800 ... hemisphere=NORTH
NWS: interval=10800 max_age=604800 lid=MAZ014 lid_desc=None foid=BOX
XTide: interval=1209600 max_age=2419200 location='Boston, Boston Harbor, Massachusetts' duration=2419200
```

API keys are obfuscated in these lines, so they are safe to paste when asking
for help.

### "forecast will not be run"

A source logs this, preceded by a line naming what is missing, when it cannot
start — a placeholder API key, no location, no `lid`.  It then does nothing at
all for the life of the process: it never binds, so the message appears **once**
at startup and never repeats, and the source costs nothing on any archive cycle.

This is the expected state for every source you have not configured, because the
installer enables all nine.  To silence them, remove the ones you do not use from
`archive_services` — see
[Configuration](configuration.md#enabling-and-disabling-sources).

### "... require Python 3.7 or later"

Two sources need Python 3.7 and say so if they do not have it: XTide, whose tide
generation calls `subprocess.run(capture_output=...)`, and UKMO, whose parser
calls `datetime.fromisoformat`.  You are on WeeWX 4 with an older Python.  The
other seven sources continue to work; only these two decline.  See
[Installation](installation.md#requirements).

### No data in your report

Check, in order:

1. The source logged its startup line and *not* "forecast will not be run".
2. `search_list_extensions = user.forecast.ForecastVariables` is set for that
   report — see [Configuration](configuration.md#making-forecasts-available-to-reports).
3. The database has rows.  `sqlite3 archive/forecast.sdb "select method, count(*) from archive group by method;"`
   shows what each source has actually written.
4. Enough time has passed for the source's `interval` to have elapsed at least
   once.

## The command-line harness

`forecast.py` can download and parse a forecast on its own, without WeeWX
running, which separates "the service is unreachable" from "the parser is
wrong".  Run it with the Python that runs WeeWX.

On WeeWX 5, activate the environment if you have a pip install, then:

```
python3 ~/weewx-data/bin/user/forecast.py --help
```

On WeeWX 4:

```
PYTHONPATH=/home/weewx/bin python3 /home/weewx/bin/user/forecast.py --help
```

Adjust the path to wherever your `bin/user` actually is; the examples below
write it as `forecast.py` for brevity.

Download a forecast and print it:

```
forecast.py --action=download --method=nws --lid=MAZ014 --foid=BOX
forecast.py --action=download --method=wu --api-key=KEY --loc=02139
forecast.py --action=download --method=ukmo --api-key=KEY --latitude=51.5 --longitude=-0.07
forecast.py --action=download --method=xtide --loc="Boston, Boston Harbor, Massachusetts" --prog=/usr/local/bin/tide
```

Parse a saved file and print the records it yields:

```
forecast.py --action=parse --method=nws --filename=forecast.txt --lid=MAZ014
forecast.py --action=parse --method=ukmo --filename=forecast.txt --latitude=51.5 --longitude=-0.07
```

{: .note }
> UKMO takes `--latitude` and `--longitude`, not `--loc`.  It is the one source
> keyed by coordinates rather than a location name.

## Saving raw and failed forecasts

Set `save_raw` to keep each downloaded document, and `save_failed` to keep the
ones whose parsing produced messages.  Both write into your WeeWX directory and
are the right attachment for a bug report about a mis-parsed forecast.

## Reporting a problem

Open an issue at
<https://github.com/chaunceygardiner/weewx-forecast/issues> with your WeeWX
version, your Python version, the source involved, the startup line from the
log, and — for a parsing problem — the saved raw forecast.
