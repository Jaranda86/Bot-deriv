import json
import os

archivo = "historial.json"

# =========================
# 📊 GUARDAR RESULTADO
# =========================
def guardar_resultado(par, score, resultado):
    data = []

    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            data = json.load(f)

    data.append({
        "par": par,
        "score": score,
        "resultado": resultado
    })

    with open(archivo, "w") as f:
        json.dump(data, f)


# =========================
# 🧠 APRENDIZAJE
# =========================
def ajustar_score(score):
    if not os.path.exists(archivo):
        return score

    with open(archivo, "r") as f:
        data = json.load(f)

    ultimos = data[-20:]

    wins = sum(1 for x in ultimos if x["resultado"] == "win")
    losses = sum(1 for x in ultimos if x["resultado"] == "loss")

    if losses > wins:
        score -= 1
    elif wins > losses:
        score += 1

    return score


# =========================
# 📊 ANALISIS (simple pero efectivo)
# =========================
def analizar_mercado(par, bot):
    velas = bot.get_candles(par)

    if len(velas) < 10:
        return 0, None

    cierres = [float(v["close"]) for v in velas]

    score = 0

    # tendencia simple
    if cierres[-1] > cierres[-2]:
        score += 1
    else:
        score -= 1

    if cierres[-2] > cierres[-3]:
        score += 1
    else:
        score -= 1

    # impulso
    if cierres[-1] > cierres[-5]:
        score += 1

    # IA aprendizaje
    score = ajustar_score(score)

    tipo = "call" if score > 0 else "put"

    return score, tipo


# =========================
# 📊 CONFIANZA
# =========================
def calcular_confianza(score):
    return min(max(score * 25, 0), 100)


# =========================
# 🎯 DECISION FINAL
# =========================
def decision_final(tipo, score, confianza):
    if score < 4:
        return None

    if confianza < 75:
        return None

    return tipo
