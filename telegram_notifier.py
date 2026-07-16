"""
Sends messages to Telegram via direct HTTP call to the Bot API.
Kept deliberately simple (no async framework) since the live bot is a
straightforward polling loop, not an interactive bot.
"""
import requests

try:
    from bot_secrets import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    raise ImportError(
        "secrets.py not found. Copy secrets_example.py to secrets.py and fill in "
        "your Telegram bot token and chat id."
    )


def send_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"[telegram] Failed to send message: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[telegram] Error sending message: {e}")


def format_signal_message(sig) -> str:
    emoji = "🟢" if sig.side == "LONG" else "🔴"
    reasons_text = "\n".join(f"  • {r}" for r in sig.reasons)
    return (
        f"{emoji} *{sig.side} SIGNAL — {sig.symbol}*\n\n"
        f"Entry: `{sig.entry:.6f}`\n"
        f"Stop Loss: `{sig.stop_loss:.6f}`\n"
        f"Take Profit: `{sig.take_profit:.6f}`\n"
        f"R:R Ratio: `{sig.rr_ratio}`\n"
        f"Suggested Leverage: `{sig.leverage}x`\n"
        f"Confidence: `{sig.confidence}%`\n\n"
        f"*Reasons:*\n{reasons_text}\n\n"
        f"⚠️ Not financial advice. Use proper risk management."
    )


def format_result_message(symbol: str, side: str, result: str, entry: float, exit_price: float, pnl_pct: float, leverage: int) -> str:
    emoji = "✅" if result == "TP" else "❌"
    result_word = "TAKE PROFIT HIT" if result == "TP" else "STOP LOSS HIT"
    leveraged_pnl = pnl_pct * leverage
    return (
        f"{emoji} *{result_word} — {symbol}*\n\n"
        f"Side: `{side}`\n"
        f"Entry: `{entry:.6f}`\n"
        f"Exit: `{exit_price:.6f}`\n"
        f"Price Move: `{pnl_pct:+.2f}%`\n"
        f"Est. P/L at {leverage}x leverage: `{leveraged_pnl:+.2f}%`\n\n"
        f"_(Estimated — actual P/L depends on your position size and fees)_"
    )
