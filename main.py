import time
import os
import requests
from conexion_deriv import DerivBot
# from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final, aprender_resultado

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

    print("🚀 BOT INICIADO - MODO PRUEBA RÁPIDA")
    enviar_telegram("🤖 BOT IA PRO - CONECTADO ✅")

    while True:
        try:
            print("\n" + "="*50)
            print("🔄 NUEVO CICLO")
            print("="*50)

            for par in pares:
                print(f"\n📊 ANALIZANDO {par}...")
                contract_id = None

                bot = DerivBot()
                
                # CONECTAR
                conectado = bot.conectar()
                if not conectado:
                    print("❌ FALLO CONEXIÓN")
                    time.sleep(5)
                    continue

                # VELAS
                print("📥 LLAMANDO A get_candles...")
                velas = bot.get_candles(par)
                print(f"📈 Velas recibidas: {len(velas)}")

                if len(velas) < 10:
                    print("⚠️ Pocos datos, saltando...")
                    bot.cerrar()
                    continue

                # ==================================
                # ✅ PRUEBA DIRECTA: COMPRAR YA
                # ==================================
                print("⚡ EJECUTANDO PRUEBA DE COMPRA...")
                enviar_telegram(f"🚀 ENTRADA PRUEBA | {par} | CALL | Monto: {MONTO}")

                try:
                    contract_id = bot.comprar(par, "CALL", MONTO)
                    print(f"📥 contract_id = {contract_id}")

                    if contract_id:
                        print(f"✅ ORDEN ENVIADA! ID: {contract_id}")
                        
                        profit = bot.check_result(contract_id)
                        print(f"🏁 RESULTADO: Profit = {profit}")
                        
                        bot.cerrar()

                        if profit > 0:
                            enviar_telegram(f"✅ GANADA | +{profit} USD")
                            martingala = 1
                            racha_perdidas = 0
                        else:
                            enviar_telegram(f"❌ PERDIDA | {profit} USD")
                            racha_perdidas += 1
                            perdidas_dia += profit
                            
                    else:
                        print("❌ FALLO: contract_id es None")
                        enviar_telegram(f"⚠️ FALLO EJECUCIÓN EN {par}")
                        bot.cerrar()
                        time.sleep(10)

                except Exception as e:
                    print(f"💥 ERROR EJECUCIÓN: {e}")
                    enviar_telegram(f"💥 EXCEPCIÓN: {e}")
                    bot.cerrar()
                    time.sleep(10)

                time.sleep(5)

            print("\n✅ Ciclo terminado. Esperando 60s...")
            time.sleep(60)

        except Exception as e:
            print(f"💥 ERROR GLOBAL: {e}")
            time.sleep(30)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    ejecutar_bot()
