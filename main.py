import time
import requests
from datetime import datetime
from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final, guardar_resultado

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "8329264709:AAHyKe68ERfMr37EM8qn33KzMJuCuV6KeIM"
CHAT_ID = "6826449033"

pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

monto_base = 10
monto = monto_base

perdidas_dia = 0
LIMITE_PERDIDA = -50

racha_perdidas = 0

# =========================
# TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Error Telegram")


# =========================
# BOT
# =========================
def ejecutar_bot():
    global monto, perdidas_dia, racha_perdidas

    bot = DerivBot()

    if not bot.conectar():
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🔥 MODO DIOS PRO ACTIVADO")

    while True:
           try:

            if perdidas_dia <= LIMITE_PERDIDA:
                enviar_telegram("🛑 LIMITE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            if racha_perdidas >= 3:
                enviar_telegram("⚠️ pausa por racha negativa")
                time.sleep(600)
                racha_perdidas = 0
                continue

            for par in pares:

                time.sleep(5)

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"{par} score {score} | IA {confianza}")

                if tipo is None:
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | score {score} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                # =========================
                # RESULTADO
                # =========================
                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")

                    guardar_resultado(par, score, "win")

                    monto = monto_base
                    racha_perdidas = 0

                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")

                    guardar_resultado(par, score, "loss")

                    perdidas_dia += profit
                    racha_perdidas += 1

                    # MARTINGALA
                    monto *= 2

        except Exception as e:
            print("ERROR:", e)
            enviar_telegram(f"❌ ERROR: {e}")
            time.sleep(5)


# =========================
# START
# =========================
if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
