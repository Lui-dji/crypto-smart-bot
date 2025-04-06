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
            usdc = balance['free'].get('USDC', 0)
            tickers = self.exchange.fetch_tickers()
            markets = self.exchange.load_markets()
        except Exception as e:
            log(f"❌ TraderBot Erreur API : {e}")
            return

        for symbol, ticker in tickers.items():
            if "/USDC" not in symbol or symbol not in markets:
                continue

            if ticker['last'] is None:
                continue

            base = symbol.replace("/USDC", "")
            price = ticker['last']
            score = get_trend_score(self.exchange, symbol)
            if score < 0.75:
                continue

            # Nouvelle opportunité détectée
            if usdc >= self.budget_per_position:
                qty = round(self.budget_per_position / price, 6)
                try:
                    self.exchange.create_market_buy_order(symbol, qty)
                    log(f"🟢 Achat {qty} {base} à {price} USDC (score: {score:.2f})")
                    usdc -= qty * price
                    self.positions[base] = price
                except Exception as e:
                    log(f"❌ Erreur achat {base} : {e}")
            elif self.positions:
                # Arbitrage : vendre le moins prometteur
                worst = min(self.positions.items(), key=lambda x: x[1])
                worst_symbol = f"{worst[0]}/USDC"
                try:
                    balance = self.exchange.fetch_balance()
                    qty = balance.get(worst[0], {}).get("free", 0)
                    if qty > 0:
                        self.exchange.create_market_sell_order(worst_symbol, qty)
                        log(f"🔁 Arbitrage : revente {qty} {worst[0]} pour acheter {base}")
                        del self.positions[worst[0]]
                        time.sleep(2)
                except Exception as e:
                    log(f"❌ Erreur arbitrage : {e}")
