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
            market = markets[symbol]
            filters = market.get("info", {}).get("filters", [])
            step = float(next((f["stepSize"] for f in filters if f["filterType"] == "LOT_SIZE"), 0.000001))
            minQty = float(next((f["minQty"] for f in filters if f["filterType"] == "LOT_SIZE"), 0.000001))
            minNotional = float(next((f.get("minNotional", 1) for f in filters if f["filterType"] == "NOTIONAL"), 1))

            sell_qty = qty - (qty % step)
            if sell_qty >= minQty and sell_qty * price >= minNotional:
                try:
                    self.exchange.create_market_sell_order(symbol, sell_qty)
                    log(f"🧹 Revente résidu : {sell_qty} {base}")
                except Exception as e:
                    log(f"❌ Cleaner erreur {base} : {e}")
