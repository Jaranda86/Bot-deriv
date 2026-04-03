import csv
import os

archivo = "historial.csv"

def guardar_operacion(par, accion, resultado, score):

    existe = os.path.isfile(archivo)

    with open(archivo, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not existe:
            writer.writerow(["par", "accion", "resultado", "score"])

        writer.writerow([par, accion, resultado, score])


def filtrar_operacion(score):
    if score >= 4:
        return True
    elif score <= -4:
        return True
    else:
        return False
