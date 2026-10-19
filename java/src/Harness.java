import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Harness de medición en Java - Taller 3 (Ordenamiento y Búsqueda).
 *
 * Lo usan las tres personas del grupo. Se encarga de:
 *   - leer los archivos de data/
 *   - hacer una ejecución de CALENTAMIENTO (JIT) que no se incluye en el promedio
 *   - medir solo el algoritmo (lectura, copia y verificación quedan fuera)
 *   - repetir 5 veces y calcular promedio y desviación estándar
 *   - guardar cada medición como una fila en un CSV de results/
 *
 * Todos los tiempos se guardan en nanosegundos (ns).
 * Compilar y ejecutar desde la carpeta raíz del proyecto:
 *   javac -d java/out java/src/*.java
 *   java -cp java/out Harness
 */
public class Harness {

    /** Algoritmo de ordenamiento: puede ordenar el mismo arreglo y retornarlo, o retornar uno nuevo. */
    public interface Ordenamiento { int[] ordenar(int[] a); }

    /** Algoritmo de búsqueda: retorna un índice i con a[i] == clave, o -1 si no está. */
    public interface Busqueda { int buscar(int[] a, int clave); }

    static final int REPETICIONES = 5;
    static final long LIMITE_NS = 5L * 60 * 1_000_000_000L;   // 5 minutos
    static final long CALENTAMIENTO_NS = 500_000_000L;         // 0,5 s máximo de calentamiento
    static final String LENGUAJE = "Java";
    static final Path DATA = Paths.get("data");
    static final Path RESULTS = Paths.get("results");
    static final String ENCABEZADO =
        "algoritmo,lenguaje,punto,variante,n,rep1,rep2,rep3,rep4,rep5,promedio_ns,desviacion_ns,tipo";

    /** Evita que el JIT elimine las búsquedas cuyo resultado "no se usa". */
    static volatile long sumidero;

    // ------------------------------------------------------------ lectura
    public static int[] leer(String nombre) throws IOException {
        List<String> lineas = Files.readAllLines(DATA.resolve(nombre));
        return lineas.stream().map(String::trim).filter(s -> !s.isEmpty())
                     .mapToInt(Integer::parseInt).toArray();
    }

    // ------------------------------------------------------------ CSV
    static double[] guardarFila(String csv, String algoritmo, int punto, String variante,
                                int n, double[] tiempos, String tipo) throws IOException {
        Files.createDirectories(RESULTS);
        Path ruta = RESULTS.resolve(csv);
        boolean nuevo = !Files.exists(ruta);
        double prom = 0, desv = 0;
        if (tiempos.length > 0) {
            for (double t : tiempos) prom += t;
            prom /= tiempos.length;
            if (tiempos.length > 1) {                       // desviación muestral (n-1)
                for (double t : tiempos) desv += (t - prom) * (t - prom);
                desv = Math.sqrt(desv / (tiempos.length - 1));
            }
        }
        StringBuilder sb = new StringBuilder();
        if (nuevo) sb.append(ENCABEZADO).append('\n');
        sb.append(algoritmo).append(',').append(LENGUAJE).append(',').append(punto).append(',')
          .append(variante).append(',').append(n);
        for (int r = 0; r < REPETICIONES; r++) {
            sb.append(',');
            if (r < tiempos.length) sb.append(String.format(Locale.US, "%.3f", tiempos[r]));
        }
        if (tiempos.length > 0) {
            sb.append(String.format(Locale.US, ",%.2f,%.2f", prom, desv));
        } else {
            sb.append(",,");
        }
        sb.append(',').append(tipo).append('\n');
        Files.writeString(ruta, sb.toString(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        return new double[]{prom, desv};
    }

    // ------------------------------------------------------------ ordenamiento
    public static void medirOrdenamiento(String nombre, Ordenamiento alg, String variante, int n,
                                         String csv) throws IOException {
        int[] original = leer(variante + "_" + n + ".txt");
        int[] esperado = leer("asc_" + n + ".txt");
        try {
            // Calentamiento (JIT): al menos 1 ejecución completa que NO se cuenta.
            // Si el algoritmo es rápido se repite durante 0,5 s (máximo 1.000 vueltas),
            // para que el JIT termine de optimizar antes de empezar a medir.
            long inicioCal = System.nanoTime();
            int vueltas = 0;
            do {
                verificarOrden(nombre, alg.ordenar(original.clone()), esperado, variante, n);
                vueltas++;
            } while (vueltas < 1000 && System.nanoTime() - inicioCal < CALENTAMIENTO_NS);

            List<Double> tiempos = new ArrayList<>();
            for (int r = 0; r < REPETICIONES; r++) {
                int[] copia = original.clone();               // copia nueva, FUERA del tiempo
                long inicio = System.nanoTime();
                int[] resultado = alg.ordenar(copia);
                long fin = System.nanoTime();
                verificarOrden(nombre, resultado, esperado, variante, n);   // FUERA del tiempo
                tiempos.add((double) (fin - inicio));
                if (fin - inicio > LIMITE_NS) {
                    System.out.println("  aviso: " + nombre + " supero 5 minutos; se detienen las repeticiones");
                    break;
                }
            }
            double[] t = tiempos.stream().mapToDouble(Double::doubleValue).toArray();
            double[] pd = guardarFila(csv, nombre, 1, variante, n, t, "medido");
            System.out.printf(Locale.US, "  %-22s %-7s n=%,9d  prom=%12.3f ms  desv=%10.3f ms%n",
                              nombre, variante, n, pd[0] / 1e6, pd[1] / 1e6);
        } catch (StackOverflowError e) {
            // No se oculta el error: queda registrado en el CSV para documentarlo
            guardarFila(csv, nombre, 1, variante, n, new double[0], "error:StackOverflowError");
            System.out.printf(Locale.US, "  %-22s %-7s n=%,9d  ERROR: StackOverflowError (desbordamiento de pila)%n",
                              nombre, variante, n);
        }
    }

    static void verificarOrden(String nombre, int[] resultado, int[] esperado, String variante, int n) {
        if (!Arrays.equals(resultado, esperado))
            throw new AssertionError(nombre + " no ordeno bien (" + variante + ", n=" + n + ")");
    }

    // ------------------------------------------------------------ búsqueda
    static void verificarBusqueda(String nombre, Busqueda alg, int[] arr, int[] claves) {
        Set<Integer> presentes = new HashSet<>();
        for (int x : arr) presentes.add(x);
        for (int k : claves) {
            int i = alg.buscar(arr, k);
            if (presentes.contains(k)) {
                if (i == -1 || arr[i] != k)
                    throw new AssertionError(nombre + ": no encontro " + k + ", que si esta");
            } else if (i != -1) {
                throw new AssertionError(nombre + ": dice encontrar " + k + ", que no esta");
            }
        }
    }

    /**
     * variante "claves": las 1.000 claves de claves.txt (500 presentes + 500 ausentes).
     * variante "inicio" / "centro" / "final": la misma clave buscada 1.000 veces.
     * Se mide el tiempo TOTAL de las 1.000 búsquedas y se guarda el promedio por búsqueda.
     */
    public static void medirBusqueda(String nombre, Busqueda alg, int n, String variante,
                                     String csv) throws IOException {
        int[] arr = leer("asc_" + n + ".txt");
        int[] claves;
        if (variante.equals("claves")) {
            claves = leer("claves.txt");
        } else {
            int pos = variante.equals("inicio") ? 0 : variante.equals("centro") ? 1 : 2;
            claves = new int[1000];
            Arrays.fill(claves, leer("posiciones_" + n + ".txt")[pos]);
        }
        verificarBusqueda(nombre, alg, arr, claves);         // FUERA del tiempo

        // Calentamiento (JIT): se recorren las claves durante 0,5 s (máx. 1.000 vueltas) sin contar el tiempo
        long suma = 0;
        long inicioCal = System.nanoTime();
        int vueltas = 0;
        do {
            for (int k : claves) suma += alg.buscar(arr, k);
            vueltas++;
        } while (vueltas < 1000 && System.nanoTime() - inicioCal < CALENTAMIENTO_NS);

        double[] tiempos = new double[REPETICIONES];
        for (int r = 0; r < REPETICIONES; r++) {
            long inicio = System.nanoTime();
            for (int k : claves) suma += alg.buscar(arr, k);
            long fin = System.nanoTime();
            tiempos[r] = (double) (fin - inicio) / claves.length;   // tiempo por búsqueda
        }
        sumidero = suma;
        double[] pd = guardarFila(csv, nombre, 2, variante, n, tiempos, "medido");
        System.out.printf(Locale.US, "  %-22s %-7s n=%,9d  prom=%12.1f ns/busqueda  desv=%10.1f%n",
                          nombre, variante, n, pd[0], pd[1]);
    }

    // ------------------------------------------------------------ prueba del harness
    public static void main(String[] args) throws IOException {
        String csv = "prueba_harness_java.csv";
        Files.deleteIfExists(RESULTS.resolve(csv));
        System.out.println("Prueba del harness (resultados en results/" + csv + ")");

        Ordenamiento sortPrueba = a -> { Arrays.sort(a); return a; };   // solo para probar
        for (int n : new int[]{1_000, 10_000})
            medirOrdenamiento("sort_java_PRUEBA", sortPrueba, "random", n, csv);

        Busqueda linealPrueba = (a, k) -> {
            for (int i = 0; i < a.length; i++) if (a[i] == k) return i;
            return -1;
        };
        for (int n : new int[]{1_000, 10_000})
            for (String v : new String[]{"claves", "inicio", "centro", "final"})
                medirBusqueda("lineal_PRUEBA", linealPrueba, n, v, csv);

        // Prueba 1: la verificación detecta un ordenamiento incorrecto
        try {
            medirOrdenamiento("ordenamiento_malo", a -> a, "random", 1_000, csv);
            System.out.println("  FALLA: la verificacion no detecto un ordenamiento incorrecto");
        } catch (AssertionError e) {
            System.out.println("  OK: la verificacion detecto el error -> " + e.getMessage());
        }

        // Prueba 2: un desbordamiento de pila se registra en vez de detener el programa
        Ordenamiento recursivoInfinito = new Ordenamiento() {
            public int[] ordenar(int[] a) { return ordenar(a); }
        };
        medirOrdenamiento("recursion_infinita", recursivoInfinito, "random", 1_000, csv);
    }
}
