# Bybit Multi-Symbol Signal Bot — Backtest First

## What this is (Phase 1 of 2)

This is the **backtesting engine**, not the live Telegram bot yet. On purpose.
Before this fires a single live signal, you need to see real numbers on real
Bybit history — that's what actually separates this from the old bot that
went bad. Get the strategy validated here first; the live/Telegram layer is
a small addition once the logic is proven.

## Setup

```bash
pip install -r requirements.txt --break-system-packages   # if on a system-managed Python (e.g. your VPS)
python run_backtest.py
```

This will:
1. Pull ~1000 historical 15m candles per symbol from Bybit (public data, no API key needed).
2. Run the exact strategy logic (trend filter + MACD/RSI confluence + ATR volatility gate) bar-by-bar.
3. Simulate trades with ATR-based SL/TP, track wins/losses, apply Bybit taker fees.
4. Print win rate, expectancy, R:R, drawdown, and equity curve per symbol.
5. Save `results/backtest_summary.csv` and `results/all_trades.csv`.

## How to read the results

- **`win_rate_pct`** — % of trades that hit TP vs SL.
- **`avg_rr`** — average reward:risk actually achieved (should be near your `ATR_TP_MULT / ATR_SL_MULT` setting, e.g. 3.0/1.5 = 2.0).
- **`expectancy_pct_per_trade`** — the number that matters most. This is your real edge per trade, in % price move. **If this is ≤ 0, do not go live with this config** — it means the strategy loses money on average even before you add real slippage.
- **`max_drawdown_pct`** — worst peak-to-trough equity decline in the backtest. Gives you a feel for what a losing streak looks like.

## What to tune if results are weak

All in `config.py`:
- `EMA_FAST` / `EMA_SLOW` — trend filter sensitivity. Tighter = more signals, more noise. Wider = fewer, higher-quality signals.
- `RSI_OVERBOUGHT` / `RSI_OVERSOLD` — how strict the momentum filter is.
- `ATR_SL_MULT` / `ATR_TP_MULT` — your risk:reward per trade. Don't just raise TP multiplier to "improve" numbers — check `win_rate_pct` doesn't collapse alongside it.
- `MIN_ATR_PCT` / `MAX_ATR_PCT` — volatility gate. If a symbol shows 0 trades, its volatility might be outside this range for the timeframe chosen.
- `TIMEFRAME` — 15m is a reasonable scalp starting point. Faster timeframes (5m, 3m) = more signals but more noise and fee drag relative to average move size.

**Important honesty note:** past performance in a backtest does not guarantee future results, and this backtest doesn't model slippage, partial fills, or funding rate costs on perpetuals (all of which eat into real returns). Treat a backtest as a filter for "is this obviously broken" rather than proof it'll be profitable live. Consider paper-trading (see Phase 2) before risking real capital.

## Phase 2 (next step, once backtest looks solid)

Once `expectancy_pct_per_trade` is consistently positive across most symbols over a good sample size (aim for 50+ trades per symbol, not 5-10 — small samples lie):
1. Add the live scanning loop (reuses `strategy.py` + `indicators.py` unchanged).
2. Add Telegram bot integration for signal alerts + TP/SL hit notifications.
3. Add per-symbol state tracking + cooldown + daily signal cap (`config.py` already has these params ready).
4. Optionally run in **paper-trading mode** first (log what would have happened without sending real orders) before wiring in actual VPS-based live signal sends.

Let me know your backtest numbers and I'll help build Phase 2 tuned to what's actually working, rather than guessing.
