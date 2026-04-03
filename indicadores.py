import random

# ==============================
# 📊 ANALIZAR MERCADO
# ==============================

def analizar_mercado(bot, par):

    # 🔥 Simulación de indicadores (después lo mejoramos con datos reales)

    puntuacion = 0

    # simulación de señales
    dir_vela = random.choice([-1, 1])
    bb_pos = random.random()
    stoch_k = random.randint(0, 100)
    ema_tend = random.choice([-1, 1])

    # ==============================
    # 🧠 LÓGICA
    # ==============================

    if dir_vela == 1:
        puntuacion += 1
    else:
        puntuacion -= 1

    if bb_pos < 0.2:
        puntuacion += 1
    elif bb_pos > 0.8:
        puntuacion -= 1

    if stoch_k < 20:
        puntuacion += 1
    elif stoch_k > 80:
        puntuacion -= 1

    if ema_tend == 1:
        puntuacion += 1
    else:
        puntuacion -= 1

    # ==============================
    # 🎯 DECISIÓN
    # ==============================

    if puntuacion >= 3:
        return "call", puntuacion

    elif puntuacion <= -3:
        return "put", puntuacion

    else:
        return None, puntuacion
