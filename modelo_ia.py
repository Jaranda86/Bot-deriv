import random

# =========================
# 📊 ANALISIS MERCADO
# =========================

def analizar_mercado(par, bot):
    try:
        velas = bot.get_candles(par)

        if not velas or len(velas) < 10:
            return 0, None

        cierres = [v["close"] for v in velas]

        # tendencia simple
        if cierres[-1] > cierres[-2] > cierres[-3]:
            return 3, "call"

        if cierres[-1] < cierres[-2] < cierres[-3]:
            return 3, "put"

        return 1, None

    except Exception as e:
        print("Error analizar:", e)
        return 0, None


# =========================
# 🧠 CONFIANZA IA
# =========================

def calcular_confianza(par, score):
    try:
        if score >= 3:
            return random.randint(70, 100)
        elif score == 2:
            return random.randint(50, 70)
        else:
            return random.randint(0, 50)
    except:
        return 0


# =========================
# 🎯 DECISION FINAL
# =========================

def decision_final(tipo, score, confianza):
    if tipo is None:
        return None

    if score >= 3 and confianza >= 60:
        return tipo

    return None


# =========================
# 🧪 DEBUG IA
# =========================

def debug_ia(par, score, confianza):
    print(f"IA → {par} | score: {score} | confianza: {confianza}%")
