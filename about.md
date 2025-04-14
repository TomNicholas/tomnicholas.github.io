# About me

I'm a physicist turned open-source software engineer. I work on projects that make it easier to analyse and share massive scientific datasets. 

I strongly feel that progress in most fields of computational science is bottlenecked by how uneccessarily hard that is right now. There are [crucial missing pieces](./blog/2025/science-needs-a-social-network.md) of global scientific infrastructure.

Climate science, meteorology, and all downstream impact analyses are similarly hamstrung, and I hope my work contributes in some small way to addressing the global climate crisis by helping enable them.

## What I do

```{div}
:class: col-gutter-left

**Open Source Software and Infrastructure for Science**
```
```{div}
:class: col-body-right

I contribute to a number of open-source software projects that support this aim, often as part of the [Pangeo Community](https://pangeo.io/).

A few projects I'm particularly proud of or excited about, and my role in them:

- [Xarray](https://xarray.dev/) - N-D labeled arrays and datasets in Python (core maintainer).
- [VirtualiZarr](https://github.com/zarr-developers/VirtualiZarr) - Cloud-Optimizes your Scientific Data as Virtual Zarr stores, using Xarray syntax (original author and lead developer).
- [Cubed](https://cubed-dev.github.io/cubed/) - Scalable array processing with bounded memory (cheerleader, and author of the [Cubed-Xarray integration](https://cubed-dev.github.io/cubed/examples/xarray.html)).
- [FROST](https://github.com/TomNicholas/FROST) - Federated registry of all scientific datasets (originator - I'm trying to make this a thing).

Check out my [my GitHub page](https://github.com/tomnicholas) for more details.
```
```{div}
:class: col-gutter-left
**Scientific Research Dilettante**
```
```{div}
:class: col-body-right

I have at some point somehow been involved in research on or written peer-reviewed pieces on a wide range of topics, including:

- Nuclear Fusion Plasma Physics
- Economics of Fusion Reactors
- Physical Oceanography
- Ocean-based Carbon Dioxide Removal
- Climate Science
- Superconductivity
- Hypersonic Aerothermodynamics (Spacecraft Re-entry)
- Seismology

I also regularly interact with researchers in all sort of fields of science, from biology to social science to machine learning.

In every field I see the same kinds of pain around doing computational work, which motivates my software projects.

For a list of publications and scholarly artifacts in which I've been involved,
check out [my ORCID page](https://orcid.org/0000-0002-2176-0530) or [my Google Scholar page](https://scholar.google.com/citations?user=sRqgW3gAAAAJ&hl=en).
```

## About this website

This website is my fork of [Chris Holdgraf](https://chrisholdgraf.com/)'s experiment in hosting a personal website and blog via Sphinx extensions instead of using Jekyll. All credit for the website should go to him.

(about:timeline)=
## A rough timeline

Below is a rough timeline of my working life so far.

:::::::{div}
:class: col-body-inset-left

:::::{card}
**2025- : Engineer at Earthmover**
^^^
...
:::::

:::::::

:::::::{div}
:class: col-body-inset-right

:::::{card}
**2023-2025: Staff Scientist at [C]Worthy**
^^^
...
:::::

:::::::

:::::::{div}
:class: col-body-inset-left

:::::{card}
**2021-2023: Oceanographer at Columbia University**
^^^
...
:::::

:::::::

:::::::{div}
:class: col-body-inset-right

:::::{card}
**2018: First contributions to Xarray**
^^^
I first heard about Xarray during my PhD, and immediately started [using it](https://github.com/boutproject/xBOUT) to analyse my plasma physics simulation data.

To get this to work I began making upstream contributions. One of my [first big contributions](https://github.com/pydata/xarray/pull/2553) was generalizing `xarray.open_mfdataset` to work on N-dimensional grids of files, which still sees a lot of use via the `combine='by_coords'/'nested'` options.
:::::

:::::::

:::::::{div}
:class: col-body-inset-left

:::::{card}
**2016-2021: PhD at Culham Centre for Fusion Energy**
^^^
I did big simulations of turbulent plasmas inside magnetically-confinement fusion experiments (particularly MAST-U). I was a student of the University of York as part of the excellent [Fusion CDT](https://fusion-cdt.ac.uk/), but worked at [Culham Centre for Fusion Energy](https://ccfe.ukaea.uk/). The simulations generated a lot of netCDF files on HPC... 

My proudest work during my PhD wasn't physics but economics: a paper about the [(lack of) future market for fusion power](https://arxiv.org/abs/2101.05727).
:::::

:::::::

:::::::{div}
:class: col-body-inset-right

:::::{card}
**2012-2016 Studied Physics at Oxford**
^^^
Graduated from Oxford University with an MPhys in Physics, specializing in Theoretical and Condensed Matter Physics. Did my Master's thesis on modelling and data analysis of certain types of novel superconducting materials.
:::::

:::::::