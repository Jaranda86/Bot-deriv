import time
import os
import requests
import datetime
from conexion_deriv import DerivBot
# IMPORTAMOS LA NUEVA ESTRATEGIA
from estrategia_nueva import EstrategiaAvanzada

# =========================
# CONFIGURACIÓN TELEGRAM
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(msg):
    try:
        if not TOKEN or not CHAT_ID:
            print("❌ FALTA TOKEN O CHAT_ID")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        datos = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, data=datos, timeout=15)
    except:
        pass

# =========================
# ⏰ HORARIO
# =========================
HORA_INICIO = 11
HORA_FIN = 14

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    return HORA_INICIO <= hora_actual < HORA_FIN

# =========================
# 🛡️ PARÁMETROS
# =========================
PARES = ["R_50"]
MONTO_BASE = 0.35
LIMITE_PERDIDA = -5.00

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
📊 <b>REPORTE NUEVA ESTRATEGIA</b> 📊
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

    print("🚀 BOT INICIADO - NUEVA ESTRATEGIA 🚀")
    enviar_telegram("🤖 <b>VERSION 2.0 ACTIVADA</b>\n✅ Nueva Logica\n⏰ 11:00 a 14:00\n🛑 Stop Loss: $5.00")

    # INICIALIZAMOS LA NUEVA ESTRATEGIA
    estrategia = EstrategiaAvanzada()

    while True:
        bot = None
        
        if not esta_dentro_horario():
            print("💤 Fuera de horario...")
            hora_actual = datetime.datetime.now()
            if hora_actual.hour == HORA_FIN and hora_actual.minute >= 5:
                enviar_reporte()
                operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}
                perdidas_dia = 0
            time.sleep(300)
            continue

        try:
            bot = DerivBot()
            if not bot.conectar():
                time.sleep(60)
                continue

            for par in PARES:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")
                    velas = bot.get_candles(par)

                    if len(velas) < 20:
                        time.sleep(3)
                        continue

                    # ==== AQUI USAMOS LA NUEVA LOGICA ====
                    señal, confianza, info = estrategia.calcular_senal(velas)
                    
                    print(f"📊 Señal: {señal} | Confianza: {confianza}%")

                    # Solo entramos si hay señal y confianza alta
                    if señal and confianza >= 85:
                        enviar_telegram(f"🚀 ENTRADA | {par} | {señal.upper()} | Conf: {confianza}%")
                        
                        contract_id = bot.comprar(par, señal, MONTO_BASE)

                        if contract_id:
                            profit = bot.check_result(contract_id)
                            print(f"🏁 RESULTADO: {profit}")

                            if profit > 0:
                                enviar_telegram(f"✅ GANADA | +{profit} USD")
                                racha_perdidas = 0
                                operaciones_hoy['ganadas'] += 1
                            else:
                                enviar_telegram(f"❌ PERDIDA | {profit} USD")
                                racha_perdidas += 1
                                perdidas_dia += profit
                                operaciones_hoy['perdidas'] += 1
                                
                                # PAUSA POR RACHA
                                if racha_perdidas >= 2:
                                    enviar_telegram(f"⚠️ RACHA DE 2 - PAUSA 10 MIN")
                                    time.sleep(600)
                                    racha_perdidas = 0

                            operaciones_hoy['total'] += profit

                            # STOP LOSS TOTAL
                            if perdidas_dia <= LIMITE_PERDIDA:
                                enviar_telegram(f"🛑 LIMITE ALCANZADO - DETENIENDO")
                                enviar_reporte()
                                bot.cerrar()
                                return

                    time.sleep(5)

                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(10)

            bot.cerrar()
            time.sleep(60)

        except Exception as e:
            print(f"Error Global: {e}")
            if bot: bot.cerrar()
            time.sleep(60)

if __name__ == "__main__":
    ejecutar_bot()
