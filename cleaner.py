
import ccxt
import os
import time
from utils import log

class Cleaner:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("API_KEY"),
            'secret': os.getenv("SECRET_KEY"),
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

        usdc = balance['free'].get('USDC', 0)

        for base, qty in balance['free'].items():
            if base in ["USDC"] or qty == 0:
                continue

            symbol = f"{base}/USDC"
            if symbol not in tickers or symbol not in markets:
                continue

            price = tickers[symbol].get("last")
            if not price:
                continue

            market = markets[symbol]
            filters = {f["filterType"]: f for f in market.get("info", {}).get("filters", [])}
            step = float(filters.get("LOT_SIZE", {}).get("stepSize", 0.000001))
            minQty = float(filters.get("LOT_SIZE", {}).get("minQty", 0.000001))
            minNotional = float(filters.get("NOTIONAL", {}).get("minNotional", 1))

            sell_qty = qty - (qty % step)
            sell_qty = round(sell_qty, 6)

            if sell_qty >= minQty and sell_qty * price >= minNotional:
                try:
                    self.exchange.create_market_sell_order(symbol, sell_qty)
                    log(f"🧹 Revente directe : {sell_qty} {base}")
                except Exception as e:
                    log(f"❌ Erreur vente {base} : {e}")
