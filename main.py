import time
import requests
import os

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# =========================
# 🔐 TELEGRAM
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
# ⚙️ CONFIG BOT
# =========================
pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

monto_base = 1
monto = monto_base

martingala = True
multiplicador = 2

ganancia_total = 0
perdidas_dia = 0
racha_perdidas = 0

LIMITE_PERDIDA = -50


# =========================
# 🚀 BOT PRINCIPAL
# =========================
def ejecutar_bot():
    global monto, perdidas_dia, racha_perdidas

    print("🔥 ARRANCÓ EL BOT")
    enviar_telegram("🔥 BOT DIOS PRO ACTIVADO")

    bot = DerivBot()

    # 🔌 CONEXIÓN SEGURA (ANTI BLOQUEO)
    if not bot.conectar():
        print("❌ No conecta a Deriv, reintento en 60s")
        time.sleep(60)
        return

    print("✅ Conectado a Deriv")

    while True:
        try:

            # 🔴 LIMITE DE PÉRDIDA
            if perdidas_dia <= LIMITE_PERDIDA:
                enviar_telegram("🛑 LIMITE DE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            # ⚠️ PAUSA POR RACHA
            if racha_perdidas >= 3:
                enviar_telegram("⚠️ Pausa por racha de pérdidas")
                time.sleep(600)
                racha_perdidas = 0
                monto = monto_base
                continue

            for par in pares:
                time.sleep(5)

                print(f"🔍 Analizando {par}")

                score, tipo = analizar_mercado(par, bot)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("❌ IA bloqueó operación")
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | score {score} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    print("❌ No se ejecutó compra")
                    continue

                time.sleep(65)

                profit = bot.check_result(contract_id)

                # ✅ GANADA
                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")
                    monto = monto_base
                    racha_perdidas = 0

                # ❌ PERDIDA
                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")
                    perdidas_dia += profit
                    racha_perdidas += 1

                    if martingala:
                        monto *= multiplicador

        except Exception as e:
            print("❌ ERROR GENERAL:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(10)


# =========================
# ▶️ INICIO
# =========================
if __name__ == "__main__":
    ejecutar_bot()
