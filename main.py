
import ccxt
import time
from datetime import datetime, timezone
import os
from cleaner import Cleaner
from trader import TraderBot
from utils import log

log("Lancement bot complet")

if os.getenv("BOT_ACTIVE", "true").lower() != "true":
    log("⏸️ Bot inactif (BOT_ACTIVE est false)")
else:
    cleaner = Cleaner()
    cleaner.run()
    bot = TraderBot(
        score_min=float(os.getenv("SCORE_MIN", 0.35))
    )
    while True:
        bot.run()
        log("✅ Fin du cycle. Pause de 30s.")
        time.sleep(30)
