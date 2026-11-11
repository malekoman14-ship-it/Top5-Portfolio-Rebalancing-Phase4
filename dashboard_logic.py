"""Testable dashboard adapters; no Alpaca order submission."""
from dataclasses import asdict
import numpy as np
import pandas as pd

import config
from portfolio_state import Position, build_trade_list, compute_current_weights, compute_drift, needs_rebalance


def example_prices(days=800):
    """Deterministic synthetic *educational* prices, never real quotes."""
    rng = np.random.default_rng(20261110)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    market = rng.normal(0.00035, 0.009, size=(days, 1))
    noise = rng.normal(0, 0.012, size=(days, len(config.TICKERS)))
    returns = np.clip(market + noise + np.array([0.00025,0.0001,0.0001,0.00015,0.0001]), -.18, .18)
    values = 100 * np.exp(np.cumsum(np.log1p(returns), axis=0))
    return pd.DataFrame(values, index=dates, columns=config.TICKERS)


def calculate(prices, capital, current_stock_percent, current_cash_percent):
    """Run original Phase 3 optimizer and position-sizing logic in simulation."""
    if capital <= 0:
        raise ValueError('Portfolio capital must be positive.')
    if abs(sum(current_stock_percent.values()) + current_cash_percent - 100) > .01:
        raise ValueError('Current allocation including cash must sum to 100%.')
    from optimizer import apply_cash_buffer, compute_target_weights
    raw = compute_target_weights(prices[config.TICKERS], config.MIN_WEIGHT,
                                 config.MAX_WEIGHT, config.RISK_FREE_RATE,
                                 config.OPTIMIZATION_OBJECTIVE)
    targets = apply_cash_buffer(raw, config.CASH_BUFFER)
    latest = {t: float(prices[t].iloc[-1]) for t in config.TICKERS}
    positions = [Position(ticker=t, qty=(capital * pct / 100) / latest[t],
                          market_value=capital * pct / 100)
                 for t, pct in current_stock_percent.items() if pct > 0]
    cash = capital * current_cash_percent / 100
    current = compute_current_weights(positions, cash)
    drift = compute_drift(current, targets)
    rebalance = needs_rebalance(drift, config.DRIFT_THRESHOLD)
    trades = [asdict(t) for t in build_trade_list(positions, cash, targets, latest)] if rebalance else []
    return dict(targets=targets, current=current, drift=drift,
                needs_rebalance=rebalance, trades=trades, latest=latest)
