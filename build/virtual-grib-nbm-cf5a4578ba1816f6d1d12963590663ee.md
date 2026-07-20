---
date: "2026-07-13"
title: "Virtually Gribberish - Bringing Icechunk clarity to GRIB archives"
description: |
  GRIB data is notoriously hard to work with, so we made it easy to create virtual Icechunk stores from GRIB archives such as the NOAA National Blend of Models, allowing cloud-optimized access to GRIB data archives without copying the data.
thumbnail: images/grib-on-a-boat.jpg
tags:
- icechunk
- zarr
- virtual-zarr
- virtualizarr
- grib
- noaa
kernelspec:
  name: python3
  display_name: 'Python 3'
---

(Originally posted on the [Earthmover blog](https://earthmover.io/blog/virtual-grib-nbm), co-authored with Matt Iannucci)

Tl;dr: The most important weather forecasts in the world are distributed in the 40-year-old GRIB format, but GRIB data is notoriously hard to work with in the cloud. We made it easy to create virtual Icechunk stores from GRIB archives such as the NOAA National Blend of Models, allowing cloud-optimized access to GRIB data archives without copying the data.

## GRIB is critical infrastructure

Some of the most important and widely-used weather forecasting models around the world - NOAA's GFS and HRRR, as well as ECMWF's IFS - are distributed in the decades old GRIB format.
Even cutting-edge AI-generated weather forecast models such as [ECMWF's AIFS](https://www.ecmwf.int/en/newsletter/178/news/aifs-new-ecmwf-forecasting-system) are being generated in GRIB2 format.
These operational systems underpin every use of modern weather forecast data globally, so clearly cannot be changed overnight.

## GRIB is great at sea

When GRIB was invented back in the late 1980s, its design made total sense.
As our engineer Deepak's incredible [historical deep dive](https://www.earthmover.io/blog/cloud-native-platforms-are-the-natural-evolution-of-atmosphere-ocean-open-data-practice#1960-1990-the-cold-war--world-weather-watch) explains, the World Meteorological Organisation planned for

> “WMO Member States and Territories [to] collaborat[e] to collectively operate a global observing system (GOS), [and] exchange the global observing system data through a global telecommunications system (GTS)”

where the GTS was a system of undersea telecom cables.

```{figure} images/gts-network-schematic.png
:alt: Schematic of WMO's GTS network
:width: 70%

Schematic of WMO's Global Telecommunication System (GTS) network ([source](https://www.jma.go.jp/jma/jma-eng/jma-center/rth/RTH_Tokyo.html)).
```

The **Gri**dded **B**inary format (GRIB), along with its tabular sibling [BUFR](https://en.wikipedia.org/wiki/BUFR), were designed to stream weather data reliably and efficiently over this telecom system.

These networks were unreliable, so to ensure data reached its destination intact, GRIB files are split into a series of "messages", each of which is self-describing and can be reassembled into a GRIB file.
If any message got corrupted, that data would be lost but the rest of the file could still be read.
This **streaming-friendly format** also allows omitting irrelevant messages while still leaving a valid GRIB to plot, which is useful for sending the minimal amount of information relevant to a specific user.
This is arguably a precursor to our modern paradigm of cloud-native formats downloading only the chunks needed to fulfill a request.

Since the GTS cables had what would now be considered very low bandwidth (e.g. 64 kbit/s), GRIB was also designed to **maximise compression** with compact encoding strategies.
They achieved this partially through the use of "external tables". Rather than repeating common pieces of metadata (such as "2-metre air temperature in Kelvin") in every message, an integer code (e.g. 11) is sent, and the receiver looks up what that code means in an "external table".

Sailors appreciate these features, since GRIB is still the preferred format for receiving weather forecasts while at sea.
In the middle of the ocean even a modern Iridium satellite connection only has a bandwidth of ~2 kbits/s - comparable to GTS, and a fraction of even 90s era dial-up household internet speeds.
Such a connection is also unreliable and intermittent, so GRIB's advantages are still very relevant.
For these reasons services like [Saildocs](http://www.saildocs.com/) became popular, where a sailor sends an email with a latitude-longitude box and receives an email back containing a minimal local forecast in GRIB format.
(Note that it would now be quite straightforward to build a similar service that delivers custom GRIBs on request derived from any dataset in the [Earthmover Marketplace](https://app.earthmover.io/marketplace) via a cloud-native data delivery service like [Flux](https://www.earthmover.io/blog/announcing-flux).)

## GRIB sucks in the cloud

So GRIB was designed for reliably delivering forecast data over the _worst networks you can imagine_.
In contrast, modern scientific data work happens in the cloud, where bandwidth between object storage and a single compute node is [~15GB/s](https://www.earthmover.io/blog/i-o-maxing-tensors-in-the-cloud), over _7 orders of magnitude faster_ than telecom or satellite connections.
Unfortunately in this modern cloud-native context many of GRIB's features make it notoriously hard to work with.

- **No enforced overall schema or consistency.** All messages within a GRIB file are independent, and all GRIB files within an archive are independent too. So nothing tells the user about the global structure of the GRIB dataset, nothing ensures the messages' contents form parts of some logical greater whole, and nothing enforces that the data stays consistent with any schema the provider declares their data obeys.
- **External tables mean GRIB files aren't fully self-describing.** Since the external table is a separate artifact, it's not included with the GRIB file.
Even worse, the tables allowed for some code numbers to vary with "local use", which over time led to a divergence between standards used by different data providers, creating the "two flavours" of GRIB people see today: "European" (from ECMWF) and "American" (from NWS/NCEP).
- **Only one allowed chunking strategy.** GRIB's structure assumes that each message contains the values of a field for a latitude-longitude grid for a single level.
This effectively fixes the allowed chunking scheme, and prevents storing any data that isn't on a latitude-longitude grid.
- **Efficient random access requires a separate index file.** While GRIB's per-message splitting thankfully allows fetching only relevant parts of a file, GRIB is still not a ["cloud-optimized format"](https://www.earthmover.io/blog/fundamentals-what-is-cloud-optimized-scientific-data) since there is no cheaply-fetchable top-level metadata describing the entire contents of the GRIB file or a collection of GRIB files.
Sometimes this metadata is provided as an auxiliary "GRIB index file", but that is not always the case, and again there is nothing to guarantee consistency.

```{figure} images/grib-on-a-boat.jpg
:alt: Two-panel cartoon: on the left, a curly-haired woman relaxes on her sailboat 'Serenity' in calm sunny seas, reading a GRIB wind forecast on her phone; on the right, the same sailor and boat are caught in a violent storm with towering waves and lightning, beneath a dark cloud reading 'GRIB CLOUD FAILURE'.
:width: 70%

GRIB shines when you're downloading a forecast over a trickle of satellite bandwidth from the middle of the ocean — but GRIB is rough to work with at scale in the cloud.
```

## Agencies provide GRIBs, but users want cloud-optimized datacubes

Meteorological agencies such as NOAA NCEP and ECMWF have spent decades building critical infrastructure to deliver their forecasts via GRIB, and continue to do so today.
But users don't want to worry about servers, GRIB messages, and external code tables.
Instead they just want direct access to the entire dataset in object storage, available in a cloud-optimized format.

This is the same conundrum we described in [our post on the GOES-16 satellite data archive](https://www.earthmover.io/blog/virtual-zarr): the data is only available in a legacy format, creating a usability barrier, but the data provider (and users) cannot simply copy the entire archive into a new format.

As with GOES, the solution is [_virtual chunks_](https://www.earthmover.io/blog/virtual-zarr#solution-cloud-optimised-virtual-stores-referencing-existing-files) - give users an Icechunk store containing virtual chunk references that point back to the contents of the original GRIB files.
By making targeted HTTP range requests to only the relevant parts of the GRIB files, this approach provides cloud-optimized access to the entire dataset as a single logical [datacube](https://www.earthmover.io/blog/what-is-zarr), without copying any of the data.

(PSA: Unfortunately this virtual references trick cannot work if the archival file was then further compressed with a tool like gzip, which some data providers choose to do.
In that case you can still use Gribberish and Xarray to ingest the GRIB data into Icechunk as native chunks, at the cost of duplicating the data.)

## Gribberish understands GRIB files

Interpreting the contents of the GRIB files requires some GRIB-specific tool.
We use an open-source Rust library originally written by our very own Earthmover engineer Matt Iannucci - the pithily named ["Gribberish"](https://github.com/mpiannucci/gribberish).

We recently released Gribberish 1.0, which amongst other things added [support](https://github.com/mpiannucci/gribberish/blob/main/python/README.md#virtualizarr) for using Gribberish to create zero-copy virtual references to the contents of GRIB files, via its new [VirtualiZarr](https://virtualizarr.readthedocs.io/en/stable/)-compatible `GribberishParser`.

Gribberish also provides a [dedicated Zarr codec](https://github.com/mpiannucci/gribberish/blob/main/python/README.md#zarr) for decoding the specific compression strategy used by GRIB files.

## VirtualiZarr organizes GRIB contents

Since there is no global schema for a collection of GRIB files/messages, there is no one correct way to map the contents of a GRIB dataset to a Zarr-like datacube.
Our solution is to let the data provider decide how they want to arrange the contents of their GRIBs.

We achieve this flexibility by having Gribberish choose an initial default structure, but then leveraging the python library [VirtualiZarr](https://github.com/zarr-developers/VirtualiZarr)'s ability to alter schema and metadata arbitrarily during ingestion.
The Xarray interface to VirtualiZarr then allows moving groups, concatenating variables, renaming variables/groups/dimensions, and correcting metadata.
VirtualiZarr's support for nested groups via `xarray.DataTree` is also extremely helpful here, since complex sets of related GRIB messages often decode to deeply nested hierarchies by default.

For example, opening a single NBM GRIB file with VirtualiZarr's `open_virtual_datatree` returns an `xarray.DataTree` whose default structure mirrors how Gribberish grouped the messages:

```python
from virtualizarr import open_virtual_datatree
from gribberish.virtualizarr import GribberishParser

parser = GribberishParser(use_index="auto")
vdt = open_virtual_datatree(url, registry=registry, parser=parser)
vdt
```

```{figure} images/nbm-datatree.png
:alt: xarray HTML repr of the xarray.DataTree produced from a single NBM GRIB file, showing top-level groups such as /asl, /atm, /clb, /cld_ceiling, /clt, /entire_atm, /hcl, /isobar, /local195, /local196, /local197 and /sfc, each with a count of child groups.
:width: 90%

xarray's HTML repr of the `xarray.DataTree` produced from a single NBM GRIB file. Gribberish's default grouping splits the messages by their GRIB fixed-surface / level type (e.g. `/asl` above sea level, `/atm` whole atmosphere, `/isobar` isobaric levels, `/sfc` surface), and nests a further split by statistic (`/instant`, `/acc1h`, `/derived`) within each — producing the deeply nested hierarchy that VirtualiZarr then lets the provider reshape.
```

This initial representation can then be easily and cheaply manipulated into the most user-friendly structure.
Overall this provides a practical way for data providers to present the data in a way that makes most sense for their users, rather than being tied to the structure and conventions of the original GRIB files.
This is possible without duplicating data storage since we are only manipulating metadata, not the original binary data values.

(Note that when GRIB index files are available much of this process can be short-circuited via an [option to Gribberish](https://github.com/mpiannucci/gribberish/blob/main/python/README.md#sidecar-index-files-idx--index), since the index files effectively provide a global schema and the virtual references in one go.)

## Example: NOAA National Blend of Models archive

To test these new capabilities, we used Gribberish and VirtualiZarr to ingest the [NOAA National Blend of Models](https://vlab.noaa.gov/web/mdl/nbm) forecast data archive into Icechunk.

```{figure} images/nbm-diagram.png
:alt: Logo for the NOAA National Blend of Models dataset, showing output from GFS, MOS, CMC, and ensemble forecasts feeding into the National Blend of Models dataset. The image is clearly homemade in Microsoft paint or similar.
:width: 70%

The National Blend of Models combines output from a range of models — GFS, MOS, CMC, and ensemble forecasts — into a single blended forecast. Yes this appears to be the [official logo](https://vlab.noaa.gov/web/mdl/nbm) for the dataset.
```

We chose NOAA NBM because it's big (~2 PB in total, split into ~40 million GRIB2 files, ~800 per forecast cycle), has a complex structure, and the raw GRIB files are available in public object storage via the [AWS Open Data Registry](https://registry.opendata.aws/noaa-nbm/).

If you're interested in the details please see the [code we used for the ingestion](https://gist.github.com/TomNicholas/5701f91c601715207e9a3174bb60de51), and if you want to play with the data the [resultant Icechunk store](https://app.earthmover.io/earthmover-public/nbm-conus-cube) is accessible as a public repository on Arraylake.

As a proof of concept, we just ingested a single forecast cycle over CONUS (the contiguous United States).
(We didn't do the whole thing because one forecast cycle is enough to encounter all the idiosyncrasies of GRIB, and we are confident that scaling up would work - we have already shown that virtual Icechunk stores can scale up to [extremely large datasets](https://www.earthmover.io/blog/virtual-zarr)!)
If you are interested in a cloud-optimized version of the entire NBM dataset, especially one which stays up-to-date with new forecasts, please [contact us](mailto:support@earthmover.io).

Once ingested, accessing and plotting any part of the GRIB datacube becomes straightforward:

```python
import numpy as np
import arraylake as al
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
import gribberish  # imports the GribberishCodec, needed to decode the chunks upon read

# login to Arraylake
client = al.Client()
client.login()

# access data
repo = client.get_repo("earthmover-public/nbm-conus-cube")
session = repo.readonly_session("main")
ds = xr.open_zarr(session.store)
t2m = ds["t2m"].isel(time=0) - 273.15  # Kelvin -> Celsius

# plot (with correct projection and coastlines etc.)
proj = ccrs.LambertConformal(central_longitude=-95, central_latitude=25,
                             standard_parallels=(25, 25),
                             globe=ccrs.Globe(semimajor_axis=6371229, semiminor_axis=6371229))
ax = plt.axes(projection=proj)
t2m.plot.imshow(ax=ax, x="x", y="y", transform=proj, cmap="RdYlBu_r",
                interpolation="antialiased", regrid_shape=1600, center=False,
                cbar_kwargs={"label": "2 m temperature (°C)"})
ax.add_feature(cfeature.STATES, edgecolor="0.4", linewidth=0.3)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.set_title(f"NBM CONUS 2 m temperature — valid {str(ds.time[0].values)[:16]}Z")
plt.show()
```

```{figure} images/nbm_t2m_imshow.png
:alt: Map of 2 m temperature over the contiguous United States from the NOAA National Blend of Models, plotted on a Lambert Conformal projection with state boundaries and coastlines, using a red-yellow-blue colormap in degrees Celsius.
:width: 70%

2 m temperature over CONUS from the virtual Icechunk store, plotted directly from the code above.
```

## Zarr datacube vs TIFF files

Interestingly there is [already another copy](https://registry.opendata.aws/noaa-nbm/) of NOAA NBM on the AWS Open Data Registry in a cloud-optimized format: Cloud-Optimized GeoTIFF (COG).
We believe our approach of creating a virtual Icechunk store is superior in a number of ways, which further highlight the benefits of virtual Zarr:

- The TIFF conversion duplicated all the data, doubling overall storage costs,
- The TIFF copy is many files, without a single global entrypoint like the Zarr datacube has,
- The TIFF copy is harder to update or modify since it cannot take advantage of Icechunk's ACID transactional features or commit history,
- Despite the fact that rewriting the data gives the opportunity to update the chunk structure, TIFF files, like GRIB, are limited in the chunking structure they allow, whereas a full rewrite in Zarr would allow arbitrary chunking across arbitrary dimensions (e.g. timeseries-optimized or "churro" chunks).

## Bridge to the future

GRIB has its place, but at some point we hope agencies will transition to delivering their forecasts via a fully cloud-native system.
Until that happens creating virtual references pointing at GRIB archives is a great way to bridge the gap between existing systems and user needs.
