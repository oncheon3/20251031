from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

DATA_PATH = Path(__file__).resolve().with_name("temp.csv")
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.03  # 3% annualised risk-free rate assumption


@lru_cache(maxsize=1)
def load_close_prices() -> pd.DataFrame:
    """Load and tidy the closing price data from ``temp.csv``."""
    df = pd.read_csv(DATA_PATH, header=[0, 1], index_col=0, skiprows=[2])
    df.index = pd.to_datetime(df.index)
    close = df["Close"].apply(pd.to_numeric, errors="coerce")
    close = close.sort_index().dropna(how="all")
    return close


def compute_portfolio_statistics() -> Dict[str, object]:
    close = load_close_prices()
    returns = close.pct_change().dropna(how="any")

    mean_returns = returns.mean() * TRADING_DAYS_PER_YEAR
    cov_matrix = returns.cov() * TRADING_DAYS_PER_YEAR

    tickers = mean_returns.index.to_list()
    rng = np.random.default_rng(seed=42)
    weights = rng.dirichlet(np.ones(len(tickers)), size=4000)

    port_returns = weights @ mean_returns.to_numpy()
    port_vols = np.sqrt(np.einsum("ij,jk,ik->i", weights, cov_matrix.to_numpy(), weights))
    with np.errstate(divide="ignore", invalid="ignore"):
        sharpe = (port_returns - RISK_FREE_RATE) / port_vols
    sharpe = np.nan_to_num(sharpe, nan=-np.inf, neginf=-np.inf, posinf=np.inf)

    frontier: List[Dict[str, float]] = []
    for ret, vol, shp in zip(port_returns, port_vols, sharpe):
        frontier.append({
            "return": float(ret * 100),
            "risk": float(vol * 100),
            "sharpe": float(shp),
        })

    min_vol_idx = int(np.argmin(port_vols))
    max_sharpe_idx = int(np.argmax(sharpe))

    def describe_portfolio(idx: int) -> Dict[str, object]:
        weight_vector = weights[idx]
        return {
            "return": float(port_returns[idx] * 100),
            "risk": float(port_vols[idx] * 100),
            "sharpe": float(sharpe[idx]),
            "weights": {
                ticker: float(weight)
                for ticker, weight in zip(tickers, weight_vector)
            },
        }

    asset_stats = []
    asset_vols = np.sqrt(np.diag(cov_matrix.to_numpy()))
    for ticker, mean_return, vol in zip(tickers, mean_returns.to_numpy(), asset_vols):
        asset_stats.append({
            "ticker": ticker,
            "return": float(mean_return * 100),
            "risk": float(vol * 100),
        })

    latest_prices = close.iloc[-1].dropna().to_dict()

    return {
        "frontier": frontier,
        "min_vol": describe_portfolio(min_vol_idx),
        "max_sharpe": describe_portfolio(max_sharpe_idx),
        "assets": asset_stats,
        "latest_prices": latest_prices,
        "tickers": tickers,
    }


@app.route("/")
def index():
    stats = compute_portfolio_statistics()
    return render_template(
        "index.html",
        frontier=stats["frontier"],
        min_portfolio=stats["min_vol"],
        max_portfolio=stats["max_sharpe"],
        assets=stats["assets"],
        latest_prices=stats["latest_prices"],
        tickers=stats["tickers"],
        risk_free_rate=RISK_FREE_RATE * 100,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
