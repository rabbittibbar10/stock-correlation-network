"""Reusable figures."""
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

# One fixed colour per sector (11 sectors), so a sector is the same colour in every figure
SECTOR_COLOURS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
                  "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#393b79"]


def sector_colour_map(sectors: pd.Series) -> dict:
    return {s: SECTOR_COLOURS[i % len(SECTOR_COLOURS)] for i, s in enumerate(sorted(sectors.unique()))}


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


def mst_figure(T: nx.Graph, sectors: pd.Series, title: str, label_top: int = 10):
    """Draw the tree, colouring stocks by sector and labelling the biggest hubs."""
    pos = nx.kamada_kawai_layout(T)            # a layout that spreads trees out nicely
    colour = sector_colour_map(sectors)

    fig, ax = plt.subplots(figsize=(11, 9))
    nx.draw_networkx_edges(T, pos, ax=ax, edge_color="#bbbbbb", width=0.8)
    for s, c in colour.items():
        nodes = [v for v in T.nodes() if sectors[v] == s]
        nx.draw_networkx_nodes(T, pos, nodelist=nodes, node_color=c, node_size=30,
                               edgecolors="white", linewidths=0.5, label=s, ax=ax)
    for v, d in sorted(T.degree(), key=lambda x: -x[1])[:label_top]:
        ax.annotate(f"{v} ({d})", pos[v], xytext=(4, 4), textcoords="offset points", fontsize=8)

    ax.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=8, frameon=False, title="GICS sector")
    ax.set_title(title)
    ax.axis("off")
    return fig