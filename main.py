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
        print("📤 Enviando a Telegram:", msg)

        if not TOKEN or not CHAT_ID:
            print("❌ TELEGRAM NO CONFIGURADO")
            return

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

    except Exception as e:
        print("❌ Error Telegram:", e)


# =========================
# CONFIG
# =========================

pares = ["R_10", "R_25", "R_50"]

MONTO = 10
martingala = 1
racha_perdidas = 0
perdidas_dia = 0
LIMITE_PERDIDA = -50


# =========================
# BOT PRINCIPAL
# =========================

def ejecutar_bot():

    global martingala, racha_perdidas, perdidas_dia

    print("🔥 ARRANCANDO BOT...")
    enviar_telegram("🔥 BOT INICIADO")

    bot = DerivBot()

    time.sleep(2)

    while True:
        try:
            print("🔄 LOOP ACTIVO")

            for par in pares:

                print(f"📊 Analizando {par}")

                time.sleep(2)

                if not bot.conectar():
                    print("❌ No conecta Deriv")
                    continue

                velas = bot.get_candles(par)

                print(f"VELAS {par}: {len(velas)}")

                if len(velas) < 20:
                    print("❌ Sin velas")
                    bot.cerrar()
                    continue

                score, tipo = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"{par} → {tipo} | IA {confianza}%")

                if tipo is None:
                    bot.cerrar()
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, MONTO * martingala)

                if not contract_id:
                    bot.cerrar()
                    continue

                print("⏳ Esperando resultado...")
                time.sleep(65)

                profit = bot.check_result(contract_id)

                bot.cerrar()

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
            time.sleep(5)


# =========================
# INICIO
# =========================

if __name__ == "__main__":
    ejecutar_bot()
