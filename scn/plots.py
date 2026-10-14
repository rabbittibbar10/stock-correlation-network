"""Reusable figures."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def sector_heatmap(C: pd.DataFrame, sectors: pd.Series, title: str, vmax: float = 1.0):
    """Correlation matrix with stocks grouped by sector and sector boundaries marked."""
    order = sectors.sort_values().index
    s = sectors.loc[order].values

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(C.loc[order, order], cmap="RdBu_r", vmin=-vmax, vmax=vmax)

    bounds = np.where(s[1:] != s[:-1])[0] + 0.5
    for b in bounds:
        ax.axhline(b, color="white", lw=0.6)
        ax.axvline(b, color="white", lw=0.6)
    starts = np.r_[0, bounds + 0.5]
    ends = np.r_[bounds + 0.5, len(s)]
    ax.set_yticks((starts + ends) / 2 - 0.5)
    ax.set_yticklabels(s[starts.astype(int)], fontsize=7)
    ax.set_xticks([])
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.04, label="Correlation")
    return fig