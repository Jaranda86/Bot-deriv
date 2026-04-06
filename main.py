import time
import os
import requests
from conexion_deriv import DerivBot  # <-- Usamos TU archivo de conexión
from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final

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
MONTO = 0.35
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

    while True:
        try:
            print("🔄 NUEVO CICLO")

            for par in pares:
                print(f"\n📊 Analizando {par}")

                # CREAMOS CONEXIÓN
                bot = DerivBot()

                if not bot.conectar():
                    print("❌ No conecta Deriv, reintentando...")
                    time.sleep(5)
                    continue

                # OBTENER VELAS
                velas = bot.get_candles(par)
                print(f"VELAS {par}: {len(velas)}")

                if len(velas) < 20:
                    print("❌ Sin velas suficientes")
                    bot.cerrar()
                    continue

                # ANÁLISIS DE LA IA
                score, tipo = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"{par} → {tipo} | IA {confianza}%")

                if tipo is None:
                    bot.cerrar()
                    time.sleep(2)
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | IA {confianza}%")

                # EJECUTAR OPERACIÓN
                contract_id = bot.comprar(par, tipo, MONTO * martingala)

                if not contract_id:
                    print("❌ No se pudo comprar")
                    bot.cerrar()
                    continue

                print("⏳ Esperando resultado...")
                profit = bot.check_result(contract_id)

                bot.cerrar()

                # GESTIÓN DE CAPITAL
                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")
                    martingala = 1
                    racha_perdidas = 0
                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")
                    martingala *= 2
                    racha_perdidas += 1
                    perdidas_dia += profit

                # CONTROL DE PÉRDIDAS
                if perdidas_dia <= LIMITE_PERDIDA:
                    enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO. BOT DETENIDO.")
                    print("🛑 Bot detenido.")
                    return

                time.sleep(3)

        except Exception as e:
            print("❌ ERROR GENERAL:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(10)

# =========================
# INICIO
# =========================
if __name__ == "__main__":
    ejecutar_bot()
