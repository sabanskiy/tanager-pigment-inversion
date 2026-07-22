"""
Basic radiance-to-reflectance atmospheric correction.

Two paths are supported depending on scene contents:

1. Empirical line correction, if the scene contains known reference targets
   (e.g. calibration panels or invariant surfaces) with known reflectance.
2. A simplified ATCOR-like radiative-transfer approach otherwise, using
   standard atmospheric parameters (AOD, water vapour) rather than
   scene-specific ground truth.

This module implements a general open approach — it is not SilvaIQ's
internal atmospheric correction pipeline.
"""

from __future__ import annotations

import numpy as np


def empirical_line_correction(
    radiance: np.ndarray,
    reference_radiance: np.ndarray,
    reference_reflectance: np.ndarray,
) -> np.ndarray:
    """Fit a per-band linear radiance-to-reflectance transform from reference targets.

    Parameters
    ----------
    radiance : ndarray, shape (rows, cols, bands)
    reference_radiance : ndarray, shape (n_targets, bands) — radiance sampled at reference targets
    reference_reflectance : ndarray, shape (n_targets, bands) — known reflectance of those targets

    Returns
    -------
    reflectance : ndarray, shape (rows, cols, bands)
    """
    raise NotImplementedError


def simplified_atmospheric_correction(
    radiance: np.ndarray,
    wavelengths: np.ndarray,
    solar_zenith_deg: float,
) -> np.ndarray:
    """Approximate radiance-to-reflectance conversion without reference targets."""
    raise NotImplementedError
