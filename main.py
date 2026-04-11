import time
import os
import requests
import datetime
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
# ⏰ CONFIGURACIÓN HORARIO
# =========================
HORA_INICIO = 9    # 9 AM servidor = 6 AM tuyo
HORA_FIN = 23      # 11 PM servidor = 8 PM tuyo

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    return HORA_INICIO <= hora_actual < HORA_FIN

# =========================
# PARÁMETROS MODO SEGURO
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO_BASE = 0.35           
LIMITE_PERDIDA = -30.00    # Bajé el límite para proteger

martingala = 1
racha_perdidas = 0
perdidas_dia = 0
operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}

# =========================
# 📊 FUNCIÓN REPORTE DIARIO
# =========================
def enviar_reporte():
    total_ops = operaciones_hoy['ganadas'] + operaciones_hoy['perdidas']
    efectividad = round((operaciones_hoy['ganadas'] / total_ops) * 100, 2) if total_ops > 0 else 0
    
    mensaje = f"""
📊 **REPORTE DIARIO DE TRADING** 📊
📅 Fecha: {datetime.datetime.now().strftime("%d/%m/%Y")}
✅ Operaciones Ganadas: {operaciones_hoy['ganadas']}
❌ Operaciones Perdidas: {operaciones_hoy['perdidas']}
💰 Resultado Total: ${operaciones_hoy['total']:.2f}
⚡ Efectividad: {efectividad}%
    """
    enviar_telegram(mensaje)

# =========================
# BUCLE PRINCIPAL
# =========================
def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia, operaciones_hoy

    print("🚀 BOT INICIADO - MODO SEGURIDAD ACTIVADO 🚀")
    enviar_telegram("🤖 **BOT DOLA INICIADO** 🚀\n✅ Modo Seguridad Activado\n⏰ Horario: 06:00 AM a 20:00 PM")

    while True:
        bot = None
        
        # VERIFICAR HORARIO
        if not esta_dentro_horario():
            print("💤 Fuera de horario. Esperando apertura...")
            
            # Enviar reporte al cierre
            hora_actual = datetime.datetime.now()
            if hora_actual.hour == HORA_FIN and hora_actual.minute >= 5:
                enviar_reporte()
                # Reiniciar contadores
                operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}
                perdidas_dia = 0
                
            time.sleep(300) # Esperar 5 min
            continue

        try:
            print("\n" + "="*60)
            print("🔄 NUEVO CICLO - CONECTANDO...")
            print("="*60)

            # 💡 CONECTAR
            bot = DerivBot()
            conectado = bot.conectar()
            if not conectado:
                print("❌ FALLO CONEXIÓN - ESPERANDO 60 SEG...")
                time.sleep(60)
                continue

            # ==================================
            # RECORRER PARES
            # ==================================
            for par in pares:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")

                    # VELAS
                    velas = bot.get_candles(par)
                    print(f"📈 Velas recibidas: {len(velas)}")

                    if len(velas) < 10:
                        print("⚠️ Pocos datos, saltando...")
                        time.sleep(3)
                        continue

                    # ANÁLISIS
                    score, tipo, datos_ia = analizar_mercado(par, velas)
                    confianza = calcular_confianza(score)
                    decision = decision_final(tipo, score, confianza)

                    print(f"📊 Score: {score} | Confianza: {confianza}% | Decisión: {decision}")

                    # 🛡️ MODO SEGURO: Solo entrar si confianza alta
                    if not decision or confianza < 70:
                        print("⏭️  SIN SEÑAL O POCA CONFIANZA")
                        time.sleep(3)
                        continue

                    # ==================================
                    # 💸 CALCULAR MONTO CORRECTO
                    # ==================================
                    monto_bruto = MONTO_BASE * martingala
                    monto_final = round(monto_bruto, 2)  # ✅ REDONDEAR
                    
                    enviar_telegram(f"🚀 ENTRADA | {par} | {decision.upper()} | Monto: {monto_final}")

                    contract_id = bot.comprar(par, decision, monto_final)
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
                            operaciones_hoy['ganadas'] += 1
                        else:
                            enviar_telegram(f"❌ PERDIDA | {profit} USD 🧠")
                            racha_perdidas += 1
                            perdidas_dia += profit
                            operaciones_hoy['perdidas'] += 1
                            
                            # 🛡️ MARTINGALA MÁS SUAVE
                            if racha_perdidas >= 2:
                                martingala = 1
                            else:
                                martingala *= 1.2 # Bajé de 1.3 a 1.2

                        operaciones_hoy['total'] += profit

                        if perdidas_dia <= LIMITE_PERDIDA:
                            enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO - DETENIENDO")
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

            # ==================================
            # FIN CICLO
            # ==================================
            print("\n✅ Ciclo terminado. Cerrando conexión...")
            bot.cerrar()
            print("⏳ ESPERANDO 60 SEGUNDOS...")
            time.sleep(60)

        except Exception as e:
            print(f"💥 ERROR GLOBAL: {e}")
            if bot:
                bot.cerrar()
            print("⏳ ESPERANDO 60 SEGUNDOS...")
            time.sleep(60)

# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    ejecutar_bot()
