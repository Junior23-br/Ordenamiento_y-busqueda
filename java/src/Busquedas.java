import java.io.IOException;
import java.util.*;

/**
 * Algoritmos de búsqueda - Taller 3, Punto 2 (Persona 1).
 *
 * Todos reciben (arr, x) con arr ordenado ascendente y retornan
 * un índice i tal que arr[i] == x, o -1 si x no está.
 * Las versiones son iterativas (sin recursión) y son las mismas que en busquedas.py.
 *
 * Fuentes (GeeksforGeeks):
 *   Lineal:        https://www.geeksforgeeks.org/dsa/linear-search/
 *   Binaria:       https://www.geeksforgeeks.org/dsa/binary-search/
 *   Ternaria:      https://www.geeksforgeeks.org/dsa/ternary-search/
 *   Saltos:        https://www.geeksforgeeks.org/dsa/jump-search/
 *   Interpolación: https://www.geeksforgeeks.org/dsa/interpolation-search/
 *   Exponencial:   https://www.geeksforgeeks.org/dsa/exponential-search/
 */
public class Busquedas {

    /** O(n). Revisa los elementos uno por uno desde el inicio. */
    public static int lineal(int[] arr, int x) {
        for (int i = 0; i < arr.length; i++)
            if (arr[i] == x) return i;
        return -1;
    }

    /** O(log n). Compara con el elemento del medio y descarta la mitad. */
    public static int binaria(int[] arr, int x) {
        return binaria(arr, x, 0, arr.length - 1);
    }

    static int binaria(int[] arr, int x, int lo, int hi) {
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;          // evita desbordar (lo + hi)
            if (arr[mid] == x) return mid;
            if (arr[mid] < x) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    /** O(log3 n). Divide el rango en tres partes con dos puntos de corte. */
    public static int ternaria(int[] arr, int x) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int tercio = (hi - lo) / 3;
            int mid1 = lo + tercio;
            int mid2 = hi - tercio;
            if (arr[mid1] == x) return mid1;
            if (arr[mid2] == x) return mid2;
            if (x < arr[mid1]) hi = mid1 - 1;
            else if (x > arr[mid2]) lo = mid2 + 1;
            else { lo = mid1 + 1; hi = mid2 - 1; }
        }
        return -1;
    }

    /** O(√n). Salta de a √n posiciones y luego busca linealmente en el bloque. */
    public static int saltos(int[] arr, int x) {
        int n = arr.length;
        if (n == 0) return -1;
        int paso = (int) Math.sqrt(n);
        int prev = 0, actual = paso;
        while (actual < n && arr[actual - 1] < x) {   // avanzar por bloques
            prev = actual;
            actual += paso;
        }
        int fin = Math.min(actual, n);
        for (int i = prev; i < fin; i++) {             // lineal dentro del bloque
            if (arr[i] == x) return i;
            if (arr[i] > x) break;
        }
        return -1;
    }

    /**
     * O(log log n) con datos uniformes, O(n) en el peor caso.
     * Estima la posición según el valor, como al buscar una palabra en el diccionario.
     * El producto se calcula en long: (x - arr[lo]) puede ser ~9*10^7 y (hi - lo) ~10^6,
     * y su producto (~9*10^13) no cabe en un int.
     */
    public static int interpolacion(int[] arr, int x) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi && x >= arr[lo] && x <= arr[hi]) {
            if (arr[hi] == arr[lo])                    // evita dividir entre cero
                return arr[lo] == x ? lo : -1;
            int pos = lo + (int) (((long) (x - arr[lo]) * (hi - lo)) / (arr[hi] - arr[lo]));
            if (arr[pos] == x) return pos;
            if (arr[pos] < x) lo = pos + 1;
            else hi = pos - 1;
        }
        return -1;
    }

    /**
     * O(log i), donde i es la posición de x. Duplica el rango (1, 2, 4, 8, ...)
     * hasta pasarse de x y luego hace búsqueda binaria en ese rango.
     */
    public static int exponencial(int[] arr, int x) {
        int n = arr.length;
        if (n == 0) return -1;
        if (arr[0] == x) return 0;
        int i = 1;
        while (i < n && arr[i] <= x) i *= 2;
        return binaria(arr, x, i / 2, Math.min(i, n - 1));
    }

    /** Los 6 algoritmos con su nombre, en el mismo orden que en Python. */
    public static LinkedHashMap<String, Harness.Busqueda> algoritmos() {
        LinkedHashMap<String, Harness.Busqueda> m = new LinkedHashMap<>();
        m.put("Lineal", Busquedas::lineal);
        m.put("Binaria", Busquedas::binaria);
        m.put("Ternaria", Busquedas::ternaria);
        m.put("Saltos", Busquedas::saltos);
        m.put("Interpolacion", Busquedas::interpolacion);
        m.put("Exponencial", Busquedas::exponencial);
        return m;
    }

    // ------------------------------------------------------------- pruebas de correctitud
    public static void main(String[] args) throws IOException {
        System.out.println("1) Casos borde con un arreglo pequeno (con un valor repetido)");
        int[] a = {10, 20, 20, 30, 40, 50, 60, 70, 80, 90};
        int[] presentes = {10, 90, 20, 50};        // primero, último, repetido, medio
        int[] ausentes = {5, 95, 35};              // menor, mayor, entre dos valores
        for (Map.Entry<String, Harness.Busqueda> e : algoritmos().entrySet()) {
            Harness.Busqueda f = e.getValue();
            boolean ok = true;
            for (int x : presentes) {
                int i = f.buscar(a, x);
                if (i == -1 || a[i] != x) { ok = false; System.out.println("   FALLA buscar " + x + " -> " + i); }
            }
            for (int x : ausentes) {
                int i = f.buscar(a, x);
                if (i != -1) { ok = false; System.out.println("   FALLA buscar " + x + " -> " + i); }
            }
            if (f.buscar(new int[0], 3) != -1 || f.buscar(new int[]{7}, 3) != -1) {
                ok = false; System.out.println("   FALLA arreglo vacio o de 1 elemento");
            }
            System.out.println("   " + (ok ? "OK    " : "FALLA ") + e.getKey());
        }

        System.out.println("2) Las 1.000 claves y las 3 posiciones, en los 4 tamanos");
        int[] claves = Harness.leer("claves.txt");
        for (int n : new int[]{1_000, 10_000, 100_000, 1_000_000}) {
            int[] arr = Harness.leer("asc_" + n + ".txt");
            int[] pos = Harness.leer("posiciones_" + n + ".txt");
            int[] todas = Arrays.copyOf(claves, claves.length + 3);
            System.arraycopy(pos, 0, todas, claves.length, 3);
            for (Map.Entry<String, Harness.Busqueda> e : algoritmos().entrySet())
                Harness.verificarBusqueda(e.getKey(), e.getValue(), arr, todas);   // lanza error si falla
            System.out.printf(Locale.US, "   OK    n = %,d: los 6 algoritmos responden bien%n", n);
        }
        System.out.println("\nRESULTADO: TODOS LOS ALGORITMOS SON CORRECTOS");
    }
}
