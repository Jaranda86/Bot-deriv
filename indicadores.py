import numpy as np

# =========================
# 📊 ANALIZAR MERCADO
# =========================
def analizar_mercado(par, bot=None):
    try:
        # 🔥 usamos velas reales
        if bot:
            velas = bot.get_candles(par)
        else:
            return 0, None

        if not velas or len(velas) < 20:
            return 0, None

        closes = [float(v["close"]) for v in velas]

        score = 0
        tipo = None

        # =========================
        # 📈 RSI SIMPLE
        # =========================
        ganancias = []
        perdidas = []

        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                ganancias.append(diff)
            else:
                perdidas.append(abs(diff))

        avg_gain = np.mean(ganancias) if ganancias else 0
        avg_loss = np.mean(perdidas) if perdidas else 0

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        if rsi < 30:
            score += 2
            tipo = "call"
        elif rsi > 70:
            score += 2
            tipo = "put"

        # =========================
        # 📊 TENDENCIA (EMA)
        # =========================
        ema = np.mean(closes[-10:])
        precio_actual = closes[-1]

        if precio_actual > ema:
            score += 1
            if tipo is None:
                tipo = "call"
        else:
            score += 1
            if tipo is None:
                tipo = "put"

        # =========================
        # 🔥 MOMENTUM
        # =========================
        if closes[-1] > closes[-3]:
            score += 1
        else:
            score -= 1

        # =========================
        # 🚫 FILTRO MERCADO BASURA
        # =========================
        volatilidad = np.std(closes[-10:])

        if volatilidad < 0.1:
            return 0, None

        return score, tipo

    except Exception as e:
        print("❌ Error análisis:", e)
        return 0, None
