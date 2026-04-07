import numpy as np
import os
import json

# =========================
# SISTEMA DE MEMORIA
# =========================
ARCHIVO_MEMORIA = "memoria.json"

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, 'r') as f:
            return json.load(f)
    return {"stats": {"ganadas": 0, "perdidas": 0}, "config": {"rsi_min_compra": 45, "rsi_max_venta": 55, "fuerza_minima": 0.0005}}

def guardar_memoria(datos):
    with open(ARCHIVO_MEMORIA, 'w') as f:
        json.dump(datos, f, indent=2)

def aprender_resultado(resultado, analisis):
    memoria = cargar_memoria()
    if resultado > 0:
        memoria["stats"]["ganadas"] += 1
        print("🧠 ✅ APRENDIZAJE: Estrategia buena")
    else:
        memoria["stats"]["perdidas"] += 1
        print("🧠 ❌ APRENDIZAJE: Ajustando...")
        if analisis["tipo"] == "call":
            memoria["config"]["rsi_min_compra"] -= 2
        else:
            memoria["config"]["rsi_max_venta"] += 2
            
    # Limites para no romperse
    memoria["config"]["rsi_min_compra"] = max(20, memoria["config"]["rsi_min_compra"])
    memoria["config"]["rsi_max_venta"] = min(80, memoria["config"]["rsi_max_venta"])
    guardar_memoria(memoria)

# =========================
# INDICADORES
# =========================
def calcular_ema(precios, periodo=14):
    precios = np.array(precios)
    if len(precios) < periodo:
        return precios[-1]
    ema = precios[0]
    k = 2 / (periodo + 1)
    for precio in precios:
        ema = precio * k + ema * (1 - k)
    return ema

def calcular_rsi(precios, periodo=14):
    precios = np.array(precios)
    if len(precios) < periodo + 1:
        return 50
    deltas = np.diff(precios)
    ganancias = np.where(deltas > 0, deltas, 0)
    perdidas = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(ganancias[-periodo:])
    avg_loss = np.mean(perdidas[-periodo:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_bandas(precios, periodo=20):
    media = np.mean(precios[-periodo:])
    desviacion = np.std(precios[-periodo:])
    banda_sup = media + (desviacion * 2)
    banda_inf = media - (desviacion * 2)
    return banda_sup, media, banda_inf

# =========================
# ANÁLISIS PRINCIPAL
# =========================
def analizar_mercado(par, velas):
    memoria = cargar_memoria()
    config = memoria["config"]
    
    closes = [float(v["close"]) for v in velas]
    if len(closes) < 30:
        return 0, None, {}

    ema9 = calcular_ema(closes, 9)
    ema21 = calcular_ema(closes, 21)
    rsi = calcular_rsi(closes, 14)
    banda_sup, banda_med, banda_inf = calcular_bandas(closes)

    precio = closes[-1]
    score = 0
    tipo = None

    # 1. TENDENCIA (MÁS FÁCIL DE ACTIVAR)
    if precio > ema9 and ema9 > ema21:
        score += 1
        tipo = "call"
    elif precio < ema9 and ema9 < ema21:
        score += 1
        tipo = "put"
    # Permitimos tendencia leve también
    elif precio > ema9 or precio > ema21:
        score += 0.5
        tipo = "call"
    elif precio < ema9 or precio < ema21:
        score += 0.5
        tipo = "put"
    else:
        return 0, None, {}

    # 2. RSI (MÁS FLEXIBLE)
    if tipo == "call" and rsi < config["rsi_min_compra"]:
        score +=1
    elif tipo == "put" and rsi > config["rsi_max_venta"]:
        score +=1

    # 3. UBICACIÓN
    if (tipo == "call" and precio < banda_med) or (tipo == "put" and precio > banda_med):
        score +=1

    datos_analisis = {"tipo": tipo, "rsi": rsi, "score": score}
    return score, tipo, datos_analisis

# =========================
# CONFIANZA
# =========================
def calcular_confianza(score):
    if score >= 2.5:
        return 90
    elif score >= 1.5:
        return 75
    else:
        return 0

def decision_final(tipo, score, confianza):
    if score >= 1.5 and confianza >= 70:
        return tipo
    return None
