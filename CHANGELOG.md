# Changelog

## [1.1.0] - 2026-11-09

### Changed

- Change the default network backend from `httpx` to `requests`
- Rename `coder.address()` to `coder.geocode()` and deprecate the old name
- Rename `spatial.isolines()` to `spatial.isoline()` and deprecate the old name
- Raise `ValueError` on duplicate ID values
- Mark constants with `typing.Final`

### Added

- Add support for truck routing
- Add a logistics module with support for matrix routing and TSP calculations
- Add a URL template builder for the casaGeo map tile API
- Add support for library versions `geopandas>=1.0.0`, `pandas>=2.2.0` and older versions of `numpy`
- Add `coordinates` option to `spatial.isoline()` and `spatial.routes()`
- Add `navid` output column to enumerate sub-results for results with multiple navigation points
- Add `direction` output column to `spatial.isoline()`
- Expose valid string values and integer limits as module constants
- Ignore whitespace in comma-separated lists

### Fixed

- Fix `TypeError` when `position` is `None`
- Fix `KeyError` when no navigation points are returned
- Fix `ValueError` on missing input coordinates

[1.1.0]: https://github.com/casaGeo/casaGeoTools/releases/tag/v1.1.0



## [1.0.2] - 2026-05-04

### Added

- Add documentation on https://casageotools.readthedocs.io

[1.0.2]: https://github.com/casaGeo/casaGeoTools/releases/tag/v1.0.2



## [1.0.1] - 2026-04-29

### Changed

- Update project links and metadata

### Added

- Add support for Python 3.12
- Document routing behavior regarding traffic data

### Fixed

- Reduce memory consumption the module objects

[1.0.1]: https://github.com/casaGeo/casaGeoTools/releases/tag/v1.0.1



## [1.0.0] - 2026-04-23

*First public release.*

[1.0.0]: https://github.com/casaGeo/casaGeoTools/releases/tag/v1.0.0
