"""Correlation-matrix and network analyses."""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import minimum_spanning_tree as scipy_mst

from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score, completeness_score, homogeneity_score

# --------------------------------------------------------------------------
# Random matrix theory
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# Minimum spanning tree
# --------------------------------------------------------------------------
def mantegna_distance(C: pd.DataFrame) -> pd.DataFrame:
    """d = sqrt(2(1 - rho)): turns correlations into a true distance (Mantegna 1999)."""
    return np.sqrt(np.clip(2 * (1 - C), 0, None))


def minimum_spanning_tree(C: pd.DataFrame) -> nx.Graph:
    """Tree connecting all stocks with the smallest total Mantegna distance."""
    D = mantegna_distance(C).values.copy()
    np.fill_diagonal(D, 0)
    # scipy reads a 0 as "no link". That's fine here: only the diagonal is 0,
    # because duplicate share classes were removed, so no two stocks have rho = 1.
    tree = scipy_mst(D).tocoo()

    tickers = list(C.index)
    T = nx.Graph()
    T.add_nodes_from(tickers)
    for i, j, d in zip(tree.row, tree.col, tree.data):
        T.add_edge(tickers[i], tickers[j], distance=float(d), corr=float(C.values[i, j]))
    return T


def same_sector_share(T: nx.Graph, sector_of: dict) -> float:
    """Fraction of tree links that join two stocks in the same sector."""
    return float(np.mean([sector_of[u] == sector_of[v] for u, v in T.edges()]))


def shuffled_sector_share(T: nx.Graph, sectors: pd.Series, n_shuffles: int = 1000,
                          seed: int = 0) -> np.ndarray:
    """Null model: the same tree, with sector labels randomly reassigned to stocks."""
    rng = np.random.default_rng(seed)
    nodes = list(T.nodes())
    labels = sectors.loc[nodes].values
    return np.array([
        same_sector_share(T, dict(zip(nodes, rng.permutation(labels))))
        for _ in range(n_shuffles)
    ])

# --------------------------------------------------------------------------
# Communities vs GICS sectors
# --------------------------------------------------------------------------
def score_partition(true_labels, pred_labels) -> dict:
    """ARI (0 = chance, 1 = perfect), homogeneity (pure groups), completeness (unsplit sectors)."""
    return {
        "ari": adjusted_rand_score(true_labels, pred_labels),
        "homogeneity": homogeneity_score(true_labels, pred_labels),
        "completeness": completeness_score(true_labels, pred_labels),
    }


def louvain_partition(C: pd.DataFrame, resolution: float = 1.0, seed: int = 0) -> pd.Series:
    """Louvain on the full graph weighted by correlation (negative links set to 0)."""
    W = np.clip(C.values, 0, None)             # Louvain needs non-negative weights
    np.fill_diagonal(W, 0)
    G = nx.from_numpy_array(W)
    comms = nx.community.louvain_communities(G, weight="weight", resolution=resolution, seed=seed)
    labels = np.empty(len(C), dtype=int)
    for k, members in enumerate(comms):
        labels[list(members)] = k
    return pd.Series(labels, index=C.index)


def louvain_sweep(C: pd.DataFrame, sectors: pd.Series, resolutions, seed: int = 0) -> pd.DataFrame:
    """Score Louvain against the sectors at each resolution."""
    rows = []
    for r in resolutions:
        part = louvain_partition(C, r, seed)
        rows.append({"resolution": r, "communities": part.nunique(),
                     **score_partition(sectors.loc[C.index], part)})
    return pd.DataFrame(rows)


def hierarchical_partition(C: pd.DataFrame, n_clusters: int) -> pd.Series:
    """Baseline: average-linkage clustering on Mantegna distance, cut into n_clusters groups."""
    D = mantegna_distance(C).values.copy()
    np.fill_diagonal(D, 0)
    Z = linkage(squareform(D, checks=False), method="average")
    return pd.Series(fcluster(Z, n_clusters, criterion="maxclust"), index=C.index)