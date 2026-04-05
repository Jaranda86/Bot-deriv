 import time
import datetime
import os

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final, debug_ia

# =========================
# 🔔 TELEGRAM
# =========================

import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("❌ Error enviando a Telegram")

# =========================
# 🤖 BOT PRINCIPAL
# =========================

def ejecutar_bot():
    bot = DerivBot()

    if not bot.connect():
        print("❌ No conecta a Deriv")
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🚀 BOT DIOS ACTIVADO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0
    profit_dia = 0

    LIMITE_DIARIO = -50

    while True:
        try:
            for par in pares:

                time.sleep(5)  # 🔥 evita bloqueos API

                print(f"\n🔍 ANALIZANDO {par}")

                # =========================
                # 📈 VELAS REALES
                # =========================
                velas = bot.get_candles(par)
                print("VELAS:", velas)

                if not velas:
                    print("❌ NO HAY VELAS")
                    continue

                # =========================
                # 🧠 IA ANALISIS
                # =========================
                score, tipo = analizar_mercado(par, bot)
                print("DEBUG SCORE:", score, tipo)

                confianza = calcular_confianza(par, score)
                debug_ia(par, score, confianza)

                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("⛔ IA bloqueó operación")
                    continue

                # =========================
                # 💰 CONTROL RIESGO
                # =========================
                if profit_dia <= LIMITE_DIARIO:
                    enviar_telegram("🛑 Límite de pérdida alcanzado")
                    print("STOP DIARIO")
                    time.sleep(3600)
                    continue

                # =========================
                # 🚀 OPERAR
                # =========================
                enviar_telegram(f"📊 {par} → {tipo.upper()}")

                print(f"💰 Ejecutando {tipo} en {par}")

                resultado = bot.comprar(par, tipo, monto)

                time.sleep(65)  # esperar resultado real

                # =========================
                # 📊 RESULTADO
                # =========================
                balance = bot.get_balance()

                if resultado == "ok":
                    ganadas += 1
                    profit_dia += monto * 0.95

                    enviar_telegram(f"✅ GANADA en {par}")
                    monto = monto_base

                else:
                    perdidas += 1
                    profit_dia -= monto

                    enviar_telegram(f"❌ PERDIDA en {par}")

                    # 🔥 MARTINGALA SIMPLE
                    monto *= 2

                enviar_telegram(f"💰 Balance: {balance}")

                print(f"Balance actual: {balance}")

                # =========================
                # 📅 RESUMEN DIARIO 20HS
                # =========================
                hora = datetime.datetime.now().hour

                if hora == 20:
                    enviar_telegram(f"""
📊 RESUMEN DIARIO

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Profit: {profit_dia}
""")
                    ganadas = 0
                    perdidas = 0
                    profit_dia = 0

        except Exception as e:
            error = f"❌ ERROR BOT: {str(e)}"
            print(error)
            enviar_telegram(error)
            time.sleep(10)

# =========================
# 🔁 LOOP GLOBAL
# =========================

if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)                   
