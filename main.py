from trader import TraderBot
from cleaner import Cleaner
import time

print("[DEBUG] Lancement SmartBot++ PRO")

trader = TraderBot()
cleaner = Cleaner()

while True:
    trader.run()
    cleaner.run()
    time.sleep(30)
