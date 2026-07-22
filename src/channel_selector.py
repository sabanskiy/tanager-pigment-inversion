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
    return {name: int(np.argmin(np.abs(wavelengths - nm))) for name, nm in target_nm.items()}


def swir_incremental_subsets(
    wavelengths: np.ndarray,
    base_bands_nm: dict[str, float],
    swir_window_nm: float = 50.0,
    n_steps: int = 4,
) -> list[np.ndarray]:
    """Build a sequence of boolean band masks: the multispectral base subset,
    then with SWIR channels added incrementally around the water absorption
    features (1450 nm, 1940 nm), in `n_steps` widening windows.

    Returns a list of boolean masks over `wavelengths`, from base-only to
    base + full incremental SWIR window.
    """
    n_bands = len(wavelengths)
    base_idx = set(nearest_band_indices(wavelengths, base_bands_nm).values())

    base_mask = np.zeros(n_bands, dtype=bool)
    base_mask[list(base_idx)] = True

    masks = [base_mask.copy()]
    for step in range(1, n_steps + 1):
        half_window = swir_window_nm * step
        mask = base_mask.copy()
        for center in SWIR_WATER_FEATURES_NM:
            in_window = np.abs(wavelengths - center) <= half_window
            mask |= in_window
        masks.append(mask)
    return masks
