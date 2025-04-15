import ccxt
import os
import time
from utils import log, get_ohlcv_trend

class SmartGridBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("API_KEY"),
            'secret': os.getenv("SECRET_KEY"),
            'enableRateLimit': True
        })
        self.budget_per_position = float(os.getenv("POSITION_BUDGET", 15))

    def run(self):
        try:
            tickers = self.exchange.fetch_tickers()
            markets = self.exchange.load_markets()
            balance = self.exchange.fetch_balance()
        except Exception as e:
            log(f"❌ Erreur API : {e}")
            return

        usdc = balance['free'].get("USDC", 0)
        for symbol in tickers:
            if "/USDC" not in symbol:
                continue
            try:
                candles = self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=10)
                score = get_ohlcv_trend(candles)
                log(f"🔎 {symbol} score={score:.2f}")
                if score >= 0.5 and usdc > self.budget_per_position:
                    price = tickers[symbol]['last']
                    qty = round(self.budget_per_position / price, 6)
                    base = symbol.split("/")[0]
                    self.exchange.create_market_buy_order(symbol, qty)
                    log(f"🟢 Achat {qty} {base} à {price} USDC (score: {score:.2f})")
                    usdc -= qty * price
            except Exception as e:
                log(f"❌ Erreur {symbol} : {e}")
