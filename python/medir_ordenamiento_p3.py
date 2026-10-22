"""
Mediciones del Punto 1 en Python - Persona 3.
Merge Sort, Radix Sort y Bucket Sort con entrada aleatoria, ascendente y descendente.

Regla para los casos lentos (enunciado: más de 5 minutos por ejecución):
  antes de cada tamaño se PREDICE el tiempo de una ejecución a partir del tamaño anterior
  y de la complejidad teórica. Si la predicción supera 5 minutos, NO se ejecuta y se registra
  como "estimado". Si un tamaño menor falló por el límite de recursión, los mayores también
  fallarán: se registra el error y el tiempo estimado.

Uso, desde la carpeta raíz:
  python python/medir_ordenamiento_p3.py --piloto   mide solo 1.000 y 10.000 y muestra el plan
  python python/medir_ordenamiento_p3.py            medición completa -> results/ordenamiento_python_p3.csv
"""
import math
import os
import sys
import time

import harness
from ordenamientos_p3 import ALGORITMOS

TAMANOS = [1_000, 10_000, 100_000, 1_000_000]
VARIANTES = ["random", "asc", "desc"]
LIMITE_S = 5 * 60

# Crecimiento teórico de cada caso (se usa para predecir y para estimar)
CRECIMIENTO = {
    ("MergeSort", "random"): "n log n", ("MergeSort", "asc"): "n log n", ("MergeSort", "desc"): "n log n",
    ("RadixSort", "random"): "n", ("RadixSort", "asc"): "n", ("RadixSort", "desc"): "n",
    ("BucketSort", "random"): "n", ("BucketSort", "asc"): "n", ("BucketSort", "desc"): "n",
}


def factor(tipo, n0, n1):
    """Cuántas veces crece el tiempo al pasar de n0 a n1 según la complejidad."""
    if tipo == "n":
        return n1 / n0
    if tipo == "n^2":
        return (n1 / n0) ** 2
    return (n1 * math.log2(n1)) / (n0 * math.log2(n0))       # n log n


def duracion(s):
    if s >= 3600:
        return f"{s / 3600:.1f} h"
    if s >= 60:
        return f"{s / 60:.1f} min"
    return f"{s:.1f} s"


def main(piloto):
    csv = "piloto_ordenamiento_python_p3.csv" if piloto else "ordenamiento_python_p3.csv"
    ruta = os.path.join(harness.RESULTS, csv)
    if os.path.exists(ruta):
        os.remove(ruta)                                       # se empieza de cero
    tamanos_medir = TAMANOS[:2] if piloto else TAMANOS
    plan = []                                                 # para el resumen del piloto
    t0 = time.time()

    for nombre, f in ALGORITMOS.items():
        for v in VARIANTES:
            tipo = CRECIMIENTO[(nombre, v)]
            ultimo = None                                     # (n, promedio_ns) del último tamaño
            fallo = False
            for n in TAMANOS:
                pred = ultimo[1] * factor(tipo, ultimo[0], n) if ultimo else None
                if n not in tamanos_medir:                    # solo en el piloto
                    plan.append((nombre, v, n, pred, fallo))
                    if pred:
                        ultimo = (n, pred)
                    continue
                if fallo:
                    print(f"  {nombre:<22} {v:<7} n={n:>9,}  NO SE EJECUTA: falló por recursión "
                          f"con un n menor -> estimado {duracion(pred / 1e9)}")
                    harness.guardar_estimado(csv, nombre, 1, v, n, pred)
                    ultimo = (n, pred)
                elif pred and pred / 1e9 > LIMITE_S:
                    print(f"  {nombre:<22} {v:<7} n={n:>9,}  NO SE EJECUTA: predicción "
                          f"{duracion(pred / 1e9)} > 5 min -> estimado ({tipo})")
                    harness.guardar_estimado(csv, nombre, 1, v, n, pred)
                    ultimo = (n, pred)
                else:
                    prom = harness.medir_ordenamiento(nombre, f, v, n, archivo_csv=csv)
                    if prom is None:                          # RecursionError
                        fallo = True
                        if pred:
                            print(f"  {'':<22} {'':<7} {'':>11}  estimado si no hubiera fallado: "
                                  f"{duracion(pred / 1e9)} ({tipo})")
                            harness.guardar_estimado(csv, nombre, 1, v, n, pred)
                            ultimo = (n, pred)
                    else:
                        ultimo = (n, prom)

    print(f"\nTiempo total: {duracion(time.time() - t0)}. Resultados en results/{csv}")

    if piloto:
        print("\nPLAN para la medición completa (predicción de UNA ejecución):")
        total = 0
        for nombre, v, n, pred, fallo in plan:
            if pred is None:
                continue
            s = pred / 1e9
            if fallo:
                accion = "error de recursión -> estimar"
            elif s > LIMITE_S:
                accion = "supera 5 min -> estimar"
            else:
                accion = f"se mide (5 rep. = {duracion(5 * s)})"
                total += 5 * s
            print(f"  {nombre:<20} {v:<7} n={n:>9,}  {duracion(s):>9}  {accion}")
        print(f"\n  Tiempo aproximado de la medición completa: {duracion(total + time.time() - t0)}")


if __name__ == "__main__":
    main("--piloto" in sys.argv)