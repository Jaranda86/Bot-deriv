import time
import os
import requests
from deriv_api import DerivBot
from indicadores import analizar_mercado

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("TOKEN TELEGRAM:", TELEGRAM_TOKEN)
print("CHAT ID:", CHAT_ID)

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })

        print("📨 Telegram response:", r.text)

    except Exception as e:
        print("❌ Error Telegram:", e)

def bot():
    bot = DerivBot()

    if not bot.connect():
        print("❌ No conecta a Deriv")
        return

    enviar_telegram("🤖 BOT DEMO INICIADO")

    pares = ["R_10", "R_25", "R_50"]

    while True:
        for par in pares:
            print(f"🔎 Analizando {par}...")

            decision, score = analizar_mercado(bot, par)

            if decision is None:
                print("❌ Sin señal clara")
                continue

            tipo = "CALL" if decision == "CALL" else "PUT"

            enviar_telegram(f"📊 {par} → {tipo} | Score: {score}")

            print(f"🚀 Ejecutando {tipo} en {par}")

            resultado = bot.comprar(par, tipo)

            if resultado is None:
                print("❌ Error operación")
                continue

            if resultado > 0:
                print("✅ GANADA")
                enviar_telegram(f"✅ GANADA en {par} | +{resultado}")
            else:
                print("❌ PERDIDA")
                enviar_telegram(f"❌ PERDIDA en {par} | {resultado}")

            balance = bot.get_balance()
            print("💰 Balance:", balance)
            enviar_telegram(f"💰 Balance actual: {balance}")

            time.sleep(5)

if __name__ == "__main__":
    bot()
