
import os
import time
import ccxt
from datetime import datetime, timezone

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_API_SECRET")
exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret_key,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
})

def log(msg):
    print(f"[{datetime.now(timezone.utc)}] {msg}")

def buy_symbol(symbol, amount):
    try:
        order = exchange.create_market_buy_order(symbol, amount)
        log(f"✅ Achat confirmé {amount} {symbol}")
        return order
    except Exception as e:
        log(f"❌ Erreur achat {symbol} : {e}")
        return None

def main():
    log("Lancement bot avec confirmations achat")
    # Exemple d'achat test, à adapter
    symbol = "GMX/USDC"
    amount = 1  # à ajuster selon le marché réel
    buy_symbol(symbol, amount)

if __name__ == "__main__":
    main()
