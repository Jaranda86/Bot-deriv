import time
import os
import requests
from deriv_api import DerivAPI
from modelo_ia import analizar_mercado, calcular_confianza, decision_final

# =========================
# TELEGRAM
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
# CONFIG
# =========================
pares = ["R_10", "R_25", "R_50"]
MONTO = 0.35  # Usar USD o la moneda de tu cuenta
duracion = 60  # segundos
unidad_duracion = "s"
martingala = 1
racha_perdidas = 0
perdidas_dia = 0
LIMITE_PERDIDA = -50

# =========================
# CONEXIÓN DERIV
# =========================
app_id = "1234"  # ⚠️ CAMBIA ESTO POR TU APP ID REAL (lo sacas en deriv.com)
api_token = os.getenv("DERIV_TOKEN")

async def conectar_deriv():
    api = DerivAPI(app_id=app_id)
    await api.authorize(api_token)
    return api

# =========================
# FUNCIONES AUXILIARES
# =========================
async def get_velas(api, symbol, count=20, interval=60):
    response = await api.ticks_history({
        "ticks_history": symbol,
        "adjust_start_time": 1,
        "count": count,
        "end": "latest",
        "granularity": interval,
        "style": "candles"
    })
    return response['candles']

async def comprar_operacion(api, symbol, tipo, monto):
    contrato = {
        "buy": 1,
        "parameters": {
            "amount": monto,
            "basis": "stake",
            "contract_type": tipo,
            "currency": "USD",
            "duration": duracion,
            "duration_unit": unidad_duracion,
            "symbol": symbol
        }
    }
    res = await api.buy(contrato)
    return res.get('buy', {}).get('contract_id', None)

async def check_resultado(api, contract_id):
    res = await api.proposal_open_contract({"contract_id": contract_id})
    profit = res['proposal_open_contract']['profit']
    return float(profit)

# =========================
# BOT PRINCIPAL
# =========================
async def ejecutar_bot():
    global martingala, racha_perdidas, perdidas_dia

    print("🔥 ARRANCANDO BOT...")
    enviar_telegram("🔥 BOT INICIADO")

    api = await conectar_deriv()

    while True:
        try:
            print("🔄 LOOP ACTIVO")

            for par in pares:
                print(f"📊 Analizando {par}")
                time.sleep(2)

                velas = await get_velas(api, par, count=30, interval=60)
                
                if len(velas) < 20:
                    print("❌ Pocos datos, salteando...")
                    continue

                score, tipo = analizar_mercado(par, velas)
                confianza = calcular_confianza(score)
                tipo = decision_final(tipo, score, confianza)

                print(f"{par} → {tipo} | IA {confianza}%")

                if tipo is None:
                    continue

                enviar_telegram(f"📊 {par} → {tipo.upper()} | IA {confianza}%")

                monto_actual = MONTO * martingala
                contract_id = await comprar_operacion(api, par, tipo, monto_actual)

                if not contract_id:
                    print("❌ No se pudo ejecutar la operación")
                    continue

                print("⏳ Esperando resultado...")
                time.sleep(duracion + 5)

                profit = await check_resultado(api, contract_id)

                if profit > 0:
                    enviar_telegram(f"✅ GANADA {par} | +{profit}")
                    martingala = 1
                    racha_perdidas = 0
                else:
                    enviar_telegram(f"❌ PERDIDA {par} | {profit}")
                    martingala *= 2
                    racha_perdidas += 1
                    perdidas_dia += profit

                # Control de pérdidas
                if perdidas_dia <= LIMITE_PERDIDA:
                    enviar_telegram("🛑 LÍMITE DE PÉRDIDA ALCANZADO. BOT DETENIDO.")
                    print("🛑 Bot detenido por límite de pérdida")
                    return

        except Exception as e:
            print("❌ ERROR GENERAL:", e)
            enviar_telegram(f"❌ ERROR BOT: {e}")
            time.sleep(10)

# =========================
# INICIO
# =========================
if __name__ == "__main__":
    import asyncio
    asyncio.run(ejecutar_bot())
