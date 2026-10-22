"""
Algoritmos de ordenamiento - Taller 3, Punto 1, Persona 3

Merge Sort, Radix Sort y Bucket Sort.
Todos reciben la lista y la ordenan EN LA MISMA LISTA (no retornan nada).
El código es el mismo que en OrdenamientosP3.java.

Fuentes (GeeksforGeeks):
  Merge Sort:  https://www.geeksforgeeks.org/dsa/merge-sort/
  Radix Sort:  https://www.geeksforgeeks.org/dsa/radix-sort/
  Bucket Sort: https://www.geeksforgeeks.org/dsa/bucket-sort-2/
  Los nombres de las variables se cambiaron a palabras completas en español
  (por ejemplo left, mid, right -> izquierda, medio, derecha); la lógica es la misma.
  Bucket Sort se adaptó de decimales en [0, 1) a enteros de 8 dígitos (ver la sección de Bucket Sort).
"""


# ================================================================ Merge Sort
# O(n log n) en todos los casos. Estable. NO es in-place: usa O(n) de memoria extra.

def merge_sort(arreglo):
    """Envoltorio: lo que llama el harness."""
    _merge_sort(arreglo, 0, len(arreglo) - 1)


def _merge_sort(arreglo, izquierda, derecha):
    """Ordena la parte del arreglo que va desde la posición izquierda hasta la posición derecha."""
    # Profundidad de recursión: log2(n) ≈ 20 niveles con n = 1.000.000 -> nunca supera el límite de Python
    if izquierda < derecha:                           # si izquierda == derecha hay 1 elemento: caso base
        medio = izquierda + (derecha - izquierda) // 2
        _merge_sort(arreglo, izquierda, medio)        # ordena la primera mitad
        _merge_sort(arreglo, medio + 1, derecha)      # ordena la segunda mitad
        _merge(arreglo, izquierda, medio, derecha)    # mezcla las dos mitades ordenadas


def _merge(arreglo, izquierda, medio, derecha):
    """Mezcla arreglo[izquierda..medio] con arreglo[medio+1..derecha], que ya están ordenados."""
    tamano_izquierda = medio - izquierda + 1
    tamano_derecha = derecha - medio

    # Copias temporales de las dos mitades
    mitad_izquierda = [0] * tamano_izquierda
    mitad_derecha = [0] * tamano_derecha
    for i in range(tamano_izquierda):
        mitad_izquierda[i] = arreglo[izquierda + i]
    for i in range(tamano_derecha):
        mitad_derecha[i] = arreglo[medio + 1 + i]

    pos_izquierda = 0          # recorre mitad_izquierda
    pos_derecha = 0            # recorre mitad_derecha
    pos_arreglo = izquierda    # dónde se escribe el resultado en el arreglo
    while pos_izquierda < tamano_izquierda and pos_derecha < tamano_derecha:
        if mitad_izquierda[pos_izquierda] <= mitad_derecha[pos_derecha]:   # "<=" mantiene el orden de los iguales: ESTABLE
            arreglo[pos_arreglo] = mitad_izquierda[pos_izquierda]
            pos_izquierda += 1
        else:
            arreglo[pos_arreglo] = mitad_derecha[pos_derecha]
            pos_derecha += 1
        pos_arreglo += 1

    # Copia lo que haya sobrado de alguna de las dos mitades
    while pos_izquierda < tamano_izquierda:
        arreglo[pos_arreglo] = mitad_izquierda[pos_izquierda]
        pos_izquierda += 1
        pos_arreglo += 1
    while pos_derecha < tamano_derecha:
        arreglo[pos_arreglo] = mitad_derecha[pos_derecha]
        pos_derecha += 1
        pos_arreglo += 1


# ================================================================ Radix Sort
# O(d · (n + 10)), con d = número de dígitos del máximo (aquí d = 8): lineal en n.
# No compara elementos entre sí. Estable. No es in-place: usa O(n) extra.

def radix_sort(arreglo):
    """Envoltorio: lo que llama el harness."""
    if len(arreglo) == 0:
        return
    maximo = obtener_maximo(arreglo)
    # El máximo tiene 8 dígitos -> 8 pasadas (exponente = 1, 10, 100, ..., 10.000.000)
    exponente = 1
    while maximo // exponente > 0:
        counting_sort_por_digito(arreglo, exponente)
        exponente *= 10


def obtener_maximo(arreglo):
    maximo = arreglo[0]
    for i in range(1, len(arreglo)):
        if arreglo[i] > maximo:
            maximo = arreglo[i]
    return maximo


def counting_sort_por_digito(arreglo, exponente):
    """Counting sort estable según un solo dígito. "exponente" indica cuál:
    1 = unidades, 10 = decenas, 100 = centenas... El dígito es (valor // exponente) % 10."""
    n = len(arreglo)
    salida = [0] * n
    conteo = [0] * 10                                   # un contador por dígito 0..9

    for i in range(n):                                  # cuenta cuántos hay de cada dígito
        conteo[(arreglo[i] // exponente) % 10] += 1
    for digito in range(1, 10):                         # posiciones finales acumuladas
        conteo[digito] += conteo[digito - 1]
    for i in range(n - 1, -1, -1):                      # de derecha a izquierda: ESTABLE; sin esto Radix ordenaría mal
        digito = (arreglo[i] // exponente) % 10
        salida[conteo[digito] - 1] = arreglo[i]
        conteo[digito] -= 1
    for i in range(n):
        arreglo[i] = salida[i]


# ================================================================ Bucket Sort
# Promedio O(n) con datos uniformes; peor caso O(n²) si todo cae en una cubeta.
# Estable (Insertion Sort dentro de cada cubeta). No es in-place: usa O(n) extra.
#
# ADAPTACIÓN: GeeksforGeeks ordena decimales en [0, 1) y asigna la cubeta con n * valor.
# Aquí los datos son enteros, así que:
#   - Se usan n cubetas (tantas como elementos).
#   - El valor x va a la cubeta  (x - minimo) * n // (maximo - minimo + 1),
#     es decir, se reparte el rango [minimo, maximo] en n intervalos del mismo tamaño.
#     Con n = 1.000.000 y el rango de 8 dígitos, cada cubeta cubre unos 90 valores.
#   - En Python los enteros no tienen límite, así que no hace falta el "long" de Java.

def bucket_sort(arreglo):
    """Envoltorio: lo que llama el harness."""
    n = len(arreglo)
    if n <= 1:
        return

    minimo = maximo = arreglo[0]
    for valor in arreglo:
        if valor < minimo:
            minimo = valor
        if valor > maximo:
            maximo = valor
    rango = maximo - minimo + 1

    # 1) Crear n cubetas vacías
    cubetas = [[] for _ in range(n)]

    # 2) Poner cada elemento en su cubeta
    #    Datos uniformes -> cada cubeta recibe en promedio 1 elemento -> ordenar cada cubeta es O(1)
    for valor in arreglo:
        indice_cubeta = (valor - minimo) * n // rango
        cubetas[indice_cubeta].append(valor)

    # 3) Ordenar cada cubeta con Insertion Sort (como en GeeksforGeeks)
    for cubeta in cubetas:
        insertion_sort(cubeta)

    # 4) Concatenar las cubetas en orden
    posicion = 0
    for cubeta in cubetas:
        for valor in cubeta:
            arreglo[posicion] = valor
            posicion += 1


def insertion_sort(cubeta):
    for i in range(1, len(cubeta)):
        clave = cubeta[i]
        j = i - 1
        while j >= 0 and cubeta[j] > clave:             # desplaza a la derecha los mayores
            cubeta[j + 1] = cubeta[j]
            j -= 1
        cubeta[j + 1] = clave


# ================================================================ registro para el harness
# Los 3 algoritmos con su nombre, en el mismo orden que en Java.
ALGORITMOS = {
    "MergeSort": merge_sort,
    "RadixSort": radix_sort,
    "BucketSort": bucket_sort,
}


# ================================================================ pruebas de correctitud
if __name__ == "__main__":
    import random
    import harness

    print("1) Casos borde")
    generador = random.Random(1)
    casos = {
        "vacio": [], "un elemento": [12_345_678], "dos elementos": [99_999_999, 10_000_000],
        "repetidos": [30_000_003, 10_000_001, 30_000_003, 20_000_002],
        "todos iguales": [55_555_555] * 10,
        "ordenado": [10_000_000 + i for i in range(20)],
        "inverso": [99_999_999 - i for i in range(20)],
        "aleatorio": [generador.randint(10_000_000, 99_999_999) for _ in range(300)],
        "muchos repetidos en rango pequeño": [10_000_000 + generador.randint(0, 4) for _ in range(300)],
    }
    for nombre, f in ALGORITMOS.items():
        ok = True
        for descripcion, datos in casos.items():
            copia = datos.copy()
            f(copia)
            if copia != sorted(datos):
                ok = False
                print(f"   FALLA {nombre}: {descripcion}")
        print(f"   {'OK   ' if ok else 'FALLA'} {nombre}")

    print("2) Archivos del taller, n = 1.000 y 100.000 (aleatorio, ascendente, descendente)")
    for n in [1_000, 100_000]:
        esperado = harness.leer(f"asc_{n}.txt")
        for nombre, f in ALGORITMOS.items():
            for v in ["random", "asc", "desc"]:
                datos = harness.leer(f"{v}_{n}.txt")
                f(datos)
                assert datos == esperado, f"{nombre} falló con {v}, n={n}"
        print(f"   OK    n = {n:,}: los 3 algoritmos ordenan bien")

    print("\nRESULTADO: LOS 3 ALGORITMOS ORDENAN CORRECTAMENTE")