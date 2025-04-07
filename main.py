from trader import TraderBot
from cleaner import Cleaner
import time
from utils import log
import os

SCORE_MIN = float(os.getenv("SCORE_MIN", 0.35))

print(f"[DEBUG] Lancement SmartBot++ PRO 1.4 | Seuil score min: {SCORE_MIN}")

trader = TraderBot(score_min=SCORE_MIN)
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
