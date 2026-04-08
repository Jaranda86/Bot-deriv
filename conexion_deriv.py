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
        print("📤 ENVIANDO A TG:", msg)
        if not TOKEN or not CHAT_ID:
            print("❌ TELEGRAM NO CONFIGURADO")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("❌ ERROR TG:", e)

# =========================
# PARÁMETROS
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO = 0.35           
LIMITE_PERDIDA = -50.00   

martingala = 1
racha_perdidas = 0
perdidas_dia = 0

# =========================
# BUCLE PRINCIPAL
# =========================
def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia

    print("🚀 BOT INICIADO - MODO CONEXIÓN ÚNICA 🚀")
    enviar_telegram("🤖 BOT IA PRO - ACTIVADO | MULTI-INDICADORES 📊")

    while True:
        bot = None
        try:
            print("\n" + "="*60)
            print("🔄 NUEVO CICLO - CONECTANDO UNA VEZ...")
            print("="*60)

            # 💡 CONECTAR SOLO UNA VEZ AL INICIO DEL CICLO
            bot = DerivBot()
            conectado = bot.conectar()
            if not conectado:
                print("❌ NO SE PUDO CONECTAR - ESPERANDO...")
                time.sleep(30)
                continue

            # ==================================
            # RECORRER TODOS LOS PARES CON LA MISMA CONEXIÓN
            # ==================================
            for par in pares:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")

                    # VELAS
                    velas = bot.get_candles(par)
                    print(f"📈 Velas recibidas: {len(velas)}")

                    if len(velas) < 30:
                        print("⚠️ Pocos datos, saltando...")
                        time.sleep(3)
                        continue

                    # ANÁLISIS
                    score, tipo, datos_ia = analizar_mercado(par, velas)
                    confianza = calcular_confianza(score)
                    decision = decision_final(tipo, score, confianza)

                    print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                    if not decision:
                        print("⏭️  SIN SEÑAL SUFICIENTE")
                        time.sleep(3)
                        continue

                    # ==================================
                    # 💸 EJECUTAR
                    # ==================================
                    monto_actual = MONTO * martingala
                    enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Confianza: {confianza}% | Monto: {monto_actual}")

                    contract_id = bot.comprar(par, decision, monto_actual)
                    print(f"📥 contract_id = {contract_id}")

                    if contract_id:
                        print(f"✅ ORDEN ENVIADA! ID: {contract_id}")
                        
                        profit = bot.check_result(contract_id)
                        print(f"🏁 RESULTADO: Profit = {profit}")
                        
                        # 🧠 APRENDER
                        datos_ia["par"] = par
                        aprender_resultado(profit, datos_ia)

                        if profit > 0:
                            enviar_telegram(f"✅ GANADA | +{profit} USD 🧠")
                            martingala = 1
                            racha_perdidas = 0
                        else:
                            enviar_telegram(f"❌ PERDIDA | {profit} USD 🧠")
                            racha_perdidas += 1
                            perdidas_dia += profit
                            
                            if racha_perdidas >= 2:
                                martingala = 1
                            else:
                                martingala *= 1.3

                        if perdidas_dia <= LIMITE_PERDIDA:
                            enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO")
                            bot.cerrar()
                            return

                    else:
                        print("❌ FALLO: contract_id es None")
                        enviar_telegram(f"⚠️ FALLO EJECUCIÓN EN {par}")
                        time.sleep(10)

                except Exception as e:
                    print(f"💥 ERROR EN {par}: {e}")
                    time.sleep(10)

            # ==================================
            # FIN DEL CICLO
            # ==================================
            print("\n✅ Ciclo terminado. Cerrando conexión...")
            bot.cerrar()
            print("⏳ Esperando 60s para nuevo ciclo...")
            time.sleep(60)

        except Exception as e:
            print(f"💥 ERROR GLOBAL: {e}")
            if bot:
                bot.cerrar()
            time.sleep(30)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    ejecutar_bot()
