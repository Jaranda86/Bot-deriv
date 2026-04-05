import time
import requests
from deriv_api import DerivBot
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# =========================
# ⚙️ CONFIG
# =========================
TELEGRAM_TOKEN = "8329264709:AAHyKe68ERfMr37EM8qn33KzMJuCuV6KeIM"
CHAT_ID = "6826449033"

pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]
monto_base = 10

# =========================
# 📲 TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("❌ Error Telegram")

# =========================
# 🚀 BOT
# =========================
def ejecutar_bot():
    bot = DerivBot()

    if not bot.conectar():
        enviar_telegram("❌ No conecta a Deriv")
        return

    enviar_telegram("🚀 BOT ACTIVADO REAL")

    while True:
        try:
            for par in pares:

                time.sleep(5)

                print(f"🔎 Analizando {par}")

                # 📊 análisis IA
                score, tipo = analizar_mercado(par, bot)

                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"Score: {score} | Confianza: {confianza}")

                if tipo is None:
                    print("⛔ IA bloqueó")
                    continue

                # 📲 aviso
                enviar_telegram(f"📊 {par} → {tipo.upper()} | score {score} | IA {confianza}%")

                # 💰 COMPRA REAL
                contract_id = bot.comprar(par, tipo, monto_base)

                if not contract_id:
                    continue

                # ⏱ esperar resultado real
                time.sleep(65)

                profit = bot.check_result(contract_id)

                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")
                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")

        except Exception as e:
            print("❌ ERROR BOT:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(5)

# =========================
# ▶️ INICIO
# =========================
if __name__ == "__main__":
    while True:
        ejecutar_bot()
        time.sleep(10)
