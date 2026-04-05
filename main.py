print("🔥 BOT MODO DIOS FINAL 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import (
    inicializar_csv,
    guardar_operacion,
    calcular_confianza,
    decision_final,
    debug_ia
)

# =========================
# 📲 TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Error Telegram")

# =========================
# 🤖 BOT PRINCIPAL
# =========================
def ejecutar_bot():

    inicializar_csv()

    bot = DerivBot()

    if not bot.connect():
        enviar_telegram("❌ No conecta a Deriv")
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT DIOS ACTIVADO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0
    racha_perdidas = 0

    STOP_DIARIO = -50  # 🔒 límite pérdida diaria
    profit_dia = 0

    while True:
        try:
            for par in pares:

                time.sleep(5)  # 🔥 evita bloqueos

                print(f"🔎 Analizando {par}")

                # 📊 mercado
                score, tipo = analizar_mercado(par, bot)

                confianza = calcular_confianza(par, score)
                debug_ia(par, score, confianza)

                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("⛔ IA bloqueó operación")
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | Score: {score} | IA: {confianza}%")

                print(f"💰 Ejecutando {tipo} en {par} con ${monto}")

                resultado = bot.comprar(par, tipo, monto)

                if resultado == "win":
                    ganadas += 1
                    profit_dia += monto
                    racha_perdidas = 0

                    enviar_telegram(f"✅ GANADA en {par} +{monto}")

                    monto = monto_base

                elif resultado == "loss":
                    perdidas += 1
                    profit_dia -= monto
                    racha_perdidas += 1

                    enviar_telegram(f"❌ PERDIDA en {par} -{monto}")

                    # 🔥 martingale controlado
                    if racha_perdidas <= 2:
                        monto *= 2
                    else:
                        monto = monto_base
                        racha_perdidas = 0

                guardar_operacion(par, score, resultado)

                balance = bot.get_balance()
                enviar_telegram(f"💰 Balance: {balance}")

                # 🔒 STOP DIARIO
                if profit_dia <= STOP_DIARIO:
                    enviar_telegram("🛑 STOP DIARIO ACTIVADO")
                    return

                # 📊 RESUMEN 20:00
                hora = datetime.datetime.now().hour

                if hora == 20:
                    enviar_telegram(f"""📊 RESUMEN DIARIO

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Profit: {profit_dia}
💼 Balance: {balance}
""")

                    ganadas = 0
                    perdidas = 0
                    profit_dia = 0

                    time.sleep(3600)

        except Exception as e:
            error_msg = f"❌ ERROR BOT: {str(e)}"
            print(error_msg)
            enviar_telegram(error_msg)
            time.sleep(5)

# =========================
# 🔁 LOOP GLOBAL
# =========================
if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
