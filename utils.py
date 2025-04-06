import time
import ccxt
from datetime import datetime, timezone

def log(msg):
    print(f"[{datetime.now(timezone.utc)}] {msg}")

def get_trend_score(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=10)
        closes = [c[4] for c in ohlcv]
        if len(closes) < 5:
            return 0
        delta = closes[-1] - closes[0]
        score = delta / closes[0]
        return max(0, min(1, score * 10))  # Normalisé entre 0 et 1
    except Exception as e:
        return 0
