print("🔥 BOT PRO REAL + IA ACTIVA 🔥")

import time
import os
import requests
import datetime

from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import calcular_confianza, guardar_operacion


# =========================
# 📲 TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error Telegram:", e)


# =========================
# 🤖 BOT PRINCIPAL
# =========================
def ejecutar_bot():

    bot = DerivBot()

    if not bot.connect():
        print("❌ No conecta a Deriv")
        time.sleep(10)
        return

    enviar_telegram("🚀 BOT REAL + IA APRENDIZAJE INICIADO")

    pares = ["R_10", "R_25", "R_50"]

    monto = 10
    ganadas = 0
    perdidas = 0

    while True:
        try:
            for par in pares:

                # 🛑 evitar bloqueo API
                time.sleep(5)

                print(f"🔎 Analizando {par}")

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)

                print(f"Score: {score} | IA: {confianza}%")

                # 📲 SIEMPRE reporta análisis
                enviar_telegram(f"📊 {par} | Score: {score} | IA: {confianza}%")

                # ❌ mercado malo
                if score < 2:
                    enviar_telegram(f"⛔ {par} sin señal (score bajo)")
                    continue

                # 🤖 IA bloquea malas decisiones
                if confianza < 55:
                    enviar_telegram(f"🤖 IA bloquea {par} | confianza: {confianza}%")
                    continue

                # 🎯 EJECUTA OPERACIÓN
                if tipo is not None:

                    enviar_telegram(f"📈 {par} → {tipo.upper()}")

                    print(f"💰 Ejecutando {tipo} en {par}")

                    resultado = bot.comprar(par, tipo, monto)

                    # =========================
                    # RESULTADO
                    # =========================
                    if resultado == "win":
                        ganadas += 1
                        guardar_operacion(par, score, "win")
                        enviar_telegram(f"✅ GANADA en {par}")

                    else:
                        perdidas += 1
                        guardar_operacion(par, score, "loss")
                        enviar_telegram(f"❌ PERDIDA en {par}")

                    # actualizar balance real
                    balance = bot.get_balance()

                    enviar_telegram(f"💰 Balance actual: {balance}")

            # =========================
            # 🕐 RESUMEN DIARIO
            # =========================
            hora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).hour

            if hora == 20:
                enviar_telegram(f"""📊 RESUMEN DIARIO

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Balance: {bot.balance}
""")

                ganadas = 0
                perdidas = 0

                # evita spam durante esa hora
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
