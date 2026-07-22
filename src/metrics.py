"""
Retrieval quality metrics for the hyperspectral vs multispectral comparison.

RMSE and R^2 per retrieved parameter, plus bootstrap confidence intervals
to express retrieval uncertainty (relevant given the ill-posed nature of
the inversion problem this project investigates).
"""

from __future__ import annotations

import numpy as np


def rmse(true_values: np.ndarray, retrieved_values: np.ndarray) -> float:
    return float(np.sqrt(np.mean((true_values - retrieved_values) ** 2)))


def r_squared(true_values: np.ndarray, retrieved_values: np.ndarray) -> float:
    ss_res = np.sum((true_values - retrieved_values) ** 2)
    ss_tot = np.sum((true_values - np.mean(true_values)) ** 2)
    return float(1 - ss_res / ss_tot)


def bootstrap_confidence_interval(
    values: np.ndarray, n_resamples: int = 1000, ci: float = 0.95, seed: int | None = None
) -> tuple[float, float]:
    """Bootstrap confidence interval for the mean of `values`."""
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples)
    n = len(values)
    for i in range(n_resamples):
        sample = rng.choice(values, size=n, replace=True)
        means[i] = np.mean(sample)
    alpha = (1 - ci) / 2
    return float(np.quantile(means, alpha)), float(np.quantile(means, 1 - alpha))
