from datetime import datetime

def log(msg):
    print(f"[{datetime.utcnow()}] {msg}")

def get_ohlcv_trend(exchange, symbol):
    try:
        candles = exchange.fetch_ohlcv(symbol, '1m', limit=10)
        if len(candles) < 2:
            return 0.0
        first = candles[0][4]
        last = candles[-1][4]
        delta = (last - first) / first
        return max(0, min(1, delta * 10))
    except:
        return 0.0