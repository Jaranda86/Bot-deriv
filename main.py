import time
from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# ==============================
# TELEGRAM
# ==============================
import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje})
    except Exception as e:
        print("Error Telegram:", e)

# ==============================
# BOT PRINCIPAL
# ==============================

def ejecutar_bot():

    bot = DerivBot()

    if not bot.conectar():
        print("❌ Error conexión Deriv")
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🔥 BOT DIOS PRO ACTIVADO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    monto_base = 10
    monto = monto_base

    ganadas = 0
    perdidas = 0
    racha_perdidas = 0

    LIMITE_PERDIDA = 50
    perdidas_dia = 0

    while True:
        try:

            # 🔒 límite diario
            if perdidas_dia >= LIMITE_PERDIDA:
                enviar_telegram("🛑 LIMITE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            # ⚠️ racha negativa
            if racha_perdidas >= 3:
                enviar_telegram("⚠️ Pausa por racha negativa")
                time.sleep(600)
                racha_perdidas = 0
                monto = monto_base
                continue

            for par in pares:

                time.sleep(5)

                print(f"🔎 Analizando {par}")

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(par, score)
                tipo = decision_final(tipo, score, confianza)

                print(f"DEBUG → {par} | score: {score} | confianza: {confianza}")

                if tipo is None:
                    print("⛔ IA bloqueó operación")
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | score {score} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                if profit > 0:
                    ganadas += 1
                    racha_perdidas = 0
                    monto = monto_base

                    enviar_telegram(f"✅ GANADA {par} | +{profit}")

                else:
                    perdidas += 1
                    racha_perdidas += 1
                    perdidas_dia += abs(profit)

                    monto *= 2  # 🔥 martingala

                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")

        except Exception as e:
            print("ERROR BOT:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(10)

# ==============================
# INICIO
# ==============================

if __name__ == "__main__":
    ejecutar_bot()
