import time
from trader import SmartGridBot

bot = SmartGridBot()
while True:
    bot.run()
    time.sleep(30)
