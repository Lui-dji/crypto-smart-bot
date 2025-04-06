import os
import time
import math
import ccxt
from datetime import datetime, timezone

print("[DEBUG] Lancement SmartBot++ PATCH 8 - Dust Merge + Flush")

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

        # Si la quantité est trop faible pour être vendue, on tente de compléter
        if adjusted_qty < min_sell or adjusted_qty * last_price < min_notional:
            if RECYCLE_DUST and usdc_balance > 0:
                needed = min_sell - qty
                cost = needed * last_price
                if cost <= usdc_balance and cost >= min_notional:
                    try:
                        buy_qty = adjust_to_step(needed, step_size)
                        exchange.create_market_buy_order(symbol, buy_qty)
                        log(f"♻️ Achat complémentaire : {buy_qty} {base} pour compléter un résidu")
                        time.sleep(1.5)
                        # Après achat, revente complète
                        balance = exchange.fetch_balance()
                        qty = balance.get(base, {}).get("free", 0)
                        sell_qty = adjust_to_step(qty, step_size)
                        if sell_qty >= min_sell and sell_qty * last_price >= min_notional:
                            exchange.create_market_sell_order(symbol, sell_qty)
                            log(f"✅ Résidu fusionné & revendu : {sell_qty} {base}")
                            time.sleep(1.5)
                    except Exception as e:
                        log(f"❌ Erreur fusion/vente {base} : {e}")
            continue

        # Si assez de quantité → vendre normalement (flush)
        if FLUSH_MODE and adjusted_qty >= min_sell and adjusted_qty * last_price >= min_notional:
            try:
                exchange.create_market_sell_order(symbol, adjusted_qty)
                log(f"🧹 Flush direct : {adjusted_qty} {base}")
                time.sleep(1.5)
            except Exception as e:
                log(f"❌ Erreur flush {base} : {e}")

while True:
    try:
        run_bot()
        time.sleep(60.0)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60.0)
