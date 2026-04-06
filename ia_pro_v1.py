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
# BOLLINGER BANDS (NUEVO FILTRO)
# =========================
def calcular_bandas(precios, periodo=20):
    media = np.mean(precios[-periodo:])
    desviacion = np.std(precios[-periodo:])
    banda_sup = media + (desviacion * 2)
    banda_inf = media - (desviacion * 2)
    return banda_sup, media, banda_inf

# =========================
# ANÁLISIS DE MERCADO MEJORADO
# =========================
def analizar_mercado(par, velas):
    closes = [float(v["close"]) for v in velas]
    if len(closes) < 30:
        return 0, None

    # Indicadores
    ema_rapida = calcular_ema(closes, 9)
    ema_lenta = calcular_ema(closes, 21)
    rsi = calcular_rsi(closes, 14)
    banda_sup, banda_med, banda_inf = calcular_bandas(closes)

    precio_actual = closes[-1]
    precio_anterior = closes[-2]

    score = 0
    tipo = None

    # ==================================
    # 1. TENDENCIA FUERTE (EMA)
    # ==================================
    if ema_rapida > ema_lenta and precio_actual > ema_rapida:
        score += 1
        tipo = "call"
    elif ema_rapida < ema_lenta and precio_actual < ema_rapida:
        score += 1
        tipo = "put"
    else:
        # Si no hay tendencia clara, NO SUMAMOS PUNTOS
        return 0, None 

    # ==================================
    # 2. MOMENTO (RSI)
    # ==================================
    if tipo == "call" and rsi < 40:  # Compra solo si no está sobrecomprado
        score += 1
    elif tipo == "put" and rsi > 60:  # Venta solo si no está sobrevendido
        score += 1

    # ==================================
    # 3. UBICACIÓN EN PRECIO (BANDAS)
    # ==================================
    if tipo == "call" and precio_actual < banda_med:
        score += 1  # Bonus si busca compra abajo de la media
    elif tipo == "put" and precio_actual > banda_med:
        score += 1  # Bonus si busca venta arriba de la media

    return score, tipo

# =========================
# CONFIANZA IA
# =========================
def calcular_confianza(score):
    if score >= 3:
        return 95  # Muy alta confianza
    elif score == 2:
        return 80  # Alta confianza
    else:
        return 0   # No operar

# =========================
# DECISIÓN FINAL MÁS ESTRICTA
# =========================
def decision_final(tipo, score, confianza):
    # SOLO ENTRAR SI LA CONFIANZA ES MUY ALTA
    if score < 2 or confianza < 80:
        return None

    return tipo
