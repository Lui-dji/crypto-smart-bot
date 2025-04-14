
import os
import time
from datetime import datetime
import ccxt
import numpy as np

# === CONFIG ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")
POSITION_BUDGET = float(os.getenv("POSITION_BUDGET", 15))
SCORE_MIN = float(os.getenv("SCORE_MIN", 0.35))
IGNORE_SELL = os.getenv("IGNORE_SELL", "").split(",")

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True
})

def log(msg): print(f"[{datetime.utcnow()}] {msg}")

# === DUMMY AI MODEL ===
def compute_score(prices):
    if len(prices) < 3 or any(p is None for p in prices):
        return None
    trend = np.polyfit(range(len(prices)), prices, 1)[0]
    return max(0, min(1, trend * 10))

def get_usdc_balance():
    balance = exchange.fetch_balance()
    return balance.get('USDC', {}).get('free', 0)

def analyze_market():
    tickers = exchange.fetch_tickers()
    usdc_balance = get_usdc_balance()
    log(f"💰 Solde USDC: {usdc_balance}")
    for symbol in tickers:
        if not symbol.endswith("/USDC") or symbol.count("/") != 1:
            continue
        try:
            ticker = tickers[symbol]
            prices = [ticker.get('open'), ticker.get('high'), ticker.get('low'), ticker.get('close')]
            score = compute_score(prices)
            if score is None:
                log(f"📉 Crypto ignorée (données incomplètes) : {symbol}")
                continue
            log(f"🔎 {symbol} score={score:.2f}")
            if score >= SCORE_MIN and usdc_balance >= POSITION_BUDGET:
                base = symbol.replace("/USDC", "")
                amount = POSITION_BUDGET / ticker['last']
                log(f"💰 Achat de {amount:.4f} {base} à {ticker['last']}")
                # exchange.create_market_buy_order(symbol, amount)
        except Exception as e:
            log(f"❌ Erreur {symbol}: {e}")

while True:
    try:
        log("📊 Analyse du marché IA...")
        analyze_market()
    except Exception as e:
        log(f"🚨 Erreur globale: {e}")
    time.sleep(60)
