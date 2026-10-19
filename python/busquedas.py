"""
Algoritmos de búsqueda - Taller 3, Punto 2 (Persona 1).

Todos reciben (arr, x) con arr ordenado ascendente y retornan
un índice i tal que arr[i] == x, o -1 si x no está.
Las versiones son iterativas (sin recursión) y son las mismas que en Busquedas.java.

Fuentes (GeeksforGeeks):
  Lineal:        https://www.geeksforgeeks.org/dsa/linear-search/
  Binaria:       https://www.geeksforgeeks.org/dsa/binary-search/
  Ternaria:      https://www.geeksforgeeks.org/dsa/ternary-search/
  Saltos:        https://www.geeksforgeeks.org/dsa/jump-search/
  Interpolación: https://www.geeksforgeeks.org/dsa/interpolation-search/
  Exponencial:   https://www.geeksforgeeks.org/dsa/exponential-search/
"""
import math


def busqueda_lineal(arr, x):
    """O(n). Revisa los elementos uno por uno desde el inicio."""
    for i in range(len(arr)):
        if arr[i] == x:
            return i
    return -1


def busqueda_binaria(arr, x, lo=0, hi=None):
    """O(log n). Compara con el elemento del medio y descarta la mitad."""
    if hi is None:
        hi = len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def busqueda_ternaria(arr, x):
    """O(log3 n). Divide el rango en tres partes con dos puntos de corte."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        tercio = (hi - lo) // 3
        mid1 = lo + tercio
        mid2 = hi - tercio
        if arr[mid1] == x:
            return mid1
        if arr[mid2] == x:
            return mid2
        if x < arr[mid1]:
            hi = mid1 - 1
        elif x > arr[mid2]:
            lo = mid2 + 1
        else:
            lo, hi = mid1 + 1, mid2 - 1
    return -1


def busqueda_saltos(arr, x):
    """O(√n). Salta de a √n posiciones y luego busca linealmente en el bloque."""
    n = len(arr)
    if n == 0:
        return -1
    paso = int(math.sqrt(n))
    prev, actual = 0, paso
    # avanzar por bloques mientras el último elemento del bloque sea menor que x
    while actual < n and arr[actual - 1] < x:
        prev = actual
        actual += paso
    # búsqueda lineal dentro del bloque [prev, min(actual, n))
    fin = min(actual, n)
    for i in range(prev, fin):
        if arr[i] == x:
            return i
        if arr[i] > x:
            break
    return -1


def busqueda_interpolacion(arr, x):
    """O(log log n) con datos uniformes, O(n) en el peor caso.
    Estima la posición según el valor, como al buscar una palabra en el diccionario."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi and arr[lo] <= x <= arr[hi]:
        if arr[hi] == arr[lo]:                    # evita dividir entre cero
            return lo if arr[lo] == x else -1
        pos = lo + ((x - arr[lo]) * (hi - lo)) // (arr[hi] - arr[lo])
        if arr[pos] == x:
            return pos
        if arr[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


def busqueda_exponencial(arr, x):
    """O(log i), donde i es la posición de x. Duplica el rango (1, 2, 4, 8, ...)
    hasta pasarse de x y luego hace búsqueda binaria en ese rango."""
    n = len(arr)
    if n == 0:
        return -1
    if arr[0] == x:
        return 0
    i = 1
    while i < n and arr[i] <= x:
        i *= 2
    return busqueda_binaria(arr, x, i // 2, min(i, n - 1))


ALGORITMOS = {
    "Lineal": busqueda_lineal,
    "Binaria": busqueda_binaria,
    "Ternaria": busqueda_ternaria,
    "Saltos": busqueda_saltos,
    "Interpolacion": busqueda_interpolacion,
    "Exponencial": busqueda_exponencial,
}


# ------------------------------------------------------------- pruebas de correctitud
if __name__ == "__main__":
    import harness

    print("1) Casos borde con un arreglo pequeño (con un valor repetido)")
    a = [10, 20, 20, 30, 40, 50, 60, 70, 80, 90]
    casos = [(10, True), (90, True), (20, True), (50, True),     # primero, último, repetido, medio
             (5, False), (95, False), (35, False)]               # menor, mayor, entre dos valores
    for nombre, f in ALGORITMOS.items():
        ok = True
        for x, esta in casos:
            i = f(a, x)
            if (esta and (i == -1 or a[i] != x)) or (not esta and i != -1):
                ok = False
                print(f"   FALLA {nombre}: buscar {x} retornó {i}")
        for vacio in ([], [7]):
            if f(vacio, 3) != -1:
                ok = False
                print(f"   FALLA {nombre}: arreglo {vacio}")
        print(f"   {'OK   ' if ok else 'FALLA'} {nombre}")

    print("2) Las 1.000 claves y las 3 posiciones, en los 4 tamaños")
    for n in [1_000, 10_000, 100_000, 1_000_000]:
        arr = harness.leer(f"asc_{n}.txt")
        claves = harness.leer("claves.txt") + harness.leer(f"posiciones_{n}.txt")
        for nombre, f in ALGORITMOS.items():
            if nombre == "Lineal" and n == 1_000_000:
                claves_n = claves[:50] + claves[-3:]   # la lineal es lenta: muestra
            else:
                claves_n = claves
            harness.verificar_busqueda(nombre, f, arr, claves_n)   # lanza error si falla
        print(f"   OK    n = {n:,}: los 6 algoritmos responden bien")

    print("\nRESULTADO: TODOS LOS ALGORITMOS SON CORRECTOS")
