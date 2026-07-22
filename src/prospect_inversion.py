"""
PROSPECT-D/SAIL LUT generation and inversion.

Uses the open-source `prosail` package (Féret et al.) to build a Look-Up
Table over literature-standard parameter ranges, then inverts observed
reflectance spectra by nearest-neighbour LUT lookup. See REFERENCES.md for
citations.

Parameter ranges here are for demonstration/analysis purposes and are not
SilvaIQ's production-calibrated LUT ranges.
"""

from __future__ import annotations

import numpy as np

# Literature-standard parameter ranges for LUT generation (not production values).
PARAMETER_RANGES = {
    "N": (1.0, 2.5),       # leaf structure parameter
    "Cab": (0.0, 80.0),    # chlorophyll a+b, ug/cm2
    "Car": (0.0, 20.0),    # carotenoids, ug/cm2
    "Ant": (0.0, 10.0),    # anthocyanins, ug/cm2
    "Cw": (0.002, 0.05),   # equivalent water thickness, cm
    "Cm": (0.002, 0.02),   # dry matter, g/cm2
    "LAI": (0.5, 6.0),     # leaf area index
}


def generate_lut(n_samples: int, wavelengths: np.ndarray, seed: int | None = None) -> dict:
    """Sample PARAMETER_RANGES and simulate PROSPECT-D/SAIL spectra via `prosail`.

    Returns a dict with 'parameters' (n_samples, n_params) and 'spectra'
    (n_samples, n_bands) arrays.
    """
    raise NotImplementedError


def invert_lut(observed_spectrum: np.ndarray, lut: dict, wavelength_mask: np.ndarray | None = None) -> dict:
    """Find the best-matching LUT entry for an observed spectrum.

    Parameters
    ----------
    observed_spectrum : ndarray, shape (bands,)
    lut : output of generate_lut
    wavelength_mask : optional boolean mask selecting a channel subset
        (used for the hyperspectral vs multispectral comparison)

    Returns
    -------
    dict of retrieved parameter values, keyed by name.
    """
    raise NotImplementedError
