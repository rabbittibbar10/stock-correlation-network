"""Download S&P 500 constituents and daily prices."""
from __future__ import annotations
import numpy as np

import io
from pathlib import Path

import pandas as pd
import requests

WIKI_SP500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
DATA_DIR = Path("data")


def get_constituents() -> pd.DataFrame:
    """Current S&P 500 members with their GICS sector, cached to data/constituents.csv."""
    cache = DATA_DIR / "constituents.csv"
    if cache.exists():
        return pd.read_csv(cache)

    # Wikipedia blocks requests that don't say who they are, so send a User-Agent
    html = requests.get(
        WIKI_SP500,
        headers={"User-Agent": "stock-correlation-network (student research project)"},
        timeout=30,
    ).text
    table = pd.read_html(io.StringIO(html))[0]   # the first table on the page is the member list

    df = pd.DataFrame({
        # Yahoo writes BRK.B as BRK-B, so convert the format
        "ticker": table["Symbol"].str.replace(".", "-", regex=False),
        "name": table["Security"],
        "sector": table["GICS Sector"],
    })
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(cache, index=False)
    return df


def download_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Daily adjusted close prices (rows = dates, columns = tickers), cached to CSV."""
    cache = DATA_DIR / f"prices_{start}_{end}.csv"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)

    import yfinance as yf

    # auto_adjust=True corrects prices for dividends and stock splits, so returns are real
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=True)
    prices = raw["Close"].sort_index()

    DATA_DIR.mkdir(exist_ok=True)
    prices.to_csv(cache)
    return prices


def clean_prices(prices: pd.DataFrame, max_gap: int = 5) -> pd.DataFrame:
    """Keep only stocks with a price on every day of the window (short gaps filled)."""
    prices = prices.dropna(how="all")          # drop days where no stock has a price
    prices = prices.ffill(limit=max_gap)       # fill short gaps, e.g. a trading halt
    return prices.dropna(axis=1)               # drop any stock still missing data


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily log returns: ln(P_t / P_{t-1})."""
    return np.log(prices).diff().dropna(how="all")