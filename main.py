import time
import os
import requests
from deriv_api import DerivBot
from indicadores import analizar_mercado

# ==============================
# 🚀 INICIO
# ==============================

print("🚀 BOT ARRANCANDO...")

# ==============================
# 🔐 CONFIG
# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MONTO = 1
MAX_PERDIDAS = 3
PAUSA_DEFENSA = 300  # segundos

pares = ["R_50", "R_75", "R_100"]

perdidas_consecutivas = 0


# ==============================
# 📲 TELEGRAM
# ==============================

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("❌ Error Telegram:", e)


# ==============================
# 📊 OPERAR PAR
# ==============================

def operar_par(bot, par):
    global perdidas_consecutivas

    print(f"🔍 Analizando {par}...")

    direccion, puntuacion = analizar_mercado(bot, par)

    print(f"📊 {par} | Score: {puntuacion}")

    if direccion is None:
        print("❌ Sin señal clara")
        return

    print(f"📈 Señal: {direccion.upper()} en {par}")
    enviar_telegram(f"📊 {par} → {direccion.upper()} | Score: {puntuacion}")

    resultado = bot.comprar(par, direccion, MONTO)

    if resultado is None:
        print("❌ Error al operar")
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

def iniciar_bot():
    global perdidas_consecutivas

    print("🤖 INICIANDO BOT...")

    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión Deriv")
        enviar_telegram("❌ Error conexión Deriv")
        return

    print("✅ CONECTADO A DERIV")
    enviar_telegram("🤖 BOT DEMO INICIADO")

    print("🔁 ENTRANDO AL LOOP...")

    while True:
        for par in pares:

            # 🛑 MODO DEFENSA
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
# ▶️ EJECUCIÓN
# ==============================

if __name__ == "__main__":
    iniciar_bot()
