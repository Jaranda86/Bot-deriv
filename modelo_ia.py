# ==========================================
# 🤖 IA EXPERTA - AUTOAPRENDIZAJE + CONTROL
# ==========================================

import random

# 📊 historial global
historial = []

# ==============================
# 🧠 REGISTRAR RESULTADO
# ==============================
def registrar_resultado(resultado):
    try:
        if resultado in ["win", "loss"]:
            historial.append(resultado)

        # limitar historial
        if len(historial) > 100:
            historial.pop(0)

    except Exception as e:
        print("Error registrando:", e)


# ==============================
# 📊 CALCULAR WINRATE
# ==============================
def calcular_winrate():
    if len(historial) == 0:
        return 0.5

    wins = historial.count("win")
    return wins / len(historial)


# ==============================
# 🔥 DETECTAR RACHA
# ==============================
def detectar_racha_perdidas():
    racha = 0
    for r in reversed(historial):
        if r == "loss":
            racha += 1
        else:
            break
    return racha


# ==============================
# 🎯 CALCULAR CONFIANZA PRO
# ==============================
def calcular_confianza(score):
    try:
        base = (score / 5) * 100

        winrate = calcular_winrate()

        # 📈 ajuste por rendimiento
        if winrate > 0.65:
            base += 10
        elif winrate < 0.45:
            base -= 10

        # 🔥 penalización por racha
        racha = detectar_racha_perdidas()
        if racha >= 3:
            base -= 15

        # 🎯 ruido leve tipo IA
        base += random.uniform(-3, 3)

        return int(max(0, min(100, base)))

    except:
        return 50


# ==============================
# 🚫 BLOQUEO INTELIGENTE
# ==============================
def bloquear_operaciones():
    racha = detectar_racha_perdidas()
    winrate = calcular_winrate()

    # 🔥 condiciones de peligro
    if racha >= 4:
        return True

    if winrate < 0.35 and len(historial) > 10:
        return True

    return False


# ==============================
# 🧠 DECISIÓN FINAL EXPERTA
# ==============================
def decision_final(score, tipo):
    confianza = calcular_confianza(score)

    # 🚫 bloqueo total
    if bloquear_operaciones():
        return False, confianza, "bloqueado"

    # ❌ sin señal
    if tipo is None:
        return False, confianza, "sin señal"

    # 🔥 filtro fuerte
    if score >= 3 and confianza >= 60:
        return True, confianza, "operar"

    return False, confianza, "rechazada"


# ==============================
# 📊 ESTADÍSTICAS
# ==============================
def obtener_estadisticas():
    total = len(historial)
    wins = historial.count("win")
    losses = historial.count("loss")

    winrate = (wins / total * 100) if total > 0 else 0

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }
