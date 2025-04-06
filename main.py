from trader import TraderBot
from cleaner import Cleaner
import time
from utils import log

print("[DEBUG] Lancement SmartBot++ PRO 1.1")

trader = TraderBot()
cleaner = Cleaner()

while True:
    try:
        log("🌀 Démarrage d’un nouveau cycle d’analyse...")
        trader.run()
        cleaner.run()
        log("✅ Fin du cycle. Pause de 30s.")
        time.sleep(30)
    except Exception as e:
        log(f"🚨 Erreur globale : {e}")
        time.sleep(30)
