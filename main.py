import os
import time
import math
import ccxt
from datetime import datetime, timezone

print("[DEBUG] Lancement SmartBot++ PATCH 7 - FLUSH + stepSize FIX")

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
RECYCLE_DUST = os.getenv("RECYCLE_DUST", "true").lower() == "true"
FLUSH_MODE = os.getenv("FLUSH_MODE", "true").lower() == "true"
BUDGET_TOTAL = float(os.getenv("BUDGET_TOTAL", 150))
POSITION_BUDGET = float(os.getenv("POSITION_BUDGET", 10))
MAX_POSITIONS = int(BUDGET_TOTAL // POSITION_BUDGET)

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True
})

def log(msg): print(f"[{datetime.now(timezone.utc)}] {msg}")

def get_open_positions(balance):
    return [coin for coin, data in balance.items() if isinstance(data, dict) and data.get('total', 0) > 0]

def adjust_to_step(value, step):
    return math.floor(value / step) * step

def run_bot():
    try:
        balance = exchange.fetch_balance()
        tickers = exchange.fetch_tickers()
        markets = exchange.load_markets()
        usdc_balance = balance['free'].get('USDC', 0)
    except Exception as e:
        log(f"❌ Erreur API : {e}")
        return

    log("📊 Analyse du marché...")

    for symbol in tickers:
        if "/USDC" not in symbol or symbol not in markets:
            continue

        base = symbol.replace("/USDC", "")
        market = markets[symbol]
        min_sell = float(market.get("limits", {}).get("amount", {}).get("min", 0.01))
        min_notional = float(market.get("limits", {}).get("cost", {}).get("min", 1))
        step_size = float(market.get("precision", {}).get("amount", 6))
        ticker = tickers[symbol]
        if ticker.get("last") is None:
            continue

        last_price = ticker["last"]
        qty = balance.get(base, {}).get("free", 0)
        adjusted_qty = adjust_to_step(qty, step_size)

        if adjusted_qty < min_sell or adjusted_qty * last_price < min_notional:
            continue

        try:
            if FLUSH_MODE or RECYCLE_DUST:
                exchange.create_market_sell_order(symbol, adjusted_qty)
                log(f"🧹 Flush/Revente : {adjusted_qty} {base} à {last_price}")
                time.sleep(2.0)
        except Exception as e:
            log(f"❌ Erreur flush/vente {base} : {e}")

while True:
    try:
        run_bot()
        time.sleep(60.0)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60.0)
