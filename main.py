import time
import requests
import os

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final, guardar_resultado

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

MONTO_BASE = 10
monto = MONTO_BASE

perdidas = 0
racha = 0
LIMITE = -50


def ejecutar_bot():
    global monto, perdidas, racha

    bot = DerivBot()

    if not bot.conectar():
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🔥 BOT ULTRA PRO ACTIVADO")

    while True:
        try:

            if perdidas <= LIMITE:
                enviar_telegram("🛑 LIMITE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            if racha >= 3:
                enviar_telegram("⚠️ PAUSA POR RACHA")
                time.sleep(600)
                racha = 0
                continue

            for par in pares:

                time.sleep(5)

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    continue

                enviar_telegram(f"{par} → {tipo} | score {score} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                guardar_resultado(par, tipo, profit)

                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} +{profit}")
                    monto = MONTO_BASE
                    racha = 0
                else:
                    enviar_telegram(f"❌ PERDIDA {par} {profit}")
                    perdidas += profit
                    racha += 1

                    # martingala controlada
                    monto = min(monto * 2, 50)

        except Exception as e:
            enviar_telegram(f"❌ ERROR {e}")
            time.sleep(10)


if __name__ == "__main__":
    ejecutar_bot()
