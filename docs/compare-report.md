---
title: The comparison report
layout: default
nav_order: 7
description: The compare skin, which plots every configured forecast source side by side so you can see which one is right for your location.
---

# The comparison report

The `compare` skin plots your configured sources against each other, so you can
see which one actually gets your location right over time.

## Enabling it

```
[StdReport]
    [[compare]]
        skin = compare
        HTML_ROOT = public_html/compare
```

Then restart WeeWX, or run it once with `weectl report run compare`.

## Requirements

- **Pillow (PIL)** for image generation
- **the DejaVu fonts** — the `fonts-dejavu` package on Debian and Ubuntu
- **more than one forecast source** configured, since the point is comparison
- **about a day of retained forecast history**, so the "forecast over time"
  plots have something to draw

{: .note }
> A freshly installed station shows empty plots, and that is not a fault.  The
> report needs history it has not accumulated yet.  Give it a day.

## How it works

`ForecastPlotGenerator` builds a scratch database, draws its plots from it, and
deletes it at the end of every run.  On a station with a five-minute report
cycle this means `weewx.manager` logs a `Created and initialized table 'archive'`
line every five minutes.  That is by design, not a symptom.

The scratch database is created under your `SQLITE_ROOT`.  A station configured
for MySQL only, with no SQLite root, gets a process-stamped file in the system
temporary directory instead.

On WeeWX 5.5 and later the generator honours the shutdown flag WeeWX hands to
report generators, checking it while scanning the forecast database, while
collecting data, and between plots — so stopping WeeWX partway through a report
no longer waits for every plot to finish.  Earlier WeeWX releases have no such
flag and are unaffected.
