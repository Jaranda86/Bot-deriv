import time
import os
import requests
import asyncio
from deriv_api import DerivAPI  # <- Usamos la librería OFICIAL
from ia_pro_v1 import analizar_mercado, calcular_confianza, decision_final

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
MONTO = 10      # Monto base
DURACION = 60      # Duración en segundos
LIMITE_PERDIDA = -50

# Variables de control
martingala = 1
racha_perdidas = 0
perdidas_dia = 0

# =========================
# CONEXIÓN DERIV API
# =========================
# ⚠️ CAMBIA ESTE NÚMERO POR TU APP ID REAL
APP_ID = "80108879"
API_TOKEN = os.getenv("DERIV_TOKEN")

async def conectar():
    api = DerivAPI(app_id=APP_ID)
    await api.authorize(API_TOKEN)
    print("✅ Conectado exitosamente a Deriv")
    return api

# =========================
# FUNCIONES AUXILIARES
# =========================
async def get_velas(api, simbolo, cantidad=30):
    """Obtiene historial de velas"""
    respuesta = await api.ticks_history({
        "ticks_history": simbolo,
        "adjust_start_time": 1,
        "count": cantidad,
        "end": "latest",
        "granularity": DURACION,
        "style": "candles"
    })
    return respuesta['candles']

async def ejecutar_operacion(api, simbolo, tipo, monto):
    """Ejecuta compra o venta"""
    parametros = {
        "buy": 1,
        "parameters": {
            "amount": monto,
            "basis": "stake",
            "contract_type": tipo,
            "currency": "USD",
            "duration": DURACION,
            "duration_unit": "s",
            "symbol": simbolo
        }
    }
    resultado = await api.buy(parametros)
    return resultado.get('buy', {}).get('contract_id')

async def ver_resultado(api, contract_id):
    """Espera y verifica ganancia/perdida"""
    await asyncio.sleep(DURACION + 2)  # Esperar a que cierre el contrato
    datos = await api.proposal_open_contract({"contract_id": contract_id})
    return float(datos['proposal_open_contract']['profit'])

# =========================
# BUCLE PRINCIPAL
# =========================
async def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia

    print("🔥 INICIANDO SISTEMA IA PRO V1...")
    enviar_telegram("🤖 BOT IA PRO V1 - SISTEMA ACTIVO")

    bot = DerivBot()
if not bot.conectar():
    print("❌ No conectó")
    continue
    

    while True:
        try:
            for par in pares:
                print(f"\n📊 Analizando {par}...")

                # 1. Obtener datos del mercado
                velas = await get_velas(api, par, cantidad=30)
                
                if len(velas) < 20:
                    print("⚠️ Pocos datos, saltando par...")
                    continue

                # 2. ANÁLISIS DE TU INTELIGENCIA ARTIFICIAL
                score, tipo_señal = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                decision = decision_final(tipo_señal, score, confianza)

                print(f"📈 Score: {score} | Confianza: {confianza}% | Señal: {decision}")

                # 3. FILTRO DE ENTRADA
                if not decision:
                    print("⏭️  Señal débil o nula, no entramos.")
                    continue

                # 4. EJECUTAR OPERACIÓN
                monto_real = MONTO * martingala
                enviar_telegram(f"🚀 {par} | {decision.upper()} | Confianza: {confianza}% | Monto: {monto_real} USD")

                contract_id = await ejecutar_operacion(api, par, decision, monto_real)

                if not contract_id:
                    print("❌ Falló la ejecución de la orden")
                    continue

                # 5. ESPERAR CIERRE Y VER RESULTADO
                profit = await ver_resultado(api, contract_id)

                # 6. GESTIÓN DE CAPITAL (MARTINGALA)
                if profit > 0:
                    enviar_telegram(f"✅ GANADA | +{profit} USD")
                    martingala = 1
                    racha_perdidas = 0
                else:
                    enviar_telegram(f"❌ PERDIDA | {profit} USD")
                    martingala *= 2
                    racha_perdidas += 1
                    perdidas_dia += profit

                # 7. CONTROL DE RIESGO TOTAL
                if perdidas_dia <= LIMITE_PERDIDA:
                    enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO. BOT DETENIDO.")
                    print("🛑 Stop total por seguridad.")
                    return

                await asyncio.sleep(3)  # Pausa corta entre análisis

        except Exception as e:
            print("❌ ERROR CRÍTICO:", e)
            enviar_telegram(f"⚠️ ERROR EN EL SISTEMA: {e}")
            await asyncio.sleep(10)  # Esperar antes de reintentar

# =========================
# ARRANCAR PROGRAMA
# =========================
if __name__ == "__main__":
    try:
        asyncio.run(ejecutar_bot())
    except KeyboardInterrupt:
        print("👋 Bot detenido por el usuario")
