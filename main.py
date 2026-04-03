import time
import os
import requests
from deriv_api import DerivBot
from indicadores import analizar_mercado

# ==============================
# 🔐 CONFIG
# ==============================

TOKEN = os.getenv("8329264709:AAHyKe68ERfMr37EM8qn33KzMJuCuV6KeIM")
CHAT_ID = os.getenv("6826449033")

MONTO = 1
MAX_PERDIDAS = 3
PAUSA_DEFENSA = 300  # 5 minutos

pares = ["R_50", "R_75", "R_100"]

perdidas_consecutivas = 0


# ==============================
# 📲 TELEGRAM
# ==============================

def enviar_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url, data=data)
    except:
        print("❌ Error Telegram")


# ==============================
# 📊 OPERAR PAR
# ==============================

def operar_par(bot, par):
    global perdidas_consecutivas

    direccion, puntuacion = analizar_mercado(bot, par)

    print(f"🔍 {par} | Score: {puntuacion}")

    if direccion is None:
        print("❌ Sin señal clara")
        return

    print(f"📊 Señal: {direccion.upper()} en {par}")

    enviar_telegram(f"📊 {par} → {direccion.upper()} | Score: {puntuacion}")

    resultado = bot.comprar(par, direccion, MONTO)

    if resultado is None:
        print("❌ Error al ejecutar trade")
        return

    if resultado == "win":
        print("✅ GANADA")
        enviar_telegram(f"✅ GANADA en {par}")
        perdidas_consecutivas = 0

    else:
        print("❌ PERDIDA")
        enviar_telegram(f"❌ PERDIDA en {par}")
        perdidas_consecutivas += 1


# ==============================
# 🧠 BOT PRINCIPAL
# ==============================

def bot():
    global perdidas_consecutivas

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión Deriv")
        enviar_telegram("❌ Error conexión Deriv")
        return

    print("🤖 BOT DEMO INICIADO")
    enviar_telegram("🤖 BOT DEMO INICIADO")

    while True:
        for par in pares:

            # 🛑 modo defensa
            if perdidas_consecutivas >= MAX_PERDIDAS:
                print("🛑 MODO DEFENSA ACTIVADO")
                enviar_telegram("🛑 Modo defensa activado (pausa 5 min)")
                time.sleep(PAUSA_DEFENSA)
                perdidas_consecutivas = 0

            try:
                operar_par(bot, par)
            except Exception as e:
                print(f"❌ Error en {par}: {e}")

            time.sleep(10)


# ==============================
# 🚀 RUN
# ==============================

if __name__ == "__main__":
    bot()
