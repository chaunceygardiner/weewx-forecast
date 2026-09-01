---
title: Installation
layout: default
nav_order: 2
description: Installing weewx-forecast on WeeWX 4 or 5, building xtide for tide forecasts, and what the installer writes into weewx.conf.
---

# Installation

## Requirements

| | |
|:--|:--|
| **WeeWX** | 4.0 or later, including WeeWX 5 |
| **Python** | 3.7 or later, **for tide and UK Met Office forecasts only** |
| **xtide** | only if you want tide forecasts — see [below](#building-and-installing-xtide) |
| **Pillow and DejaVu fonts** | only for the [comparison report](compare-report.md) |

{: .note }
> Two sources need Python 3.7: XTide, and the UK Met Office.  The other seven
> run on earlier Pythons.  If you are on WeeWX 4 with Python 3.5 or 3.6, each
> of those two logs that it requires Python 3.7 or later and declines to run;
> everything else carries on normally.  WeeWX 5 requires Python 3.7 or later
> anyway, so its users are never affected.

## Installing the extension

Download `weewx-forecast.zip` from the
[latest release](https://github.com/chaunceygardiner/weewx-forecast/releases/latest),
then run the installer for your kind of WeeWX install.

**WeeWX 5, pip install.**  `weectl` lives in the virtual environment, so activate
it first.  Yours may sit elsewhere; `~/weewx-venv` is the usual place.

```
source ~/weewx-venv/bin/activate
weectl extension install weewx-forecast.zip
```

**WeeWX 5, Debian or Red Hat package install.**  `weectl` is already on the path.
No `sudo`: that install put your account in the `weewx` group, which owns the
files.  If you installed WeeWX in this same login session, log out and back in
first so the group membership takes effect.

```
weectl extension install weewx-forecast.zip
```

**WeeWX 4.**  That layout is root-owned, so this one does need `sudo`.

```
sudo wee_extension --install weewx-forecast.zip
```

On a setup.py install, use the full path -- e.g.
`/home/weewx/bin/wee_extension`.  The package installs put the utility in
`/usr/bin`, which is on `sudo`'s path; `/home/weewx/bin` is not.

Then restart WeeWX.

## What the installer writes

The installer adds a commented `[Forecast]` section to `weewx.conf`, along with
the `[DataBindings]`, `[Databases]` and `[StdReport]` entries the extension
needs.  Every option arrives with a comment explaining what it is and, where an
API key is required, where to get one.

It also appends **all nine** forecast services to `archive_services`.  A source
whose credentials are still `INSERT_..._HERE` placeholders logs one error at
startup naming what is missing and then does nothing at all — it never binds, so
the message does not repeat and it costs no time on any archive cycle.  Remove
the sources you do not use from `archive_services` if you would rather not see
those startup messages.

{: .note }
> The installer never rewrites sections that already exist, so upgrading an
> existing station leaves your settings — and your API keys — untouched.

Next, fill in the placeholders for the sources you want: see
[Configuration](configuration.md) and [Forecast sources](sources.md).

## Building and installing xtide

Skip this unless you want tide forecasts.

Current versions of Debian (trixie) do not package xtide, and this is likely
true of other distributions, so it must be built.  It is easiest to save the
following as a script and run it.

```
# Install dependencies
sudo apt install build-essential libpng-dev

# Download and install libtcd
cd /tmp
wget https://flaterco.com/files/xtide/libtcd-2.2.7-r2.tar.bz2
tar xf libtcd-2.2.7-r2.tar.bz2
cd libtcd-2.2.7
./configure
make
sudo make install
sudo ldconfig

# Download and build xtide
cd /tmp
wget https://flaterco.com/files/xtide/xtide-2.16.tar.xz
tar xf xtide-2.16.tar.xz
cd xtide-2.16
./configure --without-x --disable-shared CPPFLAGS="-I/usr/local/include" LDFLAGS="-L/usr/local/lib"
make
sudo make install

# Download harmonics data
cd /tmp
wget https://flaterco.com/files/xtide/harmonics-dwf-20251228-free.tar.xz
tar xf harmonics-dwf-20251228-free.tar.xz
cd harmonics-dwf-20251228
sudo mkdir -p /usr/local/share/xtide
sudo cp harmonics-dwf-20251228-free.tcd /usr/local/share/xtide/

# Create conf file
echo "/usr/local/share/xtide" | sudo tee /etc/xtide.conf
```

Verify it works, running as the user WeeWX runs under:

```
/usr/local/bin/tide -l "Palo Alto Yacht Harbor"
```

List the station names xtide knows with `tide -ml`.  Then point the extension at
the program you just built:

```
[Forecast]
    [[XTide]]
        location = Palo Alto Yacht Harbor, San Francisco Bay, California
        prog = /usr/local/bin/tide
```

{: .important }
> Station names routinely contain commas.  weewx-forecast handles that, but the
> name must match one xtide knows — copy it from `tide -ml` rather than
> shortening it.

## Uninstalling

```
weectl extension uninstall forecast
```

on WeeWX 5, or `wee_extension --uninstall forecast` on WeeWX 4.  This leaves the
forecast database in place; delete `archive/forecast.sdb` yourself if you want
it gone.
