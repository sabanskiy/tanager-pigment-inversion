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


def _distance_matrix(
    obs: np.ndarray, spectra: np.ndarray, cost: str, band_sigma: np.ndarray | None
) -> np.ndarray:
    """(n_pixels, n_lut) pairwise distance matrix, lower = better match.

    `cost`:
      - "sse"              : raw sum-of-squared residuals in reflectance units (the
                              original, unweighted metric — flagged in an external methods
                              review (not included in this repository) as a possible
                              confound: it over-weights the high-reflectance NIR plateau
                              relative to the low-reflectance SWIR water features).
      - "noise_normalized" : per-band residuals divided by `band_sigma` before SSR —
                              weights each band by inverse measured noise
                              (`surface_reflectance_uncertainty`), so bands the sensor
                              measures more precisely count for more.
      - "sam"               : Spectral Angle Mapper — scale-invariant by construction
                              (depends only on spectral *shape*, not magnitude), so it
                              cannot be confounded by band-magnitude imbalance at all.
                              Ranking by ascending angle is equivalent to ranking by
                              descending cosine similarity, so this returns -cos_sim.
    """
    if cost == "sse":
        a, b = obs, spectra
    elif cost == "noise_normalized":
        if band_sigma is None:
            raise ValueError("cost='noise_normalized' requires band_sigma")
        a, b = obs / band_sigma, spectra / band_sigma
    elif cost == "sam":
        obs_n = obs / np.linalg.norm(obs, axis=1, keepdims=True)
        spectra_n = spectra / np.linalg.norm(spectra, axis=1, keepdims=True)
        return -(obs_n @ spectra_n.T)
    else:
        raise ValueError(f"Unknown cost: {cost!r} (expected 'sse', 'noise_normalized', or 'sam')")

    a_norm = np.sum(a**2, axis=1, keepdims=True)
    b_norm = np.sum(b**2, axis=1)[None, :]
    cross = a @ b.T
    return a_norm + b_norm - 2 * cross


def _prepare_for_distance(
    observed_spectra: np.ndarray,
    lut: dict,
    wavelength_mask: np.ndarray | None,
    band_sigma: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    spectra = lut["spectra"]
    obs = observed_spectra
    if wavelength_mask is not None:
        spectra = spectra[:, wavelength_mask]
        obs = obs[:, wavelength_mask]
        if band_sigma is not None:
            band_sigma = band_sigma[wavelength_mask]
    return obs, spectra, band_sigma


def invert_lut_batch(
    observed_spectra: np.ndarray,
    lut: dict,
    wavelength_mask: np.ndarray | None = None,
    cost: str = "sse",
    band_sigma: np.ndarray | None = None,
) -> np.ndarray:
    """Vectorized nearest-neighbour LUT inversion for many observed spectra at once.

    The default cost ("sse") uses the identity ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a.b so
    the pairwise distance matrix is computed via a single matrix multiply rather than an
    (n_pixels, n_lut, n_bands) broadcast — this is what makes inverting thousands of real
    image pixels against an LUT of thousands of samples tractable in a notebook. The
    "noise_normalized" and "sam" costs reuse the same matmul structure (see `_distance_matrix`).

    Parameters
    ----------
    observed_spectra : ndarray, shape (n_pixels, bands)
    lut : output of generate_lut
    wavelength_mask : optional boolean band mask (hyperspectral vs multispectral comparison)
    cost : "sse" (default, unweighted), "noise_normalized", or "sam" — see `_distance_matrix`
    band_sigma : ndarray, shape (bands,) — required if cost="noise_normalized"; per-band
        noise standard deviation (e.g. from the scene's measured `surface_reflectance_uncertainty`),
        over the *same* (unmasked) band axis as `observed_spectra`/`lut["spectra"]`.

    Returns
    -------
    ndarray, shape (n_pixels, n_params) — retrieved parameters per pixel,
    columns ordered per `lut["parameter_names"]`.
    """
    obs, spectra, band_sigma = _prepare_for_distance(observed_spectra, lut, wavelength_mask, band_sigma)
    dist = _distance_matrix(obs, spectra, cost, band_sigma)
    best_idx = np.argmin(dist, axis=1)
    return lut["parameters"][best_idx]


def k_best_retrieval(
    observed_spectra: np.ndarray,
    lut: dict,
    k: int,
    wavelength_mask: np.ndarray | None = None,
    cost: str = "sse",
    band_sigma: np.ndarray | None = None,
) -> dict:
    """Return the k best-fitting LUT parameter vectors per observed spectrum, plus their
    mean and spread — the direct diagnostic for whether a parameter is well-constrained
    (tight spread among near-optimal matches) or ill-posed (broad "cost-valley" spread),
    rather than inferring ill-posedness indirectly from a negative R² on the single-NN
    (`argmin`) retrieval alone (review point M3, an external methods review not included
    in this repository).

    Returns a dict with:
        'topk_params' : ndarray (n_pixels, k, n_params), best-match-first
        'mean'        : ndarray (n_pixels, n_params)
        'std'         : ndarray (n_pixels, n_params)
        'iqr'         : ndarray (n_pixels, n_params) — 75th minus 25th percentile among the k
    """
    obs, spectra, band_sigma = _prepare_for_distance(observed_spectra, lut, wavelength_mask, band_sigma)
    dist = _distance_matrix(obs, spectra, cost, band_sigma)

    n_pixels = dist.shape[0]
    part_idx = np.argpartition(dist, k - 1, axis=1)[:, :k]
    row_idx = np.arange(n_pixels)[:, None]
    order = np.argsort(dist[row_idx, part_idx], axis=1)
    idx_sorted = part_idx[row_idx, order]

    topk_params = lut["parameters"][idx_sorted]  # (n_pixels, k, n_params)
    q75, q25 = np.percentile(topk_params, [75, 25], axis=1)
    return {
        "topk_params": topk_params,
        "mean": topk_params.mean(axis=1),
        "std": topk_params.std(axis=1),
        "iqr": q75 - q25,
    }
