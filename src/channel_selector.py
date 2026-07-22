"""
Selecting spectral channel subsets for the hyperspectral vs multispectral
inversion comparison.

Defines the full Tanager VSWIR band set and simulated multispectral sensor
subsets (e.g. a 5-band UAV multispectral sensor), plus incremental SWIR
channel additions used in the SWIR contribution analysis.
"""

from __future__ import annotations

import numpy as np

# Approximate band centres (nm) for a typical 5-band UAV multispectral sensor,
# used to simulate a multispectral subset from the full Tanager spectrum.
MULTISPECTRAL_BANDS_NM = {
    "blue": 450,
    "green": 560,
    "red": 650,
    "red_edge": 730,
    "nir": 840,
}

# Water absorption feature windows (nm) relevant to Cw/Cm retrieval.
SWIR_WATER_FEATURES_NM = (1450, 1940)


def nearest_band_indices(wavelengths: np.ndarray, target_nm: dict[str, float]) -> dict[str, int]:
    """Map named target wavelengths to the nearest available Tanager band index."""
    raise NotImplementedError


def swir_incremental_subsets(wavelengths: np.ndarray, base_bands_nm: dict[str, float]) -> list[np.ndarray]:
    """Build a sequence of boolean band masks: multispectral base, then with
    SWIR channels added incrementally around the water absorption features."""
    raise NotImplementedError
