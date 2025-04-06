import ccxt
import os
import time
from utils import log, get_trend_score

class TraderBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_SECRET_KEY"),
            'enableRateLimit': True
        })
        self.budget_per_position = float(os.getenv("POSITION_BUDGET", 15))
        self.positions = {}

    def run(self):
        try:
            balance = self.exchange.fetch_balance()
            tickers = self.exchange.fetch_tickers()
            markets = self.exchange.load_markets()
        except Exception as e:
            log(f"❌ TraderBot Erreur API : {e}")
            return

        count = 0

        for symbol, ticker in tickers.items():
            if "/USDC" not in symbol or symbol not in markets:
                continue
            if ticker['last'] is None:
                continue
            if count >= 300:
                break

            count += 1
            base = symbol.replace("/USDC", "")
            price = ticker['last']
            score = get_trend_score(self.exchange, symbol)
            log(f"🔎 {symbol} score={score:.2f}")

            if score < 0.75:
                continue

            usdc = balance['free'].get('USDC', 0)
            if usdc >= self.budget_per_position:
                qty = round(self.budget_per_position / price, 6)
                try:
                    self.exchange.create_market_buy_order(symbol, qty)
                    log(f"🟢 Achat {qty} {base} à {price} USDC (score: {score:.2f})")
                    balance['free']['USDC'] -= qty * price
                    self.positions[base] = price
                except Exception as e:
                    log(f"❌ Erreur achat {base} : {e}")
            elif self.positions:
                worst = min(self.positions.items(), key=lambda x: x[1])
                worst_symbol = f"{worst[0]}/USDC"
                try:
                    qty = balance.get(worst[0], {}).get("free", 0)
                    if qty > 0:
                        self.exchange.create_market_sell_order(worst_symbol, qty)
                        log(f"🔁 Arbitrage : revente {qty} {worst[0]} pour acheter {base}")
                        del self.positions[worst[0]]
                        time.sleep(2)
                except Exception as e:
                    log(f"❌ Erreur arbitrage : {e}")
