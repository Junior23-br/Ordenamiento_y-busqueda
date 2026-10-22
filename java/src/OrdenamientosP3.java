import java.io.IOException;
import java.util.*;

/**
 * Algoritmos de ordenamiento - Taller 3, Punto 1, Persona 3
 *
 * Merge Sort, Radix Sort y Bucket Sort.
 * Todos reciben el arreglo, lo ordenan y lo retornan, como pide Harness.Ordenamiento.
 * El código es el mismo que en ordenamientos_p3.py.
 *
 * Fuentes (GeeksforGeeks):
 *   Merge Sort:  https://www.geeksforgeeks.org/dsa/merge-sort/
 *   Radix Sort:  https://www.geeksforgeeks.org/dsa/radix-sort/
 *   Bucket Sort: https://www.geeksforgeeks.org/dsa/bucket-sort-2/
 *   Los nombres de las variables se cambiaron a palabras completas en español
 *   (por ejemplo l, m, r -> izquierda, medio, derecha); la lógica es la misma.
 *   Bucket Sort se adaptó de decimales en [0, 1) a enteros de 8 dígitos (ver la sección de Bucket Sort).
 */
public class OrdenamientosP3 {

    // ================================================================ Merge Sort
    // O(n log n) en todos los casos. Estable. NO es in-place: usa O(n) de memoria extra.

    /** Envoltorio: lo que llama el harness. */
    public static int[] mergeSort(int[] arreglo) {
        mergeSort(arreglo, 0, arreglo.length - 1);
        return arreglo;
    }

    // Ordena la parte del arreglo que va desde la posición "izquierda" hasta la posición "derecha".
    static void mergeSort(int[] arreglo, int izquierda, int derecha) {
        // Profundidad de recursión: log2(n) ≈ 20 niveles con n = 1.000.000 -> nunca desborda la pila
        if (izquierda < derecha) {                          // si izquierda == derecha hay 1 elemento: caso base
            int medio = izquierda + (derecha - izquierda) / 2;
            mergeSort(arreglo, izquierda, medio);           // ordena la primera mitad
            mergeSort(arreglo, medio + 1, derecha);         // ordena la segunda mitad
            merge(arreglo, izquierda, medio, derecha);      // mezcla las dos mitades ordenadas
        }
    }

    // Mezcla arreglo[izquierda..medio] con arreglo[medio+1..derecha], que ya están ordenados.
    static void merge(int[] arreglo, int izquierda, int medio, int derecha) {
        int tamanoIzquierda = medio - izquierda + 1;
        int tamanoDerecha = derecha - medio;

        // Copias temporales de las dos mitades
        int[] mitadIzquierda = new int[tamanoIzquierda];
        int[] mitadDerecha = new int[tamanoDerecha];
        for (int i = 0; i < tamanoIzquierda; i++) mitadIzquierda[i] = arreglo[izquierda + i];
        for (int i = 0; i < tamanoDerecha; i++) mitadDerecha[i] = arreglo[medio + 1 + i];

        int posIzquierda = 0;          // recorre mitadIzquierda
        int posDerecha = 0;            // recorre mitadDerecha
        int posArreglo = izquierda;    // dónde se escribe el resultado en el arreglo
        while (posIzquierda < tamanoIzquierda && posDerecha < tamanoDerecha) {
            if (mitadIzquierda[posIzquierda] <= mitadDerecha[posDerecha]) {   // "<=" mantiene el orden de los iguales: ESTABLE
                arreglo[posArreglo] = mitadIzquierda[posIzquierda];
                posIzquierda++;
            } else {
                arreglo[posArreglo] = mitadDerecha[posDerecha];
                posDerecha++;
            }
            posArreglo++;
        }
        // Copia lo que haya sobrado de alguna de las dos mitades
        while (posIzquierda < tamanoIzquierda) arreglo[posArreglo++] = mitadIzquierda[posIzquierda++];
        while (posDerecha < tamanoDerecha) arreglo[posArreglo++] = mitadDerecha[posDerecha++];
    }

    // ================================================================ Radix Sort
    // O(d · (n + 10)), con d = número de dígitos del máximo (aquí d = 8): lineal en n.
    // No compara elementos entre sí. Estable. No es in-place: usa O(n) extra.

    /** Envoltorio: lo que llama el harness. */
    public static int[] radixSort(int[] arreglo) {
        int n = arreglo.length;
        if (n == 0) return arreglo;
        int maximo = obtenerMaximo(arreglo);
        // El máximo tiene 8 dígitos -> 8 pasadas (exponente = 1, 10, 100, ..., 10.000.000)
        for (int exponente = 1; maximo / exponente > 0; exponente *= 10)
            countingSortPorDigito(arreglo, exponente);
        return arreglo;
    }

    static int obtenerMaximo(int[] arreglo) {
        int maximo = arreglo[0];
        for (int i = 1; i < arreglo.length; i++)
            if (arreglo[i] > maximo) maximo = arreglo[i];
        return maximo;
    }

    // Counting sort estable según un solo dígito. "exponente" indica cuál:
    // 1 = unidades, 10 = decenas, 100 = centenas... El dígito es (valor / exponente) % 10.
    static void countingSortPorDigito(int[] arreglo, int exponente) {
        int n = arreglo.length;
        int[] salida = new int[n];
        int[] conteo = new int[10];                         // un contador por dígito 0..9

        for (int i = 0; i < n; i++)                         // cuenta cuántos hay de cada dígito
            conteo[(arreglo[i] / exponente) % 10]++;
        for (int digito = 1; digito < 10; digito++)         // posiciones finales acumuladas
            conteo[digito] += conteo[digito - 1];
        for (int i = n - 1; i >= 0; i--) {                  // de derecha a izquierda: ESTABLE; sin esto Radix ordenaría mal
            int digito = (arreglo[i] / exponente) % 10;
            salida[conteo[digito] - 1] = arreglo[i];
            conteo[digito]--;
        }
        for (int i = 0; i < n; i++)
            arreglo[i] = salida[i];
    }

    // ================================================================ Bucket Sort
    // Promedio O(n) con datos uniformes; peor caso O(n²) si todo cae en una cubeta.
    // Estable (Insertion Sort dentro de cada cubeta). No es in-place: usa O(n) extra.
    //
    // ADAPTACIÓN: GeeksforGeeks ordena decimales en [0, 1) y asigna la cubeta con n * valor.
    // Aquí los datos son enteros, así que:
    //   - Se usan n cubetas (tantas como elementos).
    //   - El valor x va a la cubeta  (x - minimo) * n / (maximo - minimo + 1),
    //     es decir, se reparte el rango [minimo, maximo] en n intervalos del mismo tamaño.
    //     Con n = 1.000.000 y el rango de 8 dígitos, cada cubeta cubre unos 90 valores.
    //   - El producto se calcula en long porque (x - minimo) * n no cabe en un int.

    /** Envoltorio: lo que llama el harness. */
    public static int[] bucketSort(int[] arreglo) {
        int n = arreglo.length;
        if (n <= 1) return arreglo;

        int minimo = arreglo[0], maximo = arreglo[0];
        for (int valor : arreglo) {
            if (valor < minimo) minimo = valor;
            if (valor > maximo) maximo = valor;
        }
        long rango = (long) maximo - minimo + 1;

        // 1) Crear n cubetas vacías
        @SuppressWarnings("unchecked")
        List<Integer>[] cubetas = new ArrayList[n];
        for (int i = 0; i < n; i++)
            cubetas[i] = new ArrayList<>();

        // 2) Poner cada elemento en su cubeta
        //    Datos uniformes -> cada cubeta recibe en promedio 1 elemento -> ordenar cada cubeta es O(1)
        for (int valor : arreglo) {
            int indiceCubeta = (int) (((long) valor - minimo) * n / rango);
            cubetas[indiceCubeta].add(valor);
        }

        // 3) Ordenar cada cubeta con Insertion Sort (como en GeeksforGeeks)
        for (List<Integer> cubeta : cubetas)
            insertionSort(cubeta);

        // 4) Concatenar las cubetas en orden
        int posicion = 0;
        for (List<Integer> cubeta : cubetas)
            for (int valor : cubeta)
                arreglo[posicion++] = valor;
        return arreglo;
    }

    static void insertionSort(List<Integer> cubeta) {
        for (int i = 1; i < cubeta.size(); i++) {
            int clave = cubeta.get(i);
            int j = i - 1;
            while (j >= 0 && cubeta.get(j) > clave) {       // desplaza a la derecha los mayores
                cubeta.set(j + 1, cubeta.get(j));
                j--;
            }
            cubeta.set(j + 1, clave);
        }
    }

    // ================================================================ registro para el harness
    /** Los 3 algoritmos con su nombre, en el mismo orden que en Python. */
    public static LinkedHashMap<String, Harness.Ordenamiento> algoritmos() {
        LinkedHashMap<String, Harness.Ordenamiento> mapa = new LinkedHashMap<>();
        mapa.put("MergeSort", OrdenamientosP3::mergeSort);
        mapa.put("RadixSort", OrdenamientosP3::radixSort);
        mapa.put("BucketSort", OrdenamientosP3::bucketSort);
        return mapa;
    }

    // ================================================================ pruebas de correctitud
    public static void main(String[] args) throws IOException {
        System.out.println("1) Casos borde");
        Random aleatorioGen = new Random(1);
        int[] aleatorio = new int[300];
        for (int i = 0; i < aleatorio.length; i++) aleatorio[i] = 10_000_000 + aleatorioGen.nextInt(90_000_000);
        int[] repetidos = new int[300];
        for (int i = 0; i < repetidos.length; i++) repetidos[i] = 10_000_000 + aleatorioGen.nextInt(5);
        int[] ordenado = new int[20], inverso = new int[20], iguales = new int[10];
        for (int i = 0; i < 20; i++) { ordenado[i] = 10_000_000 + i; inverso[i] = 99_999_999 - i; }
        Arrays.fill(iguales, 55_555_555);
        int[][] casos = {{}, {12_345_678}, {99_999_999, 10_000_000},
                {30_000_003, 10_000_001, 30_000_003, 20_000_002},
                iguales, ordenado, inverso, aleatorio, repetidos};
        for (Map.Entry<String, Harness.Ordenamiento> e : algoritmos().entrySet()) {
            boolean ok = true;
            for (int[] datos : casos) {
                int[] esperado = datos.clone();
                Arrays.sort(esperado);
                if (!Arrays.equals(e.getValue().ordenar(datos.clone()), esperado)) {
                    ok = false;
                    System.out.println("   FALLA " + e.getKey() + ": " + Arrays.toString(datos));
                }
            }
            System.out.println("   " + (ok ? "OK    " : "FALLA ") + e.getKey());
        }

        System.out.println("2) Archivos del taller, n = 1.000 y 100.000 (aleatorio, ascendente, descendente)");
        for (int n : new int[]{1_000, 100_000}) {
            int[] esperado = Harness.leer("asc_" + n + ".txt");
            for (Map.Entry<String, Harness.Ordenamiento> e : algoritmos().entrySet())
                for (String v : new String[]{"random", "asc", "desc"}) {
                    int[] resultado = e.getValue().ordenar(Harness.leer(v + "_" + n + ".txt"));
                    if (!Arrays.equals(resultado, esperado))
                        throw new AssertionError(e.getKey() + " fallo con " + v + ", n=" + n);
                }
            System.out.printf(Locale.US, "   OK    n = %,d: los 3 algoritmos ordenan bien%n", n);
        }
        System.out.println("\nRESULTADO: LOS 3 ALGORITMOS ORDENAN CORRECTAMENTE");
    }
}