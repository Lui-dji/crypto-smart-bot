import ccxt
import time
from datetime import datetime, timezone
import os

def log(msg):
    print(f"[{datetime.now(timezone.utc)}] {msg}")

log("Lancement bot avec confirmations achat")

exchange = ccxt.binance({
    "apiKey": os.getenv("API_KEY"),
    "secret": os.getenv("SECRET_KEY"),
    "enableRateLimit": True,
    "options": {"defaultType": "spot"}
})

symbol = "GMX/USDC"
amount = 1

try:
    order = exchange.create_market_buy_order(symbol, amount)
    log(f"✅ Achat confirmé : {order}")
except Exception as e:
    log(f"❌ Erreur achat {symbol} : {e}")

while True:
    log("📊 Analyse du marché...")
    time.sleep(30)