import time
import requests
import os

from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final, guardar_resultado

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
        print("❌ Error Telegram:", e)

# =========================
# CONFIG
# =========================

pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

MONTO_BASE = 10
monto = MONTO_BASE

perdidas = 0
racha = 0
LIMITE = -50

# =========================
# BOT
# =========================

def ejecutar_bot():

    global monto, perdidas, racha

    print("🚀 Iniciando bot...")
    enviar_telegram("🚀 Iniciando bot...")

    bot = DerivBot()

    print("📡 Intentando conectar...")
    conectado = bot.conectar()

    if not conectado:
        print("❌ No conecta a Deriv")
        enviar_telegram("❌ No conecta a Deriv")
        return

    print("✅ Conectado correctamente, iniciando operaciones...")
    enviar_telegram("🔥 BOT ULTRA PRO ACTIVADO")

    while True:
        try:

            # =========================
            # CONTROL DE RIESGO
            # =========================

            if perdidas <= LIMITE:
                print("🛑 Límite de pérdida alcanzado")
                enviar_telegram("🛑 LIMITE PERDIDA ALCANZADO")
                time.sleep(3600)
                continue

            if racha >= 3:
                print("⚠️ Pausa por racha")
                enviar_telegram("⚠️ PAUSA POR RACHA")
                time.sleep(600)
                racha = 0
                continue

            # =========================
            # LOOP DE MERCADO
            # =========================

            for par in pares:

                time.sleep(5)

                print(f"📊 Analizando {par}")

                score, tipo = analizar_mercado(par, bot)
                print(f"Score: {score} | Tipo: {tipo}")

                confianza = calcular_confianza(score)
                print(f"Confianza IA: {confianza}%")

                tipo = decision_final(tipo, score, confianza)

                if tipo is None:
                    print("⛔ IA bloqueó operación")
                    continue

                enviar_telegram(f"{par} → {tipo} | score {score} | IA {confianza}%")

                contract_id = bot.comprar(par, tipo, monto)

                if not contract_id:
                    print("❌ No se ejecutó compra")
                    continue

                print("⏳ Esperando resultado...")
                time.sleep(65)

                profit = bot.check_result(contract_id)
                print(f"Resultado: {profit}")

                guardar_resultado(par, tipo, profit)

                # =========================
                # RESULTADO
                # =========================

                if profit > 0:
                    print("✅ GANADA")
                    enviar_telegram(f"✅ GANADA {par} +{profit}")

                    monto = MONTO_BASE
                    racha = 0

                else:
                    print("❌ PERDIDA")
                    enviar_telegram(f"❌ PERDIDA {par} {profit}")

                    perdidas += profit
                    racha += 1

                    # martingala controlada
                    monto = min(monto * 2, 50)

        except Exception as e:
            print("❌ ERROR GENERAL:", e)
            enviar_telegram(f"❌ ERROR: {e}")
            time.sleep(10)

# =========================

if __name__ == "__main__":
    ejecutar_bot()
