"""Verifica que los archivos de data/ cumplan las condiciones del taller."""
import os

TAMANOS = [1_000, 10_000, 100_000, 1_000_000]
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def leer(nombre):
    with open(os.path.join(CARPETA, nombre)) as f:
        return [int(linea) for linea in f if linea.strip()]


def check(condicion, mensaje):
    print(("  OK    " if condicion else "  FALLA ") + mensaje)
    return condicion


todo_bien = True
for n in TAMANOS:
    print(f"n = {n:,}")
    r, a, d = leer(f"random_{n}.txt"), leer(f"asc_{n}.txt"), leer(f"desc_{n}.txt")
    p = leer(f"posiciones_{n}.txt")
    todo_bien &= check(len(r) == len(a) == len(d) == n, "los tres archivos tienen n elementos")
    todo_bien &= check(all(10_000_000 <= x <= 99_999_999 for x in r), "todos tienen 8 dígitos")
    todo_bien &= check(all(a[i] <= a[i + 1] for i in range(n - 1)), "asc está ordenado ascendente")
    todo_bien &= check(d == a[::-1], "desc es asc al revés")
    todo_bien &= check(sorted(r) == a, "asc tiene los mismos números que random")
    todo_bien &= check(p == [a[0], a[n // 2], a[n - 1]], "posiciones = inicio, centro, final")

print("claves.txt")
claves = leer("claves.txt")
conjunto_1000 = set(leer("random_1000.txt"))
conjunto_1m = set(leer("random_1000000.txt"))
pres = [k for k in claves if k in conjunto_1000]
aus = [k for k in claves if k not in conjunto_1m]
todo_bien &= check(len(claves) == 1000, "hay 1.000 claves")
todo_bien &= check(len(pres) == 500, f"500 presentes en todos los tamaños ({len(pres)})")
todo_bien &= check(len(aus) == 500, f"500 ausentes en todos los tamaños ({len(aus)})")

print("\nRESULTADO:", "TODO CORRECTO" if todo_bien else "HAY ERRORES")
