print("🔥 BOT PRO REAL ACTIVO 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import calcular_confianza


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


def ejecutar_bot():

    bot = DerivBot()

    if not bot.connect():
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT REAL INICIADO")

    pares = ["R_10", "R_25", "R_50"]

    monto = 10
    ganadas = 0
    perdidas = 0

    while True:
        try:
            for par in pares:

                time.sleep(5)

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)

                enviar_telegram(f"📊 {par} | Score: {score} | IA: {confianza}%")

                if score < 2:
                    continue

                if tipo is not None:

                    enviar_telegram(f"📈 {par} → {tipo.upper()}")

                    resultado = bot.comprar(par, tipo, monto)

                    if resultado == "win":
                        ganadas += 1
                        enviar_telegram(f"✅ GANADA {par}")
                    else:
                        perdidas += 1
                        enviar_telegram(f"❌ PERDIDA {par}")

                    enviar_telegram(f"💰 Balance: {bot.balance}")

            # resumen diario
            hora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).hour

            if hora == 20:
                enviar_telegram(f"""📊 RESUMEN

Ganadas: {ganadas}
Perdidas: {perdidas}
Balance: {bot.balance}
""")

                ganadas = 0
                perdidas = 0
                time.sleep(3600)

        except Exception as e:
            enviar_telegram(f"❌ ERROR: {str(e)}")
            time.sleep(5)


if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
