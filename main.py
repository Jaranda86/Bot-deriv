import time
import datetime
import os
import requests

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final, debug_ia


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Error Telegram")


def ejecutar_bot():
    bot = DerivBot()

    if not bot.connect():
        print("No conecta a Deriv")
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🚀 BOT DIOS ACTIVADO")

    pares = ["R_10", "R_25", "R_50"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0

    while True:
        try:
            for par in pares:

                time.sleep(5)

                print(f"Analizando {par}")

                velas = bot.get_candles(par)
                print("VELAS:", velas)

                if not velas:
                    print("NO HAY VELAS")
                    continue

                score, tipo = analizar_mercado(par, bot)
                print("SCORE:", score, tipo)

                confianza = calcular_confianza(par, score)
                debug_ia(par, score, confianza)

                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("IA bloqueó")
                    continue

                enviar_telegram(f"{par} → {tipo}")

                resultado = bot.comprar(par, tipo, monto)

                time.sleep(65)

                if resultado == "ok":
                    ganadas += 1
                    enviar_telegram("GANADA")
                    monto = monto_base
                else:
                    perdidas += 1
                    enviar_telegram("PERDIDA")
                    monto *= 2

        except Exception as e:
            print("ERROR:", e)
            enviar_telegram(f"ERROR: {e}")
            time.sleep(10)


if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
