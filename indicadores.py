import numpy as np


# =========================
# 📊 RSI
# =========================
def calcular_rsi(cierres, periodo=14):
    deltas = np.diff(cierres)
    ganancias = deltas.clip(min=0)
    perdidas = -deltas.clip(max=0)

    media_ganancias = np.mean(ganancias[-periodo:])
    media_perdidas = np.mean(perdidas[-periodo:])

    if media_perdidas == 0:
        return 100

    rs = media_ganancias / media_perdidas
    return 100 - (100 / (1 + rs))


# =========================
# 📊 EMA
# =========================
def calcular_ema(cierres, periodo=10):
    return np.mean(cierres[-periodo:])


# =========================
# 🧠 ANALIZAR MERCADO REAL
# =========================
def analizar_mercado(par, bot):

    velas = bot.get_candles(par)

    if not velas:
        return 0, None

    cierres = [vela["close"] for vela in velas]

    rsi = calcular_rsi(cierres)
    ema = calcular_ema(cierres)

    ultimo_precio = cierres[-1]

    score = 0
    tipo = None

    # 🔹 RSI
    if rsi < 30:
        score += 2
        tipo = "call"
    elif rsi > 70:
        score -= 2
        tipo = "put"

    # 🔹 EMA
    if ultimo_precio > ema:
        score += 1
    else:
        score -= 1

    print(f"📊 RSI: {rsi:.2f} | EMA: {ema:.2f}")

    return score, tipo
