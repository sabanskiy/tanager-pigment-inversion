"""
Reading Planet Tanager Basic Radiance / Surface Reflectance scenes.

Tanager products are HDF5, structured as an HDF-EOS swath:

    HDFEOS/SWATHS/HYP/Data Fields/
        toa_radiance                    (bands, rows, cols) float32
                                         attrs: wavelengths [nm], fwhm [nm], Unit
        surface_reflectance             (bands, rows, cols) float32   [SR product only]
        surface_reflectance_uncertainty (bands, rows, cols) float32   [SR product only]
        beta_cloud_mask, beta_cirrus_mask, nodata_pixels   (rows, cols) uint8
        sun_zenith, sun_azimuth, sensor_zenith, sensor_azimuth,
        sensor_to_ground_path_length    (rows, cols) float32
    HDFEOS/SWATHS/HYP/Geolocation Fields/
        Latitude, Longitude              (rows, cols) float64

Verified directly against a downloaded sample scene (see data/README.md).
Cubes are returned as (rows, cols, bands) — transposed from the file's
native (bands, rows, cols) layout — to match this repository's convention.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import h5py
import numpy as np

_SWATH_GROUP = "HDFEOS/SWATHS/HYP"
_DATA_FIELDS = f"{_SWATH_GROUP}/Data Fields"
_GEO_FIELDS = f"{_SWATH_GROUP}/Geolocation Fields"


class TanagerScene(NamedTuple):
    cube: np.ndarray  # (rows, cols, bands) — radiance or reflectance, see `variable`
    variable: str  # "toa_radiance" or "surface_reflectance"
    wavelengths: np.ndarray  # (bands,) nm
    fwhm: np.ndarray  # (bands,) nm
    unit: str
    cloud_mask: np.ndarray  # (rows, cols) bool — True where cloudy
    cirrus_mask: np.ndarray  # (rows, cols) bool
    nodata_mask: np.ndarray  # (rows, cols) bool — True where no valid data
    latitude: np.ndarray  # (rows, cols)
    longitude: np.ndarray  # (rows, cols)
    sun_zenith: np.ndarray  # (rows, cols) degrees


def _load(path: str | Path, variable: str) -> TanagerScene:
    with h5py.File(path, "r") as f:
        data_fields = f[_DATA_FIELDS]
        geo_fields = f[_GEO_FIELDS]

        ds = data_fields[variable]
        cube = np.transpose(ds[()], (1, 2, 0))  # (bands, rows, cols) -> (rows, cols, bands)
        wavelengths = np.asarray(ds.attrs["wavelengths"], dtype=float)
        fwhm = np.asarray(ds.attrs["fwhm"], dtype=float)
        unit = str(ds.attrs["Unit"])

        cloud_mask = data_fields["beta_cloud_mask"][()] > 0
        cirrus_mask = data_fields["beta_cirrus_mask"][()] > 0
        nodata_mask = data_fields["nodata_pixels"][()] > 0
        sun_zenith = data_fields["sun_zenith"][()]

        latitude = geo_fields["Latitude"][()]
        longitude = geo_fields["Longitude"][()]

    return TanagerScene(
        cube=cube,
        variable=variable,
        wavelengths=wavelengths,
        fwhm=fwhm,
        unit=unit,
        cloud_mask=cloud_mask,
        cirrus_mask=cirrus_mask,
        nodata_mask=nodata_mask,
        latitude=latitude,
        longitude=longitude,
        sun_zenith=sun_zenith,
    )


def load_basic_radiance(path: str | Path) -> TanagerScene:
    """Load a Tanager `basic_radiance_hdf5` scene (top-of-atmosphere radiance)."""
    return _load(path, "toa_radiance")


def load_surface_reflectance(path: str | Path) -> TanagerScene:
    """Load a Tanager `basic_sr_hdf5` scene (Planet's atmospherically-corrected
    surface reflectance product — the primary reflectance input for this project;
    see `src/atmospheric.py` for why this repo does not re-derive reflectance
    from radiance as its main path)."""
    return _load(path, "surface_reflectance")
