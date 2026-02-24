"""Data quality checks for OHLCV data.

These checks are lightweight and meant to emit warnings, not fail the pipeline.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from . import logger


def validate_ohlcv_dataframe(
    df: pd.DataFrame,
    symbol: str,
    open_col: str,
    high_col: str,
    low_col: str,
    close_col: str,
    volume_col: str,
    max_missing_business_days: int = 5,
    max_stale_business_days: int = 3,
) -> Dict[str, int]:
    """Run basic sanity checks and log warnings if needed.

    Returns a dict with counts of issues found.
    """
    issues = {
        "duplicates": 0,
        "missing_business_days": 0,
        "ohlc_inconsistent": 0,
        "stale_business_days": 0,
        "nan_close": 0,
        "nan_volume": 0,
    }

    if df.empty:
        return issues

    idx = df.index
    if isinstance(idx, pd.DatetimeIndex):
        if idx.tz is not None:
            idx = idx.tz_convert(None)
    else:
        return issues

    # Duplicate timestamps
    issues["duplicates"] = int(idx.duplicated().sum())
    if issues["duplicates"] > 0:
        logger.warning("[%s] %d duplicated timestamps in OHLCV data", symbol, issues["duplicates"])

    # Missing business days (heuristic, holidays will count as missing)
    start = idx.min().normalize()
    end = idx.max().normalize()
    expected = pd.date_range(start, end, freq="B")
    missing = expected.difference(idx.normalize())
    issues["missing_business_days"] = int(len(missing))
    if issues["missing_business_days"] > max_missing_business_days:
        logger.warning(
            "[%s] %d missing business days between %s and %s",
            symbol,
            issues["missing_business_days"],
            start.date(),
            end.date(),
        )

    # Stale data check
    today = pd.Timestamp.utcnow().normalize()
    if end < today:
        stale = len(pd.bdate_range(end, today)) - 1
        issues["stale_business_days"] = int(max(stale, 0))
        if issues["stale_business_days"] > max_stale_business_days:
            logger.warning(
                "[%s] Data is stale by %d business days (last=%s, today=%s)",
                symbol,
                issues["stale_business_days"],
                end.date(),
                today.date(),
            )

    # OHLC consistency checks
    low = df[low_col]
    high = df[high_col]
    open_ = df[open_col]
    close = df[close_col]

    inconsistent = (low > high) | (open_ < low) | (open_ > high) | (close < low) | (close > high)
    issues["ohlc_inconsistent"] = int(inconsistent.sum())
    if issues["ohlc_inconsistent"] > 0:
        logger.warning("[%s] %d rows with inconsistent OHLC values", symbol, issues["ohlc_inconsistent"])

    issues["nan_close"] = int(close.isna().sum())
    if issues["nan_close"] > 0:
        logger.warning("[%s] %d NaN close values", symbol, issues["nan_close"])

    issues["nan_volume"] = int(df[volume_col].isna().sum())
    if issues["nan_volume"] > 0:
        logger.warning("[%s] %d NaN volume values", symbol, issues["nan_volume"])

    return issues
