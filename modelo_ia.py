import csv
import os

ARCHIVO = "historial.csv"

def guardar_operacion(par, decision, score, resultado):
    existe = os.path.isfile(ARCHIVO)

    with open(ARCHIVO, "a", newline="") as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow(["par", "decision", "score", "resultado"])

        writer.writerow([par, decision, score, resultado])


def analizar_historial():
    if not os.path.exists(ARCHIVO):
        return 0

    total = 0
    ganadas = 0

    with open(ARCHIVO, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if row["resultado"] == "win":
                ganadas += 1

    if total == 0:
        return 0

    return ganadas / total
