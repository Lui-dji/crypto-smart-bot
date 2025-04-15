import ccxt
import os
import time
from utils import log, get_ohlcv_trend

class SmartGridBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            "apiKey": os.getenv("API_KEY"),
            "secret": os.getenv("SECRET_KEY"),
            "enableRateLimit": True
        })
        self.budget = float(os.getenv("POSITION_BUDGET", 15))
        self.score_min = float(os.getenv("SCORE_MIN", 0.35))
        self.positions = {}

    def run(self):
        balance = self.exchange.fetch_balance()
        usdc = balance["free"].get("USDC", 0)
        tickers = self.exchange.fetch_tickers()
        markets = self.exchange.load_markets()

        count = 0
        for symbol in tickers:
            if "/USDC" not in symbol or symbol not in markets:
                continue
            count += 1
            if count > 100:
                break

            score = get_ohlcv_trend(self.exchange, symbol)
            log(f"🔎 {symbol} score={score:.2f}")
            if score < self.score_min:
                continue

            price = tickers[symbol]['last']
            if usdc >= self.budget:
                qty = round(self.budget / price, 6)
                try:
                    self.exchange.create_market_buy_order(symbol, qty)
                    log(f"💰 Achat intelligent : {qty} {symbol} à {price}")
                except Exception as e:
                    log(f"❌ Erreur achat {symbol} : {e}")