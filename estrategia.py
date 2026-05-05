def ema(data, period):
    k = 2 / (period + 1)
    e = data[0]
    for p in data:
        e = p * k + e * (1 - k)
    return e

def rsi(data, period=14):
    gains, losses = [], []

    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    if not gains or not losses:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def señal_con_ia(velas, ia):
    closes = [float(v["close"]) for v in velas]

    if len(closes) < 30:
        return None, 0

    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)
    precio = closes[-1]

    # 🔥 MÁS FLEXIBLE (ANTES ERA MUY ESTRICTO)
    señal = None

    if precio > e21 and r < 55:
        señal = "call"

    elif precio < e21 and r > 45:
        señal = "put"

    if not señal:
        return None, 0

    prob = ia.predecir(closes)
    print(f"🧠 IA: {prob}")

    if prob > 0.55:
        return señal, 70 + prob * 30

    return None, 0
