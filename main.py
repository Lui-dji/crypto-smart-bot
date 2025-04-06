import os
import time
import math
import ccxt
from datetime import datetime, timezone

print("[DEBUG] Lancement SmartBot++ PATCH 12 - Looping Residue Flush")

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
RECYCLE_DUST = os.getenv("RECYCLE_DUST", "true").lower() == "true"
FLUSH_MODE = os.getenv("FLUSH_MODE", "true").lower() == "true"
OVERBUY_FACTOR = float(os.getenv("DUST_OVERBUY_FACTOR", 3))
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

def attempt_final_resell(base, symbol, step, minQty, minNotional, last_price):
    """Essaie de vider la position jusqu'à disparition du résidu"""
    for _ in range(3):
        try:
            balance = exchange.fetch_balance()
            qty = balance.get(base, {}).get("free", 0)
            adjusted_qty = adjust_to_step(qty, step)
            if adjusted_qty >= minQty and adjusted_qty * last_price >= minNotional:
                exchange.create_market_sell_order(symbol, adjusted_qty)
                log(f"♻️ Revente résidu final : {adjusted_qty} {base}")
                time.sleep(1.5)
            else:
                break
        except Exception as e:
            log(f"❌ Erreur revente finale {base} : {e}")
            break

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

    dust_targets = []

    for symbol in tickers:
        if "/USDC" not in symbol or symbol not in markets:
            continue

        base = symbol.replace("/USDC", "")
        market = markets[symbol]
        filters = market.get("info", {}).get("filters", [])
        stepSize = next((float(f["stepSize"]) for f in filters if f["filterType"] == "LOT_SIZE"), 0.000001)
        minQty = next((float(f["minQty"]) for f in filters if f["filterType"] == "LOT_SIZE"), 0.000001)
        minNotional = float(market.get("limits", {}).get("cost", {}).get("min", 1))

        ticker = tickers[symbol]
        if ticker.get("last") is None:
            continue

        last_price = ticker["last"]
        qty = balance.get(base, {}).get("free", 0)
        adjusted_qty = adjust_to_step(qty, stepSize)

        if FLUSH_MODE and adjusted_qty >= minQty and adjusted_qty * last_price >= minNotional:
            try:
                exchange.create_market_sell_order(symbol, adjusted_qty)
                log(f"🧹 Flush direct : {adjusted_qty} {base}")
                time.sleep(1.5)
                attempt_final_resell(base, symbol, stepSize, minQty, minNotional, last_price)
            except Exception as e:
                log(f"❌ Erreur flush {base} : {e}")
            continue

        if adjusted_qty < minQty or adjusted_qty * last_price < minNotional:
            dust_targets.append({
                "symbol": symbol,
                "base": base,
                "qty": qty,
                "step": stepSize,
                "minQty": minQty,
                "minNotional": minNotional,
                "last_price": last_price
            })

    for item in dust_targets:
        symbol = item["symbol"]
        base = item["base"]
        qty = item["qty"]
        step = item["step"]
        minQty = item["minQty"]
        last_price = item["last_price"]
        minNotional = item["minNotional"]

        target_qty = minQty * OVERBUY_FACTOR
        needed = target_qty - qty
        cost = needed * last_price

        if RECYCLE_DUST and cost <= usdc_balance and cost >= minNotional:
            try:
                buy_qty = adjust_to_step(needed, step)
                exchange.create_market_buy_order(symbol, buy_qty)
                log(f"♻️ OVERBUY : {buy_qty} {base} pour atteindre {target_qty}")
                time.sleep(1.5)

                updated = exchange.fetch_balance()
                final_qty = updated.get(base, {}).get("free", 0)
                sell_qty = adjust_to_step(final_qty, step)
                if sell_qty >= minQty and sell_qty * last_price >= minNotional:
                    exchange.create_market_sell_order(symbol, sell_qty)
                    log(f"✅ Résidu OVERBUY & revendu : {sell_qty} {base}")
                    time.sleep(1.5)
                    attempt_final_resell(base, symbol, step, minQty, minNotional, last_price)
                    usdc_balance = updated['free'].get('USDC', usdc_balance)
            except Exception as e:
                log(f"❌ Erreur overbuy/vente {base} : {e}")

while True:
    try:
        run_bot()
        time.sleep(60.0)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60.0)
