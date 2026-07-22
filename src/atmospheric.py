"""
Optional radiance-to-reflectance validation.

This project's primary reflectance input is Planet's own `basic_sr_hdf5`
product (`tanager_io.load_surface_reflectance`), which is already
atmospherically corrected — this repository does not re-derive surface
reflectance from radiance as a required pipeline step.

`empirical_line_correction` below exists only as an optional secondary
check: fit a linear radiance-to-reflectance transform from a handful of
reference pixels (e.g. bare soil / bright and dark invariant targets
visible in the scene) and compare the result against the official
`surface_reflectance` product on a few bands, as a sanity check on the
official product rather than a replacement for it.
"""

from __future__ import annotations

import numpy as np


def empirical_line_correction(
    radiance: np.ndarray,
    reference_radiance: np.ndarray,
    reference_reflectance: np.ndarray,
) -> np.ndarray:
    """Fit a per-band linear radiance-to-reflectance transform from reference targets
    and apply it to a full radiance cube.

    Parameters
    ----------
    radiance : ndarray, shape (rows, cols, bands)
    reference_radiance : ndarray, shape (n_targets, bands) — radiance sampled at reference targets
    reference_reflectance : ndarray, shape (n_targets, bands) — known reflectance of those targets

    Returns
    -------
    reflectance : ndarray, shape (rows, cols, bands)
    """
    n_targets, n_bands = reference_radiance.shape
    gain = np.empty(n_bands)
    offset = np.empty(n_bands)
    for b in range(n_bands):
        gain[b], offset[b] = np.polyfit(reference_radiance[:, b], reference_reflectance[:, b], deg=1)
    return radiance * gain + offset
