import time
import os
import requests
import datetime
from conexion_deriv import DerivBot
from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final, aprender_resultado

# =========================
# CONFIGURACIÓN TELEGRAM
# =========================
TOKEN = os.getenv("8329264709:AAHyKe68ERfMr37EM8qn33KzMJuCuV6KeIM")
CHAT_ID = os.getenv("6826449033")

def enviar_telegram(msg):
    try:
        print("📤 ENVIANDO A TG:", msg)
        if not TOKEN or not CHAT_ID:
            print("❌ FALTA TOKEN O CHAT_ID")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("✅ ENVIADO OK")
    except Exception as e:
        print("❌ ERROR TG:", str(e))

# =========================
# ⏰ HORARIO
# =========================
HORA_INICIO = 9
HORA_FIN = 23

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    return HORA_INICIO <= hora_actual < HORA_FIN

# =========================
# 🛡️ PARÁMETROS SEGUROS
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO_BASE = 0.35           
LIMITE_PERDIDA = -15.00    

racha_perdidas = 0
perdidas_dia = 0
operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}

# =========================
# 📊 REPORTE
# =========================
def enviar_reporte():
    total_ops = operaciones_hoy['ganadas'] + operaciones_hoy['perdidas']
    efectividad = round((operaciones_hoy['ganadas'] / total_ops) * 100, 2) if total_ops > 0 else 0
    mensaje = f"""
📊 **REPORTE DIARIO** 📊
📅 Fecha: {datetime.datetime.now().strftime("%d/%m/%Y")}
✅ Ganadas: {operaciones_hoy['ganadas']}
❌ Perdidas: {operaciones_hoy['perdidas']}
💰 Total: ${operaciones_hoy['total']:.2f}
⚡ Efectividad: {efectividad}%
    """
    enviar_telegram(mensaje)

# =========================
# BUCLE PRINCIPAL
# =========================
def ejecutar_bot():
    global racha_perdidas, perdidas_dia, operaciones_hoy

    print("=====================================")
    print("🚀 BOT INICIADO - MODO SEGURO 🚀")
    print("=====================================")
    enviar_telegram("🤖 **BOT DOLA INICIADO** 🚀\n✅ Modo Seguro\n⏰ 06:00 AM a 20:00 PM")

    while True:
        bot = None
        
        # VERIFICAR HORARIO
        if not esta_dentro_horario():
            print("💤 Fuera de horario. Esperando...")
            hora_actual = datetime.datetime.now()
            if hora_actual.hour == HORA_FIN and hora_actual.minute >= 5:
                enviar_reporte()
                operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}
                perdidas_dia = 0
            time.sleep(300)
            continue

        try:
            print("\n" + "="*50)
            print("🔄 NUEVO CICLO")
            print("="*50)

            bot = DerivBot()
            if not bot.conectar():
                print("❌ FALLO CONEXIÓN")
                time.sleep(60)
                continue

            # RECORRER PARES
            for par in pares:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")
                    velas = bot.get_candles(par)
                    
                    if len(velas) < 10:
                        print("⚠️ Pocos datos, salteando...")
                        time.sleep(3)
                        continue

                    score, tipo, datos_ia = analizar_mercado(par, velas)
                    confianza = calcular_confianza(score)
                    decision = decision_final(tipo, score, confianza)

                    print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                    # 🛡️ FILTRO DE SEGURIDAD
                    if not decision or confianza < 80:
                        print("⏭️  SALTEANDO (poca confianza)")
                        time.sleep(3)
                        continue

                    # 💸 MONTO FIJO
                    monto_final = MONTO_BASE 
                    
                    enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Monto: {monto_final}")

                    contract_id = bot.comprar(par, decision, monto_final)

                    if contract_id:
                        print(f"✅ ORDEN ENVIADA! ID: {contract_id}")
                        profit = bot.check_result(contract_id)
                        print(f"🏁 RESULTADO: Profit = {profit}")
                        
                        datos_ia["par"] = par
                        aprender_resultado(profit, datos_ia)

                        if profit > 0:
                            enviar_telegram(f"✅ GANADA | +{profit} USD 🧠")
                            racha_perdidas = 0
                            operaciones_hoy['ganadas'] += 1
                        else:
                            enviar_telegram(f"❌ PERDIDA | {profit} USD 🧠")
                            racha_perdidas += 1
                            perdidas_dia += profit
                            operaciones_hoy['perdidas'] += 1

                        operaciones_hoy['total'] += profit

                        if perdidas_dia <= LIMITE_PERDIDA:
                            enviar_telegram("🛑 LÍMITE ALCANZADO - DETENIENDO")
                            enviar_reporte()
                            bot.cerrar()
                            return

                    else:
                        print("❌ FALLO: contract_id es None")
                        enviar_telegram(f"⚠️ FALLO EJECUCIÓN EN {par}")
                        time.sleep(10)

                except Exception as e:
                    print(f"💥 ERROR EN {par}: {e}")
                    time.sleep(10)

            print("\n✅ Ciclo terminado. Cerrando conexión...")
            bot.cerrar()
            print("⏳ ESPERANDO 60 SEGUNDOS...")
            time.sleep(60)

        except Exception as e:
            print(f"💥 ERROR GLOBAL: {e}")
            if bot:
                bot.cerrar()
            time.sleep(60)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    try:
        ejecutar_bot()
    except Exception as e:
        print(f"💥 ERROR FATAL: {e}")
        # Intentar avisar del error
        try:
            enviar_telegram(f"💥 BOT DETENIDO POR ERROR: {e}")
        except:
            pass
