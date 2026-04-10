# ============ BOT DOLA - MODO SEGURIDAD MAXIMA ============
# Horario: 06:00 AM - 20:00 PM (Hora Local)
# Configuración: Conservadora | Reporte Diario a Telegram ON
# ===========================================================

import datetime
import time
# from your_modules import your_logic  <-- Aquí están tus importaciones reales

# ---------------------- CONFIGURACIÓN PRINCIPAL ----------------------
CONFIG = {
    'horario_inicio': 9,    # 🕒 AJUSTADO A HORA SERVIDOR (9 AM UTC = 6 AM tuyo)
    'horario_fin': 23,      # 🕒 AJUSTADO A HORA SERVIDOR (11 PM UTC = 8 PM tuyo)
    'riesgo_por_operacion': 0.5,
    'stop_loss_pips': 15,
    'take_profit_pips': 30,
    'fuerza_minima_señal': 70
}

# ---------------------- FUNCIONES INTERNAS ----------------------

def enviar_mensaje_telegram(texto):
    """Función para mandar mensajes rápidos"""
    # --- AQUÍ ESTÁ TU CÓDIGO REAL DE CONEXIÓN ---
    print(f"📤 Enviado a Telegram: {texto}")

def esta_dentro_horario():
    hora_actual = datetime.datetime.now().hour
    return CONFIG['horario_inicio'] <= hora_actual < CONFIG['horario_fin']

def calcular_fuerza_senal():
    """IA analiza el mercado"""
    # --- AQUÍ ESTÁ TU LÓGICA REAL DE INDICADORES ---
    puntaje = 0
    
    # ... (Tu código real aquí) ...
    
    return puntaje

def abrir_operacion(riesgo, sl, tp):
    """Ejecuta la orden real"""
    # --- AQUÍ ESTÁ TU CÓDIGO REAL DE TRADING ---
    print(f"📈 Abriendo operación | Riesgo: {riesgo}% | SL: {sl} | TP: {tp}")
    
    # Simulación de resultado
    return {'profit': 0}

def enviar_reporte_telegram(resumen):
    mensaje = f"""
📊 **REPORTE DIARIO DE TRADING** 📊
📅 Fecha: {resumen['fecha']}
✅ Ganadas: {resumen['ganadas']}
❌ Perdidas: {resumen['perdidas']}
💰 Total: ${resumen['profit_total']:.2f}
⚡ Efectividad: {resumen['efectividad']}%
    """
    enviar_mensaje_telegram(mensaje)

def ejecutar_trading():
    operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'profit_total': 0}
    
    while True:
        hora_actual = datetime.datetime.now()
        
        if not esta_dentro_horario():
            print("💤 Fuera de horario. Esperando...")
            
            # Enviar reporte al cierre
            if hora_actual.hour == 23 and hora_actual.minute >= 5:
                total_ops = operaciones_hoy['ganadas'] + operaciones_hoy['perdidas']
                if total_ops > 0:
                    efectividad = round((operaciones_hoy['ganadas'] / total_ops) * 100, 2)
                else:
                    efectividad = 0
                
                reporte = {
                    'fecha': hora_actual.strftime("%d/%m/%Y"),
                    'ganadas': operaciones_hoy['ganadas'],
                    'perdidas': operaciones_hoy['perdidas'],
                    'profit_total': operaciones_hoy['profit_total'],
                    'efectividad': efectividad
                }
                enviar_reporte_telegram(reporte)
                operaciones_hoy = {'ganadas': 0, 'perdidas': 0, 'profit_total': 0}
            
            time.sleep(300)
            continue

        print("🔍 Analizando mercado...")
        fuerza = calcular_fuerza_senal()
        
        if fuerza >= CONFIG['fuerza_minima_señal']:
            print(f"✅ Señal fuerte ({fuerza} pts). Ejecutando orden...")
            resultado = abrir_operacion(
                riesgo=CONFIG['riesgo_por_operacion'],
                sl=CONFIG['stop_loss_pips'],
                tp=CONFIG['take_profit_pips']
            )
            
            if resultado['profit'] > 0:
                operaciones_hoy['ganadas'] += 1
            else:
                operaciones_hoy['perdidas'] += 1
            operaciones_hoy['profit_total'] += resultado['profit']
            
        else:
            print(f"⏳ Señal débil ({fuerza} pts). Esperando...")
            
        time.sleep(60)

# ---------------------- INICIO DEL BOT ----------------------
if __name__ == "__main__":
    print("=====================================")
    print("🚀 INICIANDO BOT DOLA - MODO SEGURO")
    print("=====================================")
    
    # ✅ MENSAJE DE INICIO A TELEGRAM
    enviar_mensaje_telegram("🤖 **BOT DOLA INICIADO** 🚀\nModo Seguridad Activado | Operando de 06:00 AM a 20:00 PM")
    
    ejecutar_trading()
