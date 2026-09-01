---
title: Skins and labels
layout: default
nav_order: 6
description: The sample forecast skin, its display options, and the complete set of overridable labels -- how to reword or translate every code weewx-forecast emits.
---

# Skins and labels

## The sample skin

The installer adds a `forecast` skin with four ready-made layouts, each a
Cheetah include you can drop into your own templates:

| Include | Layout |
|:--------|:-------|
| `forecast_table.inc` | A table, time running down the page |
| `forecast_strip.inc` | A strip, time running left to right |
| `forecast_iconic.inc` | An icon-led horizontal timeline |
| `forecast_compact.inc` | A condensed icon summary |

Each begins with a block of variables controlling what it displays — which
source to read, how many periods to show, which rows appear.  Edit those at the
top of the file rather than the markup below.

The skin also ships the icon set: cloud cover, storms, rain, snow, sleet,
freezing rain, hail and the rest.

## Labels

Every code the extension emits has a label, and every label can be overridden in
`skin.conf` under `[Forecast] [[Labels]]`.  Add only the ones you are changing;
anything you leave out keeps its default.  This is also how you translate the
extension — nothing is hard-coded in English.

```
[Forecast]
    [[Labels]]
        [[[Tide]]]
            H = Marée haute
            L = Marée basse
```

### Tide labels

| Code | Default |
|:-----|:--------|
| `H` | High Tide |
| `L` | Low Tide |

### Compass directions

`N`, `NNE`, `NE`, `ENE`, `E`, `ESE`, `SE`, `SSE`, `S`, `SSW`, `SW`, `WSW`, `W`,
`WNW`, `NW`, `NNW` — each defaults to itself, so overriding them is purely for
translation.

### Zambretti codes

| | | | |
|:--|:--|:--|:--|
| `A` Settled fine | `H` Fairly fine, showery later | `O` Showery, becoming less settled | `V` Rain at times, very unsettled |
| `B` Fine weather | `I` Showery early, improving | `P` Changeable, some rain | `W` Rain at frequent intervals |
| `C` Becoming fine | `J` Changeable, mending | `Q` Unsettled, short fine intervals | `X` Rain, very unsettled |
| `D` Fine, becoming less settled | `K` Fairly fine, showers likely | `R` Unsettled, rain later | `Y` Stormy, may improve |
| `E` Fine, possible showers | `L` Rather unsettled clearing later | `S` Unsettled, some rain | `Z` Stormy, much rain |
| `F` Fairly fine, improving | `M` Unsettled, probably improving | `T` Mostly very unsettled | |
| `G` Fairly fine, possible showers early | `N` Showery, bright intervals | `U` Occasional rain, worsening | |

### Weather components

`temp` Temperature · `dewpt` Dewpoint · `humidity` Relative Humidity ·
`winddir` Wind Direction · `windspd` Wind Speed · `windchar` Wind Character ·
`windgust` Wind Gust · `clouds` Sky Coverage · `windchill` Wind Chill ·
`heatindex` Heat Index · `obvis` Obstructions to Visibility

### Precipitation types

`rain` Rain · `rainshwrs` Rain Showers · `sprinkles` Rain Sprinkles ·
`tstms` Thunderstorms · `drizzle` Drizzle · `snow` Snow ·
`snowshwrs` Snow Showers · `flurries` Snow Flurries · `sleet` Ice Pellets ·
`frzngrain` Freezing Rain · `frzngdrzl` Freezing Drizzle · `hail` Hail

### Sky cover

| Code | Default |
|:-----|:--------|
| `CL` | Clear |
| `FW` | Few Clouds |
| `BK` | Broken Clouds |
| `B1` | Mostly Cloudy |
| `B2` | Considerable Cloudiness |
| `OV` | Overcast |

### Precipitation likelihood and coverage

| Code | Default | Quantifier | |
|:-----|:--------|:-----------|:--|
| `S` | Slight Chance | `Sq` | `<20%` |
| `C` | Chance | `Cq` | `30-50%` |
| `L` | Likely | `Lq` | `60-70%` |
| `O` | Occasional | `Oq` | `80-100%` |
| `D` | Definite | `Dq` | `80-100%` |
| `IS` | Isolated | `ISq` | `<20%` |
| `NM` | Numerous | `NMq` | `60-70%` |
| `EC` | Extensive | `ECq` | `80-100%` |
| `PA` | Patchy | `PAq` | `<25%` |
| `AR` | Areas | `ARq` | `25-50%` |
| `WD` | Widespread | `WDq` | `>50%` |

| `SC` | Scattered | `SCq` | `30-50%` |

{: .important }
> **`SC` means "Scattered", not "Scattered Clouds".**  Sky cover and
> precipitation coverage share one namespace, and coverage won: `forecast.py`
> ships `'SC': 'Scattered Clouds'` **commented out**, so an NWS sky-cover value
> of `SC` renders as `Scattered`.  There is no separate sky-cover label for it.
> Override `SC` and you change both meanings at once.

### Aeris weather types

Aeris reports its own weather codes, each with its own label:

| | | | |
|:--|:--|:--|:--|
| `A` Hail | `IP` Ice Pellets/Sleet | `SW` Snow Showers | `ZF` Freezing Fog |
| `BR` Mist | `R` Rain | `T` Thunderstorms | `ZL` Freezing Drizzle |
| `BY` Blowing Spray | `RW` Rain Showers | `UP` Unknown Precipitation | `ZR` Freezing Rain |
| `FR` Frost | `RS` Rain/Snow Mix | `VA` Volcanic Ash | `ZY` Freezing Spray |
| `IC` Ice Crystals | `SI` Snow/Sleet Mix | `WP` Waterspouts | |
| `IF` Ice Fog | `WM` Wintry Mix | | |

{: .note }
> Aeris's `L` (Drizzle) and `S` (Snow) are commented out in `forecast.py` for
> the same namespace reason as `SC`: `L` is already Likely and `S` is already
> Slight Chance in the coverage table above.

### Obstructions to visibility

`F` Fog · `PF` Patchy Fog · `F+` Dense Fog · `PF+` Patchy Dense Fog ·
`H` Haze · `BS` Blowing Snow · `K` Smoke · `BD` Blowing Dust ·
`AF` Volcanic Ash · `M` Mist · `FF` Freezing Fog · `DST` Dust · `SND` Sand ·
`SP` Spray · `DW` Dust Whirls · `SS` Sand Storm · `LDS` Low Drifting Snow ·
`LDD` Low Drifting Dust · `LDN` Low Drifting Sand · `BN` Blowing Sand ·
`SF` Shallow Fog

### Wind character

| Code | Default |
|:-----|:--------|
| `LT` | Light |
| `GN` | Gentle |
| `BZ` | Breezy |
| `WY` | Windy |
| `VW` | Very Windy |
| `SD` | Strong/Damaging |
| `HF` | Hurricane Force |
