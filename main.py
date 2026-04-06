import time
import os
import requests

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# =========================
# TELEGRAM
# =========================

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error Telegram:", e)


# =========================
# CONFIGURACIÓN
# =========================

pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

MONTO = 1
martingala = 1
racha_perdidas = 0
perdidas_dia = 0
LIMITE_PERDIDA = -50


# =========================
# BOT PRINCIPAL
# =========================

def ejecutar_bot():

    global martingala, racha_perdidas, perdidas_dia

    bot = DerivBot()

    enviar_telegram("🔥 BOT DIOS PRO ACTIVO")

    time.sleep(3)  # evitar rate limit inicial

    while True:
        try:

            # 🔴 límite de pérdidas
            if perdidas_dia <= LIMITE_PERDIDA:
                enviar_telegram("🛑 LIMITE DE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            # 🔴 pausa por racha negativa
            if racha_perdidas >= 3:
                enviar_telegram("⚠️ Pausa por racha negativa")
                time.sleep(600)
                racha_perdidas = 0
                continue

            for par in pares:

                time.sleep(2)  # 🔥 evita rate limit

                # 🔌 conectar (UNA vez por operación)
                if not bot.conectar():
                    continue

                velas = bot.get_candles(par)

                print(f"VELAS {par}: {len(velas)}")

                if len(velas) < 20:
                    print("❌ Sin velas")
                    bot.cerrar()
                    continue

                # 🧠 IA
                score, tipo = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"{par} score {score} | IA {confianza}%")

                if tipo is None:
                    bot.cerrar()
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | IA {confianza}%")

                # 💰 operar
                monto_final = MONTO * martingala
                contract_id = bot.comprar(par, tipo, monto_final)

                if not contract_id:
                    bot.cerrar()
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                bot.cerrar()  # 🔥 cerrar conexión SIEMPRE

                # 📊 resultado
                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")
                    martingala = 1
                    racha_perdidas = 0
                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")
                    martingala *= 2
                    racha_perdidas += 1
                    perdidas_dia += profit

        except Exception as e:
            print("❌ ERROR GENERAL:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(10)


# =========================
# INICIO
# =========================

if __name__ == "__main__":
    ejecutar_bot()
