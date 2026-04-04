print("🔥 BOT PRO FINAL ACTIVO 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import guardar_operacion, calcular_confianza

# ============================
# 🔑 TELEGRAM
# ============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("⚠️ Error enviando a Telegram")


# ============================
# 🤖 BOT PRINCIPAL
# ============================

def ejecutar_bot():

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión Deriv")
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT PRO INICIADO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0
    racha_perdidas = 0

    while True:
        try:
            for par in pares:

                print(f"🔎 Analizando {par}...")

                score, tipo = analizar_mercado(bot, par)
                confianza = calcular_confianza(score)

                print(f"Score: {score} | IA: {confianza}%")

                # ❌ evitar mercado basura
                if score < 2:
                    continue

                # DEBUG
                print(f"DEBUG → {par} | score: {score} | tipo: {tipo} | IA: {confianza}")

                # 🎯 entrada
                if tipo is not None and score >= 3 and confianza >= 55:

                    enviar_telegram(f"📊 {par} → {tipo.upper()} | Score: {score}")

                    print(f"💰 Ejecutando {tipo} en {par}")

                    resultado = bot.comprar(par, tipo, monto)

                    if resultado == "win":
                        enviar_telegram(f"✅ GANADA en {par}")
                        ganadas += 1
                        monto = monto_base
                        racha_perdidas = 0

                        guardar_operacion(par, score, 1)

                    else:
                        enviar_telegram(f"❌ PERDIDA en {par}")
                        perdidas += 1
                        racha_perdidas += 1

                        guardar_operacion(par, score, 0)

                        # martingale leve
                        monto = min(monto * 2, 50)

                # descanso por par
                time.sleep(1)

            # 🔥 descanso general (ANTI RATE LIMIT)
            time.sleep(5)

            # ============================
            # 🕒 RESUMEN DIARIO
            # ============================

            hora = datetime.datetime.now().hour

            if hora == 20:
                enviar_telegram(f"""📊 RESUMEN DEL DÍA

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Balance: {bot.balance}
""")

                ganadas = 0
                perdidas = 0

                time.sleep(3600)

        except Exception as e:
            error_msg = f"❌ ERROR BOT: {str(e)}"
            print(error_msg)
            enviar_telegram(error_msg)
            time.sleep(5)


# ============================
# 🔁 LOOP GLOBAL
# ============================

if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
