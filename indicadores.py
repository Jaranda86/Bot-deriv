import numpy as np

# =========================
# 📊 RSI
# =========================
def calcular_rsi(cierres, periodo=14):
    if len(cierres) < periodo + 1:
        return 50

    deltas = np.diff(cierres)
    subidas = deltas.clip(min=0)
    bajadas = -deltas.clip(max=0)

    media_subidas = np.mean(subidas[-periodo:])
    media_bajadas = np.mean(bajadas[-periodo:])

    if media_bajadas == 0:
        return 100

    rs = media_subidas / media_bajadas
    return 100 - (100 / (1 + rs))


# =========================
# 📊 EMA
# =========================
def calcular_ema(datos, periodo):
    k = 2 / (periodo + 1)
    ema = [datos[0]]

    for precio in datos[1:]:
        ema.append(precio * k + ema[-1] * (1 - k))

    return np.array(ema)


# =========================
# 📊 MACD
# =========================
def calcular_macd(cierres):
    ema12 = calcular_ema(cierres, 12)
    ema26 = calcular_ema(cierres, 26)

    macd = ema12 - ema26
    signal = calcular_ema(macd, 9)

    return macd[-1], signal[-1]


# =========================
# 🔥 ANALISIS REAL
# =========================
def analizar_mercado(bot, par):
    velas = bot.get_candles(par)

    if not velas or len(velas) < 30:
        return 0, None

    cierres = [v["close"] for v in velas]

    rsi = calcular_rsi(cierres)
    macd, signal = calcular_macd(cierres)

    ema9 = calcular_ema(cierres, 9)
    ema21 = calcular_ema(cierres, 21)

    score = 0

    # RSI
    if rsi < 30:
        score += 1
    elif rsi > 70:
        score -= 1

    # MACD
    if macd > signal:
        score += 1
    else:
        score -= 1

    # EMA tendencia
    if ema9[-1] > ema21[-1]:
        score += 1
    else:
        score -= 1

    # DECISIÓN
    if score >= 2:
        return score, "call"
    elif score <= -2:
        return score, "put"
    else:
        return score, None
