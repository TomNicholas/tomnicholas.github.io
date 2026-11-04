---
date: "2026-06-02"
title: "Old format, no problem!: Cloud-optimizing the GOES-16 archive as Virtual Zarr"
description: |
  Access billions of chunks of satellite imagery as a single Zarr store, without copying any data!
thumbnail: images/cover.mp4
tags:
- fundamentals
- icechunk
- zarr
- virtual-zarr
- virtualizarr
- arraylake
kernelspec:
  name: python3
  display_name: 'Python 3'
---

(Originally posted on the [Earthmover blog](https://earthmover.io/blog/virtual-zarr))

Tl;dr: Using VirtualiZarr, Icechunk, and Arraylake, we made a massive archive of GOES-16 satellite imagery available a single cloud-optimized virtual Zarr store, all without copying any data. [View the repo here](https://app.earthmover.io/marketplace/6a1a01ff883407eea64c0380)!

## The future of scientific data is cloud-native, but archival formats aren't

Cloud is clearly the future of scientific data sharing. 
["Analysis-Ready, Cloud-Optimized"](https://ieeexplore.ieee.org/abstract/document/9354557) (or ARCO) data stores are now being been championed by major public agencies internationally (including [USGS](https://opengeohub.org/2023/01/12/analysis-ready-and-cloud-optimized-arco-landsat-data-for-all/), [NOAA](https://registry.opendata.aws/noaa-nodd-kerchunk/), [NASA](https://www.earthdata.nasa.gov/engage/data-producer-resources/data-product-development-guide-producers-v2), and [ECMWF](https://climate.copernicus.eu/work-progress-our-data-stores-turn-arco)), as well as myriad non-profits and private companies.
Compared to traditional fileserver-backed data portals, ARCO data stores are more scalable to big datasets, more reliable, more performant for high-throughput workloads such as ML training, are a cost-efficient way to serve unlimited numbers of users, and are globally accessible so better facilitate collaboration.

However, many scientific file formats still in widespread use **predate the invention of the cloud**, sometimes by [over](https://en.wikipedia.org/wiki/NetCDF#:~:text=released%20in%201990%2C%20now%20known%20as%20%22netCDF%20classic%20format%22) [15 years](https://en.wikipedia.org/wiki/Amazon_S3#:~:text=AWS%20launched%20Amazon%20S3%20in%20the%20United%20States%20on%20March%2014%2C%202006)!
These "archival" file formats don't work well at all in cloud object storage, because they were never designed with that use case in mind. 
(For a deep dive on exactly what makes a format "cloud-optimized", and just how much difference it makes, read our earlier post ["What is Cloud-Optimized Scientific Data?"](https://www.earthmover.io/blog/fundamentals-what-is-cloud-optimized-scientific-data)).

## Dilemma: Duplicate data or let users suffer?

Pressure to move to the cloud under budget constraints mean data providers often begin a cloud migration by performing a "lift and shift", whereby data archives are uploaded to cloud object storage in their original formats without any other modifications.
Their data is now technically accessible through the cloud, but without many of the benefits of a truly cloud-native system.

In an ideal world, data providers would convert all the data into a cloud optimized formats such as [Zarr](https://www.earthmover.io/blog/what-is-zarr), but often there are requirements to keep the data available in the older formats for several years yet.
This presents a dilemma: either they create an additional copy of the data (costing twice as much - very expensive for Petabyte-scale datasets), or they leave the data in a format that is poorly suited for the cloud.
In some situations, there's a strong case to be made to duplicate the data, but we know that is not always an option.

## Solution: Cloud-optimised "virtual stores" referencing existing files

One solution to this dilemma is to provide cloud-optimized access to the contents of the files, without modifying or duplicating them.
This is what "virtual Zarr stores" enable, allowing stewards of massive archival scientific datasets to provide a great experience for their users, _with only a single copy of the data_. 

Let's briefly discuss how it's possible to provide cloud-optimized access to non-cloud-optimized files.
Unlike traditional POSIX file systems, you interact with data in cloud object storage over HTTP.
The tricky thing about cloud object storage is finding out exactly where the chunks of data you want are located without the use of filesystem primitives like `seek()`.
Once you do know their exact locations you can fetch many chunks efficiently in parallel using HTTP range requests (i.e. you can achieve [very high throughput](https://www.earthmover.io/blog/fundamentals-what-is-cloud-optimized-scientific-data#a-series-of-fat-pipes)).
Unfortunately pre-cloud file formats usually don't come with an efficient way to find out where the chunks you want are.
In general you may have to _download all the data_ [just to learn what's in the data](https://www.earthmover.io/blog/fundamentals-what-is-cloud-optimized-scientific-data#describe-yourself-in-8-bytes) - this is incredibly inefficient and severely limits what users are able to easily do with the data.

However, if someone has already done the up-front work of scanning the data to find the exact locations of every chunk, you can simply consult that mapping and immediately know exactly which location from which to fetch the chunks you want.
Amazingly, this trick works for many different scientific file formats, including HDF5, netCDF3, netCDF4, GeoTIFF, GRIB, FITS, and even Zarr itself!
You end up with a "chunk manifest" for every variable that looks something like this:

```{code-block} python
:caption: An example chunk manifest: each Zarr chunk key maps to a byte range (offset and length) within an existing file.

{
    "0.0.0": {"path": "s3://bucket/foo.nc", "offset": 100, "length": 100},
    "0.0.1": {"path": "s3://bucket/foo.nc", "offset": 200, "length": 100},
    "0.1.0": {"path": "s3://bucket/foo.nc", "offset": 300, "length": 100},
    "0.1.1": {"path": "s3://bucket/foo.nc", "offset": 400, "length": 100},
}
```

Once generated, this mapping can be saved to disk (comprising the "virtual store"), and used by anyone else wishing to subsequently access the same data archive.
Those user's queries are now much more efficient because they can immediately make targeted requests to the precise locations of the chunks within the archival files.

### Archives as virtual Zarr datacubes

This idea of [keeping important metadata separate](https://www.earthmover.io/blog/fundamentals-what-is-cloud-optimized-scientific-data#idea-separate-the-metadata) from the actual chunk data is central to Zarr - it's what allows you to learn what's inside arbitrarily large data stores without having to download their entire contents.
But the "native" Zarr format has nowhere to store this manifest.
Icechunk, on the other hand, neatly generalizes across the different types of chunks - in fact there is literally [an enum](https://github.com/earth-mover/icechunk/blob/7562c4db9e3f002451ccc84ee2d620700740a32b/icechunk-format/src/manifest.rs#L409) deep within the Icechunk Rust library that defines this distinction clearly.

```{code-block} rust
:caption: "Icechunk's ChunkPayload enum encodes the three chunk types: inline, virtual, and native."

pub enum ChunkPayload {
    Virtual(VirtualChunkRef), // Virtual - used for referring to chunks of external files too large to duplicate cheaply
    Ref(ChunkRef),            // Native - a conventional Zarr chunk - used for most chunks of intermediate size
    Inline(Bytes),            // Inline - used for tiny chunks that are easier to store in the manifest itself
}
```

As Icechunk exposes a Zarr interface (i.e. Icechunk is a special type of Zarr store), it combines the convenience of Zarr (a single entrypoint to an arbitarily large logical [datacube](https://www.earthmover.io/blog/what-is-zarr)) with the generality of the three chunk types.
In other words, Icechunk can act as a "virtual Zarr store".

```{figure} images/what-is-zarr.gif
:alt: A silly meme where the aliens from Toy Story gesture at the Claw, but instead of the Claw its a Zarr datacube

Behold the Zarr datacube. Credit: Lindsey Nield, Earthmover Engineer
```

## GOES-16 archive - a gargantuan data access challenge

Another tricky part about recording information about every chunk is that scientific data archives can have _a lot_ of chunks.
The NOAA GOES-16 (Geostationary Earth Observing Satellite) archive for example contains 7 years of data, stored as 380,000 different netCDF4 files (for just one product!) on a [public AWS bucket](https://registry.opendata.aws/noaa-goes/).

We should first sincerely thank the [NOAA NODD program](https://www.noaa.gov/information-technology/open-data-dissemination) and the [AWS Open Data Program](https://registry.opendata.aws/noaa-goes/) for providing the raw data on S3 where anyone can reach it.
But the result is typical of a lift-and-shift - technically the data is all available on the cloud, but it's very hard to use.
To view a specific location and time, every user will at minimum have to select from 380,000 filenames (which follow a dataset-specific convention, with no guarantee of being consistent), then often have to [download entire files](https://geonetcast.wordpress.com/2018/01/10/script-to-download-goes-16-netcdfs-from-amazon-s3/) just to access a few pixels (each file contains 470 million pixels).
The worst case is if the user wants a timeseries at just one specific point: they have to iterate over every file and throw away 99% of the contents!

Instead, wouldn't it be awesome if the entire GOES-16 archive was browsable as a single virtual Zarr store?
This very large archive provides an excellent test case for the virtualization approach.
If it can work at this scale, it's likely to to be able to handle most real-world datasets.

To make this data truly accessible we need to:

1. Parse the files to extract the virtual references at scale,
2. Organise all the references into a logical datacube,
3. Commit and store the manifests robustly at scale,
4. Efficiently look up chunk locations within the virtual store,
5. Stream chunks with high throughput back out to users of the store,
6. Ensure convenient discoverability of the resultant data product.

VirtualiZarr, Icechunk, and Arraylake achieve these requirements together.

### VirtualiZarr extracts and organizes virtual chunks

[VirtualiZarr](https://virtualizarr.readthedocs.io/en/stable/) is a Python tool for creating virtual Zarr stores, which handles steps (1) and (2).

While some tools for extracting virtual chunks already existed (e.g. [Kerchunk](https://github.com/fsspec/kerchunk)), VirtualiZarr aims to make it as easy as possible to extract references from a range of archival of file types, and organize them into a logical Zarr datacube.
An extensible system of "parsers" handle common archival file formats, but also allow writing custom parsers for more esoteric formats.
Xarray syntax (e.g. `xarray.concat` and `xarray.merge`) make it intuitive to do even rather complicated aggregations of virtual references from many files, and metadata can be arbitrarily altered before writing.

VirtualiZarr was also designed to scale - it uses an efficient in-memory representation of the manifests, it allows parallelizing reference generation across files using a range of parallel executors, and it writes the combined references into Icechunk efficiently.

### Icechunk stores the virtual chunks

[Icechunk](https://icechunk.io/en/latest/) is a serverless transactional cloud-native database for storing chunks, which handles steps (3), (4), and (5).

We've already discussed how Icechunk stores virtual chunks, but it also directly addresses two of the main downsides of the "virtual references" approach:
- It organises the myriad possible locations which virtual chunks could refer to via the concept of "virtual chunk containers",
- If someone quietly overwrites or deletes the referenced archival files, it protects you against reading corrupted data by immediately warning you that the object was modified since the virtual reference was written.

### Arraylake makes your data discoverable

[Arraylake](https://docs.earthmover.io/) is a cloud data lake, whose catalog and web app handles step (6).

Icechunk is serverless - an Icechunk store is "simply" a bunch of special files in object storage.
This is awesome, but it means that to access your data, people have to know that its located in AWS `us-west-2` at `s3://my-bucket/goes-16/`, and that refers to virtual chunks at `s3://goes-16`.

For totally open data, this works fairly well - just put write the Icechunk store into an anonymous-access public bucket and you're done!
But that's not enough if you want to:
- Make the data discoverable to consumers who might be interested in using it
- Browse the data in a web UI or catalog
- Record metrics of who is accessing the data
- Restrict access to certain people (i.e. within an org, or behind a paywall)
- Use additional services on top, such as a tile server.

That's where Arraylake comes in - Arraylake is a managed service run by Earthmover which provides all these features.
Since Icechunk is 100% open-source and permissively-licensed, you can always use Icechunk with or without Arraylake, then easily import existing Icechunk data into Arraylake.

Arraylake recently gained upgraded support for virtual chunks, particularly in the context of privacy-conscious users - look out for a future blog post on that.

### Access as Zarr

Accessing the entire resulting dataset as a Zarr store via Arraylake is just a few lines of Python:

```python
import arraylake as al
import xarray as xr

client = al.Client()
client.login()

repo = client.get_repo("earthmover-public/goes-16")
session = repo.readonly_session("main")
ds = xr.open_zarr(session.store, group="ABI-L2-MCMIPF/post-2023-04-19")
ds
```

```{code-block} text
:caption: The entire GOES-16 MCMIPF archive opened as a single Xarray Dataset — petabytes addressable through one entrypoint, without copying any data.

<xarray.Dataset> Size: 2PB
Dimensions:                                 (t: 285037, y: 5424, x: 5424,
                                            band: 16,
                                            number_of_time_bounds: 2,
                                            number_of_image_bounds: 2)
Coordinates:
  * t                                       (t) datetime64[ns] 2MB 2017-02-28...
  * y                                       (y) float64 43kB 0.1518 ... -0.1518
  * x                                       (x) float64 43kB -0.1518 ... 0.1518
  * band                                    (band) int64 128B 1 2 3 ... 14 15 16
    wavelength                              (band) float32 64B ...
    x_image                                 float32 4B ...
    y_image                                 float32 4B ...
Dimensions without coordinates: number_of_time_bounds, number_of_image_bounds
Data variables: (12/38)
    CMI_C01                                 (t, y, x) float64 67TB ...
    CMI_C02                                 (t, y, x) float64 67TB ...
    CMI_C05                                 (t, y, x) float64 67TB ...
    CMI_C08                                 (t, y, x) float64 67TB ...
    CMI_C09                                 (t, y, x) float64 67TB ...
    CMI_C12                                 (t, y, x) float64 67TB ...
    ...                                      ...
    std_dev_brightness_temperature          (t, band) float32 18MB ...
    std_dev_reflectance_factor              (t, band) float32 18MB ...
    time_bounds                             (t, number_of_time_bounds) datetime64[ns] 5MB ...
    outlier_pixel_count                     (t, band) float64 36MB ...
    x_image_bounds                          (t, number_of_image_bounds) float32 2MB ...
    y_image_bounds                          (t, number_of_image_bounds) float32 2MB ...
```

Plotting the full disk at one timestep is just a [few more lines of Xarray](https://gist.github.com/TomNicholas/4c441c1e69ada4d2c1e0abe35262e007#file-plot_goes-ipynb).

```{figure} images/eclipse-full-disk.png
:alt: GOES-16 true color full disk on 8 April 2024, with the dark shadow of the lunar umbra from the total solar eclipse visible over North America

The 2024 total solar eclipse captured in a single GOES-16 full-disk scan — the Moon's umbra is the dark patch over North America.
```

GOES-16 has since been superceded by newer satellites, so this particular archive is static, but data repositories don't have to be.
Icechunk's [transactional version control capabilities](https://www.earthmover.io/blog/learning-about-icechunk-consistency) mean that new operational data can be committed as it arrives, and users can safely read from the data at any moment, and even rollback to see earlier versions of the data if they want.

## Ingestion lessons

The unprecedented scale of this virtual ingestion was challenging.
Whilst the absolute size of this archive was manageable (~115TB on-disk for the [MCMIPF product](https://www.goes-r.gov/education/docs/fs_imagery.pdf)), because the internal chunks within the netCDF files are suboptimally small, the total number of virtual chunk references to extract and store was extremely large - over 7.1 billion chunks.
(If the chunks were rewritten with a more optimal size of 10MB, a store with this many chunk references would be 23PB on disk.)
For the work VirtualiZarr and Icechunk have to do, number of chunks is the important metric, which is why we chose this dataset as a stress test.

The ingestion pipeline required batching, careful schema validation to handle [inconsistencies](https://gist.github.com/TomNicholas/4c441c1e69ada4d2c1e0abe35262e007#file-goes_data_inconsistencies-md) encountered in the netCDF files, advanced Icechunk features such as manifest splitting, and some new performance optimizations in both [VirtualiZarr v2.6.0](https://github.com/zarr-developers/VirtualiZarr/releases/tag/v2.6.0) and [Icechunk v2](https://www.earthmover.io/blog/announcing-icechunk-2-better-consistency-performance-and-reliability-for-tensor-storage).
For practitioners interested in the details the [code is available here](https://gist.github.com/TomNicholas/4c441c1e69ada4d2c1e0abe35262e007#file-goes-16-ingest-ipynb), along with explanations of choices made.

## Timeseries

One workload that many users want to perform on GOES data is to analyse how a particular point on the disk changed over time, i.e. timeseries analysis.

This is notoriously hard for long-term satellite data archives: the data is downloaded from the satellite as an whole multi-band image every few minutes (i.e. ingested as "pancake chunks"), but the user access pattern works best with the opposite layout (i.e. query as "churro chunks").

Since the netCDFs have spatial chunks, it is possible to do a point timeseries query across the underlying 300,000 files relatively efficiently with this store.
It currently takes Xarray and Dask about 7 minutes to [fetch a timeseries](https://gist.github.com/TomNicholas/4c441c1e69ada4d2c1e0abe35262e007#file-plot_goes-ipynb) spanning 250,000 timesteps.
However, we have an internal prototype of a new Rust-based query engine that do it in less than 2 minutes, and we're confident that can still be improved upon a lot. 
EDIT (06/03/2026): Our resident Rust wizard Luiz already found a way to make it almost 3x faster!

## Freedom of reach

One interesting feature of the virtual references trick is that anyone can do it.

Since metadata (including manifests) can be stored in a separate location to the archival files, only read access to the data is required, meaning you can cloud-optimize data archives _even without the data provider's explicit permission_ to do so.
Here we did not have to convince the NOAA GOES programme team to change anything about their current data distribution approach - we didn't even contact them.

Even better - since the manifests are generally millions of times smaller than the actual data, and the ingestion is a one-off cost, it's extremely cheap to do this.
Running the [ingestion notebook](https://gist.github.com/TomNicholas/6e908090583c3c4bbed1a305ac8c3bfd#file-goes-16-ingest-per-band-batched-ipynb) cost ~$100, and storing the ~80GB of metadata (i.e. the manifests) generated on S3 costs $1.84 per month, compared to ~$2,600 per month to store a duplicated copy of this 115TB archive.

This allows anyone to immediately make the data usable with modern cloud-native tooling, while respecting the reality that data producers — especially public agencies — often need to operate on a slower, more deliberate timeline.

## Caveats

Of course, there are some tradeoffs with this virtual store approach.

- **The original chunks cannot be modified, only referenced as they exist.** This means the virtual store inherits the data's original chunk shapes and sizes, which may be subptimal. This is a hard constraint that is a properly of how HTTP range requests to object storage work. Of course you can choose to overwrite parts of the data with native chunks, but that uses more storage - those chunks are no longer virtual.
- **VirtualiZarr assumes your data can be described by the Zarr data model.** Zarr's model is very general, so it can absorb netCDF/GeoTIFF/GRIB and more, but this does rule out some more esoteric file formats. The virtual approach also works better the more cube-like the data is, so it currently works nicely on alignable Level 3 data (or L2 data products regridded to a common grid, as we used here), but less easily on L2 data. Interestingly however the concept of a virtual reference does not strictly require the Zarr model...
- **The set of files in the archive must be [homogenous](https://virtualizarr.readthedocs.io/en/stable/faq.html#can-my-specific-data-be-virtualized)**, in the sense of collectively mapping to a single Zarr store. Any inconsistencies, such as changes in compression schemes, can make it harder or even impossible to create a virtual store. In the GOES-16 case, the archive actually had to be split into a few different Zarr groups instead of a single datacube because the netCDF compression and encoding were apparently changed on two occasions during the lifetime of GOES-16.

We're working hard on relaxing these constraints, so that more and more data can be ingested through the virtual approach. But for now, [we still recommend native Zarr when feasible](https://virtualizarr.readthedocs.io/en/stable/faq.html#why-write-to-a-cloud-native-format-directly-if-i-can-just-virtualize-later).

## Conclusion

We just made a massive archival scientific dataset much easier to use, without copying any data.
The resultant virtual store still benefits from all the features of the Earthmover stack:

- It's a Zarr store, with a single entrypoint, clear logical structure, and efficient to read data from.
- We're still free to make arbitrary updates to the data, enabling metadata to be corrected, or new data to be added.
- Users can see immutable commits and tags, allowing true reproducibility, like we would expect for code.
- The data is stored in an [open-source format](https://icechunk.io/en/latest/reference/spec/).
- Since Icechunk is serverless there is no server between users and the raw data. Users with high throughput requirements will prefer to hit object storage directly, so we can avoid capacity issues when aged agency servers getting blasted by people wanting to train AI weather models!
- Through Arraylake the data store is easy to advertise and user access metrics can be collected.

Put together, this is foundational infrastructure for data-intensive science and commerce.

#### Acknowledgements

- [C]Worthy for supporting the original development of VirtualiZarr.
- The community of contributors to VirtualiZarr, including developers from DevelopmentSeed, CarbonPlan, Element84, NASA, and USGS.
