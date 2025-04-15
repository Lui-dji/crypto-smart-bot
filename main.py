import os
import time
from trader import SmartGridBot
from cleaner import Cleaner
from utils import log

log("🚀 Lancement SmartBot++ GRID INTELLIGENT")

if os.getenv("BOT_ACTIVE", "true").lower() == "true":
    bot = SmartGridBot()
    cleaner = Cleaner()
    while True:
        bot.run()
        cleaner.run()
        time.sleep(30)