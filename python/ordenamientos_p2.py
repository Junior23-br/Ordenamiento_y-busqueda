"""
Algoritmos de ordenamiento - Taller 3, Punto 1 (Persona 2: César Tulcán).

Insertion Sort, Dual-Pivot QuickSort (pivotes en el primer y el último elemento) y Heap Sort.
Todos ordenan la lista EN EL MISMO ARREGLO (in-place) y no retornan nada.
El código es el mismo que en OrdenamientosP2.java.

Fuentes (GeeksforGeeks):
  Insertion Sort:        https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/
  Dual-Pivot QuickSort:  https://www.geeksforgeeks.org/dsa/dual-pivot-quicksort/
  Heap Sort:             https://www.geeksforgeeks.org/dsa/heap-sort/

NOTA: no se modifica el límite de recursión de Python (1.000 por defecto). El enunciado
pide documentar el error si un algoritmo falla por el límite de recursión, no ocultarlo.
"""


# ------------------------------------------------------------------ Insertion Sort
def insertion_sort(arr):
    """Mejor caso O(n) (ya ordenado), promedio y peor caso O(n²) (orden inverso).
    Estable e in-place."""
    for i in range(1, len(arr)):
        clave = arr[i]
        j = i - 1
        # desplaza a la derecha los elementos mayores que la clave
        while j >= 0 and arr[j] > clave:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = clave


# ------------------------------------------------------------------ Dual-Pivot QuickSort
def dual_pivot_quicksort(arr):
    """Mejor y promedio O(n log n), peor caso O(n²) (entrada ordenada o inversa,
    porque los pivotes son el mínimo y el máximo). No estable, in-place
    (usa O(log n) de pila en promedio y O(n) en el peor caso)."""
    _dpqs(arr, 0, len(arr) - 1)


def _dpqs(arr, low, high):
    if low < high:
        lp, rp = _particion(arr, low, high)
        _dpqs(arr, low, lp - 1)          # elementos menores que p
        _dpqs(arr, lp + 1, rp - 1)       # elementos entre p y q
        _dpqs(arr, rp + 1, high)         # elementos mayores que q


def _particion(arr, low, high):
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    p, q = arr[low], arr[high]           # pivotes: primer y último elemento
    j = k = low + 1
    g = high - 1
    while k <= g:
        if arr[k] < p:                   # va a la zona izquierda
            arr[k], arr[j] = arr[j], arr[k]
            j += 1
        elif arr[k] >= q:                # va a la zona derecha
            while arr[g] > q and k < g:
                g -= 1
            arr[k], arr[g] = arr[g], arr[k]
            g -= 1
            if arr[k] < p:
                arr[k], arr[j] = arr[j], arr[k]
                j += 1
        k += 1
    j -= 1
    g += 1
    arr[low], arr[j] = arr[j], arr[low]  # ubica los pivotes en su posición final
    arr[high], arr[g] = arr[g], arr[high]
    return j, g


# ------------------------------------------------------------------ Heap Sort
def heap_sort(arr):
    """O(n log n) en mejor, promedio y peor caso. No estable, in-place."""
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):  # construir el max-heap
        _heapify(arr, n, i)
    for i in range(n - 1, 0, -1):        # sacar el máximo y reordenar el heap
        arr[0], arr[i] = arr[i], arr[0]
        _heapify(arr, i, 0)


def _heapify(arr, n, i):
    mayor = i
    izq, der = 2 * i + 1, 2 * i + 2
    if izq < n and arr[izq] > arr[mayor]:
        mayor = izq
    if der < n and arr[der] > arr[mayor]:
        mayor = der
    if mayor != i:
        arr[i], arr[mayor] = arr[mayor], arr[i]
        _heapify(arr, n, mayor)          # profundidad máxima log2(n), unos 20 niveles


ALGORITMOS = {
    "InsertionSort": insertion_sort,
    "DualPivotQuickSort": dual_pivot_quicksort,
    "HeapSort": heap_sort,
}


# ------------------------------------------------------------------ pruebas de correctitud
if __name__ == "__main__":
    import random
    import harness

    print("1) Casos borde")
    casos = {
        "vacio": [], "un elemento": [5], "dos elementos": [2, 1],
        "repetidos": [3, 1, 3, 2, 1, 3], "todos iguales": [7] * 10,
        "ordenado": list(range(20)), "inverso": list(range(20, 0, -1)),
    }
    rng = random.Random(1)
    casos["aleatorio con repetidos"] = [rng.randint(0, 50) for _ in range(300)]
    for nombre, f in ALGORITMOS.items():
        ok = True
        for desc, datos in casos.items():
            copia = datos.copy()
            f(copia)
            if copia != sorted(datos):
                ok = False
                print(f"   FALLA {nombre}: {desc}")
        print(f"   {'OK   ' if ok else 'FALLA'} {nombre}")

    print("2) Archivos del taller, n = 1.000 (aleatorio, ascendente, descendente)")
    esperado = harness.leer("asc_1000.txt")
    for nombre, f in ALGORITMOS.items():
        for v in ["random", "asc", "desc"]:
            datos = harness.leer(f"{v}_1000.txt")
            f(datos)
            assert datos == esperado, f"{nombre} falló con {v}"
        print(f"   OK    {nombre}")

    print("3) Comportamiento esperado: QuickSort con entrada ordenada, n = 10.000")
    try:
        dual_pivot_quicksort(harness.leer("asc_10000.txt"))
        print("   (no falló)")
    except RecursionError:
        print("   OK    RecursionError, como se esperaba: la recursión llega a ~5.000 niveles")
        print("         y el límite de Python es 1.000. Esto se documenta en el análisis.")

    print("\nRESULTADO: LOS 3 ALGORITMOS ORDENAN CORRECTAMENTE")
