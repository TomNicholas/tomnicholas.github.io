---
date: "2021-06-29"
title: "Pan-Plasma: Plasma physics needs an open scientific python ecosystem following Pangeo"
description: |
  Geoscientists have already solved many of the software problems plasma physicists still struggle with - they should just use the same solutions.
tags:
- open-science
- fusion
- plasma
kernelspec:
  name: python3
  display_name: 'Python 3'
---

## Pan-Plasma: Plasma physics needs an open scientific python ecosystem following Pangeo

Tom Nicholas, 29/06/2021

TLDR: The MCF and plasma physics community should copy the [Pangeo project](https://pangeo.io/) and its (xarray + dask-based) software ecosystem, because geosciences have already solved many of the software problems we still struggle with.

### Problems to solve

My experience of software practices in fusion research has been that there are some common and widespread problems. In particular:

  - **Code is not open or shared.** Whilst there are notable exceptions, the typical workflow of a fusion research group right now involves simulation or diagnostic processing code that is closed-source, sometimes requires a licence (for IDL or MatLab), and is not designed to be reusable or composable for other researchers. This increases the chance of bugs, massively inhibits collaboration, and prevents reproducibility.
  - **Re-inventing the wheel regularly** is another inevitable result of not sharing tools. Even different groups who use the same simulation code often have different data loading and analysis scripts. Clear opportunities for standardization are not taken - for example the ubiquitous edge simulation code SOLPS has no good set of standard analysis tools. This is to say nothing of the myriad equilibrium solving codes, field-line tracers, and diverted geometry plotting scripts.
  - **Not taking advantage of existing solutions** from other domains. A lot of what we do already has well-developed tools, and other fields have already faced and overcome many software challenges that we still struggle with. There is perhaps a bit of a cultural issue at play where we think fusion is especially hard or different somehow, e.g. "the science and engineering challenges are novel and unprecedentedly complicated, so we need to use totally bespoke software tools". This does not follow - in reality the majority of fusion research involves rather similar modelling and analysis tasks to other fields of science. Most of us still merely need to load gridded numerical data from simulations or experiment, run some pretty standard analysis functions on it, and then visualize the results. (The one exception *might* be in the degree of complexity of integrated modelling, but that effort would still benefit from these recommendations.)
  - **Outdated** analysis scripts in IDL are commonplace, and even groups that use python aren't necessarily using the external libraries that they should be.
  - **Doesn't scale**. Using older tools, downloading to local filesystems, and not standardizing methods of parallel data analysis will uneccesarily limit a lot of our workflows in size. This will impact our science: new simlations and diagnostics are already producing ever-larger datasets and working at scale (not to mention for training Machine Learning models) needs to be an explicit priority.

### Geosciences have already solved these!

It turns out that another field of science has already found a good solution to many of these problems: the [Pangeo project](https://pangeo.io/) for Big Data Geoscience.

Whilst most if not all fields of science could benefit from efforts like Pangeo, the crossover is especially clear for fusion research, as geoscientists and plasma physicists have extremely similar problems computationally. Both fields deal primarily with datasets which are:
- Multidimensional (often fluid turbulent),
- Large (bigger than local RAM),
- On regular but warped grids,
- Often pulled from central servers,
- From multiple sources but with common structure (e.g. experimental and simulation data for the same device).

Pangeo is both a set of packages and a community, which aims to solve the problems I mentioned earlier.

- **Open** code and data encourages collaboration, with all packages available on github, many important datasets available online, and technical discussions happening publicly via github issues or the community's [discourse forum](https://discourse.pangeo.io/).
- **Shared tools** are the aim, via creating and advertising tools for the community. Clear entry points for new packages mean that only a small compatibility layer is required in order to plug into and benefit the whole ecosystem.
- **Uses domain-agnostic tools** where possible, enabled by a conscious splitting of responsibility. For example the xarray package provides powerful labelled multidimensional data structures for manipulation by downstream libraries, but does not require the data stored to be geospatial or even necessarily scientific. Instead each layer of functionality is separated by a common API, allowing packages to be swapped out. This also allows tool sharing across disciplines, massively disributing the development effort.
- **Modern** tools and software practices are the norm, with well-tested and documented code throughout the stack. Pangeo's main stack is written in Python, but there is no reason why a similar ecosystem could not work in another open-source language like Julia for example.
- **Scalable** data analysis is enabled through the dask library, which seamlessly integrates with xarray to parallelize data analysis with little or no extra effort for the user. Pangeo also provides a cloud platform for users to run data analysis tasks, which works best with cloud-optimized file formats such as [Zarr](https://zarr.readthedocs.io/en/stable/). [Moving scientific work to the Cloud](https://medium.com/pangeo/the-case-for-cloud-in-science-3f98f6538a33) is potentially a paradigm shift in how we think about scientific data analysis challenges.

### How would this fit in with other fusion software efforts?

Whilst the majority of fusion researchers are using scattered codebases, there are at least three significant efforts to improve the software experience for plasma physicists. Each of these would benefit from a pangeo-like ecosystem.

- **OMFIT** is a simulation and analysis workflow tool, essentially providing a huge and extensible GUI on top of existing simulation codes. It already uses xarray under the hood for some parts, and so should aim to sit atop a pangeo-like set of packages. Therefore improvements in the standardization and interoperability of underlying packages would improve the reliability, maintainability, and power of OMFIT itself, by allowing OMFIT developers and the rest of the (non-OMFIT-using) community to benefit from each other's work.
- **IMAS** is an extremly powerful and complex software project at ITER. Like OMFIT, IMAS would benefit from being able to internally rely upon modular packages which are also in use in the wider community. 
- **PlasmaPy** is the closest effort to this proposal already existing, and is huge step in the right direction. A pangeo-like ecosystem differs in the emphasis on modularity and interoperability between separate packages, treating xarray & dask as key packages which together enable analysis at scale, and taking care to keep as much functionality as domain-agnostic as possible.

### Specific needs and vision

Certain packages and specifications would be particularly useful within a plasma ecosystem. Each of these suggestions either currently does not exist, or exists in multiple places unneccesarily, without a standardized interface. Several of these suggestions have clear analogies to existing geoscience libraries used in Pangeo.

- **A single tokamak data model** for multidimensional data. Xarray provides a powerful and general data structure, but some agreement about how to encode tokamak-specific features may be required so that downstream packages know what to expect. This can be taken  further into grid-aware analysis, like [xGCM](https://github.com/xgcm/xgcm) does for Global Circulation Models.
- **Shared plasma metadata conventions** about grids, variables and units, similar to the [Climate and Forecast Metadata Conventions](https://cfconventions.org/) designed for netCDF files, would ameliorate the challenge of integrated analysis of output from a very large number of plasma simulation codes and datasets. Shared conventions would vastly improve interoperability, reproducibility, and accuracy. Xarray can store arbitrary metadata in the attributes of data objects, and decoding of file metadata can be done upon opening.
- **Tokamak plotting** of various geometries consuming these data structures, dealing with the tricky projections and topologies in one place, just like [Cartopy](https://github.com/SciTools/cartopy) does for map projections of the Earth. Careful separation of plotting from projection, topology, and features (e.g. separatrices and walls) would avoid locking users into a single plotting library. Cartopy provides [inspiration](https://github.com/boutproject/xBOUT/issues/11#issuecomment-453502099) for a tokamak-specific equivalent (*cartomak*?):
    ```python
    from cartomak.geometries import axisymmetric as cga
    from cartomak.features import VESSEL
    
    ax = density.plot(projection=cga.PoloidalSlice())
    ax.add_feature(ctf.VESSEL, machine='MAST'); ax.separatrices()
    ```
- **Indexers for complex topologies**. Xarray will soon provide [full flexibility with indexers](https://github.com/pydata/xarray/projects/1), allowing the user to specify how they want a location query to be evaluated for their data. As well as allowing more accurate representations such as periodic indexes, we could imagine [specialised indexer objects](https://github.com/pydata/xarray/issues/3620#issuecomment-855710036) which allow for querying tokmak data in specific ways. Building an `xarray.Dataset` with such a `TokamakIndex` would allow for any type of indexing we liked.
- **Common analysis tools**. Every fusion physicist has an implementation of certain common tasks, such as equilibrium handling, timeseries analysis, common diagnostic instrument analysis, and field-line tracing. PlasmaPy has made a good start on some of this, but building on top of a shared stack with specified conventions and separation of concerns would allow for plug-and-play tools that everyone could use.
- **Code-specific compatibility layers** would standardize the output of simulation codes for analysis, and place the responsiblity for integration with the wider ecosystem with the simulation code's community. [xBOUT](https://github.com/boutproject/xBOUT) is an example of this for [BOUT++](https://boutproject.github.io/) data: it will open any BOUT++ output files and return an xarray dataset ready for analysis. Writing a similar layer for SOLPS for example would only require wrapping `xarray.open_dataset`, but conversion of [arbitrary binary file formats](https://github.com/MITgcm/xmitgcm) is also possible.
    ```python
    from xbout import open_boutdataset
    ds1 = open_boutdataset('BOUT.dmp.*.nc')
    
    from solps import open_solps
    ds2 = open_solps('output.nc')
    
    # Both datasets immediately in the same data structures for comparison
    ```

### Would immediately unlock powerful existing features
  
Whilst the full creation of a complete ecosystem might take a while, refactoring to use some of pangeo's most popular packages would bring immediate benefits for many fusion researchers.
  
- **Parallel and out-of-memory analysis**. [Dask](https://dask.org/) could easily scale our analysis to large turbulence datasets, or mining data over many shots. This is *incredibly* powerful and on its own is a sufficient reason to rewrite analysis tools to use xarray.
- **Cloud-optimized storage** via Zarr allows for efficient parallel access of datasets, reducing the degree to which I/O bottlenecks analysis workflows.
- **Labelled dimensions** of xarray data structures make analysis code vastly clearer, more succinct, and less error-prone, allowing scientists to focus more on the scientific content.
- **Unit-aware arithmetic** is inherent to scientific work, but rarely encoded in our software. Recent [pint](https://github.com/hgrecco/pint) integration [into xarray](https://github.com/xarray-contrib/pint-xarray) would solve our unit-conversion headaches, eliminating a whole class of possible errors. (The same [generalization](https://github.com/pydata/xarray/projects/2) which allows this should allow soon allow for other duck-arrays, for example [GPU-backed cupy arrays](https://github.com/pydata/xarray/issues/4212).)
- **Easier reproducibility** Project Jupyter allows us run this analysis in the cloud, and turn code into presentable results much more quickly.
- **Plotting flexibility** We would have the flexibility to choose plotting libraries easily, such as HoloViews and matplotlib, and get interactive plots through bokeh. 
- **Machine Learning integration** benefits from work in other fields which allows consuming of xarray-type gridded data by ML frameworks such as `scikit_learn`.


### Conclusion

Successful software efforts in the geosciences have provided us plasma physicists with a blueprint for improving our software, workflows, user experience, and science. Realising these benefits in fusion research requires an explicit focus on modularity, re-using powerful domain-agnostic tools, and planning for big data challenges early.
