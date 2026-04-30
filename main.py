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
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje: {e}")
        pass

# =========================
# ⏰ HORARIO - AJUSTADO PARA PROBAR, PUEDES VOLVER A 11 Y 14 CUANDO QUIERAS
# =========================
HORA_INICIO = 8
HORA_FIN = 20

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    dentro = HORA_INICIO <= hora_actual < HORA_FIN
    print(f"⏰ Hora actual: {hora_actual} | Dentro de horario: {dentro}")
    return dentro

# =========================
# 🛡️ PARÁMETROS
# =========================
PARES = ["R_50"]
MONTO_BASE = 0.35
LIMITE_PERDIDA = -5.00
CONFIAZA_MINIMA = 50  # BAJADO DE 70 A 50 PARA QUE DETECTE MÁS SEÑALES

racha_perdidas = 0
perdidas_dia = 0
operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}

# =========================
# 📊 REPORTE
# =========================
def enviar_reporte():
    total_ops = operaciones_hoy['ganadas'] + operaciones_hoy['perdidas']
    efectividad = round((operaciones_hoy['ganadas'] / total_ops) * 100, 2) if total_ops >  0 else 0
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
    enviar_telegram("🤖 <b>VERSION 2.2 ACTIVADA</b>\n✅ Correcciones aplicadas\n⏰ Horario ampliado para pruebas\n🛑 Stop Loss: $5.00")

    # INICIALIZAMOS LA ESTRATEGIA (una sola vez)
    estrategia = EstrategiaAvanzada()
    
    bot = None 
    
    while True:
        # Si no está dentro de horario, dormir
        if not esta_dentro_horario():
            print("💤 Fuera de horario...")
            hora_actual = datetime.datetime.now()
            if hora_actual.hour == HORA_FIN and hora_actual.minute >= 5:
                enviar_reporte()
                operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'total': 0.0}
                perdidas_dia = 0
            time.sleep(300)
            
            if bot:
                try:
                    bot.cerrar()
                except:
                    pass
                bot = None
            continue

        # Conectar si no hay conexión
        if not bot:
            try:
                print("🔌 Conectando a Deriv...")
                bot = DerivBot()
                if not bot.conectar():
                    print("❌ Error al conectar. Reintentando en 60s...")
                    enviar_telegram("❌ No se pudo conectar a Deriv. Reintentando...")
                    time.sleep(60)
                    bot = None
                    continue
                print("✅ Conectado exitosamente!")
                enviar_telegram("✅ Conexión establecida con Deriv")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
                enviar_telegram(f"❌ Error de conexión: {str(e)}")
                time.sleep(60)
                bot = None
                continue

        try:
            for par in PARES:
                try:
                    print(f"\n📊 ANALIZANDO {par}...")
                    velas = bot.get_candles(par)

                    # MENSAJE AGREGADO: Ver cuántas velas se reciben
                    print(f"📈 Velas obtenidas: {len(velas)}")

                    if len(velas) < 20:
                        print("⚠️ No hay suficientes velas, esperando...")
                        time.sleep(3)
                        continue

                    # Cálculo de señal
                    señal, confianza, info = estrategia.calcular_senal(velas)
                    print(f"🔍 Resultado análisis -> Señal: {señal} | Confianza: {confianza}% | Info: {info}")

                    # Condición de entrada con límite más bajo
                    if señal and confianza >= CONFIAZA_MINIMA:
                        enviar_telegram(f"🚀 ENTRADA | {par} | {señal.upper()} | Conf: {confianza}%\n{info}")
                        
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
                                
                                if racha_perdidas >= 2:
                                    enviar_telegram(f"⚠️ RACHA DE 2 - PAUSA 10 MIN")
                                    time.sleep(600)
                                    racha_perdidas = 0

                            operaciones_hoy['total'] += profit

                            # Stop Loss total
                            if perdidas_dia <= LIMITE_PERDIDA:
                                enviar_telegram(f"🛑 LIMITE ALCANZADO - DETENIENDO")
                                enviar_reporte()
                                if bot: bot.cerrar()
                                return

                    else:
                        print("ℹ️ No cumple condiciones para entrar")

                    time.sleep(5)

                except Exception as e:
                    print(f"⚠️ Error en par {par}: {e}")
                    if "rate limit" in str(e).lower() or "autoriz" in str(e).lower():
                        print("🔄 Posible problema de conexión. Reiniciando...")
                        enviar_telegram("🔄 Reiniciando conexión por error...")
                        if bot: bot.cerrar()
                        bot = None
                        break
                    time.sleep(10)

            # Esperar 1 minuto antes de volver a revisar
            if bot:
                time.sleep(60)

        except Exception as e:
            print(f"❌ Error Global: {e}")
            enviar_telegram(f"❌ Error grave: {str(e)}. Reiniciando...")
            if bot: 
                try:
                    bot.cerrar()
                except:
                    pass
            bot = None
            time.sleep(60)

if __name__ == "__main__":
    ejecutar_bot()
