def calcular_rsi(cierres, periodo=14):
    ganancias = []
    perdidas = []

    for i in range(1, len(cierres)):
        cambio = cierres[i] - cierres[i-1]
        if cambio > 0:
            ganancias.append(cambio)
        else:
            perdidas.append(abs(cambio))

    if not ganancias or not perdidas:
        return 50

    avg_gain = sum(ganancias[-periodo:]) / periodo
    avg_loss = sum(perdidas[-periodo:]) / periodo

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calcular_ema(cierres, periodo=10):
    ema = cierres[0]
    k = 2 / (periodo + 1)

    for precio in cierres:
        ema = precio * k + ema * (1 - k)

    return ema
