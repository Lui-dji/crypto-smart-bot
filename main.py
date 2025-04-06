import os
import time
import ccxt
from datetime import datetime, timedelta

print("[DEBUG] Lancement SmartBot++ PATCH")

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
RISK_LEVEL = os.getenv("RISK_LEVEL", "medium").lower()
RECYCLE_DUST = os.getenv("RECYCLE_DUST", "true").lower() == "true"
BUDGET_TOTAL = float(os.getenv("BUDGET_TOTAL", 150))
POSITION_BUDGET = float(os.getenv("POSITION_BUDGET", 10))
MAX_POSITIONS = int(BUDGET_TOTAL // POSITION_BUDGET)

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True
})

positions = {}
last_trade_time = {}

def log(msg): print(f"[{datetime.utcnow()}] {msg}")

def get_open_positions(balance):
    return [coin for coin, data in balance.items() if isinstance(data, dict) and data['total'] > 0]

def run_bot():
    global positions
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
        if ticker.get("last") is None or ticker.get("percentage") is None:
            continue

        last_price = ticker["last"]
        change = ticker["percentage"]
        qty = balance.get(base, {}).get("free", 0)

        # PATCH ici : vérifie que la valeur d'achat supplémentaire atteindrait bien 1 USDC mini
        if qty < min_sell:
            needed = min_sell - qty
            cost = needed * last_price
            if RECYCLE_DUST and usdc_balance >= cost and cost >= min_notional:
                log(f"♻️ Recyclage : achat {round(needed, 6)} {base} pour vider résidu")
                try:
                    exchange.create_market_buy_order(symbol, needed)
                    time.sleep(1)
                    qty = min_sell
                except Exception as e:
                    log(f"❌ Erreur recyclage : {e}")
                    continue
            else:
                continue

        if qty >= min_sell and (change >= 10 or change <= -5):
            try:
                exchange.create_market_sell_order(symbol, qty)
                log(f"⚠️ Vente de {qty} {base} à {last_price} (Change: {change}%)")
                time.sleep(1)
            except Exception as e:
                log(f"❌ Erreur vente {base} : {e}")

    if len(get_open_positions(balance)) >= MAX_POSITIONS:
        log(f"🚫 Max positions atteintes ({MAX_POSITIONS}), attente...")
        return

    for symbol in tickers:
        if "/USDC" not in symbol or symbol not in markets:
            continue
        base = symbol.replace("/USDC", "")
        market = markets[symbol]
        if not market["active"]:
            continue
        min_cost = float(market.get("limits", {}).get("cost", {}).get("min", 0))
        ticker = tickers[symbol]
        if ticker.get("percentage") is None or ticker.get("last") is None:
            continue

        change = ticker["percentage"]
        last_price = ticker["last"]

        if change < 5 or POSITION_BUDGET < min_cost or usdc_balance < POSITION_BUDGET:
            continue

        amount = round(POSITION_BUDGET / last_price, 6)
        try:
            exchange.create_market_buy_order(symbol, amount)
            log(f"💰 Achat {amount} {base} à {last_price} (Change: {change}%)")
            break
        except Exception as e:
            log(f"❌ Erreur achat {base}: {e}")

while True:
    try:
        run_bot()
        time.sleep(60)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60)
