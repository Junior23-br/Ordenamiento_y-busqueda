"""
Punto 3.2 - ¿Ordenar o no ordenar? (Persona 1)

Compara, para un arreglo desordenado de n = 1.000.000:
  Opción A: k búsquedas lineales sobre el arreglo desordenado      -> k * t_lineal
  Opción B: ordenar una vez (mejor algoritmo medido) + k binarias  -> T_orden + k * t_binaria
Ordenar conviene cuando B < A, es decir, cuando  k > T_orden / (t_lineal - t_binaria).

Lee:
  results/busqueda_java.csv, results/busqueda_python.csv        (Persona 1)
  results/ordenamiento_java.csv, results/ordenamiento_python.csv (Personas 2 y 3)
Ejecutar desde la carpeta raíz:  python graficas/punto_3_2.py
"""
import csv
import glob
import math
import os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RESULTS = os.path.join(RAIZ, "results")
N = 1_000_000


def filas(patron):
    out = []
    for ruta in glob.glob(os.path.join(RESULTS, patron)):
        with open(ruta) as f:
            out += [r for r in csv.DictReader(f) if r["promedio_ns"]]
    return out


def ms(ns):
    return f"{ns / 1e6:,.3f} ms"


for lenguaje in ["Java", "Python"]:
    print(f"\n===== {lenguaje} =====")
    busq = {r["algoritmo"]: float(r["promedio_ns"])
            for r in filas(f"busqueda_{lenguaje.lower()}.csv")
            if r["variante"] == "claves" and int(r["n"]) == N}
    orden = [r for r in filas(f"ordenamiento_{lenguaje.lower()}*.csv")
             if r["variante"] == "random" and int(r["n"]) == N]
    if not busq or not orden:
        print("  Faltan datos: se necesitan los CSV de búsqueda y de ordenamiento.")
        continue
    mejor = min(orden, key=lambda r: float(r["promedio_ns"]))
    T = float(mejor["promedio_ns"])
    tl, tb = busq["Lineal"], busq["Binaria"]
    k = T / (tl - tb)
    print(f"  Mejor ordenamiento (aleatorio, n = 1.000.000): {mejor['algoritmo']} = {ms(T)}"
          f" ({mejor['tipo']})")
    print(f"  Búsqueda lineal  (promedio por búsqueda):       {tl:,.1f} ns")
    print(f"  Búsqueda binaria (promedio por búsqueda):       {tb:,.1f} ns")
    print(f"\n  k* = T_orden / (t_lineal - t_binaria) = {T:,.0f} / ({tl:,.1f} - {tb:,.1f}) = {k:,.2f}")
    print(f"  => Ordenar conviene a partir de k = {math.floor(k) + 1} búsquedas\n")
    print(f"  {'k':>8} | {'A: k lineales':>16} | {'B: ordenar + k binarias':>24} | mejor")
    kc = math.floor(k) + 1
    for kk in sorted({1, 10, max(kc - 1, 1), kc, 100, 1000, 10_000}):
        a, b = kk * tl, T + kk * tb
        print(f"  {kk:>8,} | {ms(a):>16} | {ms(b):>24} | {'ordenar' if b < a else 'lineal'}")
