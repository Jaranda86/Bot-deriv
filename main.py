print("🔥 BOT PRO FINAL 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import guardar_operacion, calcular_confianza

# 🔥 evita problemas de inicio
time.sleep(5)

# =========================
# 🔑 TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("Error Telegram:", e)

# =========================
# 🤖 BOT PRINCIPAL
# =========================
def ejecutar_bot():

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión Deriv")
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT PRO FINAL ACTIVO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 1
    monto = monto_base

    ganadas = 0
    perdidas = 0
    racha_perdidas = 0

    while True:
        try:
            for par in pares:

                print(f"🔎 Analizando {par}")
                score, tipo = analizar_mercado(bot, par)

                confianza = calcular_confianza(par, score)

                print(f"Score: {score} | IA: {confianza}%")

                # 🛑 evitar mercado basura
                if score < 2:
                    continue

                # 🎯 filtro fuerte
                if score >= 4 and confianza >= 60:

                    enviar_telegram(f"📊 {par} → {tipo.upper()} | Score: {score} | IA: {confianza}%")

                    print(f"💰 Ejecutando {tipo} con ${monto}")
                    resultado = bot.comprar(par, tipo, monto)

                    if resultado == "win":
                        enviar_telegram(f"✅ GANADA en {par}")
                        ganadas += 1
                        monto = monto_base
                        racha_perdidas = 0
                        guardar_operacion(par, score, "win")

                    else:
                        enviar_telegram(f"❌ PERDIDA en {par}")
                        perdidas += 1
                        monto *= 1.5
                        racha_perdidas += 1
                        guardar_operacion(par, score, "loss")

                        # 💣 límite de riesgo
                        if monto > 10:
                            monto = monto_base

                    print("Balance:", bot.balance)

                    # 🛑 pausa por pérdidas
                    if racha_perdidas >= 3:
                        enviar_telegram("⛔ Pausa 10 min por pérdidas")
                        print("⛔ Pausa activada")
                        time.sleep(600)
                        racha_perdidas = 0

                else:
                    print("❌ Sin señal fuerte")

                time.sleep(2)

            # ⏰ resumen diario
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
            print("❌ Error general:", e)
            time.sleep(5)

# =========================
# 🔄 LOOP GLOBAL
# =========================
if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
