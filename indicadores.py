import random

def analizar_mercado(par):
    """
    Analiza el mercado del par recibido
    """

    print(f"📊 Analizando mercado: {par}")

    # 🔹 Simulación (después lo mejoramos con velas reales)
    score = random.randint(-5, 5)

    if score >= 2:
        tipo = "call"
    elif score <= -2:
        tipo = "put"
    else:
        tipo = None

    return score, tipo
