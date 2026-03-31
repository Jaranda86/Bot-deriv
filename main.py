import time
import threading

from deriv_api import DerivBot
from indicadores import *
from modelo_ia import ModeloIA

# ===== CONFIG =====
TIEMPO = 2
MONTO_BASE = 10

CONFIANZA_MINIMA_IA = 0.75
MAX_OPERACIONES_SIMULTANEAS = 1

# ===== CONTROL RIESGO =====
MAX_PERDIDAS_CONSECUTIVAS = 3
PAUSA_TRAS_PERDIDAS = 300  # segundos (5 min)

# ===== IA =====
modelo_ia = ModeloIA()

# ===== ESTADO =====
operaciones_activas = {}
lock = threading.Lock()

perdidas_consecutivas = 0
modo_defensa = False
tiempo_pausa = 0


# ===== FUNCIONES =====

def contar_operaciones():
    with lock:
        return sum(1 for op in operaciones_activas.values() if op)


def obtener_monto():
    global modo_defensa
    if modo_defensa:
        return MONTO_BASE * 0.5
    return MONTO_BASE


def filtro_multi_timeframe(cierres):
    # tendencia mayor simulada (últimas 20 velas)
    media_corta = sum(cierres[-5:]) / 5
    media_larga = sum(cierres[-20:]) / 20

    if media_corta > media_larga:
        return 1
    elif media_corta < media_larga:
        return -1
    return 0


def analizar_par(bot, par):
    global modo_defensa, tiempo_pausa

    try:
        # ===== PAUSA POR RIESGO =====
        if modo_defensa and time.time() < tiempo_pausa:
            return

        velas_raw = bot.get_candles(par, 60, 50)
        if not velas_raw:
            return

        velas = [{
            "open": float(v["open"]),
            "close": float(v["close"]),
            "max": float(v["high"]),
            "min": float(v["low"]),
        } for v in velas_raw]

        cierres = [v["close"] for v in velas]

        # ===== INDICADORES =====
        rsi = calcular_rsi(cierres)
        macd, senal_macd, hist = calcular_macd(cierres)
        bb_sup, bb_inf, bb_med, bb_pos = calcular_bollinger(cierres)
        stoch_k, stoch_d = calcular_estocastico(velas)
        _, ema_tend, ema_diff = calcular_ema_crossover(cierres)
        patron, dir_vela = analizar_velas(velas)

        tendencia_mayor = filtro_multi_timeframe(cierres)

        decision, score, _ = obtener_senal(
            rsi, macd, senal_macd, hist,
            dir_vela, bb_pos, stoch_k, stoch_d, 0, ema_tend
        )

        # ===== FILTROS HEDGE FUND =====

        if decision is None or abs(score) < 4:
            return

        # tendencia mayor obligatoria
        if decision == "call" and tendencia_mayor < 0:
            return
        if decision == "put" and tendencia_mayor > 0:
            return

        # tendencia local
        if abs(ema_diff) < 0.0001:
            return

        if (decision == "call" and ema_tend < 0) or (decision == "put" and ema_tend > 0):
            return

        # RSI extremo obligatorio
        if not (rsi < 30 or rsi > 70):
            return

        # evitar sobrecompra lateral
        if 45 < rsi < 55:
            return

        # ===== IA =====
        features = modelo_ia.construir_features(
            rsi, macd, senal_macd, hist,
            dir_vela, score,
            bb_pos, stoch_k, stoch_d,
            ema_tend, ema_diff
        )

        confianza = modelo_ia.predecir_confianza(features)

        if confianza is None or confianza < CONFIANZA_MINIMA_IA:
            return

        # ===== CONTROL =====
        if contar_operaciones() >= MAX_OPERACIONES_SIMULTANEAS:
            return

        with lock:
            if operaciones_activas.get(par):
                return

        monto = obtener_monto()

        result = bot.buy(par, monto, decision, TIEMPO, "m")
        if not result:
            return

        contract_id = result["contract_id"]

        with lock:
            operaciones_activas[par] = True

        print(f"[{par}] 🚀 {decision.upper()} | IA:{confianza:.2f} | Modo:{'DEFENSA' if modo_defensa else 'NORMAL'}")

        t = threading.Thread(
            target=verificar_resultado,
            args=(bot, contract_id, par, features),
            daemon=True
        )
        t.start()

    except Exception as e:
        print(f"[{par}] Error: {e}")


def verificar_resultado(bot, contract_id, par, features):
    global perdidas_consecutivas, modo_defensa, tiempo_pausa

    time.sleep(TIEMPO * 60 + 5)

    result = bot.check_result(contract_id)

    if not result:
        with lock:
            operaciones_activas[par] = None
        return

    gano = result["won"]
    profit = result["profit"]

    modelo_ia.registrar_resultado(features, gano)

    if gano:
        perdidas_consecutivas = 0
        modo_defensa = False
        estado = "✅ GANADA"
    else:
        perdidas_consecutivas += 1
        estado = "❌ PERDIDA"

    # activar defensa
    if perdidas_consecutivas >= MAX_PERDIDAS_CONSECUTIVAS:
        modo_defensa = True
        tiempo_pausa = time.time() + PAUSA_TRAS_PERDIDAS
        print("🛑 MODO DEFENSA ACTIVADO")

    print(f"[{par}] {estado} | {profit}")

    with lock:
        operaciones_activas[par] = None


# ===== BOT =====

def bot():
    bot = DerivBot()

    if not bot.connect():
        print("❌ Error conexión")
        return

    print("🏦 BOT HEDGE FUND INICIADO")

    pares = ["R_100", "R_50", "R_75"]

    while True:
        for par in pares:
            analizar_par(bot, par)

        time.sleep(10)


if __name__ == "__main__":
    bot()
