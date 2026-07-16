"""
Central configuration for the bot.
Tune these after seeing backtest results — don't just guess-and-check on live data.
"""

# --- Symbols to scan (Bybit USDT perpetuals) ---
# ADAUSDT and LINKUSDT removed after backtest validation showed negative/near-zero
# expectancy with high drawdown. Only trade symbols with a demonstrated edge.
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
]

# --- Timeframe for signal generation ---
# Bybit kline intervals: 1,3,5,15,30,60,120,240,360,720,D,W,M
TIMEFRAME = "15"          # 15-minute candles — adjust for scalp speed
HISTORY_LIMIT = 6000     # candles to pull per backtest (~62 days on 15m) — need enough for a real sample size

# --- Trend filter (regime detection) ---
EMA_FAST = 50
EMA_SLOW = 200
# Minimum % gap between EMA_FAST and EMA_SLOW (relative to price) required
# to call it a real trend, not just a fresh/weak crossover. Raise this if
# too many low-quality signals are getting through.
TREND_STRENGTH_MIN_PCT = 0.5

# --- Entry trigger ---
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
RSI_MIDLINE = 50   # longs require RSI above this, shorts require RSI below this (momentum confirmation)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# --- Volatility / risk ---
ATR_PERIOD = 14
ATR_SL_MULT = 1.5        # stop loss = ATR * this
ATR_TP_MULT = 3.0         # take profit = ATR * this (gives ~2:1 R:R baseline)
MIN_ATR_PCT = 0.15        # skip signal if ATR% of price below this (dead market)
MAX_ATR_PCT = 3.5         # skip signal if ATR% of price above this (news spike / unstable)

# --- Leverage suggestion ---
# Suggested leverage scales DOWN as volatility (ATR%) goes UP.
MAX_LEVERAGE = 20
MIN_LEVERAGE = 3

# --- Cooldown / signal throttling ---
COOLDOWN_BARS = 6          # bars to wait after a closed trade on same symbol before re-signaling
MAX_SIGNALS_PER_DAY_PER_SYMBOL = 4   # quality over quantity — tune after backtest

# --- Backtest ---
STARTING_BALANCE = 1000
RISK_PER_TRADE_PCT = 1.0   # % of balance risked per trade (for equity curve simulation)
TAKER_FEE_PCT = 0.055      # Bybit perpetual taker fee (approx, check current fee tier)

# --- Live bot settings ---
POLL_INTERVAL_SECONDS = 30      # how often to check price for open-position TP/SL hits
KLINE_FETCH_LIMIT = 300         # candles to fetch each cycle for indicator calculation (needs > EMA_SLOW)
LOG_FILE = "live_bot.log"
STATE_FILE = "bot_state.json"   # persists open positions + daily trade log across restarts
API_CALL_DELAY_SECONDS = 1.5    # pause between each symbol's API call, avoids bursting Bybit's rate limit
RATE_LIMIT_BACKOFF_SECONDS = 60 # extra wait if Bybit's rate limit is hit, before resuming normal polling

# Daily loss circuit breaker: if cumulative leveraged P/L for the day (WAT)
# drops to or below this %, new signals pause until midnight WAT reset.
# Existing open positions are still monitored and closed normally either way.
MAX_DAILY_LOSS_PCT = -5.0
