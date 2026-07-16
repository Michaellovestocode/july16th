"""
Entry point: run this to backtest the current strategy config across
all symbols in config.py, using real historical Bybit data.

Usage:
    python run_backtest.py
"""
import pandas as pd
import config as cfg
from data_fetcher import fetch_ohlcv, to_ccxt_symbol
from backtester import simulate_symbol, summarize


def main():
    all_results = {}
    all_trades = []

    for symbol in cfg.SYMBOLS:
        print(f"Fetching {symbol}...")
        ccxt_symbol = to_ccxt_symbol(symbol)
        try:
            df = fetch_ohlcv(ccxt_symbol, cfg.TIMEFRAME, cfg.HISTORY_LIMIT)
        except Exception as e:
            print(f"  Failed to fetch {symbol}: {e}")
            continue

        if len(df) < 250:
            print(f"  Not enough data for {symbol} ({len(df)} candles), skipping.")
            continue

        trades = simulate_symbol(df, symbol)
        stats = summarize(trades)
        all_results[symbol] = stats
        all_trades.extend(trades)
        print(f"  {symbol}: {stats}")

    print("\n" + "=" * 70)
    print("SUMMARY ACROSS ALL SYMBOLS")
    print("=" * 70)

    results_df = pd.DataFrame(all_results).T
    print(results_df.to_string())

    results_df.to_csv("results/backtest_summary.csv")

    trades_df = pd.DataFrame([t.__dict__ for t in all_trades])
    trades_df.to_csv("results/all_trades.csv", index=False)

    print(f"\nSaved detailed results to results/backtest_summary.csv and results/all_trades.csv")

    if not results_df.empty and "win_rate_pct" in results_df.columns:
        overall_wr = results_df["win_rate_pct"].mean()
        overall_expectancy = results_df["expectancy_pct_per_trade"].mean()
        print(f"\nAverage win rate across symbols: {overall_wr:.1f}%")
        print(f"Average expectancy per trade: {overall_expectancy:.3f}%")
        if overall_expectancy <= 0:
            print("\n⚠️  Negative/flat expectancy — this config is NOT ready for live signals.")
            print("    Try adjusting EMA/RSI/MACD periods or ATR multipliers in config.py and re-run.")


if __name__ == "__main__":
    main()
