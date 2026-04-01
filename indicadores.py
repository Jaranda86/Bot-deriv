import numpy as np

def calcular_rsi(cierres, periodo=14):
    if len(cierres) < periodo + 1:
        return 50

    deltas = np.diff(cierres)
    subidas = deltas.clip(min=0)
    bajadas = -1 * deltas.clip(max=0)

    media_subidas = np.mean(subidas[-periodo:])
    media_bajadas = np.mean(bajadas[-periodo:])

    if media_bajadas == 0:
        return 100

    rs = media_subidas / media_bajadas
    return 100 - (100 / (1 + rs))


def calcular_ema(datos, periodo):
    k = 2 / (periodo + 1)
    ema_vals = [datos[0]]
    for precio in datos[1:]:
        ema_vals.append(precio * k + ema_vals[-1] * (1 - k))
    return np.array(ema_vals)


def calcular_macd(cierres, rapido=12, lento=26, senal=9):
    if len(cierres) < lento + senal:
        return 0, 0, 0

    ema_rapida = calcular_ema(cierres, rapido)
    ema_lenta = calcular_ema(cierres, lento)
    linea_macd = ema_rapida - ema_lenta
    linea_senal = calcular_ema(linea_macd, senal)
    histograma = linea_macd - linea_senal

    return linea_macd[-1], linea_senal[-1], histograma[-1]


def calcular_bollinger(cierres, periodo=20, desviaciones=2):
    if len(cierres) < periodo:
        return 0, 0, 0, 0

    datos = np.array(cierres[-periodo:])
    media = np.mean(datos)
    std = np.std(datos)

    banda_superior = media + desviaciones * std
    banda_inferior = media - desviaciones * std

    precio_actual = cierres[-1]
    posicion = (precio_actual - banda_inferior) / (banda_superior - banda_inferior)

    return banda_superior, banda_inferior, media, posicion


def calcular_estocastico(velas, periodo_k=14):
    if len(velas) < periodo_k:
        return 50, 50

    altos = [v["max"] for v in velas[-periodo_k:]]
    bajos = [v["min"] for v in velas[-periodo_k:]]
    cierre = velas[-1]["close"]

    maximo = max(altos)
    minimo = min(bajos)

    k = ((cierre - minimo) / (maximo - minimo)) * 100 if maximo != minimo else 50
    return k, k


def calcular_ema_crossover(cierres, rapida=9, lenta=21):
    if len(cierres) < lenta + 2:
        return 0, 0, 0

    ema_rapida = calcular_ema(cierres, rapida)
    ema_lenta = calcular_ema(cierres, lenta)

    diff = ema_rapida[-1] - ema_lenta[-1]

    tendencia = 1 if diff > 0 else -1 if diff < 0 else 0
    return 0, tendencia, diff


def analizar_velas(velas):
    actual = velas[-1]
    cuerpo = abs(actual["close"] - actual["open"])
    rango = actual["max"] - actual["min"]

    if rango == 0:
        return "neutral", 0

    ratio = cuerpo / rango

    if ratio < 0.3:
        return "debil", 0

    return ("alcista", 1) if actual["close"] > actual["open"] else ("bajista", -1)


def obtener_senal(rsi, macd, senal_macd, histograma, dir_vela,
                  bb_pos, stoch_k, stoch_d, ema_cruce, ema_tend):

    puntuacion = 0

    if rsi < 30:
        puntuacion += 1
    elif rsi > 70:
        puntuacion -= 1

    if macd > senal_macd:
        puntuacion += 1
    elif macd < senal_macd:
        puntuacion -= 1

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

    if abs(puntuacion) < 4:
        return None, puntuacion, []

    # filtro tendencia
    if puntuacion > 0 and ema_tend < 0:
        return None, puntuacion, []

    if puntuacion < 0 and ema_tend > 0:
        return None, puntuacion, []

    # ===== DECISIÓN FINAL =====
def decision_final(puntuacion):
    if puntuacion > 0:
        return "call", puntuacion
    elif puntuacion < 0:
        return "put", puntuacion
    else:
        return None, puntuacion
