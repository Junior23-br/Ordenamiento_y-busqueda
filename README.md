# Taller de Ordenamiento y Búsqueda

Comparación experimental del desempeño de algoritmos de ordenamiento y búsqueda, implementados en **Java** (lenguaje compilado, con JIT) y **Python** (lenguaje interpretado), para verificar si su comportamiento corresponde con su complejidad teórica.

**Curso:** Análisis de Algoritmos

**Integrantes:**

| Persona | Nombre | Responsabilidad |
|---|---|---|
| 1 | Jefferson Rodríguez Velásquez | Datos de prueba, harness de medición, algoritmos de búsqueda (Punto 2), Punto 3.2 |
| 2 | César Camilo Tulcán Erira | Insertion Sort, Dual-Pivot QuickSort, Heap Sort |
| 3 | Meller David Batero Rodríguez | Merge Sort, Radix Sort, Bucket Sort, gráficas del Punto 1, Punto 3.1 |

---

## Estructura del repositorio

```
├── data/          Datos de prueba (generados una sola vez con semilla fija)
├── generador/     Scripts que generan y verifican los datos
├── java/src/      Código Java: harness, algoritmos y programas de medición
├── python/        Código Python: harness, algoritmos y programas de medición
├── results/       Resultados de las mediciones (CSV) y tablas
├── graficas/      Scripts de gráficas y las gráficas generadas (PNG)
└── ejecutar_punto2.ps1   Ejecuta todo el Punto 2 con un solo comando
```

## Requisitos

- **Java** 17 o superior (JDK, para compilar con `javac`)
- **Python** 3.10 o superior
- **matplotlib**, para las gráficas: `pip install matplotlib`

Todos los comandos se ejecutan **desde la carpeta raíz del repositorio**.

---

## 1. Datos de prueba

Los datos ya están incluidos en `data/`, así que no es necesario generarlos de nuevo.

| Archivo | Contenido |
|---|---|
| `random_N.txt` | N enteros aleatorios de 8 dígitos (10.000.000 a 99.999.999), uno por línea |
| `asc_N.txt` / `desc_N.txt` | Los mismos N números, ordenados ascendente / descendente |
| `claves.txt` | 1.000 claves de búsqueda: 500 presentes y 500 ausentes, mezcladas |
| `posiciones_N.txt` | 3 claves: la primera, la del centro y la última del arreglo ascendente |

N = 1.000, 10.000, 100.000 y 1.000.000.

**Decisiones de diseño:**

- Se generó una sola secuencia de 1.000.000 de números con la **semilla fija 2026**. Cada tamaño menor es un prefijo de esa secuencia (los primeros N números).
- Gracias a eso, las 500 claves presentes (tomadas de los primeros 1.000 elementos) están presentes en **todos** los tamaños, y las 500 ausentes no están en ninguno. Un solo archivo de claves sirve para los cuatro tamaños.
- Hay valores repetidos en los datos: con 1.000.000 de números elegidos entre 90 millones de valores posibles, aparecen unos 5.500 duplicados. Esto es esperado y no afecta a los algoritmos.

**Para regenerar y verificar los datos:**

```
python generador/generar_datos.py
python generador/verificar_datos.py
```

La verificación debe terminar con `RESULTADO: TODO CORRECTO`. Para confirmar que los datos regenerados son idénticos a los del repositorio, las tres primeras líneas de `data/random_1000.txt` deben ser `25988000`, `52880483` y `77446522`.

---

## 2. Harness de medición

Todos los algoritmos, de los dos puntos y de las tres personas, se miden con el mismo harness: `python/harness.py` y `java/src/Harness.java`. Así se garantiza que todos se midan bajo las mismas condiciones.

| Condición del taller | Cómo la cumple el harness |
|---|---|
| Medir solo el algoritmo | La lectura de archivos, la copia del arreglo y la verificación quedan fuera del tiempo medido |
| Reloj de alta precisión | `System.nanoTime()` en Java y `time.perf_counter_ns()` en Python |
| 5 repeticiones | Promedio y desviación estándar muestral (n − 1) |
| Calentamiento en lenguajes con JIT | En Java, al menos 1 ejecución completa, repetida hasta 0,5 s (máx. 1.000 vueltas) si el algoritmo es rápido. No se incluye en el promedio |
| Copia nueva en cada repetición | `clone()` / `copy()` antes de iniciar el reloj |
| Verificación del resultado | Ordenamiento: se compara con `asc_N.txt`. Búsqueda: el índice retornado debe cumplir `arr[i] == clave`, o −1 si la clave no está |
| Límite de 5 minutos | Si una repetición supera 5 minutos, se detienen las repeticiones restantes |
| Errores de pila o recursión | `StackOverflowError` y `RecursionError` se capturan y se registran en el CSV con `tipo = error:...`, sin detener el programa |

En Java, el resultado de cada búsqueda se acumula en una variable `volatile`. Esto impide que el compilador JIT elimine búsquedas cuyo resultado "no se usa".

**Uso para agregar un algoritmo:**

- **Ordenamiento:** función que recibe un arreglo de enteros y retorna el arreglo ordenado (puede ser el mismo arreglo).
  - Python: `harness.medir_ordenamiento(nombre, funcion, variante, n, archivo_csv)`
  - Java: `Harness.medirOrdenamiento(nombre, algoritmo, variante, n, csv)`
  - `variante` es `"random"`, `"asc"` o `"desc"`.
- **Búsqueda:** función que recibe `(arr, clave)` y retorna el índice de la clave, o −1 si no está.
  - Python: `harness.medir_busqueda(nombre, funcion, n, variante, archivo_csv)`
  - Java: `Harness.medirBusqueda(nombre, algoritmo, n, variante, csv)`

**Prueba del harness** (usa algoritmos de prueba y escribe en `results/prueba_harness_*.csv`, que está excluido del repositorio):

```
python python/harness.py
javac -d java/out java/src/*.java
java -cp java/out Harness
```

### Formato de los resultados (CSV)

Cada fila es una medición:

```
algoritmo,lenguaje,punto,variante,n,rep1,rep2,rep3,rep4,rep5,promedio_ns,desviacion_ns,tipo
```

- Los tiempos están en **nanosegundos**. En búsqueda, son el tiempo **promedio por búsqueda**.
- `tipo` puede ser `medido`, `estimado` o `error:<causa>`.

---

## 3. Punto 1: Algoritmos de ordenamiento

Seis algoritmos, con el mismo código en Java y en Python. Todos ordenan el arreglo recibido en el mismo arreglo.

| Algoritmo | Complejidad (caso promedio) | Código |
|---|---|---|
| Insertion Sort | O(n²) | `python/ordenamientos_p2.py`, `java/src/OrdenamientosP2.java` |
| Dual-Pivot QuickSort | O(n log n); O(n²) con entrada ordenada | `python/ordenamientos_p2.py`, `java/src/OrdenamientosP2.java` |
| Heap Sort | O(n log n) | `python/ordenamientos_p2.py`, `java/src/OrdenamientosP2.java` |
| Merge Sort | O(n log n) | `python/ordenamientos_p3.py`, `java/src/OrdenamientosP3.java` |
| Radix Sort | O(n) para enteros de 8 dígitos | `python/ordenamientos_p3.py`, `java/src/OrdenamientosP3.java` |
| Bucket Sort | O(n) con datos uniformes; O(n²) en el peor caso | `python/ordenamientos_p3.py`, `java/src/OrdenamientosP3.java` |

**Variantes de entrada:** cada algoritmo se mide con entrada aleatoria (`random`), ascendente (`asc`) y descendente (`desc`), con n = 1.000, 10.000, 100.000 y 1.000.000.

**Ejecutar las mediciones** (desde la raíz del repositorio). Con `--piloto` solo se miden n = 1.000 y 10.000 y se muestra el plan de qué casos se estimarán.

```
javac -d java/out java/src/*.java

java -cp java/out MedirOrdenamientoP2          # Insertion, Dual-Pivot, Heap  -> results/ordenamiento_java_p2.csv
java -cp java/out MedirOrdenamientoP3          # Merge, Radix, Bucket         -> results/ordenamiento_java_p3.csv
python python/medir_ordenamiento_p2.py         # -> results/ordenamiento_python_p2.csv
python python/medir_ordenamiento_p3.py         # -> results/ordenamiento_python_p3.csv

python graficas/graficas_ordenamiento.py       # gráficas del Punto 1
```

**Detalles de implementación:**

- **Radix Sort:** versión LSD en base 10, con 8 pasadas (una por dígito) y Counting Sort estable en cada una.
- **Bucket Sort:** la versión de GeeksforGeeks trabaja con decimales en [0, 1); se adaptó a enteros de 8 dígitos. Se usan n cubetas y el índice de cada valor es `(valor − mínimo) · n / (máximo − mínimo + 1)`. Cada cubeta se ordena con Insertion Sort. Como los datos son uniformes, cada cubeta recibe en promedio un elemento.
- **Merge Sort:** estable (usa `<=` al mezclar) y no es in-place: usa O(n) de memoria extra.
- **Dual-Pivot QuickSort:** el pivote se toma de los extremos del subarreglo. Con entrada ya ordenada (ascendente o descendente) la partición queda muy desbalanceada y la recursión llega a una profundidad cercana a n/2. Por eso en esos casos se producen `RecursionError` en Python y `StackOverflowError` en Java; se registran en el CSV como `error:...` sin detener el programa.

**Casos que superan 5 minutos o fallan por la pila:** antes de medir cada tamaño se predice el tiempo de una ejecución a partir del tamaño anterior: `tiempo_predicho = último tiempo medido × factor teórico` (el factor es 10 para O(n), 100 para O(n²) y ≈ 10 · log(n₁)/log(n₀) para O(n log n)). Si la predicción supera 5 minutos, el caso no se ejecuta y se registra con `tipo = estimado`. Si un tamaño menor falló por la pila, los mayores también se registran como estimados. En las gráficas, los valores estimados se dibujan con línea punteada, marcador hueco o barra rayada.

Resultados: `results/ordenamiento_java_p2.csv`, `results/ordenamiento_java_p3.csv`, `results/ordenamiento_python_p2.csv` y `results/ordenamiento_python_p3.csv`.

| Archivo de gráfica | Contenido |
|---|---|
| `graficas/p1_crecimiento_java.png`, `graficas/p1_crecimiento_python.png` | n contra tiempo para los seis algoritmos, escala log-log, una gráfica por tipo de entrada |
| `graficas/p1_orden_java_1000.png`, `_10000.png`, `_100000.png` | Efecto del orden de la entrada (aleatoria, ascendente, descendente) |
| `graficas/p1_java_vs_python_1M.png` | Barras Java contra Python con n = 1.000.000, entrada aleatoria |

---

## 4. Punto 2: Algoritmos de búsqueda

Algoritmos implementados (iterativos, mismo código en ambos lenguajes): `python/busquedas.py` y `java/src/Busquedas.java`.

| Algoritmo | Complejidad |
|---|---|
| Lineal | O(n) |
| Binaria | O(log n) |
| Ternaria | O(log₃ n) |
| Saltos (Jump Search) | O(√n) |
| Interpolación | O(log log n) con datos uniformes, O(n) en el peor caso |
| Exponencial | O(log i), con i la posición de la clave |

**Ejecutar todo el Punto 2** con un solo comando: verifica los datos y los algoritmos, mide en Java y Python, y genera las gráficas y tablas.

```
powershell -ExecutionPolicy Bypass -File .\ejecutar_punto2.ps1
```

**O paso a paso:**

```
javac -d java/out java/src/*.java
java -cp java/out Busquedas            # pruebas de correctitud
python python/busquedas.py             # pruebas de correctitud
java -cp java/out MedirBusquedas       # mediciones Java   (~15 s)
python python/medir_busquedas.py       # mediciones Python (~5 min)
python graficas/graficas_busqueda.py   # gráficas y tablas
```

**Qué se mide:**

- Las 1.000 claves de `claves.txt` en los cuatro tamaños. Sirve para las gráficas de crecimiento y de compilado frente a interpretado.
- La clave del inicio, del centro y del final, buscada 1.000 veces cada una, con n = 1.000.000. Sirve para la tabla de posición de la clave.

**Salidas:**

| Archivo | Contenido |
|---|---|
| `results/busqueda_java.csv`, `results/busqueda_python.csv` | Todas las mediciones |
| `graficas/p2_crecimiento_java.png`, `graficas/p2_crecimiento_python.png` | n contra tiempo, escala log-log |
| `graficas/p2_java_vs_python_1M.png` | Barras Java vs Python con n = 1.000.000 |
| `results/p2_tabla_posicion_java.md` / `.csv` | Tabla de posición de la clave (Java) |
| `results/p2_tabla_posicion_python.md` / `.csv` | Tabla de posición de la clave (Python) |

---

## 5. Punto 3.2: ¿Ordenar o no ordenar?

Calcula a partir de cuántas búsquedas k conviene ordenar el arreglo (con el algoritmo de ordenamiento más rápido medido, entrada aleatoria) y usar búsqueda binaria, en lugar de hacer k búsquedas lineales:

```
k > k* = T_orden / (t_lineal − t_binaria)
```

Requiere los CSV de búsqueda y de ordenamiento (con n = 1.000.000):

```
python graficas/punto_3_2.py
```

Resultados con las mediciones definitivas:

| | Java | Python |
|---|---|---|
| Mejor ordenamiento (T_orden) | Radix Sort: 31,826 ms | Bucket Sort: 766,435 ms |
| Búsqueda lineal | 88.983,2 ns | 13.477.961,4 ns |
| Búsqueda binaria | 125,8 ns | 1.734,1 ns |
| k* | 358,16 → conviene ordenar desde k = 359 | 56,87 → conviene ordenar desde k = 57 |

---

## Equipo de medición

Todas las mediciones definitivas se realizaron en el mismo equipo, para que los tiempos sean comparables entre algoritmos y entre lenguajes.

| | |
|---|---|
| Equipo | Portátil de César Tulcán (persona 2) |
| Procesador | Intel Core i7-13620H (13.ª generación) |
| Memoria RAM | 16 GB |
| Sistema operativo | Windows 11 Home |
| Java | OpenJDK 25.0.4.1 LTS (Microsoft Build of OpenJDK) |
| Python | 3.14.7 (CPython) |

Condiciones: equipo conectado a la corriente, sin otras aplicaciones abiertas y sin uso durante las mediciones.

---

## Fuentes

**Búsqueda (GeeksforGeeks):**

- [Linear Search](https://www.geeksforgeeks.org/dsa/linear-search/)
- [Binary Search](https://www.geeksforgeeks.org/dsa/binary-search/)
- [Ternary Search](https://www.geeksforgeeks.org/dsa/ternary-search/)
- [Jump Search](https://www.geeksforgeeks.org/dsa/jump-search/)
- [Interpolation Search](https://www.geeksforgeeks.org/dsa/interpolation-search/)
- [Exponential Search](https://www.geeksforgeeks.org/dsa/exponential-search/)

**Ordenamiento (GeeksforGeeks):**

- [Insertion Sort](https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/)
- [Dual-Pivot QuickSort](https://www.geeksforgeeks.org/dsa/dual-pivot-quicksort/)
- [Heap Sort](https://www.geeksforgeeks.org/dsa/heap-sort/)
- [Merge Sort](https://www.geeksforgeeks.org/dsa/merge-sort/)
- [Radix Sort](https://www.geeksforgeeks.org/dsa/radix-sort/)
- [Bucket Sort](https://www.geeksforgeeks.org/dsa/bucket-sort-2/)

## Uso de inteligencia artificial

Se utilizó Claude (Anthropic) como apoyo en la implementación del harness de medición, los algoritmos de búsqueda, los scripts de gráficas y la redacción de borradores de análisis. El detalle está en la sección correspondiente del documento PDF.
