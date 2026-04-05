import csv
import os
import random

ARCHIVO = "historial.csv"

# =========================
# 📊 CREAR ARCHIVO SI NO EXISTE
# =========================
def inicializar_csv():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["par", "score", "resultado"])

# =========================
# 💾 GUARDAR OPERACIÓN
# =========================
def guardar_operacion(par, score, resultado):
    with open(ARCHIVO, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([par, score, resultado])

# =========================
# 🧠 IA QUE APRENDE
# =========================
def calcular_confianza(par, score):
    try:
        datos = []

        with open(ARCHIVO, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["par"] == par:
                    datos.append(row)

        # Si no hay datos → neutro
        if len(datos) < 10:
            return 50

        # Filtrar datos similares
        similares = []
        for d in datos:
            if abs(float(d["score"]) - score) <= 1:
                similares.append(d)

        if len(similares) < 5:
            return 50

        wins = sum(1 for d in similares if d["resultado"] == "win")
        total = len(similares)

        confianza = int((wins / total) * 100)

        return confianza

    except:
        return 50

# =========================
# 🎯 DECISIÓN FINAL IA
# =========================
def decision_final(tipo, score, confianza):
    # 🔥 filtro fuerte IA
    if confianza < 60:
        return None

    # 🔥 score mínimo
    if score < 3:
        return None

    return tipo

# =========================
# 🧪 DEBUG IA
# =========================
def debug_ia(par, score, confianza):
    print(f"🤖 IA → {par} | score: {score} | confianza: {confianza}%")
