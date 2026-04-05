import json
import os
from indicadores import calcular_rsi, calcular_ema

ARCHIVO = "historial_ia.json"


def cargar_historial():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO, "r") as f:
        return json.load(f)


def guardar_historial(data):
    with open(ARCHIVO, "w") as f:
        json.dump(data, f)


# =========================
def analizar_mercado(par, bot):
    velas = bot.get_candles(par)

    if len(velas) < 30:
        return 0, None

    closes = [v["close"] for v in velas]

    rsi = calcular_rsi(closes)
    ema = calcular_ema(closes)

    score = 0
    tipo = None

    precio_actual = closes[-1]

    # =========================
    # 📈 TENDENCIA EMA
    if precio_actual > ema:
        score += 2
        tipo = "call"
    else:
        score -= 2
        tipo = "put"

    # =========================
    # 🔥 RSI
    if rsi < 30:
        score += 2
        tipo = "call"
    elif rsi > 70:
        score += 2
        tipo = "put"

    # =========================
    # ⚡ MOMENTUM
    if closes[-1] > closes[-2]:
        score += 1
    else:
        score -= 1

    # =========================
    # 🚫 FILTRO MERCADO LATERAL
    rango = max(closes[-10:]) - min(closes[-10:])
    if rango < 0.5:
        return 0, None

    return score, tipo


# =========================
def calcular_confianza(score):
    historial = cargar_historial()

    if not historial:
        return 60

    wins = sum(1 for x in historial if x["resultado"] == "win")
    total = len(historial)

    tasa = (wins / total) * 100

    confianza = int((abs(score) * 20) + (tasa * 0.6))

    return min(confianza, 99)


# =========================
def decision_final(tipo, score, confianza):

    if score < 3:
        return None

    if confianza < 70:
        return None

    return tipo


# =========================
def guardar_resultado(par, tipo, resultado):
    historial = cargar_historial()

    historial.append({
        "par": par,
        "tipo": tipo,
        "resultado": "win" if resultado > 0 else "loss"
    })

    historial = historial[-300:]

    guardar_historial(historial)
