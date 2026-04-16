import time
import os
import requests
import datetime
from conexion_deriv import DerivBot
from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final, aprender_resultado

from time_strategy import obtener_estrategia, TipoActivo, Estrategia

# =========================
# CONFIGURACIÓN TELEGRAM
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        print("📤 ENVIANDO A TG:", msg)
        if not TOKEN or not CHAT_ID:
            print("❌ FALTA TOKEN O CHAT_ID")
            return
            
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        datos = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        respuesta = requests.post(url, data=datos, timeout=15)
        
        if respuesta.status_code == 200:
            print("✅ MENSAJE ENVIADO OK")
        else:
            print(f"⚠️ ERROR TG: {respuesta.status_code}")
            
    except Exception as e:
        print("❌ ERROR ENVIANDO:", str(e))

# =========================
# ⏰ HORARIO ULTRA REDUCIDO
# =========================
HORA_INICIO = 11
HORA_FIN = 14  # ✅ TERMINA A LAS 14:00 HS

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    return HORA_INICIO <= hora_actual < HORA_FIN

# =========================
# 🛡️ PARÁMETROS DE RIESGO MÁXIMO
# =========================
pares = ["R_50"]  # ✅ SOLO R_50, QUITAMOS LOS OTROS
MONTO_BASE = 0.35
LIMITE_PERDIDA = -5.00    # ✅ SI PERDEMOS 5 USD PARAMOS YA

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
📊 <b>REPORTE DIARIO DE TRADING</b> 📊
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
    print("🚀 BOT INICIADO - MODO CIRUJANO 🚀")
    print("=====================================")
    enviar_telegram("🤖 <b>MODO CIRUJANO ACTIVADO</b> 🔪\n✅ Solo R_50\n⏰ Horario: 11:00 a 14:00\n🎯 Confianza: 95%+\n🛑 Stop Loss: $5.00")

    while True:
        bot = None
        
        if not esta_dentro_horario():
            print("💤 Fuera de horario quirúrgico. Esperando...")
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

            for par in pares:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")
                    
                    tipo_activo = TipoActivo.TIPO_B
                        
                    estrategias_permitidas = obtener_estrategia(datetime.datetime.now().hour, tipo_activo)
                    
                    permitido = any(e.value == par for e in estrategias_permitidas)
                    
                    if not permitido:
                        print(f"⏭️  {par} DESACTIVADO.")
                        time.sleep(2)
                        continue
                    else:
                        print(f"✅ {par} ACTIVO")

                    velas = bot.get_candles(par)
                    
                    if len(velas) < 10:
                        print("⚠️ Pocos datos, salteando...")
                        time.sleep(3)
                        continue

                    score, tipo, datos_ia = analizar_mercado(par, velas)
                    confianza = calcular_confianza(score)
                    decision = decision_final(tipo, score, confianza)

                    print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                    # 🛡️ FILTRO DE CONFIANZA SUBIDO A 95%
                    if not decision or confianza < 95:
                        print("⏭️  SALTEANDO (confianza < 95% o sin señal)")
                        time.sleep(3)
                        continue

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
                            
                            # PAUSA INMEDIATA
                            if racha_perdidas >= 2:
                                msg_pausa = f"⚠️ RACHA DE {racha_perdidas} PERDIDAS - PAUSA 10 MINUTOS"
                                print(msg_pausa)
                                enviar_telegram(msg_pausa)
                                time.sleep(600) # 10 minutos de descanso
                                racha_perdidas = 0

                        operaciones_hoy['total'] += profit

                        # LÍMITE DE PÉRDIDA DIARIA
                        if perdidas_dia <= LIMITE_PERDIDA:
                            enviar_telegram(f"🛑 LÍMITE DE ${LIMITE_PERDIDA} ALCANZADO - DETENIENDO")
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
        try:
            enviar_telegram(f"💥 BOT DETENIDO: {e}")
        except:
            pass
