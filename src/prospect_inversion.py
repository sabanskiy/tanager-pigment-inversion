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
import prosail
from scipy.stats import qmc

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

# `prosail.run_prosail` returns reflectance on a fixed 400-2500 nm, 1 nm grid
# (its soil spectra are only defined over that range).
_PROSAIL_WAVELENGTHS = np.arange(400, 2501, dtype=float)

# Canopy structure / geometry held fixed across the LUT — this project's
# question is about biochemical parameter retrieval (Cab/Car/Ant/LAI/Cw/Cm),
# not canopy structure retrieval, so these are literature-standard defaults
# rather than additional free parameters.
_DEFAULT_LIDFA = -0.35  # spherical leaf angle distribution (typelidf=2)
_DEFAULT_HSPOT = 0.01
_DEFAULT_RSOIL = 1.0
_DEFAULT_PSOIL = 0.5


def generate_lut(
    n_samples: int,
    wavelengths: np.ndarray,
    seed: int | None = None,
    tts: float = 30.0,
    tto: float = 0.0,
    psi: float = 0.0,
) -> dict:
    """Latin-hypercube-sample PARAMETER_RANGES and simulate PROSPECT-D/SAIL
    spectra via `prosail`, resampled onto `wavelengths`.

    `tts`/`tto`/`psi` (solar zenith, sensor zenith, relative azimuth) should
    be set from the scene's own geometry (see `tanager_io.TanagerScene`)
    rather than left at the defaults, for a physically grounded LUT.

    Bands in `wavelengths` below 400 nm are outside PROSPECT/SAIL's defined
    range and are flat-extrapolated from the 400 nm edge value (`np.interp`
    default behaviour) — negligible in practice since Tanager only has a
    handful of bands there.

    Returns a dict with:
        'parameters'      : (n_samples, n_params) ndarray
        'parameter_names' : list of the n_params names, matching PARAMETER_RANGES
        'spectra'         : (n_samples, len(wavelengths)) ndarray
    """
    param_names = list(PARAMETER_RANGES.keys())
    lo = np.array([PARAMETER_RANGES[k][0] for k in param_names])
    hi = np.array([PARAMETER_RANGES[k][1] for k in param_names])

    sampler = qmc.LatinHypercube(d=len(param_names), seed=seed)
    unit_samples = sampler.random(n=n_samples)
    scaled = qmc.scale(unit_samples, lo, hi)

    spectra = np.empty((n_samples, len(wavelengths)))
    for i in range(n_samples):
        p = dict(zip(param_names, scaled[i]))
        rho = prosail.run_prosail(
            n=p["N"], cab=p["Cab"], car=p["Car"], cbrown=0.0,
            cw=p["Cw"], cm=p["Cm"], lai=p["LAI"],
            lidfa=_DEFAULT_LIDFA, hspot=_DEFAULT_HSPOT,
            tts=tts, tto=tto, psi=psi,
            ant=p["Ant"], prospect_version="D",
            rsoil=_DEFAULT_RSOIL, psoil=_DEFAULT_PSOIL,
        )
        spectra[i] = np.interp(wavelengths, _PROSAIL_WAVELENGTHS, rho)

    return {"parameters": scaled, "parameter_names": param_names, "spectra": spectra}


def invert_lut(observed_spectrum: np.ndarray, lut: dict, wavelength_mask: np.ndarray | None = None) -> dict:
    """Find the best-matching LUT entry for an observed spectrum by nearest
    neighbour (minimum sum-of-squared-residuals) search.

    Parameters
    ----------
    observed_spectrum : ndarray, shape (bands,)
    lut : output of generate_lut
    wavelength_mask : optional boolean mask selecting a channel subset
        (used for the hyperspectral vs multispectral comparison) — the
        search is restricted to these bands, but the full spectrum is still
        expected as input for a consistent call signature.

    Returns
    -------
    dict of retrieved parameter values, keyed by name.
    """
    spectra = lut["spectra"]
    obs = observed_spectrum
    if wavelength_mask is not None:
        spectra = spectra[:, wavelength_mask]
        obs = obs[wavelength_mask]

    residuals = spectra - obs
    ssr = np.sum(residuals**2, axis=1)
    best_idx = int(np.argmin(ssr))

    return dict(zip(lut["parameter_names"], lut["parameters"][best_idx]))
