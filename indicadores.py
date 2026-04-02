def analizar_indicadores(velas):
    puntuacion = 0

    # 🔧 VALORES SIMULADOS (ajústalos si ya los calculas)
    dir_vela = velas.get("dir_vela", 0)
    bb_pos = velas.get("bb_pos", 0.5)
    stoch_k = velas.get("stoch_k", 50)
    ema_tend = velas.get("ema_tend", 0)

    if dir_vela == 1:
        puntuacion += 1
    elif dir_vela == -1:
        puntuacion -= 1

    if bb_pos < 0.1:
        puntuacion += 1
    elif bb_pos > 0.9:
        puntuacion -= 1

    if stoch_k < 20:
        puntuacion += 1
    elif stoch_k > 80:
        puntuacion -= 1

    if ema_tend == 1:
        puntuacion += 1
    elif ema_tend == -1:
        puntuacion -= 1

    if abs(puntuacion) < 3:
        return None, puntuacion, []

    if puntuacion > 0 and ema_tend < 0:
        return None, puntuacion, []

    if puntuacion < 0 and ema_tend > 0:
        return None, puntuacion, []

    return ("call" if puntuacion > 0 else "put"), puntuacion, []


def decision_final(puntuacion):
    if puntuacion > 0:
        return "call", puntuacion
    elif puntuacion < 0:
        return "put", puntuacion
    else:
        return None, puntuacion
