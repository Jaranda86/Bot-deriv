import time
import os
from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import guardar_operacion, filtrar_operacion

# ===== TELEGRAM =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

import requests

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

# ===== BOT =====
def bot():
    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión con Deriv")
        return

    print("🤖 BOT DEMO INICIADO")
    enviar_telegram("🤖 BOT DEMO INICIADO")

    pares = ["R_50", "R_75", "R_100"]

    while True:
        for par in pares:

            decision, score = analizar_mercado(bot, par)

            if decision is None:
                print(f"❌ Sin señal clara en {par}")
                continue

            # FILTRO IA
            if not filtrar_operacion(score):
                print(f"🧠 IA evitó operación en {par}")
                continue

            print(f"📊 {par} → {decision.upper()} | Score: {score}")
            enviar_telegram(f"📊 {par} → {decision.upper()} | Score: {score}")

            resultado = bot.operar(par, decision)

            if resultado:
                print(f"✅ GANADA en {par}")
                enviar_telegram(f"✅ GANADA en {par}")
                guardar_operacion(par, decision, 1, score)
            else:
                print(f"❌ PERDIDA en {par}")
                enviar_telegram(f"❌ PERDIDA en {par}")
                guardar_operacion(par, decision, 0, score)

            time.sleep(5)

        time.sleep(10)

if __name__ == "__main__":
    bot()
