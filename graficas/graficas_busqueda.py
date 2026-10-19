"""
Gráficas y tablas del Punto 2 (Persona 1).

Lee results/busqueda_java.csv y results/busqueda_python.csv y genera:
  graficas/p2_crecimiento_java.png        n contra tiempo, log-log (Java)
  graficas/p2_crecimiento_python.png      n contra tiempo, log-log (Python)
  graficas/p2_java_vs_python_1M.png       barras n = 1.000.000, Java vs Python, eje log
  results/p2_tabla_posicion_java.md/.csv  tabla de posición de la clave (Java)
  results/p2_tabla_posicion_python.md/.csv

Los valores con tipo "estimado" se dibujan con línea punteada / barra rayada.
Ejecutar desde la carpeta raíz:  python graficas/graficas_busqueda.py
Requiere: pip install matplotlib
"""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RESULTS = os.path.join(RAIZ, "results")
GRAFICAS = os.path.join(RAIZ, "graficas")

ALGORITMOS = ["Lineal", "Binaria", "Ternaria", "Saltos", "Interpolacion", "Exponencial"]
NOMBRES = {"Interpolacion": "Interpolación"}
# Paleta categórica validada (orden fijo; cada algoritmo conserva su color en todas las gráficas)
COLORES = {"Lineal": "#2a78d6", "Binaria": "#eb6834", "Ternaria": "#1baf7a",
           "Saltos": "#eda100", "Interpolacion": "#e87ba4", "Exponencial": "#008300"}
MARCADORES = {"Lineal": "o", "Binaria": "s", "Ternaria": "^",
              "Saltos": "D", "Interpolacion": "v", "Exponencial": "P"}
COLOR_LENGUAJE = {"Java": "#2a78d6", "Python": "#eb6834"}
TEXTO, TEXTO_2, REJILLA = "#1f1f1e", "#5f5e5a", "#e4e3df"

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": REJILLA, "axes.labelcolor": TEXTO_2,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2, "axes.titlecolor": TEXTO,
    "axes.titleweight": "bold", "axes.titlesize": 12, "figure.dpi": 150,
    "axes.spines.top": False, "axes.spines.right": False,
})


def nombre(alg):
    return NOMBRES.get(alg, alg)


def formato_tiempo(ns):
    """Muestra el tiempo con la unidad más legible."""
    if ns >= 1e6:
        return f"{ns / 1e6:.2f} ms"
    if ns >= 1e3:
        return f"{ns / 1e3:.2f} µs"
    return f"{ns:.1f} ns"


def leer(lenguaje):
    datos = {}
    with open(os.path.join(RESULTS, f"busqueda_{lenguaje.lower()}.csv")) as f:
        for r in csv.DictReader(f):
            if not r["promedio_ns"]:
                continue
            clave = (r["algoritmo"], r["variante"], int(r["n"]))
            datos[clave] = (float(r["promedio_ns"]), float(r["desviacion_ns"] or 0), r["tipo"])
    return datos


def eje_tiempo(ax):
    ax.set_yscale("log")
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.tick_params(axis="y", which="minor", length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: formato_tiempo(v)))
    ax.grid(True, which="major", axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------ crecimiento
def grafica_crecimiento(lenguaje, datos):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    tamanos = sorted({n for (_, v, n) in datos if v == "claves"})
    etiquetas = []
    for alg in ALGORITMOS:
        puntos = [(n, *datos[(alg, "claves", n)]) for n in tamanos if (alg, "claves", n) in datos]
        if not puntos:
            continue
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]
        medidos = [p for p in puntos if p[3] == "medido"]
        estimados = [p for p in puntos if p[3] != "medido"]
        # tramo medido: línea continua
        ax.plot([p[0] for p in medidos], [p[1] for p in medidos], color=COLORES[alg],
                linewidth=2, marker=MARCADORES[alg], markersize=7,
                markeredgecolor="white", markeredgewidth=1.5, label=nombre(alg))
        # tramo estimado (si existe): línea punteada desde el último medido
        if estimados:
            tramo = ([medidos[-1]] if medidos else []) + estimados
            ax.plot([p[0] for p in tramo], [p[1] for p in tramo], color=COLORES[alg],
                    linewidth=2, linestyle=":", marker=MARCADORES[alg], markersize=7,
                    markerfacecolor="white")
        etiquetas.append([alg, xs[-1], ys[-1]])

    # etiquetas directas al final de cada línea, separadas para que no se monten
    etiquetas.sort(key=lambda e: e[2])
    pos = [math.log10(e[2]) for e in etiquetas]
    separacion = 0.16
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + separacion)
    for (alg, x, y), py in zip(etiquetas, pos):
        ax.annotate(nombre(alg), xy=(x, y), xytext=(x * 1.35, 10 ** py),
                    color=TEXTO, fontsize=9, va="center",
                    arrowprops=dict(arrowstyle="-", color=COLORES[alg], lw=0.8))

    ax.set_xscale("log")
    ax.set_xticks(tamanos)
    ax.set_xticklabels([f"{n:,}".replace(",", ".") for n in tamanos])
    ax.set_xlim(tamanos[0] / 1.6, tamanos[-1] * 4)
    eje_tiempo(ax)
    ax.set_xlabel("Tamaño del arreglo (n)")
    ax.set_ylabel("Tiempo promedio por búsqueda")
    ax.set_title(f"Crecimiento del tiempo de búsqueda - {lenguaje}", loc="left", pad=22)
    ax.text(0, 1.01, "1.000 claves (500 presentes + 500 ausentes) · escala logarítmica en ambos ejes",
            transform=ax.transAxes, color=TEXTO_2, fontsize=9, va="bottom")
    ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=2)
    fig.tight_layout()
    ruta = os.path.join(GRAFICAS, f"p2_crecimiento_{lenguaje.lower()}.png")
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    print("  " + os.path.relpath(ruta, RAIZ))


# ------------------------------------------------------------------ Java vs Python
def grafica_lenguajes(java, python, n=1_000_000):
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ancho, hueco = 0.38, 0.02
    for j, (lenguaje, datos) in enumerate([("Java", java), ("Python", python)]):
        for i, alg in enumerate(ALGORITMOS):
            if (alg, "claves", n) not in datos:
                continue
            valor, _, tipo = datos[(alg, "claves", n)]
            x = i + (j - 0.5) * (ancho + hueco)
            estimado = tipo != "medido"
            ax.bar(x, valor, width=ancho, color="white" if estimado else COLOR_LENGUAJE[lenguaje],
                   edgecolor=COLOR_LENGUAJE[lenguaje], linewidth=1.2,
                   hatch="///" if estimado else None,
                   label=lenguaje if i == 0 else None)
            ax.text(x, valor * 1.12, formato_tiempo(valor) + (" (est.)" if estimado else ""),
                    ha="center", va="bottom", fontsize=8, color=TEXTO, rotation=0)
    # debajo de cada algoritmo: cuántas veces más lento es Python que Java
    etiquetas = []
    for alg in ALGORITMOS:
        if (alg, "claves", n) in java and (alg, "claves", n) in python:
            r = python[(alg, "claves", n)][0] / java[(alg, "claves", n)][0]
            etiquetas.append(f"{nombre(alg)}\nPython ×{r:.0f}")
        else:
            etiquetas.append(nombre(alg))
    ax.set_xticks(range(len(ALGORITMOS)))
    ax.set_xticklabels(etiquetas, fontsize=9)
    eje_tiempo(ax)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax * 3)
    ax.set_ylabel("Tiempo promedio por búsqueda")
    ax.set_title("Compilado frente a interpretado: búsqueda con n = 1.000.000", loc="left", pad=22)
    ax.text(0, 1.01, "Java (compilado, JIT) vs Python (interpretado) · eje logarítmico · \"Python ×N\" = cuántas veces más lento es Python",
            transform=ax.transAxes, color=TEXTO_2, fontsize=9, va="bottom")
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    ruta = os.path.join(GRAFICAS, "p2_java_vs_python_1M.png")
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    print("  " + os.path.relpath(ruta, RAIZ))


# ------------------------------------------------------------------ tabla de posición
def tabla_posicion(lenguaje, datos, n=1_000_000):
    filas = []
    for alg in ALGORITMOS:
        vals = [datos.get((alg, v, n)) for v in ["inicio", "centro", "final"]]
        if None in vals:
            continue
        ini, cen, fin = (v[0] for v in vals)
        filas.append((alg, ini, cen, fin, fin / ini))
    base = os.path.join(RESULTS, f"p2_tabla_posicion_{lenguaje.lower()}")
    with open(base + ".csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["algoritmo", "inicio_ns", "centro_ns", "final_ns", "final_sobre_inicio"])
        for a, i, c, fi, r in filas:
            w.writerow([nombre(a), f"{i:.1f}", f"{c:.1f}", f"{fi:.1f}", f"{r:.1f}"])
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(f"Tiempo promedio por búsqueda, {lenguaje}, n = 1.000.000\n\n")
        f.write("| Algoritmo | Inicio | Centro | Final | Final / Inicio |\n|---|---|---|---|---|\n")
        for a, i, c, fi, r in filas:
            f.write(f"| {nombre(a)} | {formato_tiempo(i)} | {formato_tiempo(c)} | "
                    f"{formato_tiempo(fi)} | {r:,.1f}× |\n")
    print("  " + os.path.relpath(base + ".md", RAIZ) + "  (y .csv)")
    print(open(base + ".md", encoding="utf-8").read())


if __name__ == "__main__":
    os.makedirs(GRAFICAS, exist_ok=True)
    java, python = leer("Java"), leer("Python")
    print("Generando:")
    grafica_crecimiento("Java", java)
    grafica_crecimiento("Python", python)
    grafica_lenguajes(java, python)
    tabla_posicion("Java", java)
    tabla_posicion("Python", python)
