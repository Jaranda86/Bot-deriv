import numpy as np


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


def calcular_ema(cierres, periodo=10):
    return np.mean(cierres[-periodo:])


def analizar_mercado(par, bot):
    velas = bot.get_candles(par)

    if not velas:
        return 0, None

    cierres = [v["close"] for v in velas]

    rsi = calcular_rsi(cierres)
    ema = calcular_ema(cierres)
    precio = cierres[-1]

    score = 0
    tipo = None

    # RSI
    if rsi < 30:
        score += 2
        tipo = "call"
    elif rsi > 70:
        score -= 2
        tipo = "put"

    # Tendencia EMA
    if precio > ema:
        score += 1
    else:
        score -= 1

    print(f"📊 {par} | RSI: {rsi:.2f} | EMA: {ema:.2f} | Precio: {precio}")

    return score, tipo
