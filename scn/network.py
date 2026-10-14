"""Correlation-matrix and network analyses."""
from __future__ import annotations

import numpy as np
import pandas as pd


def eigen_decomposition(C: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues (largest first) and matching eigenvectors (as columns)."""
    vals, vecs = np.linalg.eigh(C.values)      # eigh is for symmetric matrices: fast and exact
    order = np.argsort(vals)[::-1]
    return vals[order], vecs[:, order]


def mp_upper_bound(n_stocks: int, n_days: int, noise_variance: float = 1.0) -> float:
    """Largest eigenvalue pure noise would produce (Marchenko-Pastur law)."""
    q = n_stocks / n_days
    return noise_variance * (1 + np.sqrt(q)) ** 2


def remove_market_mode(C: pd.DataFrame, n_days: int) -> pd.DataFrame:
    """Rebuild the correlation matrix from the 'sector' eigenmodes only.

    Drops the market mode (eigenvalue 1) and every eigenvalue inside the noise band.
    """
    vals, vecs = eigen_decomposition(C)
    N = len(C)
    noise_var = 1 - vals[0] / N                # variance left once the market mode is removed
    lam_max = mp_upper_bound(N, n_days, noise_var)
    keep = [k for k in range(1, N) if vals[k] > lam_max]
    Cg = (vecs[:, keep] * vals[keep]) @ vecs[:, keep].T
    return pd.DataFrame(Cg, index=C.index, columns=C.columns)