import numpy as np
import os
import json
from datetime import datetime

# =========================
# SISTEMA DE MEMORIA
# =========================
ARCHIVO_MEMORIA = "memoria.json"
HISTORIAL_FILE = "historial_operaciones.json"

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, 'r') as f:
            return json.load(f)
    return {"stats": {"ganadas": 0, "perdidas": 0}, "config": {"rsi_min_compra": 35, "rsi_max_venta": 65, "fuerza_minima": 20}}

def guardar_memoria(datos):
    with open(ARCHIVO_MEMORIA, 'w') as f:
        json.dump(datos, f, indent=2)

def guardar_historial(par, tipo, profit, score):
    try:
        historial = []
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, 'r') as f:
                historial = json.load(f)
        
        nueva = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "par": par,
            "tipo": tipo,
            "profit": profit,
            "score": score
        }
        historial.append(nueva)
        
        if len(historial) > 1000:
            historial = historial[-1000:]
            
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(historial, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error guardando historial: {e}")

# =========================
# INDICADORES TÉCNICOS
# =========================
def calcular_ema(precios, periodo):
    precios = np.array(precios)
    if len(precios) < periodo:
        return precios[-1] if len(precios) > 0 else 0
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
    return 100 - (100 / (1 + rs))

def calcular_bandas(precios, periodo=20):
    media = np.mean(precios[-periodo:])
    desviacion = np.std(precios[-periodo:])
    return media + (desviacion * 2), media, media - (desviacion * 2)

def calcular_macd(precios):
    ema12 = calcular_ema(precios, 12)
    ema26 = calcular_ema(precios, 26)
    macd_line = ema12 - ema26
    signal = calcular_ema(np.array([macd_line]), 9)
    return macd_line, signal

def calcular_stochastic(precios, alto, bajo, periodo=14):
    if len(precios) < periodo:
        return 50
    ultimo_precio = precios[-1]
    minimo = np.min(precios[-periodo:])
    maximo = np.max(precios[-periodo:])
    if maximo == minimo:
        return 50
    return ((ultimo_precio - minimo) / (maximo - minimo)) * 100

def calcular_adx(precios, alto, bajo, periodo=14):
    if len(precios) < periodo + 1:
        return 20
    tr = []
    plus_dm = []
    minus_dm = []
    for i in range(1, len(precios)):
        tr_val = max(abs(alto[i]-alto[i-1]), abs(bajo[i]-bajo[i-1]), abs(precios[i]-precios[i-1]))
        tr.append(tr_val)
        up = alto[i] - alto[i-1]
        down = bajo[i-1] - bajo[i]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
    
    atr = np.mean(tr[-periodo:])
    plus_di = 100 * (np.mean(plus_dm[-periodo:]) / atr) if atr > 0 else 0
    minus_di = 100 * (np.mean(minus_dm[-periodo:]) / atr) if atr > 0 else 0
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
    adx = np.mean([dx]*periodo)
    return adx

# =========================
# ANÁLISIS PRINCIPAL
# =========================
def analizar_mercado(par, velas):
    memoria = cargar_memoria()
    config = memoria["config"]
    
    closes = [float(v["close"]) for v in velas]
    highs = [float(v["high"]) for v in velas]
    lows = [float(v["low"]) for v in velas]
    
    if len(closes) < 30:
        return 0, None, {}

    # CALCULAR INDICADORES
    ema9 = calcular_ema(closes, 9)
    ema21 = calcular_ema(closes, 21)
    rsi = calcular_rsi(closes)
    banda_sup, banda_med, banda_inf = calcular_bandas(closes)
    macd_line, signal = calcular_macd(closes)
    stoch = calcular_stochastic(closes, highs, lows)
    adx = calcular_adx(closes, highs, lows)

    precio = closes[-1]
    score = 0
    tipo = None

    # ==================================
    # 1. TENDENCIA Y FUERZA (ADX)
    # ==================================
    # 🔽 BAJÉ EL LÍMITE DE 25 A 20 PARA QUE ENTRE MÁS
    if adx > config["fuerza_minima"]:
        score += 1
        if precio > ema9 and ema9 > ema21:
            score += 2
            tipo = "call"
        elif precio < ema9 and ema9 < ema21:
            score += 2
            tipo = "put"
        elif precio > ema9 or precio > ema21:
            score += 1
            tipo = "call"
        elif precio < ema9 or precio < ema21:
            score += 1
            tipo = "put"
        else:
            print(f"📉 Tendencia neutra")
            return 0, None, {}
    else:
        print(f"📉 ADX bajo ({round(adx,1)}) - Sin tendencia clara")
        return 0, None, {}

    # ==================================
    # 2. RSI
    # ==================================
    if tipo == "call" and rsi < config["rsi_min_compra"]:
        score +=1
    elif tipo == "put" and rsi > config["rsi_max_venta"]:
        score +=1

    # ==================================
    # 3. BANDAS DE BOLLINGER
    # ==================================
    if (tipo == "call" and precio < banda_med) or (tipo == "put" and precio > banda_med):
        score +=1

    # ==================================
    # 4. MACD
    # ==================================
    if tipo == "call" and macd_line > signal:
        score +=1
    elif tipo == "put" and macd_line < signal:
        score +=1

    # ==================================
    # 5. STOCHASTIC
    # ==================================
    if tipo == "call" and stoch < 50:  # 🔽 ANTES ERA 40, AHORA 50
        score +=1
    elif tipo == "put" and stoch > 50: # 🔽 ANTES ERA 60, AHORA 50
        score +=1

    datos_analisis = {
        "tipo": tipo,
        "rsi": round(rsi,2),
        "adx": round(adx,2),
        "macd": round(macd_line,4),
        "stoch": round(stoch,2),
        "score": score
    }
    
    print(f"📊 INDICADORES: RSI={datos_analisis['rsi']} | ADX={datos_analisis['adx']} | STOCH={datos_analisis['stoch']} | SCORE={score}")

    return score, tipo, datos_analisis

# =========================
# CONFIANZA Y DECISIÓN
# =========================
def calcular_confianza(score):
    if score >= 6:
        return 90
    elif score >= 4:
        return 80
    elif score >= 3:  # 🔽 ANTES ERA 4, AHORA 3
        return 70
    else:
        return 0

def decision_final(tipo, score, confianza):
    if score >= 3 and confianza >= 70:  # 🔽 BAJÉ LA EXIGENCIA
        return tipo
    return None

def aprender_resultado(profit, analisis):
    memoria = cargar_memoria()
    par = analisis.get("par", "DESCONOCIDO")
    
    guardar_historial(par, analisis['tipo'], profit, analisis['score'])
    
    if profit > 0:
        memoria["stats"]["ganadas"] += 1
        print(f"🧠 ✅ APRENDIZAJE: Estrategia buena | Score: {analisis['score']}")
    else:
        memoria["stats"]["perdidas"] += 1
        print(f"🧠 ❌ APRENDIZAJE: Ajustando... | Score: {analisis['score']}")
        
        if analisis['tipo'] == "call":
            memoria["config"]["rsi_min_compra"] = max(30, memoria["config"]["rsi_min_compra"] - 1)
        else:
            memoria["config"]["rsi_max_venta"] = min(70, memoria["config"]["rsi_max_venta"] + 1)
            
    guardar_memoria(memoria)
