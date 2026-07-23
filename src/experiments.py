"""
Multi-seed, multi-cost robustness experiments.

Addresses two required points from an external methods review (not included in this repository):
- M2: headline subset comparisons rested on a single (LUT, truth, noise) seed
  triple with no uncertainty. `run_subset_experiment` repeats the comparison
  over many independent seed triples so results carry a mean +/- SD.
- M1: the inversion cost (unweighted sum-of-squared residuals) is a possible
  confound for the "targeted SWIR beats full hyperspectral" finding.
  `run_subset_experiment` accepts multiple `costs` (see
  `prospect_inversion.invert_lut_batch`) so the same seed-repeated comparison
  can be run under each cost function.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import metrics
from . import prospect_inversion as pi


def run_subset_experiment(
    seed_triples: list[tuple[int, int, int]],
    subset_masks: list[np.ndarray],
    subset_labels: list[str],
    wavelengths: np.ndarray,
    tts: float,
    costs: tuple[str, ...] = ("sse",),
    band_sigma: np.ndarray | None = None,
    n_reference_lut: int = 8000,
    n_truth: int = 300,
    noise_sigma: float = 0.005,
) -> pd.DataFrame:
    """Repeat the spectral-subset self-consistency comparison over many
    independent seed triples and (optionally) multiple inversion costs.

    Parameters
    ----------
    seed_triples : list of (lut_seed, truth_seed, noise_seed) — independent draws;
        a new reference LUT and truth set are generated per triple so the
        result reflects realisation-to-realisation variance, not just one
        lucky/unlucky draw.
    subset_masks, subset_labels : spectral subsets to compare (same mask/label
        convention as notebooks 03-05, e.g. from `channel_selector`).
    wavelengths, tts : scene wavelength grid and mean solar zenith (LUT geometry).
    costs : any of "sse", "noise_normalized", "sam" (see
        `prospect_inversion.invert_lut_batch`); multiple costs are evaluated on
        the *same* per-seed LUT/truth/noise draw, so cost comparisons are not
        confounded by realisation differences.
    band_sigma : required if "noise_normalized" is in `costs` — per-band noise
        std over the full (unmasked) wavelength grid, e.g. from the scene's own
        measured `surface_reflectance_uncertainty`.

    Returns
    -------
    Long-format DataFrame, one row per (seed_idx, cost, subset, parameter):
    seed_idx, lut_seed, truth_seed, noise_seed, cost, subset, n_bands,
    parameter, rmse, r_squared, relative_rmse_pct.
    """
    rows = []
    for seed_idx, (lut_seed, truth_seed, noise_seed) in enumerate(seed_triples):
        reference_lut = pi.generate_lut(n_samples=n_reference_lut, wavelengths=wavelengths, seed=lut_seed, tts=tts)
        truth_lut = pi.generate_lut(n_samples=n_truth, wavelengths=wavelengths, seed=truth_seed, tts=tts)

        rng = np.random.default_rng(noise_seed)
        noisy_spectra = truth_lut["spectra"] + rng.normal(0, noise_sigma, size=truth_lut["spectra"].shape)
        true_params = truth_lut["parameters"]
        param_names = reference_lut["parameter_names"]

        for cost in costs:
            cost_kwargs = {"band_sigma": band_sigma} if cost == "noise_normalized" else {}
            for label, mask in zip(subset_labels, subset_masks):
                retrieved = pi.invert_lut_batch(
                    noisy_spectra, reference_lut, wavelength_mask=mask, cost=cost, **cost_kwargs
                )
                for j, name in enumerate(param_names):
                    t, r = true_params[:, j], retrieved[:, j]
                    lo, hi = pi.PARAMETER_RANGES[name]
                    rows.append(
                        {
                            "seed_idx": seed_idx,
                            "lut_seed": lut_seed,
                            "truth_seed": truth_seed,
                            "noise_seed": noise_seed,
                            "cost": cost,
                            "subset": label,
                            "n_bands": int(mask.sum()),
                            "parameter": name,
                            "rmse": metrics.rmse(t, r),
                            "r_squared": metrics.r_squared(t, r),
                            "relative_rmse_pct": 100 * metrics.rmse(t, r) / (hi - lo),
                        }
                    )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, group_cols: tuple[str, ...] = ("cost", "subset", "n_bands", "parameter")) -> pd.DataFrame:
    """Mean +/- SD across seed_idx within each group (default: cost x subset x parameter)."""
    agg = (
        df.groupby(list(group_cols))
        .agg(
            r_squared_mean=("r_squared", "mean"),
            r_squared_sd=("r_squared", "std"),
            relative_rmse_pct_mean=("relative_rmse_pct", "mean"),
            relative_rmse_pct_sd=("relative_rmse_pct", "std"),
            n_seeds=("r_squared", "count"),
        )
        .reset_index()
    )
    return agg
