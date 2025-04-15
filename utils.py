from datetime import datetime

def log(msg):
    print(f"[{datetime.utcnow()}] {msg}")

def get_ohlcv_trend(candles):
    if len(candles) < 2:
        return 0
    first_close = candles[0][4]
    last_close = candles[-1][4]
    delta = (last_close - first_close) / first_close
    score = max(0, min(1, delta * 10))
    return score
