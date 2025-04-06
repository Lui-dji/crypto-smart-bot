import os
import time
import ccxt
from datetime import datetime, timezone

print("[DEBUG] Lancement SmartBot++ PATCH 3 - Recyclage + Revente directe")

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
RECYCLE_DUST = os.getenv("RECYCLE_DUST", "true").lower() == "true"
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
        ticker = tickers[symbol]
        if ticker.get("last") is None:
            continue

        last_price = ticker["last"]
        qty = balance.get(base, {}).get("free", 0)

        if qty < min_sell:
            needed = min_sell - qty
            cost = needed * last_price
            if RECYCLE_DUST and usdc_balance >= cost and cost >= min_notional:
                try:
                    exchange.create_market_buy_order(symbol, needed)
                    log(f"♻️ Recyclage : achat {round(needed, 6)} {base}")
                    time.sleep(1)

                    full_qty = qty + needed
                    exchange.create_market_sell_order(symbol, full_qty)
                    log(f"✅ Résidu revendu : {full_qty} {base} à {last_price}")
                    time.sleep(1)
                    continue
                except Exception as e:
                    log(f"❌ Erreur recyclage/vente {base} : {e}")
                    continue

        # Vente normale si valeur suffisante
        if qty >= min_sell and qty * last_price >= min_notional:
            try:
                exchange.create_market_sell_order(symbol, qty)
                log(f"⚠️ Vente directe de {qty} {base} à {last_price}")
                time.sleep(1)
            except Exception as e:
                log(f"❌ Erreur vente {base} : {e}")

while True:
    try:
        run_bot()
        time.sleep(60)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60)
