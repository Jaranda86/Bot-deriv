import time
import os
import requests
from conexion_deriv import DerivBot
from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final, aprender_resultado

# =========================
# CONFIGURACIÓN TELEGRAM
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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("❌ Error Telegram:", e)

# =========================
# PARÁMETROS DE TRADING
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO = 0.10           
LIMITE_PERDIDA = -50   

# Variables de control
martingala = 1
racha_perdidas = 0
perdidas_dia = 0

# =========================
# BUCLE PRINCIPAL
# =========================
def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia

    print("🔥 ARRANCANDO BOT CON MEMORIA...")
    enviar_telegram("🤖 BOT IA PRO V2 - SISTEMA DE MEMORIA ACTIVO 🧠")

    while True:
        try:
            print("\n----------------------------------------")
            print("🔄 NUEVO CICLO DE ANÁLISIS")
            print("----------------------------------------")

            for par in pares:
                print(f"\n📊 Analizando {par}...")

                # 1. CONECTAR CON TIEMPO LÍMITE
                bot = DerivBot()
                try:
                    conectado = bot.conectar()
                    if not conectado:
                        print("❌ Falló conexión. Esperando 10 seg...")
                        time.sleep(10)
                        continue
                except Exception as e:
                    print(f"💥 ERROR CONEXIÓN: {e}")
                    time.sleep(15)
                    continue

                # 2. OBTENER DATOS
                try:
                    velas = bot.get_candles(par)
                    print(f"📈 Velas recibidas: {len(velas)}")
                except Exception as e:
                    print(f"💥 ERROR DATOS: {e}")
                    bot.cerrar()
                    time.sleep(10)
                    continue

                if len(velas) < 20:
                    print("⚠️ Pocos datos, saltando...")
                    bot.cerrar()
                    time.sleep(5)
                    continue

                # 3. ANÁLISIS
                score, tipo, datos_ia = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                decision = decision_final(tipo, score, confianza)

                print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                if not decision:
                    print("⏭️  No hay señal confiable, pasamos...")
                    bot.cerrar()
                    time.sleep(3)
                    continue

                # 4. EJECUTAR
                monto_actual = MONTO * martingala
                enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Confianza: {confianza}% | Monto: {monto_actual}")

                try:
                    contract_id = bot.comprar(par, decision, monto_actual)
                    if not contract_id:
                        print("❌ Falló compra")
                        bot.cerrar()
                        time.sleep(10)
                        continue

                    # 5. ESPERAR Y VER RESULTADO
                    print("⏳ Esperando cierre...")
                    profit = bot.check_result(contract_id)
                    bot.cerrar()

                    # 🧠 APRENDER
                    aprender_resultado(profit, datos_ia)

                    # GESTIÓN CAPITAL
                    if profit > 0:
                        enviar_telegram(f"✅ GANADA | +{profit} USD 🧠")
                        martingala = 1
                        racha_perdidas = 0
                    else:
                        enviar_telegram(f"❌ PERDIDA | {profit} USD 🧠")
                        racha_perdidas += 1
                        perdidas_dia += profit
                        
                        if racha_perdidas >= 2:
                            print("🛑 Reseteamos monto por seguridad")
                            martingala = 1
                        else:
                            martingala *= 1.5

                    if perdidas_dia <= LIMITE_PERDIDA:
                        enviar_telegram("🛑 LÍMITE ALCANZADO. BOT DETENIDO.")
                        return

                except Exception as e:
                    print(f"💥 ERROR EJECUCIÓN: {e}")
                    bot.cerrar()
                    time.sleep(10)

                time.sleep(5)

            # ==================================
            # ⏳ PAUSA GRANDE FINAL
            # ==================================
            print("\n✅ Ciclo completo. Esperando 45 segundos...")
            time.sleep(45)

        except Exception as e:
            print(f"\n💥 ERROR GLOBAL: {e}")
            print("⏳ Reiniciando ciclo en 30 segundos...")
            time.sleep(30)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    try:
        ejecutar_bot()
    except KeyboardInterrupt:
        print("👋 Bot detenido")
