"""
Generador de datos de prueba - Taller 3 (Ordenamiento y Búsqueda).
Se ejecuta UNA sola vez. Todos los algoritmos (Java y Python) leen estos archivos.

Archivos que crea en la carpeta data/:
  random_N.txt     arreglo en orden aleatorio
  asc_N.txt        mismo arreglo ordenado ascendente
  desc_N.txt       mismo arreglo ordenado descendente
  claves.txt       1.000 claves de búsqueda (500 presentes + 500 ausentes)
  posiciones_N.txt 3 claves: inicio, centro y final del arreglo ascendente
"""
import os
import random

SEMILLA = 2026
TAMANOS = [1_000, 10_000, 100_000, 1_000_000]
MINIMO, MAXIMO = 10_000_000, 99_999_999      # enteros de 8 dígitos
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def guardar(nombre, valores):
    with open(os.path.join(CARPETA, nombre), "w") as f:
        f.write("\n".join(map(str, valores)) + "\n")


def main():
    os.makedirs(CARPETA, exist_ok=True)
    rng = random.Random(SEMILLA)

    # 1) Una sola secuencia de 1.000.000; cada tamaño menor es un prefijo de ella.
    #    Así una clave presente en el arreglo de 1.000 está presente en todos.
    base = [rng.randint(MINIMO, MAXIMO) for _ in range(max(TAMANOS))]

    for n in TAMANOS:
        datos = base[:n]
        asc = sorted(datos)                 # orden de referencia (no se mide)
        guardar(f"random_{n}.txt", datos)
        guardar(f"asc_{n}.txt", asc)
        guardar(f"desc_{n}.txt", asc[::-1])
        # claves al inicio, centro y final del arreglo ascendente
        guardar(f"posiciones_{n}.txt", [asc[0], asc[n // 2], asc[n - 1]])
        print(f"n = {n:>9,}: random, asc, desc y posiciones generados")

    # 2) Claves de búsqueda: 500 presentes (tomadas de los primeros 1.000) y
    #    500 ausentes (valores de 8 dígitos que no están en el arreglo de 1.000.000).
    presentes = rng.sample(base[:1_000], 500)
    todos = set(base)
    ausentes = set()
    while len(ausentes) < 500:
        x = rng.randint(MINIMO, MAXIMO)
        if x not in todos:
            ausentes.add(x)
    claves = presentes + sorted(ausentes)
    rng.shuffle(claves)                     # mezcladas para no favorecer a nadie
    guardar("claves.txt", claves)
    print("claves.txt: 500 presentes + 500 ausentes")


if __name__ == "__main__":
    main()
