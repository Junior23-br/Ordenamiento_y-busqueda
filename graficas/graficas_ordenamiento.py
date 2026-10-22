"""
Graficas del Punto 1 (ordenamiento): 6 algoritmos, Java y Python.

Lee:  results/ordenamiento_{java,python}_p2.csv  (Insertion, Dual-Pivot, Heap)
      results/ordenamiento_{java,python}_p3.csv  (Merge, Radix, Bucket)
Genera en graficas/:
  p1_crecimiento_java.png, p1_crecimiento_python.png     (n vs tiempo, log-log)
  p1_orden_java_1000.png, _10000.png, _100000.png        (random/asc/desc)
  p1_java_vs_python_1M.png                               (n = 1.000.000, aleatorio)
Los valores estimados se dibujan con linea punteada / barra rayada.
Uso (desde la raiz del repositorio):  python graficas/graficas_ordenamiento.py
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTADOS = "results"
SALIDA = "graficas"
ALGORITMOS = ["InsertionSort", "DualPivotQuickSort", "HeapSort",
              "MergeSort", "RadixSort", "BucketSort"]
NOMBRES = {"InsertionSort": "Insertion", "DualPivotQuickSort": "Dual-Pivot QS",
           "HeapSort": "Heap", "MergeSort": "Merge", "RadixSort": "Radix",
           "BucketSort": "Bucket"}
# Un color fijo por algoritmo en todas las graficas (paleta apta para daltonismo)
COLORES = {"InsertionSort": "#D55E00", "DualPivotQuickSort": "#CC79A7",
           "HeapSort": "#E69F00", "MergeSort": "#0072B2",
           "RadixSort": "#009E73", "BucketSort": "#56B4E9"}
MARCAS = {"InsertionSort": "o", "DualPivotQuickSort": "s", "HeapSort": "^",
          "MergeSort": "D", "RadixSort": "v", "BucketSort": "P"}
TAMANOS = [1000, 10000, 100000, 1000000]
VARIANTES = [("random", "Aleatoria"), ("asc", "Ascendente"), ("desc", "Descendente")]


def cargar(lenguaje):
    """Devuelve {(algoritmo, variante, n): (ns, es_estimado)}.
    Una fila 'estimado' reemplaza a una fila 'error:*' del mismo caso."""
    datos = {}
    for sufijo in ("p2", "p3"):
        ruta = os.path.join(RESULTADOS, f"ordenamiento_{lenguaje}_{sufijo}.csv")
        if not os.path.exists(ruta):
            print(f"AVISO: falta {ruta}")
            continue
        with open(ruta, newline="", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                if not fila["promedio_ns"]:
                    continue
                clave = (fila["algoritmo"], fila["variante"], int(fila["n"]))
                datos[clave] = (float(fila["promedio_ns"]), fila["tipo"] == "estimado")
    return datos


def formato(ns):
    s = ns / 1e9
    if s >= 3600:
        return f"{s / 3600:.1f} h"
    if s >= 60:
        return f"{s / 60:.1f} min"
    if s >= 1:
        return f"{s:.2f} s"
    if s >= 1e-3:
        return f"{s * 1e3:.1f} ms"
    return f"{s * 1e6:.0f} us"


def crecimiento(datos, lenguaje):
    fig, ejes = plt.subplots(1, 3, figsize=(17, 5.2), sharey=True)
    for eje, (var, titulo) in zip(ejes, VARIANTES):
        for alg in ALGORITMOS:
            pts = [(n, datos[(alg, var, n)]) for n in TAMANOS if (alg, var, n) in datos]
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1][0] / 1e9 for p in pts]
            est = [p[1][1] for p in pts]
            c = COLORES[alg]
            # tramo medido: linea continua; tramos que terminan en estimado: punteada
            for i in range(len(xs) - 1):
                eje.plot(xs[i:i + 2], ys[i:i + 2], color=c,
                         linestyle="--" if est[i + 1] else "-", linewidth=1.8)
            for x, y, e in zip(xs, ys, est):
                eje.plot(x, y, marker=MARCAS[alg], color=c, markersize=7,
                         markerfacecolor="white" if e else c)
            eje.plot([], [], color=c, marker=MARCAS[alg], label=NOMBRES[alg])
        eje.set_xscale("log")
        eje.set_yscale("log")
        eje.set_xticks(TAMANOS)
        eje.set_xticklabels(["1.000", "10.000", "100.000", "1.000.000"])
        eje.set_title(f"Entrada {titulo.lower()}")
        eje.set_xlabel("n (elementos)")
        eje.grid(True, which="both", alpha=0.25)
    ejes[0].set_ylabel("Tiempo promedio (s)")
    ejes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle(f"Crecimiento del tiempo de ordenamiento - {lenguaje} "
                 "(linea punteada y marcador hueco = valor estimado)", fontsize=12)
    fig.tight_layout()
    ruta = os.path.join(SALIDA, f"p1_crecimiento_{lenguaje.lower()}.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print("Generada", ruta)


def orden_entrada(datos, n):
    fig, eje = plt.subplots(figsize=(12, 5.8))
    k = len(ALGORITMOS)
    ancho = 0.8 / k
    ymax = 0
    for j, alg in enumerate(ALGORITMOS):
        for i, (var, _) in enumerate(VARIANTES):
            if (alg, var, n) not in datos:
                continue
            ns, est = datos[(alg, var, n)]
            x = i - 0.4 + ancho * (j + 0.5)
            eje.bar(x, ns / 1e9, ancho * 0.95, color=COLORES[alg],
                    hatch="//" if est else None, edgecolor="black" if est else COLORES[alg],
                    linewidth=0.6)
            eje.text(x, ns / 1e9 * 1.08, formato(ns), ha="center", va="bottom",
                     fontsize=7, rotation=90)
            ymax = max(ymax, ns / 1e9)
    eje.set_yscale("log")
    eje.set_ylim(top=ymax * 12)
    eje.set_xticks(range(3))
    eje.set_xticklabels([t for _, t in VARIANTES])
    eje.set_ylabel("Tiempo promedio (s, escala log)")
    eje.set_title(f"Java - efecto del orden de la entrada, n = {n:,}".replace(",", ".")
                  + " (barra rayada = estimado)")
    eje.grid(True, axis="y", which="both", alpha=0.25)
    for alg in ALGORITMOS:
        eje.bar(0, 0, color=COLORES[alg], label=NOMBRES[alg])
    eje.legend(ncol=6, loc="upper center", fontsize=9)
    fig.tight_layout()
    ruta = os.path.join(SALIDA, f"p1_orden_java_{n}.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print("Generada", ruta)


def java_vs_python(dj, dp, n=1000000, var="random"):
    fig, eje = plt.subplots(figsize=(12, 5.8))
    ancho = 0.38
    ymax = 0
    for i, alg in enumerate(ALGORITMOS):
        for off, datos, lang, hatch_base in ((-ancho / 2, dj, "Java", None),
                                             (ancho / 2, dp, "Python", None)):
            if (alg, var, n) not in datos:
                continue
            ns, est = datos[(alg, var, n)]
            color = COLORES[alg]
            eje.bar(i + off, ns / 1e9, ancho * 0.95, color=color,
                    alpha=1.0 if lang == "Java" else 0.55,
                    hatch="//" if est else None, edgecolor="black", linewidth=0.6)
            eje.text(i + off, ns / 1e9 * 1.08, formato(ns), ha="center",
                     va="bottom", fontsize=8, rotation=90)
            ymax = max(ymax, ns / 1e9)
    eje.set_yscale("log")
    eje.set_ylim(top=ymax * 12)
    eje.set_xticks(range(len(ALGORITMOS)))
    eje.set_xticklabels([NOMBRES[a] for a in ALGORITMOS])
    eje.set_ylabel("Tiempo promedio (s, escala log)")
    eje.set_title("Compilado (Java, color pleno) vs interpretado (Python, color claro), "
                  "n = 1.000.000 aleatorio (barra rayada = estimado)")
    eje.grid(True, axis="y", which="both", alpha=0.25)
    fig.tight_layout()
    ruta = os.path.join(SALIDA, "p1_java_vs_python_1M.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print("Generada", ruta)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    dj, dp = cargar("java"), cargar("python")
    if not dj or not dp:
        sys.exit("Faltan CSV de resultados.")
    crecimiento(dj, "Java")
    crecimiento(dp, "Python")
    for n in (1000, 10000, 100000):
        orden_entrada(dj, n)
    java_vs_python(dj, dp)


if __name__ == "__main__":
    main()