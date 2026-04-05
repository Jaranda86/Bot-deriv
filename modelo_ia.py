import csv
import os

ARCHIVO = "historial.csv"


# =========================
# 📊 GUARDAR OPERACIONES
# =========================
def guardar_operacion(par, score, resultado):
    existe = os.path.isfile(ARCHIVO)

    with open(ARCHIVO, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow(["par", "score", "resultado"])

        writer.writerow([par, score, resultado])


# =========================
# 🧠 CALCULAR CONFIANZA INTELIGENTE
# =========================
def calcular_confianza(score):

    if not os.path.isfile(ARCHIVO):
        return 50  # sin datos

    total = 0
    ganadas = 0

    with open(ARCHIVO, mode="r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            s = int(row["score"])
            r = row["resultado"]

            # solo compara scores similares
            if abs(s - score) <= 1:
                total += 1
                if r == "win":
                    ganadas += 1

    if total == 0:
        return 50

    winrate = ganadas / total

    return int(winrate * 100)
