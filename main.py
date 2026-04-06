import time
import requests
import os

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# =========================
# TELEGRAM
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(msg):
    try:
        if not TOKEN or not CHAT_ID:
            print("❌ TELEGRAM NO CONFIGURADO")
            return

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error Telegram:", e)


# =========================
# CONFIG
# =========================
pares = ["R_10", "R_25", "R_50"]

monto_base = 1
monto = monto_base

perdidas_dia = 0
racha_perdidas = 0

LIMITE_PERDIDA = -50


# =========================
# BOT
# =========================
def ejecutar_bot():
    global monto, perdidas_dia, racha_perdidas

    print("🔥 ARRANCÓ EL BOT")
    enviar_telegram("🔥 BOT DIOS ACTIVO")

    bot = DerivBot()

    if not bot.conectar():
        print("❌ No conecta a Deriv")
        time.sleep(60)
        return

    print("✅ Conectado a Deriv")

    while True:
        try:

            for par in pares:
                print(f"🔍 Analizando {par}")
                time.sleep(5)

                # 🔥 DEBUG REAL
                candles = bot.get_candles(par)
                print("VELAS:", len(candles))

                if not candles:
                    print("❌ Sin velas")
                    continue

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("❌ IA bloqueó")
                    continue

                enviar_telegram(f"{par} → {tipo} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    print("❌ No compra")
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                if profit > 0:
                    print("✅ GANADA", profit)
                    enviar_telegram(f"✅ GANADA {par} +{profit}")
                    monto = monto_base
                    racha_perdidas = 0

                else:
                    print("❌ PERDIDA", profit)
                    enviar_telegram(f"❌ PERDIDA {par} {profit}")
                    perdidas_dia += profit
                    racha_perdidas += 1
                    monto *= 2

        except Exception as e:
            print("❌ ERROR:", e)
            enviar_telegram(f"❌ ERROR {e}")
            time.sleep(10)


# =========================
# START
# =========================
if __name__ == "__main__":
    ejecutar_bot()
