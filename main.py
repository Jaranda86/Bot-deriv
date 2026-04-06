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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("❌ Error Telegram:", e)

# =========================
# PARÁMETROS DE TRADING
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO = 0.10          # Monto base
LIMITE_PERDIDA = -50   # Límite de pérdida diaria

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
            print("\n🔄 NUEVO CICLO DE ANÁLISIS")

            for par in pares:
                print(f"\n📊 Analizando {par}...")

                # 1. CONECTAR A DERIV
                bot = DerivBot()
                if not bot.conectar():
                    print("❌ No se pudo conectar a Deriv")
                    time.sleep(5)
                    continue

                # 2. OBTENER DATOS
                velas = bot.get_candles(par)
                print(f"📈 Velas recibidas: {len(velas)}")

                if len(velas) < 20:
                    print("⚠️ Pocos datos, saltando...")
                    bot.cerrar()
                    continue

                # 3. ANÁLISIS CON IA Y MEMORIA
                score, tipo, datos_ia = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                decision = decision_final(tipo, score, confianza)

                print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                # 4. SI NO HAY SEÑAL, SALIR
                if not decision:
                    print("⏭️  No hay señal confiable, pasamos...")
                    bot.cerrar()
                    time.sleep(2)
                    continue

                # 5. EJECUTAR OPERACIÓN
                monto_actual = MONTO * martingala
                enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Confianza: {confianza}% | Monto: {monto_actual}")

                contract_id = bot.comprar(par, decision, monto_actual)

                if not contract_id:
                    print("❌ Falló la ejecución de la compra")
                    bot.cerrar()
                    continue

                # 6. ESPERAR Y VER RESULTADO
                print("⏳ Esperando cierre de operación...")
                profit = bot.check_result(contract_id)
                bot.cerrar()

                # ==================================
                # 🧠 SISTEMA DE APRENDIZAJE
                # ==================================
                aprender_resultado(profit, datos_ia)

                # ==================================
                # GESTIÓN DE CAPITAL (MÁS SEGURA)
                # ==================================
                if profit > 0:
                    enviar_telegram(f"✅ GANADA | +{profit} USD 🧠 +1 Experiencia")
                    martingala = 1
                    racha_perdidas = 0
                else:
                    enviar_telegram(f"❌ PERDIDA | {profit} USD 🧠 Ajustando estrategia...")
                    racha_perdidas += 1
                    perdidas_dia += profit
                    
                    # Martingala MODIFICADA (más segura)
                    if racha_perdidas >= 2:
                        print("🛑 Racha de pérdidas, reseteamos monto para proteger cuenta")
                        martingala = 1
                    else:
                        martingala *= 1.5  # Aumenta suave, no duplica bruscamente

                # ==================================
                # CONTROL DE RIESGO TOTAL
                # ==================================
                if perdidas_dia <= LIMITE_PERDIDA:
                    enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO. BOT DETENIDO POR SEGURIDAD.")
                    print("🛑 Bot detenido.")
                    return

                time.sleep(3)  # Pausa entre operaciones

        except Exception as e:
            print("❌ ERROR EN EL SISTEMA:", e)
            enviar_telegram(f"⚠️ ERROR CRÍTICO: {e}")
            time.sleep(10)

# =========================
# INICIAR BOT
# =========================
if __name__ == "__main__":
    try:
        ejecutar_bot()
    except KeyboardInterrupt:
        print("👋 Bot detenido por el usuario")
