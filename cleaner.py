import ccxt
import os
from utils import log

class Cleaner:
    def __init__(self):
        self.exchange = ccxt.binance({
            "apiKey": os.getenv("API_KEY"),
            "secret": os.getenv("SECRET_KEY"),
            "enableRateLimit": True
        })

    def run(self):
        balance = self.exchange.fetch_balance()
        tickers = self.exchange.fetch_tickers()
        markets = self.exchange.load_markets()
        usdc = balance['free'].get('USDC', 0)

        for asset, amount in balance['free'].items():
            if asset in ["USDC"] or amount == 0:
                continue

            symbol = f"{asset}/USDC"
            if symbol not in tickers or symbol not in markets:
                continue

            price = tickers[symbol]["last"]
            try:
                market = markets[symbol]
                step = float(market["info"]["filters"][2]["stepSize"])
                min_qty = float(market["info"]["filters"][1]["minQty"])
                min_notional = float(market["info"]["filters"][3]["minNotional"])
                sell_qty = amount - (amount % step)

                if sell_qty * price >= min_notional:
                    self.exchange.create_market_sell_order(symbol, sell_qty)
                    log(f"🧹 Vente propre : {sell_qty} {asset}")
            except Exception as e:
                log(f"❌ Erreur cleaner {symbol} : {e}")