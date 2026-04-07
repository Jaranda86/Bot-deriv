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
MONTO = 0.10           
LIMITE_PERDIDA = -50   

martingala = 1
racha_perdidas = 0
perdidas_dia = 0

# =========================
# BUCLE PRINCIPAL
# =========================
def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia

    print("🚀 BOT INICIADO - MODO DEBUG ACTIVO")
    enviar_telegram("🤖 BOT IA PRO - INICIADO Y MONITOREEANDO 📊")

    while True:
        try:
            print("\n" + "="*50)
            print("🔄 NUEVO CICLO")
            print("="*50)

            for par in pares:
                print(f"\n📊 ANALIZANDO {par}...")

                bot = DerivBot()
                conectado = False
                
                try:
                    print("🔌 Conectando...")
                    conectado = bot.conectar()
                    if conectado:
                        print("✅ CONEXIÓN EXITOSA")
                    else:
                        print("❌ FALLO CONEXIÓN")
                        time.sleep(5)
                        continue
                except Exception as e:
                    print(f"💥 ERROR CONECTANDO: {e}")
                    time.sleep(10)
                    continue

                # OBTENER VELAS
                try:
                    print("📥 Pidiendo velas...")
                    velas = bot.get_candles(par)
                    print(f"📈 Velas recibidas: {len(velas)}")
                except Exception as e:
                    print(f"💥 ERROR VELAS: {e}")
                    bot.cerrar()
                    continue

                if len(velas) < 20:
                    print("⚠️ Pocos datos")
                    bot.cerrar()
                    continue

                # ANÁLISIS
                score, tipo, datos_ia = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                decision = decision_final(tipo, score, confianza)

                print(f"📊 Score: {score} | Conf: {confianza}% | Decisión: {decision}")

                if not decision:
                    print("⏭️  SIN SEÑAL")
                    bot.cerrar()
                    time.sleep(2)
                    continue

                # ==================================
                # 💸 EJECUCIÓN REAL
                # ==================================
                monto_actual = MONTO * martingala
                print(f"💰 INTENTANDO COMPRAR: {par} | {decision} | Monto: {monto_actual}")
                
                enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Confianza: {confianza}% | Monto: {monto_actual}")

                try:
                    contract_id = bot.comprar(par, decision, monto_actual)
                    
                    if contract_id:
                        print(f"✅ ORDEN ENVIADA! ID: {contract_id}")
                        
                        # ESPERAR RESULTADO
                        print("⏳ Esperando resultado...")
                        profit = bot.check_result(contract_id)
                        print(f"🏁 RESULTADO FINAL: Profit = {profit}")
                        
                        bot.cerrar()

                        # APRENDER
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
                                martingala *= 1.5

                        if perdidas_dia <= LIMITE_PERDIDA:
                            enviar_telegram("🛑 LÍMITE ALCANZADO")
                            return

                    else:
                        print("❌ FALLO CRÍTICO: contract_id es NINGUNO")
                        print("⚠️ Posible causa: Saldo insuficiente, Permisos, o API rechazó")
                        bot.cerrar()
                        enviar_telegram(f"⚠️ FALLO EJECUCIÓN EN {par} | Revisar logs")
                        time.sleep(10)

                except Exception as e:
                    print(f"💥 ERROR EN EJECUCIÓN: {e}")
                    bot.cerrar()
                    time.sleep(10)

                time.sleep(5)

            print("\n✅ Ciclo terminado. Esperando 45s...")
            time.sleep(45)

        except Exception as e:
            print(f"💥 ERROR GLOBAL: {e}")
            time.sleep(30)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    ejecutar_bot()
