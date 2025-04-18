---
date: "2022-08-30"
title: "Unit-aware arithmetic in Xarray, via pint"
description: |
  All scientific computations involve units, so let's make our analysis software aware of them.
tags:
- code
- python
- xarray
- pint
- open-science
- physical-units
kernelspec:
  name: python3
  display_name: 'Python 3'
---

(This post was originally published on the [xarray blog](https://xarray.dev/blog/introducing-pint-xarray).)

_TLDR: Pint-Xarray supports unit-aware operations by wrapping [pint arrays](https://pint.readthedocs.io/en/stable/), so your code can automatically track the physical units that your data represents:_

```python
distance = xr.DataArray(10).pint.quantify("metres")
time = xr.DataArray(4).pint.quantify("seconds")

distance / time
```

```
Out:
<xarray.DataArray ()>
<Quantity(2.5, 'meter / second')>
```

## Units are integral to science

All quantities in science have units, whether explicitly or implicitly. (And even dimensionless quantities like ratios still technically have units.)

Getting our units right is finicky, and can very easily go unnoticed in our code.

Even worse, the consequences of getting units wrong can be huge!

The most famous example of a units error has to be NASA's $125 million [Mars Climate Orbiter](https://www.simscale.com/blog/2017/12/nasa-mars-climate-orbiter-metric/), which in 1999 burned up in the Martian atmosphere instead of successfully entering orbit around Mars.
A trajectory course correction had gone wrong, and the error was eventually traced back to a units mismatch: the engineers at Lockheed Martin expressed impulse in [pound-force](<https://en.wikipedia.org/wiki/Pound_(force)>) seconds, whereas the engineers at JPL assumed the impulse value their part of the software received was in SI newton seconds.

<p align='center'>
  <img src='https://web.archive.org/web/20191116161743/https://clqtg10snjb14i85u49wifbv-wpengine.netdna-ssl.com/wp-content/uploads/2017/12/Customers.jpg' />
</p>

<p align='center'>
  Newspaper cartoon depicting the incongruence in the units used by NASA and
  Lockheed Martin scientists that led to the Mars Climate Orbiter disaster.
</p>

We should take stories like this seriously: If we can automatically track units we can potentially eliminate a whole class of possible errors in our scientific work...

## Pint tracks units

There are a few packages for handling units in python (notably [unyt](https://github.com/yt-project/unyt) and [astropy.units](https://docs.astropy.org/en/stable/units/)), but for technical reasons we began units integration in Xarray with [pint](https://pint.readthedocs.io/en/stable/).
These various packages work by providing a numerical array type that acts similarly to a NumPy array, and is intended to plug in and replace the raw NumPy array (a so-called "duck array type").

Pint provides the `Quantity` object, which is a normal numpy array combined with a `pint.Unit`:

```python
q = np.array([6, 7]) * pint.Unit('metres')
print(repr(q))
```

```
Out:
<Quantity([6 7], 'meter')>
```

Pint Quantities act like NumPy arrays, except that the units are carried around with the arrays, propagated through operations, and checked during operations involving multiple quantities.

## Xarray now wraps Pint

Thanks to the [tireless work](https://github.com/pydata/xarray/issues/3594) of Xarray core developer [Justus Magin](https://github.com/keewis), you can now enjoy this automatic unit-handling in Xarray!

Once you create a unit-aware Xarray object (see below for how) you can see the units of the data variables displayed as part of the printable representation.
You also immediately get the key benefits of Pint:

1. Units are propagated through arithmetic, and new quantities are built using the units of the inputs:

   ```python
   distance = xr.DataArray(10).pint.quantify("metres")
   time = xr.DataArray(4).pint.quantify("seconds")

   distance / time
   ```

   ```
   Out:
   <xarray.DataArray ()>
   <Quantity(2.5, 'meter / second')>
   ```

2. Dimensionally inconsistent units are caught automatically:

   ```python
   apples = xr.DataArray(10).pint.quantify("kg")
   oranges = xr.DataArray(200).pint.quantify("cm^3")

   apples + oranges
   ```

   ```
   Out:
   DimensionalityError: Cannot convert from 'kilogram' ([mass]) to 'centimeter ** 3' ([length] ** 3)
   ```

3. Unit conversions become simple:

   ```python
   walk = xr.DataArray(500).pint.quantify('miles')

   walk.pint.to('parsecs')
   ```

   ```
   Out:
   <xarray.DataArray ()>
   <Quantity(2.6077643524162074e-11, 'parsec')>
   ```

With these features, you can build code that automatically propagates units and converts them where necessary to stay consistent.
For example, the problem of the NASA orbiter could have been prevented by explicitly converting to the correct units at the start

```python
def jpl_trajectory_code(impulse):

    # Defensively check units first
    impulse = impulse.pint.to("Newton * seconds")

    # This function we called here will only compute the correct result if supplied input in units of Newton-seconds,
    # but that's fine because we already converted the values to be in the correct units!
    propagated_position = some_rocket_science(impulse)

    return propagated_position
```

Note: We are adding [new features](https://github.com/xarray-contrib/pint-xarray/pull/143) to make specifying the units of parameters of existing library functions more slick.

In the abstract, tracking units like this is useful in the same way that labelling dimensions with Xarray is useful: it helps us avoid errors by relieving us of the burden of remembering arbitrary information about our data.

## Quantifying with pint-xarray

The easiest way to create a unit-aware Xarray object is to use the helper package we made: [pint-xarray](https://github.com/xarray-contrib/pint-xarray).
Once you `import pint_xarray` you can access unit-related functionality via `.pint` on any `DataArray` or `Dataset` (this works via [Xarray's accessor interface](https://xarray.pydata.org/en/stable/internals/extending-xarray.html)).

Above we have seen examples of quantifying explicitly, where we specify the units in the call to `.quantify()`.
We can do this for multiple variables too, and we can also pass `pint.Unit` instances:

```python
ds = xr.Dataset({'a': 2, 'b': 10})

ds.pint.quantify({'a': 'kg',
                  'b': pint.Unit('moles')})
```

```
Out:
<xarray.Dataset>
Dimensions:  ()
Data variables:
    a        int64 [kg] 2
    b        int64 [mol] 10
```

Alternatively, we can quantify from the object's `.attrs`, automatically reading the metadata which xarray objects carry around.
If nothing is passed to `.quantify()`, it will attempt to parse the `.attrs['units']` entry for each data variable.

This means that for scientific datasets which are stored as files with units in their attributes (which netCDF and Zarr can do for example), using Pint with Xarray becomes as simple as:

```python
import pint_xarray

ds = open_dataset(filepath).pint.quantify()
```

## Dequantifying

To convert our pint arrays back into NumPy arrays, we can use `.dequantify`.
This will strip the units from the arrays and replace them into the `.attrs['units']` of each variable.
This is useful when we want to save our data back to a file, as it means that the current units will be preserved in the attributes of a netCDF file (or Zarr store etc.), as long as we just do `ds.pint.dequantify().to_netcdf(...)`.

## Dask integration

So Xarray can wrap Dask arrays, and now it can wrap Pint quantities… Can we use both together? Yes!

You can get a unit-aware, Dask-backed array either by `.pint.quantify()`-ing a chunked array, or you can `.pint.chunk()` a quantified array.
(If you have Dask installed, then `open_dataset(f, chunks={}).pint.quantify()` will already give you a Dask-backed, quantified array.)
From there you can `.compute()` the Dask-backed objects as normal, and the units will be retained.

(Under the hood we now have an `xarray.DataArray` wrapping a `pint.Quantity`, which wraps a `dask.array.Array`, which wraps a `numpy.ndarray`.
This "multi-nested duck array" approach can be generalised to include other array libraries (e.g. `scipy.sparse`), but requires [coordination](https://github.com/pydata/duck-array-discussion) between the maintainers of the libraries involved.)

## Unit-aware indexes

We would love to be able to promote Xarray indexes to Pint Quantities, as that would allow you to select data subsets in a unit-aware manner like:

```python
da = xr.DataArray(name='a', data=[0, 1, 2], dims='x', coords={'x': [1000, 2000, 3000]})
da = da.pint.quantify({'a': 'Pa', 'x': 'm'})

da.pint.sel(x=2 * 'km')
```

Unfortunately this will not possible until the ongoing work to extend Xarray to support [explicit indexes](https://github.com/pydata/xarray/issues/1603) is complete.

In the meantime pint-xarray offers a workaround. If you tell `.quantify` the units you wish an index to have, it will store those in `.attrs["units"]` instead.

```python
time = xr.DataArray([0.1, 0.2, 0.3], dims='time')
distance = xr.DataArray(name='distance',
                        data=[10, 20, 25],
                        dims=['time'],
                        coords={'time': time})
distance = distance.pint.quantify({'distance': 'metres',
                                   'time': 'seconds'})
print(distance.coords['time'].attrs)
```

```
Out:
{'units': <Unit('second')>}
```

This allows us to provide conveniently wrapped versions of common xarray methods like `.sel`, so that you can still select subsets of data in a unit-aware fashion like this:

```python
distance.pint.sel(time=200 * pint.Unit('milliseconds'))
```

```
Out:
<xarray.DataArray 'distance' ()>
<Quantity(20, 'meter')>
Coordinates:
    time     float64 200.0
```

Observe how the `.pint.sel` operation has first converted 200 milliseconds to 0.2 seconds, before finding the distance value that occurs at a time position of 0.2 seconds.

[This wrapping is currently necessary](https://xarray.pydata.org/en/stable/user-guide/duckarrays.html#missing-features) for any operation which needs to be aware of the units of a dimension coordinate of the dataarray, or any xarray operation which relies on an external library (such as calling `scipy` in `.integrate`).

## CF-compliant units for geosciences with cf-xarray

Different fields tend to have different niche conventions about how certain units are defined.
By default, Pint doesn't understand all the unusual units and conventions we use in geosciences.
But [Pint is customisable](https://pint.readthedocs.io/en/stable/defining.html), and with the help of [cf-xarray](https://github.com/xarray-contrib/cf-xarray) we can teach it about these geoscience-specific units.

If we `import cf_xarray.units` (before `import pint_xarray`) then we can `quantify` example climate data from the [Pangeo Project's CMIP6 catalog](https://pangeo-data.github.io/pangeo-cmip6-cloud/):

```python
import xarray as xr
import cf_xarray.units
import pint_xarray

ds = xr.open_dataset('gs://cmip6/CMIP6/CMIP/NCAR/CESM2-FV2/historical/r2i1p1f1/Amon/sfcWind/gn/v20200226/', engine='zarr')
ds = ds.pint.quantify()

squared_wind = ds['sfcWind'] ** 2
squared_wind.pint.units
```

```
Out:
<Unit('meter ** 2 / second ** 2')>
```

Here (thanks to `cf_xarray`) pint has successfully interpreted the CF-style units `'m s-1'`, then automatically changed them when we squared the wind speed.

## Plotting

We can complete our real-world example by plotting the data in its new units:

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

p = squared_wind.isel(time="2014-01").plot(
    subplot_kws=dict(projection=ccrs.Orthographic(-80, 35), facecolor="gray"),
    transform=ccrs.PlateCarree(),
)
p.axes.set_global()
p.axes.coastlines()
plt.show()
```

![cartopy plot of a quantified dataset](/images/squared_wind.png)

where `xarray.plot` has detected the Pint units automatically.

## Conclusion

Please have a go! You will need xarray (v2022.03.0+), pint (0.18+), and pint-xarray (0.3+).

Please also tell us about any bugs you find, or documentation suggestions you have on the [Xarray](https://github.com/pydata/xarray/issues) or [pint-xarray issue trackers](https://github.com/xarray-contrib/pint-xarray/issues).
If you have usage questions you can raise them there, on the [Xarray discussions page](https://github.com/pydata/xarray/discussions), or on the [Pangeo Discourse forum](https://discourse.pangeo.io/).

The work here to allow Xarray to wrap Pint objects is part of a [broader effort to generalise Xarray](http://xarray.pydata.org/en/stable/roadmap.html#flexible-arrays) to handle a wide variety of data types (so-called "duck array wrapping").
Along with the incoming [support for flexible indexes](http://xarray.pydata.org/en/stable/roadmap.html#flexible-indexes), we are excited for all the new features that this will enable for Xarray users!
