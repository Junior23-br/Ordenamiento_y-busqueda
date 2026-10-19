"""
Harness de medición en Python - Taller 3 (Ordenamiento y Búsqueda).

Lo usan las tres personas del grupo. Se encarga de:
  - leer los archivos de data/
  - medir solo el algoritmo (la lectura de archivos y la copia quedan fuera)
  - repetir 5 veces y calcular promedio y desviación estándar
  - verificar el resultado FUERA del tiempo medido
  - guardar cada medición como una fila en un CSV de results/

Todos los tiempos se guardan en nanosegundos (ns).
"""
import csv
import os
import statistics
import time

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(RAIZ, "data")
RESULTS = os.path.join(RAIZ, "results")

REPETICIONES = 5
LIMITE_NS = 5 * 60 * 1_000_000_000          # 5 minutos por ejecución
LENGUAJE = "Python"

COLUMNAS = ["algoritmo", "lenguaje", "punto", "variante", "n",
            "rep1", "rep2", "rep3", "rep4", "rep5",
            "promedio_ns", "desviacion_ns", "tipo"]


# ---------------------------------------------------------------- lectura
def leer(nombre):
    """Lee un archivo de data/ y retorna una lista de enteros."""
    with open(os.path.join(DATA, nombre)) as f:
        return [int(linea) for linea in f if linea.strip()]


# ---------------------------------------------------------------- CSV
def guardar_fila(archivo_csv, algoritmo, punto, variante, n, tiempos, tipo="medido"):
    """Agrega una fila al CSV. Si el archivo no existe, escribe el encabezado."""
    os.makedirs(RESULTS, exist_ok=True)
    ruta = os.path.join(RESULTS, archivo_csv)
    nuevo = not os.path.exists(ruta)
    reps = list(tiempos) + [""] * (REPETICIONES - len(tiempos))
    if not tiempos:                              # ejecución que falló: sin tiempos
        promedio = desviacion = ""
    else:
        promedio = round(statistics.mean(tiempos), 2)
        desviacion = round(statistics.stdev(tiempos), 2) if len(tiempos) > 1 else 0.0
    with open(ruta, "a", newline="") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(COLUMNAS)
        w.writerow([algoritmo, LENGUAJE, punto, variante, n, *reps,
                    promedio, desviacion, tipo])
    return promedio, desviacion


# ---------------------------------------------------------------- ordenamiento
def medir_ordenamiento(nombre, funcion, variante, n, archivo_csv="ordenamiento_python.csv"):
    """
    funcion(arr) puede ordenar en el mismo arreglo (y retornar None)
    o retornar una lista nueva ordenada. Ambas formas se aceptan.
    variante: "random", "asc" o "desc".
    """
    original = leer(f"{variante}_{n}.txt")
    esperado = leer(f"asc_{n}.txt")              # respuesta correcta conocida
    tiempos = []
    try:
        for r in range(REPETICIONES):
            copia = original.copy()              # copia nueva, FUERA del tiempo
            inicio = time.perf_counter_ns()
            resultado = funcion(copia)
            fin = time.perf_counter_ns()
            if resultado is None:
                resultado = copia
            if resultado != esperado:            # verificación, FUERA del tiempo
                raise AssertionError(f"{nombre} no ordenó bien ({variante}, n={n})")
            tiempos.append(fin - inicio)
            if fin - inicio > LIMITE_NS:
                print(f"  aviso: {nombre} superó 5 minutos; se detienen las repeticiones")
                break
    except RecursionError:
        # No se oculta el error: queda registrado en el CSV para documentarlo
        guardar_fila(archivo_csv, nombre, 1, variante, n, [], tipo="error:RecursionError")
        print(f"  {nombre:<22} {variante:<7} n={n:>9,}  ERROR: RecursionError (límite de recursión)")
        return
    prom, desv = guardar_fila(archivo_csv, nombre, 1, variante, n, tiempos)
    print(f"  {nombre:<22} {variante:<7} n={n:>9,}  prom={prom/1e6:12.3f} ms  desv={desv/1e6:10.3f} ms")


# ---------------------------------------------------------------- búsqueda
def verificar_busqueda(nombre, funcion, arr, claves):
    """Comprueba (fuera del tiempo) que cada búsqueda responde bien.
    La función debe retornar un índice i con arr[i] == clave, o -1 si no está."""
    presentes = set(arr)
    for k in claves:
        i = funcion(arr, k)
        if k in presentes:
            if i == -1 or arr[i] != k:
                raise AssertionError(f"{nombre}: no encontró {k}, que sí está")
        elif i != -1:
            raise AssertionError(f"{nombre}: dice encontrar {k}, que no está")


def medir_busqueda(nombre, funcion, n, variante="claves", archivo_csv="busqueda_python.csv"):
    """
    variante "claves": las 1.000 claves de claves.txt (500 presentes + 500 ausentes).
    variante "inicio" / "centro" / "final": la misma clave buscada 1.000 veces.
    Se mide el tiempo TOTAL de las 1.000 búsquedas y se guarda el promedio por búsqueda.
    """
    arr = leer(f"asc_{n}.txt")
    if variante == "claves":
        claves = leer("claves.txt")
    else:
        posicion = {"inicio": 0, "centro": 1, "final": 2}[variante]
        claves = [leer(f"posiciones_{n}.txt")[posicion]] * 1000

    verificar_busqueda(nombre, funcion, arr, claves)
    tiempos = []
    for r in range(REPETICIONES):
        inicio = time.perf_counter_ns()
        for k in claves:
            funcion(arr, k)
        fin = time.perf_counter_ns()
        tiempos.append((fin - inicio) / len(claves))   # tiempo por búsqueda
    prom, desv = guardar_fila(archivo_csv, nombre, 2, variante, n, tiempos)
    print(f"  {nombre:<22} {variante:<7} n={n:>9,}  prom={prom:12.1f} ns/búsqueda  desv={desv:10.1f}")


# ---------------------------------------------------------------- prueba del harness
if __name__ == "__main__":
    # Algoritmos de PRUEBA, solo para comprobar que el harness funciona.
    def busqueda_lineal_prueba(arr, clave):
        for i in range(len(arr)):
            if arr[i] == clave:
                return i
        return -1

    def ordenamiento_prueba(arr):
        arr.sort()                               # sort de Python, solo para probar

    print("Prueba del harness (resultados en results/prueba_harness_python.csv)")
    for n in [1_000, 10_000]:
        medir_ordenamiento("sort_python_PRUEBA", ordenamiento_prueba, "random", n,
                           archivo_csv="prueba_harness_python.csv")
    for n in [1_000, 10_000]:
        for v in ["claves", "inicio", "centro", "final"]:
            medir_busqueda("lineal_PRUEBA", busqueda_lineal_prueba, n, v,
                           archivo_csv="prueba_harness_python.csv")

    # Prueba de que la verificación detecta errores
    try:
        medir_ordenamiento("ordenamiento_malo", lambda a: None, "random", 1_000,
                           archivo_csv="prueba_harness_python.csv")
        print("  FALLA: la verificación no detectó un ordenamiento incorrecto")
    except AssertionError as e:
        print(f"  OK: la verificación detectó el error -> {e}")

    # Prueba de que un error de recursión se registra en vez de detener el programa
    def recursion_infinita(arr):
        return recursion_infinita(arr)
    medir_ordenamiento("recursion_infinita", recursion_infinita, "random", 1_000,
                       archivo_csv="prueba_harness_python.csv")
