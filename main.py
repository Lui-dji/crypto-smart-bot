import os
import ccxt
import time
from datetime import datetime

print(f"[{datetime.utcnow()}] Lancement bot avec confirmations achat")

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

if not api_key or not secret_key:
    print("❌ API_KEY ou SECRET_KEY manquant(e)")
    exit()

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

symbol = "GMX/USDC"
amount = 1  # exemple simple

try:
    orderbook = exchange.fetch_order_book(symbol)
    price = orderbook['asks'][0][0]
    print(f"💰 Achat de {amount} {symbol.split('/')[0]} à {price}")

    order = exchange.create_market_buy_order(symbol, amount)
    print(f"✅ Achat confirmé : {order}")
except Exception as e:
    print(f"❌ Erreur achat {symbol} : {e}")