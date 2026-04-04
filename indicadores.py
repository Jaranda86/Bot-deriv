import random

def analizar_mercado(bot, par):
    puntuacion = 0

    # simulación inteligente (base IA simple)
    dir_vela = random.choice([-1, 1])
    bb_pos = random.random()
    stoch_k = random.randint(0, 100)
    ema_tend = random.choice([-1, 1])

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

    if abs(puntuacion) < 3:
        return None, puntuacion

    if puntuacion > 0:
        return "CALL", puntuacion
    else:
        return "PUT", puntuacion
