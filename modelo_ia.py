import csv
import os

archivo = "historial.csv"

def guardar_operacion(par, score, resultado):
    existe = os.path.isfile(archivo)

    with open(archivo, mode='a', newline='') as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow(["par", "score", "resultado"])

        writer.writerow([par, score, resultado])


def calcular_confianza(par, score):
    if not os.path.isfile(archivo):
        return 50

    total = 0
    aciertos = 0

    with open(archivo, mode='r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["par"] == par:
                total += 1
                if row["resultado"] == "win":
                    aciertos += 1

    if total == 0:
        return 50

    return round((aciertos / total) * 100, 2)
