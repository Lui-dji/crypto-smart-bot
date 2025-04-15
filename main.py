import ccxt
import time
from datetime import datetime, timezone
import os
from trader import TraderBot
from cleaner import Cleaner
from utils import log

log("Lancement bot avec confirmations achat")

exchange = ccxt.binance({
    "apiKey": os.getenv("API_KEY"),
    "secret": os.getenv("SECRET_KEY"),
    "enableRateLimit": True,
    "options": {"defaultType": "spot"}
})

bot = TraderBot(score_min=0.30)
cleaner = Cleaner()

while True:
    cleaner.run()
    bot.run()
    time.sleep(30)