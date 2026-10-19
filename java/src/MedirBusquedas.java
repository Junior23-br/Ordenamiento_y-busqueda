import java.io.IOException;
import java.nio.file.*;
import java.util.Map;

/**
 * Mediciones del Punto 2 en Java (Persona 1).
 *
 * Genera results/busqueda_java.csv con:
 *   - variante "claves": las 1.000 claves, en los 4 tamaños
 *   - variantes "inicio", "centro", "final": solo n = 1.000.000
 *
 * Ejecutar desde la carpeta raíz del proyecto:
 *   javac -d java/out java/src/*.java
 *   java -cp java/out MedirBusquedas
 */
public class MedirBusquedas {
    public static void main(String[] args) throws IOException {
        String csv = "busqueda_java.csv";
        Files.deleteIfExists(Harness.RESULTS.resolve(csv));   // se empieza de cero
        long t0 = System.nanoTime();

        System.out.println("Crecimiento: 1.000 claves (500 presentes + 500 ausentes)");
        for (int n : new int[]{1_000, 10_000, 100_000, 1_000_000})
            for (Map.Entry<String, Harness.Busqueda> e : Busquedas.algoritmos().entrySet())
                Harness.medirBusqueda(e.getKey(), e.getValue(), n, "claves", csv);

        System.out.println("\nPosicion de la clave: n = 1.000.000");
        for (Map.Entry<String, Harness.Busqueda> e : Busquedas.algoritmos().entrySet())
            for (String v : new String[]{"inicio", "centro", "final"})
                Harness.medirBusqueda(e.getKey(), e.getValue(), 1_000_000, v, csv);

        System.out.printf("%nListo en %.0f s. Resultados en results/%s%n", (System.nanoTime() - t0) / 1e9, csv);
    }
}
