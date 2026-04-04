import time
import os
import requests
from deriv_api import DerivBot
from indicadores import analizar_mercado
from modelo_ia import guardar_operacion, analizar_historial

print("🔥 BOT PRO ACTIVO 🔥")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ganadas = 0
perdidas = 0
balance = 0

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


def resumen_diario():
    global ganadas, perdidas, balance

    msg = f"""
📊 RESUMEN DEL DÍA

✅ Ganadas: {ganadas}
❌ Perdidas: {perdidas}
💰 Balance: {balance}
"""
    enviar_telegram(msg)

    ganadas = 0
    perdidas = 0
    balance = 0


def bot():
    global ganadas, perdidas, balance

    bot = DerivBot()

    if not bot.connect():
        return

    enviar_telegram("🤖 BOT INICIADO")

    pares = ["R_10", "R_25", "R_50", "R_75", "R_100"]

    while True:
        hora = time.localtime().tm_hour

        # 🕗 resumen diario
        if hora == 20:
            resumen_diario()
            time.sleep(60)

        precision = analizar_historial()
        print(f"🧠 IA precisión: {round(precision*100,2)}%")

        for par in pares:
            decision, score = analizar_mercado(bot, par)

            if decision is None:
                print(f"❌ Sin señal en {par}")
                continue

            print(f"📊 {par} → {decision.upper()} | Score: {score}")
            enviar_telegram(f"{par} → {decision.upper()} | Score: {score}")

            resultado = bot.comprar(par, decision, monto=10)

            # 🔥 simulación resultado (mejorable luego)
            win = True if score > 0 else False

            if win:
                ganadas += 1
                balance += 1
                enviar_telegram(f"✅ GANADA en {par}")
                guardar_operacion(par, decision, score, "win")
            else:
                perdidas += 1
                balance -= 1
                enviar_telegram(f"❌ PERDIDA en {par}")
                guardar_operacion(par, decision, score, "loss")

            time.sleep(5)

        time.sleep(10)


if __name__ == "__main__":
    bot()
