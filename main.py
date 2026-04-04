print("🔥 VERSION PRO DEL BOT 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import guardar_operacion, calcular_confianza

# 🔥 Evita errores de inicio en Render
time.sleep(5)

# =========================
# 🔑 VARIABLES TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("TOKEN TELEGRAM:", TELEGRAM_TOKEN)
print("CHAT ID:", CHAT_ID)

# =========================
# 📩 FUNCION TELEGRAM
# =========================
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
def bot():
    bot = DerivBot()

    # 🔌 CONEXIÓN CONTROLADA
    if not bot.connect():
        print("❌ No conecta a Deriv")
        time.sleep(10)
        return

    enviar_telegram("🤖 BOT PRO ACTIVO 🔥")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    # 💰 GESTIÓN DE DINERO
    monto_base = 10
    monto = monto_base

    # 📊 CONTADORES
    ganadas = 0
    perdidas = 0

    while True:
        try:
            for par in pares:

                print(f"🔎 Analizando {par}...")
                score, tipo = analizar_mercado(bot, par)

                print(f"{par} score: {score}")

                # 🧠 IA
                confianza = calcular_confianza(par, score)

                print(f"Confianza IA: {confianza}%")

                if score >= 3 and confianza >= 55:

                    mensaje = f"📊 {par} → {tipo.upper()} | Score: {score} | IA: {confianza}%"
                    print(mensaje)
                    enviar_telegram(mensaje)

                    print(f"💰 Ejecutando {tipo} en {par} con ${monto}")
                    resultado = bot.comprar(par, tipo, monto)

                    # 📊 RESULTADO
                    if resultado == "win":
                        enviar_telegram(f"✅ GANADA en {par} 💰")
                        ganadas += 1
                        monto = monto_base
                        guardar_operacion(par, score, "win")

                    else:
                        enviar_telegram(f"❌ PERDIDA en {par} 💸")
                        perdidas += 1
                        monto *= 1.5
                        guardar_operacion(par, score, "loss")

                    print("Balance:", bot.balance)

                else:
                    print("❌ Sin señal clara")

                time.sleep(2)

            # ⏰ RESUMEN DIARIO
            hora = datetime.datetime.now().hour

            if hora == 20:
                resumen = f"""📊 RESUMEN DIARIO
✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Balance: {bot.balance}
"""
                enviar_telegram(resumen)

                ganadas = 0
                perdidas = 0

                time.sleep(3600)

        except Exception as e:
            print("❌ Error general:", e)
            time.sleep(5)

# =========================
# 🚀 INICIO
# =========================
if __name__ == "__main__":
    while True:
        bot()
        time.sleep(10)
