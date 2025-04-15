
from datetime import datetime

def log(msg):
    print(f"[{datetime.utcnow()}] {msg}")

def get_trend_score(exchange, symbol):
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=10)
        if len(candles) < 2:
            return 0
        first = candles[0][4]
        last = candles[-1][4]
        delta = (last - first) / first
        score = max(0, min(1, delta * 10))
        return score
    except:
        return 0
