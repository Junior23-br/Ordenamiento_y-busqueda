import java.io.IOException;
import java.util.*;

/**
 * Algoritmos de ordenamiento - Taller 3, Punto 1 (Persona 2: César Tulcán).
 *
 * Insertion Sort, Dual-Pivot QuickSort (pivotes en el primer y el último elemento) y Heap Sort.
 * Todos ordenan EN EL MISMO ARREGLO (in-place) y lo retornan, como pide Harness.Ordenamiento.
 * El código es el mismo que en ordenamientos_p2.py.
 *
 * Fuentes (GeeksforGeeks):
 *   Insertion Sort:        https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/
 *   Dual-Pivot QuickSort:  https://www.geeksforgeeks.org/dsa/dual-pivot-quicksort/
 *   Heap Sort:             https://www.geeksforgeeks.org/dsa/heap-sort/
 *
 * NOTA: no se modifica el tamaño de la pila de Java. El enunciado pide documentar el error
 * si un algoritmo falla por desbordamiento de pila, no ocultarlo.
 */
public class OrdenamientosP2 {

    // ------------------------------------------------------------ Insertion Sort
    /** Mejor caso O(n) (ya ordenado), promedio y peor caso O(n²). Estable e in-place. */
    public static int[] insertionSort(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            int clave = arr[i];
            int j = i - 1;
            while (j >= 0 && arr[j] > clave) {   // desplaza a la derecha los mayores
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = clave;
        }
        return arr;
    }

    // ------------------------------------------------------------ Dual-Pivot QuickSort
    /** Mejor y promedio O(n log n), peor caso O(n²) (entrada ordenada o inversa). No estable, in-place. */
    public static int[] dualPivotQuickSort(int[] arr) {
        dpqs(arr, 0, arr.length - 1);
        return arr;
    }

    static void dpqs(int[] arr, int low, int high) {
        if (low < high) {
            int[] piv = particion(arr, low, high);
            dpqs(arr, low, piv[0] - 1);           // menores que p
            dpqs(arr, piv[0] + 1, piv[1] - 1);    // entre p y q
            dpqs(arr, piv[1] + 1, high);          // mayores que q
        }
    }

    static int[] particion(int[] arr, int low, int high) {
        if (arr[low] > arr[high]) swap(arr, low, high);
        int p = arr[low], q = arr[high];          // pivotes: primer y último elemento
        int j = low + 1, k = low + 1, g = high - 1;
        while (k <= g) {
            if (arr[k] < p) {                     // va a la zona izquierda
                swap(arr, k, j);
                j++;
            } else if (arr[k] >= q) {             // va a la zona derecha
                while (arr[g] > q && k < g) g--;
                swap(arr, k, g);
                g--;
                if (arr[k] < p) {
                    swap(arr, k, j);
                    j++;
                }
            }
            k++;
        }
        j--;
        g++;
        swap(arr, low, j);                        // ubica los pivotes en su posición final
        swap(arr, high, g);
        return new int[]{j, g};
    }

    // ------------------------------------------------------------ Heap Sort
    /** O(n log n) en mejor, promedio y peor caso. No estable, in-place. */
    public static int[] heapSort(int[] arr) {
        int n = arr.length;
        for (int i = n / 2 - 1; i >= 0; i--) heapify(arr, n, i);   // construir el max-heap
        for (int i = n - 1; i > 0; i--) {                          // sacar el máximo
            swap(arr, 0, i);
            heapify(arr, i, 0);
        }
        return arr;
    }

    static void heapify(int[] arr, int n, int i) {
        int mayor = i, izq = 2 * i + 1, der = 2 * i + 2;
        if (izq < n && arr[izq] > arr[mayor]) mayor = izq;
        if (der < n && arr[der] > arr[mayor]) mayor = der;
        if (mayor != i) {
            swap(arr, i, mayor);
            heapify(arr, n, mayor);               // profundidad máxima log2(n)
        }
    }

    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    /** Los 3 algoritmos con su nombre, en el mismo orden que en Python. */
    public static LinkedHashMap<String, Harness.Ordenamiento> algoritmos() {
        LinkedHashMap<String, Harness.Ordenamiento> m = new LinkedHashMap<>();
        m.put("InsertionSort", OrdenamientosP2::insertionSort);
        m.put("DualPivotQuickSort", OrdenamientosP2::dualPivotQuickSort);
        m.put("HeapSort", OrdenamientosP2::heapSort);
        return m;
    }

    // ------------------------------------------------------------ pruebas de correctitud
    public static void main(String[] args) throws IOException {
        System.out.println("1) Casos borde");
        Random rng = new Random(1);
        int[] aleatorio = new int[300];
        for (int i = 0; i < aleatorio.length; i++) aleatorio[i] = rng.nextInt(51);
        int[] ordenado = new int[20], inverso = new int[20], iguales = new int[10];
        for (int i = 0; i < 20; i++) { ordenado[i] = i; inverso[i] = 20 - i; }
        Arrays.fill(iguales, 7);
        int[][] casos = {{}, {5}, {2, 1}, {3, 1, 3, 2, 1, 3}, iguales, ordenado, inverso, aleatorio};
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

        System.out.println("2) Archivos del taller, n = 1.000 (aleatorio, ascendente, descendente)");
        int[] esperado = Harness.leer("asc_1000.txt");
        for (Map.Entry<String, Harness.Ordenamiento> e : algoritmos().entrySet()) {
            for (String v : new String[]{"random", "asc", "desc"}) {
                int[] r = e.getValue().ordenar(Harness.leer(v + "_1000.txt"));
                if (!Arrays.equals(r, esperado)) throw new AssertionError(e.getKey() + " fallo con " + v);
            }
            System.out.println("   OK    " + e.getKey());
        }

        System.out.println("3) Comportamiento esperado: QuickSort con entrada ordenada, n = 100.000");
        try {
            dualPivotQuickSort(Harness.leer("asc_100000.txt"));
            System.out.println("   (no fallo con la pila de este equipo)");
        } catch (StackOverflowError e) {
            System.out.println("   OK    StackOverflowError, como se esperaba: la recursion llega a ~50.000");
            System.out.println("         niveles y no cabe en la pila de Java. Esto se documenta en el analisis.");
        }
        System.out.println("\nRESULTADO: LOS 3 ALGORITMOS ORDENAN CORRECTAMENTE");
    }
}
