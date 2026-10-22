import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/**
 * Mediciones del Punto 1 en Java - Persona 2 (César Tulcán).
 * Insertion Sort, Dual-Pivot QuickSort y Heap Sort con entrada aleatoria, ascendente y descendente.
 *
 * Regla para los casos lentos (enunciado: más de 5 minutos por ejecución):
 *   antes de cada tamaño se PREDICE el tiempo de una ejecución a partir del tamaño anterior
 *   y de la complejidad teórica. Si la predicción supera 5 minutos, NO se ejecuta y se registra
 *   como "estimado". Si un tamaño menor falló por desbordamiento de pila, los mayores también
 *   fallarán: se registra el error y el tiempo estimado.
 *
 * Uso, desde la carpeta raíz:
 *   javac -d java/out java/src/*.java
 *   java -cp java/out MedirOrdenamientoP2 --piloto   mide solo 1.000 y 10.000 y muestra el plan
 *   java -cp java/out MedirOrdenamientoP2            medición completa -> results/ordenamiento_java_p2.csv
 */
public class MedirOrdenamientoP2 {

    static final int[] TAMANOS = {1_000, 10_000, 100_000, 1_000_000};
    static final String[] VARIANTES = {"random", "asc", "desc"};
    static final double LIMITE_S = 5 * 60;

    /** Crecimiento teórico de cada caso (se usa para predecir y para estimar). */
    static String crecimiento(String alg, String v) {
        if (alg.equals("InsertionSort")) return v.equals("asc") ? "n" : "n^2";
        if (alg.equals("DualPivotQuickSort")) return v.equals("random") ? "n log n" : "n^2";
        return "n log n";                                       // HeapSort
    }

    static double factor(String tipo, double n0, double n1) {
        if (tipo.equals("n")) return n1 / n0;
        if (tipo.equals("n^2")) return (n1 / n0) * (n1 / n0);
        return (n1 * Math.log(n1)) / (n0 * Math.log(n0));    // n log n
    }

    static String duracion(double s) {
        if (s >= 3600) return String.format(Locale.US, "%.1f h", s / 3600);
        if (s >= 60) return String.format(Locale.US, "%.1f min", s / 60);
        return String.format(Locale.US, "%.1f s", s);
    }

    public static void main(String[] args) throws IOException {
        boolean piloto = args.length > 0 && args[0].equals("--piloto");
        String csv = piloto ? "piloto_ordenamiento_java_p2.csv" : "ordenamiento_java_p2.csv";
        Files.deleteIfExists(Harness.RESULTS.resolve(csv));    // se empieza de cero
        int maxMedir = piloto ? 10_000 : 1_000_000;
        List<String> plan = new ArrayList<>();
        double total = 0;
        long t0 = System.nanoTime();

        for (Map.Entry<String, Harness.Ordenamiento> e : OrdenamientosP2.algoritmos().entrySet()) {
            String nombre = e.getKey();
            for (String v : VARIANTES) {
                String tipo = crecimiento(nombre, v);
                int nUlt = 0;
                double promUlt = 0;
                boolean fallo = false;
                for (int n : TAMANOS) {
                    double pred = nUlt > 0 ? promUlt * factor(tipo, nUlt, n) : Double.NaN;
                    if (n > maxMedir) {                          // solo en el piloto
                        if (!Double.isNaN(pred)) {
                            double s = pred / 1e9;
                            String accion;
                            if (fallo) accion = "error de pila -> estimar";
                            else if (s > LIMITE_S) accion = "supera 5 min -> estimar";
                            else {                               // 1 calentamiento + 5 repeticiones
                                accion = "se mide (calent. + 5 rep. = " + duracion(6 * s) + ")";
                                total += 6 * s;
                            }
                            plan.add(String.format(Locale.US, "  %-20s %-7s n=%,9d  %9s  %s",
                                                   nombre, v, n, duracion(s), accion));
                            nUlt = n;
                            promUlt = pred;
                        }
                        continue;
                    }
                    if (fallo) {
                        System.out.printf(Locale.US, "  %-22s %-7s n=%,9d  NO SE EJECUTA: fallo por la pila con un n menor -> estimado %s%n",
                                          nombre, v, n, duracion(pred / 1e9));
                        Harness.guardarEstimado(csv, nombre, 1, v, n, pred);
                        nUlt = n; promUlt = pred;
                    } else if (!Double.isNaN(pred) && pred / 1e9 > LIMITE_S) {
                        System.out.printf(Locale.US, "  %-22s %-7s n=%,9d  NO SE EJECUTA: prediccion %s > 5 min -> estimado (%s)%n",
                                          nombre, v, n, duracion(pred / 1e9), tipo);
                        Harness.guardarEstimado(csv, nombre, 1, v, n, pred);
                        nUlt = n; promUlt = pred;
                    } else {
                        double prom = Harness.medirOrdenamiento(nombre, e.getValue(), v, n, csv);
                        if (Double.isNaN(prom)) {                // StackOverflowError
                            fallo = true;
                            if (!Double.isNaN(pred)) {
                                System.out.printf(Locale.US, "  %-22s %-7s %11s  estimado si no hubiera fallado: %s (%s)%n",
                                                  "", "", "", duracion(pred / 1e9), tipo);
                                Harness.guardarEstimado(csv, nombre, 1, v, n, pred);
                                nUlt = n; promUlt = pred;
                            }
                        } else {
                            nUlt = n; promUlt = prom;
                        }
                    }
                }
            }
        }
        double transcurrido = (System.nanoTime() - t0) / 1e9;
        System.out.printf("%nTiempo total: %s. Resultados en results/%s%n", duracion(transcurrido), csv);
        if (piloto) {
            System.out.println("\nPLAN para la medicion completa (prediccion de UNA ejecucion):");
            plan.forEach(System.out::println);
            System.out.println("\n  Tiempo aproximado de la medicion completa: " + duracion(total + transcurrido));
        }
    }
}
