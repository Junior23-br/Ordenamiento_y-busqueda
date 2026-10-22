# Ejecuta todo el Punto 2 (Persona 1) en el portatil de medicion.
# Uso, desde la carpeta raiz del proyecto en PowerShell:
#   powershell -ExecutionPolicy Bypass -File .\ejecutar_punto2.ps1

$ErrorActionPreference = "Stop"

function Paso($texto) { Write-Host "`n==== $texto ====" -ForegroundColor Cyan }
function Ejecutar($comando) {
    Invoke-Expression $comando
    if ($LASTEXITCODE -ne 0) { throw "Fallo: $comando" }
}

Paso "1/6 Equipo de medicion (copiar estos datos al PDF)"
Get-ComputerInfo -Property CsProcessors, OsName, CsTotalPhysicalMemory | Format-List
cmd /c "java -version 2>&1"
python --version

Paso "2/6 Verificar que los datos son los mismos del repositorio"
Ejecutar "python generador/verificar_datos.py"
Write-Host "Primeras 3 lineas de random_1000.txt (deben ser 25988000, 52880483, 77446522):"
Get-Content data/random_1000.txt -TotalCount 3

Paso "3/6 Compilar Java y comprobar que los algoritmos son correctos"
Ejecutar "javac -d java/out java/src/*.java"
Ejecutar "java -cp java/out Busquedas"
Ejecutar "python python/busquedas.py"

Paso "4/6 Mediciones en Java (~15 s)"
Ejecutar "java -cp java/out MedirBusquedas"

Paso "5/6 Mediciones en Python (~5 min)"
Ejecutar "python python/medir_busquedas.py"

Paso "6/6 Graficas y tablas"
Ejecutar "python graficas/graficas_busqueda.py"

Write-Host "`nPunto 2 terminado. Resultados en results/ y graficas en graficas/." -ForegroundColor Green
