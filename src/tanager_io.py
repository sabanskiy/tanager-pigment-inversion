"""
Reading Planet Tanager Basic Radiance scenes.

Supports ENVI format (.hdr/.bil, via the `spectral` package) and GeoTIFF
(via `rasterio`). Returns radiance cubes with band-centre wavelengths (nm)
attached, since downstream PROSPECT-D/SAIL inversion is indexed by wavelength
rather than band number.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_envi_radiance(header_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load an ENVI-format Tanager Basic Radiance cube.

    Parameters
    ----------
    header_path : path to the .hdr file (companion .bil/.img must sit alongside it)

    Returns
    -------
    radiance : ndarray, shape (rows, cols, bands)
    wavelengths : ndarray, shape (bands,) — band-centre wavelengths in nm
    """
    raise NotImplementedError


def load_geotiff_radiance(tif_path: str | Path, wavelengths: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Load a GeoTIFF-format Tanager Basic Radiance cube.

    Wavelengths are not embedded in GeoTIFF band metadata in general, so the
    band-centre wavelength array must be supplied separately (from the
    scene's accompanying metadata file).
    """
    raise NotImplementedError
