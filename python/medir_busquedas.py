"""
Mediciones del Punto 2 en Python (Persona 1).

Genera results/busqueda_python.csv con:
  - variante "claves": las 1.000 claves, en los 4 tamaños (gráficas de crecimiento
    y de compilado frente a interpretado)
  - variantes "inicio", "centro", "final": solo n = 1.000.000 (tabla de posición)

Ejecutar desde la carpeta raíz del proyecto:  python python/medir_busquedas.py
"""
import os
import time

import harness
from busquedas import ALGORITMOS

CSV = "busqueda_python.csv"
TAMANOS = [1_000, 10_000, 100_000, 1_000_000]

if __name__ == "__main__":
    ruta = os.path.join(harness.RESULTS, CSV)
    if os.path.exists(ruta):
        os.remove(ruta)                 # se empieza de cero para no duplicar filas
    t0 = time.time()

    print("Crecimiento: 1.000 claves (500 presentes + 500 ausentes)")
    for n in TAMANOS:
        for nombre, f in ALGORITMOS.items():
            harness.medir_busqueda(nombre, f, n, "claves", archivo_csv=CSV)

    print("\nPosicion de la clave: n = 1.000.000")
    for nombre, f in ALGORITMOS.items():
        for v in ["inicio", "centro", "final"]:
            harness.medir_busqueda(nombre, f, 1_000_000, v, archivo_csv=CSV)

    print(f"\nListo en {time.time() - t0:.0f} s. Resultados en results/{CSV}")
