print("🔥 VERSION PRO FINAL BOT 🔥")

import time
import os
import datetime
import requests

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import decision_final, registrar_resultado

# ==============================
# 📲 TELEGRAM
# ==============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error Telegram:", e)


# ==============================
# 🤖 BOT PRINCIPAL
# ==============================
def ejecutar_bot():

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión Deriv")
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT PRO FINAL ACTIVO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0
    ultimo_resumen = None

    while True:
        try:
            for par in pares:

                # 🛑 evitar spam (CLAVE)
                time.sleep(5)

                print(f"🔎 Analizando {par}...")

                score, tipo = analizar_mercado(par)

                operar, confianza, estado = decision_final(score, tipo)

                print(f"IA → {estado} | score: {score} | confianza: {confianza}%")

                # 🚫 si no cumple condiciones
                if not operar:
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | Score: {score} | IA: {confianza}%")

                print(f"💰 Ejecutando {tipo} en {par} con ${monto}")

                resultado = bot.comprar(par, tipo, monto)

                # ==============================
                # ✅ GANADA
                # ==============================
                if resultado == "win":
                    enviar_telegram(f"✅ GANADA en {par}")
                    registrar_resultado("win")

                    ganadas += 1
                    monto = monto_base

                # ==============================
                # ❌ PERDIDA
                # ==============================
                else:
                    enviar_telegram(f"❌ PERDIDA en {par}")
                    registrar_resultado("loss")

                    perdidas += 1

                # 💰 BALANCE
                enviar_telegram(f"💰 Balance actual: {bot.balance}")

            # ==============================
            # 📊 RESUMEN DIARIO 20:00
            # ==============================
            hora_actual = datetime.datetime.now().hour

            if hora_actual == 20 and ultimo_resumen != 20:
                enviar_telegram(f"""
📊 RESUMEN DEL DÍA

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Balance: {bot.balance}
""")
                ganadas = 0
                perdidas = 0
                ultimo_resumen = 20

            # reset para próximo día
            if hora_actual != 20:
                ultimo_resumen = None

        except Exception as e:
            error_msg = f"❌ ERROR BOT: {str(e)}"
            print(error_msg)
            enviar_telegram(error_msg)
            time.sleep(5)


# ==============================
# 🔁 LOOP GLOBAL
# ==============================
if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
