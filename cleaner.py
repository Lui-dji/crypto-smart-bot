import ccxt
import os
import time
from utils import log

class Cleaner:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_SECRET_KEY"),
            'enableRateLimit': True
        })

    def run(self):
        try:
            balance = self.exchange.fetch_balance()
            tickers = self.exchange.fetch_tickers()
            markets = self.exchange.load_markets()
        except Exception as e:
            log(f"❌ Cleaner Erreur API : {e}")
            return

        for symbol, ticker in tickers.items():
            if "/USDC" not in symbol or symbol not in markets:
                continue
            base = symbol.replace("/USDC", "")
            price = ticker.get("last")
            if not price:
                continue
            qty = balance.get(base, {}).get("free", 0)
            min_sell = 1 / price  # min 1 USDC
            if qty * price >= 1:
                try:
                    self.exchange.create_market_sell_order(symbol, qty)
                    log(f"🧹 Revente résidu : {qty} {base}")
                except Exception as e:
                    log(f"❌ Cleaner erreur {base} : {e}")
