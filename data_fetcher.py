"""
Pulls historical OHLCV candles from Bybit for backtesting, and can also
be used by the live bot later for the same data shape.

Uses ccxt (no API key needed for public market data).
"""
import time
import pandas as pd
import ccxt


def get_exchange():
    return ccxt.bybit({
        "enableRateLimit": True,
        "options": {"defaultType": "swap"},  # perpetuals
    })


def fetch_ohlcv(symbol: str, timeframe: str, total_candles: int = 1000) -> pd.DataFrame:
    """
    Fetches up to `total_candles` candles, paging backwards if needed
    (ccxt/Bybit typically caps a single call at 200-1000 depending on endpoint).
    symbol format for ccxt bybit swap: 'BTC/USDT:USDT'
    """
    exchange = get_exchange()
    tf_map = {  # Bybit numeric intervals -> ccxt timeframe strings
        "1": "1m", "3": "3m", "5": "5m", "15": "15m", "30": "30m",
        "60": "1h", "120": "2h", "240": "4h", "360": "6h", "720": "12h",
        "D": "1d", "W": "1w", "M": "1M",
    }
    ccxt_tf = tf_map.get(timeframe, "15m")

    all_rows = []
    limit = 1000
    since = None

    # Fetch most recent candles first, then page backwards until we have enough
    while len(all_rows) < total_candles:
        batch = exchange.fetch_ohlcv(symbol, timeframe=ccxt_tf, since=since, limit=limit)
        if not batch:
            break
        all_rows = batch + all_rows if since else batch
        if len(batch) < limit:
            break
        earliest_ts = batch[0][0]
        since = earliest_ts - (limit * exchange.parse_timeframe(ccxt_tf) * 1000)
        time.sleep(exchange.rateLimit / 1000)

    df = pd.DataFrame(all_rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df = df.drop_duplicates(subset="timestamp").sort_values("timestamp").reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df.tail(total_candles).reset_index(drop=True)


def to_ccxt_symbol(bybit_symbol: str) -> str:
    """Converts 'BTCUSDT' -> 'BTC/USDT:USDT' (ccxt unified perpetual format)."""
    base = bybit_symbol.replace("USDT", "")
    return f"{base}/USDT:USDT"
