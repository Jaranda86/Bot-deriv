id="ia_pro_v1"
import numpy as np

# =========================
# EMA
# =========================
def calcular_ema(precios, periodo=14):
    precios = np.array(precios)

    if len(precios) < periodo:
        return precios[-1]

    ema = precios[0]
    k = 2 / (periodo + 1)

    for precio in precios:
        ema = precio * k + ema * (1 - k)

    return ema


# =========================
# RSI
# =========================
def calcular_rsi(precios, periodo=14):
    precios = np.array(precios)

    if len(precios) < periodo + 1:
        return 50

    deltas = np.diff(precios)

    ganancias = np.where(deltas > 0, deltas, 0)
    perdidas = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(ganancias[-periodo:])
    avg_loss = np.mean(perdidas[-periodo:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================
# ANÁLISIS DE MERCADO
# =========================
def analizar_mercado(par, velas):

    closes = [float(v["close"]) for v in velas]

    if len(closes) < 20:
        return 0, None

    # Indicadores
    ema_rapida = calcular_ema(closes, 9)
    ema_lenta = calcular_ema(closes, 21)
    rsi = calcular_rsi(closes, 14)

    precio_actual = closes[-1]

    score = 0
    tipo = None

    # =========================
    # LÓGICA EMA
    # =========================
    if ema_rapida > ema_lenta and precio_actual > ema_rapida:
        score += 1
        tipo = "call"

    elif ema_rapida < ema_lenta and precio_actual < ema_rapida:
        score += 1
        tipo = "put"

    # =========================
    # LÓGICA RSI
    # =========================
    if rsi < 30:
        score += 1
        tipo = "call"

    elif rsi > 70:
        score += 1
        tipo = "put"

    # =========================
    # CONFIRMACIÓN FUERZA
    # =========================
    tendencia = closes[-1] - closes[-5]

    if tendencia > 0:
        score += 1
        tipo = "call"
    elif tendencia < 0:
        score += 1
        tipo = "put"

    return score, tipo


# =========================
# CONFIANZA IA
# =========================
def calcular_confianza(score):

    if score == 3:
        return 90
    elif score == 2:
        return 75
    elif score == 1:
        return 60
    else:
        return 0


# =========================
# DECISIÓN FINAL
# =========================
def decision_final(tipo, score, confianza):

    # 🔥 filtro PRO (evita malas entradas)
    if score < 2:
        return None

    if confianza < 70:
        return None

    return tipo
