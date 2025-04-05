import os
print("[DEBUG] Lancement du fichier main.py...")

if os.getenv("BOT_ACTIVE", "true").lower() != "true":
    print("🛑 BOT désactivé via variable d'environnement")
    exit()

os.environ["PORT"] = "10000"

import time
import ccxt
from datetime import datetime, timedelta

print("[DEBUG] Importations réussies.")

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

print(f"[DEBUG] API_KEY = {'OK' if API_KEY else 'MISSING'}")
print(f"[DEBUG] SECRET_KEY = {'OK' if SECRET_KEY else 'MISSING'}")

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True
})

QUOTE = 'USDC'
BUDGET_USDT = 10
TAKE_PROFIT = 0.10
STOP_LOSS = 0.05
COOLDOWN_MINUTES = 10

last_trade_time = {}

def log(msg):
    print(f"[{datetime.utcnow()}] {msg}")

def run_bot():
    log("📊 Analyse du marché (USDC)...")
    try:
        tickers = exchange.fetch_tickers()
        markets = exchange.load_markets()
        balance = exchange.fetch_balance()
        usdt_balance = balance['free'].get(QUOTE, 0)
    except Exception as e:
        log(f"❌ Erreur connexion API Binance : {e}")
        return

    for symbol, ticker in tickers.items():
        if f"/{QUOTE}" in symbol and ticker.get('percentage') is not None and symbol in markets:
            market = markets[symbol]
            min_notional = float(market.get("limits", {}).get("cost", {}).get("min", 0))
            if min_notional and BUDGET_USDT < min_notional:
                continue  # Skip si montant trop bas pour cette paire

            if not market['active']:
                continue  # Skip marché fermé

            change = ticker['percentage']
            last_price = ticker['last']
            base = symbol.split("/")[0]

            if change > 5.0 and usdt_balance >= BUDGET_USDT:
                now = datetime.utcnow()
                last_time = last_trade_time.get(base, now - timedelta(minutes=COOLDOWN_MINUTES + 1))
                if (now - last_time).total_seconds() / 60 > COOLDOWN_MINUTES:
                    amount = round(BUDGET_USDT / last_price, 6)
                    log(f"💰 Achat auto de {amount} {base} à {last_price} {QUOTE} ({change}%)")
                    try:
                        order = exchange.create_market_buy_order(symbol, amount)
                        last_trade_time[base] = now
                    except Exception as e:
                        log(f"❌ Erreur achat : {e}")

            positions = balance.get(base)
            if positions and positions['total'] > 0:
                try:
                    buy_price = last_price / (1 + change / 100)
                    profit = (last_price - buy_price) / buy_price
                    if profit >= TAKE_PROFIT or profit <= -STOP_LOSS:
                        log(f"⚠️ Vente auto de {positions['free']} {base} à {last_price} (Profit: {round(profit*100, 2)}%)")
                        exchange.create_market_sell_order(symbol, positions['free'])
                except Exception as e:
                    log(f"❌ Erreur vente : {e}")
    time.sleep(60)

while True:
    try:
        run_bot()
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(60)
